"""Сцена candy рилса 34 (s13): «съели меньше конфет» (23.2–24.8). Две одинаковые вазочки с конфетами в фантиках на
кремовом фоне; под левой — значок девушки, которую не утешили (грустная), под правой — той, которой сказали «бывает»
(улыбается). Из левой конфеты быстро исчезают одна за другой, вокруг неё растёт гора фантиков; из правой — только две;
на «меньше» (23.68) над правой выскакивает зелёная галочка с ударом. Без букв. Всё — функция общего времени t."""
import math

import numpy as np

import lib
import parts34 as P
import person
import scene_study as SS
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, rect_pts, shape,
                 smooth, svg)

_ST = {}
MENSHE = P.wt("меньше")          # 23.68
VX = (300, 780)
RIM = 760                        # верх чаши
N = 13


def heap():
    """Места конфет в горке над чашей (x от центра, y): снизу вверх; порядок исчезновения — сверху."""
    pts = []
    rows = [(5, RIM - 6, 54), (4, RIM - 44, 54), (3, RIM - 80, 52), (1, RIM - 112, 0)]
    k = 0
    for n, y, dx in rows:
        for i in range(n):
            x = (i - (n - 1) / 2) * dx
            pts.append((x + 6 * math.sin(k * 2.3), y + 4 * math.cos(k * 1.7), -25 + (k * 37) % 50, k % 6))
            k += 1
    return pts


HEAP = heap()
ORDER = list(range(len(HEAP)))[::-1]                       # верхние первыми
T_LEFT = [23.02 + 0.13 * i for i in range(11)]             # левая: 11 из 13
T_RIGHT = [23.2, 23.45]                                    # правая: 2


def vase(x, sd):
    s = []
    s.append(blob(ellipse_pts(x, 1018, 170, 20, 16), "#b9a988", .55, blur(4)))
    s.append(shape(ellipse_pts(x, 1006, 92, 18, 16), "#8fc3e0", blob(ellipse_pts(x + 20, 1010, 70, 10, 12), "#6fa3c4"), w=4, seed=sd))
    s.append(shape(rect_pts(x - 22, 900, x + 22, 1000, 6), "#a9d4ec", blob(rect_pts(x + 6, 900, x + 22, 1000), "#7fb3d6"), w=4, seed=sd + 1))
    bowl = [(x - 152, RIM), (x + 152, RIM), (x + 130, RIM + 66), (x + 80, RIM + 120), (x, RIM + 138), (x - 80, RIM + 120), (x - 130, RIM + 66)]
    inner = blob([(x + 40, RIM), (x + 152, RIM), (x + 130, RIM + 66), (x + 80, RIM + 120), (x + 20, RIM + 138)], "#7fb3d6", .9)
    inner += line([(x - 140, RIM + 30), (x - 100, RIM + 90)], 8, "#e6f4fc", seed=sd + 3, op=.9)
    return "".join(s), shape(bowl, "#a9d4ec", inner, w=4.6, seed=sd + 2) + shape(ellipse_pts(x, RIM, 155, 15, 20), "#cfe8f6", "", w=4, seed=sd + 4)


def face_badge(x, y, spec, mood, t, sd):
    r = 112
    cid = lib.clip_of(ellipse_pts(x, y, r, r, 28))
    pose = {"mouth": "frown" if mood == "sad" else "smile", "brow": -0.7 if mood == "sad" else 0.6,
            "look": (0.0, 0.5 if mood == "sad" else 0.0), "blink": P.bump(t, 23.9 if mood == "sad" else 24.3, 0.14)}
    sp = dict(spec, face=0.0)
    head = f'<g transform="translate({f(x)} {f(y + 14)}) scale(1.05) rotate({f(-6 if mood == "sad" else 4 * math.sin(t * 3))})">{person.face(sp, pose, sd)}</g>'
    bg = "#cfd8e6" if mood == "sad" else "#ffe9a8"
    s = blob(ellipse_pts(x + 8, y + 10, r, r, 28), "#b9a988", .45)
    s += f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="{bg}"/><g clip-path="url(#{cid})">{head}</g>'
    s += f'<path d="{lib.ink_closed(ellipse_pts(x, y, r, r, 28), 5.4, seed=sd + 9)}" fill="{INK}"/>'
    if mood == "sad":
        s += line([(x + 54, y - 4), (x + 58, y + 14)], 5, "#7fc3f0", seed=sd + 11)
    return s


def wrapper_pile(x, n_on, t, times, sd, right=False):
    """Фантики: каждый вылетает из горки в момент исчезновения конфеты и ложится у подножия вазы."""
    rs = np.random.RandomState(sd)
    out = []
    for i, tt in enumerate(times):
        e = t - tt
        if e < 0:
            continue
        side = -1 if i % 2 == 0 else 1
        layer = i // 4
        tx = x + side * (95 + 30 * (i % 4 // 2) - 18 * layer + rs.uniform(-10, 10))
        ty = 1000 - 30 * layer + rs.uniform(-6, 6)
        h = HEAP[ORDER[i]]
        sx, sy = x + h[0], h[1]
        u = clamp(e / 0.35)
        px = sx + (tx - sx) * u
        py = sy + (ty - sy) * u - 160 * math.sin(math.pi * u)
        rot = h[2] + 400 * u * side + rs.uniform(-30, 30) * u
        sc = 0.85 + 0.1 * (1 - u)
        out.append(P.wrapper(px, py, rot, h[3], sd=sd + 10 * i, sc=sc))
    return "".join(out)


def candies(x, t, times, sd):
    gone = {ORDER[i]: tt for i, tt in enumerate(times)}
    s = []
    for k, (hx, hy, rot, ci) in enumerate(HEAP):
        sc = 1.0
        if k in gone:
            e = t - gone[k]
            if e > 0.08:
                continue
            if e > -0.12:
                sc = 1 + 0.25 * math.sin(math.pi * clamp((e + 0.12) / 0.2))
        s.append(P.candy(x + hx, hy - 6 * (sc - 1) * 10, rot, ci, sd=sd + k * 10, sc=0.92 * sc))
    return "".join(s)


def s13(t):
    art = [_ST["bg"]]
    for i, (x, times, spec, mood) in enumerate(((VX[0], T_LEFT, SS.GA, "sad"), (VX[1], T_RIGHT, SS.GB, "happy"))):
        back, front = _ST["vase%d" % i]
        art.append(back)
        art.append(front)
        art.append(candies(x, t, times, 5000 + i * 300))
        art.append(wrapper_pile(x, len(times), t, times, 5200 + i * 300))
        art.append(face_badge(x, 1170, spec, mood, t, 5400 + i * 50))
    # галочка на «меньше»
    e = t - MENSHE
    if e > -0.05:
        k = back_out(clamp((e + 0.05) / 0.25), 2.6)
        prog = clamp((e + 0.05) / 0.2)
        art.append(f'<g transform="translate({VX[1]} 470) scale({f(k)}) translate({-VX[1]} -470)">{P.check(VX[1], 470, 1.5, prog, sd=5600)}</g>')
        art.append(P.pop_lines(VX[1], 470, e, 140, 220, 8, col="#3cbf63", w=9, sd=5610))
    # «гора» у левой: лёгкое покачивание счётчиком — мелкие крошки-искры при каждом фантике
    u = clamp((t - 23.0) / 2.0)
    sc = 1.22 + 0.06 * ease_io(u) + 0.045 * P.kick(t, MENSHE, 6, 14)
    return "".join(art), cam(540, 860, sc, 0.5 - 0.8 * u)


def build_static():
    if _ST:
        return
    s = [f'<rect x="-600" y="-600" width="{W + 1200}" height="{H + 1200}" fill="#f3e9d2"/>']
    for k in range(-6, 30):
        s.append(f'<rect x="-600" y="{-400 + k * 80}" width="{W + 1200}" height="2" fill="#dccaa4" opacity=".7"/>')
    s.append(line([(-600, 1040), (W + 600, 1040)], 3, "#cdb98f", taper=.05, wmin=.8, seed=5001, op=.8))
    _ST["bg"] = "".join(s)
    for i, x in enumerate(VX):
        _ST["vase%d" % i] = vase(x, 5050 + i * 20)
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = s13(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#f3e9d2"/><g transform="{cm}">{art}</g>')
