"""Миф рилса 43 «успешные встают в 5 утра».
s01 (0–1.4): предрассветное небо, огромный будильник 5:00 звенит, перед ним бодро шагает «успешный» в костюме с
галстуком, кружкой кофе и портфелем; влёт камеры с кадра 0 (1/1.42 → 1 за 0.2 с, перелёт, поворот −3° → 0),
второй удар на «успешные» (0.96).
s02 (1.4–3.2): пять «успешных» в костюмах спят в кроватях полукругом под рассветным небом; на «встают» (1.80) все разом
садятся; на «пять» (2.36) над ними рукописное «5:00» с перелётом; на «утра» (2.56) из-за горизонта выпрыгивает солнце."""
import importlib.util
import math
import os

import lib
import person
from lib import (INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, rad_grad,
                 rect_pts, shape, smooth, spring, svg, T)

_HERE = os.path.dirname(os.path.abspath(__file__))
_STORY = os.path.dirname(_HERE)
_sp = importlib.util.spec_from_file_location("alarm37", os.path.join(_STORY, "..", "..", "37_budilnik", "story", "clock", "alarm.py"))
alarm37 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(alarm37)

_ST = {}
HIT1 = 0.96      # «успешные»
UP = 1.80        # «встают»
FIVE = 2.36      # «пять»
SUN = 2.56       # «утра»

BIZ = dict(skin="#f0c8a4", hair="short", hair_c="#3a2a22", top="#34416a", low="#2a3354", face=.35, jacket="#cf3a30",
           shoes="#1e1a22", brow_c="#3a2a22", bw=1.0, h=1.0)


# ─────────────────────────────── общее: небо, звёзды
def sky(top, mid, low, y0=-900, y1=1200):
    g = lin_grad([(0, top, 1), (.55, mid, 1), (1, low, 1)], 0, 0, 0, 1)
    return f'<rect x="-900" y="{y0}" width="2900" height="{y1 - y0}" fill="url(#{g})"/>'


STARS = [(-300, -200, 5), (-120, 60, 4), (60, -120, 6), (210, 120, 4), (380, -60, 5), (520, 220, 3.5), (700, -160, 6), (860, 90, 4),
         (990, -60, 5), (1180, 160, 4), (1320, -180, 5), (-200, 330, 3.5), (120, 360, 4), (300, 300, 3), (760, 330, 3.5), (940, 300, 4),
         (1260, 330, 3.5), (-60, -420, 5), (440, -380, 4), (820, -420, 5), (1120, -380, 4), (-380, -460, 4)]


def stars(t, op=1.0, dy=0.0):
    s = []
    for k, (x, y, r) in enumerate(STARS):
        tw = 0.65 + 0.35 * math.sin(t * (3.0 + k % 4) + k * 1.7)
        rr = r * (0.8 + 0.35 * tw)
        pts = []
        for j in range(8):
            a = j * math.pi / 4
            q = rr * (2.4 if j % 2 == 0 else 0.7)
            pts.append((x + q * math.cos(a), y + dy + q * math.sin(a)))
        s.append(blob(pts, "#fff4c8", op * (0.55 + 0.45 * tw)))
    return "".join(s)


# ─────────────────────────────── s01
def skyline():
    """Силуэт города у горизонта (тёмный, окна горят тёплым)."""
    s = []
    base = 1010
    blds = [(-700, 300), (-560, 420), (-420, 260), (-300, 520), (-160, 340), (-40, 610), (110, 300), (230, 470), (380, 380),
            (520, 560), (660, 300), (790, 640), (950, 360), (1080, 480), (1220, 300), (1360, 540), (1500, 340), (1640, 460)]
    for k, (x, h) in enumerate(blds):
        w = 150 if k % 3 else 120
        pts = rect_pts(x, base - h, x + w, base + 40)
        win = ""
        for r in range(int(h / 60)):
            for c in range(int(w / 40)):
                on = ((k * 7 + r * 3 + c * 5) % 5) < 2
                col = "#ffd37a" if on else "#2a3062"
                win += blob(rect_pts(x + 14 + c * 40, base - h + 24 + r * 60, x + 34 + c * 40, base - h + 52 + r * 60), col)
        s.append(shape(pts, "#1e2452" if k % 2 else "#252b5e", win, w=4, seed=600 + k))
    return "".join(s)


def ground1(t):
    s = []
    gp = [(-900, 1010, 1), (2000, 1010, 1), (2000, 2600, 1), (-900, 2600, 1)]
    inner = blob(rect_pts(-900, 1010, 2000, 1060), "#3c4277")
    # плиты тротуара едут влево — человек идёт вправо
    off = (t * 260) % 240
    for k in range(-5, 14):
        x = k * 240 - off
        inner += line([(x, 1065), (x - 120, 1420)], 4, "#2f3460", taper=.1, wmin=.8, seed=620 + (k % 7))
    inner += line([(-900, 1180), (2000, 1180)], 3.4, "#2f3460", taper=.05, wmin=.9, seed=630)
    s.append(shape(gp, "#4a5088", inner, w=4.4, seed=631))
    return "".join(s)


def mug(hnd, ang):
    x, y = hnd
    s = []
    cx, top = x + 44, y - 46
    body = [(cx - 34, top, 1), (cx + 34, top, 1), (cx + 30, top + 84, 1), (cx - 30, top + 84, 1)]
    s.append(line([(cx - 32, top + 18), (cx - 58, top + 26), (cx - 58, top + 58), (cx - 30, top + 64)], 9, INK, taper=.05, wmin=.9, seed=651))
    inner = blob([(cx + 6, top), (cx + 34, top), (cx + 30, top + 84), (cx + 8, top + 84)], "#d9d2c6")
    inner += blob(rect_pts(cx - 40, top + 30, cx + 40, top + 50), "#cf3a30")
    s.append(shape(body, "#f6f1e8", inner, w=4, seed=652))
    s.append(blob(ellipse_pts(cx, top + 2, 30, 7, 12), "#5a3424"))
    s.append(steam(cx, top, _ST.get("t", 0.0)))
    return "".join(s)


def steam(x, y, t):
    s = []
    for k in range(3):
        ph = (t * 1.3 + k / 3) % 1.0
        yy = y - 14 - ph * 110
        xx = x - 18 + k * 18
        pts = [(xx + 10 * math.sin(ph * 6 + k + j), yy - j * 22) for j in range(4)]
        w = 7 * math.sin(ph * math.pi)
        if w > 1:
            s.append(line(pts, w, "#f2eee6", taper=.6, seed=660 + k))
    return "".join(s)


def briefcase(hnd, ang, sw=0.0):
    x, y = hnd
    g = []
    g.append(line([(-34, 8), (-30, -14), (30, -14), (34, 8)], 9, INK, taper=.05, wmin=.9, seed=671))
    body = rect_pts(-96, 6, 96, 140, 14)
    inner = blob(rect_pts(-96, 96, 100, 144), "#5e3418")
    inner += line([(-96, 46), (96, 46)], 3.4, "#4a2812", taper=.05, wmin=.9, seed=672)
    g.append(shape(body, "#8a4c24", inner, w=4.6, seed=673))
    g.append(shape(rect_pts(-16, 36, 16, 58, 4), "#e8c35a", "", w=3, seed=674))
    return f'<g transform="translate({f(x)} {f(y + 10)}) rotate({f(sw)})">{"".join(g)}</g>'


def biz_walk(t, x, y, sc, sd, spec=BIZ):
    ph = t * 2 * math.pi * 1.7
    sw = math.sin(ph)
    pose = {"walk": ph, "mouth": "smile", "brow": 0.35, "look": (0.5, -0.1), "head_tilt": 3 * math.sin(ph * 2),
            "arms": {"R": (14, 118)}, "near_front": True,
            "in_hand": {"R": mug, "L": lambda h, a: briefcase(h, a, -8 * sw)},
            "curl": {"R": 0.75, "L": 0.85}}
    return person.draw(spec, pose, x, y, sc, sd)


def s01_world(t):
    s = [_ST["sky1"], stars(t), _ST["city"], ground1(t)]
    # будильник — огромный, позади, звенит
    ax, ay, asz = 690, 560, 265
    jump = 10 * abs(math.sin(t * 2 * math.pi * 3.2))
    s.append(alarm37.shadow(ax, ay + 1.27 * asz + 4, asz, .45, "#121530"))
    # свет от циферблата
    g = rad_grad([(0, "#fff2b0", .35), (1, "#fff2b0", 0)], ax, ay, 520, 520)
    s.append(f'<rect x="{ax - 560}" y="{ay - 560}" width="1120" height="1120" fill="url(#{g})"/>')
    s.append(alarm37.alarm(ax, ay - jump, asz, hh=5, mm=0, ring=1.0, t=t, uid="m1"))
    s.append(alarm37.ring_marks(ax, ay - jump, asz, t, 1.0, "#ffe7a0", seed=690))
    # человек
    px = 270 + 50 * t
    s.append(f'<ellipse cx="{f(px + 10)}" cy="1258" rx="150" ry="20" fill="#20244a" opacity=".55"/>')
    s.append(biz_walk(t, px, 1240, 1.0, 700))
    return "".join(s)


def s01_cam(t):
    s0 = 1 / 1.42
    if t < 0.2:
        u = ease_out(t / 0.2, 3)
        sc = s0 + (1.05 - s0) * u
        rot = -3 * (1 - u)
    else:
        e = t - 0.2
        sc = 1 + 0.05 * math.exp(-e * 9) * math.cos(e * 15)
        rot = 0.6 * math.exp(-e * 7) * math.sin(e * 16)
    e = t - HIT1
    cx, cy = 560 + 20 * t, 900 - 10 * t
    if e >= 0:
        k = math.exp(-e * 7)
        sc *= 1 + 0.09 * k * min(1, e / 0.05)
        cy += 10 * k * math.sin(e * 40)
    return cx, cy, sc, rot


# ─────────────────────────────── s02
SLEEP = [
    dict(skin="#f0c8a4", hair="short", hair_c="#3a2a22", top="#34416a", low="#2a3354", jacket="#cf3a30", brow_c="#3a2a22"),
    dict(skin="#c98e64", hair="short", hair_c="#1e1612", top="#3d3d46", low="#2a2a30", jacket="#2f7fd0", brow_c="#1e1612"),
    dict(skin="#f3d2b6", hair="bob", hair_c="#b0652e", top="#5a3a5e", low="#3a2840", jacket="#e0b23a", brow_c="#7a4020"),
    dict(skin="#8d5a3c", hair="bald", hair_c="#2a1a12", top="#2e4a44", low="#20342f", jacket="#d04a7a", brow_c="#2a1a12", mustache=True),
    dict(skin="#f0c8a4", hair="ponytail", hair_c="#e2c27a", top="#40465a", low="#2a2e3c", jacket="#3aa070", brow_c="#9a7a40"),
]
# (x центра кровати, y низа кровати, масштаб) — полукругом: середина ближе
BEDS = [(105, 1150, 0.80), (318, 1215, 0.96), (540, 1285, 1.12), (762, 1215, 0.96), (975, 1150, 0.80)]
ORDER = [0, 4, 1, 3, 2]


def bed(x, yb, sc, part, sd, mound=1.0):
    """Кровать со стороны ног. part='back' — изголовье и подушка; 'front' — одеяло и ножки."""
    k = sc
    hw = 150 * k           # полуширина
    s = []
    if part == "back":
        hb = rect_pts(x - hw - 6 * k, yb - 470 * k, x + hw + 6 * k, yb - 230 * k, 34 * k)
        s.append(shape(hb, "#9a6436", blob(rect_pts(x + hw * .3, yb - 470 * k, x + hw + 8 * k, yb - 230 * k), "#7e4e28") +
                       line([(x - hw + 30 * k, yb - 440 * k), (x + hw * .2, yb - 444 * k)], 6 * k, "#c08a56", seed=sd + 1, op=.9),
                       w=4.6 * k + 1.4, seed=sd))
        s.append(shape(ellipse_pts(x, yb - 300 * k, 118 * k, 46 * k, 16), "#f7f4ee",
                       blob(ellipse_pts(x + 30 * k, yb - 286 * k, 100 * k, 34 * k, 14), "#dcd8e6"), w=4 * k + 1.2, seed=sd + 2))
        return "".join(s)
    # одеяло: верх-трапеция (дальний край у подушки), передний свес
    top_y, front_y = yb - 300 * k, yb - 120 * k
    bump = 34 * k * mound
    blanket = [(x - hw * .92, top_y + 20 * k), (x - hw * .55, top_y - 4 * k - bump * .6), (x, top_y - 10 * k - bump),
               (x + hw * .55, top_y - 4 * k - bump * .6), (x + hw * .92, top_y + 20 * k), (x + hw * 1.08, front_y, 1),
               (x + hw * 1.04, yb - 40 * k, 1), (x - hw * 1.04, yb - 40 * k, 1), (x - hw * 1.08, front_y, 1)]
    inner = blob([(x - hw * 1.2, front_y), (x + hw * 1.2, front_y), (x + hw * 1.2, yb), (x - hw * 1.2, yb)], "#5f86c8")
    inner += blob([(x + hw * .3, top_y - 40 * k), (x + hw * 1.2, top_y), (x + hw * 1.2, yb), (x + hw * .55, yb)], "#4f72b0", .85)
    for j in range(3):
        inner += line([(x - hw * .7 + j * hw * .7, front_y + 14 * k), (x - hw * .74 + j * hw * .7, yb - 50 * k)], 3 * k + 1, "#41629c",
                      seed=sd + 10 + j, op=.9)
    inner += line([(x - hw * 1.1, front_y), (x + hw * 1.1, front_y)], 3.6 * k + 1, INK, taper=.1, wmin=.8, seed=sd + 14)
    s.append(shape(blanket, "#79a0dc", inner, w=4.6 * k + 1.4, seed=sd + 3))
    for side in (-1, 1):
        lx = x + side * hw * .9
        s.append(shape(rect_pts(lx - 12 * k, yb - 44 * k, lx + 12 * k, yb + 10 * k, 4), "#7e4e28", "", w=3 * k + 1, seed=sd + 5 + side))
    return "".join(s)


def sitter(i, t):
    x, yb, k = BEDS[i]
    spec = dict(SLEEP[i], face=0.0 if i == 2 else (0.25 if i < 2 else -0.25), bw=1.0, h=1.0)
    # опоздание у каждого — доли кадра: «как по команде»
    e = t - UP - 0.02 * abs(i - 2)
    up = 0.0 if e < 0 else min(1.0, spring(e, 2.6, 7.0))
    up = max(0.0, up)
    lie_y = yb - 300 * k + 440 * k       # человек «лежит»: видна только голова на подушке
    sit_y = yb - 300 * k + 270 * k
    y = lie_y + (sit_y - lie_y) * up
    breath = 4 * k * math.sin(t * 2.4 + i) * (1 - min(1, max(0, e) * 4)) if e < 0.3 else 0.0
    awake = e > 0.0
    ra = smooth(UP + 0.12, UP + 0.32, t)          # руки вверх: «бодро!»
    pose = {"no_legs": True, "arms": {"L": (4 - 166 * ra, -10 * ra), "R": (-4 + 166 * ra, 10 * ra)},
            "curl": {"L": 0.9, "R": 0.9},
            "mouth": "smile" if awake else "flat", "blink": 0.0 if awake else 1.0, "brow": .5 if awake else 0.0,
            "head_tilt": (-12 + 4 * i) * (1 - up) + (0 if awake else 3 * math.sin(t * 1.6 + i)), "look": (0, -0.3)}
    if awake and e < 0.25:
        pose["mouth"] = "o"
    return person.draw(spec, pose, x, y + breath, k, 900 + i * 50), up


def zzz(x, y, t, k, i):
    s = []
    for j in range(2):
        ph = (t * 0.9 + j * 0.5 + i * 0.21) % 1.0
        zx, zy = x + 40 * k + ph * 60 * k, y - ph * 140 * k
        sz = (22 + 16 * ph) * k
        op = math.sin(ph * math.pi)
        pts = [(zx - sz / 2, zy - sz / 2), (zx + sz / 2, zy - sz / 2), (zx - sz / 2, zy + sz / 2), (zx + sz / 2, zy + sz / 2)]
        if op > 0.15:
            s.append(line(pts, 6 * k * op + 1, "#fff4c8", taper=.05, wmin=.9, seed=950 + j + i * 3))
    return "".join(s)


def ground2():
    gp = [(-900, 900, 1), (2000, 900, 1), (2000, 2600, 1), (-900, 2600, 1)]
    inner = blob([(-900, 900), (2000, 900), (2000, 960), (-900, 960)], "#4d7a52")
    for k in range(14):
        x = -800 + k * 210
        inner += line([(x, 1030 + (k % 3) * 70), (x + 26, 1010 + (k % 3) * 70), (x + 50, 1030 + (k % 3) * 70)], 4, "#4a7650",
                      seed=1000 + k, op=.9)
    return shape(gp, "#5f9262", inner, w=4.4, seed=1020)


def sun2(t):
    e = t - SUN
    if e < -0.05:
        return ""
    y0, y1 = 980, 405
    u = 0.0 if e < 0 else spring(e, 1.8, 5.5)
    y = y0 + (y1 - y0) * u
    r = 118
    sx = 850
    s = []
    g = rad_grad([(0, "#ffe9a0", .75), (.5, "#ffc86a", .3), (1, "#ffc86a", 0)], sx, y, 520, 520)
    s.append(f'<rect x="-400" y="{f(y - 600)}" width="1900" height="1200" fill="url(#{g})"/>')
    rot = 25 * t
    for j in range(12):
        a = math.radians(rot + j * 30)
        L = (60 + 20 * (j % 2)) * min(1, max(0, e) / 0.15 + 0.01)
        if L > 4:
            s.append(line([(sx + (r + 24) * math.cos(a), y + (r + 24) * math.sin(a)),
                           (sx + (r + 24 + L) * math.cos(a), y + (r + 24 + L) * math.sin(a))], 14, "#ffc94a", taper=.3, wmin=.5,
                          seed=1040 + j))
    s.append(shape(ellipse_pts(sx, y, r, r, 28), "#ffd650", blob(ellipse_pts(sx + 30, y + 30, r, r, 24), "#f5b836", .9) +
                   blob(ellipse_pts(sx - 50, y - 50, 40, 22, 12, rot=-30), "#fff2b0", .9), w=6, seed=1050))
    return "".join(s)


def five(t):
    """Рукописное «5:00» маркером: выскакивает с перелётом на «пять»."""
    e = t - FIVE + 0.04
    if e < 0:
        return ""
    sc = back_pop(e)
    rot = -6 + 4 * math.exp(-e * 6) * math.sin(e * 20)
    strokes = [
        [(-215, -95), (-290, -95), (-298, -10), (-250, -28), (-205, -8), (-188, 40), (-212, 88), (-262, 98), (-300, 74)],
        "dot1", "dot2",
        [(-70, -92), (-112, -70), (-128, 0), (-112, 72), (-70, 96), (-28, 72), (-12, 0), (-28, -70), (-70, -92)],
        [(110, -92), (68, -70), (52, 0), (68, 72), (110, 96), (152, 72), (168, 0), (152, -70), (110, -92)],
    ]
    out_sh, out = [], []
    for j, st in enumerate(strokes):
        if st == "dot1" or st == "dot2":
            yy = -40 if st == "dot1" else 44
            out_sh.append(blob(ellipse_pts(-160 + 6, yy + 6, 15, 15, 10), "#7a1e1a"))
            out.append(blob(ellipse_pts(-160, yy, 15, 15, 10), "#e5372e"))
            continue
        sh = [(p[0] + 7, p[1] + 7) for p in st]
        out_sh.append(line(sh, 30, "#7a1e1a", taper=.12, wmin=.7, seed=1060 + j))
        out.append(line(st, 30, "#e5372e", taper=.12, wmin=.7, seed=1060 + j))
        out.append(line(st[:max(2, len(st) // 2)], 7, "#ff8f7a", taper=.4, wmin=.2, seed=1070 + j))
    # белая подложка-обводка (стикер), чтобы читалось на небе
    halo = []
    for j, st in enumerate(strokes):
        if isinstance(st, str):
            yy = -40 if st == "dot1" else 44
            halo.append(blob(ellipse_pts(-160, yy, 27, 27, 10), "#fffaf0"))
            continue
        halo.append(line(st, 54, "#fffaf0", taper=.0, wmin=1.0, seed=1080 + j))
    return (f'<g transform="translate(400 300) rotate({f(rot)}) scale({sc * 0.88:.4f})">{"".join(halo)}{"".join(out_sh)}{"".join(out)}</g>')


def back_pop(e):
    u = clamp(e / 0.14)
    if u < 1:
        return 0.2 + 1.05 * ease_out(u, 2)
    ee = e - 0.14
    return 1 + 0.25 * math.exp(-ee * 8) * math.cos(ee * 22)


def s02_world(t):
    dawn = smooth(SUN - 0.1, SUN + 0.5, t)
    s = [_ST["sky2"]]
    if dawn > 0:
        s.append(f'<g opacity="{dawn:.3f}">{_ST["sky2b"]}</g>')
    s.append(stars(t, 1 - dawn, 0))
    s.append(sun2(t))
    s.append(_ST["ground2"])
    for i in ORDER:
        x, yb, k = BEDS[i]
        s.append(f'<ellipse cx="{f(x)}" cy="{f(yb + 6)}" rx="{f(180 * k)}" ry="{f(22 * k)}" fill="#2e4a34" opacity=".5"/>')
        s.append(_ST[f"bedb{i}"])
        p, up = sitter(i, t)
        s.append(p)
        s.append(bed(x, yb, k, "front", 820 + i * 20, mound=1 - up))
        if t < UP + 0.05:
            s.append(zzz(x, yb - 300 * k - 60 * k, t, k, i))
        if 0 <= t - UP < 0.3:          # штрихи рывка вверх
            e = t - UP
            for j in (-1, 1):
                xx = x + j * 120 * k
                s.append(line([(xx, yb - 330 * k), (xx, yb - 470 * k)], 8 * k * (1 - e / 0.3) + 1, INK, taper=.5, seed=1100 + i * 4 + j))
    s.append(five(t))
    return "".join(s)


def s02_cam(t):
    v = clamp((t - 1.2) / 2.2)
    sc = 1.0 + 0.07 * ease_io(v)
    cx, cy = 540, 900 - 30 * v
    rot = 0.0
    e = t - FIVE
    if e >= 0:
        k = math.exp(-e * 8)
        sc *= 1 + 0.06 * k * min(1, e / 0.04)
        cy += 8 * k * math.sin(e * 42)
    e = t - UP
    if e >= 0:
        k = math.exp(-e * 9)
        cy += 12 * k * math.sin(e * 38)
        rot += 0.8 * k * math.sin(e * 30)
    return cx, cy, sc, rot


def frame(sid, t):
    if not _ST:
        _ST["sky1"] = sky("#0b1030", "#1f2a66", "#6a4f8e", -1200, 1100)
        _ST["city"] = skyline()
        _ST["sky2"] = sky("#0e1840", "#2c3a7a", "#8a5c8a", -1200, 960)
        _ST["sky2b"] = sky("#6f8fd6", "#f2b38a", "#ffd890", -1200, 960)
        _ST["ground2"] = ground2()
        for i in range(5):
            x, yb, k = BEDS[i]
            _ST[f"bedb{i}"] = bed(x, yb, k, "back", 800 + i * 20)
        lib.static_done()
    lib.dyn_begin()
    _ST["t"] = t
    if sid == "s01":
        body = s01_world(t)
        cx, cy, sc, rot = s01_cam(t)
        bg = "#0b1030"
    else:
        body = s02_world(t)
        cx, cy, sc, rot = s02_cam(t)
        bg = "#0e1840"
    return svg(f'<rect width="{W}" height="{H}" fill="{bg}"/><g transform="{cam(cx, cy, sc, rot)}">{body}</g>')
