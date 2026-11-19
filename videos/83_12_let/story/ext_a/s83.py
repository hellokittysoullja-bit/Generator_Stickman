"""Рилс 83 «12 лет в телефоне?», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу wN); числа в коде — длительности движений.
Хук s01–s03 и петля s18 — бег из рилса 82 (ext_c: план шагов, трекинг, влёт правил 28–29; rdima/rcat — копии): Дима бежит,
уткнувшись в телефон, и стареет на бегу (expr["age"], common/aging.py); кот бежит рядом и не стареет. Остальные планы —
common/people.py, cat.py, props.py, свой фон. Призыв s06 — scripts/story_cta_tg.py.
NOCAM=1 — без влёта, тряски и заголовка (замер движения рисунка); MASK=1 — только рисунок хука (Дима и кот) белым на чёрном."""
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
import people  # noqa: E402
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
    """Заголовок хука: экранный слой s01–s03; уходит сжатием к склейке s03→s04."""
    if NOCAM or MASK:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, text=SH["title"]["text"], t_in=SH["title"]["t_in"], t_out=T0("s04") - 0.15, hits=hits)


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
        if conf.get("still"):        # до a стоит: обе ступни на месте
            Cn.append([conf["a"] - k * tc, "n" if k % 2 == 0 else "f", conf["x0"] - (0 if k % 2 == 0 else 60), 0.0, conf["a"] - k * tc + tc * .99, tc, None])
            continue
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
        if conf.get("stop_x") is not None and x > conf["stop_x"] and conf.get("stop") is None:
            conf["stop"] = t - 1e-3
        if conf.get("stop") is not None and t > conf["stop"]:      # остановка: приставил ногу и стоит
            Cn.append([t, "n" if k % 2 == 0 else "f", x - sstep * .7, 0.0, t + 30.0, ttc, None])
            last = Cn[-2]
            last[4] = t + 30.0
            break
        Cn.append([t, "n" if k % 2 == 0 else "f", x, 0.0, t + st, ttc, tag])
        t += ttc
        x += sstep
        k += 1
    C.update(conf)
    keys = [((c[0] + min(c[4], c[0] + c[5] * .6)) / 2, c[2] + 6) for c in Cn]
    if conf.get("stop") is not None:
        xe = (Cn[-1][2] + Cn[-2][2]) / 2 + 6
        keys = [kk for kk in keys if kk[0] < Cn[-1][0] - .05] + [(Cn[-1][0] + .25, xe), (Cn[-1][0] + 30, xe)]
    if conf.get("still"):
        keys = [(conf["a"] - 3.0, conf["x0"] - 24)] + [kk for kk in keys if kk[0] >= conf["a"]]
        keys.insert(1, (conf["a"], conf["x0"] - 24))
    ts, xs = zip(*keys)
    PL.clear()
    PL.update(C=Cn, hip_x=PchipInterpolator(np.array(ts), np.array(xs)))


def hip_at(t, bob=True):
    x = float(PL["hip_x"](t))
    if C.get("walk") and (C.get("stop") is not None and t > PL["C"][-1][0] + .2 or C.get("still") and t < C["a"]):
        y = -(LEG * 0.97 + AHW)
        if C.get("sit") is not None:
            y += C["sit_drop"] * ease_io(clamp((t - C["sit"]) / .45))
            x += C.get("sit_dx", 0.0) * ease_io(clamp((t - C["sit"]) / .45))
        return np.array([x, y])
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




# ═════════════════════════ телефон в руке бегущего (в L-единицах rdima) ═════════════════════════
PH_BODY, PH_SCREEN = "#2b2e36", "#9fd6ff"


def phone_L(rot_deg=-62.0, glow=1.0, scroll=0.0):
    """Функция для pose["held"]: телефон в кулаке ближней руки, экран к лицу (повёрнут rot_deg), свет экрана."""
    def fn(Wr, d):
        c = Wr + d * 26
        o = []
        if glow > 0.01:
            g = lib.rad_grad([(0, "#d8f2ff", .32 * glow), (1, "#d8f2ff", 0)], c[0] - 20, c[1] - 40, 150)
            o.append(f'<circle cx="{c[0] - 20:.1f}" cy="{c[1] - 40:.1f}" r="150" fill="url(#{g})"/>')
        body = lib.T(lib.rrect(-30, -66, 30, 66, 12), c[0], c[1], 1.0, rot_deg)
        scr = lib.T(lib.rrect(-24, -58, 24, 58, 8), c[0], c[1], 1.0, rot_deg)
        inner = blob(scr, PH_SCREEN)
        for k in range(4):                                # «лента» листается: цветные карточки без букв
            y = -50 + ((k * 30 + scroll * 120) % 120)
            card = lib.T(lib.rrect(-19, y, 19, y + 20, 4), c[0], c[1], 1.0, rot_deg)
            inner += blob(card, ("#ff8a7a", "#ffd166", "#7bd389", "#c9a7ff")[k], .9)
        o.append(dima.shape(body, PH_BODY, inner, w=3.6, seed=2501))
        return "".join(o)
    return fn


# ═════════════════════════ хук: бег с телефоном, Дима стареет ═════════════════════════
V_RUN = 232.0 / 0.176
HOOK = dict(a=-0.4, b=T1("s03") + 0.4, x0=0.0, tc=0.176, st=0.55, step=232.0, leap=None, stumble=None,
            lean_add=lambda t: -0.08)


def age_at(t):
    """0 школьник → 1 студент («телефоне», w3) → 2 борода («двенадцать», w4) → 3 седина («жизни», w6)."""
    return (smooth(W(3) - .05, W(3) + .3, t) + smooth(W(4) - .02, W(4) + .45, t) + smooth(W(6) - .02, W(6) + .42, t))


def backpack_at(t):
    return 1 - smooth(W(3) - .05, W(3) + .25, t)


def head_frame(p):
    """Центр головы (L) по позе — как в rdima.draw."""
    lean, ha = p["lean"], p["head_ang"]
    up = dima.rot(np.array([0.0, -1.0]), lean)
    fw = dima.rot(np.array([1.0, 0.0]), lean)
    neck = up * (dima.TORSO + 52) + fw * 30
    return neck + dima.rot(np.array([24.0, -96.0]), lean * .5 + ha)


def phone_pose(p, t):
    """Ближняя рука держит телефон перед лицом, голова опущена к экрану."""
    p["head_ang"] = 0.42
    hp = head_frame(p)
    tgt = hp + dima.rot(np.array([200.0, 95.0]), p["lean"] * .5 + .2) + np.array([0, 6 * math.sin(t * 9)])
    p["arms"]["n"] = ("ik", tuple(np.array(p["hip"]) + tgt * dima.BS), -1)
    th, bend = p["arms"]["f"][1], p["arms"]["f"][2]
    p["arms"]["f"] = ("ang", 0.25 + 0.45 * (th - 0.1), 1.5)          # дальняя рука машет слабее и не заходит за голову
    p["held"] = ("front", phone_L(-58.0, 1.0, t * 1.6))
    p["held_side"] = "n"
    return p


def dima_hook(t):
    a = age_at(t)
    ex = dict(age=a, lid=0.62, look=(0.55, 0.8), brows="calm", mouth="flat", hair=0.0)
    p = run_pose(t, expr=ex)
    p["backpack"] = backpack_at(t)
    return phone_pose(p, t)


def cat_hook(t, rel_fn):
    Cat.REL_FN[0] = rel_fn
    cs = Cat.state(t, lambda tt: hip_at(tt, bob=False)[0], C["step"] / C["tc"])
    cs["shoe"] = None
    cs["look"] = (0.8, -0.3)
    cs["blinks"] = (0.9, 2.3)
    return cs


def REL01(t):
    return 300.0


def REL02(t):
    return 200.0 - 60 * smooth(W(4), W(5) + .3, t)


def REL03(t):
    return 250.0


def cat_jump(t, t0, dur=.55, h=300.0):
    u = (t - t0) / dur
    return -h * math.sin(math.pi * u) if 0 < u < 1 else 0.0


def run_world(t, rel_fn, dima_fn, cat_dy=0.0, cat_look=None):
    lib.INK_K[0] = 1.0
    ds = dima_fn(t)
    dg, wr = dima.draw(ds)
    cs = cat_hook(t, rel_fn)
    if cat_look:
        cs["look"] = cat_look
    cg = Cat.draw(cs, t)
    if cat_dy:
        cg = f'<g transform="translate(0 {cat_dy:.1f})">{cg}</g>'
    sh = f'<g opacity=".22" transform="matrix(1 0 -0.9 -0.22 0 0)">{dg}</g>'
    return sh + dg + cg, dg + cg


def _setup(conf):
    plan(conf)
    Cat._grid.clear()
    Cat.SPAN[0], Cat.SPAN[1] = conf["a"] - 0.6, conf["b"] + 1.0


def run_frame(t, s, sx, gy, rel_fn, dima_fn, hook=False, cat_dy=0.0, rot_add=0.0, mood="rush", cat_look=None):
    cam = track_cam(t, s, sx, gy, shake=0.0 if NOCAM else 1.0, drift=0.0 if NOCAM else 1.0)
    cam = (cam[0], cam[1], cam[2], cam[3] + rot_add * (0 if NOCAM else 1))
    lib.DEFS.clear()
    world, mk = run_world(t, rel_fn, dima_fn, cat_dy, cat_look)
    if MASK:
        return mask_svg(mk, cam)
    st = R.street82(t, cam, mood)
    body = st["back"] + f'<g transform="{lib.cam(*cam)}">{st["ground"]}{world}</g>' + st["front"]
    if NOCAM:
        return lib.svg(body)
    if hook:
        return lib.svg(hook_wrap(body, t, W(3)) + title(t))
    return lib.svg(f'<rect width="1080" height="1920" fill="#a9cfe9"/>{body}' + title(t))


S_HOOK = 1.62


def frame_s01(t):
    _setup(HOOK)
    return run_frame(t, S_HOOK, 330.0, 1330.0, REL01, dima_hook, hook=True)


def frame_s02(t):
    _setup(HOOK)
    k = kick(t, W(4), .05, .25)
    return run_frame(t, 2.2, 330.0, 1640.0, REL02, dima_hook, rot_add=-1.5 + 2.5 * k, cat_look=(0.3, -0.9))


def frame_s03(t):
    _setup(HOOK)
    z = 3.1 + 0.25 * smooth(T0("s03"), T1("s03"), t)
    jump = cat_jump(t, W(6) + .12, .75, 230.0)
    return run_frame(t, z, 250.0, 700.0 + 500.0 * z, REL03, dima_hook, cat_dy=jump, cat_look=(0.2, -1.0))


# ═════════════════════════ петля s18: бег без телефона, кот подставляет голову ═════════════════════════
LOOP = dict(a=T0("s18") - 0.4, b=T1("s18") + 0.4, x0=0.0, tc=0.2, st=0.55, step=230.0, leap=None, stumble=None,
            lean_add=lambda t: -0.1)
V_LOOP = 230.0 / 0.2
PET = W(93) - 0.25           # кот прыгает под руку чуть раньше «гладили»


def dima_loop(t):
    ex = dict(age=1.15, lid=0.85, look=(0.6, -0.1), brows="calm", mouth="grin", hair=0.0)
    p = run_pose(t, expr=ex)
    lk = smooth(W(88) - .1, W(88) + .3, t) * (1 - smooth(W(90), W(91), t))      # «кот» — косится вниз на кота
    if lk > 0:
        p["head_ang"] = -0.12 + 0.3 * lk
        p["expr"]["look"] = (0.5, -0.1 + 0.9 * lk)
    u = smooth(PET - .25, PET + .1, t) * (1 - smooth(T1("s18") - .2, T1("s18") + .2, t))
    if u > 0:                                 # ближняя рука вниз-вперёд, ладонь на голове кота
        hip = np.array(p["hip"])
        tgt = hip + np.array([150.0, 200.0])
        th, bend = p["arms"]["n"][1], p["arms"]["n"][2]
        cur = hip + np.array([60.0, 120.0])
        p["arms"]["n"] = ("ik", tuple(cur + (tgt - cur) * u + np.array([0, 6 * math.sin(t * 30) * u])), -1)
        p["hands"]["n"] = ("open", 0.25)
        p["head_ang"] = -0.12 + 0.32 * u
        p["expr"].update(look=(0.55, 0.9), mouth="grin")
    return p


def REL18(t):
    return 230.0 - 80 * smooth(PET - .5, PET, t)


def frame_s18(t):
    _setup(LOOP)
    Cat.LANE_Y = 36.0
    dy = -90.0 * smooth(PET - .2, PET + .05, t) * (1 - smooth(T1("s18") - .1, T1("s18") + .3, t))
    look = (0.4, -1.0) if t > W(88) - .1 else None
    return run_frame(t, S_HOOK, 330.0, 1330.0, REL18, dima_loop, cat_dy=dy, mood="calm", cat_look=look)



# ═════════════════════════ общие помощники планов в комнатах ═════════════════════════
import cat as CT  # noqa: E402

FL = 1240.0                       # пол комнат (мир = кадр при камере (540, 960, 1))
GOLD, GOLD_SH = "#f2b84b", "#c98a22"


def ws(i):
    return WORDS[i]["start"]


def we(i):
    return WORDS[i]["end"]


def ramp(t, a, d):
    return clamp((t - a) / d)


def bump(t, a, up=.08, down=.3):
    """0 → 1 за up, затухание за down."""
    u = t - a
    if u <= 0:
        return 0.0
    return min(1.0, u / up) * (math.exp(-(u - up) / down) if u > up else 1.0)


def shake(t, a, amp=10.0, dur=.35, f=11.0):
    u = t - a
    if u <= 0 or u > dur * 3:
        return 0.0, 0.0
    e = math.exp(-u / dur * 2.5)
    return amp * e * math.sin(2 * math.pi * f * u), amp * .6 * e * math.cos(2 * math.pi * f * .8 * u)


def view(body, cx, cy, s, rot=0.0, bg="#e9dcc6", over=""):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def rect(x0, y0, x1, y1, col, op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{col}"{o}/>'


def shadow(x, y, rx, op=.2):
    return blob(ellipse_pts(x, y, rx, rx * .13, 20), "#3a2a1c", op)


ROOM = dict(wall="#eadcc4", wall_sh="#d9c6a8", floor="#b98d64", floor_sh="#a07650", base="#f4ead8", ln="#8a6a4c")


def room(x0=-1200.0, x1=2400.0, wall=None, floor=None, seed=0):
    P = dict(ROOM)
    if wall:
        P["wall"], P["wall_sh"] = wall, lib.mul(wall, (.93, .92, .9))
    if floor:
        P["floor"], P["floor_sh"] = floor, lib.mul(floor, (.88, .86, .84))
    o = [rect(x0, -1400, x1, FL, P["wall"])]
    g = lib.lin_grad([(0, P["wall_sh"], .0), (1, P["wall_sh"], .9)], 0, -800, 0, FL, units="userSpaceOnUse")
    o.append(f'<rect x="{x0}" y="-1400" width="{x1 - x0}" height="{FL + 1400}" fill="url(#{g})"/>')
    o.append(rect(x0, FL, x1, FL + 1400, P["floor"]))
    for k in range(int((x1 - x0) / 170) + 1):
        x = x0 + k * 170
        o.append(line([(x, FL + 4), (x - 120, FL + 700)], 2.0, P["floor_sh"], seed=3300 + seed + k, op=.6))
    o.append(shape(lib.rect_pts(x0, FL - 26, x1, FL + 4), P["base"], "", w=3.6, seed=3290 + seed))
    return "".join(o)


def window(x0, y0, x1, y1, sky="#9fd2f2", t=0.0, sun=None, moon=None):
    o = [shape(lib.rect_pts(x0 - 18, y0 - 18, x1 + 18, y1 + 18), "#f6eee0", "", w=4.4, seed=3400)]
    o.append(rect(x0, y0, x1, y1, sky))
    if sun is not None:
        g = lib.rad_grad([(0, "#fff7d0", .9), (1, "#fff7d0", 0)], sun[0], sun[1], 110)
        o.append(f'<circle cx="{sun[0]:.1f}" cy="{sun[1]:.1f}" r="110" fill="url(#{g})"/>'
                 f'<circle cx="{sun[0]:.1f}" cy="{sun[1]:.1f}" r="38" fill="#ffe27a"/>')
    if moon is not None:
        o.append(f'<circle cx="{moon[0]:.1f}" cy="{moon[1]:.1f}" r="32" fill="#f4f0dc"/>'
                 f'<circle cx="{moon[0] + 14:.1f}" cy="{moon[1] - 8:.1f}" r="28" fill="{sky}"/>')
    inner = "".join(o[1:])
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    out = o[0] + f'<g clip-path="url(#{c})">{inner}</g>'
    out += line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], 6, "#f6eee0", taper=0, wmin=1, seed=3401)
    out += line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], 6, "#f6eee0", taper=0, wmin=1, seed=3402)
    out += f'<path d="{lib.ink_closed(lib.rect_pts(x0, y0, x1, y1), 4.0, seed=3403)}" fill="{INK}"/>'
    return out


def sofa(x0, x1, y, col="#5a7fb5"):
    """Диван: сиденье верхом на y; спинка выше, подлокотники по краям."""
    sh = lib.mul(col, (.82, .82, .86))
    o = [shape(lib.rrect(x0 + 40, y - 330, x1 - 40, y + 20, 40), sh, "", w=5, seed=3500)]
    o.append(shape(lib.rrect(x0 + 60, y - 20, x1 - 60, y + 150, 30), col, blob(lib.rect_pts(x0 + 60, y + 90, x1 - 60, y + 150), sh, .6), w=5, seed=3501))
    for k, (a, b) in enumerate(((x0 - 10, x0 + 110), (x1 - 110, x1 + 10))):
        o.append(shape(lib.rrect(a, y - 130, b, y + 160, 45), col, blob(lib.rect_pts(a, y + 40, b, y + 160), sh, .5), w=5, seed=3502 + k))
    for x in (x0 + 40, x1 - 60):
        o.append(rect(x, y + 160, x + 22, y + 200, "#5b3d26"))
    return "".join(o)


def phone_up(x, y, k=1.0, rot=0.0, glow=1.0, scroll=0.0, feed=True, dim=0.0):
    """Телефон экраном к зрителю (ЦЕНТР x, y; 120×240·k), без букв: цветные карточки ленты листаются."""
    o = []
    if glow > .01:
        g = lib.rad_grad([(0, "#d8f2ff", .35 * glow), (1, "#d8f2ff", 0)], x, y, 260 * k)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{260 * k:.1f}" fill="url(#{g})"/>')
    body = lib.T(lib.rrect(-60, -120, 60, 120, 18), x, y, k, rot)
    scr = lib.T(lib.rrect(-50, -106, 50, 106, 10), x, y, k, rot)
    inner = blob(scr, lib.mix(PH_SCREEN, "#3b4250", dim))
    if feed:
        for j in range(6):
            yy = -100 + ((j * 42 + scroll * 160) % 252) - 20
            card = lib.T(lib.rrect(-42, yy, 42, yy + 30, 6), x, y, k, rot)
            inner += blob(card, ("#ff8a7a", "#ffd166", "#7bd389", "#c9a7ff", "#ff9ec7", "#6cc4ff")[j], .9 * (1 - dim))
    c = lib.clip_of(scr)
    o.append(shape(body, PH_BODY, f'<g clip-path="url(#{c})">{inner}</g>', w=4.0 * max(.6, k), seed=3600))
    return "".join(o)


def fig(x, y, sc, expr, pose=None, feet="stand", lean=None, head_ang=None, arms=None, hands=None, layers=None, flip=False):
    kw = {}
    if pose:
        kw.update(people.pose_kw(pose, x, y, sc))
    if feet == "stand":
        kw.update(people.stand_kw(x, y, sc))
    elif feet == "sit":
        kw.update(people.sit_kw(x, y, sc))
    elif isinstance(feet, dict):
        kw["feet"] = feet
    if lean is not None:
        kw["lean"] = lean
    if head_ang is not None:
        kw["head_ang"] = head_ang
    if arms is not None:
        kw["arms"] = arms
    if hands is not None:
        kw["hands"] = hands
    return people.figure("dima", x, y, sc, expr=expr, layers=layers, flip=flip, **kw)


def dima_phone(x, y, sc, expr, t, feet="stand", lean=0.12, glow=1.0, ph_k=None, scroll_v=1.6, extra_arms=None, head_ang=0.32):
    """Дима держит телефон двумя руками перед грудью и смотрит в экран. -> (svg, res, точка телефона)."""
    arms = {"f": ("ik", (x + 210 * sc, y - 330 * sc), -1), "n": ("ik", (x + 300 * sc, y - 335 * sc), -1)}
    if extra_arms:
        arms.update(extra_arms)
    hands = {"f": {"dir": (.9, -.3), "curl": (.55, .55, .6, .62), "thumb": .5}, "n": {"dir": (-.6, -.7), "curl": (.6, .6, .65, .68), "thumb": .6}}
    base = fig(x, y, sc, expr, feet=feet, lean=lean, head_ang=head_ang, arms=arms, hands=hands, layers=("legs", "pelvis", "arm_f", "body"))
    near = fig(x, y, sc, expr, feet=feet, lean=lean, head_ang=head_ang, arms=arms, hands=hands, layers=("arm_n",))
    wf, wn = np.array(base["wrist"]["f"]), np.array(base["wrist"]["n"])
    pp = (wf + wn) / 2 + np.array([10 * sc, -60 * sc])
    ph = phone_up(pp[0], pp[1], (ph_k or 0.9) * sc / .5 * .5, -14, glow, t * scroll_v)
    return base["svg"] + ph + near["svg"], base, pp


def cat(x, y, k, t, **st):
    return CT.draw(x, y, k, st, t)


def gold_drop(x, y, k=1.0, rot=0.0):
    return PR.drop(x, y, k, rot, col=GOLD)


def grains(pts, t, n=30, seed=0, k=1.0, speed=1.0, up=False, col=GOLD):
    """Песчинки летят по ломаной pts (от начала к концу) непрерывной струёй."""
    P_ = np.array(pts, float)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P_, axis=0), axis=1))]
    o = []
    rs = np.random.RandomState(5100 + seed)
    for i in range(n):
        ph = (rs.uniform() + t * speed) % 1.0
        d = ph * seg[-1]
        j = min(len(seg) - 2, int(np.searchsorted(seg, d) - 1))
        j = max(j, 0)
        u = (d - seg[j]) / max(1e-6, seg[j + 1] - seg[j])
        p = P_[j] + (P_[j + 1] - P_[j]) * u + rs.uniform(-12, 12, 2) * k
        r = rs.uniform(4, 8) * k
        o.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r:.1f}" fill="{col}" stroke="{INK}" stroke-width="{1.6 * k:.2f}"/>')
    return "".join(o)


def bez(a, c, b, n=16):
    a, c, b = map(np.array, (a, c, b))
    return [tuple((1 - u) ** 2 * a + 2 * u * (1 - u) * c + u * u * b) for u in np.linspace(0, 1, n)]


def dark(op, col="#14183a"):
    return f'<rect x="-3000" y="-3000" width="7000" height="7000" fill="{col}" opacity="{op:.3f}"/>' if op > .005 else ""


# ═════════════════════════ s04: диван, «посчитал свои» — песочные часы столбиком из экрана ═════════════════════════
SOF_HIP = (430.0, 1010.0)
SOF_K = 0.62


def sofa_scene(t, sky="#f2b98a", sun=None, moon=None, light=0.0):
    o = [room(), window(-60, 260, 300, 700, sky, t, sun, moon), sofa(140, 1060, 1060)]
    return "".join(o)


def frame_s04(t):
    a = T0("s04")
    rec = smooth(ws(11) - .05, ws(11) + .25, t)
    ex = dict(people.EXPR["dima"]["focus"]) if rec < .5 else dict(people.EXPR["dima"]["saucer"])
    ex["age"] = 1.2
    x, y = SOF_HIP
    dg, res, pp = dima_phone(x, y, SOF_K, ex, t, feet="sit", lean=0.12 - 0.3 * rec, head_ang=0.3 - 0.45 * rec)
    o = [sofa_scene(t)]
    o.append(cat(985, 1050, 0.62, t, look=(-.3, -.8 * smooth(ws(9), ws(9) + .3, t)), tail=8 * math.sin(t * 3),
                 blink=1.0 if abs(t - (a + .9)) < .06 else 0.0))
    o.append(dg)
    n = 22
    c0 = smooth(ws(8) - .05, ws(12), t)                    # «посчитал» → «поверил»: столбик часов растёт
    for i in range(n):
        ti = ws(8) - .05 + (ws(12) - ws(8)) * i / n
        if t < ti:
            break
        u = back_out(clamp((t - ti) / .18))
        py = pp[1] - 120 - i * 76
        px = pp[0] + 60 + 6 * math.sin(i * 1.7)
        if u < 1:                                           # вылетает из экрана к своему месту
            px, py = pp[0] + (px - pp[0]) * u, pp[1] + (py - pp[1]) * u
        o.append(PR.hourglass(px, py, 0.34 * min(1.0, .3 + u), rot=4 * math.sin(i + t * 3), flow=1.0, top=.6, t=t, seed=i))
    _ = c0
    dx, dy = shake(t, ws(11), 14)
    z = 1.0 + 0.06 * ramp(t, a, T1("s04") - a) + 0.05 * bump(t, ws(11))
    cy = 860 - 160 * smooth(ws(9), ws(12), t)
    return view("".join(o), 560 + dx, cy + dy, z, 0.8 * math.sin(t * 1.3))


def back_out(u, s=1.7):
    return lib.back_out(u, s)


# ═════════════════════════ s05: тот же диван, за окном сменяются дни ═════════════════════════
def frame_s05(t):
    a = T0("s05")
    per = (ws(18) - ws(13)) / 2.0                          # два полных дня за «пять часов в день, каждый день»
    ph = ((t - a + per * .15) / per) % 1.0
    day = .5 + .5 * math.cos(2 * math.pi * (ph - .25))     # 1 — полдень
    sky = lib.mix("#18204a", "#9fd2f2", day)
    sun = (120 + 260 * math.cos(math.pi * (ph * 2 % 1)), 640 - 380 * math.sin(math.pi * min(1, ph * 2))) if ph < .5 else None
    moon = (120 + 260 * math.cos(math.pi * ((ph - .5) * 2)), 640 - 380 * math.sin(math.pi * (ph - .5) * 2)) if ph >= .5 else None
    ex = dict(people.EXPR["dima"]["zombie"], age=1.2)
    x, y = SOF_HIP
    dg, res, pp = dima_phone(x, y, SOF_K, ex, t, feet="sit", lean=0.12, head_ang=0.3, scroll_v=2.4)
    o = [sofa_scene(t, sky, sun, moon)]
    sl = 1 - day
    o.append(cat(985, 1050, 0.62, t, sleep=clamp(sl * 1.4 - .2), look=(-.4, -.2)))
    o.append(dg)
    o.append(dark(.5 * (1 - day)))
    o.append(phone_up(pp[0], pp[1], SOF_K * .9, -14, 1.0 + .8 * (1 - day), (t) * 2.4) if day < .6 else "")
    dx, dy = shake(t, ws(16), 8)
    dx2, dy2 = shake(t, ws(18), 8)
    return view("".join(o), 520 + dx + dx2, 820 + dy + dy2, 0.86 + 0.04 * ramp(t, a, 2.2), 0)


# ═════════════════════════ s06: призыв ═════════════════════════
def frame_s06(t):
    import story_cta_tg as tg
    press = ws(22) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=os.path.join(STORY, "common"))


# ═════════════════════════ s07: песок из груди утекает в экран ═════════════════════════
def frame_s07(t):
    a = T0("s07")
    fl = bump(t, ws(29), .06, .35)                         # «двенадцать» — на миг седеет
    ex = dict(people.EXPR["dima"]["dull"], age=1.2 + 1.8 * fl)
    x, y = 470.0, 860.0
    sc = 0.62
    dg, res, pp = dima_phone(x, y, sc, ex, t, lean=0.08, head_ang=0.3)
    o = [room(wall="#e5d3c8")]
    o.append(shadow(x + 40, FL + 20, 200))
    o.append(dg)
    chest = np.array([x + 40 * sc, y - 260 * sc])
    thick = 1 + 1.4 * smooth(ws(28), ws(29) + .2, t)
    path = bez(chest, (chest[0] + 260, chest[1] - 260), (pp[0], pp[1] - 30))
    o.append(grains(path, t, n=int(26 * thick), seed=1, k=1.0, speed=1.3))
    o.append(blob(ellipse_pts(chest[0], chest[1], 40, 30, 12), GOLD, .35 + .3 * math.sin(t * 9) ** 2))
    o.append(phone_up(pp[0], pp[1], .56, -14, 1.2, t * 1.6))
    cx_ = 840 + 30 * math.sin(t * 2)
    paw = .5 + .5 * math.sin(t * 8)
    o.append(cat(cx_, FL + 10, 0.7, t, look=(-.6, -.9), paw=paw, paw_dx=-60))
    if fl > .02:
        o.append(f'<rect x="-2000" y="-2000" width="5000" height="5000" fill="#ffffff" opacity="{.35 * fl:.3f}"/>')
    z = 1.0 + 0.18 * ease_io(ramp(t, a, T1("s07") - a)) + 0.06 * fl
    dx, dy = shake(t, ws(29), 12)
    return view("".join(o), 560 + 40 * ramp(t, a, 1.9) + dx, 760 + dy, z, 0)


FRAMES = {k[6:]: v for k, v in dict(globals()).items() if k.startswith("frame_s")}


def frame(sid, t):
    return FRAMES[sid](t)
