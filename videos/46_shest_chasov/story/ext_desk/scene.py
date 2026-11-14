"""Сцена desk рилса 32: планы s01, s02, s03, s04, s06, s13. frame(sid, t) -> SVG 1080×1920 (t — общее время ролика).

Мир — den.py (ночная комната: окно, часы, доска со стикерами, полка, стол с лампой); Дима — people.py (сидит слева
лицом вправо, таз (230, 1262)); кот — cat.py на столе у лампы. Крупные планы s03 (кружки) и s04 (лист с глазами) —
свои композиции (top.py). Удары — на словах по voice/words.json.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat_desk as Cat  # noqa: E402
import den  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import room  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wi(i):
    return WORDS[i]["start"]


T_CHAS = wi(2)            # 1.04
T_IDEEY = wi(5)           # 1.76
T_PUSTO = wi(9)           # 3.04
T_KOFE = wi(10)           # 3.72
T_ESCHE = wi(11)          # 4.48
T_SMOTRIT = wi(18)        # 6.72
T_NEGO = wi(20)           # 7.12
T_BESP = wi(28)           # 10.08
T_ZASTR = wi(60)          # 23.44

BS = 0.6
HIP = np.array([230.0, 1262.0])
CAT_P = (905.0, 1110.0, 0.4)


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
    """Удар камерой: +amp за up с, возврат за down с."""
    if t < t0:
        return 0.0
    if t < t0 + up:
        return amp * ease_out((t - t0) / up, 2)
    return amp * (1 - ease_io(clamp((t - t0 - up) / down)))


def whip_in(t, t0, dur=0.2):
    return 1 - ease_out(clamp((t - t0) / dur), 3)


def sweat(x, y, k, u):
    if u <= 0:
        return ""
    yy = y + 46 * k * ease_in(u)
    r = 15 * k * min(1, u * 3)
    drop = [(x, yy - r * 2.2), (x + r, yy - r * .1), (x + r * .8, yy + r * .7), (x, yy + r), (x - r * .8, yy + r * .7), (x - r, yy - r * .1)]
    return shape(drop, "#bfe6fa", blob([(x - r * .4, yy - r * .6), (x - r * .1, yy - r * .9), (x - r * .1, yy - r * .2)], "#ffffff"), w=3, seed=3001)


# ═════════════════════════ Дима за столом ═════════════════════════
def dima(t, arms, hands=None, expr=None, hip=None, lean=0.12, head_ang=0.0, feet=None):
    hip = HIP if hip is None else np.array(hip, float)
    if feet is None:
        feet = {"n": ((450, 1468), 0.0), "f": ((425, 1462), 0.0)}
    p = dict(hip=tuple(hip), scale=BS, lean=lean, feet=feet, arms=arms, hands=hands or {}, expr=expr or {}, head_ang=head_ang,
             hood=0.0, strings=(2 * osc(t, 1.3), 1.5 * osc(t, 1.1, 1)))
    return people.draw(p, "dima")


def room_back(t, clock=(0.0, 0.0, 0.0, 0.0)):
    h, m, jolt, tilt = clock
    return "".join([den.wall(t), den.window(t), den.board(t), den.shelf(t), den.clock(h, m, jolt, tilt), den.floor()])


def cat_on_desk(t, st, pos=None):
    x, y, k = pos or CAT_P
    return Cat.draw(x, y, k, st, t)


def compose(world, cam, front_screen="", on=1.0):
    cx, cy, s, r = cam
    set_ink(s)
    o = ['<rect width="1080" height="1920" fill="#2a3346"/>',
         f'<g transform="{lib.cam(cx, cy, s, r)}">{world}{den.lamp_cone(0, on)}{den.glow(on)}</g>', front_screen, vignette()]
    return lib.svg("".join(o))


def vignette():
    g = lib.rad_grad([(0, "#0a0c1e", 0), (.6, "#0a0c1e", 0), (1, "#0a0c1e", .45)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def desk_world(t, d, clock, *, chair_dx=0.0, on_desk="", mid="", front="", cat="", pencil_desk=True, extra_back=""):
    """d — выход people.draw. Слои: комната, стул, задние ножки, ноги, столешница, предметы, кот, рука дальняя, тело,
    mid (карандаш у рта и т.п.), рука ближняя, front."""
    w = [room_back(t, clock), extra_back]
    w.append(room.chair(HIP[0] + chair_dx, HIP[1] + 4, 1, 2300))
    w.append(den.desk_back())
    w.append(d.get("legs", ""))
    w.append(den.desk_top())
    w.append(den.sheet_side())
    if pencil_desk:
        w.append(den.pencil((520, 1134), (622, 1128), 10))
    w.append(on_desk)
    w.append(den.lamp(t))
    w.append(cat)
    w.append(d["arm_f"])
    w.append(d["body"])
    w.append(mid)
    w.append(d["arm_n"])
    w.append(front)
    return "".join(w)


def desk_mugs(t, steam=True):
    o = []
    for (x, y, k, col, kind) in [(752.0, 1100.0, .38, "#5f6fa8", "e"), (800.0, 1106.0, .4, "#c44f3a", "e"), (776.0, 1136.0, .44, "#e0a93a", "e"),
                                 (700.0, 1130.0, .46, "#3f7a72", "c")]:
        o.append(den.mug(x, y, k, col, fill="coffee" if kind == "c" else None, ring=kind == "e",
                         steam_t=t if (kind == "c" and steam) else None))
    return "".join(o)


def chewing(t, expr, head_ang=0.0, rate=4.2, amp=1.0, lean0=.14, far=(482, 1112), far_hand=None):
    """Дима грызёт карандаш: конец карандаша во рту, кулак держит его середину, жуёт (кулак и голова ходят)."""
    chew = osc(t, rate) * amp
    lean, hang = lean0 + .006 * chew, .03 * chew + head_ang
    probe = dima(t, {"n": ("ik", (380, 1080), -1), "f": ("ik", far, -1)}, {}, expr, lean=lean, head_ang=hang)
    mouth = probe["head"] + people.rot(np.array([84.0, 92.0]) * BS, lean * .5 + hang)
    u = np.array([math.cos(math.radians(30 + 4 * chew)), math.sin(math.radians(30 + 4 * chew))])
    a = mouth - u * 8
    fist = a + u * 62
    hd = np.array([-.3, -1.0]) / np.linalg.norm([-.3, -1.0])
    wr = fist - hd * 26
    arms = {"n": ("ik", tuple(wr), -1), "f": ("ik", far, -1)}
    hands = {"n": dict(kind="open", dir=tuple(hd), curl=(.85, .9, .92, .95), spread=.02, thumb=.85, bend=.05),
             "f": far_hand or dict(kind="open", dir=(1, .12), curl=(.2, .25, .3, .35), spread=.08, thumb=.4)}
    d = dima(t, arms, hands, expr, lean=lean, head_ang=hang)
    return d, den.pencil(tuple(a), tuple(a + u * 140), 10)


# ═════════════════════════ s01: хук — грызёт карандаш, часы крутятся, щелчок на 3:00 («час») ═════════════════════════
def clock_hands(t):
    """Стрелки: с кадра 0 бегут (минутная — 3 оборота), на «час» встают на 3:00 со щелчком и отскоком."""
    tc = T_CHAS
    if t < tc:
        u = clamp(t / tc)
        hrs = 3.0 * (u ** 1.15)
    else:
        v = t - tc
        hrs = 3.0 + .018 * math.exp(-9 * v) * math.sin(v * 40)
    return (hrs * 30.0) % 360, (hrs * 360.0) % 360


def s01(t):
    z, rot = hook_zoom(t, 0.0, .4, .22, -3.0)
    k = ease_io(clamp(t / 1.6))
    hit = punch(t, T_CHAS, .08, .06, .4)
    s = 1.3 * z * (1 + .03 * k) * (1 + hit)
    cam = (555 - 40 * (1 - z) + 20 * k, 860 + 60 * (1 - z) - 10 * k, s, rot + .3 * osc(t, .5) + 1.2 * bump(t, T_CHAS, .3) * osc(t, 9))
    ha, ma = clock_hands(t)
    jolt = bump(t, T_CHAS, .35)
    tilt = 5 * math.exp(-5 * max(0, t - T_CHAS)) * math.sin(max(0, t - T_CHAS) * 22) if t > T_CHAS else 1.2 * osc(t, 3)
    # грызёт карандаш: кулак у рта ходит вверх-вниз (жуёт), карандаш качается
    jump = bump(t, T_CHAS, .3)
    expr = dict(lid=.45 + .35 * jump, look=(.55, .55 - .5 * jump), brows="worry" if jump < .4 else "up", mouth="flat",
                closed=blink_at(t, .62, .14), hair=4 * jump * osc(t, 8))
    d, pen = chewing(t, expr, head_ang=-.04 * jump)
    cat = cat_on_desk(t, dict(look=(-.6, .2), turn=-.3, tail=4 * osc(t, .5), blink=blink_at(t, .9), ear=8 * bump(t, T_CHAS + .05, .25)))
    w = desk_world(t, d, (ha, ma, jolt, tilt), on_desk=desk_mugs(t), mid=pen, cat=cat, pencil_desk=False,
                   front=den.clock_click(clamp((t - T_CHAS) / .3)))
    return compose(w, cam)


# ═════════════════════════ s02: крупно голова, пустое облачко; «идеей» — тужится; «пусто» — перекати-поле ═════════════════════════
def cloud_pts(cx, cy, rx, ry, wob=0.0, t=0.0, n=9):
    pts = []
    for j in range(n * 6):
        th = 2 * math.pi * j / (n * 6)
        bump_ = abs(math.sin(n * th / 2 + .4)) ** .7
        r = 1 + .14 * bump_ + wob * .08 * math.sin(th * 3 + t * 9)
        pts.append((cx + rx * r * math.cos(th), cy + ry * r * math.sin(th)))
    return pts


def thought_cloud(cx, cy, k, sag, t, hx, hy):
    """Облачко мысли: k — размер (сдувается), sag — провис/морщины. Пузырьки от головы (hx, hy)."""
    o = []
    rx, ry = 80 * k, 60 * k * (1 - .35 * sag)
    cy2 = cy + 60 * sag
    for j, u in enumerate((.25, .5, .72)):
        bx, by = hx + (cx - hx) * u, hy + (cy2 + ry - hy) * u
        r = (9 + 9 * u) * (.6 + .4 * k)
        o.append(shape(ellipse_pts(bx, by, r, r * .9, 12), "#ffffff", blob(ellipse_pts(bx + r * .3, by + r * .3, r * .8, r * .7, 10), "#dfe4ee"), w=3.4,
                       seed=4100 + j))
    pts = cloud_pts(cx, cy2, rx, ry, sag, t)
    inner = blob(cloud_pts(cx + 18 * k, cy2 + 24 * k, rx * .95, ry * .9, sag, t), "#dfe4ee")
    inner += blob(cloud_pts(cx - 6 * k, cy2 - 4 * k, rx * .9, ry * .82, sag, t), "#ffffff")
    o.append(shape(pts, "#ffffff", inner, w=5, seed=4110))
    return "".join(o)


def tumbleweed(x, y, r, ang):
    """Перекати-поле: клубок сухих веток (без заливки-шара), торчащие прутики за контуром."""
    rs = np.random.RandomState(41)
    g = [blob(ellipse_pts(0, 0, r * .7, r * .7, 14), "#a87c42")]
    for j in range(16):
        a0 = rs.uniform(0, 2 * math.pi)
        rr = r * rs.uniform(.5, 1.05)
        cx, cy = rs.uniform(-.3, .3) * r, rs.uniform(-.3, .3) * r
        pts = [(cx + rr * math.cos(a0 + v), cy + rr * math.sin(a0 + v)) for v in np.linspace(0, rs.uniform(2.2, 4.2), 9)]
        g.append(line(pts, 6.4, lib.INK, seed=4200 + j, taper=.3, wmin=.4))
        g.append(line(pts, 3.2, "#d2a35e" if j % 2 else "#b5803f", seed=4200 + j, taper=.3, wmin=.4))
    for j in range(7):
        a = rs.uniform(0, 2 * math.pi)
        p0 = (r * .8 * math.cos(a), r * .8 * math.sin(a))
        p1 = (r * 1.35 * math.cos(a + .2), r * 1.35 * math.sin(a + .2))
        g.append(line([p0, p1], 3.6, lib.INK, seed=4240 + j, taper=.6, wmin=.2))
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f})">{"".join(g)}</g>'


def s02(t):
    tp, ti = T_PUSTO, T_IDEEY
    k = ease_io(clamp((t - 1.2) / 2.66))
    hit = punch(t, tp, .07, .07, .45)
    s = (3.05 + .3 * k) * (1 + hit)
    cam = (352 + 6 * k, 915 - 6 * k, s, -.6 + .9 * k + .8 * bump(t, tp, .3) * osc(t, 8))
    strain = smooth(ti - .1, ti + .15, t) * (1 - smooth(tp - .2, tp + .1, t))
    shake = strain * osc(t, 14)
    empty = smooth(tp + .05, tp + .4, t)
    expr = dict(lid=.42 - .3 * strain + .38 * empty, look=(.35 * (1 - empty) + .1 * empty, -.2 - .25 * empty), brows="det" if strain > .3 else
                ("worry" if empty < .5 else "up"), mouth="flat", blush=strain, closed=blink_at(t, 1.45, .14), hair=2 * shake)
    d, pen = chewing(t, expr, head_ang=.02 * shake - .06 * empty, rate=4.2 + 3 * strain, amp=1 - .6 * empty)
    hx, hy = d["head"]
    w = desk_world(t, d, (90.0, 0.0, 0.0, 0.0), on_desk=desk_mugs(t), mid=pen, cat="", pencil_desk=False)
    # облачко: дрожит от натуги; перекати-поле катится слева направо по облачку; облачко сдувается
    ck = 1.0 - .42 * smooth(tp + .35, tp + .8, t)
    sag = smooth(tp + .3, tp + .75, t)
    cx, cy = hx + 150 + 3 * shake, hy - 200
    front = thought_cloud(cx, cy, ck * (1 + .03 * osc(t, 1.3)), sag, t, hx + 70, hy - 90)
    u = clamp((t - (tp - .25)) / .9)
    if 0 < u < 1:
        x = cx - 150 + 300 * u
        y = cy + 14 - 22 * abs(math.sin(u * math.pi * 3))
        front += tumbleweed(x, y, 22, 620 * u)
        for j in range(3):
            v = clamp((u - j * .2) * 2)
            if 0 < v < 1:
                px, py = cx - 170 + 340 * (j * .2 + .1), cy + 44
                front += line([(px - 14 * v, py), (px - 30 * v, py - 10 * v)], 4, "#c9b48a", seed=4300 + j, op=1)
    if strain > .2:
        for j in range(3):
            a = math.radians(-150 + j * 40)
            r0 = 150 + 6 * osc(t, 10, j)
            front += line([(hx + 10 + r0 * math.cos(a), hy - 20 + r0 * math.sin(a)), (hx + 10 + (r0 + 30) * math.cos(a), hy - 20 + (r0 + 30) * math.sin(a))],
                          5, "#3a2a22", seed=4310 + j, taper=.3, wmin=.4)
    return compose(w + front, cam)


# ═════════════════════════ s03: рука ставит кружку с паром («Кофе»), вторую — со стуком («ещё») ═════════════════════════
def kw_hand():
    people.C = people.PAL["dima"]
    return dict(shape_fn=people.shape, line_fn=people.line, skin=people.C["SKIN"], skin_sh=people.C["SKIN_SH"], skin_sh2=people.C["SKIN_SH2"])


def grip_mug(mx, my, mk, side=-1):
    kw = kw_hand()
    old = people.LWK
    people.LWK = BS
    try:
        b, f = Hand.grip((mx, my - 64 * mk), 50 * mk, side, k=BS * 1.05, h=70, seed=2600, **kw)
    finally:
        people.LWK = old
    return b, f


M1 = (650.0, 1132.0, .5, "#3f7a72")
M2 = (572.0, 1142.0, .52, "#d8483c")


def mug_path(t, t_land, x, y, x0, y0, dur=.45):
    """Кружка летит из (x0, y0) к (x, y), садится на t_land (разгон к удару)."""
    u = clamp((t - (t_land - dur)) / dur)
    e = ease_in(u, 1.6)
    return x0 + (x - x0) * ease_out(u, 2), y0 + (y - y0) * e - 40 * math.sin(math.pi * u)


def s03(t):
    tk, te = T_KOFE, T_ESCHE
    k = ease_io(clamp((t - 3.46) / 2.3))
    sh = bump(t, te, .32)
    s = (3.3 + .25 * k) * (1 + punch(t, te, .05, .05, .35))
    cam = (640 + 10 * k + 7 * sh * osc(t, 13), 1048 - 8 * k + 5 * sh * osc(t, 17, 1), s, -.5 + .6 * k + 1.4 * sh * osc(t, 9))
    # кружка 1
    x1, y1, k1, c1 = M1
    if t < tk:
        mx1, my1 = mug_path(t, tk, x1, y1, x1 - 120, y1 - 140, .45)
    else:
        mx1, my1 = x1, y1
    jump1 = 16 * bump(t, te + .01, .22)
    sq1 = 1 - .06 * bump(t, tk, .14)
    # кружка 2: рука возвращается за ней влево и несёт со стуком
    x2, y2, k2, c2 = M2
    if t < te:
        mx2, my2 = mug_path(t, te, x2, y2, x2 - 150, y2 - 150, .42)
    else:
        mx2, my2 = x2, y2
    if t < tk + .12:
        hold, (gx, gy, gk) = 1, (mx1, my1, k1)
    elif t < te - .42:
        hold = 0
        u = ease_io(clamp((t - tk - .12) / (te - .42 - tk - .12)))
        gx, gy, gk = x1 + (x2 - 150 - x1) * u, y1 - 60 * math.sin(math.pi * u) + (y2 - 150 - y1) * u, k2
    elif t < te + .14:
        hold, (gx, gy, gk) = 2, (mx2, my2, k2)
    else:
        hold = 3
        u = ease_io(clamp((t - te - .14) / .5))
        gx, gy, gk = x2 - 90 * u, y2 - 40 * u, k2
    wr = (gx - 50 * gk - 62 * BS + 8, gy - 64 * gk + 4)
    expr = dict(lid=.4, look=(.6, .5), brows="worry", mouth="flat")
    hand_open = dict(kind="open", dir=(1, .1), curl=(.35, .4, .45, .5), spread=.05, thumb=.5)
    d = dima(t, {"n": ("ik", wr, -1), "f": ("ik", (440, 1108), -1)},
             {"n": dict(kind="none") if hold in (1, 2) else hand_open, "f": dict(kind="open", dir=(1, .12), curl=(.2, .25, .3, .35), spread=.08, thumb=.4)},
             expr, lean=.3)
    on_desk = desk_mugs(t, steam=False).replace("", "") if False else ""
    for (x, y, kk, col) in [(752.0, 1100.0, .38, "#5f6fa8"), (800.0, 1106.0, .4, "#c44f3a"), (776.0, 1136.0, .44, "#e0a93a"), (720.0, 1104.0, .36, "#8a5a8a")]:
        on_desk += den.mug(x, y - 10 * bump(t, te + .02, .2), kk, col, ring=True)
    pen_j = 22 * bump(t, te, .26)
    on_desk_front = den.pencil((520, 1134 - pen_j), (622, 1128 - pen_j * 1.3), 10)
    m1 = f'<g transform="translate({mx1:.1f} {my1 - jump1:.1f}) scale(1 {sq1:.3f}) translate({-mx1:.1f} {-my1:.1f})">' + \
        den.mug(mx1, my1, k1, c1, fill="coffee", steam_t=t if t > tk - .1 else None) + "</g>"
    m2 = den.mug(mx2, my2, k2, c2, fill="coffee", steam_t=t if t > te else None) if t > tk + .15 else ""
    front = ""
    if hold == 1:
        gb, gf = grip_mug(mx1, my1, k1)
        front = gb + m1 + gf
        m1 = ""
    elif hold == 2:
        gb, gf = grip_mug(mx2, my2, k2)
        front = gb + m2 + gf
        m2 = ""
    # удар второй кружки: штрихи и капли
    hitk = clamp((t - te) / .3)
    if 0 < hitk < 1:
        for j, sx in enumerate((-1,)):
            for q in range(3):
                r0 = 40 + 30 * hitk + q * 14
                front += line([(x2 + sx * (r0 + 20), y2 - 10 - q * 22), (x2 + sx * (r0 + 44), y2 - 20 - q * 30)], 5, "#3a2a22", seed=4400 + j * 3 + q, op=1,
                              taper=.3, wmin=.4)
        for j in range(4):
            a = math.radians(-60 - j * 22)
            dx, dy = 80 * hitk * math.cos(a), 110 * hitk * math.sin(a) + 160 * hitk * hitk
            front += shape(ellipse_pts(x2 + dx, y2 - 128 * k2 - 8 + dy, 4.5, 5.5, 8), "#6a3a22", "", w=2, seed=4420 + j)
    w = desk_world(t, d, (90.0, 0.0, 0.0, 0.0), on_desk=on_desk + m1 + m2, front=front, pencil_desk=False, mid="")
    w = w.replace(den.lamp(t), den.lamp(t) + on_desk_front, 1)
    return compose(w, cam)


# ═════════════════════════ s04: крупно пустой лист; «смотрит» — у листа открываются глаза; «него» — Дима отшатывается ═════════════════════════
def wood_top():
    lib.DEFS.append('<pattern id="pWood32" width="420" height="150" patternUnits="userSpaceOnUse">'
                    '<rect width="420" height="150" fill="#a8693f"/>'
                    '<path d="M0 34 C120 26 260 44 420 32 M0 84 C140 92 280 72 420 88 M0 124 C110 116 300 132 420 120" fill="none" '
                    'stroke="#8f5733" stroke-width="3"/><rect y="148" width="420" height="2" fill="#6e4224"/></pattern>')
    return '<rect x="-800" y="-800" width="2700" height="3600" fill="url(#pWood32)"/>'


SH4 = [(330, 470), (900, 490), (980, 1210), (240, 1190)]


def paper_eye(cx, cy, rx, ry, o, look, sd):
    """Нарисованный тушью глаз на бумаге: o 0 — закрыт (дуга с ресницами), 1 — открыт."""
    s = []
    if o < .06:
        arc = [(cx - rx, cy), (cx - rx * .4, cy + ry * .45), (cx + rx * .4, cy + ry * .45), (cx + rx, cy)]
        s.append(line(arc, 7, lib.INK, seed=sd, taper=.4, wmin=.4))
        for j in range(3):
            x = cx - rx * .5 + j * rx * .5
            s.append(line([(x, cy + ry * .4), (x + (j - 1) * 6, cy + ry * .75)], 4, lib.INK, seed=sd + 10 + j, taper=.6, wmin=.2))
        return "".join(s)
    up = ry * o
    pts = [(cx - rx, cy, 1)]
    for v in np.linspace(-1, 1, 9)[1:-1]:
        pts.append((cx + rx * v, cy - up * (1 - v * v) ** .6 * 1.05))
    pts.append((cx + rx, cy, 1))
    for v in np.linspace(1, -1, 9)[1:-1]:
        pts.append((cx + rx * v, cy + up * (1 - v * v) ** .7 * .85))
    px, py = cx + rx * .45 * look[0], cy + up * .35 * look[1]
    pr = min(ry * .48, up * .85)
    cid = lib.clip_of(pts)
    inner = (f'<g clip-path="url(#{cid})"><circle cx="{px:.1f}" cy="{py:.1f}" r="{pr:.1f}" fill="{lib.INK}"/>'
             f'<circle cx="{px - pr * .35:.1f}" cy="{py - pr * .35:.1f}" r="{pr * .28:.1f}" fill="#ffffff"/></g>')
    s.append(f'<path d="{lib.fill_d(pts)}" fill="#ffffff"/>' + inner)
    s.append(f'<path d="{lib.ink_closed(pts, 6.5 * lib.INK_K[0], seed=sd)}" fill="{lib.INK}"/>')
    for j in range(3):
        x = cx - rx * .5 + j * rx * .5
        y = cy - up * (1.0 if j == 1 else .93)
        s.append(line([(x, y), (x + (j - 1) * 10, y - 22 * o)], 4.4, lib.INK, seed=sd + 10 + j, taper=.6, wmin=.2))
    return "".join(s)


def mug_top(x, y, r, col, coffee=True, t=None):
    s = [blob(ellipse_pts(x + 14, y + 18, r + 6, r + 6, 20), "#1a0c04", .35, lib.blur(8))]
    hd = [(x + r * .8, y - r * .5), (x + r * 1.5, y - r * .6), (x + r * 1.6, y + r * .1), (x + r * .85, y + r * .25)]
    s.append(line(hd, 22, lib.INK, taper=.05, wmin=.9, seed=4501))
    s.append(line(hd, 12, col, taper=.05, wmin=.9, seed=4502))
    s.append(shape(ellipse_pts(x, y, r, r, 22), col, blob(ellipse_pts(x + r * .2, y + r * .2, r * .85, r * .85, 18), lib.mix(col, "#000000", .2)), w=5,
                   seed=4503))
    s.append(shape(ellipse_pts(x, y, r * .76, r * .76, 20), "#5a3220" if coffee else "#3a2420",
                   blob(ellipse_pts(x - r * .2, y - r * .2, r * .3, r * .22, 12), "#8a5636", .9) if coffee else "", w=3.6, seed=4504))
    return "".join(s)


def s04(t):
    ts, tn = T_SMOTRIT, T_NEGO
    k = ease_io(clamp((t - 5.36) / 2.74))
    s = (1.0 + .14 * k) * (1 + punch(t, ts, .07, .06, .4))
    cam = (610 - 20 * k, 860 - 10 * k, s, .8 - 1.2 * k + .8 * bump(t, ts, .3) * osc(t, 8))
    set_ink(s)
    w = [wood_top()]
    # кружки сверху, карандаш
    w.append(mug_top(930, 300, 92, "#3f7a72", t=t))
    w.append(mug_top(1060, 560, 80, "#c44f3a", coffee=False))
    w.append(mug_top(880, 1360, 86, "#e0a93a", coffee=False))
    w.append(den.steam(930, 270, 1.4, t))
    w.append(blob([(p[0] + 18, p[1] + 26) for p in SH4], "#1a0c04", .35, lib.blur(10)))
    # лист: дышит уголком на «смотрит»
    lift = 14 * bump(t, ts, .5)
    pts = [(SH4[0][0], SH4[0][1], 1), (SH4[1][0], SH4[1][1] - lift, 1), (SH4[2][0], SH4[2][1], 1), (SH4[3][0], SH4[3][1], 1)]
    w.append(shape(pts, "#fbf8f0", blob([(SH4[2][0] - 40, SH4[2][1]), SH4[2], (SH4[1][0], SH4[1][1] - lift), (SH4[1][0] - 20, SH4[1][1] + 40)],
                                       "#ece6d8", .8), w=5, seed=4510))
    # глаза листа
    o = -1.0
    if t >= ts:
        v = t - ts
        o = clamp(v / .12) * (1 + .18 * math.exp(-6 * v) * math.sin(v * 22))
        bl = 7.62
        if bl - .08 < t < bl + .1:
            o *= abs(t - bl) / .1 if t < bl else (t - bl) / .1
            o = max(o, 0)
    look = (0.0, 0.0)
    if t > tn - .05:
        g = smooth(tn - .05, tn + .1, t)
        look = (-.75 * g, -.35 * g)
    if o > -1:
        for (cx, sd) in ((500, 4520), (760, 4530)):
            w.append(paper_eye(cx, 800, 112, 84, max(o, 0), look, sd))
    # Дима у левого края: смотрит на лист; на «него» отшатывается
    rec = ease_out(clamp((t - tn) / .22), 3) - .15 * bump(t, tn + .25, .4)
    hx = 150 - 110 * rec
    hy = 1020 + 30 * rec
    ang = -6 - 14 * rec + 1.5 * osc(t, .7)
    people.C = people.PAL["dima"]
    expr = dict(lid=.4 + .55 * smooth(tn - .05, tn + .1, t), look=(.75 - .3 * rec, .4 - .3 * rec), brows="worry" if t < tn else "up",
                mouth="flat" if t < tn else "talk", open=.55 * smooth(tn, tn + .1, t), closed=blink_at(t, 5.9, .14), hair=10 * bump(t, tn, .4))
    head = people.dima_head(expr)
    # шея и плечо худи под головой (уходят за левый нижний край)
    sx, sy = hx - 20, hy + 150
    body = [(sx - 330, sy + 40), (sx - 120, sy - 30), (sx + 60, sy - 10), (sx + 160, sy + 70), (sx + 225, sy + 230), (sx + 300, sy + 900, 1),
            (sx - 400, sy + 900, 1)]
    hood = [(hx - 250, hy + 20), (hx - 200, hy - 120), (hx - 90, hy - 160), (hx - 20, hy + 60), (hx - 60, sy + 40), (hx - 260, sy + 60)]
    w.append(shape(hood, "#a97b25", line([(hx - 200, hy - 40), (hx - 130, hy + 60)], 3, "#6b4a12", seed=4564, op=.8), w=5, seed=4563))
    neck = [(hx - 70, hy + 40), (hx + 80, hy + 60), (hx + 70, sy + 30), (hx - 90, sy + 20)]
    w.append(shape(neck, people.C["SKIN_SH"], "", w=4, seed=4560))
    w.append(shape(body, "#d4a23e", blob([(sx - 400, sy + 200), (sx + 200, sy + 160), (sx + 200, sy + 420), (sx - 400, sy + 420)], "#a97b25", .9) +
                   line([(sx - 60, sy + 10), (sx + 20, sy + 120), (sx + 30, sy + 260)], 3, "#6b4a12", seed=4562, op=.8), w=5, seed=4561))
    w.append(f'<g transform="translate({hx:.1f} {hy:.1f}) rotate({ang:.2f}) scale(1.9)">{head}</g>')
    sw = clamp((t - tn - .05) / .7)
    if sw > 0:
        w.append(sweat(hx + 200, hy - 200, 2.0, sw))
    if t > tn:
        u = clamp((t - tn) / .35)
        for j in range(3):
            a = math.radians(-30 + j * 30)
            r0 = 280 + 30 * u
            w.append(line([(hx + 40 + r0 * math.cos(a), hy - 40 + r0 * math.sin(a)), (hx + 40 + (r0 + 40) * math.cos(a), hy - 40 + (r0 + 40) * math.sin(a))],
                          6, "#3a2a22", seed=4540 + j, op=1 - u * .99 if u < 1 else 0, taper=.3, wmin=.4))
    g = lib.rad_grad([(0, "#fff0c0", .45), (.55, "#ffd890", .15), (1, "#ffd890", 0)], 640, 760, 760, 760)
    g2 = lib.rad_grad([(0, "#000000", 0), (.5, "#000000", 0), (1, "#0a0c1e", .6)], 600, 820, 1000, 1100)
    w.append(f'<rect x="-800" y="-800" width="2700" height="3600" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    w.append(f'<rect x="-800" y="-800" width="2700" height="3600" fill="url(#{g2})"/>')
    o_ = ['<rect width="1080" height="1920" fill="#5a3a22"/>', f'<g transform="{lib.cam(*cam)}">{"".join(w)}</g>', vignette()]
    return lib.svg("".join(o_))


# ═════════════════════════ s06: Дима застыл (подпёр голову), растёт паутина; «бесполезно» — паучок на нитке перед носом ═════════════════════════
def cobweb(cx, cy, anchors, g, seed=4600):
    """Паутина: центр (cx, cy), anchors — точки крепления; g 0..1 — рост (сначала лучи, потом спираль)."""
    o = []
    col = "#e9eef6"
    gr = clamp(g / .45)
    for j, a in enumerate(anchors):
        e = (cx + (a[0] - cx) * gr, cy + (a[1] - cy) * gr)
        o.append(line([(cx, cy), e], 2.6, col, seed=seed + j, taper=.05, wmin=.9, op=.85))
    gs = clamp((g - .3) / .7)
    n = len(anchors)
    rings = int(7 * gs + .999)
    for r in range(rings):
        f_ = (r + 1) / 8.0
        kk = clamp(7 * gs - r)
        pts = []
        m = max(2, int(round(n * kk)) + 1)
        for j in range(m):
            a = anchors[j % n]
            pts.append((cx + (a[0] - cx) * f_ * (1 - .06 * (j % 2)), cy + (a[1] - cy) * f_ * (1 - .06 * (j % 2)) + 3))
        o.append(line(pts, 2.0, col, seed=seed + 30 + r, taper=.05, wmin=.9, op=.8))
    return "".join(o)


def spider(x, y, t, sway=0.0):
    o = []
    for side in (-1, 1):
        for j in range(4):
            a = math.radians(-50 + j * 30) + .15 * math.sin(t * 9 + j)
            k1 = (x + side * 14 * math.cos(a), y + 14 * math.sin(a) - 4)
            k2 = (x + side * 28 * math.cos(a - .2), y - 10 + 18 * math.sin(a) - 6)
            k3 = (x + side * 38 * math.cos(a), y + 20 + 14 * j * .3)
            o.append(line([(x, y), k1, k2, k3], 4.2, "#1c1622", seed=4700 + j + (side > 0) * 10, taper=.4, wmin=.4))
    o.append(shape(ellipse_pts(x, y + 6, 18, 20, 14), "#2a2230", blob(ellipse_pts(x + 5, y + 10, 12, 14, 10), "#15111a"), w=3, seed=4720))
    o.append(shape(ellipse_pts(x, y - 14, 11, 10, 12), "#2a2230", "", w=2.6, seed=4721))
    for sx in (-1, 1):
        o.append(f'<circle cx="{x + sx * 5:.1f}" cy="{y - 15:.1f}" r="4.6" fill="#ffffff"/><circle cx="{x + sx * 5 - 1:.1f}" cy="{y - 13.5:.1f}" r="2.2" fill="#15111a"/>')
    return f'<g transform="rotate({sway:.2f} {x:.1f} {y - 14:.1f})">{"".join(o)}</g>'


def s06(t):
    tb = T_BESP
    k = ease_io(clamp((t - 9.1) / 2.06))
    s = (2.05 - .35 * k) * (1 + punch(t, tb, .04, .06, .4))
    cam = (342 + 20 * k, 985 - 25 * k, s, .5 - .7 * k)
    expr = dict(lid=.3, look=(.62, .12), brows="tired", mouth="flat", closed=0.0)
    surprise = smooth(tb + .05, tb + .2, t)
    expr["lid"] = .3 + .45 * surprise
    expr["look"] = (.62 + .1 * surprise, .12 + .25 * surprise)
    arms = {"n": ("ik", (326, 1052), -1), "f": ("ik", (470, 1110), -1)}
    hands = {"n": dict(kind="open", dir=(-.2, -1), curl=(.8, .85, .9, .92), spread=.02, thumb=.75),
             "f": dict(kind="open", dir=(1, .1), curl=(.2, .25, .3, .35), spread=.08, thumb=.4)}
    d = dima(t, arms, hands, expr, lean=.2, head_ang=.12)
    hx, hy = d["head"]
    g = clamp((t - 9.1) / 1.7)
    web = cobweb(158, 930, [(112, 872), (112, 930), (112, 1000), (150, 1010), (205, 990), (226, 930), (214, 870), (160, 856)], g)
    # паучок: спускается с верха кадра, на «бесполезно» — перед носом с пружиной
    u = clamp((t - (tb - .55)) / .55)
    ny = hy + 30
    y = (ny - 520) + 520 * ease_in(u, 1.6) if t < tb else ny + 26 * math.exp(-5 * (t - tb)) * math.sin((t - tb) * 16)
    x = hx + 128
    thread = line([(x, ny - 900), (x, y - 22)], 2.2, "#e9eef6", seed=4730, taper=.02, wmin=.95)
    sp = spider(x, y, t, sway=12 * math.sin(t * 3.1)) if t > tb - .6 else ""
    # пылинки в свете
    motes = ""
    rs = np.random.RandomState(9)
    for j in range(12):
        mx = rs.uniform(200, 560) + 12 * math.sin(t * .8 + j)
        my = rs.uniform(820, 1100) - 10 * t % 40
        motes += blob(ellipse_pts(mx, my, 2.4, 2.4, 6), "#fff0c8")
    w = desk_world(t, d, (90.0, 0.0, 0.0, 0.0), on_desk=desk_mugs(t), cat="", front=web + thread + sp + motes)
    return compose(w, cam)


# ═════════════════════════ s13: снова ночь; «застревает» — решительно встаёт, стул отъезжает, берёт кепку; кот спрыгивает ═════════════════════════
def cap(x, y, ang=0.0, k=1.0):
    """Кепка сбоку: (x, y) — низ-центр тульи."""
    P = lambda pts: lib.T(pts, x, y, k, ang)  # noqa: E731
    o = [shape(P([(-60, 0), (-56, -40), (-30, -66), (10, -70), (44, -54), (60, -18), (62, 0)]), "#c44f3a",
               blob(P([(14, -70), (44, -54), (60, -18), (62, 0), (24, 0)]), "#9c3a2a", .9) + line(P([(0, -70), (-4, 0)]), 2.4, "#7a2a1e", seed=4810, op=.8),
               w=4, seed=4800)]
    o.append(shape(P([(30, -4), (112, 0), (120, 10), (40, 12)]), "#9c3a2a", "", w=3.6, seed=4801))
    o.append(shape(P(ellipse_pts(-2, -70, 8, 5, 8)), "#9c3a2a", "", w=2.4, seed=4802))
    return "".join(o)


def s13(t):
    tz = T_ZASTR
    k = ease_io(clamp((t - 21.76) / 2.34))
    wh = whip_in(t, 21.82, .22)
    s = (1.5 - .3 * k) * (1 + punch(t, tz, .06, .06, .4))
    cam = (520 + 80 * k + 420 * wh, 965 - 25 * k, s, -2.5 * wh + .6 * bump(t, tz, .3) * osc(t, 8))
    up = ease_out(clamp((t - tz) / .36), 2.4)
    over = .05 * bump(t, tz + .3, .3)
    hip = (230 + 50 * up, 1262 - 158 * up - 8 * over)
    fx = 450 - 160 * ease_io(clamp((t - tz - .05) / .3))
    feet = {"n": ((fx + 4, 1468), 0.0), "f": ((fx - 22, 1462), 0.0)}
    det = smooth(tz - .08, tz + .08, t)
    expr = dict(lid=.4 + .45 * det, look=(.55 - .1 * det, .55 - .7 * det), brows="tired" if det < .5 else "det",
                mouth="flat" if det < .5 else "smile", smile=.5, closed=blink_at(t, 22.6, .14), hair=8 * bump(t, tz, .45))
    grab = smooth(tz + .3, tz + .5, t)
    lift = ease_io(clamp((t - tz - .5) / .3))
    cap_pos = np.array([470.0, 1094.0])
    if t < tz - .12:
        d, pen = chewing(t, expr, rate=2.6, amp=.8, far=(470, 1110))
        mid, on = pen, ""
    else:
        slap = clamp((t - tz + .12) / .12)
        nw = np.array([420.0, 1092.0]) * (1 - grab) + (cap_pos + np.array([-30, -62])) * grab
        cap_hold = cap_pos + np.array([-40 * lift, -150 * lift])
        if lift > 0:
            nw = cap_hold + np.array([-30, -62])
        arms = {"n": ("ik", tuple(nw), -1), "f": ("ik", (446, 1094 - 6 * (1 - slap)), -1)}
        hands = {"n": dict(kind="open", dir=(1, .35 + .2 * grab), curl=(.15 + .45 * grab,) * 4, spread=.06, thumb=.4 + .4 * grab),
                 "f": dict(kind="open", dir=(1, .2), curl=(.15, .2, .25, .3), spread=.1, thumb=.3)}
        d = dima(t, arms, hands, expr, hip=hip, lean=.14 - .1 * up, head_ang=-.05 * det, feet=feet)
        mid = ""
        on = den.pencil((520, 1134), (622, 1128), 10)
    cp = cap_pos if t < tz + .5 else cap_pos + np.array([-40 * lift, -150 * lift])
    cap_svg = cap(cp[0], cp[1], -8 * lift, .85)
    # кот: смотрит на Диму, на «застревает» прыгает со стола вправо-вниз
    tj = tz + .08
    if t < tj:
        cat = cat_on_desk(t, dict(look=(-.6, .2), turn=-.3, tail=4 * osc(t, .5), blink=blink_at(t, 22.9), perk=.6 * smooth(tz - .2, tz, t)))
    else:
        v = clamp((t - tj) / .4)
        cx = CAT_P[0] + 95 * v
        cy = CAT_P[1] - 110 * math.sin(math.pi * v) + 370 * v * v
        rot_ = 24 * math.sin(math.pi * v)
        land = bump(t, tj + .4, .25)
        cat = (f'<g transform="rotate({rot_:.1f} {cx:.1f} {cy - 60:.1f}) translate({cx:.1f} {cy:.1f}) scale({1 + .08 * land:.3f} {1 - .1 * land:.3f}) '
               f'translate({-cx:.1f} {-cy:.1f})">' + Cat.draw(cx, cy, CAT_P[2] * 1.15, dict(look=(-.5, -.2), turn=-.3, tail=-15 * math.sin(math.pi * v), perk=1),
                                                             t) + "</g>")
    chair_dx = -130 * ease_out(clamp((t - tz - .05) / .35), 2)
    w = desk_world(t, d, (90.0, 0.0, 0.0, 0.0), chair_dx=chair_dx, on_desk=desk_mugs(t) + on + ("" if grab > .5 else cap_svg), mid=mid + (cap_svg if grab > .5 else ""), cat=cat, pencil_desk=False)
    if lift > 0:      # кепка в руке поверх кисти не рисуется дважды: она уже в on_desk, кисть ложится на неё
        pass
    return compose(w, cam)


SHOTS = {"s01": s01, "s02": s02, "s03": s03, "s04": s04, "s06": s06, "s13": s13}


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    return SHOTS[sid](t)
