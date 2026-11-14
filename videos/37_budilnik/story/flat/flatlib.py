"""Общее сцены flat рилса 37 (s14–s18): утренняя кухня Димы (мир кухни рилса 29 — world.py, Дима — people.py рилса 29),
красная кофеварка на столешнице, тот же будильник, что в clock/ и bed/ (clock/alarm.py соседа, тушь приведена к толщине
мира), кружка, струйка кофе, пар, волны запаха. Камера, тушь от масштаба, удары — помощники отсюда."""
import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import lib  # noqa: E402
import people  # noqa: E402
import world as Wd  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, mix, rect_pts, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def word(w, after=0.0):
    for x in WORDS:
        if x["start"] >= after and x["word"].strip(".,!?").lower().startswith(w):
            return x["start"]
    raise KeyError(w)


# ─────────────────────────── будильник соседа (clock/alarm.py)
_sp = importlib.util.spec_from_file_location("alarm37", os.path.join(STORY, "clock", "alarm.py"))
A37 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(A37)
_INK0 = A37._ink


class _InkK:
    """Обёртка туши будильника: толщина × k (будильник рисуется в своих единицах; в мире кухни он мелкий, и без
    поправки его линия была бы втрое тоньше линии кофеварки рядом)."""
    k = 1.0

    def __getattr__(self, n):
        return getattr(_INK0, n)

    def ink_closed(self, pts, w=5.0, *a, **kw):
        return _INK0.ink_closed(pts, w * self.k, *a, **kw)

    def ink_open(self, pts, w=4.0, *a, **kw):
        return _INK0.ink_open(pts, w * self.k, *a, **kw)


_IK = _InkK()
A37._ink = _IK


def alarm(cx, bottom, size, t=0.0, hh=7.0, mm=0.0, ring=0.0, press=0.0, squash=1.0, rot=0.0, uid="fa"):
    """Будильник ножками на bottom; тушь — как у предметов мира (~4.6 × INK_K)."""
    _IK.k = 200.0 / size * lib.INK_K[0] * 1.0
    cy = bottom - A37.FOOT_Y / 200.0 * size
    s = A37.alarm(cx, cy, size=size, hh=hh, mm=mm, ring=ring, t=t, press=press, squash=squash, rot=rot, uid=uid)
    _IK.k = 1.0
    return s


def alarm_marks(cx, bottom, size, t, amp):
    _IK.k = 200.0 / size * lib.INK_K[0] * 0.8
    cy = bottom - A37.FOOT_Y / 200.0 * size
    s = A37.ring_marks(cx, cy, size, t, amp)
    _IK.k = 1.0
    return s


def alarm_top(cx, bottom, size):
    """Точка кнопки сверху будильника (мир)."""
    cy = bottom - A37.FOOT_Y / 200.0 * size
    return cx, cy - 1.12 * size


# ─────────────────────────── кофеварка (кофеварка рилса 26, в единицах 600×780, ставится масштабом)
MACH_X, MACH_K = 905.0, 0.38          # центр низа кофеварки на столешнице, масштаб
SPOUT_L = (45.0, -312.0)              # носик в единицах кофеварки (от центра низа)
ALARM_X, ALARM_S = 690.0, 56.0        # будильник слева от кофеварки
MUG_K = 0.55
CT = Wd.CT_TOP


def scaled(svg_fn, x, y, k, *a, **kw):
    """Рисунок в своих единицах → мир (сдвиг и масштаб), тушь — толщиной мира."""
    old = lib.INK_K[0]
    lib.INK_K[0] = old / k
    try:
        s = svg_fn(*a, **kw)
    finally:
        lib.INK_K[0] = old
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.4f})">{s}</g>'


def _machine_local(lamp_on=0.0):
    s = []
    body, body_sh = "#c9473d", "#9c3029"
    X0, X1, TOP, BOT = -300, 300, -780, 0
    s.append(blob(rect_pts(X0 + 30, BOT - 20, X1 + 60, BOT + 14), "#1a0e05", .45, lib.blur(12)))
    inner = blob(rect_pts(X1 - 90, TOP, X1 + 10, BOT), body_sh, .9)
    inner += blob(rect_pts(X0, TOP, X1, TOP + 30), mix(body, "#ffffff", .25), .9)
    inner += line([(X0 + 40, TOP + 80), (X0 + 40, BOT - 60)], 10, mix(body, "#ffffff", .35), seed=4011, op=.8, taper=.3)
    s.append(shape(rect_pts(X0, TOP, X1, BOT, 46), body, inner, w=5.4, seed=950))
    s.append(shape(rect_pts(X0 + 70, -360, X1 - 70, BOT - 40, 24), "#2b2730", blob(rect_pts(X0 + 70, -360, X1 - 70, -300), "#1c1920"),
                   w=4.6, seed=951))
    s.append(shape(rect_pts(X0 + 50, -70, X1 - 50, -10, 10), "#9aa0ab",
                   "".join(line([(x, -64), (x, -18)], 3, "#6d737e", taper=.05, wmin=.9, seed=960 + k) for k, x in
                           enumerate(range(X0 + 90, X1 - 60, 36))), w=4.4, seed=961))
    sx = SPOUT_L[0]
    s.append(shape(rect_pts(sx - 90, -360, sx + 90, -328, 8), "#b9bec8", "", w=4, seed=962))
    s.append(shape([(sx - 30, -328, 1), (sx + 30, -328, 1), (sx + 14, SPOUT_L[1] + 2, 1), (sx - 14, SPOUT_L[1] + 2, 1)], "#9aa0ab", "",
                   w=3.6, seed=963))
    for k in range(3):
        y = -670 + k * 82
        s.append(shape(ellipse_pts(180, y, 30, 30, 14), "#f1ece3", blob(ellipse_pts(186, y + 6, 22, 20, 10), "#d4ccbf"), w=3.6, seed=970 + k))
    col = mix("#2e8a4a", "#8dffa8", lamp_on)
    s.append(shape(ellipse_pts(180, -425, 12, 12, 10), col, "", w=2.6, seed=980))
    if lamp_on > .05:
        g = lib.rad_grad([(0, "#9dffb4", .7 * lamp_on), (1, "#9dffb4", 0)], 180, -425, 40, 40)
        s.append(f'<circle cx="180" cy="-425" r="40" fill="url(#{g})"/>')
    return "".join(s)


def machine(lamp_on=0.0):
    return scaled(_machine_local, MACH_X, CT, MACH_K, lamp_on)


def spout():
    return MACH_X + SPOUT_L[0] * MACH_K, CT + SPOUT_L[1] * MACH_K


def mug_pos():
    sx, _ = spout()
    return sx - 6, CT - 10 * MACH_K


def mug(fill=0.0, t=0.0):
    """Кружка под носиком (вид чуть сверху): кофе поднимается fill 0..1."""
    x, y = mug_pos()
    k = MUG_K
    s = [Wd.mug(x, y, k, col="#3f9aa8", hs=1)]
    if fill > 0.02:
        lv = clamp(fill)
        rx = 42 * k * (0.75 + 0.25 * lv)
        cy = y - 128 * k + 6 * k * (1 - lv)
        s.append(blob(ellipse_pts(x, cy, rx, 7 * k, 14), "#5a3218"))
        if lv > .6:
            s.append(blob(ellipse_pts(x - 6 * k, cy - 1, rx * .55, 3.5 * k, 10), "#b9875a", .9))
    return "".join(s)


def mug_top():
    x, y = mug_pos()
    return x, y - 128 * MUG_K


def pour(t, a, b):
    """Струйка из носика в кружку с a по b (начало и конец падают сверху вниз)."""
    if t < a or t > b + 0.12:
        return ""
    sx, sy = spout()
    _, by = mug_top()
    u0 = clamp((t - a) / 0.08)
    u1 = clamp((t - b) / 0.12)
    y0 = sy + (by - sy) * u1
    y1 = sy + (by - sy) * u0
    if y1 - y0 < 2:
        return ""
    wob = 0.8 * math.sin(t * 40)
    return line([(sx + wob, y0), (sx - wob, (y0 + y1) / 2), (sx, y1 + 2)], 6.5, "#5a3218", taper=.15, wmin=.75, seed=995)


def steam(t, t0, k=1.0, n=3, h=150.0):
    """Пар над кружкой: волнистые белые струйки текут вверх, появляются с t0."""
    if t < t0:
        return ""
    a = ease_out(clamp((t - t0) / 0.3))
    x0, y0 = mug_top()
    s = []
    for j in range(n):
        xx = x0 - 18 * k + j * 18 * k
        ph = t * 3.0 + j * 2.1
        pts = []
        for i in range(7):
            v = i / 6
            pts.append((xx + 9 * k * math.sin(ph - v * 5) * (0.4 + v), y0 - 14 * k - h * k * v * a - 4 * j))
        s.append(line(pts, 7 * k * a, "#ffffff", taper=.8, wmin=.15, seed=1500 + j, peak=.35, op=.95))
    return "".join(s)


def aroma(t, t0, target, k=1.0):
    """Волны запаха: три волнистые ленты от кружки к носу (target), бегут за 0.45 с и дальше колышутся."""
    if t < t0:
        return ""
    x0, y0 = mug_top()
    x0, y0 = x0 - 10, y0 - 40
    tx, ty = target
    s = []
    grow = ease_out(clamp((t - t0) / 0.45), 2)
    for j in range(3):
        off = (j - 1) * 16 * k
        pts = []
        n = 14
        for i in range(n + 1):
            v = i / n * grow
            # дуга вверх, к носу
            bx = x0 + (tx - x0) * v
            by = y0 + (ty - y0) * v - 120 * k * math.sin(math.pi * v)
            # волна поперёк
            dx, dy = (tx - x0), (ty - y0) - 120 * k * math.pi * math.cos(math.pi * v)
            L = math.hypot(dx, dy) + 1e-6
            nx, ny = -dy / L, dx / L
            wv = 9 * k * math.sin(v * 16 - t * 9 + j * 1.7)
            pts.append((bx + nx * (wv + off), by + ny * (wv + off)))
        col = ["#e8b98a", "#d79a6a", "#f1cfa6"][j]
        s.append(line(pts, 9 * k, col, taper=.9, wmin=.15, seed=1600 + j, peak=.55, op=.92))
    return "".join(s)


def star(x, y, r, a=0.0, op=1.0):
    """Блик-звёздочка: четыре луча с перетяжкой, светлое ядро."""
    pts = []
    for i in range(8):
        ang = a + i * math.pi / 4
        rr = r if i % 2 == 0 else r * .26
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<g{o}>' + shape(pts, "#fff7cc", blob(ellipse_pts(x, y, r * .2, r * .2, 8), "#ffffff"), w=3.2, seed=2130, var=.1) + "</g>"


# ─────────────────────────── комната
def room(t, clock=(7, 20), jars=True):
    o = [Wd.wall("morning"), Wd.window("morning", t), Wd.clock_wall(clock[0], clock[1], "morning"), Wd.counter(), Wd.floor("morning"),
         Wd.shelf(0.0, 1.0, jars=jars), Wd.cupboard(0.0), Wd.fridge(0.0, magnets=True), Wd.switch(True)]
    return "".join(o)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def compose(bg, objs, cam, front="", screen="", glow=True):
    """bg — стены и мебель (солнечные лучи ложатся на них), objs — предметы и герои ПОВЕРХ света: луч экрана поверх туши
    делал её серой, а будильник — полупрозрачным на вид."""
    cx, cy, s, r = cam
    o = ['<rect width="1080" height="1920" fill="#f0dcb4"/>',
         f'<g transform="{lib.cam(cx, cy, s, r)}">{bg}{Wd.lamp_glow("morning") if glow else ""}{objs}{front}</g>', screen, vignette()]
    return lib.svg("".join(o))


def vignette():
    g = lib.rad_grad([(0, "#2a1408", 0), (.62, "#2a1408", 0), (1, "#2a1408", .32)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def osc(t, f, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def kick(t, t0, k=8.0, f=7.0):
    """Затухающая тряска после удара (−1..1)."""
    e = t - t0
    if e < 0:
        return 0.0
    return math.exp(-e * k) * math.sin(e * 2 * math.pi * f)


def whip_in(t, t0, dur=0.22):
    return 1 - ease_out(clamp((t - t0) / dur), 3)


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


_ = (np, ease_io, smooth, INK, people)
