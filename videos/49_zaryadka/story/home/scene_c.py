"""Рилс 49 «зарядка», группа C: s08 (мама с трубкой), s09 (Дима с книгой), s11 (верёвочка), s14 (диван, воскресенье), s15 (кот крупно).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Основа — кухня 29 (lib/ink/people/hand/cat/world.py), удары — по voice/words.json."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat as Cat  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import world as Wd  # noqa: E402
import scene_ref29 as R  # noqa: E402
from ink import band  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, rect_pts, shape, smooth, back_out, mix  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after and w["word"].strip(".,!?").lower() == word:
            return w["start"]
    raise KeyError(word)


T_UDIV = wt("удивилась")
T_VESNY = wt("весны")
T_VEREV = wt("верёвочкой")
T_VOSKR = wt("воскресенье")
T_KOT = wt("кот", 24.0)
T_CHAS = wt("час", 27.0)

osc, bump, blink_at, whip_in = R.osc, R.bump, R.blink_at, R.whip_in
FONT = "IDB"


def text(x, y, s, size, fill="#fff6e0", stroke=INK, sw=8, rot=0.0, op=1.0, anchor="middle"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" font-weight="900" font-size="{size:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" paint-order="stroke" opacity="{op:.3f}" '
            f'transform="rotate({rot:.2f} {x:.1f} {y:.1f})">{s}</text>')


def compose(world, cam, front="", screen="", vig="#2a1408", va=.35, blur_x=0.0):
    cx, cy, s, r = cam
    R.set_ink(s)
    f = ""
    if blur_x > 0.5:
        f = f' filter="url(#{_mb(blur_x)})"'
    g = lib.rad_grad([(0, vig, 0), (.62, vig, 0), (1, vig, va)], 540, 900, 1180, 1400)
    o = [f'<rect width="1080" height="1920" fill="#e7cfa3"/>',
         f'<g{f}><g transform="{lib.cam(cx, cy, s, r)}">{world}{front}</g></g>', screen,
         f'<rect width="1080" height="1920" fill="url(#{g})"/>']
    return lib.svg("".join(o))


def _mb(sd):
    i = f"mb{int(sd)}"
    if not any(f'id="{i}"' in x for x in lib.DEFS):
        lib.DEFS.append(f'<filter id="{i}" x="-10%" y="-5%" width="120%" height="110%"><feGaussianBlur stdDeviation="{sd:.1f} 0"/></filter>')
    return i


# ═════════════════════════ мама ═════════════════════════
people.PAL["mama"] = dict(people.PAL["friend"], SKIN="#f1cdb0", SKIN_SH="#d9a98c", SKIN_SH2="#c58f78", HAIR="#a39aa0", HAIR_SH="#766d77",
                          HAIR_HI="#cfc7cb", TOP="#8e5a86", TOP_SH="#6e4268", TOP_SH2="#55324f", FOLD="#3f2339", STITCH="#e8c88a",
                          TEE="#f6efe2", TEE_SH="#ddd2c0")


def mama_head(expr):
    C = people.C
    shape_, line_, blob_ = people.shape, people.line, people.blob
    hb = expr.get("hair", 0.0)
    s = []
    bun = ellipse_pts(-84, -170, 58, 50, 16)
    s.append(shape_(bun, C["HAIR"], blob_(ellipse_pts(-62, -150, 34, 30, 12), C["HAIR_SH"], .8) +
                    line_([(-120, -180), (-84, -196), (-50, -180)], 3, C["HAIR_HI"], seed=451, op=.9), w=5, seed=450))
    ear = [(-84, -18), (-108, -30), (-128, -8), (-126, 26), (-112, 50), (-92, 54), (-82, 44)]
    s.append(shape_(ear, C["SKIN"], blob_([(-128, -8), (-126, 26), (-112, 50), (-112, 14)], C["SKIN_SH"], .9), w=4.8, seed=452))
    inner = []
    inner.append(blob_([(-110, -130), (-36, -130), (-58, -40), (-54, 40), (-20, 130), (-110, 130)], C["SKIN_SH"], .95))
    inner.append(blob_(ellipse_pts(54, -10, 100, 62, 14), "#e3a595", .3))
    blush = expr.get("blush", .5)
    inner.append(blob_(ellipse_pts(96, 40, 24, 13, 10), "#e98a86", .5 * blush))
    inner.append(blob_(ellipse_pts(0, 44, 30, 14, 10), "#e98a86", .45 * blush))
    s.append(shape_(people.FACE, C["SKIN"], "".join(inner), w=5.6, seed=453))
    s.append(people.eyes(expr, people.EYE_N, people.EYE_F, bags=False))
    # морщинки у глаз и носогубные складки
    s.append(line_([(-26, 18), (-20, 26)], 2, C["SKIN_SH2"], seed=454, op=.7) + line_([(120, 8), (128, 16)], 2, C["SKIN_SH2"], seed=455, op=.0))
    B = people.BROWS[expr.get("brows", "calm")]
    s.append(line_(B[0], 6.4, C["HAIR_SH"], seed=456, peak=.4) + line_(B[1], 5.6, C["HAIR_SH"], seed=457, peak=.55))
    s.append(blob_([(50, 30), (62, 58), (54, 66), (44, 56)], C["SKIN_SH"], .9))
    s.append(line_([(58, 22), (76, 50), (72, 63), (58, 65)], 4.6, seed=458, peak=.45))
    s.append(line_([(50, 58), (56, 63)], 2.4, seed=459, op=.8))
    s.append(blob_(ellipse_pts(64, 69, 8, 3, 8), C["SKIN_SH2"], .7))
    m = expr.get("mouth", "smile")
    if m == "talk":
        s.append(people.talk_mouth(64, 90, expr.get("open", .3), wide=.9, smile=expr.get("smile", .3), seed=460))
    else:
        s.append(people.dima_mouth(dict(expr, mouth=m)))
    # помада на губах
    s.append(line_([(40, 90), (64, 86), (88, 90)], 3, "#c24a5a", seed=461, op=.0))
    hair = [(104, -44), (106, -88), (84, -126), (40, -156), (-10, -166), (-66, -156), (-112, -124), (-138, -70), (-146, -10), (-142, 50), (-124, 96),
            (-96, 100), (-96, 60), (-92, 10), (-84, -30), (-58, -62), (-20, -84), (30, -90), (70, -80)]
    hair = [(x, y - (hb * 4 if y < -100 else 0), *r) for (x, y, *r) in hair]
    hin = blob_([(-160, -190), (-20, -190), (-30, -130), (-70, -100), (-80, -40), (-160, -20)], C["HAIR_SH"], .95)
    hin += blob_([(10, -150), (60, -124), (100, -80), (70, -116), (40, -132)], C["HAIR_HI"], .9)
    for i, st in enumerate([[(-10, -156), (-34, -122), (-62, -96)], [(36, -146), (14, -112), (-16, -92)], [(74, -124), (58, -102), (36, -90)],
                            [(-80, -140), (-104, -116), (-120, -84)], [(-50, -108), (-80, -80), (-92, -54)], [(-110, -50), (-126, -10), (-124, 40)]]):
        hin += line_(st, 3.0, C["HAIR_SH"], seed=470 + i, op=.85)
    s.append(shape_(hair, C["HAIR"], hin, w=5.4, seed=471))
    return "".join(s)


def mama(t, hip, lean=0.0, arms=None, hands=None, expr=None, head_ang=0.0, scale=R.BS, hood=0):
    p = dict(hip=tuple(hip), scale=scale, lean=lean, feet=None, arms=arms, hands=hands or {}, expr=expr or {}, head_ang=head_ang, hood=hood, pelvis=False)
    old = people.friend_head
    people.friend_head = mama_head
    try:
        return people.draw(p, "mama")
    finally:
        people.friend_head = old


def handset(x, y, ang, k=1.0, col="#2f7f86"):
    """Трубка радиотелефона: (x, y) — центр, ang — наклон; динамик вверху."""
    def P(pts):
        return lib.T(pts, x, y, k, ang)
    body = P(rect_pts(-20, -86, 20, 86, 16))
    inner = blob(P(rect_pts(8, -86, 20, 86, 6)), mix(col, "#000000", .25), .9)
    inner += blob(P(rect_pts(-20, -86, 20, -60, 12)), mix(col, "#ffffff", .25), .9)
    inner += blob(P(ellipse_pts(-2, -30, 9, 7, 8)), "#cfe6e8", .95)
    for j in range(4):
        inner += blob(P(ellipse_pts(-2 - 0, -10 + j * 12, 3.4, 3.4, 6)), "#cfe6e8", .8)
    return shape(body, col, inner, w=4.4, seed=480) + line(P([(14, -84), (20, -118)]), 5, INK, seed=481, taper=.2, wmin=.6)


def kitchen_back(t, curtain=0.0):
    o = [Wd.wall("morning")]
    # окно с занавеской справа за мамой
    x0, x1, y0, y1 = 610, 900, 560, 1000
    sky = lib.lin_grad([(0, "#8fc4ea", 1), (1, "#e3f2f6", 1)], 0, 0, 0, 1)
    inner = f'<rect x="{x0 - 20}" y="{y0 - 20}" width="{x1 - x0 + 40}" height="{y1 - y0 + 40}" fill="url(#{sky})"/>'
    inner += blob(ellipse_pts(x0 + 70, y0 + 80, 40, 40, 18), "#fff3c4")
    inner += blob(ellipse_pts(x0 + 200 + 10 * math.sin(t * .5), y0 + 120, 56, 20, 12), "#ffffff", .95)
    inner += blob([(x0 - 20, y1 - 120), (x0 + 100, y1 - 150), (x0 + 100, y1 - 190), (x0 + 200, y1 - 190), (x0 + 200, y1 - 130), (x1 + 20, y1 - 150),
                   (x1 + 20, y1 + 20), (x0 - 20, y1 + 20)], "#7f8fa8")
    fr = "#efe6d6"
    mx = (x0 + x1) / 2
    inner += blob(rect_pts(mx - 8, y0, mx + 8, y1), fr) + blob(rect_pts(x0, (y0 + y1) / 2 - 8, x1, (y0 + y1) / 2 + 8), fr)
    o.append(shape(rect_pts(x0, y0, x1, y1, 10), fr, inner, w=5, seed=706))
    o.append(shape(rect_pts(x0 - 24, y1 - 4, x1 + 24, y1 + 26, 6), fr, "", w=4, seed=707))
    # часы и полка с горшками слева
    o.append(Wd.clock_wall(10, 10, "morning", .8, x=330, y=640))
    o.append(shape(rect_pts(260, 900, 470, 920, 4), Wd.WOOD, "", w=4, seed=720))
    o.append(shape([(310, 900, 1), (420, 900, 1), (412, 840, 1), (318, 840, 1)], "#c4673f", "", w=4, seed=721))
    for k in range(5):
        a = -2.3 + k * .4
        o.append(line([(365, 842), (365 + 80 * math.cos(a), 842 + 100 * math.sin(a) + 20 * math.sin(t * 1.5 + k) * .2)], 16, "#5f9a5a", taper=.6, seed=722 + k))
    # чайник на столешнице
    kx, ky = 760, Wd.CT_TOP
    o.append(shape([(kx - 70, ky - 4, 1), (kx + 70, ky - 4, 1), (kx + 80, ky - 70), (kx + 40, ky - 130), (kx - 40, ky - 130), (kx - 80, ky - 70)], "#cf5d4a",
                   blob([(kx + 20, ky - 130), (kx + 80, ky - 70), (kx + 70, ky - 4), (kx + 30, ky - 4)], "#a4402f", .9), w=4.4, seed=730))
    o.append(line([(kx - 70, ky - 80), (kx - 120, ky - 100), (kx - 128, ky - 120)], 12, "#cf5d4a", seed=731))
    o.append(shape(ellipse_pts(kx, ky - 134, 18, 10, 10), "#2a2228", "", w=3, seed=732))
    steam = ""
    for j in range(3):
        ph = (t * .5 + j / 3) % 1
        steam += blob(ellipse_pts(kx - 125 + 10 * math.sin(ph * 6 + j), ky - 130 - 90 * ph, 12 + 14 * ph, 10 + 10 * ph, 10), "#ffffff", .55 * math.sin(math.pi * ph))
    o.append(steam)
    return "".join(o)


def kitchen_front():
    return Wd.counter() + Wd.floor("morning")


def s08(t):
    t0 = 10.7
    k = ease_io(clamp((t - t0) / 1.8))
    tu = T_UDIV
    surprise = smooth(tu - .02, tu + .1, t)
    hit = bump(t, tu, .35)
    # руки: трубка у уха; на «удивилась» отдёргивает голову, рука вздрагивает
    hip = (480.0, 1262.0)
    lean = .02 - .07 * surprise + .02 * osc(t, 1.1)
    talkk = R.talk(t, 10.7, tu - .05, rate=6.2)
    ex = dict(lid=.55 + .45 * surprise, look=(.55 - .3 * surprise, .15 - .1 * surprise), brows="up" if surprise > .4 else "calm",
              mouth="talk", open=.28 * talkk + .95 * surprise * (1 - .0), smile=.55 * (1 - surprise) - .2 * surprise, blush=.6,
              closed=blink_at(t, 10.95) * (1 - surprise), hair=7 * hit * osc(t, 14))
    hd_ang = .03 + .05 * osc(t, 1.7) - .1 * surprise
    # предварительно считаем голову, чтобы поставить запястье у уха
    m0 = mama(t, hip, lean=lean, arms={"n": ("ang", .3, .3), "f": ("ang", .2, .3)}, hands={"n": dict(kind="none"), "f": dict(kind="none")}, expr=ex, head_ang=hd_ang)
    hx, hy = m0["head"]
    ear = np.array([hx - 78 * R.BS - 6 * surprise, hy + 6 * R.BS * 1.0])
    wr = ear + np.array([-6, 74]) + np.array([-3, -2]) * hit * 4
    arms = {"n": ("ang", .05 + .1 * surprise, 3.3 - .15 * surprise), "f": ("ang", .15, .3)}
    hands = {"n": dict(kind="open", flip=-1, dir=(0, -1), curl=(.95, .95, .95, .95), spread=0, thumb=.9, bend=.1),
             "f": dict(kind="none")}
    m = mama(t, hip, lean=lean, arms=arms, hands=hands, expr=ex, head_ang=hd_ang)
    hx, hy = m["head"]
    ear = np.array([hx - 78 * R.BS - 6 * surprise, hy + 6 * R.BS * 1.0])
    wr_ = m["wrist"]["n"]
    hs = handset(wr_[0] - 6, wr_[1] - 62, -4 + 4 * surprise, 0.74)
    w = kitchen_back(t)
    # «!?» над головой
    e = t - tu
    mark = ""
    if e > -0.02:
        sc = back_out(clamp(e / .22), 2.2) * (1.0 + .0)
        wob = 6 * math.sin(e * 22) * math.exp(-e * 5)
        mark = text(hx + 30, hy - 150 - 10 * ease_out(clamp(e / .3)), "!?", 120 * sc + 1, "#ffd23f", INK, 9, rot=-10 + wob)
    front = mark
    # камера: крупно + толчок на «удивилась»
    cam = (500 + 6 * osc(t, .9) - 14 * k, 960 - 20 * k, 2.0 + .45 * k + .22 * hit, 1.4 * (1 - k) - .5 * hit * osc(t, 8))
    return compose(w + R.layers(m, hs, "") + kitchen_front(), cam, front=front)


# ═════════════════════════ гостиная ═════════════════════════
LF = 1560      # линия пола гостиной


def living_back(t, mode="day", sun=1.0):
    o = []
    wall = "#ead6b0" if mode == "day" else "#e6caa0"
    o.append(f'<rect x="-1400" y="-1400" width="4200" height="{LF + 1400}" fill="{wall}"/>')
    o.append(f'<rect x="-1400" y="1180" width="4200" height="{LF - 1180}" fill="{mix(wall, "#8a6a3a", .16)}"/>')
    o.append(line([(-1400, 1180), (2800, 1180)], 4, INK, taper=.05, wmin=.9, seed=1900))
    o.append(shape(rect_pts(-1400, -40, 2800, -10), mix(wall, "#000000", .12), "", w=3.6, seed=1901))
    # окно справа с тёплым светом
    x0, x1, y0, y1 = 760, 1090, 520, 1030
    g = lib.lin_grad([(0, "#9fd0ee", 1), (1, "#f6ecc8", 1)], 0, 0, 0, 1)
    inner = f'<rect x="{x0 - 10}" y="{y0 - 10}" width="{x1 - x0 + 20}" height="{y1 - y0 + 20}" fill="url(#{g})"/>'
    inner += blob(ellipse_pts(x0 + 90, y0 + 120, 50, 50, 18), "#fff2bf")
    inner += blob(ellipse_pts(x0 + 230 + 14 * math.sin(t * .4), y0 + 110, 60, 20, 12), "#ffffff", .95)
    inner += blob([(x0 - 10, y1 - 140), (x0 + 120, y1 - 170), (x0 + 120, y1 - 220), (x0 + 220, y1 - 220), (x0 + 220, y1 - 150), (x1 + 10, y1 - 170),
                   (x1 + 10, y1 + 10), (x0 - 10, y1 + 10)], "#8a9cb2")
    for r_, (tx, th) in enumerate([(x0 + 40, 120), (x0 + 250, 90)]):
        inner += blob(ellipse_pts(tx, y1 - 140 - th * .2, 40, 70, 14), "#7aa86a")
    fr = "#f2e9d8"
    mx = (x0 + x1) / 2
    inner += blob(rect_pts(mx - 9, y0, mx + 9, y1), fr) + blob(rect_pts(x0, (y0 + y1) / 2 - 9, x1, (y0 + y1) / 2 + 9), fr)
    o.append(shape(rect_pts(x0, y0, x1, y1, 10), fr, inner, w=5.2, seed=1906))
    o.append(shape(rect_pts(x0 - 26, y1 - 4, x1 + 26, y1 + 26, 6), fr, blob(rect_pts(x0 - 26, y1 + 14, x1 + 26, y1 + 26), "#d6ccbb"), w=4.2, seed=1907))
    # занавеска справа
    o.append(shape([(x1 - 40, y0 - 40), (x1 + 120, y0 - 40), (x1 + 120, y1 + 120), (x1 - 10, y1 + 120), (x1 - 30 + 4 * math.sin(t), y0 + 200)], "#d98c78",
                   "".join(line([(x1 - 20 + k * 36, y0 - 30), (x1 - 10 + k * 36 + 4 * math.sin(t + k), y1 + 100)], 2.4, "#b86a58", seed=1910 + k, op=.8)
                           for k in range(4)), w=4.4, seed=1908))
    # картина
    o.append(shape(rect_pts(150, 480, 400, 690, 6), "#f6efe0", blob(rect_pts(176, 506, 374, 664), "#9cc2b4") +
                   blob([(176, 640), (250, 570), (300, 620), (340, 560), (374, 600), (374, 664), (176, 664)], "#6f9a86") +
                   blob(ellipse_pts(320, 550, 24, 24, 12), "#f1d27a"), w=5, seed=1912))
    o.append(Wd.clock_wall(10, 10, "morning", .55, x=560, y=380))
    # пол и ковёр
    col = "#b98d5f"
    inner = "".join(line([(-1400, LF + 40 + k * 90 + k * k * 8), (2800, LF + 40 + k * 90 + k * k * 8)], 3, mix(col, "#000000", .25), taper=.05, wmin=.9,
                         seed=1920 + k, op=.8) for k in range(6))
    inner += blob(rect_pts(-1400, LF, 2800, LF + 30), "#000000", .12)
    o.append(shape(rect_pts(-1400, LF, 2800, 3600), col, inner, w=4.6, seed=1919))
    # торшер слева
    o.append(line([(120, LF), (120, 760)], 10, "#4a3a30", seed=1930, taper=.05, wmin=.9))
    o.append(shape([(70, 760, 1), (170, 760, 1), (150, 680, 1), (90, 680, 1)], "#f1cf86", blob([(130, 680), (150, 680), (170, 760), (140, 760)], "#d7a95a", .8),
                   w=4.4, seed=1931))
    o.append(shape(ellipse_pts(120, LF + 4, 50, 10, 12), "#4a3a30", "", w=3, seed=1932))
    return "".join(o)


def rug():
    return shape(ellipse_pts(540, LF + 130, 540, 70, 24), "#c8674f", blob(ellipse_pts(540, LF + 130, 420, 46, 24), "#e1a86a", .8) +
                 blob(ellipse_pts(540, LF + 130, 300, 28, 20), "#c8674f", .8), w=4.4, seed=1940)


def sofa(sx0=60, sx1=1000, top=930, seat=1390):
    """Диван анфас: спинка, подлокотники, сиденье."""
    C, CS, CL = "#5f8794", "#476c78", "#7aa3af"
    o = []
    o.append(blob(ellipse_pts((sx0 + sx1) / 2, LF + 20, (sx1 - sx0) / 2 + 20, 24, 20), "#000000", .18))
    for x in (sx0 + 40, sx1 - 40):
        o.append(shape(rect_pts(x - 22, seat + 100, x + 22, LF + 8, 4), "#5a4030", "", w=4, seed=2000 + x % 7))
    back = rect_pts(sx0 + 90, top, sx1 - 90, seat + 20, 46)
    o.append(shape(back, C, blob(rect_pts(sx0 + 90, top + 210, sx1 - 90, seat + 20, 0), CS, .7) + blob(rect_pts(sx0 + 100, top + 6, sx1 - 100, top + 40, 20), CL, .8) +
                   line([((sx0 + sx1) / 2, top + 20), ((sx0 + sx1) / 2, seat)], 4, INK, seed=2010, op=.75) +
                   "".join(line([(x, top + 80), (x + 8, top + 130)], 2.4, CS, seed=2011 + i, op=.8) for i, x in enumerate((sx0 + 300, sx1 - 300))), w=5, seed=2012))
    seatp = rect_pts(sx0 + 40, seat, sx1 - 40, seat + 120, 26)
    o.append(shape(seatp, CL, blob(rect_pts(sx0 + 40, seat + 80, sx1 - 40, seat + 120, 0), CS, .6) + line([((sx0 + sx1) / 2, seat + 8), ((sx0 + sx1) / 2, seat + 110)], 4, INK, seed=2020, op=.7),
                   w=5, seed=2021))
    for x0_, x1_ in ((sx0, sx0 + 110), (sx1 - 110, sx1)):
        o.append(shape(rect_pts(x0_, top + 150, x1_, seat + 126, 36), C, blob(rect_pts(x0_ + (60 if x0_ > 500 else 0), top + 170, x0_ + 50 + (60 if x0_ > 500 else 0), seat + 120, 0), CS, .6) +
                       blob(rect_pts(x0_, top + 150, x1_, top + 200, 30), CL, .75), w=5, seed=2030 + x0_ % 9))
    return "".join(o)


def sit_dima(t, hip, lean, arms, hands, expr, head_ang, feet_dx=250, feet_dy=215):
    feet = {"n": ((hip[0] + feet_dx, hip[1] + feet_dy), 0.0), "f": ((hip[0] + feet_dx - 36, hip[1] + feet_dy - 4), 0.0)}
    return R.dima(t, hip=hip, lean=lean, arms=arms, hands=hands, expr=expr, head_ang=head_ang, feet=feet)


# ═════════════════════════ книга ═════════════════════════
def book(cx, cy, w, h, t, flip_t0, rot=-6.0, dust=1.0, tab=True):
    """Толстая раскрытая книга «лицом к зрителю»; листаются страницы (flip_t0 — начало, 0.42 с на страницу)."""
    def P(pts):
        return lib.T(pts, cx, cy, 1.0, rot)
    o = []
    hw = w / 2
    o.append(blob(P(ellipse_pts(8, h / 2 + 20, hw + 20, 14, 16)), "#000000", .16))
    # обложка и стопка страниц снизу
    o.append(shape(P(rect_pts(-hw - 14, -h / 2 - 10, hw + 14, h / 2 + 18, 10)), "#6d4a8a", blob(P(rect_pts(-hw - 14, h / 2 + 4, hw + 14, h / 2 + 18, 4)), "#4c3262", .9), w=5, seed=3000))
    o.append(shape(P(rect_pts(-hw - 4, -h / 2 - 2, 0, h / 2 + 10, 4)), "#f3ead4", blob(P(rect_pts(-hw - 4, h / 2 - 4, 0, h / 2 + 10, 0)), "#d9cdb0", .9), w=3.6, seed=3001))
    o.append(shape(P(rect_pts(0, -h / 2 - 2, hw + 4, h / 2 + 10, 4)), "#f3ead4", blob(P(rect_pts(0, h / 2 - 4, hw + 4, h / 2 + 10, 0)), "#d9cdb0", .9), w=3.6, seed=3002))
    # строки текста: серые штрихи
    for side in (-1, 1):
        for r in range(9):
            y = -h / 2 + 24 + r * (h - 56) / 8
            x0_ = side * 22
            x1_ = side * (hw - 24 - (14 if r % 4 == 3 else 0))
            o.append(line(P([(x0_, y), (x1_, y + 1)]), 3, "#8d8470", seed=3010 + r + (side > 0) * 20, op=.65, taper=.1, wmin=.8))
    o.append(line(P([(0, -h / 2 - 2), (0, h / 2 + 10)]), 5, INK, seed=3004, taper=.05, wmin=.9))
    # переворачивающиеся страницы справа налево: сжатие по x вокруг корешка
    per = .42
    for i in range(6):
        u = (t - (flip_t0 + i * per)) / .36
        if u <= 0 or u >= 1:
            continue
        th = math.pi * ease_io(u)
        xe = hw * math.cos(th)
        lift = 12 * math.sin(th)
        pg = [(0, -h / 2 - 2), (xe, -h / 2 - 2 - lift), (xe, h / 2 + 8 - lift * .6), (0, h / 2 + 10)]
        sh = abs(math.sin(th))
        col = mix("#f3ead4", "#cdbf9f", .45 * sh)
        o.append(shape(P(pg), col, "".join(line(P([(xe * .12, -h / 2 + 24 + r * (h - 56) / 8 - lift * .5), (xe * .88, -h / 2 + 24 + r * (h - 56) / 8 - lift * .5)]),
                                                 2.6, "#8d8470", seed=3050 + r, op=.5) for r in range(0, 9, 2)), w=3.4, seed=3040 + i))
    if tab:
        # закладка «весна» торчит сверху из страниц
        tp = [(hw * .35, -h / 2 + 16), (hw * .35 + 120, -h / 2 + 16), (hw * .35 + 120, -h / 2 - 44), (hw * .35, -h / 2 - 44)]
        o.append(shape(P(tp), "#e9c46a", text_in(P, hw * .35 + 60, -h / 2 - 2, "весна", 40, "#5a3a14"), w=4, seed=3060))
    # пыль на обложке и по краю
    if dust > 0:
        rs = np.random.RandomState(5)
        for _ in range(24):
            x = rs.uniform(-hw - 10, hw + 10)
            o.append(blob(P(ellipse_pts(x, h / 2 + 14 + rs.uniform(-2, 2), rs.uniform(7, 16), 4, 6)), "#b3aa98", .8 * dust))
    return "".join(o)


def text_in(P, x, y, s, size, col):
    px, py = P([(x, y)])[0]
    return f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle" font-family="{FONT}" font-weight="900" font-size="{size}" fill="{col}">{s}</text>'


def dust_puffs(x, y, t, t0, n=7, spread=170):
    o = []
    for j in range(n):
        e = (t - t0 - j * .06)
        if e < 0 or e > 1.8:
            continue
        u = e / 1.8
        a = -2.7 + j * (2.2 / n) + .2 * math.sin(j * 3)
        d = spread * ease_out(u, 2) * (.5 + .5 * (j % 3) / 2)
        px, py = x + d * math.cos(a) * 1.2, y + d * math.sin(a) * .9 - 30 * u
        r = 22 + 36 * u
        o.append(blob(ellipse_pts(px, py, r, r * .8, 12), "#d6cfc0", .55 * (1 - u)))
    return "".join(o)


def tear_calendar(x, y, t, t_pop):
    """Отрывной календарь раннего марта: лист «1 марта» с зелёной веточкой; на слове «весны» подпрыгивает."""
    e = t - t_pop
    pop = back_out(clamp(e / .28), 2.4) if e > -0.01 else 0.0
    hang = 3 * math.sin(t * 2.0) * (1 if e > 0 else 0)
    s = max(.0, pop)
    if s < .02:
        return ""
    def P(pts):
        return lib.T(pts, x, y, s, hang)
    o = [blob(P(rect_pts(-62, -80, 82, 110, 6)), "#000000", .16)]
    o.append(shape(P(rect_pts(-70, -96, 70, 100, 6)), "#f8f3e6", blob(P(rect_pts(-70, -96, 70, -52, 0)), "#cf5d4a", .95), w=4.4, seed=3100))
    o.append(shape(P(ellipse_pts(-36, -98, 8, 8, 8)), "#403830", "", w=2, seed=3101) + shape(P(ellipse_pts(36, -98, 8, 8, 8)), "#403830", "", w=2, seed=3102))
    o.append(text_in(P, 0, -64, "МАРТ", 40 * s ** 0.0, "#fff6e0"))
    o.append(text_in(P, 0, 22, "1", 100, "#2c2630"))
    # зелёная веточка
    o.append(line(P([(-40, 84), (-14, 64), (16, 56)]), 4, "#4f8a4a", seed=3103, taper=.3))
    for j, (lx, ly, a_) in enumerate([(-24, 70, -.9), (-4, 62, .8), (10, 58, -.7)]):
        o.append(shape(P(ellipse_pts(lx, ly, 13, 6, 8, rot=math.degrees(a_) * 1.0)), "#6fb25f", "", w=2.6, seed=3110 + j))
    return "".join(o)


def s09(t):
    t0 = 12.3
    k = ease_io(clamp((t - t0) / 2.8))
    hip = (410.0, 1335.0)
    lean = -.02 + .02 * osc(t, .5)
    bw = (600.0, 1235.0)
    sw = osc(t, .9)
    # руки: ближняя держит нижний край книги справа, дальняя — слева (за книгой)
    arms = {"n": ("ik", (bw[0] + 108, bw[1] + 96), -1), "f": ("ik", (bw[0] - 90, bw[1] + 110), -1)}
    hands = {"n": dict(kind="open", flip=-1, dir=(-.35, -1), curl=(.55, .6, .65, .7), spread=.08, thumb=.6, bend=.12),
             "f": dict(kind="open", flip=-1, dir=(.3, -1), curl=(.55, .6, .65, .7), spread=.08, thumb=.6, bend=.12)}
    gaze = smooth(T_VESNY - .3, T_VESNY + .1, t)
    ex = dict(lid=.45, look=(.55 - .2 * gaze, .75 - 1.4 * gaze), brows="calm" if gaze < .5 else "up", mouth="flat" if gaze < .5 else "talk", open=.2 * gaze,
              smile=.2, closed=blink_at(t, 13.3) + blink_at(t, 14.8))
    dm = sit_dima(t, hip, lean, arms, hands, ex, .2 - .12 * gaze + .02 * sw)
    bk = book(bw[0], bw[1] + 4 * osc(t, 1.1), 290, 215, t, 12.65)
    w = living_back(t) + rug() + sofa()
    dust = dust_puffs(bw[0], bw[1] - 90, t, 12.45) + dust_puffs(bw[0] + 20, bw[1] - 80, t, 13.9, n=5, spread=120)
    cal = tear_calendar(790, 800, t, T_VESNY)
    # камера: хлёст слева на входе (whip), потом наезд к книге и Диме
    ww = whip_in(t, t0, .22)
    cam = (560 - 360 * ww + 30 * k, 1130 + 40 * k, 1.0 + .38 * ease_io(clamp((t - t0) / 2.6)), -1.2 * (1 - k) + .6 * k)
    d = R.layers(dm, bk, "")
    return compose(w + d + dust + cal, cam, blur_x=26 * ww)


# ═════════════════════════ верёвочка ═════════════════════════
def paw_up(x_sh, y_sh, x_tip, y_tip, seed=0):
    """Поднятая лапа кота (в системе рисунка кота): плечо → кончик, с подушечкой и пальцами."""
    pts = [(x_sh, y_sh), ((x_sh + x_tip) / 2 + (6 if x_tip > x_sh else -6), (y_sh + y_tip) / 2), (x_tip, y_tip)]
    bd = band(pts, 42, 38, step=4, cap=True)
    o = shape(bd, Cat.CAT, blob(band(pts[1:], 14, 12, step=4, cap=False), Cat.CAT_SH, .5), w=4.8, seed=3300 + seed)
    ang = math.atan2(y_tip - y_sh, x_tip - x_sh)
    nx, ny = math.cos(ang), math.sin(ang)
    o += blob(ellipse_pts(x_tip - nx * 2, y_tip - ny * 2 + 1, 11, 8, 8, rot=math.degrees(ang) + 90), "#e8823a")
    for j in (-1, 0, 1):
        o += blob(ellipse_pts(x_tip + nx * 10 - ny * j * 11, y_tip + ny * 10 + nx * j * 11, 4.4, 4, 8), "#e8823a")
    return o


def cat_at(x, y, k, st, t, paws=0.0, stretch=1.0):
    """Кот в мире; paws 0..1 — обе передние лапы вверх (ловит); stretch — растяжение в прыжке."""
    inner = Cat.draw(Cat.CX, Cat.CBOT, 1.0, st, t)
    if paws > 0.01:
        a = paws
        inner += paw_up(800, 1226, 800 - 56 * a, 1226 - 96 * a, 1) + paw_up(872, 1226, 872 + 56 * a, 1226 - 96 * a, 2)
    return (f'<g transform="translate({x:.2f} {y:.2f}) scale({k * (2 - stretch):.4f} {k * stretch:.4f}) translate({-Cat.CX} {-Cat.CBOT})">{inner}</g>')


def rope(tip, bob, slack, col="#e9e2d0"):
    mx, my = (tip[0] + bob[0]) / 2, (tip[1] + bob[1]) / 2 + slack
    pts = [tip, ((tip[0] + mx) / 2, (tip[1] + my) / 2 + slack * .1), (mx, my), ((bob[0] + mx) / 2, (bob[1] + my) / 2), bob]
    return line([tuple(p) for p in pts], 5, "#8a7a64", seed=3400, taper=.05, wmin=.9)


def pompom(x, y, r, rot, t):
    o = ""
    o += shape(ellipse_pts(x, y, r, r * .95, 14), "#e0576a", blob(ellipse_pts(x + r * .3, y + r * .3, r * .6, r * .5, 10), "#b83a4e", .9) +
               blob(ellipse_pts(x - r * .3, y - r * .3, r * .3, r * .22, 8), "#ff9aa6", .9), w=4.2, seed=3410)
    for j in range(4):
        a = rot + j * math.pi / 2 + .5
        o += line([(x + r * .8 * math.cos(a), y + r * .8 * math.sin(a)), (x + r * 1.35 * math.cos(a), y + r * 1.35 * math.sin(a))], 4, "#e0576a", seed=3420 + j, taper=.3)
    return o


def s11(t):
    t0 = 16.3
    P = .72
    ph = ((t - T_VEREV) / P) % 1.0 if t >= T_VEREV else ((t - T_VEREV) / P) % 1.0
    sinp = math.sin(math.pi * ph)
    hip = (310.0, 1262.0)
    # верёвочка: кончик палочки и шарик
    tip = np.array([790.0 + 14 * math.sin(t * 5), 1010.0 - 40 * sinp])
    bob = np.array([tip[0] + 26 * math.sin(2 * math.pi * ph + .8), 1410 - 215 * sinp])
    slack = max(0.0, 360 - np.linalg.norm(bob - tip)) * .35 + 12 * math.sin(t * 6)
    shoulder_guess = np.array([hip[0] + 140, 1050])
    wr = np.array([600.0, 1155 - 38 * sinp + 8 * math.sin(t * 6)])
    arms = {"n": ("ik", tuple(wr), -1), "f": ("ang", .25, .35)}
    hands = {"n": dict(kind="open", flip=-1, dir=(.8, -.6), curl=(.95, .95, .95, .95), spread=0, thumb=.9, bend=.1),
             "f": dict(kind="open", flip=-1, dir=(.1, 1), curl=(.3, .35, .4, .45), spread=.1, thumb=.4)}
    ex = dict(lid=.85, look=(.85, .5), brows="up", mouth="laugh", open=.55 + .3 * sinp, laugh=0.0, blush=1.0, smile=1.0, closed=0.0, hair=4 * osc(t, 3))
    dm = R.dima(t, hip=hip, lean=.28 + .03 * osc(t, 1.4), arms=arms, hands=hands, expr=ex, head_ang=.08, hood=3 * osc(t, 2))
    wrist = dm["wrist"]["n"]
    stick = line([tuple(wrist - np.array([40, -22])), tuple(tip)], 11, "#8a5a30", seed=3430, taper=.05, wmin=.9)
    stick = line([tuple(wrist - np.array([40, -22])), tuple(tip)], 7, "#c98f5a", seed=3431, taper=.05, wmin=.9) if False else stick
    # кот: прыгает за шариком
    jump = max(0.0, math.sin(math.pi * clamp((ph - .12) / .62)))
    cat_y = LF + 4 - 150 * jump
    st = dict(look=(-.1, -.8 + .3 * (1 - jump)), blink=0.0, tilt=-6 * jump + 3 * osc(t, 1.6), ear=-8 * jump, perk=.6 + .4 * jump, tail=14 * osc(t, 2.2) * (1 + jump),
              smile=1.0, flame_e=1.2, turn=.0)
    cat_svg = cat_at(800, cat_y, 0.82, st, t, paws=ease_io(clamp((jump - .35) / .5)), stretch=1 + .1 * jump)
    shadow = blob(ellipse_pts(800, LF + 14, 130 * (1 - .35 * jump), 18, 14), "#000000", .2)
    w = living_back(t) + rug() + shadow
    bobs = rope(tuple(tip), tuple(bob), slack) + pompom(bob[0], bob[1], 24, t * 4, t)
    # искры радости над котом на прыжке
    sp = ""
    if jump > .6:
        for j in range(3):
            a = -1.1 + j * .9
            sp += Wd.sparkle(800 + 210 * math.cos(a), cat_y - 250 + 90 * math.sin(a) * 1.4, 22 * jump, t * 3 + j)
    shake = 1.2 * osc(t, 17) * bump(t, T_VEREV, .5)
    cam = (570 + 5 * osc(t, 11) * (.3 + .7 * jump) + shake, 1280 + 7 * osc(t, 13, 1) * (.3 + .7 * jump), 1.16 + .02 * jump, .3 * osc(t, 6) * jump)
    return compose(w + R.layers(dm, stick, "") + cat_svg + bobs + sp, cam)


# ═════════════════════════ диван, воскресенье ═════════════════════════
def heart(x, y, r, col="#e8556d", rot=0.0):
    pts = []
    for i in range(24):
        a = i / 24 * 2 * math.pi
        hx = 16 * math.sin(a) ** 3
        hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((x + hx * r / 16, y + hy * r / 16))
    pts = lib.T(pts, 0, 0, 1.0, rot, x, y)
    return shape(pts, col, blob([(x - r * .55, y - r * .5), (x - r * .25, y - r * .7), (x - r * .2, y - r * .45)], "#ffd0d6", .9), w=3.6, seed=3500)


def s14(t):
    t0 = 23.2
    k = ease_io(clamp((t - t0) / 2.4))
    hip = (330.0, 1345.0)
    turn = smooth(T_KOT - .12, T_KOT + .22, t)
    sm = smooth(T_VOSKR - .1, T_VOSKR + .35, t)
    ex = dict(lid=.7, look=(.9 - .5 * turn, .05), brows="calm", mouth="smile", smile=.7 + .3 * sm, blush=.7 * sm, closed=blink_at(t, 24.0) + blink_at(t, 25.1),
              hair=2 * osc(t, 2))
    arms = {"n": ("ang", .28 + .03 * osc(t, .8), .55), "f": ("ang", .2, .4)}
    hands = {"n": dict(kind="open", flip=-1, dir=(.3, 1), curl=(.35, .4, .45, .5), spread=.1, thumb=.4),
             "f": dict(kind="open", flip=-1, dir=(.2, 1), curl=(.35, .4, .45, .5), spread=.1, thumb=.4)}
    dm = sit_dima(t, hip, .06 + .03 * osc(t, .6), arms, hands, ex, .08 - .06 * turn + .02 * osc(t, .7), feet_dx=250, feet_dy=215)
    # кот рядом на диване: смотрит в окно, на «кот» поворачивается к зрителю
    st = dict(look=(1.0 * (1 - turn), -.1 * (1 - turn)), turn=.9 * (1 - turn), tilt=-5 * (1 - turn) + 4 * turn, ear=-6 * bump(t, 24.9, .3),
              perk=.8 * turn, blink=blink_at(t, 23.9) + blink_at(t, 25.0, .2), tail=6 * osc(t, .7), smile=1.0 if turn > .5 else 0.0, flame_e=1.0)
    cat_svg = cat_at(660, 1392, .82, st, t)
    w = living_back(t) + rug() + sofa() + ""
    # тёплый свет из окна
    g = lib.rad_grad([(0, "#ffd890", .38), (1, "#ffd890", 0)], 900, 800, 620, 520)
    glow = f'<rect x="200" y="300" width="1100" height="1000" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    hearts = ""
    for j in range(7):
        e = t - (T_VOSKR + .02 + j * .17)
        if e < 0:
            continue
        u = e / 1.7
        if u > 1.0:
            u = u % 1.0 + 0.0 if j < 99 else 1.0
        sc = back_out(clamp(u / .18), 2.0)
        x = 585 + 60 * math.sin(j * 2.1) + 36 * math.sin(u * 5 + j)
        y = 1020 - 420 * u
        hearts += heart(x, y, (30 + 10 * (j % 3)) * sc, "#e8556d" if j % 2 == 0 else "#f08a9c", (j - 3) * 6 + 8 * math.sin(u * 6)) if sc > .02 and u < .98 else ""
    cam = (545 + 18 * (k - .5), 1180 - 14 * k, 1.12 + .08 * k, -.5 + .8 * k)
    return compose(w + R.layers(dm, "", "") + cat_svg + glow + hearts, cam)


# ═════════════════════════ кот крупно ═════════════════════════
def phone_cross(x, y, s, t, shake=0.0):
    pts = lib.T(rect_pts(-36, -62, 36, 62, 12), x, y, s, shake)
    o = shape(pts, "#2f3340", blob(lib.T(rect_pts(-28, -50, 28, 46, 6), x, y, s, shake), "#7aa0c4", .95), w=4.4, seed=3600)
    ring = ellipse_pts(x, y, 92 * s, 92 * s, 22)
    o += f'<path d="{lib.fill_d(ring) if hasattr(lib, "fill_d") else ""}" fill="none"/>'
    r = 92 * s
    o += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="none" stroke="{INK}" stroke-width="{22 * s:.1f}"/>'
    o += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="none" stroke="#e0463c" stroke-width="{13 * s:.1f}"/>'
    a = math.radians(-45)
    o += f'<line x1="{x - r * math.cos(a):.1f}" y1="{y + r * math.sin(a):.1f}" x2="{x + r * math.cos(a):.1f}" y2="{y - r * math.sin(a):.1f}" stroke="{INK}" stroke-width="{22 * s:.1f}" stroke-linecap="round"/>'
    o += f'<line x1="{x - r * math.cos(a):.1f}" y1="{y + r * math.sin(a):.1f}" x2="{x + r * math.cos(a):.1f}" y2="{y - r * math.sin(a):.1f}" stroke="#e0463c" stroke-width="{13 * s:.1f}" stroke-linecap="round"/>'
    return o


def bubble(x, y, w, h, s, tail, label, size):
    body = rect_pts(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 44)
    o = shape(lib.T(body, 0, 0, s, 0, x, y), "#fffaf0", "", w=5.6, seed=3610)
    tx, ty = tail
    tp = [(x - 50, y + h / 2 - 8), (tx, ty), (x + 20, y + h / 2 - 8)]
    o += shape(lib.T(tp, 0, 0, s, 0, x, y), "#fffaf0", "", w=5.2, seed=3611)
    o += blob(lib.T([(x - 44, y + h / 2 - 12), (x + 14, y + h / 2 - 12), (x - 20, y + h / 2 + 6)], 0, 0, s, 0, x, y), "#fffaf0")
    o += text(x, y + size * .34 * s, label, size * s, "#2c2630", "#fffaf0", 1, 0)
    return o


def s15(t):
    t0 = 25.0
    k = ease_io(clamp((t - t0) / 3.6))
    s = 1.5 + .5 * k
    tilt = -6 + 10 * math.sin(t * 1.3) * (1 - smooth(27.0, 27.8, t))
    st = dict(look=(.0, .0), turn=0.0, tilt=tilt, ear=-8 * bump(t, 25.5, .3), perk=.4 + .4 * bump(t, 26.5, .6), blink=blink_at(t, 26.3, .2) + blink_at(t, 28.0, .2),
              tail=8 * osc(t, .8), smile=0.0, flame_e=1.1)
    ask = ease_out(clamp((t - 25.1) / .45, 0, 1), 3) * 1.0
    wobble = 4 * math.sin(t * 4.0) * ask
    # вся картинка: тёплый фон кадра, кот по центру, поднятая лапа вопросом
    inner = Cat.draw(Cat.CX, Cat.CBOT, 1.0, st, t)
    inner += paw_up(768, 1214, 700 - wobble * .4, 1090 - 12 * ask + wobble, 5) if ask > 0 else ""
    cat_g = f'<g transform="translate(540 1340) scale(1.25) translate({-Cat.CX} {-Cat.CBOT})">{inner}</g>'
    world = "".join([
        f'<rect x="-1400" y="-1400" width="4200" height="{LF + 1400}" fill="#e9d2a8"/>',
        f'<rect x="-1400" y="1260" width="4200" height="2600" fill="#c99d6c"/>', line([(-1400, 1262), (2800, 1262)], 4, INK, taper=.05, wmin=.9, seed=3700),
        blob(ellipse_pts(540, 1340, 330, 30, 20), "#000000", .2), cat_g])
    # надписи в экранных координатах
    bsc = back_out(clamp((t - 25.25) / .3), 2.0)
    pshk = 3 * math.sin(t * 5)
    scr = ""
    if bsc > .02:
        scr += bubble(380, 360 + 4 * math.sin(t * 1.5), 400, 170, bsc, (480, 540), "кот?", 118)
        scr += phone_cross(790, 380 + 4 * math.sin(t * 1.5 + 1), .9 * back_out(clamp((t - 25.6) / .3), 2.0), t, pshk)
    e = t - T_CHAS
    if e > -0.01:
        cs = back_out(clamp(e / .22), 2.6)
        flash = ease_out(clamp(1 - e / .3, 0, 1)) if e > 0 else 0
        wob = 3 * math.sin(e * 18) * math.exp(-e * 4)
        for j in range(12):
            a = j * math.pi / 6 + .2
            r0, r1 = 230 + 40 * ease_out(clamp(e / .3)), 290 + 90 * ease_out(clamp(e / .3))
            scr += line([(540 + r0 * math.cos(a) * 1.7, 150 + r0 * math.sin(a) * .55), (540 + r1 * math.cos(a) * 1.7, 150 + r1 * math.sin(a) * .55)], 8, "#f2c23a",
                        seed=3750 + j, op=clamp(1.4 * (1 - e / .9)))
        scr += text(540, 190, "1 ЧАС", 190 * cs, "#ffd23f", INK, 16, rot=-3 + wob)
        if flash > .02:
            scr += f'<rect width="1080" height="1920" fill="#fff6c8" opacity="{.2 * flash:.3f}"/>'
    cam = (540 + 4 * osc(t, .5), 1100 - 20 * k, s, .6 - .9 * k)
    cx, cy, ss, r = cam
    return compose(world, cam, screen=scr, vig="#2a1408", va=.3)


SHOTS = {"s08": s08, "s09": s09, "s11": s11, "s14": s14, "s15": s15}


def frame(sid, t):
    lib.DEFS.clear()
    return SHOTS[sid](t)
