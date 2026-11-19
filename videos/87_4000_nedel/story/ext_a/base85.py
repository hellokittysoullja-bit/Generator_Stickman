"""Рилс 85 «Найди 3 кота» — все клипы (один каталог кода). frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Время — только из shots.json (t0/t1, окна котов "cats") и voice/words.json (слово по индексу W(i)); числа в коде — длительности движений.
Бег хука — движок рилсов 82/84 (план шагов, rdima.py); заголовок — common/big_title.py. Кот в ролике — ТОЛЬКО три спрятанных
появления из shots.json "cats" (cat_on); вне этих окон кот не рисуется нигде.
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




MASK_F = '<filter id="mk85"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 9 0"/></filter>'




PIV = 700.0     # центр влёта — у головы Димы
CATS = {c["id"]: c for c in SH.get("cats", [])}


def cat_u(cid, t):
    """Окно кота cid из shots.json: 0 — нет кота; выезд/уход по 0.1 с. Вне [t, t+dur] кот не рисуется (None)."""
    c = CATS[cid]
    a, b = c["t"], c["t"] + c["dur"]
    if not a <= t <= b:
        return None
    return ease_out(clamp((t - a) / .1)) * ease_out(clamp((b - t) / .1))


def title(t):
    if NOCAM or MASK:
        return ""
    tt = SH["title"]
    return big_title.layer(t, text=tt["text"], t_in=tt["t_in"], t_out=WE(tt["t_out_word_end"]) + tt["t_out_add"],
                           hits=[W(i) for i in tt["hits"]])


def mix(a, b, u):
    return lib.mix(a, b, clamp(u))


def kick2(t, t0, rise=.04, tau=.16):
    return kick(t, t0, rise, tau)


# ═════════════════════════ ключи (жёлтый и серый ключ на кольце, красная бирка) ═════════════════════════
def keys(x, y, k=1.0, rot=0.0, glow=0.0, seed=0):
    o = []
    if glow > 0:
        g = lib.rad_grad([(0, "#fff3a8", .85 * glow), (1, "#fff3a8", 0)], .5, .5, .5)
        o.append(f'<ellipse cx="0" cy="0" rx="120" ry="90" fill="url(#{g})"/>')
    # ключ 1 (латунь) — вправо-вниз
    k1 = [(10, 8), (40, 18), (44, 10), (100, 30), (98, 40), (92, 42), (90, 50), (84, 48), (80, 56), (72, 52), (40, 30), (6, 22)]
    o.append(shape(k1, "#f2c230", line([(48, 22), (92, 37)], 2.5, "#c8961c"), w=3.2, seed=seed + 1))
    o.append(shape(ellipse_pts(16, 14, 22, 18, 16), "#f2c230", f'<circle cx="10" cy="10" r="7" fill="#fff6c8" opacity=".8"/>', w=3.2, seed=seed + 2))
    # ключ 2 (сталь) — вниз
    k2 = [(-8, 16), (0, 46), (-6, 50), (-2, 100), (8, 98), (10, 90), (16, 88), (14, 80), (20, 76), (14, 70), (12, 48), (6, 14)]
    o.append(shape(k2, "#c9d1da", line([(3, 54), (5, 92)], 2.2, "#8a96a3"), w=3.2, seed=seed + 3))
    o.append(shape(ellipse_pts(0, 8, 18, 15, 16), "#c9d1da", "", w=3.2, seed=seed + 4))
    # бирка
    o.append(shape(lib.T(lib.rrect(-70, -26, -26, 2, 8), 0, 0), "#e2493b", '<circle cx="-34" cy="-12" r="4" fill="#fff"/>', w=3.0, seed=seed + 5))
    o.append(f'<circle cx="0" cy="0" r="20" fill="none" stroke="#b78a1c" stroke-width="6"/><circle cx="0" cy="0" r="20" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    o.append(line([(-26, -10), (-14, -6)], 3, INK, seed=seed + 6))
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.4f})">{"".join(o)}</g>'


def sparkle(x, y, r, t0, t, n=4, col="#fff7c0", life=.5):
    u = (t - t0) / life
    if not 0 <= u < 1:
        return ""
    o = []
    for i in range(n):
        a = 2 * math.pi * i / n + .4
        rr = r * (.4 + .9 * ease_out(u))
        sc = (1 - u) * (1.2 if i % 2 else .8)
        cx, cy = x + rr * math.cos(a), y + rr * math.sin(a)
        o.append(f'<path d="M{cx:.1f} {cy - 22 * sc:.1f} Q{cx:.1f} {cy:.1f} {cx + 22 * sc:.1f} {cy:.1f} Q{cx:.1f} {cy:.1f} {cx:.1f} {cy + 22 * sc:.1f} '
                 f'Q{cx:.1f} {cy:.1f} {cx - 22 * sc:.1f} {cy:.1f} Q{cx:.1f} {cy:.1f} {cx:.1f} {cy - 22 * sc:.1f}Z" fill="{col}" stroke="{INK}" stroke-width="2"/>')
    return "".join(o)


def burst(x, y, r, t0, t, col="#ffd23f", n=10, life=.4):
    u = (t - t0) / life
    if not 0 <= u < 1:
        return ""
    o = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r0, r1 = r * (.3 + .7 * ease_out(u)), r * (.55 + .8 * ease_out(u))
        o.append(line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))], 9 * (1 - u) + 2, col, seed=i))
    return "".join(o)


# ═════════════════════════ вещи, которые Дима швыряет ═════════════════════════
def item(kind, x, y, k, rot, seed=0):
    if kind == "cushion":
        b = shape(lib.rrect(-48, -40, 48, 40, 22), "#e8834a", line([(-30, -8), (30, 6)], 2.4, "#b85f2e", seed=seed) + '<circle cx="0" cy="0" r="6" fill="#b85f2e"/>', w=3.4, seed=seed)
    elif kind == "sock":
        pts = [(-14, -50), (14, -50), (16, 10), (44, 22), (46, 44), (-4, 44), (-16, 20)]
        b = shape(pts, "#f4f1ea", "".join(f'<rect x="-30" y="{-44 + 14 * i}" width="90" height="6" fill="#4a8fd8"/>' for i in range(3)), w=3.2, seed=seed)
    elif kind == "shirt":
        pts = [(-60, -40), (-24, -50), (0, -38), (24, -50), (60, -40), (72, -10), (46, -2), (44, 50), (-44, 50), (-46, -2), (-72, -10)]
        b = shape(pts, "#5aa6d6", line([(-14, -40), (0, -26), (14, -40)], 2.4, "#2f7fb0", seed=seed), w=3.4, seed=seed)
    elif kind == "paper":
        b = shape(lib.rrect(-34, -44, 34, 44, 3), "#ffffff", "".join(line([(-22, -26 + 14 * i), (18, -26 + 14 * i)], 2, "#c8cfd8", seed=seed + i) for i in range(5)), w=2.8, seed=seed)
    else:   # book
        b = shape(lib.rrect(-40, -30, 40, 30, 4), "#c94a5a", '<rect x="-40" y="-30" width="12" height="60" fill="#9c3442"/>', w=3.4, seed=seed)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f})">{b}</g>'


KINDS = ("cushion", "sock", "shirt", "paper", "book")


def throws(t, t_first, t_last, every, origin, vx, rng_seed, floor=0.0, k=1.0, g=2600.0, vy=-1050.0):
    """Вещи летят из origin(t_launch) по баллистике, падают на пол floor и лежат. -> SVG (в тех же координатах, что origin)."""
    rnd = random.Random(rng_seed)
    o = []
    tl = t_first
    i = 0
    while tl <= min(t, t_last):
        p0 = np.array(origin(tl), float)
        v = np.array([vx * rnd.uniform(.7, 1.3), vy * rnd.uniform(.8, 1.15)])
        kind = KINDS[(i + rng_seed) % len(KINDS)]
        spin = rnd.uniform(-900, 900)
        u = t - tl
        y = p0[1] + v[1] * u + .5 * g * u * u
        # время касания пола
        fl = floor + rnd.uniform(0, 260) if floor is not None else 0.0
        a_, b_, c_ = .5 * g, v[1], p0[1] - fl
        disc = b_ * b_ - 4 * a_ * c_
        tland = (-b_ + math.sqrt(max(disc, 0))) / (2 * a_)
        if u >= tland:
            u = tland
            y = fl
            rot = spin * tland
            rot = round(rot / 180) * 180 + 8 * (1 if i % 2 else -1)
        else:
            rot = spin * u
        x = p0[0] + v[0] * u
        o.append(item(kind, x, y - 30 * k, k * rnd.uniform(.85, 1.15), rot, seed=50 + i))
        tl += every
        i += 1
    return "".join(o)


# ═════════════════════════ комната (мир: пол y = 0, стена вверх) ═════════════════════════
WALL, WALL_SH, FLOOR, FLOOR_SH = "#f1e2c4", "#e2cfa8", "#c99d6e", "#b3875a"


def wardrobe(x0, x1, top, seed=0):
    w = x1 - x0
    o = [shape(lib.rect_pts(x0, top, x1, 0), "#9a6a45", f'<rect x="{x0}" y="{top}" width="{w}" height="40" fill="#b07c52"/>'
               f'<rect x="{x0 + w * .5 - 3}" y="{top + 50}" width="6" height="{-top - 90}" fill="#7a5034"/>', w=4.0, seed=seed)]
    for xx in (x0 + w * .5 - 22, x0 + w * .5 + 14):
        o.append(f'<rect x="{xx:.1f}" y="{top * .5 - 30:.1f}" width="8" height="60" rx="4" fill="#e8c27a" stroke="{INK}" stroke-width="2"/>')
    o.append(line([(x0 + 20, top * .25), (x0 + 20, top * .75)], 3, "#7a5034", seed=seed + 1))
    return "".join(o)


def win(x0, y0, x1, y1, seed=0, sky=("#9fd0f0", "#d8eefb")):
    g = lib.lin_grad([(0, sky[0], 1), (1, sky[1], 1)])
    o = [shape(lib.rect_pts(x0 - 18, y0 - 18, x1 + 18, y1 + 18), "#fbf6ea", "", w=4.0, seed=seed),
         f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>',
         f'<ellipse cx="{x0 + (x1 - x0) * .3:.0f}" cy="{y0 + (y1 - y0) * .35:.0f}" rx="{(x1 - x0) * .18:.0f}" ry="{(y1 - y0) * .07:.0f}" fill="#fff" opacity=".85"/>',
         f'<rect x="{(x0 + x1) / 2 - 7:.1f}" y="{y0}" width="14" height="{y1 - y0}" fill="#fbf6ea" stroke="{INK}" stroke-width="2.5"/>',
         f'<rect x="{x0}" y="{(y0 + y1) / 2 - 7:.1f}" width="{x1 - x0}" height="14" fill="#fbf6ea" stroke="{INK}" stroke-width="2.5"/>',
         shape(lib.rect_pts(x0 - 34, y1 + 14, x1 + 34, y1 + 34), "#fbf6ea", "", w=3.4, seed=seed + 1)]
    return "".join(o)


def win_glass(x0, y0, x1, y1, seed=0):
    """Только стекло и небо (для слоя «за окном»)."""
    g = lib.lin_grad([(0, "#9fd0f0", 1), (1, "#d8eefb", 1)])
    return (f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>'
            f'<ellipse cx="{x0 + (x1 - x0) * .3:.0f}" cy="{y0 + (y1 - y0) * .35:.0f}" rx="{(x1 - x0) * .18:.0f}" ry="{(y1 - y0) * .07:.0f}" fill="#fff" opacity=".85"/>')


def win_frame(x0, y0, x1, y1, seed=0):
    th = 20
    o = [shape(lib.rect_pts(x0 - th, y0 - th, x1 + th, y0), "#fbf6ea", "", w=3.4, seed=seed),
         shape(lib.rect_pts(x0 - th, y1, x1 + th, y1 + th), "#fbf6ea", "", w=3.4, seed=seed + 2),
         shape(lib.rect_pts(x0 - th, y0, x0, y1), "#fbf6ea", "", w=3.4, seed=seed + 3),
         shape(lib.rect_pts(x1, y0, x1 + th, y1), "#fbf6ea", "", w=3.4, seed=seed + 4),
         f'<rect x="{(x0 + x1) / 2 - 7:.1f}" y="{y0}" width="14" height="{y1 - y0}" fill="#fbf6ea" stroke="{INK}" stroke-width="2.5"/>',
         f'<rect x="{x0}" y="{(y0 + y1) / 2 - 7:.1f}" width="{x1 - x0}" height="14" fill="#fbf6ea" stroke="{INK}" stroke-width="2.5"/>',
         shape(lib.rect_pts(x0 - 34, y1 + 14, x1 + 34, y1 + 34), "#fbf6ea", "", w=3.4, seed=seed + 1)]
    return "".join(o)


def bookshelf(x0, x1, top, seed=0):
    o = [shape(lib.rect_pts(x0, top, x1, 0), "#a8784f", "", w=4.0, seed=seed)]
    rnd = random.Random(seed)
    cols = ("#c94a5a", "#4a8fd8", "#e8b84a", "#5fb07a", "#8a6fc4", "#e8834a")
    n = 3
    for r in range(n):
        y1 = top + (r + 1) * (-top) / n - 14
        y0 = y1 - (-top) / n + 40
        o.append(f'<rect x="{x0 + 14}" y="{y1:.0f}" width="{x1 - x0 - 28}" height="14" fill="#8a5c38"/>')
        x = x0 + 22
        while x < x1 - 50:
            bw = rnd.uniform(18, 34)
            bh = rnd.uniform(.6, .95) * (y1 - y0)
            o.append(f'<rect x="{x:.0f}" y="{y1 - bh:.0f}" width="{bw:.0f}" height="{bh:.0f}" fill="{rnd.choice(cols)}" stroke="{INK}" stroke-width="2.4"/>')
            x += bw + 3
    return "".join(o)


def sofa(x0, x1, seed=0, col="#5a7fb8", cushion=True):
    sh = lib.mul(col, (.8, .8, .85))
    o = [shape(lib.rrect(x0, -330, x1, -120, 30), sh, "", w=4.0, seed=seed),
         shape(lib.rrect(x0 + 10, -150, x1 - 10, -40, 18), col, "", w=4.0, seed=seed + 1)]
    if cushion:
        m = (x0 + x1) / 2
        o += [shape(lib.rrect(x0 + 70, -250, m - 6, -145, 22), col, "", w=3.6, seed=seed + 2),
              shape(lib.rrect(m + 6, -250, x1 - 70, -145, 22), col, "", w=3.6, seed=seed + 3)]
    o += [shape(lib.rrect(x0 - 20, -230, x0 + 70, -40, 26), sh, "", w=4.0, seed=seed + 4),
          shape(lib.rrect(x1 - 70, -230, x1 + 20, -40, 26), sh, "", w=4.0, seed=seed + 5)]
    for xx in (x0 + 20, x1 - 40):
        o.append(f'<rect x="{xx}" y="-40" width="20" height="40" fill="#6b4a30" stroke="{INK}" stroke-width="2.5"/>')
    return "".join(o)


def lamp(x, seed=0, on=1.0):
    o = [line([(x, 0), (x, -560)], 6, INK, seed=seed), f'<ellipse cx="{x}" cy="-4" rx="50" ry="10" fill="{INK}"/>',
         shape([(x - 70, -560), (x + 70, -560), (x + 44, -680), (x - 44, -680)], "#f6d36a", "", w=3.6, seed=seed + 1)]
    if on:
        g = lib.rad_grad([(0, "#fff1b0", .5 * on), (1, "#fff1b0", 0)], .5, .5, .5)
        o.insert(0, f'<ellipse cx="{x}" cy="-560" rx="260" ry="200" fill="url(#{g})"/>')
    return "".join(o)


def picture(cx, cy, w, h, seed=0):
    return shape(lib.rect_pts(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), "#c8a060",
                 f'<rect x="{cx - w / 2 + 14}" y="{cy - h / 2 + 14}" width="{w - 28}" height="{h - 28}" fill="#9fd0c0"/>'
                 f'<path d="M{cx - w / 2 + 14} {cy + h / 2 - 14} L{cx - w * .1} {cy - h * .1} L{cx + w * .1} {cy + h * .12} L{cx + w * .25} {cy - h * .02} L{cx + w / 2 - 14} {cy + h / 2 - 14}Z" fill="#5fa07a"/>'
                 f'<circle cx="{cx + w * .22}" cy="{cy - h * .22}" r="{h * .1}" fill="#ffd84a"/>', w=3.6, seed=seed)


def plant(x, seed=0, t=0.0):
    o = [shape([(x - 50, -120), (x + 50, -120), (x + 38, 0), (x - 38, 0)], "#d27a4a", "", w=3.6, seed=seed)]
    for i in range(6):
        a = -1.2 + .5 * i + .05 * math.sin(t * 2 + i)
        L = 150 + 30 * (i % 3)
        tip = (x + L * math.sin(a), -120 - L * math.cos(a))
        mid = (x + L * .5 * math.sin(a) + 20, -120 - L * .5 * math.cos(a))
        o.append(shape([(x, -120), mid, tip, (mid[0] - 30, mid[1] + 10)], "#5fb07a", "", w=3.0, seed=seed + i))
    return "".join(o)


def room_back(xa=-900, xb=3800, behind=""):
    """Стена, пол, мебель — по иксу мира. Окно 1 (100..420), шкаф (670..970), полка (1150..1500), картина, диван, лампа."""
    g = lib.lin_grad([(0, "#f6ead2", 1), (1, WALL, 1)], 0, -1200, 0, 0, units="userSpaceOnUse")
    o = [f'<rect x="{xa}" y="-1500" width="{xb - xa}" height="1500" fill="url(#{g})"/>']
    o += [f'<rect x="{x}" y="-1500" width="40" height="1500" fill="{WALL_SH}" opacity=".35"/>' for x in range(int(xa) // 120 * 120, int(xb), 120)]
    o.append(f'<rect x="{xa}" y="0" width="{xb - xa}" height="900" fill="{FLOOR}"/>')
    o += [line([(x, 0), (x - 300, 900)], 3, FLOOR_SH, seed=x) for x in range(int(xa) // 200 * 200, int(xb) + 400, 200)]
    o.append(f'<rect x="{xa}" y="-34" width="{xb - xa}" height="34" fill="#fbf6ea" stroke="{INK}" stroke-width="3"/>')
    o.append(rugs())
    o.append(plant(-250, 11))
    o.append(win(100, -780, 420, -420, 3))
    o.append(behind)
    o.append(wardrobe(670, 970, -900, 5))
    o.append(bookshelf(1150, 1500, -820, 7))
    o.append(picture(1720, -640, 220, 160, 9))
    o.append(sofa(1900, 2450, 13))
    o.append(lamp(2600, 15))
    o.append(win(2800, -780, 3150, -420, 17))
    o.append(wardrobe(3350, 3650, -900, 19))
    return "".join(o)


def rugs():
    return "".join(shape(ellipse_pts(rx_, 230, 520, 120, 28), rc, f'<ellipse cx="{rx_}" cy="230" rx="430" ry="90" fill="none" stroke="#fbf6ea" stroke-width="10" opacity=".7"/>', w=3.6, seed=rx_)
                   for rx_, rc in ((850, "#d9604a"), (2150, "#4aa39a")))


def coffee_table(x0, x1, top=-150.0, front=40.0, seed=0):
    o = [f'<ellipse cx="{(x0 + x1) / 2:.0f}" cy="{front + 6:.0f}" rx="{(x1 - x0) * .55:.0f}" ry="18" fill="#000" opacity=".12"/>']
    for xx in (x0 + 20, x1 - 40):
        o.append(f'<rect x="{xx}" y="{top + 20}" width="20" height="{front - top - 20}" fill="#7a5034" stroke="{INK}" stroke-width="2.5"/>')
    o.append(shape(lib.rrect(x0, top - 10, x1, top + 26, 10), "#a8784f", f'<rect x="{x0}" y="{top - 10}" width="{x1 - x0}" height="12" fill="#c49264"/>', w=3.6, seed=seed))
    return "".join(o)


def cat_peek(x_edge, y_head, k, u, t, side=-1, st=None, clip=None):
    """Голова кота выглядывает из-за края x_edge (side −1 — влево из-за предмета справа, +1 — вправо). u 0…1 — насколько выглянул.
    Рисовать ДО предмета, который прячет кота; clip — (x, y, w, h) области, где кот виден."""
    s = dict(perk=.8, look=(side * .5, .2), turn=side * .35, tail=0.0)
    if st:
        s.update(st)
    hx = x_edge + side * (-140 * k + 185 * k * u)
    cs = PE.cat_svg(hx, y_head + 234 * k, k, s, t)
    if side > 0:
        cs = f'<g transform="translate({2 * hx:.2f} 0) scale(-1 1)">{cs}</g>'
    if clip:
        c = lib.clip_rect(*clip)
        cs = f'<g clip-path="url(#{c})">{cs}</g>'
    return cs


# ═════════════════════════ хук s01–s02 и петля s17: бег/шаг по комнате ═════════════════════════
HOOK = dict(a=-0.4, b=T1("s02") + 0.6, x0=0.0, tc=0.2, st=0.55, step=190.0, leap=None, stumble=None)
_CUR = [None]


def ensure(kind):
    if _CUR[0] == kind:
        return
    _CUR[0] = kind
    if kind == "hook":
        plan(HOOK)
    elif kind == "walk":
        plan(dict(a=T0("s17") - 1.5, b=T1("s17") + .5, x0=-560.0, tc=0.46, st=0.62, step=150.0, walk=True))


def part_cam(t, t_ref, s, sx, gy, follow, shake=1.0, drift=1.0):
    """Камера, которая летит за Димой не целиком: follow — доля его хода (0.45 — комната плывёт, Дима бежит через кадр)."""
    cx, cy, s_, rot = run_cam(t, s, sx, gy, shake, drift)
    h0 = hip_at(t_ref, bob=False)[0]
    h = hip_at(t, bob=False)[0]
    return cx - (1 - follow) * (h - h0), cy, s_, rot


def run_cam(t, s, sx, gy, shake=1.0, drift=1.0):
    return track_cam(t, s, sx, gy, shake=0.0 if NOCAM else shake, drift=0.0 if NOCAM else drift)


def world_x_at(cam, sx_screen):
    cx, cy, s, rot = cam
    return cx + (sx_screen - 540) / s


KX1 = None


def frame_s01(t):
    ensure("hook")
    s, gy = 1.25, 1350.0
    cam = part_cam(t, 0.0, s, 260.0, gy, .45)
    lib.DEFS.clear()
    p = run_pose(t)
    p["expr"].update(look=(-.7, -.5) if (t // .35) % 2 == 0 else (-.4, .2), brows="up", mouth="gape" if t > W(3) else "flat", lid=1.0)
    dg, wr = dima.draw(p)
    kx = 828.0
    thr = throws(t, -1.2, T1("s02"), .26, lambda tl: (hip_at(tl, bob=False)[0] - 40, -520.0), -520.0, 85, floor=60.0, k=1.5)
    front = coffee_table(kx - 170, kx + 190, seed=21) + keys(kx, -175, 1.5, -12, glow=.4, seed=3)
    cu = cat_u(1, t)
    catl = cat_peek(670.0, -400.0, .52, cu, t, side=-1, clip=(400, -900, 270, 900)) if cu is not None else ""
    world = room_back(behind=catl) + dg + front + thr
    if MASK:
        lib.DEFS.append(MASK_F)
        return lib.svg('<rect width="1080" height="1920" fill="#000"/><g filter="url(#mk85)">'
                       f'<g transform="{lib.cam(*cam)}">{room_back_items() + dg + front + thr}</g></g>')
    body = f'<rect width="1080" height="1920" fill="{WALL}"/><g transform="{lib.cam(*cam)}">{world}</g>'
    if NOCAM:
        return lib.svg(body)
    return lib.svg(hook_wrap(body, t, W(3)) + title(t))


def room_back_items():
    """Мебель без стены и пола (для маски заполнения хука)."""
    return (rugs() + plant(-250, 11) + win(100, -780, 420, -420, 3) + wardrobe(670, 970, -900, 5) + bookshelf(1150, 1500, -820, 7)
            + picture(1720, -640, 220, 160, 9) + sofa(1900, 2450, 13) + lamp(2600, 15))


def mirror(svg_):
    return f'<g transform="translate(1080 0) scale(-1 1)">{svg_}</g>'


def frame_s02(t):
    """Ниже и ближе, зеркально: Дима бежит влево мимо того же столика, ключи крупно на переднем плане."""
    ensure("hook")
    s, gy = 1.32, 1390.0
    a = T0("s02")
    cam = part_cam(t, a, s, 250.0, gy, .72, shake=1.2)
    cx, cy, s_, rot = cam
    cam = (cx, cy, s_, rot + (0 if NOCAM else 2.0 * kick2(t, W(5))))
    lib.DEFS.clear()
    p = run_pose(t)
    p["expr"].update(look=(-.8, -.3) if (t // .3) % 2 else (-.3, -.7), brows="up", mouth="gape", lid=1.0)
    dg, wr = dima.draw(p)
    kx = world_x_at(part_cam(a + .7, a, s, 250.0, gy, .72, 0, 0), 560)
    thr = throws(t, a - .6, T1("s02"), .22, lambda tl: (hip_at(tl, bob=False)[0] - 40, -520.0), -560.0, 86, floor=60.0, k=1.5)
    front = coffee_table(kx - 170, kx + 190, seed=21) + keys(kx, -175, 1.5, -12, glow=.4, seed=3)
    world = room_back() + dg + front + thr
    z = 1 + (0 if NOCAM else .07 * kick2(t, W(5)))
    body = (f'<rect width="1080" height="1920" fill="{WALL}"/>'
            f'<g transform="translate(540 {PIV}) scale({z:.4f}) translate(-540 {-PIV})">{mirror(f"<g transform=\"{lib.cam(*cam)}\">{world}</g>")}</g>')
    return lib.svg(body + title(t))


# ═════════════════════════ стоячие сцены: стена, Дима ═════════════════════════
def view(body, cx=540.0, cy=960.0, s=1.0, rot=0.0, bg=WALL, over=""):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def drift(t, a=1.0):
    return 10 * a * math.sin(t * 1.7 + .5), 7 * a * math.sin(t * 2.3), .5 * a * math.sin(t * 1.3)


def wall_bg(floor_y=1500.0, x0=-600, x1=1680):
    g = lib.lin_grad([(0, "#f6ead2", 1), (1, WALL, 1)], 0, 0, 0, floor_y, units="userSpaceOnUse")
    o = [f'<rect x="{x0}" y="-600" width="{x1 - x0}" height="{floor_y + 600}" fill="url(#{g})"/>']
    o += [f'<rect x="{x}" y="-600" width="40" height="{floor_y + 600}" fill="{WALL_SH}" opacity=".35"/>' for x in range(x0 // 120 * 120, x1, 120)]
    o.append(f'<rect x="{x0}" y="{floor_y}" width="{x1 - x0}" height="1400" fill="{FLOOR}"/>')
    o.append(f'<rect x="{x0}" y="{floor_y - 34}" width="{x1 - x0}" height="34" fill="#fbf6ea" stroke="{INK}" stroke-width="3"/>')
    return "".join(o)


def dfig(x, hip, k, expr="calm82", pose="d82_rest", t=0.0, **kw):
    return PE.dima82(x, hip, k, expr, pose, t=t, feet=kw.pop("feet", PE.stand_kw(x, hip, k)["feet"]), **kw)


def ex(name, **kw):
    d = dict(PE.EXPR["dima"][name])
    d.update(kw)
    return d


def frame_s03(t):
    """Стоп: хлопает по карманам и вертит головой; ключи висят на крючке прямо у его головы."""
    lib.DEFS.clear()
    a = T0("s03")
    o = [wall_bg(1900.0)]
    o.append(win(-120, 560, 160, 1000, 31))
    # вешалка с крючками и ключи
    o.append(shape(lib.rrect(700, 820, 1100, 860, 10), "#a8784f", "", w=3.4, seed=33))
    for i, hx in enumerate((760, 880, 1000)):
        o.append(line([(hx, 850), (hx, 892), (hx + 18, 900)], 7, INK, seed=40 + i))
    sw = 6 * math.sin((t - a) * 9) * math.exp(-(t - a) * 1.2) + 3 * math.sin(t * 4)
    o.append(shape([(980, 860), (1100, 870), (1110, 1200), (1050, 1230), (990, 1190)], "#5a7fb8", line([(1020, 880), (1060, 1180)], 3, "#3d5f96"), w=3.6, seed=35))
    o.append(keys(880, 905, 1.7, 70 + sw, glow=.45 + .25 * math.sin(t * 6), seed=7))
    o.append(sparkle(880, 990, 70, W(7) - .1, t))
    ph = (t - a) / .3
    u = smooth(.35, .65, ph % 1.0) if int(ph) % 2 == 0 else 1 - smooth(.35, .65, ph % 1.0)
    head = .22 * math.sin((t - a) * 2 * math.pi * 1.6)
    e = ex("panic82", look=(-.9 if head > 0 else .5, -.4 if head > 0 else .3))
    f_ = dfig(380, 1660, 1.1, e, ("d82_pocket", "ask_palms"), t=t, u=u, head_add=head)
    o.append(f_["svg"])
    dx, dy, r = drift(t, 1.5)
    z = 1.0 + .06 * kick2(t, W(7)) + .03 * (t - a)
    return view("".join(o), 540 + dx, 960 + dy, z, r + 1.5 * kick2(t, W(7)), over=title(t))


# ═════════════════════════ s04: «Не моргай» — лицо крупно, часы без цифр ═════════════════════════
def wall_clock(x, y, r, t, speed=1.0):
    o = [shape(ellipse_pts(x, y, r, r, 32), "#ffffff", "", w=6.0, seed=61),
         f'<circle cx="{x}" cy="{y}" r="{r - 14}" fill="none" stroke="#e2493b" stroke-width="8"/>']
    for i in range(12):
        a = 2 * math.pi * i / 12
        L = 26 if i % 3 == 0 else 14
        o.append(line([(x + (r - 30) * math.sin(a), y - (r - 30) * math.cos(a)), (x + (r - 30 - L) * math.sin(a), y - (r - 30 - L) * math.cos(a))], 6, INK, seed=i))
    am = t * .4
    o.append(line([(x, y), (x + r * .45 * math.sin(am), y - r * .45 * math.cos(am))], 12, INK, seed=70))
    a_s = t * 2 * math.pi * speed
    o.append(line([(x - r * .15 * math.sin(a_s), y + r * .15 * math.cos(a_s)), (x + r * .78 * math.sin(a_s), y - r * .78 * math.cos(a_s))], 5, "#e2493b", seed=71))
    o.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{INK}"/>')
    return "".join(o)


def frame_s04(t):
    lib.DEFS.clear()
    a = T0("s04")
    tw = W(16)                       # «секунду»: стрелка срывается
    o = [wall_bg(2600.0)]
    sp = 1.2 + 2.5 * smooth(tw - .1, tw + .2, t)
    o.append(wall_clock(800, 360, 150, (t - a) * (1 + 1.5 * smooth(tw - .1, tw + .2, t)), sp))
    o.append(picture(150, 330, 220, 170, 63))
    seq = [(-.9, -.1), (.9, -.3), (.1, -.9), (.8, .5), (-.7, .4), (0, 0)]
    k_ = int((t - a) / .28)
    lk = seq[k_ % len(seq)]
    e = ex("saucer", look=lk)
    e["closed"] = 0.0
    if W(10) - .02 < t < W(10) + .12:             # «моргай»: веки дёргаются и снова распахнуты
        e["closed"] = .55 * math.sin(math.pi * (t - W(10) + .02) / .14)
    f_ = dfig(470, 1980, 2.05, e, "d82_rest", t=t, head_add=.06 * math.sin((t - a) * 7))
    o.append(f_["svg"])
    hx, hy = f_["head"]
    for i in range(2):                            # капли пота
        u = ((t - a) * .9 + i * .5) % 1
        o.append(shape(lib.T([(0, -26), (14, 4), (0, 18), (-14, 4)], hx - 210 + 40 * i, hy - 130 + 160 * u), "#bfe3f7", "", w=2.6, seed=80 + i))
    o.append(burst(800, 360, 230, tw, t, "#e2493b", 12, .4))
    dx, dy, r = drift(t, 1.2)
    z = 1.0 + .05 * (t - a) + .07 * kick2(t, W(10)) + .1 * kick2(t, tw)
    return view("".join(o), 540 + dx, 900 + dy, z, r + 2 * kick2(t, tw))


# ═════════════════════════ s05–s06: телефон (призыв без букв, без кота) ═════════════════════════
PH = (250.0, 290.0, 830.0, 1330.0)      # корпус телефона на экране


def phone_body(inner, t, rot=0.0, tap=None):
    x0, y0, x1, y1 = PH
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c = lib.clip_rect(x0 + 18, y0 + 18, x1 - x0 - 36, y1 - y0 - 36, 46)
    o = [f'<ellipse cx="{cx + 30}" cy="{y1 + 30}" rx="380" ry="60" fill="#000" opacity=".12"/>',
         shape(lib.rrect(x0, y0, x1, y1, 64), "#24262e", "", w=5.0, seed=90),
         f'<g clip-path="url(#{c})"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#f7f8fb"/>{inner}</g>',
         f'<rect x="{cx - 70}" y="{y0 + 30}" width="140" height="26" rx="13" fill="#24262e"/>']
    # пальцы слева и большой палец справа
    for i in range(3):
        o.append(shape(lib.rrect(x0 - 46, y0 + 380 + 120 * i, x0 + 22, y0 + 470 + 120 * i, 34), "#f0c9a6", "", w=3.6, seed=91 + i))
    tip = tap if tap is not None else (x1 - 40, y1 - 260)
    base = (x1 + 260, y1 + 260)
    d = np.array(tip) - np.array(base)
    L = float(np.linalg.norm(d))
    ang = math.degrees(math.atan2(d[1], d[0]))
    th = shape(lib.rrect(-60, -62, L + 52, 62, 60), "#f0c9a6", f'<rect x="{L - 40}" y="-40" width="72" height="80" rx="34" fill="#f8e2cc" stroke="{INK}" stroke-width="2.5"/>', w=4.0, seed=95)
    o.append(f'<g transform="translate({base[0]:.1f} {base[1]:.1f}) rotate({ang:.2f})">{th}</g>')
    body = "".join(o)
    return f'<g transform="rotate({rot:.2f} {cx} {cy})">{body}</g>'


def mini_room(x0, y0, w, h):
    return (f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{WALL}"/>'
            f'<rect x="{x0}" y="{y0 + h * .72}" width="{w}" height="{h * .28}" fill="{FLOOR}"/>'
            f'<rect x="{x0 + w * .08}" y="{y0 + h * .2}" width="{w * .2}" height="{h * .52}" fill="#9a6a45" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="{x0 + w * .62}" y="{y0 + h * .15}" width="{w * .26}" height="{h * .25}" fill="#9fd0f0" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="{x0 + w * .38}" y="{y0 + h * .66}" width="{w * .3}" height="{h * .08}" fill="#a8784f" stroke="{INK}" stroke-width="3"/>'
            + keys(x0 + w * .53, y0 + h * .64, .55, -10, seed=97))


def comment_row(x, y, col, n1, n2, hl=0.0, seed=0):
    o = []
    if hl > 0:
        o.append(f'<rect x="{x - 20}" y="{y - 46}" width="560" height="104" rx="20" fill="#ffe9a8" opacity="{hl:.2f}"/>')
    o.append(f'<circle cx="{x + 28}" cy="{y}" r="30" fill="{col}" stroke="{INK}" stroke-width="3"/>')
    o.append(f'<rect x="{x + 76}" y="{y - 24}" width="{n1}" height="16" rx="8" fill="#9aa3b0"/>')
    o.append(f'<rect x="{x + 76}" y="{y + 6}" width="{n2}" height="16" rx="8" fill="#cfd5de"/>')
    o.append(f'<path d="M{x + 480} {y - 6} c-10 -16 -32 -6 -22 10 l22 18 l22 -18 c10 -16 -12 -26 -22 -10z" fill="none" stroke="#9aa3b0" stroke-width="4"/>')
    return "".join(o)


def frame_s05(t):
    lib.DEFS.clear()
    a = T0("s05")
    x0, y0, x1, y1 = PH
    ttap = W(18)                         # «кот»: палец жмёт в поле
    tsend = WE(20)                       # «комментариях»: отправлено
    inner = [mini_room(x0 + 18, y0 + 18, x1 - x0 - 36, 360)]
    rows = [("#8fd16a", 300, 200), ("#e8834a", 240, 330), ("#8a6fc4", 340, 180), ("#4a8fd8", 260, 280)]
    up = 120 * ease_out(clamp((t - tsend) / .3))
    ny = y0 + 470
    if t >= tsend:
        sc = ease_out(clamp((t - tsend) / .25))
        inner.append(f'<g transform="translate({x0 + 40} {ny + 50}) scale({sc:.3f}) translate({-(x0 + 40)} {-(ny + 50)})">'
                     + comment_row(x0 + 40, ny + 50, "#d4a23a", 230, 150, hl=1 - .5 * clamp((t - tsend - .4) / .6)) + "</g>")
    for i, (c, n1, n2) in enumerate(rows):
        inner.append(comment_row(x0 + 40, ny + 50 + 120 * i + up, c, n1, n2, seed=i))
    # поле ввода
    fy = y1 - 150
    act = t >= ttap
    inner.append(f'<rect x="{x0 + 18}" y="{fy - 40}" width="{x1 - x0 - 36}" height="190" fill="#eef1f6"/>')
    inner.append(f'<rect x="{x0 + 40}" y="{fy}" width="{x1 - x0 - 170}" height="76" rx="38" fill="#ffffff" stroke="{"#4a8fd8" if act else "#b8c0cc"}" stroke-width="{5 if act else 3}"/>')
    if not act or t >= tsend:
        if int(t * 2.5) % 2 == 0:
            inner.append(f'<rect x="{x0 + 76}" y="{fy + 16}" width="6" height="44" rx="3" fill="#4a8fd8"/>')
    else:
        for j in range(3):
            bob = 10 * max(0.0, math.sin((t - ttap) * 12 - j * .9))
            inner.append(f'<circle cx="{x0 + 90 + 36 * j}" cy="{fy + 38 - bob:.1f}" r="11" fill="#4a8fd8"/>')
    sb = 1 + .25 * kick2(t, tsend)
    inner.append(f'<g transform="translate({x1 - 80} {fy + 38}) scale({sb:.3f})"><circle r="38" fill="#4a8fd8" stroke="{INK}" stroke-width="3"/>'
                 '<path d="M-14 -16 L18 0 L-14 16 L-8 0Z" fill="#fff"/></g>')
    for j in range(4):                    # сердечки после отправки
        u = (t - tsend - .1 * j) / .9
        if 0 <= u < 1:
            hx, hy = x1 - 90 - 40 * j + 20 * math.sin(u * 8 + j), fy - 30 - 380 * u
            inner.append(f'<path transform="translate({hx:.1f} {hy:.1f}) scale({1.4 * (1 - .4 * u):.2f})" d="M0 6 c-10 -16 -32 -6 -22 10 l22 18 l22 -18 c10 -16 -12 -26 -22 -10z" fill="#e2493b" opacity="{1 - u:.2f}"/>')
    # большой палец: ждёт → жмёт в поле → жмёт «отправить»
    rest = (x1 - 20, y1 - 330)
    fieldp = (x0 + 260, fy + 40)
    sendp = (x1 - 80, fy + 40)
    if t < ttap:
        tp = np.array(rest) + (np.array(fieldp) - np.array(rest)) * ease_io(clamp((t - (ttap - .35)) / .35))
    elif t < tsend - .25:
        tp = np.array(fieldp) + np.array([0, 10 * kick2(t, ttap)])
    else:
        tp = np.array(fieldp) + (np.array(sendp) - np.array(fieldp)) * ease_io(clamp((t - (tsend - .25)) / .25)) + np.array([0, 10 * kick2(t, tsend)])
    body = phone_body("".join(inner), t, rot=-3 + 1.2 * math.sin(t * 2), tap=tuple(tp))
    dx, dy, r = drift(t)
    z = 1.04 + .03 * (t - a) + .05 * kick2(t, tsend)
    return view(body + burst(sendp[0], sendp[1], 110, tsend, t, "#4a8fd8", 10, .35), 540 + dx, 820 + dy, z, r, bg="#d9e8f2")


def envelope(x, y, k, rot, open_=0.0):
    o = [shape(lib.rrect(-80, -52, 80, 52, 8), "#ffffff", "", w=4.0, seed=101),
         line([(-78, -48), (0, 10 - 60 * open_), (78, -48)], 4, INK, seed=102),
         f'<rect x="-30" y="12" width="60" height="22" rx="4" fill="#e2493b"/>']
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f})">{"".join(o)}</g>'


def magnifier(x, y, k, rot=0.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f})">'
            + shape(lib.rrect(30, 26, 120, 52, 12), "#6b4a30", "", w=3.4, seed=111)
            + f'<circle cx="0" cy="0" r="52" fill="#d8eefb" fill-opacity=".55" stroke="{INK}" stroke-width="12"/>'
            + f'<circle cx="0" cy="0" r="52" fill="none" stroke="#c9d1da" stroke-width="6"/><path d="M-26 -18 Q-20 -32 -4 -36" stroke="#fff" stroke-width="7" fill="none"/></g>')


def frame_s06(t):
    lib.DEFS.clear()
    a = T0("s06")
    x0, y0, x1, y1 = PH
    tin = W(23)                  # «пришлю»: печатает
    tenv = W(26)                 # «личку»: конверт влетает
    tcirc = W(29)                # «прятался»: круг дорисован
    inner = [f'<rect x="{x0}" y="{y0 + 70}" width="{x1 - x0}" height="110" fill="#eef1f6"/>',
             f'<circle cx="{x0 + 90}" cy="{y0 + 125}" r="34" fill="#4a8fd8" stroke="{INK}" stroke-width="3"/>',
             f'<rect x="{x0 + 140}" y="{y0 + 106}" width="190" height="18" rx="9" fill="#9aa3b0"/>',
             f'<rect x="{x0 + 140}" y="{y0 + 132}" width="110" height="14" rx="7" fill="#cfd5de"/>']
    # мой комментарий справа (уже отправлен)
    inner.append(f'<rect x="{x1 - 300}" y="{y0 + 230}" width="250" height="80" rx="34" fill="#d4a23a"/>'
                 f'<rect x="{x1 - 270}" y="{y0 + 262}" width="170" height="16" rx="8" fill="#fff4d6"/>')
    if tin <= t < tenv + .15:
        inner.append(f'<rect x="{x0 + 50}" y="{y0 + 360}" width="170" height="80" rx="34" fill="#e3e7ee"/>')
        for j in range(3):
            bob = 10 * max(0.0, math.sin((t - tin) * 12 - j * .9))
            inner.append(f'<circle cx="{x0 + 95 + 40 * j}" cy="{y0 + 400 - bob:.1f}" r="12" fill="#8a96a3"/>')
    if t >= tenv + .15:
        u = ease_out(clamp((t - tenv - .15) / .25))
        bx, by = x0 + 50, y0 + 360
        g = (f'<rect x="{bx}" y="{by}" width="440" height="430" rx="34" fill="#e3e7ee"/>'
             + f'<g clip-path="url(#{lib.clip_rect(bx + 20, by + 20, 400, 300, 22)})">{mini_room(bx + 20, by + 20, 400, 300)}'
             + f'<rect x="{bx + 20}" y="{by + 20}" width="400" height="300" fill="#ffffff" opacity=".35"/></g>'
             + f'<rect x="{bx + 30}" y="{by + 345}" width="300" height="18" rx="9" fill="#9aa3b0"/><rect x="{bx + 30}" y="{by + 380}" width="200" height="16" rx="8" fill="#cfd5de"/>')
        cu = clamp((t - (tcirc - .9)) / .9)       # красный круг рисуется от руки на «где он прятался»
        if cu > 0:
            ccx, ccy, rr = bx + 120, by + 120, 60
            pts = [(ccx + rr * 1.1 * math.cos(-1.2 + 2 * math.pi * 1.08 * cu * q / 30), ccy + rr * math.sin(-1.2 + 2 * math.pi * 1.08 * cu * q / 30)) for q in range(31)]
            g += line(pts, 7, "#e2493b", taper=.2, seed=121)
        g += magnifier(bx + 330 - 120 * ease_io(clamp((t - tcirc + .8) / .7)), by + 210 - 60 * ease_io(clamp((t - tcirc + .8) / .7)), .9, -20)
        inner.append(f'<g transform="translate({bx} {by + 215}) scale({u:.3f}) translate({-bx} {-(by + 215)})">{g}</g>')
    body = phone_body("".join(inner), t, rot=3 - 1.0 * math.sin(t * 2))
    # конверт влетает сверху справа в телефон
    env = ""
    if tenv - .45 <= t < tenv + .15:
        u = clamp((t - (tenv - .45)) / .45)
        ex_, ey_ = 1150 + (560 - 1150) * ease_in(u, 1.6), 120 + (700 - 120) * ease_in(u, 1.6) - 120 * math.sin(math.pi * u)
        env = envelope(ex_, ey_, 1.6 - .8 * u, 30 * (1 - u), 0)
    dx, dy, r = drift(t)
    z = 1.04 + .03 * (t - a) + .06 * kick2(t, tenv + .1)
    return view(body + env + burst(560, 700, 160, tenv + .1, t, "#ffd23f", 12, .4), 540 + dx, 820 + dy, z, r, bg="#e8dff2")


# ═════════════════════════ s07–s10: комната крупнее (экранные координаты, пол 1250) ═════════════════════════
FL = 1250.0


def chest(x0, x1, top, outs, seed=0):
    o = [shape(lib.rect_pts(x0, top, x1, FL), "#a8784f", f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="26" fill="#c49264"/>', w=4.0, seed=seed)]
    h = (FL - top - 60) / 3
    for i in range(3):
        y = top + 40 + h * i
        dx = outs[i]
        if dx > 2:
            o.append(f'<rect x="{x0 + 14 - dx * .25:.1f}" y="{y + 6:.1f}" width="{x1 - x0 - 28}" height="{h - 16:.1f}" fill="#5a3a24"/>')
        o.append(shape(lib.rect_pts(x0 + 14 - dx * .25, y + dx * .12, x1 - 14 - dx * .25, y + h - 10 + dx * .2), "#b88458",
                       f'<rect x="{(x0 + x1) / 2 - 40 - dx * .25:.1f}" y="{y + h / 2 - 8 + dx * .16:.1f}" width="80" height="16" rx="8" fill="#e8c27a" stroke="{INK}" stroke-width="2"/>',
                       w=3.4, seed=seed + 1 + i))
    return "".join(o)


def table_front(x0, x1, top, seed=0, legs=FL + 120):
    o = [f'<ellipse cx="{(x0 + x1) / 2:.0f}" cy="{legs + 4:.0f}" rx="{(x1 - x0) * .55:.0f}" ry="20" fill="#000" opacity=".12"/>']
    for xx in (x0 + 26, x1 - 50):
        o.append(f'<rect x="{xx}" y="{top + 20}" width="24" height="{legs - top - 20}" fill="#7a5034" stroke="{INK}" stroke-width="2.5"/>')
    o.append(shape(lib.rrect(x0, top - 12, x1, top + 30, 12), "#a8784f", f'<rect x="{x0}" y="{top - 12}" width="{x1 - x0}" height="14" fill="#c49264"/>', w=3.8, seed=seed))
    return "".join(o)


def frame_s07(t):
    lib.DEFS.clear()
    a = T0("s07")
    o = [wall_bg(FL)]
    o.append(win(80, 300, 380, 640, 141))
    o.append(picture(520, 420, 180, 140, 143))
    outs = [0.0, 0.0, 0.0]
    for i in range(3):
        ph = ((t - a) / .42 + i * .33) % 1.0
        outs[i] = 110 * math.sin(math.pi * ph) ** .6
    o.append(chest(640, 990, 760, outs, 145))
    # Дима у комода: роется и швыряет через плечо
    ph = (t - a) / .32
    u = smooth(.2, .5, ph % 1.0) * (1 - smooth(.6, .95, ph % 1.0))
    e = ex("panic82", look=(.7, .2) if int(ph) % 2 else (.5, .5))
    f_ = dfig(500, 1080, .92, e, ("drawer", "hooray"), t=t, u=u, head_add=.08 * math.sin((t - a) * 9))
    o.append(f_["svg"])
    o.append(throws(t, a - 1.0, T1("s07"), .32, lambda tl: (560.0, 760.0), -700.0, 87, floor=FL + 40, k=1.3, vy=-900.0))
    o.append(table_front(40, 420, 1170, 147))
    o.append(keys(230, 1150, 1.4, -14, glow=.3 + .15 * math.sin(t * 5), seed=9))
    dx, dy, r = drift(t, 1.2)
    z = 1.0 + .03 * (t - a)
    return view("".join(o), 540 + dx, 900 + dy, z, r)


def remote(x, y, k, rot):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f})">'
            + shape(lib.rrect(-26, -90, 26, 90, 18), "#3a3e48", "".join(f'<circle cx="{-10 + 20 * (j % 2)}" cy="{-50 + 24 * (j // 2)}" r="7" fill="#9aa3b0"/>' for j in range(8))
                    + '<circle cx="0" cy="-72" r="9" fill="#e2493b"/>', w=3.2, seed=151) + "</g>")


def mug(x, y, k):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})">'
            + shape([(-50, -60), (50, -60), (44, 50), (-44, 50)], "#4aa39a", '<rect x="-50" y="-30" width="100" height="14" fill="#fbf6ea" opacity=".8"/>', w=3.6, seed=153)
            + line([(50, -40), (82, -30), (84, 10), (48, 22)], 9, INK, seed=154) + "</g>")


def frame_s08(t):
    """Вставка: ключи на столике крупно, блеск на «ключи», рядом шлёпается носок."""
    lib.DEFS.clear()
    a = T0("s08")
    tk = W(37)
    o = [wall_bg(560.0)]
    o.append(shape([(-200, 640), (1280, 640), (1480, 1700), (-400, 1700)], "#a8784f",
                   "".join(line([(-300 + 260 * i, 700), (-500 + 330 * i, 1700)], 3, "#8a5c38", seed=i) for i in range(9)), w=5.0, seed=161))
    o.append(shape([(-200, 640), (1280, 640), (1290, 680), (-210, 680)], "#c49264", "", w=3.0, seed=162))
    o.append(mug(860, 820, 1.3))
    o.append(remote(200, 1060, 1.2, -30))
    ts = a + .18
    if t > ts:
        u = clamp((t - ts) / .3)
        y = 300 + (1030 - 300) * u * u
        if u >= 1:
            y = 1030 - 40 * abs(math.sin((t - ts - .3) * 14)) * math.exp(-(t - ts - .3) * 8)
        o.append(item("sock", 800, y, 1.7, 160 * (1 - u) + 15, seed=163))
    o.append(keys(520, 980, 3.2, -14, glow=.5 + .5 * kick(t, tk, .05, .4), seed=11))
    o.append(sparkle(560, 960, 210, tk, t, n=5, life=.55))
    o.append(sparkle(440, 1040, 120, tk + .18, t, n=4, life=.45))
    z = 1.0 + .1 * ease_out(clamp((t - a + .2) / 1.2)) + .06 * kick2(t, tk)
    dx, dy, r = drift(t, .6)
    return view("".join(o), 520 + dx, 960 + dy, z, r)


def frame_s09(t):
    """Дима склонился над столиком: ключи у самого носа, а он смотрит в сторону. Кот 2 — хвост с огоньком за окном."""
    lib.DEFS.clear()
    a = T0("s09")
    o = [wall_bg(FL)]
    wx0, wy0, wx1, wy1 = 690.0, 250.0, 990.0, 600.0
    o.append(win_glass(wx0, wy0, wx1, wy1))
    cu = cat_u(2, t)
    if cu is not None:
        k = .72
        feet = wy1 + 190 - 170 * cu
        cx_ = wx1 + 70
        st = dict(tail=-14 + 22 * math.sin((t - CATS[2]["t"]) * 7), look=(.5, 0), perk=.6)
        cs = cat_peek(cx_, feet - 234 * k, k, 1.0, t, side=1, st=st)    # голова — за стеной справа, видно только хвост с огоньком
        c = lib.clip_rect(wx0, wy0, wx1 - wx0, wy1 - wy0)
        o.append(f'<g clip-path="url(#{c})">{cs}</g>')
    o.append(win_frame(wx0, wy0, wx1, wy1, 171))
    o.append(shelf_simple(80, 380, 520))
    look = (-.9, -.7) if t < W(41) else (-.9, .1)
    e = ex("puzzled82", look=look)
    f_ = dfig(360, 1150, .98, e, "d82_rest", t=t, lean_add=.42 + .04 * math.sin((t - a) * 3), head_add=-.2 + .1 * math.sin((t - a) * 2.2))
    o.append(f_["svg"])
    o.append(table_front(220, 1000, 1180, 173))
    kx, ky = 800, 1162
    o.append(keys(kx, ky, 1.9, -14, glow=.35 + .25 * math.sin(t * 6), seed=13))
    o.append(sparkle(kx, ky - 20, 100, W(40), t, n=4))
    # стрелка-подсказка зрителю: ключи прямо перед ним (без букв)
    au = smooth(W(40), W(40) + .15, t)
    if au > 0:
        tip = np.array([kx + 40, ky - 70])
        tail = tip + np.array([170, -200]) * (.3 + .7 * au)
        o.append(line([tuple(tail), tuple(tip)], 14, "#e2493b", taper=.1, seed=175))
        o.append(line([(tip[0] + 58, tip[1] - 6), tuple(tip), (tip[0] + 10, tip[1] - 58)], 14, "#e2493b", taper=.1, seed=176))
    dx, dy, r = drift(t, 1.0)
    z = 1.0 + .04 * (t - a) + .05 * kick2(t, W(40))
    return view("".join(o), 540 + dx, 900 + dy, z, r)


def shelf_simple(x0, x1, y):
    rnd = random.Random(int(x0))
    o = [shape(lib.rect_pts(x0, y, x1, y + 22), "#a8784f", "", w=3.4, seed=181)]
    x = x0 + 14
    cols = ("#c94a5a", "#4a8fd8", "#e8b84a", "#5fb07a", "#8a6fc4")
    while x < x1 - 40:
        bw, bh = rnd.uniform(22, 34), rnd.uniform(90, 140)
        o.append(f'<rect x="{x:.0f}" y="{y - bh:.0f}" width="{bw:.0f}" height="{bh:.0f}" fill="{rnd.choice(cols)}" stroke="{INK}" stroke-width="2.4"/>')
        x += bw + 3
    return "".join(o)


def frame_s10(t):
    """Заглядывает под подушку дивана и разводит руками на «не видит»; ключи светятся на переднем плане."""
    lib.DEFS.clear()
    a = T0("s10")
    tn = W(46)
    o = [wall_bg(FL)]
    o.append(picture(300, 420, 240, 170, 191))
    o.append(f'<g transform="translate(0 {FL})">{sofa(40, 620, 193, col="#5a7fb8", cushion=False)}</g>')
    o.append(shape(lib.rrect(110, FL - 250, 330, FL - 145, 22), "#5a7fb8", "", w=3.6, seed=195))
    shrug = smooth(tn - .15, tn + .1, t)
    e = ex("puzzled82", look=(.2, -.7)) if t < tn else ex("puzzled82", look=(.4, .2), mouth="flat")
    f_ = dfig(540, 1090, .9, e, ("hooray", "d82_shrug"), t=t, u=shrug, head_add=-.1 + .1 * math.sin((t - a) * 3))
    o.append(f_["svg"])
    if shrug < .5:
        wn, wf = np.array(f_["wrist"]["n"]), np.array(f_["wrist"]["f"])
        m = (wn + wf) / 2 + np.array([0, -40])
        o.append(f'<g transform="translate({m[0]:.1f} {m[1]:.1f}) scale(2.3)">{item("cushion", 0, 0, 1, 6 * math.sin(t * 9), seed=197)}</g>')
    else:
        u = clamp((t - tn) / .35)
        o.append(item("cushion", 470 - 170 * u, 640 + (FL - 170 - 640) * u * u, 2.3, 120 * u, seed=197))
    o.append(table_front(700, 1100, 1200, 199))
    kx, ky = 900, 1182
    o.append(keys(kx, ky, 1.6, -14, glow=.45 + .35 * math.sin((t - a) * 7), seed=15))
    dx, dy, r = drift(t, 1.0)
    z = 1.0 + .03 * (t - a) + .05 * kick2(t, tn)
    return view("".join(o), 540 + dx, 900 + dy, z, r)


# ═════════════════════════ s11–s13: Гарвард — зал, экран, горилла, шоры ═════════════════════════
def bricks(x0, y0, x1, y1, col="#b5523b"):
    o = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{col}"/>']
    sh = lib.mul(col, (.82, .8, .8))
    for r, y in enumerate(range(int(y0), int(y1), 46)):
        o.append(f'<rect x="{x0}" y="{y + 40}" width="{x1 - x0}" height="6" fill="#e6c9b0" opacity=".75"/>')
        off = 0 if r % 2 else 60
        for x in range(int(x0) - 120 + off, int(x1), 120):
            o.append(f'<rect x="{x}" y="{y}" width="6" height="40" fill="#e6c9b0" opacity=".75"/>')
            if (x * 7 + r * 13) % 5 == 0:
                o.append(f'<rect x="{x + 8}" y="{y + 2}" width="110" height="36" fill="{sh}" opacity=".5"/>')
    return "".join(o)


def arch_window(x0, x1, y0, y1, seed=0, glow="#cfe6f6"):
    cx, r = (x0 + x1) / 2, (x1 - x0) / 2
    pts = [(x0, y1), (x0, y0 + r)] + [(cx - r * math.cos(math.pi * q / 16), y0 + r - r * math.sin(math.pi * q / 16)) for q in range(1, 16)] + [(x1, y0 + r), (x1, y1)]
    inner = (f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{glow}"/>'
             + "".join(f'<rect x="{x0 + (x1 - x0) * q / 3 - 4:.0f}" y="{y0}" width="8" height="{y1 - y0}" fill="#fbf6ea"/>' for q in (1, 2))
             + "".join(f'<rect x="{x0}" y="{y0 + r + (y1 - y0 - r) * q / 4 - 4:.0f}" width="{x1 - x0}" height="8" fill="#fbf6ea"/>' for q in (1, 2, 3)))
    return shape(pts, glow, inner, w=7.0, seed=seed, ink_color="#fbf6ea") + shape(pts, "none", "", w=3.0, seed=seed + 1)


def crest(x, y, k=1.0):
    pts = [(-80, -90), (80, -90), (80, 10), (0, 100), (-80, 10)]
    inner = "".join(f'<g transform="translate({bx} {by})"><path d="M-30 -14 Q-15 -24 0 -14 Q15 -24 30 -14 L30 14 Q15 4 0 14 Q-15 4 -30 14Z" fill="#fbf6ea" stroke="{INK}" stroke-width="2.5"/>'
                    f'<line x1="0" y1="-14" x2="0" y2="14" stroke="{INK}" stroke-width="2"/></g>' for bx, by in ((-38, -45), (38, -45), (0, 22)))
    return f'<g transform="translate({x} {y}) scale({k})">' + shape(pts, "#a51c30", inner, w=5.0, seed=211) + "</g>"


def player(x, y, k, shirt, t, ph, arm=0.0):
    sk = "#f0c9a6"
    bob = 6 * math.sin(t * 9 + ph)
    o = [line([(x - 14, y - 70), (x - 22 + 8 * math.sin(t * 7 + ph), y)], 12, "#2b3a55", seed=int(ph * 10)),
         line([(x + 14, y - 70), (x + 22 - 8 * math.sin(t * 7 + ph), y)], 12, "#2b3a55", seed=int(ph * 10) + 1),
         shape(lib.rrect(x - 34, y - 180 + bob, x + 34, y - 64, 18), shirt, "", w=3.4, seed=int(ph * 10) + 2),
         line([(x - 30, y - 160 + bob), (x - 60, y - 110 - 50 * arm + bob)], 10, sk, seed=int(ph * 10) + 3),
         line([(x + 30, y - 160 + bob), (x + 60, y - 110 - 50 * arm + bob)], 10, sk, seed=int(ph * 10) + 4),
         shape(ellipse_pts(x, y - 214 + bob, 32, 36, 14), sk, f'<path d="M{x - 32} {y - 226 + bob} Q{x} {y - 270 + bob} {x + 32} {y - 226 + bob}Z" fill="#4a3020"/>', w=3.2, seed=int(ph * 10) + 5)]
    return f'<g transform="translate({x} {y}) scale({k}) translate({-x} {-y})">{"".join(o)}</g>'


def gorilla(x, y, k, t, beat=0.0, walk=0.0):
    """Человек в костюме гориллы (смотрит на зрителя), x, y — между ступней; beat 0…1 — бьёт в грудь."""
    fur, sh, face = "#3a3438", "#262226", "#8d8590"
    sw = math.sin(walk * 2 * math.pi)
    o = [line([(x - 40, y - 150), (x - 50 - 25 * sw, y)], 46, fur, taper=.1, seed=221),
         line([(x + 40, y - 150), (x + 50 + 25 * sw, y)], 46, fur, taper=.1, seed=222),
         shape(ellipse_pts(x, y - 240, 120, 130, 22), fur, f'<ellipse cx="{x}" cy="{y - 220}" rx="70" ry="80" fill="{face}" opacity=".55"/>', w=5.0, seed=223)]
    for sgn in (-1, 1):
        if beat > 0:
            a = (math.sin(beat * 2 * math.pi * 3 + (0 if sgn < 0 else math.pi)) + 1) / 2
            hand = (x + sgn * (40 + 20 * a), y - 280 + 30 * a)
        else:
            hand = (x + sgn * 130, y - 70 - 30 * sgn * sw)
        o.append(line([(x + sgn * 100, y - 320), (x + sgn * 150, y - 220), hand], 50, fur, taper=.1, seed=224 + sgn))
        o.append(shape(ellipse_pts(hand[0], hand[1], 30, 26, 12), sh, "", w=3.2, seed=226 + sgn))
    hy = y - 410
    o.append(shape(ellipse_pts(x, hy, 82, 86, 20), fur, "", w=5.0, seed=228))
    o.append(shape(ellipse_pts(x, hy + 18, 58, 52, 16), face, f'<ellipse cx="{x - 14}" cy="{hy + 30}" rx="7" ry="5" fill="{INK}"/><ellipse cx="{x + 14}" cy="{hy + 30}" rx="7" ry="5" fill="{INK}"/>'
                   f'<path d="M{x - 26} {hy + 52} Q{x} {hy + 62 + 14 * beat} {x + 26} {hy + 52}" stroke="{INK}" stroke-width="4" fill="none"/>', w=3.4, seed=229))
    o.append(f'<path d="M{x - 52} {hy - 18} Q{x} {hy - 40} {x + 52} {hy - 18}" stroke="{sh}" stroke-width="18" fill="none"/>')
    for sgn in (-1, 1):
        o.append(f'<circle cx="{x + sgn * 24}" cy="{hy - 4}" r="9" fill="#fff"/><circle cx="{x + sgn * 24}" cy="{hy - 3}" r="5" fill="{INK}"/>')
    return f'<g transform="translate({x} {y}) scale({k}) translate({-x} {-y})">{"".join(o)}</g>'


def court(x0, y0, w, h, t, gor=None):
    """Видео на экране: спортзал, четверо пасуют мяч (белые и чёрные футболки); gor = (x доля, beat, walk) — горилла."""
    c = lib.clip_rect(x0, y0, w, h)
    k = h / 640
    o = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h * .62}" fill="#d9d2c4"/>',
         f'<rect x="{x0}" y="{y0 + h * .62}" width="{w}" height="{h * .38}" fill="#d9a865"/>',
         f'<rect x="{x0}" y="{y0 + h * .3}" width="{w}" height="10" fill="#b8ae9c"/>']
    for q in range(5):
        o.append(f'<rect x="{x0 + w * (.08 + .19 * q):.0f}" y="{y0 + h * .1:.0f}" width="{w * .1:.0f}" height="{h * .5:.0f}" fill="#c7beae"/>')
    ps = [(.16, "#ffffff", 0.0), (.38, "#2a2a2e", 1.3), (.62, "#ffffff", 2.1), (.84, "#2a2a2e", 3.7)]
    pos = [(x0 + w * px + 14 * math.sin(t * 2 + ph), y0 + h * .95) for px, _, ph in ps]
    for (px, col, ph), (xx, yy) in zip(ps, pos):
        o.append(player(xx, yy, k * 1.05, col, t, ph))
    if gor is not None:
        o.append(gorilla(x0 + w * gor[0], y0 + h * .98, k * .92, t, gor[1], gor[2]))
    # мяч: пас между белыми (0 и 2) и чёрными (1 и 3)
    for pair, off in (((0, 2), 0.0), ((3, 1), .37)):
        u = ((t * 1.25 + off) % 1.0)
        a_, b_ = pos[pair[0]], pos[pair[1]]
        if int(t * 1.25 + off) % 2:
            a_, b_ = b_, a_
        bx = a_[0] + (b_[0] - a_[0]) * u
        by = a_[1] - 150 * k - 160 * k * math.sin(math.pi * u)
        o.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{18 * k:.1f}" fill="#e8834a" stroke="{INK}" stroke-width="3"/>')
    return f'<g clip-path="url(#{c})">{"".join(o)}</g>'


def hall_heads(y, xs, k, t):
    o = []
    for i, (x, who) in enumerate(zip(xs, ("dima", "curly", "beard", "stud82", "girl", "youth"))):
        b = PE.dima_back(x, y + 6 * math.sin(t * 1.5 + i), k, tilt=.04 * math.sin(t + i), who=who)
        o.append(b["svg"])
    return "".join(o)


def frame_s11(t):
    lib.DEFS.clear()
    a = T0("s11")
    o = [bricks(-400, -600, 1480, 1300)]
    o.append(arch_window(20, 200, 40, 620, 231))
    o.append(arch_window(880, 1060, 40, 620, 233))
    o.append(crest(540, 160, 1.0 + .08 * kick2(t, W(50))))
    o.append(f'<rect x="-400" y="1300" width="1880" height="900" fill="#5a3a2a"/>')
    o.append(shape(lib.rect_pts(150, 330, 930, 840), "#2b2e36", "", w=4.0, seed=235))
    o.append(court(170, 350, 740, 470, t))
    o.append(f'<rect x="200" y="840" width="680" height="16" fill="#7a5034"/>')
    o.append(hall_heads(1080, [120, 400, 680, 960], .62, t))
    u = ease_io(clamp((t - a) / (W(52) - a)))
    z = 1.45 + (1.0 - 1.45) * u
    cy = 470 + (900 - 470) * u
    dx, dy, r = drift(t, .6)
    return view("".join(o), 540 + dx, cy + dy, z, r, bg="#b5523b")


def frame_s12(t):
    """Экран крупно: через кадр между игроками проходит человек в костюме гориллы и бьёт себя в грудь."""
    lib.DEFS.clear()
    a = T0("s12")
    tin, tb = W(57), W(61)              # «проходит» — входит справа; «гориллы» — бьёт в грудь
    gx = None
    if t >= tin - .1:
        u = clamp((t - (tin - .1)) / (tb - tin + .1))
        gx = 1.15 + (.5 - 1.15) * ease_out(u, 2)
        if t > tb + .5:
            gx = .5 - .5 * (t - tb - .5)
    beat = clamp((t - tb) / .5) if tb <= t < tb + .5 else 0.0
    gor = (gx, beat, (t - tin) * 1.6) if gx is not None else None
    o = [f'<rect x="-300" y="-300" width="1680" height="2520" fill="#1d1f26"/>',
         shape(lib.rect_pts(20, 360, 1060, 1060), "#2b2e36", "", w=4.0, seed=241),
         court(40, 380, 1000, 660, t, gor)]
    o.append(hall_heads(1260, [180, 540, 900], .8, t))
    dx, dy, r = drift(t, .5)
    z = 1.0 + .03 * (t - a) + .07 * kick2(t, tb) + .05 * kick2(t, tin + .3)
    return view("".join(o), 540 + dx + 30 * smooth(tin, tin + 1, t), 840 + dy, z, r, bg="#1d1f26")


def blinkers(head, sc, u, seed=0):
    """Шоры: два тёмных кожаных щитка сбоку от глаз (u 0…1 — захлопываются к глазам) и ремешок через лоб."""
    hx, hy = head
    hx, hy = hx + 24 * sc, hy - 30 * sc          # середина глаз (от точки головы person)
    o = [f'<path d="M{hx - 80 * sc} {hy - 20 * sc} Q{hx} {hy - 60 * sc} {hx + 80 * sc} {hy - 20 * sc}" stroke="#3b2618" stroke-width="{12 * sc:.1f}" fill="none"/>']
    for sgn, dxo, dxc in ((-1, 130, 78), (1, 130, 78)):
        cx = hx + sgn * (dxo + (dxc - dxo) * u) * sc
        pts = lib.T(lib.rrect(-20, -70, 20, 70, 16), cx, hy, sc, sgn * (35 - 30 * u))
        o.append(shape(pts, "#4a2c1a", f'<path d="M{cx:.1f} {hy - 55 * sc:.1f} L{cx:.1f} {hy + 55 * sc:.1f}" stroke="#c8a070" stroke-width="{3 * sc:.1f}" stroke-dasharray="{8 * sc:.1f} {6 * sc:.1f}"/>', w=4.0, seed=seed + (sgn > 0)))
    return "".join(o)


def frame_s13(t):
    """Зрители спереди, лица в свете экрана: у половины на глазах закрываются шоры — они видят только мяч; двое других разинули рты."""
    lib.DEFS.clear()
    a = T0("s13")
    tz = W(62)                 # «Половина» — шоры захлопываются
    tn = W(65)                 # «не заметила»
    o = [f'<rect x="-300" y="-300" width="1680" height="2520" fill="#232741"/>']
    for x in range(-5, 1200, 270):      # спинки кресел заднего ряда
        o.append(shape(lib.rrect(x - 120, 420, x + 120, 1000, 40), "#7a2a35", "", w=4.0, seed=x + 300))
    people = [("curly", 130, True), ("beard", 400, False), ("stud82", 670, True), ("youth", 940, False)]
    for i, (who, x, blind) in enumerate(people):
        if blind:
            e = {"brows": "calm", "mouth": "flat", "lid": .85, "look": (0.0, -.1)}
        else:
            e = {"brows": "up", "mouth": "o", "open": .7, "lid": 1.0, "look": (.9, -.3)}
        sc = .8
        f_ = PE.person(who, x, 1130 + 4 * math.sin(t * 2 + i), sc, e, head_add=(.1 if not blind else 0) * math.sin(t * 3 + i))
        o.append(f_["svg"])
        if blind:
            u = ease_out(clamp((t - tz) / .18), 2)
            o.append(blinkers(f_["head"], sc / .45 * .55, u, seed=250 + 3 * i))
    o.append(shape(lib.rect_pts(-300, 1100, 1380, 1500), "#5c1f28", "".join(f'<rect x="{x}" y="1100" width="12" height="400" fill="#3f141b"/>' for x in range(-140, 1300, 270)), w=4.0, seed=259))
    # свет экрана мерцает на лицах
    fl = .05 + .03 * math.sin(t * 13) + .02 * math.sin(t * 7.3)
    o.append(f'<rect x="-300" y="-300" width="1680" height="2520" fill="#bfe0ff" opacity="{fl:.3f}"/>')
    pan = -60 + 120 * ease_io(clamp((t - a) / (T1("s13") - a)))
    dx, dy, r = drift(t, .5)
    z = 1.05 + .08 * kick2(t, tz) + .04 * kick2(t, tn)
    return view("".join(o), 540 + pan + dx, 820 + dy, z, r, bg="#232741")


# ═════════════════════════ s14–s16: мозг-прожектор, «вырезает», нашёл ═════════════════════════
KEYS_SPOT = (760.0, 1150.0)


def sofa_high(x0, x1, seed=0):
    """Диван на высоких ножках (под ним щель 110 px) — в экранных координатах, пол FL."""
    lift = 110
    o = [f'<rect x="{x0 + 10}" y="{FL - lift}" width="{x1 - x0 - 20}" height="{lift}" fill="#3a3530"/>']
    for xx in (x0 + 24, x1 - 48):
        o.append(f'<rect x="{xx}" y="{FL - lift}" width="24" height="{lift}" fill="#6b4a30" stroke="{INK}" stroke-width="2.5"/>')
    return "".join(o), f'<g transform="translate(0 {FL - lift + 40})">{sofa(x0, x1, seed, col="#5a7fb8")}</g>'


def room_dark_scene(t, cat_id=None):
    """Комната для прожектора: окно, комод, диван на ножках, столик с ключами. -> (svg, координаты щели под диваном)."""
    o = [wall_bg(FL)]
    o.append(win(520, 260, 800, 600, 301))
    o.append(picture(200, 420, 200, 150, 303))
    o.append(chest(860, 1180, 780, [0, 0, 0], 305))
    under, top = sofa_high(-60, 470, 307)
    o.append(under)
    if cat_id is not None:
        cu = cat_u(cat_id, t)
        if cu is not None:
            k = .5
            hy = FL - 50 + 70 * (1 - cu)
            o.append(cat_peek(330.0, hy, k, 1.0, t, side=-1, st=dict(look=(.6, .1), turn=.3, perk=.3),
                              clip=(-60, FL - 110, 530, 110)))
    o.append(top)
    o.append(table_front(560, 960, 1170, 309))
    o.append(keys(KEYS_SPOT[0], KEYS_SPOT[1], 1.7, -14, seed=17))
    return "".join(o)


def brain(x, y, k, t, lamp=1.0):
    pts = ellipse_pts(0, 0, 110, 80, 22, jitter=.06, seed=3)
    folds = "".join(line([(-80 + 40 * i, -50 + 10 * (i % 2)), (-60 + 40 * i, -10), (-85 + 40 * i, 30 - 10 * (i % 2))], 4, "#c2607a", seed=320 + i) for i in range(5))
    o = [shape(pts, "#f4a3b8", folds + line([(0, -76), (4, 74)], 4, "#c2607a", seed=326), w=4.4, seed=321)]
    o.append(shape(ellipse_pts(118, 6, 34, 40, 16), "#ffe680", f'<ellipse cx="124" cy="0" rx="16" ry="20" fill="#fffbe0"/>', w=3.6, seed=327))
    o.append(shape(lib.rect_pts(78, -22, 100, 34), "#9aa3b0", "", w=3.0, seed=328))
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({4 * math.sin(t * 3):.1f}) scale({k:.3f})">{"".join(o)}</g>'


def spot_layer(cx, cy, r, dark, feather=40):
    m = lib.uid("m")
    g = lib.rad_grad([(0, "#000", 1), (max(0.0, (r - feather) / r), "#000", 1), (1, "#fff", 1)], .5, .5, .5)
    lib.DEFS.append(f'<mask id="{m}"><rect x="-500" y="-500" width="2100" height="2900" fill="#fff"/>'
                    f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="url(#{g})"/></mask>')
    return f'<rect x="-500" y="-500" width="2100" height="2900" fill="#0b0d1a" opacity="{dark:.3f}" mask="url(#{m})"/>'


def frame_s14(t):
    """Мозг-прожектор над головой Димы ведёт луч по тёмной комнате и останавливается на ключах на «ищет»."""
    lib.DEFS.clear()
    a = T0("s14")
    tb, tf = W(67), W(72)          # «Мозг» — появляется; «ищет» — луч встал на ключи
    o = [room_dark_scene(t)]
    e = ex("look82", look=(.6, .3))
    f_ = dfig(180, 1090, .86, e, "d82_rest", t=t, head_add=.05 * math.sin(t * 2))
    o.append(f_["svg"])
    path = [(660, 430), (1020, 900), (230, 1060), (900, 1000), KEYS_SPOT]
    u = clamp((t - (tb + .15)) / (tf - tb - .15))
    seg = min(len(path) - 2, int(u * (len(path) - 1)))
    uu = ease_io(u * (len(path) - 1) - seg)
    p = np.array(path[seg]) + (np.array(path[seg + 1]) - np.array(path[seg])) * uu
    if t >= tf:
        p = np.array(KEYS_SPOT)
    dark = .25 + .5 * smooth(tb, tb + .4, t)
    o.append(spot_layer(p[0], p[1] - 10, 150 + 20 * kick2(t, tf), dark))
    hx, hy = f_["head"]
    bx, by = hx + 30, hy - 250
    pop = back_out(clamp((t - tb) / .3)) if t >= tb else 0.0
    if pop > 0:
        lx, ly = bx + 124 * .9 * pop, by
        d = np.array(p) - np.array([lx, ly])
        n = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-6)
        o.append(f'<path d="M{lx + n[0] * 14:.1f} {ly + n[1] * 14:.1f} L{p[0] + n[0] * 150:.1f} {p[1] + n[1] * 150:.1f} L{p[0] - n[0] * 150:.1f} {p[1] - n[1] * 150:.1f} L{lx - n[0] * 14:.1f} {ly - n[1] * 14:.1f}Z" fill="#fff3a8" opacity="{.28 * pop:.2f}"/>')
        o.append(brain(bx, by, .9 * pop, t))
    o.append(sparkle(KEYS_SPOT[0], KEYS_SPOT[1] - 20, 130, tf, t, n=5))
    dx, dy, r = drift(t, .8)
    z = 1.0 + .03 * (t - a) + .05 * kick2(t, tf)
    return view("".join(o), 560 + dx, 880 + dy, z, r)


def back_out(u, s_=1.7):
    return lib.back_out(u, s_)


def scissors(x, y, ang, t):
    op = 18 * (1 + math.sin(t * 30))
    o = []
    for sgn in (-1, 1):
        o.append(f'<g transform="rotate({sgn * op:.1f})">' + shape([(0, -6), (90, -2), (90, 4), (0, 8)], "#c9d1da", "", w=3.0, seed=340 + sgn)
                 + f'<circle cx="-26" cy="{sgn * 16}" r="18" fill="none" stroke="#e2493b" stroke-width="9"/></g>')
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f})">{"".join(o)}<circle r="5" fill="{INK}"/></g>'


def frame_s15(t):
    """Всё, кроме круга с ключами, темнеет и вырезается пунктиром; кот 3 — голова из-под дивана в темноте."""
    lib.DEFS.clear()
    a = T0("s15")
    tc = W(76)                     # «вырезает»: круг замкнут
    o = [room_dark_scene(t, cat_id=3)]
    R_ = 210.0
    cx, cy = KEYS_SPOT[0], KEYS_SPOT[1] - 10
    dark = .45 + .12 * smooth(a, a + .3, t) + .3 * smooth(tc, tc + .3, t)
    o.append(spot_layer(cx, cy, R_, dark, 30))
    cu = clamp((t - (a + .2)) / (tc - a - .2))
    if cu > 0:
        n = max(2, int(60 * cu))
        pts = [(cx + R_ * math.cos(-math.pi / 2 + 2 * math.pi * cu * q / n), cy + R_ * math.sin(-math.pi / 2 + 2 * math.pi * cu * q / n)) for q in range(n + 1)]
        d = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts))
        o.append(f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="7" stroke-dasharray="22 14"/>')
        if t < tc + .1:
            ang = -90 + 360 * cu
            sx, sy = pts[-1]
            o.append(scissors(sx, sy, ang + 90, t))
    o.append(sparkle(cx, cy, 150, tc, t, n=6, life=.6))
    dx, dy, r = drift(t, .6)
    z = 1.18 + .06 * (t - a) + .06 * kick2(t, tc)
    return view("".join(o), 600 + dx, 1000 + dy, z, r)


def frame_s16(t):
    """Свет вернулся: Дима видит ключи, хватает и улыбается."""
    lib.DEFS.clear()
    a = T0("s16")
    ts, tg, tu = W(79), W(80), W(83)       # «если» — заметил; «нашёл» — схватил; «котов» — ключи вверх
    o = [wall_bg(FL)]
    o.append(win(80, 280, 380, 620, 351))
    o.append(picture(560, 420, 220, 160, 353))
    o.append(chest(860, 1180, 780, [0, 0, 0], 355))
    reach = smooth(tg - .3, tg, t)
    up = smooth(tg + .25, tu, t)
    if t < ts:
        e = ex("puzzled82", look=(-.6, -.5))
    elif t < tg + .2:
        e = ex("wow82", look=(.8, .7))
    else:
        e = ex("laugh82", look=(.4, -.2))
    pose = ("d82_rest", "offer") if up <= 0 else ("offer", "hooray")
    u = reach if up <= 0 else up
    f_ = dfig(400, 1090, .92, e, pose, t=t, u=u, head_add=-.08 * reach + .1 * up)
    o.append(f_["svg"])
    o.append(table_front(500, 980, 1170, 357))
    kx, ky = 740.0, 1150.0
    if t < tg:
        o.append(keys(kx, ky, 1.7, -14, glow=.4 + .4 * smooth(ts, ts + .2, t), seed=19))
    else:
        wn = np.array(f_["wrist"]["n"])
        o.append(keys(wn[0] + 10, wn[1] + 20, 1.7, -14 + 25 * math.sin((t - tg) * 9) * math.exp(-(t - tg) * 2), glow=.5, seed=19))
    o.append(sparkle(kx, ky - 20, 120, ts, t, n=4))
    hand = np.array(f_["wrist"]["n"])
    o.append(burst(hand[0], hand[1], 200, tu, t, "#ffd23f", 12, .45))
    o.append(sparkle(hand[0], hand[1], 230, tu + .05, t, n=6, life=.6))
    dx, dy, r = drift(t, 1.0)
    z = 1.05 + .03 * (t - a) + .07 * kick2(t, tg) + .05 * kick2(t, tu)
    return view("".join(o), 560 + dx, 900 + dy, z, r)


# ═════════════════════════ s17: петля — тот же ракурс, что у хука ═════════════════════════
def frame_s17(t):
    ensure("walk")
    a = T0("s17")
    s, gy = 1.25, 1350.0
    cam = part_cam(t, a, s, 260.0, gy, .45, shake=0.0, drift=.5)
    lib.DEFS.clear()
    p = run_pose(t)
    p["expr"].update(brows="calm", mouth="smile", lid=.8, look=(.5, -.4))
    hip = np.array(p["hip"])
    p["arms"]["n"] = ("ik", tuple(hip + np.array([150.0, -330.0])), -1)
    p["hands"] = {"n": ("open", .2), "f": "fist"}
    dg, wr = dima.draw(p)
    hn = np.array(wr["n"])
    spin = (t - a) * 720
    kk = f'<g transform="rotate({spin:.1f} {hn[0]:.1f} {hn[1] - 20:.1f})">{keys(hn[0], hn[1] - 20, 1.3, 0, seed=21)}</g>'
    world = room_back() + f'<g opacity=".18" transform="matrix(1 0 -0.9 -0.22 0 0)">{dg}</g>' + dg + kk
    body = f'<rect width="1080" height="1920" fill="{WALL}"/><g transform="{lib.cam(*cam)}">{world}</g>'
    return lib.svg(body)


def frame(sid, t):
    lib.INK_K[0] = 1.0
    return globals()["frame_" + sid](t)
