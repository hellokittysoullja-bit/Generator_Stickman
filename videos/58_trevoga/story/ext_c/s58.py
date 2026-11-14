"""Рилс 58 «тревога», группа C: s07 s09 s11 s12 s16 s17. frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Герои — people.py/cat.py/hand.py (Дима и кот рилсов 55–56, кот с нейтральной шерстью как look/hero.png), стакан, бутылка и миска — только
из ../common/props.py (общие для групп A, B, C)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import cat as Cat  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import students as ST  # noqa: E402
from lib import (INK, back_out, blob, blur, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rrect, shape,  # noqa: E402,F401
                 smooth, spring)

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def dima(hip, bs, lean, arms, hands, expr, feet=None, head_ang=0.0, head_off=(0, 0), torso_k=1.0, who="dima"):
    p = dict(hip=tuple(hip), scale=bs, lean=lean, torso_k=torso_k, feet=feet, arms=arms, hands=hands, expr=expr, head_ang=head_ang,
             head_off=head_off, hood=0.0, strings=(0, 0))
    return people.draw(p, who)


def open_hand(c=.2, d=(1, 0), spread=.2, thumb=.2, flip=1, k=1.0):
    return dict(kind="open", flip=flip, dir=d, curl=(c, c, c, c * .9), spread=spread, thumb=thumb, bend=.1, k=k)


def cstate(t, **kw):
    st = dict(look=(0, 0), turn=0.0, blink=0.0, ear=0, perk=0.0, tail=0.0, smile=0, tilt=0, flame_e=1.0)
    st.update(kw)
    return st


def blink_of(t, times, dur=.14):
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            return math.sin(math.pi * u)
    return 0.0


def sparks(t, fx, fy, n=7, seed=11, rise=120):
    rs = np.random.RandomState(seed)
    o = []
    for i in range(n):
        per = rs.uniform(.9, 1.5)
        ph = rs.uniform(0, per)
        u = ((t + ph) % per) / per
        o.append(f'<circle cx="{fx + rs.uniform(-14, 14) + 18 * math.sin(u * 5 + i):.1f}" cy="{fy - rise * u - 12:.1f}" r="{4 * (1 - u) + 1:.1f}" fill="#ffd070"/>')
    return "".join(o)


def zig(x, y, ang, L, w=7, seed=0, col=INK, n=4, amp=14):
    a = math.radians(ang)
    d = np.array([math.cos(a), math.sin(a)])
    nn = np.array([-d[1], d[0]])
    pts = [(x, y)] + [(x + d[0] * L * (i + 1) / n + nn[0] * amp * (1 if i % 2 == 0 else -1),
                       y + d[1] * L * (i + 1) / n + nn[1] * amp * (1 if i % 2 == 0 else -1)) for i in range(n)]
    return line(pts, w, col, taper=.5, wmin=.25, seed=seed)


def partial(pts, u, step=4.0):
    if u <= 0:
        return []
    P = lib.sample(pts, False, step)
    n = max(2, int(len(P) * min(u, 1.0)))
    return [tuple(p_) for p_ in P[:n]]


# ═════════════════════════════ рукописное «кот»: одно перо, слитный курсив ═════════════════════════════
_HW = {}


def _cr(pts, step=2.4):
    """Catmull-Rom через точки, равномерно по длине."""
    P = np.array(pts, float)
    P = np.vstack([P[0] * 2 - P[1], P, P[-1] * 2 - P[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        n = max(3, int(np.linalg.norm(p2 - p1) / step))
        for s in np.linspace(0, 1, n, endpoint=False):
            out.append(.5 * (2 * p1 + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    out.append(P[-2])
    return np.array(out)


def _arc(cx, cy, rx, ry, a0, a1, n=16):
    """Дуга овала: углы в градусах (0 — вправо, 90 — вверх), a1 > a0 — против часовой на экране."""
    return [(cx + rx * math.cos(math.radians(a)), cy - ry * math.sin(math.radians(a))) for a in np.linspace(a0, a1, n)]


def kot_strokes():
    """Слово «кот» строчными, курсивом, одной непрерывной линией (как пишут не отрывая пера): петля-стойка «к» с косой ручкой, «о» с
    входным и выходным соединением, «т» с тремя дугами («m»). Наклон вправо ~17°, буквы разной высоты (о ниже, к выше, т ниже), базовая
    линия ползёт вверх, в конце росчерк-подчёркивание отдельным штрихом. Координаты: y вниз, база y=0, x-высота ≈ 96."""
    if "s" in _HW:
        return _HW["s"]
    rs = np.random.RandomState(58)
    k = [(-18, -4), (-4, -36), (8, -84), (18, -122), (24, -134), (22, -112), (16, -66), (11, -26), (10, 4)]          # петля вверх, стойка вниз
    k += [(16, -22), (30, -42), (46, -66), (58, -82), (66, -88), (60, -74), (46, -56), (30, -40), (20, -28)]       # косая ручка: вверх и обратно к стойке
    k += [(30, -20), (44, -8), (56, 2), (66, 0), (78, -14), (90, -34)]                                              # нога и выходной штрих
    o = _arc(124, -44, 28, 46, 80, 80 + 380, 20)
    k += [(100, -66)] + [(x, y) for x, y in o[1:]] + [(150, -66), (166, -50)]
    k += [(172, -38), (176, -10), (184, 3), (190, -26), (198, -70), (208, -92), (220, -82), (222, -40), (224, -6), (232, 3), (240, -30), (248, -72), (260, -92),
          (272, -82), (274, -40), (276, -6), (284, 3), (302, -8), (322, -26)]
    pts = []
    for x, y in k:
        sc = 1.0 if x < 100 else (.93 if x < 170 else .96)
        pts.append((x - y * .30 + rs.normal(0, 1.1), y * sc + rs.normal(0, 1.1) - .045 * x))
    S1 = _cr(pts)
    S2 = _cr([(-14, 26), (60, 30), (160, 26), (240, 14), (318, 0)])                                       # подчёркивание-росчерк
    _HW["s"] = [S1, S2]
    return _HW["s"]


def _width(P, base=22.0):
    """Нажим: широкая линия на нисходящих и тонкая на восходящих (перо под наклоном), плавно по длине, дрожь руки."""
    d = np.gradient(P, axis=0)
    ang = np.arctan2(d[:, 1], d[:, 0])
    nib = math.radians(62)
    w = .38 + .62 * np.abs(np.sin(ang - nib))
    n = len(P)
    u = np.linspace(0, 1, n)
    w *= .3 + .7 * np.minimum(1, np.minimum(u * 18, (1 - u) * 10) ** .8)
    k = np.convolve(np.random.RandomState(n).normal(0, 1, n + 16), np.ones(17) / 17, "valid")[:n]
    w = np.convolve(np.pad(w, 4, mode="edge"), np.ones(9) / 9, "valid")
    return base * np.clip(w * (1 + .3 * k), .22, 1.0)


def _band_path(P, W):
    d = np.gradient(P, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
    N = np.stack([-d[:, 1], d[:, 0]], 1)
    Lp = P + N * (W / 2)[:, None]
    Rp = P - N * (W / 2)[:, None]
    pts = [tuple(p) for p in Lp] + [tuple(p) for p in Rp[::-1]]
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


def marker_svg(tip, ang_deg, ln=300, col="#3d6f8c"):
    a = math.radians(ang_deg)
    d = np.array([math.cos(a), math.sin(a)])
    n = np.array([-d[1], d[0]])
    T = np.array(tip, float)
    w = 30
    nib = [tuple(T), tuple(T + d * 38 + n * w * .3), tuple(T + d * 38 - n * w * .3)]
    o = lib.shape([q + (1,) for q in nib], "#2a2a34", "", w=3, seed=8801)
    body = [tuple(T + d * 38 + n * w * .5) + (1,), tuple(T + d * ln + n * w * .5) + (1,), tuple(T + d * ln - n * w * .5) + (1,), tuple(T + d * 38 - n * w * .5) + (1,)]
    sh = blob([tuple(T + d * 38 - n * w * .1), tuple(T + d * ln - n * w * .1), tuple(T + d * ln - n * w * .5), tuple(T + d * 38 - n * w * .5)], mix(col, "#000000", .2), .9)
    o += shape(body, col, sh, w=3.6, seed=8802)
    o += shape([tuple(T + d * 38 + n * w * .5) + (1,), tuple(T + d * 92 + n * w * .5) + (1,), tuple(T + d * 92 - n * w * .5) + (1,), tuple(T + d * 38 - n * w * .5) + (1,)],
               "#f0efe8", "", w=3.2, seed=8803)
    return o


def write_kot(t, t0, x0, y0, size=1.0, dur=(.78, .16), col="#1c1622"):
    """«кот» пишется пером с t0: слитная линия с нажимом, фломастер едет за остриём; после — упругий хлопок и искры."""
    S = kot_strokes()
    if t < t0 - .02:
        return ""
    o = []
    tt = t0
    tip = None
    for si, P in enumerate(S):
        a, b = tt, tt + dur[si]
        tt = b + (.06 if si == 0 else 0)
        u = clamp((t - a) / (b - a))
        u = ease_io(u) * .35 + u * .65
        if u <= 0:
            continue
        n = max(2, int(len(P) * u))
        Q = P[:n] * size + np.array([x0, y0])
        Wd = _width(P, 13.5 * size if si == 0 else 8.0 * size)[:n]
        o.append(f'<path d="{_band_path(Q, Wd)}" fill="{col}"/>')
        for e in (0, -1):
            if (e == 0 or u >= 1.0) and n > 2:
                c = Q[e]
                o.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{Wd[e] / 2:.1f}" fill="{col}"/>')
        if u < 1 and n > 3:
            tip = (Q[-1], Q[-1] - Q[-3])
    done = tt
    if tip and t < done:
        o.append(marker_svg(tuple(tip[0]), 55 + 6 * math.sin(t * 20)))
    e = t - done
    sc = 1.0
    cx_, cy_ = x0 + 150 * size, y0 - 50 * size
    if 0 < e < .5:
        sc = 1 + .05 * math.exp(-e * 9) * math.sin(min(e * 14, math.pi))
        for kk in range(9):
            a_ = kk * .7 + .2
            ez = ease_out(clamp(e / .45))
            o.append(f'<circle cx="{cx_ + (210 * size + 30) * math.cos(a_) * (.55 + .45 * ez):.1f}" '
                     f'cy="{cy_ + (110 * size + 40) * math.sin(a_) * (.6 + .4 * ez):.1f}" r="{max(.5, 8 * (1 - e / .5)):.1f}" fill="#ffd070"/>')
    return f'<g transform="translate({cx_:.1f} {cy_:.1f}) scale({sc:.4f}) translate({-cx_:.1f} {-cy_:.1f})">{"".join(o)}</g>'


# ═════════════════════════════ общий фон ═════════════════════════════
def qmark(x, y, s, seed=0, col=INK, w=9.0, op=1.0):
    pts = [(-20, -22), (-6, -40), (16, -36), (22, -16), (10, 2), (0, 14), (0, 26)]
    P = [(x + px * s, y + py * s) for px, py in pts]
    return line(P, w * s ** .5, col, taper=.35, wmin=.5, seed=7700 + seed, op=op) + blob(ellipse_pts(x, y + 50 * s, 5.5 * s, 5.8 * s, 8), col, op)


def room_blur(t):
    """Размытая комната дня: окно с мягким светом слева, полка и подоконник справа, пол. Всё в блюре (стойка — съёмка кота крупно)."""
    o = [blob(rrect(-300, -300, 1700, 1500), "#efe2c6"), blob(rrect(-300, 1180, 1700, 2400), "#cfa070")]
    g = ""
    g += blob(rrect(-60, 160, 420, 760, 16), "#bfe0f2") + blob(ellipse_pts(150, 420, 120, 40, 12), "#ffffff", .85)
    g += blob(rrect(-90, 130, -50, 790), "#fdf8ec") + blob(rrect(400, 130, 440, 790), "#fdf8ec") + blob(rrect(-60, 440, 420, 470), "#fdf8ec")
    g += blob(rrect(660, 430, 1200, 470), "#a87b47") + blob(rrect(700, 220, 800, 430, 10), "#6d8f7a") + blob(rrect(820, 290, 940, 430, 10), "#b9553f") \
        + blob(rrect(960, 250, 1030, 430, 10), "#d6b24a")
    g += blob(rrect(640, 960, 1150, 1010), "#a87b47") + blob(ellipse_pts(780, 920, 70, 56, 12), "#7aa064") + blob(rrect(740, 940, 820, 1010, 8), "#c8794a")
    g += blob(ellipse_pts(300, 1400, 420, 120, 18), "#e8d3a0", .8)
    o.append(f'<g {blur(14)}>{g}</g>')
    return "".join(o)


def sparks(t, fx, fy, n=7, seed=11, rise=120):
    rs = np.random.RandomState(seed)
    o = []
    for i in range(n):
        per = rs.uniform(.9, 1.5)
        ph = rs.uniform(0, per)
        u = ((t + ph) % per) / per
        o.append(f'<circle cx="{fx + rs.uniform(-14, 14) + 18 * math.sin(u * 5 + i):.1f}" cy="{fy - rise * u - 12:.1f}" r="{4 * (1 - u) + 1:.1f}" fill="#ffd070"/>')
    return "".join(o)


# ═════════════════════════════ s07 10.3–12.8: кот крупно ═════════════════════════════
T_ZNAESH = wt(25)        # 10.96


def frame07(t):
    A = 10.3
    u = clamp((t - A) / 2.4)
    z = 2.3 + .5 * ease_io(u) + .04 * bump(t, T_ZNAESH, .35)
    set_ink(z)
    CXc, CYc, CK = 540, 1010, 1.0
    # поворот к зрителю → на «знаешь» голова склоняется, правое ухо торчком, взгляд вопросом
    q = ease_io(clamp((t - (T_ZNAESH - .12)) / .45))
    st = cstate(t, look=(.15 * (1 - q), -.18 * q), turn=.18 * (1 - q) - .08 * q, blink=blink_of(t, (10.65, 11.95)),
                ear=-14 * q * (1 + .2 * math.sin(t * 22) * math.exp(-(t - T_ZNAESH) * 5) if t > T_ZNAESH else 1), perk=.9 * q,
                tail=6 * math.sin(t * 2.4), smile=0, flame_e=1.3 + .3 * math.sin(t * 9), tilt=-9 * q + 1.6 * math.sin(t * 1.1))
    o = [room_blur(t)]
    o.append(blob(ellipse_pts(CXc, CYc + 250, 520, 70, 20), "#7a5430", .35))
    o.append(Cat.draw(CXc, CYc, CK * 1.0, st, t))
    fx, fy = CXc + (995 - 836) * CK, CYc + (1076 - 1306) * CK
    o.append(sparks(t, fx, fy - 20, 6, 31, 100))
    # вопросительный штрих над головой: рисуется к слову «знаешь»
    pu = ease_out(clamp((t - T_ZNAESH) / .35), 2.4)
    if pu > 0:
        sc = 1.15 * (.7 + .3 * pu) * (1 + .06 * math.sin((t - T_ZNAESH) * 16) * math.exp(-(t - T_ZNAESH) * 4))
        o.append(f'<g opacity="{pu:.3f}">{qmark(CXc - 100, CYc - 455 - 20 * (1 - pu), sc, 3, "#2a2d30", 9.5)}</g>')
        for k_, a_ in enumerate((-30, 0, 30)):
            r0, r1 = 130, 170 + 14 * math.sin(t * 14 + k_)
            ar = math.radians(a_ - 40)
            hx0, hy0 = CXc + 85, CYc - 330
            o.append(line([(hx0 + r0 * math.cos(ar), hy0 + r0 * math.sin(ar)), (hx0 + r1 * math.cos(ar), hy0 + r1 * math.sin(ar))], 5, "#2a2d30", taper=.7, wmin=.3,
                          seed=7800 + k_, op=pu * (1 - smooth(T_ZNAESH + .4, T_ZNAESH + .7, t))))
    cam = lib.cam(CXc + 20 - 10 * ease_io(u), CYc - 210 + 10 * ease_io(u), z, -1.2 + 1.8 * ease_io(u) - 1.0 * bump(t, T_ZNAESH, .3))
    return f'<g transform="{cam}">{"".join(o)}</g>'


FRAMES = {}


def frame(sid, t):
    lib.dyn_begin()
    return lib.svg(FRAMES[sid](t))


FRAMES["s07"] = frame07


FLOOR = 1330


# ═════════════════════════════ коридор: стена, пол, двери ═════════════════════════════
def door(x, y_floor, w=300, h=700, handle_side=1, hl=0.0, t=0.0, tag=0, lever_ang=0.0, hfrac=.47):
    """Дверь аудитории (дерево, две филёнки, металлический рычаг справа/слева). Возвращает (svg_дверь, (hx, hy) точка рычага)."""
    x0, x1, y0 = x - w / 2, x + w / 2, y_floor - h
    o = shape(rrect(x0 - 26, y0 - 26, x1 + 26, y_floor, 6), "#8d5f35", blob(rrect(x0 - 26, y0 - 26, x0 - 8, y_floor), "#a97542", .7), w=5, seed=4100 + tag)
    o += shape(rrect(x0, y0, x1, y_floor, 3), "#c99a62", blob(rrect(x0, y0, x0 + 30, y_floor), "#d9ad78", .6), w=4.6, seed=4101 + tag)
    for i, (a, b) in enumerate(((y0 + 50, y0 + h * .42), (y0 + h * .48, y_floor - 60))):
        o += shape(rrect(x0 + 40, a, x1 - 40, b, 4), "#b98350", blob(rrect(x0 + 40, a, x1 - 40, a + 14), "#9a6a3c", .8), w=3.6, seed=4110 + i + tag)
    o += shape(rrect(x - 44, y0 + 110, x + 44, y0 + 250, 10), "#dfe9ee", blob(rrect(x - 44, y0 + 110, x - 4, y0 + 250), "#c3d6df", .8), w=3.6, seed=4120 + tag)  # окошко без стекла-текста
    hx = x + handle_side * (w / 2 - 50)
    hy = y_floor - h * hfrac
    plate = shape(rrect(hx - 14, hy - 74, hx + 14, hy + 40, 8), "#9AA0A6", blob(rrect(hx - 14, hy - 74, hx - 2, hy + 40), "#b8bec3", .8), w=3.4, seed=4130 + tag)
    lever = shape(rrect(hx - 14, hy - 12, hx - handle_side * 100 + 8, hy + 14, 10), "#9AA0A6", blob(rrect(hx - 14, hy - 12, hx - handle_side * 100 + 8, hy - 2), "#c8ced2", .9),
                  w=3.6, seed=4131 + tag)
    lever = f'<g transform="rotate({lever_ang * handle_side * -1:.2f} {hx:.1f} {hy:.1f})">{lever}</g>'
    return o + plate + lever, (hx - handle_side * 70, hy)


def corridor(x_min, x_max, floor=1330, light=0.0):
    wall_top = -300
    o = blob(rrect(x_min, wall_top, x_max, floor, 0), "#ece6d6")
    o += blob(rrect(x_min, floor - 520, x_max, floor, 0), "#8fb0a8")                       # панель стены
    o += blob(rrect(x_min, floor - 520, x_max, floor - 470, 0), "#7a9d94")
    o += line([(x_min, floor - 520), (x_max, floor - 520)], 5, "#4f6e66", taper=0, wmin=1, seed=4001)
    o += blob(rrect(x_min, floor, x_max, 2400), "#cdbb9a")
    o += blob(rrect(x_min, floor, x_max, floor + 40), "#a8946f")
    o += line([(x_min, floor), (x_max, floor)], 6, "#6f5e44", taper=0, wmin=1, seed=4002)
    for i in range(int(x_min // 220) - 1, int(x_max // 220) + 2):
        xx = i * 220
        o += line([(xx, floor + 40), (xx - 90, 2400)], 3, "#b6a283", taper=0, wmin=1, seed=4010 + i % 40, op=.9)
    for j, yy in enumerate((floor + 150, floor + 330, floor + 560)):
        o += line([(x_min, yy), (x_max, yy)], 3, "#b6a283", taper=0, wmin=1, seed=4060 + j, op=.9)
    o += blob(ellipse_pts((x_min + x_max) / 2, floor + 220, (x_max - x_min) * .45, 80, 24), "#e4d6b6", .7)   # пятно дневного света
    return o


def standing_dima(hip, bs, lean, expr, arms=None, hands=None, feet=None, head_ang=0.0, hood=0.0):
    arms = arms or {"n": ("ik", (hip[0] + 40 * bs, hip[1] + 330 * bs), -1), "f": ("ik", (hip[0] - 10 * bs, hip[1] + 330 * bs), -1)}
    hands = hands or {"n": open_hand(.35, (0, 1), .15, .3, flip=-1), "f": open_hand(.35, (0, 1), .15, .3)}
    return dima(hip, bs, lean, arms, hands, expr, feet=feet, head_ang=head_ang)


# ═════════════════════════════ s17 36.3–38.7: Дима и кот у двери, «кот» ═════════════════════════════
T_KOT = wt(84)          # 37.36
T_NAP = wt(83)          # 36.52


def frame17(t):
    A = 36.3
    u = clamp((t - A) / 2.4)
    z = 1.0 + .13 * ease_io(u) + .03 * bump(t, T_KOT, .35)
    set_ink(z)
    o = [corridor(-300, 1400)]
    dd, hpt = door(735, FLOOR, 320, 700, handle_side=-1, tag=1)
    o.append(dd)
    o.append(blob(ellipse_pts(300, FLOOR + 30, 150, 20, 14), "#7a6a50", .45) + blob(ellipse_pts(800, FLOOR + 30, 140, 18, 14), "#7a6a50", .45))
    breath = math.sin(t * 2.6)
    bs = .8
    hip = (300, 806 + 2 * breath)
    wave = math.sin(t * 7.5) * bump(t, 36.9, 1.2)
    exp = dict(lid=.94, look=(-.55, .08), closed=blink_of(t, (36.75, 38.1)), brows="calm" if t < T_KOT - .15 else "up", mouth="smile", smile=.8 + .2 * bump(t, T_KOT, .6), blush=.25)
    up = ease_io(clamp((t - 36.5) / .5))
    hand_t = (hip[0] + 150 * bs + 25 * wave, hip[1] - 250 * bs + 120 * bs * (1 - up) - 10 * wave)
    d = standing_dima(hip, bs, .02, exp, arms={"n": ("ik", hand_t, -1), "f": ("ik", (hip[0] - 40 * bs, hip[1] + 330 * bs), -1)},
                      hands={"n": open_hand(.15, (0.35 + .2 * wave, -1), .35, .3, flip=-1), "f": open_hand(.35, (0, 1), .15, .3)},
                      feet={"n": ((hip[0] + 80, FLOOR - 36), 0.0), "f": ((hip[0] - 40, FLOOR - 34), 0.0)}, head_ang=-.02 + .02 * breath)
    o.append(d.get("legs", "") + d["arm_f"] + d["body"] + d["arm_n"])
    CX_, CY_, CK = 745, FLOOR - 8, 1.45
    up = ease_io(clamp((t - T_NAP) / .3))
    st = cstate(t, look=(-.3, .05), turn=-.12, blink=blink_of(t, (36.9, 38.2)), ear=4 * bump(t, T_KOT, .4), perk=.2 * up, tail=7 * math.sin(t * 2.6),
                smile=1 if t > T_KOT else 0, flame_e=1.4 + .3 * math.sin(t * 9), tilt=2 * math.sin(t * 1.3) - 3 * bump(t, T_KOT - .2, .6))
    o.append(Cat.draw(CX_, CY_, CK, st, t))
    o.append(sparks(t, CX_ + (995 - 836) * CK, CY_ + (1076 - 1306) * CK - 20, 6, 17))
    cam = lib.cam(540 + 10 * u, 880 - 20 * u, z, -.4 + .5 * u)
    return f'<g transform="{cam}">{"".join(o)}{write_kot(t, T_KOT - .06, 525, 560, 1.3)}</g>'


FRAMES["s17"] = frame17


# ═════════════════════════════ аудитория Чикаго: зал, окна с высотками ═════════════════════════════
def skyline(x0, y0, x1, y1, seed=0):
    """Силуэты высоток за стеклом (без надписей, без флагов): башни с антеннами, светлые окна-полосы."""
    rs = np.random.RandomState(seed)
    o = ""
    x = x0 - 10
    cols = ["#7d93ad", "#6a819c", "#8da3bb", "#5f7690"]
    while x < x1:
        w = rs.uniform(46, 96)
        h = rs.uniform(.25, .85) * (y1 - y0)
        c = cols[rs.randint(4)]
        o += blob(rect_pts_(x, y1 - h, x + w, y1), c)
        if rs.rand() < .5:
            o += blob(rect_pts_(x + w * .3, y1 - h - 30, x + w * .7, y1 - h), c)
            o += line([(x + w * .5, y1 - h - 30), (x + w * .5, y1 - h - 80 - rs.uniform(0, 40))], 4, "#56697f", taper=.3, wmin=.5, seed=int(x))
        for j in range(int(h // 34)):
            o += blob(rect_pts_(x + 8, y1 - h + 14 + j * 34, x + w - 8, y1 - h + 20 + j * 34), mix(c, "#ffffff", .22))
        x += w + rs.uniform(-8, 6)
    return o


def rect_pts_(x0, y0, x1, y1):
    return [(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)]


def hall(x0, x1, tint=0.0):
    """Зал: стена с высокими окнами, паркетный пол, перегородка-доска; tint>0 — холоднее (для «ждавших»)."""
    wall = mix("#efe6d0", "#cfd4de", tint)
    floor = mix("#cfa06a", "#a99e92", tint)
    o = blob(rrect(x0, -300, x1, 1000, 0), wall) + blob(rrect(x0, 1000, x1, 2300, 0), floor)
    o += blob(rrect(x0, 940, x1, 1000, 0), mix("#a87b47", "#7c7a86", tint)) + line([(x0, 1000), (x1, 1000)], 5, "#6f5230", taper=0, wmin=1, seed=4201)
    for i, yy in enumerate((1100, 1250, 1450, 1700)):
        o += line([(x0, yy), (x1, yy + 6)], 3, mix("#a97542", "#6d6a74", tint), taper=0, wmin=1, seed=4210 + i, op=.8)
    wx = int(x0 // 460) * 460
    while wx < x1:
        a, b = wx + 40, wx + 400
        o += shape(rrect(a - 16, 120, b + 16, 920, 6), "#fdf8ec", "", w=5, seed=4300 + wx % 97)
        sky = lib.lin_grad([(0, "#9fd0ee", 1), (1, "#e2f2fa", 1)], 0, 0, 0, 1)
        o += f'<rect x="{a}" y="136" width="{b - a}" height="768" fill="url(#{sky})"/>'
        cid = lib.clip_rect(a, 136, b - a, 768)
        o += f'<g clip-path="url(#{cid})">' + skyline(a, 136, b, 904, seed=wx % 13 + 3) + "</g>"
        o += line([((a + b) / 2, 136), ((a + b) / 2, 904)], 8, "#fdf8ec", taper=0, wmin=1, seed=4310 + wx % 53) + line([(a, 420), (b, 420)], 8, "#fdf8ec", taper=0, wmin=1, seed=4320 + wx % 41)
        o += shape(rrect(a, 136, b, 904, 2), "none", "", w=4, seed=4330 + wx % 29)
        o += blob([(a - 30, 1000), (b + 30, 1000), (b + 150, 1700), (a + 40, 1700)], "#ffffff", .0)
        wx += 460
    return o


def papers_on(t, xs, edge_y, sc, t0, ph=0.0):
    o = ""
    for i, x in enumerate(xs):
        u = clamp((t - t0 - .07 * i) / .3)
        if u <= 0:
            continue
        k = sc * 1.5 * (back_out(u, 2.2))
        o += PR.ticket(x, edge_y - 18 * sc - 26 * (1 - u), k, rot=-4 + 3 * i % 7, seed=i, lines=4)
    return o


T_CHI, T_TEST = wt(36), wt(40)          # 16.24, 17.82
G1F = [("a", 200), ("b", 600), ("c", 1000)]
G1B = [("d", 400), ("e", 800)]
G2F = [("f", 1560), ("g", 1960), ("h", 2360)]
G2B = [("i", 1760), ("j", 2160)]


def frame09(t):
    A = 15.2
    u = clamp((t - A) / 3.1)
    pan = ease_io(u)
    z = 1.0 + .10 * pan + .03 * bump(t, T_CHI, .4)
    set_ink(z)
    o = [hall(-300, 3000)]
    for rowset, edge, sc, back in ((G1B + G2B, 1040, .7, True), (G1F + G2F, 1400, .98, False)):
        for key, x in rowset:
            grp2 = x > 1200
            mood = "tense" if grp2 else "calm"
            if t > T_TEST + .2 and not grp2:
                mood = "write"
            sw = 3 * math.sin(t * 1.3 + x)
            o.append(ST.student(key, x, edge + 0 * sw, sc, mood, t=t, ph=x * .01, blink_t=(15.9 + (x % 7) * .3, 17.1 + (x % 5) * .3), w=400, up=(1 if t > T_TEST else 0),
                                write=1.0 if (t > T_TEST + .3 and not grp2 and not back) else 0.0, tilt=-2 * (1 if grp2 else 0)))
        xs = [x for k_, x in rowset]
        o.append(papers_on(t, xs, edge, sc, T_TEST))
    cx = 540 + 1280 * pan
    cam = lib.cam(cx, 960 + 20 * pan, z, -.5 + 1.0 * pan + 1.0 * bump(t, T_CHI, .35))
    return f'<g transform="{cam}">{"".join(o)}</g>'


FRAMES["s09"] = frame09


def plainwall(x0, x1, tint=0.0, floor_y=1000):
    """Светлая стена класса с панелью, окном с мягким светом и пробковой доской без надписей (цветные листки-пятна)."""
    wall = mix("#f1e4c8", "#c9ced9", tint)
    o = blob(rrect(x0, -300, x1, floor_y, 0), wall)
    o += blob(rrect(x0, floor_y - 360, x1, floor_y, 0), mix("#9db7a2", "#8a93a0", tint))
    o += blob(rrect(x0, floor_y - 360, x1, floor_y - 316, 0), mix("#86a58f", "#76808e", tint))
    o += line([(x0, floor_y - 360), (x1, floor_y - 360)], 5, mix("#506f5a", "#4a5262", tint), taper=0, wmin=1, seed=4401)
    o += blob(rrect(x0, floor_y, x1, 2400, 0), mix("#cfa06a", "#a39a90", tint))
    o += line([(x0, floor_y), (x1, floor_y)], 6, "#6f5230", taper=0, wmin=1, seed=4402)
    for i, yy in enumerate((floor_y + 130, floor_y + 300, floor_y + 520)):
        o += line([(x0, yy), (x1, yy + 6)], 3, mix("#a97542", "#6d6a74", tint), taper=0, wmin=1, seed=4410 + i, op=.8)
    for k in range(int(x0 // 900) - 1, int(x1 // 900) + 2):
        bx = k * 900 + 280
        o += shape(rrect(bx, 250, bx + 300, 560, 6), "#fdf8ec", "", w=5, seed=4420 + k % 9)
        o += blob(rrect(bx + 12, 262, bx + 288, 548, 2), "#c89a5e")
        for j, (cx_, cy_, w_, h_, c_) in enumerate(((30, 30, 70, 90, "#f6d36a"), (130, 50, 80, 70, "#8fc5a2"), (210, 40, 62, 100, "#e8847a"), (50, 150, 90, 80, "#9db8e0"),
                                                      (170, 160, 100, 70, "#f6efe0"))):
            o += shape(rrect(bx + cx_, 262 + cy_, bx + cx_ + w_, 262 + cy_ + h_, 3), c_, "", w=3.2, seed=4430 + j + k % 5)
            o += line([(bx + cx_ + 8, 262 + cy_ + 20), (bx + cx_ + w_ - 12, 262 + cy_ + 20)], 3, "#2a2d30", taper=.3, wmin=.6, seed=4440 + j, op=.0)
    return o


def sheet_on(x, edge_y, sc, rot=0.0, fill=1.0, t=0.0, writing=False, seed=0):
    return PR.paper_sheet(x, edge_y - 30 * sc, sc * 1.7, fill=fill, rot=rot, t=t, writing=writing, lines=6, seed=seed)


def puff(x, y, u, s=1.0, col="#6E6A8C"):
    """Хлопок-рассыпание облачка: круглые клочки разлетаются и мельчают (без прозрачности)."""
    if u <= 0 or u >= 1:
        return ""
    o = ""
    for i in range(11):
        a = i * 2 * math.pi / 11 + .3
        r = (30 + 110 * ease_out(u)) * s * (1 + .2 * math.sin(i * 2.1))
        rad = max(.5, (16 - 14 * u) * s * (1 + .3 * math.sin(i * 1.3)))
        o += f'<circle cx="{x + r * math.cos(a):.1f}" cy="{y + r * math.sin(a) * .8:.1f}" r="{rad:.1f}" fill="{col}" stroke="{INK}" stroke-width="{max(.6, 3 * (1 - u)):.1f}"/>'
    return o


T_VYP = wt(50)          # 21.89


def frame11(t):
    A = 20.9
    u = clamp((t - A) / 3.0)
    z = 1.0 + .17 * ease_io(u)
    set_ink(z)
    o = [plainwall(-300, 1500)]
    rel = smooth(T_VYP + .05, T_VYP + .6, t)           # расслабление после «выписал»
    # дальний ряд
    for key, x, sc_, mood in (("d", 230, .8, "write"), ("e", 850, .84, "write")):
        o.append(ST.student(key, x, 960, sc_, "calm" if rel > .5 else mood, t=t, ph=x * .02, blink_t=(21.3, 22.6), w=330, write=(1 - rel) * .8, shrug=1 - rel))
    cast = (("a", 165, "write"), ("b", 540, "write"), ("c", 915, "write"))
    for key, x, m0 in cast:
        mood = "calm" if rel > .5 else "write"
        o.append(ST.student(key, x, 1370, 1.3, mood, t=t, ph=x * .01, blink_t=(21.45 + x % 3 * .2, 22.9), w=250, write=(1 - rel) * 1.0, shrug=1 - rel,
                            tilt=-3 * rel * math.sin((t - T_VYP) * 3) * 0 + 2 * rel))
        o.append(sheet_on(x + 10, 1370, 1.3, rot=-3 + 6 * (x > 600), fill=1.0, t=t, writing=(rel < .3), seed=int(x) % 7))
    # облачко: вылетает из листа центрального студента, поднимается дугой, растёт, затем рассыпается
    c0 = clamp((t - T_VYP) / 1.15)
    if 0 < c0 < 1:
        sx_, sy_ = 550, 1340
        px = sx_ + 190 * ease_out(c0) + 24 * math.sin(c0 * 11) * (1 - c0)
        py = sy_ - 880 * ease_out(c0, 1.8) - 20 * math.sin(c0 * 9)
        sc = .55 + 2.3 * ease_out(clamp(c0 * 1.2), 2.2)
        if c0 < .82:
            o.append(PR.anx_cloud(px, py, sc, 1, t))
        else:
            o.append(puff(px, py, (c0 - .82) / .18, 1.4))
    cam = lib.cam(540 + 10 * math.sin(t * .8) - 25 * u, 900 - 90 * ease_io(u) + 20 * math.sin(t * 1.1), z, .6 - 1.0 * u + 1.2 * bump(t, T_VYP, .3))
    return f'<g transform="{cam}">{"".join(o)}</g>'


FRAMES["s11"] = frame11


# ═════════════════════════════ s12 23.56–26.81: две группы рядом ═════════════════════════════
T_SDALI, T_PROSTO = wt(54), wt(59)      # 23.76, 25.66


def tick(x, y, u, s=1.0, col="#3f9a5e"):
    """Галочка-штрих пером: рисуется за u 0…1, плотная линия с нажимом, после — упругий хлопок."""
    if u <= 0:
        return ""
    P = lib.sample([(-120, -10), (-82, 36), (-44, 84), (-6, 20), (70, -90), (150, -170)], False, 3.0)
    P = np.array(P, float)
    n = max(2, int(len(P) * min(1, u)))
    Q = P[:n] * s + np.array([x, y])
    Wd = np.interp(np.linspace(0, 1, n), [0, .1, .45, .55, 1], [8, 30, 34, 26, 12]) * s * 1.0
    pop = 1 + .12 * math.exp(-max(0, u - 1) * 9) * math.sin(min(max(0, u - 1) * 14, math.pi))
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({pop:.3f}) translate({-x:.1f} {-y:.1f})"><path d="{_band_path(Q, Wd)}" fill="{col}"/></g>'


def frame12(t):
    A = 23.56
    pan = ease_io(clamp((t - 24.55) / 1.45))
    z = 1.0 + .08 * ease_io(clamp((t - A) / 3.2)) + .03 * bump(t, T_PROSTO, .35)
    set_ink(z)
    o = [f'<g>{plainwall(-300, 1180, 0.0)}</g>']
    cid = lib.clip_rect(1180, -400, 2200, 3000)
    o.append(f'<g clip-path="url(#{cid})">{plainwall(1180, 3000, .55)}</g>')
    o.append(line([(1180, -300), (1180, 2400)], 5, "#7c7a86", taper=0, wmin=1, seed=4590, op=.0))
    glad = smooth(T_SDALI - .1, T_SDALI + .25, t)
    for key, x in (("a", 200), ("b", 580), ("c", 960)):
        o.append(ST.student(key, x, 1370, 1.32, "glad", t=t, ph=x * .01, blink_t=(23.9 + x % 3 * .25, 25.3), w=250, up=0, tilt=2 * math.sin(t * 2 + x), extra_mood=dict(look=(0, .0))))
        o.append(sheet_on(x + 10, 1370, 1.32, rot=-3 + 5 * (x > 500), fill=1.0, t=t, seed=int(x) % 7))
    for key, x in (("f", 1480), ("g", 1860), ("h", 2240)):
        dr = 1 + .02 * math.sin(t * 5 + x)
        o.append(ST.student(key, x, 1370, 1.32, "grim" if key != "g" else "tense", t=t, ph=x * .01, blink_t=(24.3 + x % 3 * .3, 25.9), w=250, shrug=1.0, tilt=-3 + 2 * math.sin(t * 1.5 + x)))
    # галочка над выписавшими
    o.append(tick(580, 575, (t - T_SDALI) / .38 if t < T_SDALI + .38 else 1 + (t - T_SDALI - .38), 1.25))
    # серое облако над ждавшими
    cu = (t - T_PROSTO) / .5
    if cu > 0:
        cs = 3.4 * back_out(cu, 1.9)
        o.append(PR.anx_cloud(1860, 640 + 12 * math.sin(t * 2.4), cs, 1, t))
        for i in range(3):
            tt_ = (t * .9 + i / 3) % 1
            if cu > 1:
                o.append(line([(1800 + 60 * i, 790 + 120 * tt_), (1796 + 60 * i, 850 + 120 * tt_)], 6, "#58547A", taper=.5, wmin=.4, seed=4600 + i, op=1 - tt_))
    cx = 540 + 1260 * pan + 12 * math.sin(t * .9)
    cam = lib.cam(cx, 940 - 20 * pan, z, -.6 + 1.2 * pan + .9 * bump(t, T_PROSTO, .3))
    return f'<g transform="{cam}">{"".join(o)}</g>'


FRAMES["s12"] = frame12


# ═════════════════════════════ s16 33.7–36.7: коридор, боковой трекинг ═════════════════════════════
T_PROV, T_DVERI = wt(79), wt(82)        # 34.70, 35.73
DOOR_X = 1520
A16 = 33.7
V0, V_STOP = 470.0, (35.1, 35.55)
X0_D = 380.0


def _walk_x(t):
    """Положение таза Димы (мир): ровный шаг, подталкивание котом на 34.7 слегка ускоряет, у двери — торможение."""
    x, tt = X0_D, A16
    dt = 1 / 120
    while tt < t:
        v = V0 * (1 - smooth(V_STOP[0], V_STOP[1], tt)) * (1 + .22 * bump(tt, T_PROV + .08, .5))
        x += v * dt
        tt += dt
    return x


def frame16(t):
    set_ink(1.05)
    dxh = DOOR_X - 110
    x = _walk_x(t)
    v_now = (_walk_x(t + .02) - x) / .02
    moving = clamp(v_now / V0)
    ph = x / 250.0 * math.pi
    A = 250 / math.pi
    hip_y = 806 + 7 * abs(math.cos(ph)) * moving - 3 * (1 - moving) * 0
    bs = .8
    # дальние двери и стена
    o = [corridor(-400, 2600)]
    for i, dx in enumerate((520, 1020)):
        dd, _ = door(dx, FLOOR, 300, 760, handle_side=-1, tag=10 + i, hfrac=.5)
        o.append(dd)
    press = smooth(T_DVERI, T_DVERI + .25, t)
    dd, hpt = door(DOOR_X, FLOOR, 320, 820, handle_side=-1, tag=2, lever_ang=-16 * press, hfrac=.5)
    o.append(dd)
    # пятна света на полу и тени
    o.append(blob(ellipse_pts(x + 20, FLOOR + 30, 150, 18, 14), "#7a6a50", .45))
    swing = {}
    for side, off in (("n", 0.0), ("f", math.pi)):
        pp = ph + off
        lift = 52 * max(0.0, -math.cos(pp)) ** .8 * moving
        fx = x + (-A * math.sin(pp)) * moving + (14 if side == "n" else -10)
        swing[side] = ((fx, FLOOR - 34 - lift), -.25 * lift / 52)
    # руки: пока идёт — маятником; к двери — ближняя тянется к рычагу
    reach = smooth(35.15, T_DVERI - .02, t)
    asw = math.sin(ph) * 55 * moving
    grip = (hpt[0] - 6, hpt[1] + 4 + 8 * press)
    arm_n_t = (x + 20 * bs + asw * bs * 1.2 + 40, hip_y + 300 * bs - 30 * math.cos(ph) * moving)
    nt = (arm_n_t[0] + (grip[0] - arm_n_t[0]) * reach, arm_n_t[1] + (grip[1] - arm_n_t[1]) * reach)
    ft = (x - 30 * bs - asw * bs * 1.1, hip_y + 320 * bs)
    expr = dict(lid=.9, look=(.5, .15), closed=blink_of(t, (34.1, 35.9)), brows="calm" if t < T_DVERI else "up", mouth="smile",
                smile=.55 if t < T_PROV else .8, blush=.2)
    grip_k = smooth(T_DVERI - .02, T_DVERI + .12, t)
    lean = .06 * moving + .03 * bump(t, T_PROV + .1, .35) * 1 + .02 * reach
    d = standing_dima((x, hip_y), bs, lean, expr, arms={"n": ("ik", nt, -1), "f": ("ik", ft, -1)},
                      hands={"n": open_hand(.2 + .65 * grip_k, (1, .25 + .3 * reach), .1, .3 - .15 * grip_k, flip=-1), "f": open_hand(.35, (0, 1), .15, .3)},
                      feet=swing, head_ang=-.02 + .02 * math.sin(ph) * moving)
    o.append(d.get("legs", "") + d["arm_f"] + d["body"] + d["arm_n"])
    # кот идёт следом, на «провожает» догоняет и тычется носом в пятку
    nud = ease_io(clamp((t - T_PROV + .15) / .45)) * (1 - smooth(T_PROV + .5, T_PROV + 1.0, t))
    cat_x = x - 300 + 190 * nud + 40 * smooth(T_PROV + .5, T_PROV + 1.2, t) * 0
    hop = abs(math.sin(ph * 1.0)) * 16 * moving
    cy_ = FLOOR - 8 - hop
    st = cstate(t, look=(.5 - .3 * nud, .2), turn=.3, blink=blink_of(t, (34.4, 36.0)), ear=3 * bump(t, T_PROV, .4), perk=.3 * nud, tail=9 * math.sin(ph * .8),
                smile=0, flame_e=1.4 + .3 * math.sin(t * 9), tilt=-3 - 7 * nud + 2.5 * math.sin(ph))
    o.append(blob(ellipse_pts(cat_x, FLOOR + 28, 110, 14, 14), "#7a6a50", .45))
    o.append(Cat.draw(cat_x, cy_, .95, st, t))
    o.append(sparks(t, cat_x + (995 - 836) * .95, cy_ + (1076 - 1306) * .95 - 15, 5, 41, 90))
    cxc = x - 50 + 150 * smooth(35.4, 36.6, t) + 25 * math.sin(t * 1.5) * moving
    z = 1.02 + .12 * smooth(34.9, 36.5, t)
    set_ink(z)
    cam = lib.cam(cxc, 900 - 25 * smooth(35, 36.5, t), z, -.5 * (1 - smooth(34, 36, t)) + .6 * bump(t, T_DVERI, .3) + .6 * math.sin(ph * 2) * moving * .3)
    return f'<g transform="{cam}">{"".join(o)}</g>'


FRAMES["s16"] = frame16
