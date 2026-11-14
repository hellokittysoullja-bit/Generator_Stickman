"""Схемные планы рилса 48 «зубрёжка» (группа C): s05 календарь, s07 голова с улетающими знаниями, s08 мозг, s09 лента повторов,
s10 штамп ВАЖНО, s11 сетка человечков, s12/s13 график забывания, s15 календарь 1/3/7.
frame(sid, t) -> SVG 1080×1920 (t — общее время ролика). Удары — на словах по voice/words.json.
Фон — тетрадный лист (клетка/линейка), тушь — как в кухне (ink.py), надписи кодом шрифтом IDB (как sub/scene_sub.py)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
import people  # noqa: E402
from lib import (INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, fill_d, line, rect_pts, shape, smooth,  # noqa: E402
                 back_out, spring, mix)

SH = json.load(open(os.path.join(os.path.dirname(HERE), "shots.json")))
SHOTS = {s["id"]: s for s in SH["shots"]}
WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, nth=0):
    """Время слова по words.json (nth-е вхождение, поиск по началу без знаков)."""
    k = 0
    for w in WORDS:
        if w["word"].strip(".,:?!").lower() == word.lower():
            if k == nth:
                return w["start"]
            k += 1
    raise KeyError(word)


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def kick(t, th, k=.05, rate=8.0, fr=2.4):
    """Толчок камеры на ударе: быстрый отскок с затуханием."""
    e = t - th
    if e < 0:
        return 0.0
    return k * math.exp(-e * rate) * math.cos(2 * math.pi * fr * e)


# ═════════════════════════ камера, фон, текст ═════════════════════════
def camera(sid, t, s0, s1, c0=(540, 960), c1=(540, 960), hits=(), hk=.05, rot0=0.0, whip=None):
    sh = SHOTS[sid]
    a = max(0.0, sh["t0"] - SH["pad"])
    b = min(sh["t1"] + SH["pad"], SH["end"])
    u = ease_io(clamp((t - a) / max(.01, b - a)))
    s = s0 + (s1 - s0) * u
    cx = c0[0] + (c1[0] - c0[0]) * u
    cy = c0[1] + (c1[1] - c0[1]) * u
    rot = rot0 * (1 - u)
    for th in hits:
        k = kick(t, th, hk)
        s *= 1 + k
        rot += 18 * kick(t, th, hk, fr=3.1) * (1 if int(th * 10) % 2 else -1)
    if sh.get("whip") or whip:
        w = 1 - ease_out(clamp((t - a) / 0.22), 3)
        cx += 360 * w / max(s, .1)
        rot += 2.4 * w
    return cx, cy, s, rot


def start_of(sid):
    return max(0.0, SHOTS[sid]["t0"] - SH["pad"])


def txt(x, y, s, size, fill=INK, anchor="middle", rot=0.0, stroke=None, sw=0, op=1.0):
    st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" paint-order="stroke"' if stroke else ""
    tr = f' transform="rotate({f(rot)} {f(x)} {f(y)})"' if rot else ""
    o = f' opacity="{op:.3f}"' if op != 1 else ""
    return (f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" font-family="IDB" font-weight="900" font-size="{f(size)}" '
            f'fill="{fill}"{st}{tr}{o}>{s}</text>')


def paper(tint="#f6efdc", rule="#d9d2bd", step=64, offx=0.0, offy=0.0, margin=None):
    s = [f'<rect x="-1600" y="-1600" width="4300" height="5200" fill="{tint}"/>']
    o = []
    y0 = -1600 + (offy % step)
    for i in range(int(5200 / step) + 1):
        y = y0 + i * step
        o.append(f'<rect x="-1600" y="{f(y)}" width="4300" height="3" fill="{rule}"/>')
    x0 = -1600 + (offx % step)
    for i in range(int(4300 / step) + 1):
        x = x0 + i * step
        o.append(f'<rect x="{f(x)}" y="-1600" width="3" height="5200" fill="{rule}"/>')
    s.append("".join(o))
    return "".join(s)


def vignette(col="#2a1408", a=.22):
    g = lib.rad_grad([(0, col, 0), (.6, col, 0), (1, col, a)], 540, 960, 1180, 1500)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def compose(sid, t, body, cam_, tint="#f6efdc", rule="#d9d2bd", drift=True, over=""):
    cx, cy, s, r = cam_
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62
    off = t * 14 if drift else 0
    out = (f'<rect width="1080" height="1920" fill="{tint}"/>'
           f'<g transform="{lib.cam(cx, cy, s, r)}">{paper(tint, rule, 64, off, off * .6)}{body}</g>{over}{vignette()}')
    return lib.svg(out)


def ring(cx, cy, r, w, col, seed=1, op=1.0):
    outer = ellipse_pts(cx, cy, r + w / 2, r + w / 2, 18, jitter=.012, seed=seed)
    inner = ellipse_pts(cx, cy, max(1, r - w / 2), max(1, r - w / 2), 18, jitter=.012, seed=seed + 1)
    o = f' opacity="{op:.3f}"' if op != 1 else ""
    return f'<path d="{fill_d(outer)}{fill_d(inner)}" fill="{col}" fill-rule="evenodd"{o}/>'


def star(cx, cy, r, a=0.0, n=8, col="#ffd84a", sd=1, inner=.45, w=3.4):
    pts = []
    for i in range(n * 2):
        ang = a + i * math.pi / n
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang), 1))
    return shape(pts, col, "", w=w, seed=sd, var=.1)


def check(cx, cy, k, col="#2f9e4f", w=14, sd=5, prog=1.0):
    pts = [(cx - 26 * k, cy + 2 * k), (cx - 8 * k, cy + 22 * k), (cx + 30 * k, cy - 24 * k)]
    if prog < 1:
        if prog <= 0:
            return ""
        if prog < .4:
            u = prog / .4
            pts = [pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * u, pts[0][1] + (pts[1][1] - pts[0][1]) * u)]
        else:
            u = (prog - .4) / .6
            pts = [pts[0], pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * u, pts[1][1] + (pts[2][1] - pts[1][1]) * u)]
    return line(pts, w * k, col, taper=.2, wmin=.55, seed=sd, peak=.5)


def cross(cx, cy, k, col="#d8382e", w=12, sd=5, prog=1.0):
    a = [(cx - 30 * k, cy - 30 * k), (cx + 30 * k, cy + 30 * k)]
    b = [(cx + 30 * k, cy - 30 * k), (cx - 30 * k, cy + 30 * k)]
    o = ""
    if prog > 0:
        u = clamp(prog / .5)
        o += line([a[0], (a[0][0] + (a[1][0] - a[0][0]) * u, a[0][1] + (a[1][1] - a[0][1]) * u)], w * k, col, taper=.2, wmin=.6, seed=sd)
    if prog > .5:
        u = clamp((prog - .5) / .5)
        o += line([b[0], (b[0][0] + (b[1][0] - b[0][0]) * u, b[0][1] + (b[1][1] - b[0][1]) * u)], w * k, col, taper=.2, wmin=.6, seed=sd + 1)
    return o


def arrowhead(p, q, size, col, sd):
    """Треугольник наконечника в точке q по направлению p→q."""
    d = np.array(q, float) - np.array(p, float)
    d /= np.linalg.norm(d) + 1e-9
    n = np.array([-d[1], d[0]])
    tip = np.array(q, float) + d * size * .5
    a = tip - d * size + n * size * .55
    b = tip - d * size - n * size * .55
    return shape([tuple(tip) + (1,), tuple(a) + (1,), tuple(b) + (1,)], col, "", w=3.2, seed=sd, var=.1)


def curve_arrow(p0, p1, bend, prog, col=INK, w=11, sd=10, head=36):
    """Дуга p0→p1 (изгиб bend по нормали), нарисована на долю prog; наконечник на конце."""
    if prog <= 0:
        return ""
    p0 = np.array(p0, float)
    p1 = np.array(p1, float)
    m = (p0 + p1) / 2
    d = p1 - p0
    n = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9)
    c = m + n * bend
    pts = []
    N = 22
    for i in range(N + 1):
        u = i / N * clamp(prog)
        q = (1 - u) ** 2 * p0 + 2 * (1 - u) * u * c + u * u * p1
        pts.append((float(q[0]), float(q[1])))
    o = line(pts, w, col, taper=.25, wmin=.5, seed=sd, peak=.55)
    if prog >= .98:
        o += arrowhead(pts[-3], pts[-1], head, col, sd + 1)
    return o


# ═════════════════════════ мозг-мультяшка ═════════════════════════
PINK, PINK_SH, PINK_HI = "#f2a3b6", "#d97b95", "#f9c7d2"


def brain_outline(n=13, rx=300, ry=225, amp=.05):
    pts = []
    for i in range(n * 2):
        th = -math.pi / 2 + i * math.pi / n
        r = 1 + (amp if i % 2 == 0 else -amp * .9)
        x, y = rx * r * math.cos(th), ry * r * math.sin(th)
        if y > 0:
            y *= .86
        pts.append((x, y))
    return pts


def brain_eye(cx, cy, rx, ry, look, blink, sd):
    lx, ly = look
    k = 1 - .93 * blink
    ep = ellipse_pts(cx, cy, rx, ry * k, 14)
    cid = lib.clip_of(ep)
    px, py = cx + rx * .42 * lx, cy + ry * .4 * ly * k
    inner = (f'<ellipse cx="{f(px)}" cy="{f(py)}" rx="17" ry="{f(19 * max(.35, k))}" fill="{INK}"/>'
             f'<circle cx="{f(px - 6)}" cy="{f(py - 7 * k)}" r="5.2" fill="#ffffff"/>')
    return (f'<g><path d="{fill_d(ep)}" fill="#fbf8f1"/><g clip-path="url(#{cid})">{inner}</g></g>'
            + f'<path d="{lib.ink_closed(ep, 5.2 * lib.INK_K[0], seed=sd)}" fill="{INK}"/>')


def brain(cx, cy, k=1.0, t=0.0, look=(0.0, 0.0), blink=0.0, mood="neutral", sx=1.0, sy=1.0, rot=0.0, glow=0.0, sd=0, sweat=0.0):
    """Мозг с глазами, центр (cx, cy), масштаб k. mood: neutral / think / wow / proud / sleepy / hurt."""
    s = []
    stem = [(40, 150, 1), (120, 160), (150, 250), (100, 300, 1), (30, 280), (10, 200)]
    s.append(shape(stem, PINK_SH, "", w=5, seed=3001 + sd))
    ol = brain_outline()
    inner = blob([(-330, -260), (-80, -270), (-60, -120), (-200, -60), (-330, 40)], PINK_HI, .85)
    inner += blob([(330, 300), (330, 40), (200, 60), (130, 170), (30, 260)], PINK_SH, .55)
    for j, ln in enumerate([[(-250, -20), (-205, -95), (-150, -70), (-120, -135)],
                            [(-275, 70), (-225, 112), (-185, 78), (-195, 130)],
                            [(-160, -170), (-135, -125), (-95, -150)],
                            [(250, -20), (205, -95), (150, -70), (120, -135)],
                            [(275, 70), (225, 112), (185, 78), (195, 130)],
                            [(160, -170), (135, -125), (95, -150)],
                            [(-70, 195), (-10, 170), (60, 190)]]):
        inner += line(ln, 7, "#b95b78", taper=.3, wmin=.4, seed=3010 + j + sd, peak=.5)
    inner += line([(0, -230), (-16, -190), (8, -160), (-10, -120), (4, -92)], 7, "#b95b78", taper=.3, wmin=.4, seed=3030 + sd)
    s.append(shape(ol, PINK, inner, w=6, seed=3002 + sd))
    # лицо
    s.append(blob(ellipse_pts(-168, 62, 34, 20, 10), "#ee7f93", .55))
    s.append(blob(ellipse_pts(168, 62, 34, 20, 10), "#ee7f93", .55))
    blk = blink
    if mood == "proud":
        for ex in (-88, 88):
            s.append(line([(ex - 52, 4), (ex - 24, -34), (ex + 24, -34), (ex + 52, 4)], 11, INK, taper=.3, wmin=.5, seed=3040 + ex))
    else:
        wide = 1.14 if mood in ("wow", "hurt") else 1.0
        s.append(brain_eye(-88, -8, 58 * wide, 66 * wide, look, blk, 3050 + sd))
        s.append(brain_eye(88, -8, 58 * wide, 66 * wide, look, blk, 3051 + sd))
    br = {"think": ([(-140, -96), (-88, -112), (-40, -84)], [(40, -96), (88, -112), (140, -84)]),
          "wow": ([(-140, -118), (-88, -134), (-40, -118)], [(40, -118), (88, -134), (140, -118)]),
          "hurt": ([(-140, -84), (-88, -108), (-40, -130)], [(40, -130), (88, -108), (140, -84)]),
          "sleepy": ([(-140, -80), (-88, -84), (-40, -78)], [(40, -78), (88, -84), (140, -80)]),
          "neutral": ([(-140, -100), (-88, -112), (-40, -100)], [(40, -100), (88, -112), (140, -100)]),
          "proud": ([(-140, -92), (-88, -104), (-40, -100)], [(40, -100), (88, -104), (140, -92)])}[mood]
    s.append(line(br[0], 8, INK, taper=.4, wmin=.5, seed=3060 + sd) + line(br[1], 8, INK, taper=.4, wmin=.5, seed=3061 + sd))
    my = 112
    if mood in ("wow", "hurt"):
        s.append(shape(ellipse_pts(0, my + 10, 26, 26 if mood == "wow" else 18, 12), "#7a2f3d", blob(ellipse_pts(0, my + 22, 16, 9, 8), "#e0707f"),
                       w=5, seed=3070 + sd))
    elif mood == "proud":
        s.append(shape([(-48, my - 10), (-20, my + 20), (20, my + 20), (48, my - 10, 1), (30, my + 2), (-30, my + 2)], "#7a2f3d",
                       blob([(-20, my + 8), (20, my + 8), (14, my + 20), (-14, my + 20)], "#f4ede0"), w=5, seed=3071 + sd))
    elif mood == "think":
        s.append(line([(-34, my + 6), (-12, my - 6), (12, my + 8), (34, my - 4)], 7, INK, taper=.3, wmin=.5, seed=3072 + sd))
    else:
        s.append(line([(-32, my), (0, my + 12), (32, my)], 7, INK, taper=.3, wmin=.5, seed=3073 + sd))
    if sweat > 0:
        sy_ = -90 + 80 * sweat
        s.append(shape([(262, sy_ - 50), (282, sy_ - 10), (276, sy_ + 14), (256, sy_ + 14), (248, sy_ - 10)], "#bfe6fa",
                       blob([(256, sy_ - 8), (266, sy_ - 12), (262, sy_ + 6)], "#ffffff"), w=4, seed=3080 + sd))
    g = ""
    if glow > 0:
        g = ring(0, 0, 340 + 40 * glow, 14, "#ffd84a", seed=3090 + sd)
    tr = f'translate({f(cx)} {f(cy)}) rotate({f(rot)}) scale({f(k * sx)} {f(k * sy)})'
    return f'<g transform="{tr}">{g}{"".join(s)}</g>'


# ═════════════════════════ s05: календарь листается ═════════════════════════
DAYS = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА", "ВОСКРЕСЕНЬЕ"]
DAY_SH = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]


def cal_page(x, y, w, h, n, col="#ffffff", sd=0, num_col=INK, extra=""):
    """Лист отрывного календаря: верхний край (x+w/2, y) — на спирали. n — номер дня."""
    s = []
    inner = blob([(x, y + h - 36), (x + w, y + h - 36), (x + w, y + h), (x, y + h)], "#e3dccb")
    inner += blob([(x, y), (x + w, y), (x + w, y + 120), (x, y + 120)], "#d8382e")
    s.append(shape(rect_pts(x, y, x + w, y + h, 26), col, inner, w=6, seed=4100 + sd))
    s.append(txt(x + w / 2, y + 82, "НЕДЕЛЯ", 62, "#ffffff"))
    s.append(txt(x + w / 2, y + 480, str(n), 400, num_col))
    s.append(txt(x + w / 2, y + h - 90, DAYS[n - 1], 54 if n != 7 else 46, "#4a4458"))
    s.append(extra)
    return "".join(s)


def s05(t):
    x, y, w, h = 190, 250, 700, 790
    flips = [6.2 + .1 * i for i in range(6)]        # листы 1..6 срываются один за другим
    land = wt("неделю")                              # 6.76
    # какой лист сверху сейчас
    cur = 1 + sum(1 for ft in flips if t >= ft + .06)
    s = []
    # пружина-блокнот (подложка и стопка листов сзади)
    s.append(shape(rect_pts(x + 14, y + 22, x + w + 14, y + h + 24, 26), "#b8ae99", "", w=5, seed=4090))
    s.append(shape(rect_pts(x + 6, y + 12, x + w + 6, y + h + 14, 26), "#d9d0ba", "", w=5, seed=4091))
    pg = cal_page(x, y, w, h, cur, sd=cur)
    # ударная посадка седьмого листа
    if cur == 7:
        e = t - land
        pop = 1 + .07 * math.exp(-max(0, e) * 9) * math.cos(max(0, e) * 24) if e >= 0 else 1
        extra_r = ring(x + w / 2, y + 340, 170 * smooth(0, .25, e) + 1, 14, "#d8382e", seed=4120) if e > 0.05 else ""
        pg = (f'<g transform="translate({f(x + w / 2)} {f(y)}) scale({f(pop)}) translate({f(-(x + w / 2))} {f(-y)})">'
              + cal_page(x, y, w, h, 7, sd=7) + extra_r + "</g>")
    s.append(pg)
    # улетающие листы
    for i, ft in enumerate(flips):
        e = t - ft
        if e < 0 or e > .45:
            continue
        u = ease_in(e / .45, 1.8)
        px = -1100 * u
        py = 380 * u - 120 * math.sin(u * math.pi)
        ang = -42 * u
        n = i + 1
        s.append(f'<g transform="translate({f(px)} {f(py)}) rotate({f(ang)} {f(x + w / 2)} {f(y)})">'
                 + cal_page(x, y, w, h, n, sd=n + 20) + "</g>")
    # спираль
    for i in range(9):
        rx_ = x + 50 + i * (w - 100) / 8
        s.append(shape(rect_pts(rx_ - 14, y - 40, rx_ + 14, y + 30, 14), "#7b7f93", blob([(rx_ + 2, y - 40), (rx_ + 14, y - 40), (rx_ + 14, y + 30), (rx_ + 2, y + 30)], "#5b5f70"),
                       w=4, seed=4200 + i))
    # полоска недели снизу: дни зачёркиваются по мере листания
    sx0, sy0, cw = 130, 1110, 120
    for d in range(7):
        bx = sx0 + d * cw
        done = d < cur - 1
        fc = "#f1e3df" if done else ("#fff3c4" if d == 6 else "#ffffff")
        s.append(shape(rect_pts(bx + 6, sy0, bx + cw - 6, sy0 + 108, 14), fc, "", w=4.4, seed=4300 + d))
        s.append(txt(bx + cw / 2, sy0 + 70, DAY_SH[d], 44, "#4a4458" if not done else "#a79c98"))
        if done:
            pr = clamp((t - (flips[d] + .06)) / .18)
            s.append(cross(bx + cw / 2, sy0 + 54, 1.1, "#d8382e", 11, 4400 + d, pr))
    if cur == 7:
        s.append(ring(sx0 + 6 * cw + cw / 2, sy0 + 54, 62 * smooth(land, land + .25, t) + 1, 8, "#d8382e", seed=4500))
    cam_ = camera("s05", t, 1.0, 1.1, (540, 960), (540, 900), hits=(land,), hk=.045)
    return compose("s05", t, "".join(s), cam_, tint="#f6efdc")


# ═════════════════════════ s07: голова Димы, знания улетают ═════════════════════════
TILES = [("E=mc2", "#ffd98a", -1.3), ("1812", "#bfe3a8", 1.0), ("ABC", "#a9d4f2", -.6), ("2+2", "#f6b3c4", 1.4),
         ("H2O", "#d4c2f0", -1.0), ("a=b", "#ffc9a0", .7), ("XIV", "#b8ece0", -1.5), ("%", "#f2e88f", 1.2)]


def bust(t, expr, ang, hip=(330, 1800), scale=1.9):
    people.C = people.PAL["dima"]
    pose = dict(hip=hip, scale=scale, lean=0.05, feet=None, pelvis=True, arms={"n": ("ang", .25, .4), "f": ("ang", .1, .3)},
                hands={"n": dict(kind="open"), "f": dict(kind="open")}, expr=expr, head_ang=ang, hood=0.0,
                strings=(3 * osc(t, 1.3), 2 * osc(t, 1.1, 1)))
    d = people.draw(pose, "dima")
    return d.get("pelvis", "") + d["arm_f"] + d["body"] + d["arm_n"], d["head"]


def s07(t):
    a_out = wt("выученное")                           # 10.16
    t_end = wt("исчезает")                            # 12.0
    n = len(TILES)
    # вылет: i-й квадрат покидает облако в t_i, последний остаётся (дрожит)
    gap = (t_end - a_out - .15) / (n - 1)
    leave = [a_out + i * gap * (1 if i < n - 1 else 99) for i in range(n)]
    leave[n - 1] = 99
    # лёгкое покачивание головы, взгляд вверх на облако, брови тревожно
    prog = smooth(a_out, t_end, t)
    expr = dict(lid=.75, look=(.55, -.55 + .3 * prog), brows="worry" if prog < .6 else "up", mouth="flat" if prog < .5 else "tired",
                closed=(1.0 if (t % 2.6) < .12 else 0.0))
    body, head = bust(t, expr, -.05 + .03 * osc(t, .8) + .05 * prog)
    cl_cx, cl_cy = 690, 300
    wob = 1 + .015 * osc(t, 1.1)
    # облако мыслей: большое, с хвостом из кружков к голове
    cloud = []
    for i, (dx, dy, r) in enumerate([(-250, 0, 105), (-130, -60, 120), (10, -88, 130), (150, -60, 120), (255, 0, 105), (180, 70, 100),
                                     (40, 90, 110), (-100, 80, 100)]):
        cloud.append(ellipse_pts(cl_cx + dx * wob, cl_cy + dy * wob, r, r * .92, 16, jitter=.0))
    cp = ""
    for pts in cloud:
        cp += fill_d(pts)
    cl = f'<path d="{cp}" fill="#ffffff" fill-rule="nonzero"/>'
    # контур облака — объединение кругов нельзя обвести тушью без двойных линий, поэтому контур — одна гладкая кривая по внешним дугам
    outl = []
    N = 64
    for i in range(N):
        th = 2 * math.pi * i / N
        rr = 1.0
        # суперформула «облака»: бугры по краю
        bumps = 1 + .13 * math.cos(th * 8 + .4)
        outl.append((cl_cx + 330 * bumps * math.cos(th) * wob, cl_cy + 135 * bumps * math.sin(th) * wob * rr))
    cloud_shape = shape(outl, "#ffffff", blob(ellipse_pts(cl_cx - 40, cl_cy - 30, 230, 70, 14), "#eef3fb"), w=6, seed=5001)
    trail = ""
    hx, hy = head
    for j, (fx, fy, r) in enumerate([(.0, .0, 34), (.25, .22, 24), (.5, .42, 15)]):
        px = 560 + (cl_cx - 140 - 560) * (1 - fx) * 0 + (0)  # placeholder, перезапись ниже
    for j, (px, py, r) in enumerate([(560, 470, 36), (520, 540, 26), (498, 596, 17)]):
        trail += shape(ellipse_pts(px, py + 3 * osc(t, 1.2, j), r, r, 12), "#ffffff", "", w=5, seed=5010 + j)
    tiles = []
    nleft = 0
    for i, (tx, col, rot0) in enumerate(TILES):
        gx = cl_cx - 215 + (i % 4) * 142
        gy = cl_cy - 55 + (i // 4) * 110
        px = gx + 7 * osc(t, 1.3, i)
        py = gy + 8 * osc(t, 1.1, i * 1.7)
        e = t - leave[i]
        if e < 0:
            tw = 2 * osc(t * 3, 1, i) if i == n - 1 and t > a_out else 0
            sc, rr = 1.0, rot0 * 4 + 3 * osc(t, .9, i) + tw
            ox, oy = 0, 0
            nleft += 1
        else:
            u = e / .75
            if u >= 1:
                continue
            ox = (420 + 60 * i) * ease_in(u, 2.2) * (1 if i % 2 == 0 else 1.1)
            oy = -(560 + 40 * i) * ease_in(u, 2.0) * .9 + 90 * math.sin(u * math.pi)
            sc = 1 - .85 * ease_in(u, 1.5)
            rr = rot0 * 4 + 380 * u * (1 if i % 2 == 0 else -1)
        tile = (f'<g transform="translate({f(px + ox)} {f(py + oy)}) rotate({f(rr)}) scale({f(sc)})">'
                + shape(rect_pts(-62, -42, 62, 42, 14), col, "", w=4.6, seed=5100 + i)
                + txt(0, 15, tx, 42 if len(tx) < 5 else 36, INK) + "</g>")
        tiles.append(tile)
        if 0 < e < .3:
            tiles.append(star(px + ox, py + oy, 30 * (1 - e / .3) + 6, e * 6, 8, "#ffe27a", 5200 + i))
    # пустые места: пунктиром тень ушедшего не рисуем; рядом — счётчик «осталось»
    meter_x, meter_y = 950, 1010
    left = sum(1 for i in range(n) if t < leave[i])
    meter = shape(rect_pts(meter_x - 20, meter_y - 160, meter_x + 20, meter_y + 20, 10), "#ffffff", "", w=4.4, seed=5300)
    fill_h = 180 * left / n
    meter += shape(rect_pts(meter_x - 20, meter_y + 20 - fill_h, meter_x + 20, meter_y + 20, 10), "#7bc67e" if left > 3 else "#e8695a", "", w=4.4, seed=5301)
    meter += txt(meter_x, meter_y - 190, "ЗНАНИЯ", 36, "#4a4458")
    sweat = ""
    if t > t_end - .5:
        u = clamp((t - t_end + .5) / 1.0)
        sweat = shape([(650, 700 + 40 * u), (672, 750 + 40 * u), (666, 778 + 40 * u), (642, 778 + 40 * u), (634, 750 + 40 * u)], "#bfe6fa",
                      blob([(645, 752 + 40 * u), (656, 748 + 40 * u), (652, 770 + 40 * u)], "#ffffff"), w=4, seed=5310)
    bodyall = body + sweat + trail + cloud_shape + "".join(tiles) + meter
    cam_ = camera("s07", t, 1.0, 1.14, (540, 960), (560, 760), hits=(a_out, t_end), hk=.035)
    return compose("s07", t, bodyall, cam_, tint="#e9f0f8", rule="#cfd9e6")


# ═════════════════════════ s08: мозг входит, пульс на «вспомнить» ═════════════════════════
def ekg(x0, x1, y, t, beats, amp=130, prog_t=None, sd=1, col="#2f9e4f"):
    """Кардиограмма: плоская линия со всплесками на моментах beats; бежит слева направо — виден хвост за текущим временем."""
    pts = []
    N = 120
    for i in range(N + 1):
        x = x0 + (x1 - x0) * i / N
        tt = t - (x1 - x) / (x1 - x0) * 1.2          # время, когда точка линии «возникла»
        v = 0.0
        for b in beats:
            d = tt - b
            if -.02 < d < .34:
                v += -amp * (math.exp(-((d - .06) / .035) ** 2) * 1.0) + amp * .45 * math.exp(-((d - .14) / .05) ** 2) - amp * .2 * math.exp(-((d - .27) / .06) ** 2)
        v += 6 * math.sin(tt * 9 + i * .5) * (1 if tt < beats[0] else .2)
        pts.append((x, y + v))
    return line(pts, 9, col, taper=.15, wmin=.7, seed=sd, peak=.5)


def s08(t):
    land = wt("Мозгу")
    t_rem = wt("вспомнить")
    t0 = start_of("s08")
    # падение сверху с приземлением ровно на land
    fall_dur = land - t0
    u = clamp((t - t0) / fall_dur)
    y_final = 700
    y = -420 + (y_final + 420) * ease_in(u, 2.1)
    sx = sy = 1.0
    if t >= land:
        e = t - land
        sy = 1 - .26 * math.exp(-e * 9) * math.cos(e * 22)
        sx = 1 + .18 * math.exp(-e * 9) * math.cos(e * 22)
        y = y_final
    else:
        sy = 1 + .1 * u
        sx = 1 - .05 * u
    # пульс на вспомнить
    beats = [t_rem, t_rem + .5, t_rem + 1.0]
    pk = 0.0
    for b in beats:
        pk = max(pk, bump(t, b, .26))
    mood = "think" if t < t_rem else "wow"
    lk = (.4 * osc(t, .7), -.5 + .15 * osc(t, 1.1)) if t < t_rem else (0, 0)
    blink = 1.0 if (t % 2.2) < .1 and t > land + .3 else 0.0
    s = []
    # полка/пятно под мозгом
    s.append(blob(ellipse_pts(540, 1030, 340, 40, 20), "#c7bbd8"))
    s.append(brain(540, y, .96 * (1 + .06 * pk), t, look=lk, blink=blink, mood=mood if t > land else "neutral", sx=sx, sy=sy,
                   rot=2.5 * osc(t, 1.4) * (1 if t < t_rem else 0) - 3 * pk, glow=pk if t >= t_rem else 0))
    # «…» мысли до вспомнить
    if land + .15 < t < t_rem + .05:
        for j in range(3):
            on = (t * 3 + j * .7) % 3 < 2.2
            r = 17 + 5 * bump(t, land + .3 + j * .35, .4)
            s.append(shape(ellipse_pts(780 + j * 52, 420 - j * 40, r, r, 10), "#ffffff", "", w=4.4, seed=5500 + j))
        s.append(txt(942, 330, "?", 120, "#8d6fc9", rot=10, stroke="#ffffff", sw=10))
    # пульс-линия в экране под мозгом
    if t > land:
        s.append(shape(rect_pts(150, 1100, 930, 1250, 18), "#16202a", "", w=6, seed=5600))
        s.append(f'<g clip-path="url(#{lib.clip_rect(160, 1108, 760, 134, 12)})">' + ekg(170, 920, 1180, t, beats if t >= t_rem else [99], 56, sd=5601) + "</g>")
    # звёздочки/волны пульса
    for b in beats:
        e = t - b
        if 0 <= e < .5:
            r = 330 + 260 * ease_out(e / .5)
            s.append(ring(540, 700, r, 12 * (1 - e / .5) + 2, "#ffd84a", seed=5700 + int(b * 10)))
    cam_ = camera("s08", t, 1.0, 1.1, (540, 960), (540, 840), hits=(land, t_rem), hk=.04)
    return compose("s08", t, "".join(s), cam_, tint="#f1e9f6", rule="#dccfe6")


# ═════════════════════════ s09: лента повторов ═════════════════════════
def s09(t):
    t_gap = wt("перерывами")                           # 15.6
    flashes = [14.66, 15.06, 15.42]
    LX = [210, 540, 870]
    ly = 720
    s = []
    off = (t * 120) % 120
    # лента времени: линия со стрелкой и бегущими делениями
    s.append(shape(rect_pts(40, ly + 120, 1040, ly + 190, 30), "#e6dcc6", "", w=5, seed=5800))
    for i in range(-1, 10):
        xx = 40 + i * 120 + off * 0 - ((t * 140) % 120) + 120
        if 60 < xx < 1020:
            s.append(line([(xx, ly + 135), (xx, ly + 175)], 6, INK, taper=.1, wmin=.8, seed=5810 + i))
    s.append(arrowhead((1000, ly + 155), (1060, ly + 155), 56, INK, 5890))
    # промежутки подсвечиваются
    gp = smooth(t_gap, t_gap + .3, t)
    for j in range(2):
        x0 = LX[j] + 100
        x1 = LX[j + 1] - 100
        if gp > 0:
            wob = 1 + .06 * math.sin(t * 8 + j)
            hgt = 330 * gp
            s.append(shape(rect_pts(x0, ly + 160 - hgt, x1, ly + 160, 22), "#cfe8fb" if j == 0 else "#d8f0cf", "", w=5, seed=5900 + j))
            # песочные часы внутри
            hx, hy = (x0 + x1) / 2, ly + 160 - hgt / 2
            if gp > .6:
                k = (gp - .6) / .4
                top = [(hx - 42, hy - 66), (hx + 42, hy - 66), (hx + 6, hy - 4, 1), (hx + 6, hy + 4, 1), (hx + 42, hy + 66), (hx - 42, hy + 66), (hx - 6, hy + 4, 1), (hx - 6, hy - 4, 1)]
                s.append(shape(top, "#ffffff", blob([(hx - 30, hy + 60), (hx + 30, hy + 60), (hx + 8, hy + 20 + 20 * (1 - k)), (hx - 8, hy + 20 + 20 * (1 - k))], "#f0b84a"),
                               w=4.4, seed=5910 + j))
                s.append(txt(hx, hy + 120, "ПЕРЕРЫВ", 38, "#4a4458", rot=-2 * wob))
    # три мини-мозга со вспышками
    for i, (fx, ft) in enumerate(zip(LX, flashes)):
        e = t - ft
        pk = bump(t, ft, .3)
        awake = e >= 0
        bsc = .27 + .05 * pk
        s.append(brain(fx, ly - 40, bsc, t, look=(.3 * osc(t, .8, i), -.2), blink=1.0 if (t * 1.0 + i * .5) % 1.7 < .1 else 0.0,
                       mood="wow" if 0 <= e < .45 else ("proud" if awake else "sleepy"), rot=4 * pk * (1 if i % 2 else -1), sd=i * 40))
        s.append(shape(ellipse_pts(fx, ly + 130, 56, 12, 12), "#d9cfbc", "", w=0, ink=False))
        # номер повтора
        nb = (f'<g transform="translate({fx} {ly - 270 + 2 * osc(t, 1.2, i)}) scale({1 + .2 * pk})">'
              + shape(ellipse_pts(0, 0, 50, 50, 14), "#ffd84a" if awake else "#ece5d3", "", w=5.2, seed=6000 + i)
              + txt(0, 24, str(i + 1), 72, INK if awake else "#a79c98") + "</g>")
        s.append(nb)
        if 0 <= e < .5:
            u = e / .5
            for k in range(10):
                ang = k * 36 + i * 11
                r0 = 140 + 170 * ease_out(u)
                r1 = r0 + 70 * (1 - u)
                a_ = math.radians(ang)
                s.append(line([(fx + r0 * math.cos(a_), ly - 40 + r0 * math.sin(a_)), (fx + r1 * math.cos(a_), ly - 40 + r1 * math.sin(a_))], 11 * (1 - u) + 3,
                              "#ffb81f", taper=.5, wmin=.3, seed=6050 + k + i * 20))
    s.append(txt(540, 330, "ПОВТОР", 120, INK, stroke="#ffffff", sw=14, rot=-2))
    s.append(txt(540, 440, "ПАУЗА   ПОВТОР   ПАУЗА", 44, "#6b6280"))
    cam_ = camera("s09", t, 1.04, 1.04, (540, 960), (540, 960), hits=(flashes[0], flashes[1], flashes[2], t_gap), hk=.03)
    return compose("s09", t, "".join(s), cam_, tint="#f4f0e4", rule="#ddd6c2")


# ═════════════════════════ s10: наклейка ВАЖНО ═════════════════════════
def s10(t):
    land = wt("важно")                               # 17.48
    t0 = start_of("s10")
    s = []
    mood = "think" if t < land - .15 else ("wow" if t < land + .25 else "proud")
    # взгляд следит за наклейкой
    ux = clamp((t - t0) / (land - t0))
    lk = (-.6 + 1.1 * ux, -.6 + .3 * ux)
    pk = bump(t, land, .4)
    s.append(blob(ellipse_pts(540, 1010, 340, 40, 20), "#c7bbd8"))
    s.append(brain(540, 700, .96 * (1 - .05 * pk), t, look=lk if t < land else (0, 0), blink=1.0 if (t % 2.4) < .1 else 0.0, mood=mood,
                   sx=1 + .08 * pk, sy=1 - .1 * pk, rot=-4 * pk + 2 * osc(t, .9)))
    # три галочки-повтора слева сверху (из прошлых повторов)
    for i in range(3):
        ct = t0 + .15 + i * .35
        pr = clamp((t - ct) / .3)
        s.append(f'<g transform="translate({150 + i * 90} {400})">' + shape(ellipse_pts(0, 0, 36, 36, 12), "#ffffff", "", w=4.4, seed=6200 + i)
                 + check(0, 0, .8, "#2f9e4f", 12, 6210 + i, pr) + "</g>")
    # наклейка прилетает по дуге и шлёпается на лоб/лобную долю мозга
    sx0, sy0 = 1260, 120
    tx_, ty_ = 640, 520                              # точка посадки
    u = clamp((t - t0) / (land - t0))
    e_ = ease_in(u, 1.6) * .6 + ease_out(u, 2.2) * .4
    px = sx0 + (tx_ - sx0) * e_ + 0
    py = sy0 + (ty_ - sy0) * e_ - 220 * math.sin(u * math.pi) * (1 - u * .3)
    rot = 28 * (1 - e_) - 8
    sc = 1.55 - .55 * e_
    if t >= land:
        e = t - land
        px, py, rot, sc = tx_, ty_, -8 + 3 * math.exp(-e * 8) * math.cos(e * 26), 1.0 + .16 * math.exp(-e * 12) * math.cos(e * 20)
    stk = (f'<g transform="translate({f(px)} {f(py)}) rotate({f(rot)}) scale({f(sc)})">'
           + shape([(-190, -78), (190, -82), (194, 74), (-186, 80)], "#ffe14a",
                   blob([(-190, 44), (194, 40), (194, 74), (-186, 80)], "#f2c21f") + blob([(150, -82), (190, -82), (194, 74), (160, 74)], "#ffeb7a", .6),
                   w=6, seed=6300)
           + txt(0, 34, "ВАЖНО", 104, "#d8382e", stroke="#ffffff", sw=0) + "</g>")
    s.append(stk)
    # вспышка при посадке
    e = t - land
    if 0 <= e < .55:
        u2 = e / .55
        for k in range(12):
            ang = math.radians(k * 30 + 8)
            r0 = 150 + 190 * ease_out(u2)
            s.append(line([(tx_ + r0 * math.cos(ang), ty_ + r0 * math.sin(ang)), (tx_ + (r0 + 80 * (1 - u2)) * math.cos(ang), ty_ + (r0 + 80 * (1 - u2)) * math.sin(ang))],
                          12 * (1 - u2) + 3, "#d8382e", taper=.5, wmin=.3, seed=6400 + k))
        s.append(ring(tx_, ty_, 240 * ease_out(u2), 12 * (1 - u2) + 2, "#ffd84a", seed=6420))
    if t >= land + .1:
        for j, (sx_, sy_, r) in enumerate([(300, 460, 38), (820, 920, 30), (240, 860, 26)]):
            k = bump(t, land + .1 + j * .08, .6)
            s.append(star(sx_, sy_, r * (.6 + k * .6), t * 1.2 + j, 4, "#ffd84a", 6430 + j, inner=.35))
    s.append(txt(540, 1160, "ЗНАЧИТ, ВАЖНО", 64, "#6b6280") if t > land + .35 else "")
    cam_ = camera("s10", t, 1.0, 1.09, (540, 960), (580, 800), hits=(land,), hk=.05)
    return compose("s10", t, "".join(s), cam_, tint="#f1e9f6", rule="#dccfe6")


# ═════════════════════════ s11: сетка человечков, волна галочек ═════════════════════════
def s11(t):
    t_hit = wt("сотни")                              # 18.96
    cols, rows = 12, 22
    dx, dy = 88, 112
    gx0, gy0 = 540 - (cols - 1) * dx / 2, 960 - (rows - 1) * dy / 2 - 120
    cen = (540, 700)
    pal = ["#f2a3b6", "#a9d4f2", "#bfe3a8", "#ffd98a", "#d4c2f0", "#ffc9a0", "#b8ece0"]
    s = []
    for r in range(rows):
        for c in range(cols):
            x = gx0 + c * dx + (dx / 2 if r % 2 else 0)
            y = gy0 + r * dy
            if x < -80 or x > 1160:
                continue
            dist = math.hypot(x - cen[0], (y - cen[1]) * .8)
            ft = t_hit + dist / 1000 * .9
            e = t - ft
            on = e >= 0
            bob = 5 * math.sin(t * 5 + (c * 7 + r * 3) % 6) * (0 if on else 1) - (14 * math.exp(-e * 9) * abs(math.cos(e * 18)) if on and e < .5 else 0)
            col = pal[(c * 3 + r * 5) % len(pal)] if on else "#d9d2c0"
            sd = 7000 + r * 40 + c
            body = [(x - 28, y + 40, 1), (x - 26, y + 6), (x - 12, y - 6), (x + 12, y - 6), (x + 26, y + 6), (x + 28, y + 40, 1)]
            yy = y + bob
            s.append(shape([(a, b + bob) + ((1,) if len(p) > 2 else ()) for p in body for a, b in [(p[0], p[1])]], col, "", w=3.6, seed=sd))
            s.append(shape(ellipse_pts(x, yy - 28, 21, 21, 10), "#f3d9bf" if on else "#e8e1d0", "", w=3.6, seed=sd + 1))
            if on:
                k = ease_out(clamp(e / .25)) * (1 + .3 * math.exp(-e * 7))
                s.append(shape(ellipse_pts(x + 24, yy - 56, 15 * k, 15 * k, 8), "#ffffff", "", w=2.8, seed=sd + 2) + check(x + 24, yy - 56, .36 * k, "#2f9e4f", 11, sd + 3))
    # волна: ударное кольцо
    e = t - t_hit
    over = ""
    if 0 <= e < .9:
        r = 1300 * ease_out(e / .9, 2)
        over = ring(cen[0], cen[1], r, 26 * (1 - e / .9) + 3, "#2f9e4f", seed=7900)
    # плашка «СОТНИ»
    pop = back_out(clamp((t - t_hit) / .3), 2.2) if t >= t_hit else 0.0
    tag = ""
    if pop > 0:
        tag = (f'<g transform="translate(540 330) rotate(-3) scale({f(pop)})">'
               + shape(rect_pts(-370, -92, 370, 92, 30), "#ffd84a", "", w=7, seed=7950)
               + txt(0, 36, "СОТНИ РАЗ", 124, INK) + "</g>")
    cam_ = camera("s11", t, 1.42, 1.0, (540, 760), (540, 960), hits=(t_hit,), hk=.03)
    return compose("s11", t, "".join(s) + over + tag, cam_, tint="#eef2ea", rule="#d6dccd", drift=False)


# ═════════════════════════ s12 / s13: график забывания ═════════════════════════
GX0, GX1, GY0, GY1 = 150, 960, 1000, 330           # x слева→справа; y низ (0 %), верх (100 %)
REV = [.18, .42, .70]


def gx(x):
    return GX0 + (GX1 - GX0) * x


def gy(v):
    return GY0 + (GY1 - GY0) * v


def green_v(x):
    xs = [0.0] + REV
    ks = [3.4, 2.1, 1.1, .32]
    last = max(i for i, r in enumerate(xs) if x >= r - 1e-9)
    return math.exp(-ks[last] * (x - xs[last]))


def red_v(x):
    return math.exp(-6.2 * x)


def curve_pts(fn, x_end, N=140, jumps=()):
    pts = []
    xs = sorted(set([i / N for i in range(int(N * x_end) + 1)] + [x_end]))
    for x in xs:
        if x > x_end:
            break
        for j in jumps:
            if abs(x - j) < .5 / N and x > 0:
                pts.append((gx(j - 1e-4), gy(fn(j - 1e-4))))
        pts.append((gx(x), gy(fn(x))))
    return pts


def graph_base(t, sid):
    s = []
    # оси
    s.append(shape(rect_pts(GX0 - 60, GY1 - 70, GX1 + 60, GY0 + 60, 24), "#ffffff", "", w=5, seed=8000))
    for k in range(1, 5):
        v = k / 4
        s.append(line([(GX0, gy(v)), (GX1, gy(v))], 3, "#d9d2bd", taper=.05, wmin=.95, seed=8010 + k))
    s.append(line([(GX0, GY1 - 30), (GX0, GY0)], 8, INK, taper=.1, wmin=.8, seed=8020))
    s.append(line([(GX0, GY0), (GX1 + 20, GY0)], 8, INK, taper=.1, wmin=.8, seed=8021))
    s.append(arrowhead((GX0, GY1 + 20), (GX0, GY1 - 38), 34, INK, 8022))
    s.append(arrowhead((GX1 - 20, GY0), (GX1 + 40, GY0), 34, INK, 8023))
    s.append(txt(GX0 + 4, GY1 - 52, "ПОМНЮ", 44, "#4a4458", anchor="start"))
    s.append(txt(GX1 + 40, GY0 + 52, "ВРЕМЯ", 44, "#4a4458", anchor="end"))
    for v, lb in ((1, "100%"), (.5, "50%"), (0, "0")):
        s.append(txt(GX0 - 16, gy(v) + 14, lb, 32, "#6b6280", anchor="end"))
    return "".join(s)


def hit_ring(cx, cy, e, col, sd, r_max=120):
    if not (0 <= e < .5):
        return ""
    u = e / .5
    return ring(cx, cy, r_max * ease_out(u), 12 * (1 - u) + 2, col, seed=sd)


def s12(t):
    t_hold = wt("держится")                           # 21.28
    t0 = start_of("s12")
    s = [graph_base(t, "s12")]
    x_end = clamp((t - t0 - .1) / (t_hold - t0 - .1))
    pts = curve_pts(green_v, x_end, jumps=REV)
    if len(pts) > 2:
        s.append(line(pts, 15, "#2f9e4f", taper=.15, wmin=.8, seed=8100, peak=.5))
    # отметки повторов на уже пройденных местах
    for i, r in enumerate(REV):
        if x_end >= r:
            e = t - (t0 + (r / .62) * (t_hold - t0 + .15) ** 1.0 * 0)    # без привязки к слову: только выскакивает
            pop = back_out(clamp((x_end - r) / .06), 2.2)
            cx_, cy_ = gx(r), gy(0) - 24
            s.append(f'<g transform="translate({f(cx_)} {f(cy_)}) scale({f(pop)})">' + shape(ellipse_pts(0, 0, 32, 32, 12), "#ffd84a", "", w=4.4, seed=8200 + i)
                     + txt(0, 14, str(i + 1), 40, INK) + "</g>")
            s.append(line([(gx(r), gy(0) - 58), (gx(r), gy(green_v(r)) + 14)], 4, "#9aa0ab", taper=.1, wmin=.8, seed=8210 + i, op=.9))
    # кончик кривой — кружок
    tip = pts[-1] if pts else (gx(0), gy(1))
    s.append(shape(ellipse_pts(tip[0], tip[1], 20, 20, 12), "#ffffff", "", w=5, seed=8300) + shape(ellipse_pts(tip[0], tip[1], 9, 9, 8), "#2f9e4f", "", w=0, ink=False))
    # плашка «С ПЕРЕРЫВАМИ»
    pill_k = back_out(clamp((t - (t0 + .15)) / .3), 2)
    s.append(f'<g transform="translate({gx(.52)} {GY1 - 120}) scale({f(pill_k)})">' + shape(rect_pts(-230, -48, 230, 48, 30), "#2f9e4f", "", w=6, seed=8400)
             + txt(0, 20, "С ПЕРЕРЫВАМИ", 56, "#ffffff") + "</g>")
    # на «держится»: высоко держится — стрелка/подсветка конца и надпись
    if t >= t_hold:
        e = t - t_hold
        s.append(hit_ring(gx(1), gy(green_v(1)), e, "#2f9e4f", 8500, 130))
        bk = back_out(clamp(e / .3), 2.2)
        s.append(f'<g transform="translate({gx(.80)} {gy(green_v(1)) - 120}) rotate(-4) scale({f(bk)})">' + shape(rect_pts(-210, -54, 210, 54, 28), "#ffd84a", "", w=6, seed=8510)
                 + txt(0, 22, "ДЕРЖИТСЯ!", 70, INK) + "</g>")
    cam_ = camera("s12", t, 1.0, 1.12, (540, 960), (620, 740), hits=(t_hold,), hk=.04)
    return compose("s12", t, "".join(s), cam_, tint="#eef4ea", rule="#d6e0cf")


def s13(t):
    t_cliff = wt("присест")                           # 24.16
    t0 = start_of("s13")
    s = [graph_base(t, "s13")]
    # зелёная кривая уже построена; чуть «дышит» кончиком
    gp = curve_pts(green_v, 1.0, jumps=REV)
    # красная кривая: «ночь» — висит наверху, потом падает
    dur_hang = t_cliff - t0 - .15
    u_r = clamp((t - t0) / (t_cliff - t0 + .75))
    # прогресс по x: к моменту t_cliff ещё только 0.06; потом резкий обвал
    if t < t_cliff:
        x_end = .07 * ease_io(clamp((t - t0) / (t_cliff - t0)))
    else:
        e = t - t_cliff
        x_end = .07 + .93 * ease_out(clamp(e / .55), 2.2)
    # разница между кривыми — заливка (после обвала)
    red = curve_pts(red_v, x_end, N=160)
    if t >= t_cliff + .3:
        n = 80
        top = [(gx(i / n), gy(green_v(i / n))) for i in range(n + 1)]
        bot = [(gx(i / n), gy(red_v(i / n))) for i in range(n, -1, -1)]
        k = smooth(t_cliff + .3, t_cliff + .75, t)
        s.append(f'<g opacity="{.9 * k:.3f}"><path d="{fill_d(top + bot)}" fill="#fff0b0"/></g>')
    if len(gp) > 2:
        s.append(line(gp, 15, "#2f9e4f", taper=.15, wmin=.8, seed=8100, peak=.5))
    for i, r in enumerate(REV):
        s.append(shape(ellipse_pts(gx(r), gy(0) - 24, 26, 26, 12), "#ffd84a", "", w=4.2, seed=8200 + i) + txt(gx(r), gy(0) - 10, str(i + 1), 34, INK))
    if len(red) > 2:
        s.append(line(red, 15, "#d8382e", taper=.15, wmin=.8, seed=8600, peak=.5))
    tip = red[-1] if red else (gx(0), gy(1))
    s.append(shape(ellipse_pts(tip[0], tip[1], 20, 20, 12), "#ffffff", "", w=5, seed=8601) + shape(ellipse_pts(tip[0], tip[1], 9, 9, 8), "#d8382e", "", w=0, ink=False))
    # плашки
    pk = back_out(clamp((t - (t0 + .1)) / .3), 2)
    s.append(f'<g transform="translate({gx(.52)} {GY1 - 120}) scale({f(pk)})">' + shape(rect_pts(-230, -48, 230, 48, 30), "#2f9e4f", "", w=6, seed=8400)
             + txt(0, 20, "С ПЕРЕРЫВАМИ", 56, "#ffffff") + "</g>")
    pk2 = back_out(clamp((t - (t0 + .5)) / .3), 2)
    s.append(f'<g transform="translate({gx(.24)} {gy(.58)}) rotate(-5) scale({f(pk2)})">' + shape(rect_pts(-250, -48, 250, 48, 30), "#d8382e", "", w=6, seed=8610)
             + txt(0, 20, "ЗА ОДНУ НОЧЬ", 56, "#ffffff") + "</g>")
    # обвал: тряска, «!»
    if t >= t_cliff:
        e = t - t_cliff
        s.append(hit_ring(gx(.14), gy(red_v(.14)), e, "#d8382e", 8700, 140))
        if e < .6:
            bk = back_out(clamp(e / .25), 2.4)
            s.append(f'<g transform="translate({gx(.30)} {gy(.22)}) rotate(8) scale({f(bk)})">' + txt(0, 0, "ОБВАЛ!", 100, "#d8382e", stroke="#ffffff", sw=14) + "</g>")
    if t >= t_cliff + .8:
        e = t - t_cliff - .8
        bk = back_out(clamp(e / .35), 2.2)
        pxm = gx(.75)
        a, b = gy(green_v(.75)) + 12, gy(red_v(.75)) - 12
        s.append(f'<g opacity="{clamp(e / .2):.2f}">' + line([(pxm, a), (pxm, b)], 8, INK, taper=.1, wmin=.8, seed=8710) + arrowhead((pxm, b - 40), (pxm, a), 30, INK, 8711)
                 + arrowhead((pxm, a + 40), (pxm, b), 30, INK, 8712) + "</g>")
        s.append(f'<g transform="translate({pxm - 190} {(a + b) / 2 + 14}) scale({f(bk)})">' + txt(0, 0, "РАЗНИЦА", 54, "#6b6280") + "</g>")
    cam_ = camera("s13", t, 1.06, 1.0, (620, 760), (540, 800), hits=(t_cliff,), hk=.05)
    return compose("s13", t, "".join(s), cam_, tint="#f6ece6", rule="#e6d6cb")


# ═════════════════════════ s15: календарь 1 / 3 / 7 ═════════════════════════
def s15(t):
    t1, t3, t7 = wt("день", 1) if False else 27.92, 29.04, 29.88
    t0 = start_of("s15")
    cw, ch = 236, 290
    gx0, gy0 = 540 - 2 * cw, 330
    cells = {}
    s = []
    # блокнотная «шапка»
    s.append(shape(rect_pts(gx0 - 30, gy0 - 120, gx0 + 4 * cw + 30, gy0 + 2 * ch + 30, 30), "#ffffff", "", w=6, seed=9000))
    s.append(blob(rect_pts(gx0 - 30, gy0 - 120, gx0 + 4 * cw + 30, gy0 - 20), "#d8382e", 1.0))
    s.append(shape(rect_pts(gx0 - 30, gy0 - 120, gx0 + 4 * cw + 30, gy0 + 2 * ch + 30, 30), "none", "", w=6, seed=9001))
    s.append(txt(540, gy0 - 44, "ПОВТОРЫ", 74, "#ffffff"))
    marks = {1: t1, 3: t3, 7: t7}
    cols_ = {1: "#bfe3a8", 3: "#a9d4f2", 7: "#ffd98a"}
    for d in range(8):
        r, c = divmod(d, 4)
        x, y = gx0 + c * cw, gy0 + r * ch
        cells[d] = (x + cw / 2, y + ch / 2)
        mt = marks.get(d)
        e = t - mt if mt else -1
        done = mt is not None and e >= 0
        fc = cols_[d] if done else ("#fff7d6" if d == 0 else "#f6f1e4")
        pop = 1.0
        if done:
            pop = 1 + .09 * math.exp(-e * 8) * math.cos(e * 22)
        s.append(f'<g transform="translate({f(x + cw / 2)} {f(y + ch / 2)}) scale({f(pop)}) translate({f(-(x + cw / 2))} {f(-(y + ch / 2))})">'
                 + shape(rect_pts(x + 8, y + 8, x + cw - 8, y + ch - 8, 18), fc, "", w=5, seed=9100 + d))
        lab = "СЕГОДНЯ" if d == 0 else ""
        s.append(txt(x + cw / 2, y + 120, str(d), 130, INK if (d == 0 or done) else "#b3a995"))
        if lab:
            s.append(txt(x + cw / 2, y + 190, lab, 38, "#4a4458"))
            # книжка
            s.append(shape(rect_pts(x + cw / 2 - 44, y + 208, x + cw / 2 + 44, y + 262, 8), "#d8382e", blob([(x + cw / 2 + 30, y + 208), (x + cw / 2 + 44, y + 208), (x + cw / 2 + 44, y + 262), (x + cw / 2 + 30, y + 262)], "#f4e9d0"),
                           w=4, seed=9200))
        if done:
            pr = clamp(e / .3)
            s.append(check(x + cw / 2, y + 222, 1.25, "#2f9e4f", 14, 9300 + d, pr))
            lbl = {1: "ЧЕРЕЗ ДЕНЬ", 3: "ЧЕРЕЗ 3 ДНЯ", 7: "ЧЕРЕЗ НЕДЕЛЮ"}[d]
            s.append(txt(x + cw / 2, y + 180, lbl.split(" ", 1)[0] if d != 3 else "ЧЕРЕЗ", 36, "#4a4458") if False else "")
        s.append("</g>")
        # вспышка
        if mt and 0 <= e < .45:
            u = e / .45
            s.append(star(x + cw / 2, y + ch / 2, 130 * ease_out(u) + 40, e * 5, 10, "#ffd84a", 9400 + d, inner=.6) if u < .5 else "")
            s.append(ring(x + cw / 2, y + ch / 2, 110 + 130 * ease_out(u), 12 * (1 - u) + 2, "#2f9e4f", seed=9410 + d))
    # стрелки 0→1→3→7
    seq = [(0, 1, t1 - .22, t1, -50), (1, 3, t3 - .4, t3, -90), (3, 7, t7 - .4, t7, 60)]
    for k, (a, b, ts, te, bend) in enumerate(seq):
        pr = clamp((t - ts) / (te - ts))
        s.append(curve_arrow(cells[a], cells[b], bend, ease_out(pr, 1.5), "#4a4458", 12, 9500 + k * 5))
    # подписи «через …» под таблицей
    labels = [("ЧЕРЕЗ ДЕНЬ", t1, 410, "#6fae4d"), ("ЧЕРЕЗ 3 ДНЯ", t3, 540, "#3f86c4"), ("ЧЕРЕЗ НЕДЕЛЮ", t7, 670, "#c98a14")]
    for tx, tt, xx, col in labels:
        e = t - tt
        if e >= 0:
            bk = back_out(clamp(e / .28), 2.2)
            yy = {410: 1010, 540: 1085, 670: 1160}[xx]
            s.append(f'<g transform="translate(540 {yy}) scale({f(bk)})">' + shape(rect_pts(-250, -38, 250, 38, 24), col, "", w=5.4, seed=9600 + xx) + txt(0, 20, tx, 52, "#ffffff") + "</g>")
    cam_ = camera("s15", t, 1.0, 1.04, (540, 880), (540, 880), hits=(t1, t3, t7), hk=.05)
    return compose("s15", t, "".join(s), cam_, tint="#f4f0e4", rule="#ddd6c2")


FN = {"s05": s05, "s07": s07, "s08": s08, "s09": s09, "s10": s10, "s11": s11, "s12": s12, "s13": s13, "s15": s15}


def frame(sid, t):
    del lib.DEFS[:]
    lib._uid[0] = 0
    return FN[sid](t)
