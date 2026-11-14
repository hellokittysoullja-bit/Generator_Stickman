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
import cat as Cat  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
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
def door(x, y_floor, w=300, h=700, handle_side=1, hl=0.0, t=0.0, tag=0):
    """Дверь аудитории (дерево, две филёнки, металлический рычаг справа/слева). Возвращает (svg_дверь, (hx, hy) точка рычага)."""
    x0, x1, y0 = x - w / 2, x + w / 2, y_floor - h
    o = shape(rrect(x0 - 26, y0 - 26, x1 + 26, y_floor, 6), "#8d5f35", blob(rrect(x0 - 26, y0 - 26, x0 - 8, y_floor), "#a97542", .7), w=5, seed=4100 + tag)
    o += shape(rrect(x0, y0, x1, y_floor, 3), "#c99a62", blob(rrect(x0, y0, x0 + 30, y_floor), "#d9ad78", .6), w=4.6, seed=4101 + tag)
    for i, (a, b) in enumerate(((y0 + 50, y0 + h * .42), (y0 + h * .48, y_floor - 60))):
        o += shape(rrect(x0 + 40, a, x1 - 40, b, 4), "#b98350", blob(rrect(x0 + 40, a, x1 - 40, a + 14), "#9a6a3c", .8), w=3.6, seed=4110 + i + tag)
    o += shape(rrect(x - 44, y0 + 110, x + 44, y0 + 250, 10), "#dfe9ee", blob(rrect(x - 44, y0 + 110, x - 4, y0 + 250), "#c3d6df", .8), w=3.6, seed=4120 + tag)  # окошко без стекла-текста
    hx = x + handle_side * (w / 2 - 50)
    hy = y_floor - h * .47
    plate = shape(rrect(hx - 14, hy - 74, hx + 14, hy + 40, 8), "#9AA0A6", blob(rrect(hx - 14, hy - 74, hx - 2, hy + 40), "#b8bec3", .8), w=3.4, seed=4130 + tag)
    lever = shape(rrect(hx - 14, hy - 12, hx - handle_side * 100 + 8, hy + 14, 10), "#9AA0A6", blob(rrect(hx - 14, hy - 12, hx - handle_side * 100 + 8, hy - 2), "#c8ced2", .9),
                  w=3.6, seed=4131 + tag)
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
    dd, hpt = door(800, FLOOR, 300, 760, handle_side=-1, tag=1)
    o.append(dd)
    o.append(blob(ellipse_pts(300, FLOOR + 30, 150, 20, 14), "#7a6a50", .45) + blob(ellipse_pts(800, FLOOR + 30, 140, 18, 14), "#7a6a50", .45))
    breath = math.sin(t * 2.6)
    bs = .78
    hip = (290, 870 + 2 * breath)
    exp = dict(lid=.94, look=(-.55, .08), closed=blink_of(t, (36.75, 38.1)), brows="calm" if t < T_KOT - .15 else "up", mouth="smile", smile=.8 + .2 * bump(t, T_KOT, .6), blush=.25)
    pocket = (hip[0] + 70 * bs, hip[1] + 120 * bs)
    d = standing_dima(hip, bs, .03, exp, arms={"n": ("ik", (hip[0] + 110 * bs, hip[1] + 280 * bs), -1), "f": ("ik", (hip[0] - 40 * bs, hip[1] + 300 * bs), -1)},
                      hands={"n": open_hand(.45, (0.3, 1), .2, .3, flip=-1), "f": open_hand(.35, (0, 1), .15, .3)},
                      feet={"n": ((hip[0] + 90, FLOOR - 40), 0.0), "f": ((hip[0] - 30, FLOOR - 36), 0.0)}, head_ang=-.02 + .02 * breath)
    o.append(d.get("legs", "") + d["arm_f"] + d["body"] + d["arm_n"])
    CX_, CY_, CK = 800, FLOOR - 8, 1.18
    up = ease_io(clamp((t - T_NAP) / .3))
    st = cstate(t, look=(-.3, .05), turn=-.12, blink=blink_of(t, (36.9, 38.2)), ear=4 * bump(t, T_KOT, .4), perk=.2 * up, tail=7 * math.sin(t * 2.6),
                smile=1 if t > T_KOT else 0, flame_e=1.4 + .3 * math.sin(t * 9), tilt=2 * math.sin(t * 1.3) - 3 * bump(t, T_KOT - .2, .6))
    o.append(Cat.draw(CX_, CY_, CK, st, t))
    o.append(sparks(t, CX_ + (995 - 836) * CK, CY_ + (1076 - 1306) * CK - 20, 6, 17))
    cam = lib.cam(540 + 10 * u, 880 - 20 * u, z, -.4 + .5 * u)
    return f'<g transform="{cam}">{"".join(o)}{write_kot(t, T_KOT - .06, 560, 560, 1.25)}</g>'


FRAMES["s17"] = frame17
