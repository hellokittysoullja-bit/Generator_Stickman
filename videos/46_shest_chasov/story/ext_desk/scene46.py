"""Сцены desk рилса 46 «мне хватает 6 часов»: s03 (полдень, Дима за ноутбуком, часы 12:00, счётчик ×1 ×2 ×3), s04 (крупно экран
с письмом, глаза бегают, петля-стрелка, лицо в ладонь), s14 (утро, письмо с первого раза, зелёная галочка).
Кот s05/s16 — в cats46.py. frame(sid, t) -> SVG 1080×1920, t — общее время ролика; удары на словах по voice/words.json."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import day  # noqa: E402
import den  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import scene as S  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


T_OBEDU = wt(12)        # 4.0
T_UZHE = wt(14)         # 4.56
T_TRETIJ = wt(15)       # 4.8
T_PERECH = wt(17)       # 5.52
T_PISMO = wt(19)        # 6.4
T_PERVOGO = wt(89)      # 31.92
osc, bump, punch, blink_at = S.osc, S.bump, S.punch, S.blink_at

HAND_KEYS = dict(kind="open", dir=(1, .22), curl=(.45, .5, .55, .6), spread=.05, thumb=.5)


def back_ease(u, k=1.9):
    u = clamp(u)
    return 1 + (k + 1) * (u - 1) ** 3 + k * (u - 1) ** 2


def typing_arms(t, rate=7.5, amp=7.0, rest=False):
    a = 0 if rest else amp
    n = (566 + 6 * osc(t, rate / 2) * (0 if rest else 1), 1094 - a * max(0, osc(t, rate)))
    f = (532 + 6 * osc(t, rate / 2, 2) * (0 if rest else 1), 1100 - a * max(0, osc(t, rate, 3.1)))
    return {"n": ("ik", n, -1), "f": ("ik", f, -1)}


def at_laptop(t, expr, content="", arms=None, hands=None, lean=.30, head_ang=0.0, bob=0.0, extra_front="", clock=(270.0, 0.0, 0.0, 0.0), tone="noon",
              hip=None, mug=True, on_desk_extra=""):
    arms = arms or typing_arms(t)
    hands = hands or {"n": HAND_KEYS, "f": HAND_KEYS}
    d = S.dima(t, arms, hands, expr, lean=lean, head_ang=head_ang, hip=hip)
    lap, to_world = day.laptop(content, bob=bob)
    w = [day.room_back_day(t, clock, tone)]
    w.append(S.room.chair(S.HIP[0] if hip is None else hip[0], (S.HIP[1] if hip is None else hip[1]) + 4, 1, 2300))
    w.append(den.desk_back())
    w.append(d.get("legs", ""))
    w.append(den.desk_top())
    w.append(den.lamp(t, on=0.0))
    w.append(day.mug_on_desk(t) if mug else "")
    w.append(on_desk_extra)
    w.append(d["arm_f"])
    w.append(lap)
    w.append(d["body"])
    w.append(d["arm_n"])
    w.append(extra_front)
    return "".join(w), d, to_world


# ═════════════════════════ счётчик-бейджи ═════════════════════════
def badge(x, y, k, n, u):
    """Плашка-галочка с «×n»: выпрыгивает с перелётом (u 0..1 — появление)."""
    if u <= 0:
        return ""
    sc = k * back_ease(u, 2.2)
    rot = 8 * (1 - ease_out(clamp(u), 2)) - 3
    body = shape([(-62, -40, 1), (62, -40, 1), (62, 40, 1), (-62, 40, 1)], "#fff8e6",
                 blob([(-62, 18), (62, 18), (62, 40), (-62, 40)], "#e8d9b0", .9), w=5, seed=6100 + n)
    body = shape(day_round(-62, -40, 62, 40, 16), "#fff8e6", blob(day_round(-62, 14, 62, 40, 14), "#e8d9b0", .9), w=5, seed=6100 + n)
    chk = (line([(-50, 2), (-36, 18), (-12, -16)], 17, lib.INK, taper=.05, wmin=.95, seed=6110 + n) +
           line([(-50, 2), (-36, 18), (-12, -16)], 10, "#3cbf63", taper=.05, wmin=.95, seed=6120 + n))
    txt = (f'<text x="3" y="16" text-anchor="start" font-family="IDB" font-weight="900" font-size="54" fill="{lib.INK}">×{n}</text>'
           f'<text x="0" y="13" text-anchor="start" font-family="IDB" font-weight="900" font-size="54" fill="#e2543f">×{n}</text>')
    txt = f'<g transform="translate(6 0)">{txt}</g>'
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sc:.3f})">{body}{chk}{txt}</g>'


def day_round(x0, y0, x1, y1, r):
    pts = []
    for (cx, cy, a0) in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for j in range(5):
            a = math.radians(a0 + 90 * j / 4)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def starburst(x, y, u, n=9, r0=70, r1=140, seed=6200, col="#3a2a22"):
    if u <= 0 or u >= 1:
        return ""
    o = []
    for j in range(n):
        a = 2 * math.pi * j / n + .3
        a0, a1 = r0 + (r1 - r0) * ease_out(u, 2), r0 + 30 + (r1 - r0) * ease_out(u, 2)
        o.append(line([(x + a0 * math.cos(a), y + a0 * math.sin(a)), (x + a1 * math.cos(a), y + a1 * math.sin(a))], 6, col, seed=seed + j, taper=.3, wmin=.4,
                      op=1 - u))
    return "".join(o)


# ═════════════════════════ s03: полдень, ноутбук, часы 12:00, счётчик ═════════════════════════
def s03(t):
    z = S.whip_in(t, 3.4, .22)
    k = ease_io(clamp((t - 3.4) / 2.3))
    s = (1.22 + .08 * k) * (1 + punch(t, T_TRETIJ, .05, .05, .35))
    cam = (555 + 420 * z + 15 * k, 880 + 12 * z - 10 * k, s, -2.2 * z + .7 * k - .5 + .9 * bump(t, T_TRETIJ, .3) * osc(t, 8))
    # часы: с кадра 0 крутятся 9:00 → 12:00, на «обеду» встают со щелчком
    if t < T_OBEDU:
        u = clamp((t - 3.3) / (T_OBEDU - 3.3))
        hrs = 9.0 + 3.0 * ease_in(u, 1.3)
        ha, ma = (hrs * 30.0) % 360, (hrs * 360.0) % 360
        jolt, tilt = 0.0, 1.2 * osc(t, 3)
    else:
        v = t - T_OBEDU
        ha = ma = 1.1 * math.exp(-9 * v) * math.sin(v * 40) * 20
        jolt, tilt = bump(t, T_OBEDU, .35), 5 * math.exp(-5 * v) * math.sin(v * 22)
    nod = clamp((t - T_UZHE) / 1.0)
    expr = dict(lid=.42 - .1 * smooth(T_UZHE, T_TRETIJ, t), look=(.7, .3 + .1 * osc(t, 2.4)), brows="worry", mouth="flat", closed=blink_at(t, 4.25, .14) +
                blink_at(t, 5.35, .14), hair=3 * bump(t, T_TRETIJ, .4) * osc(t, 9))
    hl = ((t - 3.4) * 2.4) % 9
    w, d, tw = at_laptop(t, expr, content=day.letter(hl=hl), head_ang=-.03 * nod, bob=0.0, clock=(ha, ma, jolt, tilt))
    hx, hy = d["head"]
    front = den.clock_click(clamp((t - T_OBEDU) / .3)) if t >= T_OBEDU else ""
    # счётчик: три плашки над головой, на «уже» / «третий»
    bx, by = hx + 150, hy - 215
    bd = ""
    for n, tt in ((1, T_UZHE - .06), (2, T_UZHE + .22), (3, T_TRETIJ + .02)):
        u = (t - tt) / .34
        bd += badge(bx + 200 * (n - 2), by - 70 * (n == 3) + 20 * (n % 2), 1.25 if n < 3 else 1.7, n, u)
    bd += starburst(bx + 200, by - 70, clamp((t - T_TRETIJ) / .35))
    return day.compose_day(w + front + bd, cam, "noon")


# ═════════════════════════ s04: крупно письмо; «перечитывает» — петля; «письмо» — лицо в ладонь ═════════════════════════
def loop_arrow(g, to_world, seed=6300):
    """Красная стрелка-петля вокруг текста письма (в координатах экрана): g 0..1 — сколько нарисовано."""
    if g <= 0:
        return ""
    pts = []
    cx, cy = 135, 160
    for j in range(0, 41):
        a = math.radians(-60 + j * 9.5)
        pts.append((cx + (118 - j * .35) * math.cos(a), cy + (86 - j * .1) * math.sin(a)))
    n = max(2, int(len(pts) * g))
    seg = [to_world(*p) for p in pts[:n]]
    o = line(seg, 12, lib.INK, taper=.05, wmin=.9, seed=seed) + line(seg, 6.5, "#e2543f", taper=.05, wmin=.9, seed=seed + 1)
    if g > .9 and n >= 3:
        (x1, y1), (x0, y0) = seg[-1], seg[-4]
        a = math.atan2(y1 - y0, x1 - x0)
        head = [(x1 + 24 * math.cos(a), y1 + 24 * math.sin(a), 1), (x1 + 20 * math.cos(a + 2.4), y1 + 20 * math.sin(a + 2.4), 1),
                (x1 + 20 * math.cos(a - 2.4), y1 + 20 * math.sin(a - 2.4), 1)]
        o += shape(head, "#e2543f", "", w=4, seed=seed + 2)
    return o


def s04(t):
    tn = T_PISMO
    k = ease_io(clamp((t - 5.3) / 2.2))
    s = (1.95 + .25 * k) * (1 + punch(t, T_PERECH, .05, .05, .35) + .03 * punch(t, tn, 1, .05, .3))
    cam = (500 + 8 * k, 1010 - 24 * k, s, .7 - 1.0 * k + .7 * bump(t, tn, .35) * osc(t, 9))
    # взгляд бегает по строкам, потом снова сверху (перечитывает); после «письмо» — лицо в ладонь
    fp = smooth(tn - .12, tn + .22, t)
    sweep = ((t - 5.3) * 2.6) % 1.0
    hl = sweep * 9
    look = (.45 + .5 * sweep, .1 + .55 * ((t - 5.3) * 2.6 * 1.0 % 1.0) * (1 - fp))
    look = (.3 + .6 * abs(math.sin((t - 5.3) * 9.0)), .0 + .6 * sweep)
    expr = dict(lid=.34 + .2 * fp, look=look if fp < .5 else (.1, .9), brows="worry" if fp < .6 else "tired", mouth="flat", closed=blink_at(t, 5.95, .14) + fp * .9,
                hair=6 * bump(t, tn, .4))
    lean = .30 + .18 * fp
    arms = typing_arms(t, rest=False)
    hands = {"n": HAND_KEYS, "f": HAND_KEYS}
    d0 = S.dima(t, arms, hands, expr, lean=lean, head_ang=.0)
    hx0, hy0 = d0["head"]
    if fp > 0:
        # ближняя рука поднимается к лицу: кисть ладонью на лоб/глаза
        tgt = (hx0 + 92 * S.BS / .6 * .62, hy0 + 78 * S.BS / .6 * .62)
        tgt = (hx0 + 62, hy0 + 66)
        cur = np.array(arms["n"][1])
        wr = tuple(cur + (np.array(tgt) - cur) * ease_io(fp))
        arms = {"n": ("ik", wr, -1), "f": arms["f"]}
        hands = {"n": dict(kind="open", dir=(.0, -1), curl=(.25, .28, .3, .35), spread=.1, thumb=.5), "f": HAND_KEYS}
    ha = -.1 * fp + .02 * math.sin(t * 5) * fp
    letterC = day.letter(hl=hl if fp < .2 else -1, dim=.35 * fp)
    w, d, tw = at_laptop(t, expr, content=letterC, arms=arms, hands=hands, lean=lean, head_ang=ha)
    g = clamp((t - T_PERECH) / .55)
    front = ""
    if t >= T_PERECH:
        front += loop_arrow(g, tw)
    hx, hy = d["head"]
    sw = clamp((t - tn - .08) / .7)
    front += S.sweat(hx + 150, hy - 20, 1.5, sw)
    if t > tn:
        u = clamp((t - tn) / .35)
        for j in range(3):
            a = math.radians(-120 + j * 28)
            r0 = 190 + 30 * u
            front += line([(hx + 40 + r0 * math.cos(a), hy - 40 + r0 * math.sin(a)), (hx + 40 + (r0 + 36) * math.cos(a), hy - 40 + (r0 + 36) * math.sin(a))],
                          6, "#3a2a22", seed=6340 + j, op=1 - u if u < 1 else 0, taper=.3, wmin=.4)
    return day.compose_day(w + front, cam, "noon")


# ═════════════════════════ s14: утро, письмо с первого раза, зелёная галочка ═════════════════════════
def big_check(x, y, k, u, seed=6400):
    """Зелёная галочка, нарисованная пером за u 0..1, с отскоком в конце."""
    if u <= 0:
        return ""
    pts = [(-70, 0), (-24, 52), (78, -62)]
    full = []
    for a, b in zip(pts, pts[1:]):
        for j in range(8):
            v = j / 8
            full.append((a[0] + (b[0] - a[0]) * v, a[1] + (b[1] - a[1]) * v))
    full.append(pts[-1])
    n = max(2, int(len(full) * clamp(u / .7)))
    seg = [(x + p[0] * k, y + p[1] * k) for p in full[:n]]
    pop = 1 + .14 * math.sin(math.pi * clamp((u - .7) / .3)) if u > .7 else 1.0
    glow = ""
    if u > .7:
        g = lib.rad_grad([(0, "#bff5c8", .55 * (1 - clamp((u - .7) / .3) * .5)), (1, "#bff5c8", 0)], x, y, 180 * k, 150 * k)
        glow = f'<rect x="{x - 200 * k:.1f}" y="{y - 180 * k:.1f}" width="{400 * k:.1f}" height="{360 * k:.1f}" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    return (glow + f'<g transform="translate({x:.1f} {y:.1f}) scale({pop:.3f}) translate({-x:.1f} {-y:.1f})">' +
            line(seg, 44 * k, lib.INK, taper=.04, wmin=.97, seed=seed) + line(seg, 30 * k, "#3cbf63", taper=.04, wmin=.97, seed=seed + 1) + "</g>")


def s14(t):
    tc = T_PERVOGO
    z = S.whip_in(t, 30.8, .22)
    k = ease_io(clamp((t - 30.8) / 2.4))
    s = (1.22 + .08 * k) * (1 + punch(t, tc, .05, .05, .35))
    cam = (555 - 420 * z + 15 * k, 880 + 12 * z - 10 * k, s, 2.2 * z + .7 * k - .5 + .9 * bump(t, tc, .3) * osc(t, 8))
    # читает один раз: подсветка идёт сверху вниз 31.0 → 31.9, глаза следом; на «первого» — улыбка и галочка
    u = clamp((t - 30.85) / 1.0)
    hl = u * 9 if t < tc + .05 else -1
    sm = smooth(tc - .06, tc + .18, t)
    look = (.35 + .55 * abs(math.sin((t - 30.8) * 6.0)), .0 + .6 * u) if sm < .5 else (.8, -.3)
    expr = dict(lid=.5 + .15 * sm, look=look, brows="worry" if sm < .3 else "up", mouth="flat" if sm < .3 else "smile", smile=.9 * sm,
                closed=blink_at(t, 31.55, .14), blush=1.0 * sm, hair=5 * bump(t, tc, .4) * osc(t, 9))
    rest = u > .98
    w, d, tw = at_laptop(t, expr, content=day.letter(hl=hl), arms=typing_arms(t, rate=3.0, amp=3.5, rest=False), lean=.28 - .04 * sm,
                         head_ang=-.04 * sm, tone="morning", clock=(270.0, 0.0, 0.0, 0.0) if False else (90.0, 0.0, 0.0, 0.0))
    hx, hy = d["head"]
    front = big_check(700, 700, 1.25, clamp((t - tc) / .5))
    front += starburst(700, 700, clamp((t - tc - .05) / .4), r0=130, r1=210, seed=6420, col="#2a7a44")
    return day.compose_day(w + front, cam, "morning")


SHOTS = {"s03": s03, "s04": s04, "s14": s14}


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    return SHOTS[sid](t)
