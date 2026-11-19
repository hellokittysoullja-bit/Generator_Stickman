"""Рилс 84 «Год пролетел?» — все клипы (один каталог кода). frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу wN); числа в коде — длительности движений.
Бег хука — код рилса 82 (ext_c: план шагов, rdima.py, rcat.py); заголовок — common/big_title.py; призыв — scripts/story_cta_tg.py.
NOCAM=1 — без влёта, тряски и заголовка (замер движения рисунка); MASK=1 — только рисунок хука белым на чёрном (замер заполнения)."""
import json
import math
import os
import random
import sys

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(STORY)))
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
sys.path.insert(1, os.path.join(REPO, "scripts"))
import big_title  # noqa: E402
import lib  # noqa: E402
import people as PE  # noqa: E402
import rcat as Cat  # noqa: E402
import rdima as dima  # noqa: E402
import room as R  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, smooth  # noqa: E402,F401

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




MASK_F = '<filter id="mk84"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 9 0"/></filter>'


def mask_svg(world_mask, cam):
    lib.DEFS.append(MASK_F)
    return lib.svg('<rect width="1080" height="1920" fill="#000"/>'
                   f'<g transform="{lib.cam(*cam)}"><g filter="url(#mk84)">{world_mask}</g></g>')


# ═════════════════════════ хук s01–s02: погоня ═════════════════════════


PIV = 600.0     # центр влёта — у головы Димы


def T0(sid):
    return SHOT[sid]["t0"]


def T1(sid):
    return SHOT[sid]["t1"]


def title(t):
    """Заголовок хука: экранный слой s01–s03, уходит на слове shots.json title.t_out_word."""
    if NOCAM or MASK:
        return ""
    tt = SH["title"]
    return big_title.layer(t, text=tt["text"], t_in=tt["t_in"], t_out=W(tt["t_out_word"]), hits=[W(i) for i in tt["hits"]])


# ═════════════════════════ листки календаря (без цифр: цветная полоса месяца, пустая сетка) ═════════════════════════
MONTHS = ["#8fc3ea", "#6fa8d8", "#b5d8f0",            # зима: снег
          "#8fd16a", "#5fb85a", "#b6e06a",            # весна: зелень
          "#f6c945", "#ffb03a", "#f39a5a",            # лето
          "#e5733a", "#d4462f", "#c0843a"]            # осень: листопад
PAPER = "#fbf8f1"
R.ST82["winter"] = dict(R.ST82["rush"], sky0="#8eb4d8", sky1="#dce8f2", sky2="#f7efe2", far="#c3d0d8", far2="#aebdc8",
                        lawn="#eef3f6", tree="#e3ecf1", tree_sh="#b8c8d3", walk="#d8dce0", walk_sh="#b7bdc4", walk_lit="#eef1f3")


def leaf(x, y, k, rot, mi, flip=1.0, seed=0, op=1.0):
    """Листок отрывного календаря: (x, y) — центр, k — масштаб (100×124 при k=1), mi — месяц (цвет полосы), flip −1…1 —
    кувырок (сжатие по ширине). Ни цифр, ни букв: полоса месяца, дырочки переплёта, пустая сетка дней."""
    col = MONTHS[mi % 12]
    fx = max(0.08, abs(flip)) * (1 if flip >= 0 else -1)
    sh = lib.mul(col, (.82, .82, .86))
    o = [shape(lib.rect_pts(-50, -62, 50, 62, 6), PAPER,
               f'<rect x="-50" y="-62" width="100" height="30" fill="{col}"/><rect x="-50" y="-36" width="100" height="5" fill="{sh}" opacity=".6"/>'
               + "".join(f'<rect x="{-40 + 21 * c}" y="{-22 + 19 * r}" width="16" height="14" rx="2" fill="{col}" opacity="{.16 + .1 * ((c + r + seed) % 3 == 0)}"/>'
                         for r in range(4) for c in range(4)),
               w=3.2, seed=4000 + seed % 997)]
    for hx in (-24, 0, 24):
        o.append(f'<ellipse cx="{hx}" cy="-54" rx="4" ry="3" fill="{INK}" opacity=".75"/>')
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k * fx:.4f} {k:.4f})"' + (f' opacity="{op:.3f}"' if op < 1 else "")
            + f'>{"".join(o)}</g>')


_RNG = random.Random(84)
STORM = [dict(layer=L, x0=_RNG.uniform(0, 1500), y0=_RNG.uniform(80, 1300), ph=_RNG.uniform(0, 6.3), mi=_RNG.randrange(12),
              spin=_RNG.uniform(-260, 260), tumble=_RNG.uniform(3, 7), wob=_RNG.uniform(30, 90), seed=_RNG.randrange(999))
         for L, n in ((0, 20), (1, 14), (2, 8)) for _ in range(n)]
LAYER_K = (0.5, 0.85, 1.45)
LAYER_V = (700.0, 1150.0, 1900.0)


def storm(t, layers=(0, 1, 2), speed=1.0, fall=0.0, drop=()):
    """Метель листков в экранных координатах: летят справа налево (Дима бежит им навстречу). speed — доля скорости,
    fall — падение вниз (петля: медленно падают). drop — индексы листков, которые не рисуются (их ведёт сцена)."""
    o = []
    for i, s in enumerate(STORM):
        if s["layer"] not in layers or i in drop:
            continue
        L = s["layer"]
        v = LAYER_V[L] * speed
        span = 1080 + 500
        x = (s["x0"] - v * t) % span - 250
        y = s["y0"] + s["wob"] * math.sin(t * 2.3 + s["ph"]) + fall * ((t * 90 + s["x0"]) % 1500 - 200)
        if fall:
            y = (s["y0"] + fall * 160 * t + 40 * math.sin(t * 1.3 + s["ph"])) % 1500 - 150
        o.append(leaf(x, y, LAYER_K[L], s["spin"] * t * speed + s["ph"] * 40, s["mi"],
                      math.cos(s["tumble"] * t * (speed if speed > .3 else .3) + s["ph"]), s["seed"], op=(.75 if L == 0 else 1.0)))
    return "".join(o)


def to_screen(p, cam):
    cx, cy, s, rot = cam
    v = (np.array(p, float) - np.array([cx, cy])) * s
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return np.array([540 + v[0] * c - v[1] * sn, 960 + v[0] * sn + v[1] * c])


def face_world(p):
    """Середина лица Димы рилса 82 (rdima) в мире по позе."""
    H = np.array(p["hip"], float)
    lean, ha = p["lean"], p.get("head_ang", 0.0)
    up = dima.rot(np.array([0.0, -1.0]), lean)
    fw = dima.rot(np.array([1.0, 0.0]), lean)
    neck = up * (dima.TORSO + 52) + fw * 30
    hpos = neck + dima.rot(np.array([24.0, -96.0]), lean * .5 + ha)
    return H + (hpos + dima.rot(np.array([48.0, -6.0]), lean * .5 + ha)) * dima.BS


def splat_leaf(t, t_hit, start, face, stick=0.3, mi=3, k=1.0, seed=7, away=(-900, -300)):
    """Листок прилетает из start в face к t_hit, липнет на stick с, отрывается и уносится. -> SVG (экран) или ''."""
    fly = .26
    if t < t_hit - fly or t > t_hit + stick + .5:
        return ""
    if t < t_hit:
        u = (t - (t_hit - fly)) / fly
        p = np.array(start) + (np.array(face) - np.array(start)) * u ** 1.4 + np.array([0, -60 * math.sin(math.pi * u)])
        return leaf(p[0], p[1], k, 30 * (1 - u) - 8, mi, math.cos(9 * u), seed)
    if t < t_hit + stick:
        sq = 1 + .12 * math.exp(-(t - t_hit) / .05)
        return leaf(face[0], face[1], k * sq, -8 + 3 * math.sin((t - t_hit) * 30), mi, 1.0, seed)
    u = (t - t_hit - stick) / .5
    p = np.array(face) + np.array(away) * ease_in(u, 1.6)
    return leaf(p[0], p[1], k, -8 - 260 * u, mi, math.cos(10 * u), seed)


# ═════════════════════════ хук: бег сквозь метель ═════════════════════════
V_RUN = 232.0 / 0.176
HOOK = dict(a=-0.4, b=T1("s03") + 0.6, x0=0.0, tc=0.176, st=0.55, step=232.0, leap=None, stumble=None)
CAT_REL = 330.0
_CUR = [None]


def ensure(kind):
    if _CUR[0] == kind:
        return
    _CUR[0] = kind
    if kind == "hook":
        plan(HOOK)
        Cat.REL_FN[0] = lambda t: CAT_REL
        Cat.SPAN[0], Cat.SPAN[1] = -1.0, 5.0
        Cat._grid.clear()
    elif kind == "walk":
        plan(dict(a=T0("s18") - 1.5, b=T1("s18") + .5, x0=0.0, tc=0.5, st=0.62, step=170.0, walk=True))


def dima_pose(t, face_hit=0.0):
    p = run_pose(t)
    if face_hit > 0:
        p["expr"].update(lid=1.0, brows="up", mouth="gape")
    return p


def cat_run(t):
    cs = Cat.state(t, lambda tt: hip_at(tt, bob=False)[0], V_RUN)
    cs["shoe"] = None
    cs["look"] = (0.6, -0.5)
    cs["blinks"] = (0.95,)
    return cs


def run_cam(t, s, sx, gy, shake=1.0, drift=1.0):
    return track_cam(t, s, sx, gy, shake=0.0 if NOCAM else shake, drift=0.0 if NOCAM else drift)


def frame_s01(t):
    ensure("hook")
    s = 1.55
    cam = run_cam(t, s, 380.0, 1300.0)
    lib.DEFS.clear()
    p = dima_pose(t, kick(t, W(1), .03, .25))
    dg, _ = dima.draw(p)
    cg = Cat.draw(cat_run(t), t)
    world = f'<g opacity=".2" transform="matrix(1 0 -0.9 -0.22 0 0)">{dg}</g>' + dg + cg
    face = to_screen(face_world(p), cam)
    hitl = splat_leaf(t, W(1), (1250, face[1] - 260), face, stick=.28, mi=1, k=1.15, seed=11)
    if MASK:
        lib.DEFS.append(MASK_F)
        return lib.svg('<rect width="1080" height="1920" fill="#000"/><g filter="url(#mk84)">'
                       f'<g transform="{lib.cam(*cam)}">{world}</g>{storm(t, (1, 2))}{hitl}</g>')
    st = R.street82(t, cam, "winter")
    body = (st["back"] + storm(t, (0,)) + f'<g transform="{lib.cam(*cam)}">{st["ground"]}{world}</g>' + st["front"]
            + storm(t, (1, 2)) + hitl)
    if NOCAM:
        return lib.svg(body)
    return lib.svg(hook_wrap(body, t, W(1)) + title(t))



def cat_flip(svg_, x):
    """Кот common/cat.py смотрит влево — зеркалим вокруг x, чтобы бежал вправо."""
    return f'<g transform="translate({2 * x:.2f} 0) scale(-1 1)">{svg_}</g>'


def frame_s02(t):
    """Низкий ракурс: кот (common/cat.py) в прыжке ловит листок пастью и лапами на «год» (w5), Дима проносится слева."""
    ensure("hook")
    a, b = T0("s02") - .2, T1("s02") + .2
    k = .72
    catx = lambda tt: hip_at(tt, bob=False)[0] + 470.0      # noqa: E731
    u = .3 + .62 * (t - a) / (W(5) + .36 - a)
    u = min(1.0, u) if t < W(5) + .36 else min(1.0, .92 + .08 * (t - W(5) - .36) / .2)
    p0, p1 = (catx(a), 0.0), (catx(W(5) + .5), 0.0)
    # кот в мире — по формуле cat_jump; позиция для листка
    e = clamp((u - .4) / .45)
    cpos = np.array(p0) + (np.array(p1) - np.array(p0)) * e + np.array([0, -190 * 4 * e * (1 - e)])
    s = 1.6
    cam = (float(cpos[0]) + 40, -(1330 - 960) / s - (0 if NOCAM else 12 * math.sin(t * 3)), s,
           0 if NOCAM else -2.5 + 2 * kick(t, W(5), .04, .2))
    lib.DEFS.clear()
    caught = t >= W(5)
    st = dict(perk=1.0, look=(-.3, -.6), paw=1.0 if not caught else .6, smile=.8 if caught else 0.0, flame_e=1.5)
    if caught:
        st["mouth_item"] = leaf(770, 1150, 1.5, 70 + 6 * math.sin(t * 20), 6, 1.0, 21)
    cj = PE.cat_jump(p0, p1, k, u, t, st, height=190.0)
    mouth = to_screen(cpos + np.array([75 * k, -150 * k]), cam)
    pd = dima_pose(t)
    dg, _ = dima.draw(pd)
    world = dg + cat_flip(cj, float(cpos[0]))
    fl = "" if caught else splat_leaf(t, W(5), (1200, mouth[1] - 300), mouth, stick=0, mi=6, k=1.0, seed=21)
    if MASK:
        lib.DEFS.append(MASK_F)
        return lib.svg('<rect width="1080" height="1920" fill="#000"/><g filter="url(#mk84)">'
                       f'<g transform="{lib.cam(*cam)}">{world}</g>{storm(t, (1, 2))}{fl}</g>')
    stt = R.street82(t, cam, "winter")
    body = (stt["back"] + storm(t, (0,)) + f'<g transform="{lib.cam(*cam)}">{stt["ground"]}{world}</g>' + stt["front"]
            + storm(t, (1, 2), drop=(30, 31)) + fl)
    return lib.svg(body + title(t))


def frame_s03(t):
    """Крупнее, камера чуть впереди и ниже: листок облепляет лицо на «кончился» (w7), Дима бежит вслепую, листок срывает ветром."""
    ensure("hook")
    s = 2.15
    a = T0("s03") - .2
    uu = ease_out(clamp((t - a) / .5), 3)
    cam = run_cam(t, s, 300 + 160 * uu, 1700.0, shake=1.2, drift=.6)
    cx, cy, s_, rot = cam
    cam = (cx, cy, s_, rot + (0 if NOCAM else -5 + 3 * uu))
    lib.DEFS.clear()
    th = stress(7, .15)
    pd = dima_pose(t, 1.0 if th < t < th + .8 else 0.0)
    if t > th + .55:
        pd["expr"].update(lid=1.0, brows="up", mouth="gape", look=(.9, -.2))
    dg, _ = dima.draw(pd)
    cg = Cat.draw(cat_run(t), t)
    face = to_screen(face_world(pd), cam)
    fl = splat_leaf(t, th, (1250, face[1] - 200), face, stick=.55, mi=10, k=2.0, seed=31, away=(-1100, -500))
    world = cg + dg
    if MASK:
        lib.DEFS.append(MASK_F)
        return lib.svg('<rect width="1080" height="1920" fill="#000"/><g filter="url(#mk84)">'
                       f'<g transform="{lib.cam(*cam)}">{world}</g>{storm(t, (1, 2))}{fl}</g>')
    stt = R.street82(t, cam, "winter")
    body = (stt["back"] + storm(t, (0,)) + f'<g transform="{lib.cam(*cam)}">{stt["ground"]}{world}</g>' + stt["front"]
            + storm(t, (1, 2)) + fl)
    if not NOCAM:
        z = 1 + .08 * kick(t, th, .05, .2)
        body = f'<g transform="translate(540 {PIV}) scale({z:.4f}) translate(-540 {-PIV})">{body}</g>'
    return lib.svg(f'<rect width="1080" height="1920" fill="#a9cfe9"/>{body}' + title(t))


# ═════════════════════════ общие помощники сцен s04–s18 ═════════════════════════
def view(body, cx=540.0, cy=960.0, s=1.0, rot=0.0, bg="#f4efe4", over=""):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def grad_bg(c0, c1):
    g = lib.lin_grad([(0, c0, 1), (1, c1, 1)], 0, 0, 0, 1920, units="userSpaceOnUse")
    return f'<rect x="-1500" y="-1500" width="4080" height="4920" fill="url(#{g})"/>'


def drift(t, a=1.0):
    return 10 * a * math.sin(t * 1.7 + .5), 7 * a * math.sin(t * 2.3), .5 * a * math.sin(t * 1.3)


def dfig(x, hip, k, expr="calm82", pose="d82_rest", t=0.0, **kw):
    return PE.dima82(x, hip, k, expr, pose, t=t, feet=kw.pop("feet", PE.stand_kw(x, hip, k)["feet"]), **kw)


def ex(name, **kw):
    d = dict(PE.EXPR["dima"][name])
    d.update(kw)
    return d


def cat(x, y, k, st, t, right=False):
    c = PE.cat_svg(x, y, k, st, t)
    return cat_flip(c, x) if right else c


def card_pic(kind, t=0.0):
    """Картинка дня в рамке 200×150 (0..200, 0..150), без букв."""
    if kind == "sea":
        return ('<rect width="200" height="150" fill="#8fd0f0"/><circle cx="150" cy="40" r="22" fill="#ffd84a"/>'
                + "".join(f'<path d="M0 {90 + 18 * i} q25 -14 50 0 t50 0 t50 0 t50 0 V150 H0Z" fill="{c}"/>'
                          for i, c in enumerate(("#3f9fd8", "#2f86c4", "#236fa8"))))
    if kind == "mount":
        return ('<rect width="200" height="150" fill="#bfe3f7"/><path d="M-10 150 L70 40 L120 110 L150 70 L215 150Z" fill="#6f8fa8"/>'
                '<path d="M70 40 L88 66 L74 62 L60 70 L56 60Z M150 70 L162 86 L148 82 L140 86Z" fill="#fff"/>'
                '<rect y="128" width="200" height="22" fill="#7cc56a"/>')
    if kind == "fire":
        o = '<rect width="200" height="150" fill="#1f2a5a"/>'
        for j, (cx, cy, c) in enumerate(((60, 55, "#ff6a8a"), (140, 45, "#ffd84a"), (105, 95, "#6ae0ff"))):
            r = 26 + 6 * math.sin(t * 6 + j)
            o += "".join(f'<line x1="{cx}" y1="{cy}" x2="{cx + r * math.cos(a / 6 * math.pi):.1f}" y2="{cy + r * math.sin(a / 6 * math.pi):.1f}" '
                         f'stroke="{c}" stroke-width="4" stroke-linecap="round"/>' for a in range(12))
        return o
    if kind == "train":
        return ('<rect width="200" height="150" fill="#ffe6a8"/><rect y="112" width="200" height="38" fill="#9cc46e"/>'
                '<rect x="20" y="66" width="150" height="46" rx="10" fill="#e2463c"/><rect x="34" y="76" width="26" height="18" rx="3" fill="#cfeaf7"/>'
                '<rect x="72" y="76" width="26" height="18" rx="3" fill="#cfeaf7"/><rect x="110" y="76" width="26" height="18" rx="3" fill="#cfeaf7"/>'
                '<circle cx="50" cy="114" r="9" fill="#333"/><circle cx="140" cy="114" r="9" fill="#333"/>')
    # серый одинаковый день: стол, окно, всё одного цвета
    return ('<rect width="200" height="150" fill="#c9cbcf"/><rect x="120" y="22" width="56" height="44" fill="#dfe1e4"/>'
            '<rect x="20" y="96" width="160" height="10" fill="#9fa3a9"/><rect x="60" y="58" width="56" height="38" rx="4" fill="#8d9197"/>')


def card(x, y, k, kind, rot=0.0, t=0.0, seed=0, op=1.0):
    """Карточка-день: (x, y) — центр, 220×170 при k=1."""
    c = lib.clip_rect(-100, -75, 200, 150, 10)
    gray = kind == "gray"
    o = shape(lib.rrect(-110, -85, 110, 85, 14), "#f7f4ee" if not gray else "#e1e2e4",
              blob(lib.rrect(-110, 55, 110, 85, 10), "#d9d4c8" if not gray else "#c6c8cb", .6), w=4.0, seed=5000 + seed)
    o += f'<g clip-path="url(#{c})"><g transform="translate(-100 -75)">{card_pic(kind, t)}</g></g>'
    o += shape(lib.rrect(-100, -75, 100, 75, 10), "none", w=3.0, seed=5100 + seed)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f}) scale({k:.4f})" opacity="{op:.3f}">{o}</g>'


def burst(x, y, r, t0, t, col="#ffd23f", n=10, life=.4):
    u = (t - t0) / life
    if u < 0 or u > 1:
        return ""
    o = ""
    for i in range(n):
        a = 2 * math.pi * i / n + .3
        r0, r1 = r * (.7 + .8 * u), r * (1.0 + 1.2 * u)
        o += line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))], 9 * (1 - u) + 2, col,
                  seed=6000 + i, taper=.5)
    return o


# ═════════════════════════ s04: новогодняя ночь → один миг → декабрь ═════════════════════════
def tree(x, y, k, t, lit=1.0):
    o = shape([(x - 14 * k, y), (x + 14 * k, y), (x + 14 * k, y - 50 * k), (x - 14 * k, y - 50 * k)], "#7a5a40", w=3, seed=701)
    for i, (w_, h_) in enumerate(((190, 210), (150, 190), (105, 170))):
        yb = y - 40 * k - i * 140 * k
        o += shape([(x - w_ * k, yb), (x + w_ * k, yb), (x, yb - h_ * k)], ("#2f8a4a", "#379a52", "#40a85a")[i],
                   blob([(x, yb), (x + w_ * k, yb), (x, yb - h_ * k)], "#246e3a", .5), w=4, seed=710 + i)
    rng = random.Random(4)
    for i in range(22):
        lv = rng.randrange(3)
        w_ = (190, 150, 105)[lv] * k * rng.uniform(.2, .8)
        yb = y - 40 * k - lv * 140 * k - rng.uniform(20, 120) * k
        xx = x + rng.choice((-1, 1)) * w_ * (1 - (y - 40 * k - lv * 140 * k - yb) / ((210, 190, 170)[lv] * k))
        c = ("#ffd23f", "#ff6a8a", "#6ae0ff", "#ff9a3a")[i % 4]
        on = lit * (.55 + .45 * math.sin(t * 7 + i * 1.7))
        o += f'<circle cx="{xx:.1f}" cy="{yb:.1f}" r="{9 * k:.1f}" fill="{c}" opacity="{max(.15, on):.2f}"/>'
        if on > .6:
            o += f'<circle cx="{xx:.1f}" cy="{yb:.1f}" r="{22 * k:.1f}" fill="{c}" opacity="{.25 * on * lit:.2f}"/>'
    o += f'<path d="M{x} {y - 40 * k - 2 * 140 * k - 190 * k} l10 22 24 2 -18 15 6 24 -22 -13 -22 13 6 -24 -18 -15 24 -2Z" fill="#ffd23f" stroke="{INK}" stroke-width="3" opacity="{.3 + .7 * lit:.2f}"/>'
    return o


def window_view(x0, y0, w, h, mode, t, flash=0.0):
    """Окно: mode 'night' — салют, 'snow' — снегопад; flash 0…1 — пролетают сезоны полосами."""
    c = lib.clip_rect(x0, y0, w, h, 6)
    if mode == "night":
        inn = f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#1c2452"/>' + card_pic("fire", t).replace('<rect width="200" height="150" fill="#1f2a5a"/>', "")
        inn = f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#1c2452"/><g transform="translate({x0} {y0}) scale({w / 200:.3f} {h / 150:.3f})">{card_pic("fire", t)}</g>'
    else:
        rng = random.Random(9)
        inn = f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#b9cde0"/><rect x="{x0}" y="{y0 + h * .78}" width="{w}" height="{h * .22}" fill="#f4f8fb"/>'
        for i in range(40):
            sx = x0 + (rng.uniform(0, w) + 20 * math.sin(t * 2 + i)) % w
            sy = y0 + (rng.uniform(0, h) + 120 * t) % h
            inn += f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{rng.uniform(3, 7):.1f}" fill="#fff"/>'
    if flash > 0:
        seas = ("#7cc56a", "#f6c945", "#e5733a", "#e9eef2")
        i = min(3, int(flash * 4))
        inn += f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{seas[i]}" opacity=".9"/>'
        for j in range(6):
            yy = y0 + ((j * 97 + flash * 2000) % h)
            inn += f'<rect x="{x0}" y="{yy:.1f}" width="{w}" height="18" fill="#fff" opacity=".35"/>'
    o = f'<g clip-path="url(#{c})">{inn}</g>'
    o += shape(lib.rect_pts(x0 - 18, y0 - 18, x0 + w + 18, y0 + h + 18), "none", w=6, seed=730)
    o += shape(lib.rect_pts(x0 + w / 2 - 8, y0, x0 + w / 2 + 8, y0 + h), "#f2ece0", w=3.4, seed=731)
    o += shape(lib.rect_pts(x0 - 30, y0 + h + 4, x0 + w + 30, y0 + h + 34), "#f2ece0", w=4, seed=732)
    return o


def frame_s04(t):
    tb = W(9) + .08                       # «моргнул»: веки закрываются
    to = W(14)                             # «открыл»: глаза открыты — декабрь
    day = smooth(to - .05, to + .05, t)
    lib.DEFS.clear()
    wall = R.mix("#2a3266", "#e9e3d6", day) if hasattr(R, "mix") else lib.mix("#2a3266", "#e9e3d6", day)
    o = [f'<rect x="-300" y="-300" width="1680" height="2520" fill="{wall}"/>',
         f'<rect x="-300" y="1240" width="1680" height="600" fill="{lib.mix("#3a2f4a", "#c9b89a", day)}"/>']
    mode = "night" if t < to else "snow"
    flash = clamp((t - (tb + .45)) / (to - tb - .5)) if tb + .45 < t < to else 0.0
    o.append(window_view(560, 360, 400, 470, mode, t, flash))
    if t < to:
        o.append(tree(260, 1250, 1.05, t, lit=1.0 - smooth(to - .4, to, t)))
    else:
        # декабрь: ёлки нет, на подоконнике кот в снежинках
        o.append(cat(770, 852, .62, dict(look=(-.6, .2), perk=.9, tail=6 * math.sin(t * 3), smile=.4), t))
    closed = 0.0
    if tb < t < to:
        closed = min(1.0, (t - tb) / .07)
    if to <= t < to + .06:
        closed = 1 - (t - to) / .06
    e = ex("calm_smile") if t < tb else (dict(ex("wow82") if "wow82" in PE.EXPR["dima"] else ex("zeal")) if t >= to else ex("calm_smile"))
    e["closed"] = closed
    k = 1.25
    f_ = dfig(520, 1620, k, e, "d82_rest", t=t, head_add=-.1 * smooth(to, to + .2, t))
    o.append(f_["svg"])
    if t >= to:
        o.append(burst(f_["head"][0], f_["head"][1] - 40, 190, to, t, "#ffffff", 12, .35))
    dx, dy, r = drift(t)
    z = 1 + .05 * kick(t, to, .04, .25) + .02 * (t - T0("s04"))
    return view("".join(o), 540 + dx, 900 + dy, z, r, bg=wall)


# ═════════════════════════ s05: призыв «Телеграм» ═════════════════════════
def frame_s05(t):
    import story_cta_tg as tg
    press = W(20) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=COMMON)


# ═════════════════════════ s06: календарь листается сам и улетает ═════════════════════════
def frame_s06(t):
    lib.DEFS.clear()
    a = T0("s06")
    tf = W(30)                                    # «пролетел»: листки срываются очередью
    o = ['<rect x="-300" y="-300" width="1680" height="2520" fill="#ece3d2"/>', '<rect x="-300" y="1180" width="1680" height="700" fill="#cdb894"/>']
    o.append(window_view(-60, 300, 300, 420, "snow", t))
    # блок календаря: тоньше с каждым сорванным
    rate = lambda tt: 3.0 * max(0, tt - a) + 26 * max(0, tt - tf) ** 1.2       # noqa: E731
    n_off = rate(t)
    thick = max(6.0, 60 - 2.0 * n_off)
    bx, by = 600, 620
    o.append(shape(lib.rect_pts(bx - 160, by - 220, bx + 160, by - 180), "#7a5a40", w=4, seed=760))
    o.append(shape(lib.rect_pts(bx - 150, by - 180, bx + 150, by + 200 + thick), "#e9e4d8",
                   "".join(f'<rect x="{bx - 150}" y="{by + 200 + i * 5}" width="300" height="2" fill="#bdb6a6"/>' for i in range(int(thick / 5))), w=4, seed=761))
    cur = int(n_off)
    o.append(leaf(bx, by + 10, 3.0, 0, cur % 12, 1.0, cur))
    # сорванные листки: каждый — свой полёт влево к окну
    for j in range(max(0, cur - 14), cur):
        tj = a
        lo, hi = a - 2, t
        for _ in range(18):                        # момент срыва j-го листка
            m = (lo + hi) / 2
            if rate(m) < j + 1:
                lo = m
            else:
                hi = m
        tj = hi
        u = (t - tj) / .7
        if u > 1:
            continue
        px = bx - 900 * ease_in(u, 1.5) + 40 * math.sin(u * 9 + j)
        py = by + 10 - 500 * math.sin(math.pi * u * .6) + 200 * u
        o.append(leaf(px, py, 3.0 * (1 - .5 * u), -40 * u * (1 + j % 3), j % 12, math.cos(8 * u + j), j))
    # Дима тянется к блоку, кот на тумбе прижимает его лапой
    reach = smooth(tf - .2, tf + .3, t)
    f_ = dfig(250, 1500, 1.05, ex("panic82") if reach > .3 else ex("look82"), "d82_rest", t=t,
              arms={"n": ("ik", (250 + (300 + 60 * reach) * 1.05, 1500 - 380 - 200 * reach), -1)}, hands={"n": {"dir": (1, -.3), "spread": .4}})
    o.append(shape(lib.rect_pts(700, 1020, 1100, 1300), "#9a6f4a", w=5, seed=770))
    o.append(cat(880, 1022, .6, dict(look=(.2, -.6), paw=smooth(tf - .1, tf + .15, t), paw_dx=40, perk=1.0, flat_ears=0.0), t))
    o.append(f_["svg"])
    dx, dy, r = drift(t)
    z = 1.0 + .06 * kick(t, tf, .04, .3)
    return view("".join(o), 540 + dx, 960 + dy, z, r, bg="#ece3d2")


# ═════════════════════════ s07: кот зовёт «смотри» и поддевает тонкую карточку ═════════════════════════
def frame_s07(t):
    lib.DEFS.clear()
    td = W(36)                                     # «делся»
    o = [grad_bg("#f3e4c8", "#e8d2a8"), '<rect x="-300" y="1050" width="1680" height="900" fill="#b88a5c"/>',
         '<rect x="-300" y="1050" width="1680" height="22" fill="#9a6f44"/>']
    lift = smooth(td - .05, td + .25, t)
    # тонкая серая карточка на столе: край поднимается лапой
    cx_, cy_ = 300, 1090
    o.append(f'<ellipse cx="{cx_}" cy="{cy_ + 8}" rx="170" ry="14" fill="#000" opacity=".15"/>')
    o.append(f'<g transform="translate({cx_ - 160} {cy_}) rotate({-24 * lift:.2f}) translate({-cx_ + 160} {-cy_})">'
             + shape(lib.rect_pts(cx_ - 160, cy_ - 8, cx_ + 160, cy_ + 2), "#c9cbcf", w=3.2, seed=780) + "</g>")
    if lift > .3:
        o.append(f'<ellipse cx="{cx_}" cy="{cy_}" rx="150" ry="10" fill="#a87c50" opacity="{lift:.2f}"/>')
    look = (-.2, -.1) if t < td - .3 else (-.8, .5)
    o.append(cat(700, 1084, 1.55, dict(look=look, paw_l=lift, paw_l_dx=150, perk=1.0, tilt=-6 * smooth(T0("s07"), W(33) + .3, t),
                                      tail=8 * math.sin(t * 4), smile=.3), t))
    dx, dy, r = drift(t, 1.4)
    z = 1.0 + .07 * kick(t, W(33), .05, .25) + .06 * kick(t, td, .04, .25)
    return view("".join(o), 540 + dx, 860 + dy, z, r, bg="#f3e4c8")


# ═════════════════════════ s08: яркие разные дни встают отдельно ═════════════════════════
def frame_s08(t):
    lib.DEFS.clear()
    a = T0("s08")
    tn = W(40)                                     # «новое»: самая яркая
    o = [grad_bg("#fff7e6", "#ffe9c2")]
    slots = [("sea", 285, 560, -6), ("mount", 800, 520, 5), ("train", 280, 1090, 4), ("fire", 795, 1060, -4)]
    for i, (kind, x, y, rot) in enumerate(slots):
        ti = a - .25 + .3 * i if kind != "fire" else tn - .12
        u = (t - ti) / .32
        if u <= 0:
            continue
        sx = x + (1300 - x) * (1 - ease_out(u, 3)) * (1 if i % 2 else -1) * .8
        sy = y - 300 * (1 - ease_out(u, 3))
        k = 2.35 * (1 + .25 * math.exp(-max(0, u - 1) * 6) * (u > 1)) if kind == "fire" else 2.2
        o.append(card(sx, sy, k, kind, rot + 30 * (1 - ease_out(u)), t, seed=i))
    o.append(burst(795, 1060, 300, tn + .1, t, "#ffd23f", 14, .45))
    dx, dy, r = drift(t)
    return view("".join(o), 540 + dx, 820 + dy, 1.0 + .04 * kick(t, tn + .1, .04, .3), r, bg="#fff7e6")


# ═════════════════════════ s09: серые одинаковые дни сливаются в один ═════════════════════════
def frame_s09(t):
    lib.DEFS.clear()
    a = T0("s09")
    tm, t1 = W(44), W(46)                          # «сливаются», «один»
    o = [grad_bg("#e9eaec", "#d5d7da")]
    merge = smooth(tm - .1, t1, t)
    squash = smooth(t1 - .05, t1 + .12, t)
    n = 9
    for i in range(n):
        ti = a - .25 + .06 * i
        u = clamp((t - ti) / .3)
        if u <= 0:
            continue
        gx, gy = 225 + 315 * (i % 3), 470 + 250 * (i // 3)
        x = gx + (540 - gx) * merge + 900 * (1 - ease_out(u))
        y = gy + (860 - gy) * merge + i * 4 * merge
        k = 1.35 + .6 * merge
        o.append(card(x, y, k * (1 - .0 * squash), "gray", (i % 3 - 1) * 4 * (1 - merge), t, seed=40 + i))
    if squash > 0:
        # всё сплющилось в одну тонкую серую карточку
        o = [grad_bg("#e9eaec", "#d5d7da")]
        h = 170 * (1 - .9 * squash)
        o.append(f'<g transform="translate(540 {880:.1f}) scale(2.2 {2.2 * h / 170:.3f})">{card(0, 0, 1, "gray", 0, t, 49)}</g>')
        o.append(burst(540, 880, 300, t1, t, "#9fa3a9", 12, .4))
    o.append(cat(540, 1250, .8, dict(look=(0, -.9), perk=1.0, tilt=10 * squash, flat_ears=.0), t))
    dx, dy, r = drift(t)
    return view("".join(o), 540 + dx, 860 + dy, 1.0 + .05 * kick(t, t1, .04, .25), r, bg="#e9eaec")


# ═════════════════════════ s10: храповик «работа, дом, лента» ═════════════════════════
def gray_scene(kind, t, k=1.0):
    """Один и тот же серый день: Дима по пояс, усталый, у монитора / на диване / с телефоном."""
    o = ['<rect x="-400" y="-400" width="1880" height="2720" fill="#c8cbd0"/>']
    if kind == "work":
        o.append(shape(lib.rect_pts(560, 520, 1000, 820, 10), "#4b525c", '<rect x="590" y="550" width="380" height="240" fill="#9fb2c4"/>'
                       + "".join(f'<rect x="620" y="{580 + 40 * i}" width="{300 - 50 * (i % 2)}" height="14" fill="#7f93a6"/>' for i in range(5)), w=5, seed=800))
        o.append(shape(lib.rect_pts(740, 820, 820, 900), "#4b525c", w=4, seed=801))
        o.append('<rect x="-400" y="1100" width="1880" height="40" fill="#8d9197"/>')
    elif kind == "home":
        o.append(shape(lib.rrect(40, 900, 1040, 1400, 60), "#7f8794", blob(lib.rrect(40, 900, 1040, 1000, 40), "#6d7480", .8), w=5, seed=810))
        o.append(shape(lib.rect_pts(820, 380, 900, 900), "#9a9fa6", w=4, seed=811))
        o.append(shape([(760, 380), (960, 380), (920, 250), (800, 250)], "#e0d9b8", w=4, seed=812))
    f_ = dfig(420, 1580, 1.5, ex("gloom"), "d82_hold" if kind == "feed" else "d82_rest", t=t)
    o.append(f_["svg"])
    if kind == "feed":
        px, py = f_["hold"][0] + 40, f_["hold"][1] - 120
        o.append(shape(lib.rrect(px - 90, py - 160, px + 90, py + 160, 22), "#2a2d33",
                       f'<rect x="{px - 76}" y="{py - 140}" width="152" height="280" fill="#aeb6c0"/>'
                       + "".join(f'<rect x="{px - 64}" y="{py - 130 + ((70 * i - 400 * t) % 280):.1f}" width="128" height="52" rx="6" fill="#8b95a2"/>'
                                 for i in range(4)), w=4, seed=820))
    return "".join(o)


def frame_s10(t):
    lib.DEFS.clear()
    beats = [W(47), W(48), W(49)]
    i = max([j for j, b in enumerate(beats) if t >= b - .02] or [0])
    kind = ("work", "home", "feed")[i]
    z = 1.0 + .14 * kick(t, beats[i], .03, .18) + .03 * (t - beats[i])
    dx, dy, r = drift(t, .6)
    return view(gray_scene(kind, t), 540 + dx, 900 + dy, z, r, bg="#c8cbd0")


# ═════════════════════════ s11: триста раз подряд → в памяти неделя ═════════════════════════
def frame_s11(t):
    lib.DEFS.clear()
    a, tm, tw = T0("s11"), W(55), W(57)            # «памяти», «неделя»
    o = ['<rect x="-400" y="-400" width="1880" height="2720" fill="#b9bdc3"/>']
    grow = clamp((t - a) / (tm - a))
    n = int(2 + 22 * grow ** 1.3)                  # плитка мельчает и множится
    col = smooth(tm, tm + .45, t)
    cell = 1080 / n
    rng = random.Random(5)
    if col < 1:
        for r_ in range(int(1920 / cell) + 1):
            for c_ in range(n):
                j = (r_ * n + c_) % 3
                x, y = c_ * cell, r_ * cell
                tx, ty = 230 + ((r_ * n + c_) % 7) * 92, 820
                x = x + (tx - x) * ease_io(col)
                y = y + (ty - y) * ease_io(col)
                sz = cell * (1 - .15) * (1 - col) + 56 * col
                o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{sz:.1f}" height="{sz * .8:.1f}" rx="{sz * .1:.1f}" '
                         f'fill="{("#8d9197", "#7f8794", "#9aa1aa")[j]}" stroke="#5e636b" stroke-width="{max(1, sz * .04):.1f}" opacity="{1 - .6 * col:.2f}"/>')
                o.append(f'<rect x="{x + sz * .2:.1f}" y="{y + sz * .2:.1f}" width="{sz * .6:.1f}" height="{sz * .2:.1f}" fill="#c9ccd1" opacity="{1 - col:.2f}"/>')
    if col > 0:
        f_ = dfig(470, 1560, 1.35, ex("puzzled82"), "d82_hold", t=t)
        o.append(f_["svg"])
        hx, hy = f_["hold"]
        sh = smooth(tw - .1, tw + .2, t)
        for q in range(7):
            x = hx - 420 + q * 92
            o.append(f'<rect x="{x:.1f}" y="{hy - 110 - 30 * (1 - col) - 12 * sh * math.sin(q + t * 8):.1f}" width="80" height="64" rx="8" fill="#9aa1aa" stroke="{INK}" stroke-width="4" opacity="{col:.2f}"/>')
    dx, dy, r = drift(t)
    return view("".join(o), 540 + dx, 900 + dy, 1 + .05 * kick(t, tm, .04, .3), r, bg="#b9bdc3")


# ═════════════════════════ s12: Израиль, учёные с двумя лентами ═════════════════════════
def palm(x, y, k, t, seed=0):
    o = line([(x, y), (x + 20 * k, y - 250 * k), (x + 10 * k, y - 480 * k)], 26 * k, "#8a6a48", seed=900 + seed, taper=.3, wmin=.5)
    tx, ty = x + 10 * k, y - 480 * k
    for i in range(7):
        a = -math.pi * (.05 + .9 * i / 6) + .06 * math.sin(t * 2 + i + seed)
        ex_, ey = tx + 210 * k * math.cos(a), ty + 210 * k * math.sin(a) + 90 * k
        mx, my = tx + 120 * k * math.cos(a), ty + 120 * k * math.sin(a) - 30 * k
        o += shape([(tx, ty), (mx, my - 18 * k), (ex_, ey), (mx, my + 18 * k)], "#4f9a48", w=3.2, seed=910 + i + seed)
    return o


def ribbon(x0, y, x1, kind, t, h=56, seed=0):
    """Лента времени: пёстрая (bright) — разные квадраты; серая (gray) — одинаковые."""
    if x1 <= x0 + 4:
        return ""
    o = shape(lib.rect_pts(x0, y - h / 2, x1, y + h / 2), "#f7f4ee" if kind == "bright" else "#c9ccd1", w=3.6, seed=950 + seed)
    step = 46
    i = 0
    x = x0 + 8
    while x + 34 < x1:
        c = MONTHS[(i * 5 + seed) % 12] if kind == "bright" else "#a3a8af"
        o += f'<rect x="{x:.1f}" y="{y - h / 2 + 10:.1f}" width="34" height="{h - 20}" rx="5" fill="{c}"/>'
        x += step
        i += 1
    return o


def frame_s12(t):
    lib.DEFS.clear()
    a, tp = T0("s12"), W(61)                       # «проверили»: ленты разворачиваются
    o = [grad_bg("#7fc3ef", "#d9eef8"), '<circle cx="860" cy="260" r="80" fill="#fff6c8"/><circle cx="860" cy="260" r="140" fill="#fff6c8" opacity=".3"/>']
    # белый камень: стена из блоков с аркой
    o.append(shape(lib.rect_pts(-300, 560, 1380, 1300), "#efe4cc",
                   "".join(f'<rect x="{-300 + (c * 150 + (75 if r % 2 else 0))}" y="{560 + r * 70}" width="146" height="66" fill="{("#f3ead6", "#e8dcc0", "#efe2c8")[(r + c) % 3]}"/>'
                           for r in range(11) for c in range(13)), w=5, seed=960))
    o.append(shape([(360, 1300), (360, 820), (380, 760), (440, 720), (500, 760), (520, 820), (520, 1300)], "#c9a878", w=5, seed=961))
    o.append(palm(120, 1250, 1.0, t, 0) + palm(960, 1250, 1.1, t, 3))
    o.append('<rect x="-300" y="1240" width="1680" height="700" fill="#e2cf9e"/>')
    u = smooth(tp - .15, tp + .5, t)
    fa = PE.scientist82("a", 250, 1000, .62, "rest", t=t, expr="focus")
    fb = PE.scientist82("b", 830, 990, .62, "rest", t=t, expr="focus", flip=True)
    o.append(fa["svg"] + fb["svg"])
    hy = fa["hold"][1]
    o.append(ribbon(fa["hold"][0], hy + 20, fa["hold"][0] + 60 + 640 * u, "bright", t, h=80, seed=1))
    o.append(ribbon(fb["hold"][0] - 60 - 300 * u, hy + 150, fb["hold"][0], "gray", t, h=80, seed=2))
    pan = ease_io(clamp((t - a) / 1.6))
    return view("".join(o), 540, 780 + 160 * pan, 1.12 - .1 * pan, 0, bg="#bfe3f5")


# ═════════════════════════ s13: две ленты — однообразная съёживается ═════════════════════════
def frame_s13(t):
    lib.DEFS.clear()
    tk = W(66)                                     # «короче»
    o = [grad_bg("#fbf3e2", "#f1e2c4")]
    sh = smooth(tk - .05, tk + .35, t)
    o.append(ribbon(40, 600, 1040, "bright", t, h=170, seed=1))
    w = 960 - 600 * ease_out(sh, 3) + 30 * damp(t, tk + .35, 1, 4, 7)
    o.append(ribbon(40, 900, 40 + w, "gray", t, h=170, seed=2))
    o.append(f'<g transform="translate(860 1250)">{cat(0, 0, .8, dict(look=(.8, -.6), perk=1.0, tilt=8 * sh), t)}</g>')
    dx, dy, r = drift(t)
    return view("".join(o), 540 + dx, 860 + dy, 1.0 + .05 * kick(t, tk, .04, .25), r, bg="#fbf3e2")


# ═════════════════════════ s14–s15: впервые — новая улица ═════════════════════════
FAC_GRAY = ("#b9bcc2", "#aeb2b8", "#c4c7cc")
FAC_NEW = ("#46c2b8", "#f08bb0", "#ffd04a", "#7aa8f0", "#ff8f5a")


def facades(x0, x1, cols, ground, seed=0, lamps=0.0, t=0.0):
    o = []
    x = x0 - (x0 % 220)
    i = int(x // 220)
    while x < x1:
        c = cols[(i + seed) % len(cols)]
        hgt = 760 + 120 * ((i * 7 + seed) % 3)
        o.append(shape(lib.rect_pts(x, ground - hgt, x + 220, ground), c,
                       "".join(f'<rect x="{x + 34 + 90 * cc}" y="{ground - hgt + 70 + 170 * rr}" width="62" height="96" rx="6" fill="#e9f3f8" opacity=".85"/>'
                               for rr in range(int(hgt / 170) - 1) for cc in range(2)), w=4, seed=1000 + i))
        if lamps > 0:
            for q in range(4):
                lx, ly = x + 25 + q * 55, ground - hgt + 40 + 14 * math.sin(q * 1.4)
                on = lamps * (.6 + .4 * math.sin(t * 6 + q + i))
                o.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="13" fill="{("#ffd23f", "#ff6a8a", "#6ae0ff")[q % 3]}" opacity="{on:.2f}"/>')
            o.append(line([(x, ground - hgt + 30), (x + 110, ground - hgt + 56), (x + 220, ground - hgt + 30)], 3, INK, seed=1100 + i, taper=.1))
        x += 220
        i += 1
    return "".join(o)


def walk_scene(t, cols, mood_new, lamps=0.0, expr="calm82", reveal=None):
    G = 1300.0
    v = 170.0
    xc = v * t
    o = [grad_bg("#a8d4f2" if mood_new else "#c7ccd4", "#f6ead2" if mood_new else "#e1e3e6")]
    o.append(f'<g transform="translate({-xc * .9:.1f} 0)">{facades(xc * .9 - 700, xc * .9 + 1800, cols, G, 2, lamps, t)}</g>')
    if reveal is not None:
        # яркий переулок открывается справа (cтена раздвигается)
        cl = lib.clip_rect(1080 - 1100 * reveal, -200, 1500, 1600)
        o.append(f'<g clip-path="url(#{cl})"><g transform="translate({-xc * .9:.1f} 0)">{facades(xc * .9 - 700, xc * .9 + 1800, FAC_NEW, G, 5, 1.0, t)}</g></g>')
    o.append(f'<rect x="-400" y="{G}" width="1880" height="700" fill="{"#e6d6b8" if mood_new else "#a9adb3"}"/>')
    ph = (t * 1.0) % 1.0
    f_ = PE.dima82_walk(430, 1300 - 598 * .95, .95, ph, t=t, expr=expr, mug=False)
    o.append(f_["svg"])
    o.append(cat(800, G + 6, .68, dict(walk=(t * 2.2) % 1.0, look=(.3, -.3), rot=2 * math.sin(t * 9), tail=8 * math.sin(t * 4)), t, right=True))
    return "".join(o)


def frame_s14(t):
    lib.DEFS.clear()
    tf = W(74)                                     # «впервые»
    rev = smooth(W(71), tf, t)
    dx, dy, r = drift(t, .5)
    return view(walk_scene(t, FAC_GRAY, False, 0.0, "calm82" if rev < .5 else "wow82", reveal=rev), 540 + dx, 900 + dy, 1.0 + .03 * rev, r)


def frame_s15(t):
    lib.DEFS.clear()
    tu = W(76)                                     # «улица»
    lamps = smooth(tu - .1, tu + .15, t)
    dx, dy, r = drift(t, .8)
    return view(walk_scene(t, FAC_NEW, True, lamps, "wow82"), 540 + dx, 880 + dy, 1.04 + .05 * kick(t, tu, .04, .25), r)


# ═════════════════════════ s16: новое блюдо ═════════════════════════
def frame_s16(t):
    lib.DEFS.clear()
    tb = W(78)                                     # «блюдо»: пробует
    o = [grad_bg("#ffe2b8", "#f7c98a")]
    taste = smooth(tb - .1, tb + .1, t)
    f_ = dfig(500, 1640, 1.45, ex("laugh82") if taste > .5 else ex("wow82", look=(.3, .8)), "d82_rest", t=t, head_add=.12 * taste)
    o.append(f_["svg"])
    o.append('<rect x="-300" y="1230" width="1680" height="900" fill="#c0563a"/><rect x="-300" y="1230" width="1680" height="20" fill="#9a3f28"/>')
    bx, by = 600, 1260
    o.append(shape([(bx - 260, by - 30), (bx + 260, by - 30), (bx + 200, by + 140), (bx - 200, by + 140)], "#2f86c4",
                   blob([(bx - 260, by + 40), (bx + 260, by + 40), (bx + 200, by + 140), (bx - 200, by + 140)], "#236fa8", .8), w=5, seed=1200))
    food = [("#ffd04a", -150, -40, 70), ("#7cc56a", -40, -60, 55), ("#ff8f5a", 80, -50, 65), ("#e2463c", 170, -30, 40), ("#f7f4ee", 10, -20, 60)]
    for i, (c, fx, fy, r_) in enumerate(food):
        o.append(blob(ellipse_pts(bx + fx, by + fy, r_, r_ * .55, 12, seed=i), c))
    for i in range(3):
        u = ((t * .8 + i / 3) % 1.0)
        sx = bx - 100 + 100 * i + 30 * math.sin(u * 6 + i)
        o.append(line([(sx, by - 80 - 300 * u), (sx + 20, by - 140 - 300 * u), (sx - 10, by - 200 - 300 * u)], 10, "#ffffff", seed=1210 + i, op=.7 * (1 - u)))
    o.append(burst(bx, by - 120, 260, tb, t, "#ffd23f", 12, .4))
    o.append(cat(940, 1250, .8, dict(look=(-.9, .4), perk=1.0, tilt=-10, smile=.3 + .5 * taste), t))
    dx, dy, r = drift(t)
    return view("".join(o), 540 + dx, 960 + dy, 1.0 + .06 * kick(t, tb, .04, .25), r, bg="#ffe2b8")


# ═════════════════════════ s17: длинная лента года, кот спит, лапки на пятницах ═════════════════════════
RIB_Y = lambda x: 900 + 60 * math.sin(x / 260)      # noqa: E731


def frame_s17(t):
    lib.DEFS.clear()
    a, b = T0("s17"), T1("s17")
    tc = W(84)                                     # «кот»
    L = 4200.0
    o = ['<rect x="-1500" y="-1500" width="8000" height="5000" fill="#fbefd2"/>']
    # лента — сегментами по волне
    for i in range(int(L / 46)):
        x = i * 46
        y = RIB_Y(x)
        o.append(f'<rect x="{x:.1f}" y="{y - 50:.1f}" width="48" height="100" fill="#f7f4ee"/>')
        c = MONTHS[(i // 8) % 12] if i % 7 == 4 else "#e6e0d2"
        o.append(f'<rect x="{x + 7:.1f}" y="{y - 38:.1f}" width="34" height="76" rx="6" fill="{c}"/>')
    o.append(line([(x, RIB_Y(x) - 50) for x in range(0, int(L), 60)], 4, INK, seed=1300, taper=.05))
    o.append(line([(x, RIB_Y(x) + 50) for x in range(0, int(L), 60)], 4, INK, seed=1301, taper=.05))
    pan = ease_io(clamp((t - a) / (tc - a + .1)))
    camx = 400 + (L - 900 - 400) * pan
    # лапки на каждой яркой отметке, ставятся, когда камера проходит
    for i in range(int(L / 46)):
        if i % 7 != 4:
            continue
        x = i * 46 + 24
        if x < camx + 250:
            pu = clamp((camx + 250 - x) / 150)
            y = RIB_Y(x)
            o.append(f'<g transform="translate({x:.1f} {y:.1f}) scale({.6 + .4 * pu:.2f})" opacity="{pu:.2f}">'
                     '<ellipse cx="0" cy="8" rx="12" ry="10" fill="#2a2d30"/><circle cx="-12" cy="-8" r="5" fill="#2a2d30"/>'
                     '<circle cx="-4" cy="-14" r="5" fill="#2a2d30"/><circle cx="5" cy="-14" r="5" fill="#2a2d30"/><circle cx="13" cy="-8" r="5" fill="#2a2d30"/></g>')
    xc = L - 900
    o.append(PE.cat_curl(xc, RIB_Y(xc) + 30, .62, dict(squint=1.0, breath=1.2, flame_e=1.3), t))
    for q in range(3):                              # «з-з» сна без букв: пузырьки дыхания
        u = ((t * .7 + q / 3) % 1)
        o.append(f'<circle cx="{xc - 120 + 40 * u:.1f}" cy="{RIB_Y(xc) - 140 - 160 * u:.1f}" r="{8 + 14 * u:.1f}" fill="none" stroke="{INK}" stroke-width="3" opacity="{1 - u:.2f}"/>')
    z = 1.9 + .3 * smooth(tc - .3, b, t)
    return view("".join(o), camx, RIB_Y(camx) - 20, z, -1.5 * math.sin(t), bg="#fdf3dc")


# ═════════════════════════ s18: петля — та же улица, листки медленно падают, Дима ловит один ═════════════════════════
def frame_s18(t):
    ensure("walk")
    s = 1.55
    cam = run_cam(t, s, 380.0, 1300.0, shake=0.0, drift=.4)
    lib.DEFS.clear()
    tc = W(87)                                     # «пятницу»: ловит
    p = run_pose(t)
    p["expr"].update(brows="calm", mouth="smile", lid=.8, look=(.6, -.6))
    face = face_world(p)
    catch = face + np.array([170.0, -60.0])
    reach = smooth(tc - .45, tc, t)
    if reach > 0:
        p["arms"]["n"] = ("ik", tuple(np.array(p["hip"]) + (catch - np.array(p["hip"])) * reach + (np.array(p["hip"]) + np.array([60, -150])) * 0 * (1 - reach)), -1)
        p["hands"] = {"n": ("open", .3), "f": "fist"}
    dg, wr = dima.draw(p)
    hx = hip_at(t, bob=False)[0]
    cg = cat(hx + 300, 0, .5, dict(walk=(t * 2.0) % 1.0, look=(.2, -.8), tail=8 * math.sin(t * 3), smile=.5), t, right=True)
    st = R.street82(t, cam, "calm")
    world = f'<g opacity=".2" transform="matrix(1 0 -0.9 -0.22 0 0)">{dg}</g>' + dg + cg
    # пойманный листок: падает к руке к tc и остаётся в ней
    hand = to_screen(wr["n"], cam)
    if t < tc:
        u = clamp((t - (tc - 1.2)) / 1.2)
        lp = hand + np.array([60 * (1 - u), -700 * (1 - u)])
        lf = leaf(lp[0], lp[1] - 30, 1.0, 20 * math.sin(t * 3), 6, math.cos(t * 2.5), 77)
    else:
        lf = leaf(hand[0] + 10, hand[1] - 40, 1.0, -8, 6, 1.0, 77)
    body = (st["back"] + storm(t, (0, 1), speed=.08, fall=1.0) + f'<g transform="{lib.cam(*cam)}">{st["ground"]}{world}</g>' + st["front"] + lf
            + burst(hand[0], hand[1] - 40, 120, tc, t, "#ffd23f", 10, .4))
    return lib.svg(body)


def frame(sid, t):
    lib.INK_K[0] = 1.0
    return globals()["frame_" + sid](t)
