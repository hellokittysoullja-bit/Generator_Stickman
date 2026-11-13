"""Золотая рыбка рилса 31 — одна и та же во всех планах (сцены fish и lab).

Локальные координаты: рыбка смотрит вправо (+x), центр тела в (0, 0), нос у x≈106, вуалевый хвост до x≈-270.
draw(...) -> строка SVG; положение, масштаб, поворот и разворот (face от -1 до 1) — трансформом группы,
изгиб тела при плавании и волна хвоста — в локальных точках (контур туши остаётся живой линией ink.py).
"""
import math

import numpy as np

from lib import DEFS, INK, blob, clamp, clip_of, ellipse_pts, f, fill_d, ink_closed, lin_grad, line, shape, uid

BODY = "#f7931e"
BODY_SH = "#dc6a12"
BODY_HI = "#ffbe5c"
BELLY = "#ffc978"
FIN = "#ffa53a"
FIN_PALE = "#ffe1a0"
RAY = "#e8781c"
SCALE = "#e57a1a"
LID = "#f7931e"
PUPIL = "#141018"

_BODY = [(106, 2), (101, -22), (82, -50), (46, -70), (2, -75), (-42, -66), (-76, -45), (-96, -18, 1), (-96, 18, 1), (-78, 42),
         (-46, 61), (-2, 69), (44, 63), (80, 45), (100, 22)]
# вуалевый хвост: две лопасти, волнистый край, выемка посередине
_TAIL = [(-90, -13), (-122, -44), (-166, -84), (-212, -114), (-252, -128), (-274, -118), (-266, -98), (-276, -78), (-258, -58),
         (-262, -36), (-236, -18), (-214, 0), (-236, 18), (-262, 36), (-258, 58), (-276, 78), (-266, 98), (-274, 118), (-252, 128),
         (-212, 114), (-166, 84), (-122, 44), (-90, 13)]
_DORSAL = [(46, -62), (26, -100), (-8, -126), (-48, -136), (-84, -126), (-104, -104), (-96, -84), (-80, -56)]
_PELVIC = [(14, 58), (2, 96), (-16, 116), (-34, 112), (-30, 60)]
_ANAL = [(-48, 50), (-64, 86), (-86, 102), (-104, 92), (-84, 36)]
_PECT = [(0, 0), (-18, 16), (-34, 40), (-30, 54), (-12, 50), (6, 30), (8, 8)]


def _bend(pts, ph, amp, tail_amp):
    """Изгиб тела волной от головы к хвосту + трепет вуали (ph — фаза плавания, рад)."""
    out = []
    for p in pts:
        x, y = p[0], p[1]
        w = clamp((40 - x) / 150, 0, 2.2)
        dy = amp * math.sin(ph - x * 0.022) * w ** 1.5
        if x < -88:
            d = (-88 - x) / 180
            dy += tail_amp * math.sin(ph * 1.0 - (-88 - x) / 55) * d ** 1.2
            # вуаль чуть «опаздывает» по x
            x = x + 6 * tail_amp / 30 * math.sin(ph * 2 - (-88 - x) / 40) * d
        out.append((x, y + dy) + tuple(p[2:]))
    return out


def _rot(pts, cx, cy, a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return [(cx + (p[0] - cx) * c - (p[1] - cy) * s, cy + (p[0] - cx) * s + (p[1] - cy) * c) + tuple(p[2:]) for p in pts]


def _eye(ex, ey, rx, ry, lw, look, lid, closed, blank, seed, brow=0.0, lid_c=LID, sq=0.0):
    """Глаз: белок, маленький зрачок; lid — верхнее веко 0..1; closed — закрыт дугой (0 — нет, 1 — ∩ «довольный»,
    2 — ∪ «подмигнул»); blank — зрачок-точка в центре («забыла»); sq — нижнее веко (прищур)."""
    s = []
    if closed:
        if closed == 1:
            pts = [(ex - rx * .9, ey + ry * .15), (ex - rx * .4, ey - ry * .35), (ex + rx * .4, ey - ry * .35), (ex + rx * .9, ey + ry * .15)]
        else:
            pts = [(ex - rx * .9, ey - ry * .05), (ex - rx * .35, ey + ry * .3), (ex + rx * .35, ey + ry * .3), (ex + rx * .9, ey - ry * .05)]
        s.append(line(pts, lw * 1.25, INK, taper=.5, wmin=.35, seed=seed + 7))
        return "".join(s)
    ep = ellipse_pts(ex, ey, rx, ry, 18)
    cid = clip_of(ep)
    o = [f'<path d="{fill_d(ep)}" fill="#fbfaf4"/><g clip-path="url(#{cid})">']
    o.append(blob(ellipse_pts(ex + rx * .18, ey + ry * .45, rx * .95, ry * .42, 12), "#dcd8cc"))
    pr = rx * (0.22 - 0.1 * blank)
    lx, ly = look
    px = ex + (lx * rx * 0.42) * (1 - blank)
    py = ey + (ly * ry * 0.38) * (1 - blank)
    o.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="{f(pr)}" fill="{PUPIL}"/>')
    if blank < 0.5:
        o.append(f'<circle cx="{f(px - pr * .38)}" cy="{f(py - pr * .4)}" r="{f(pr * .3)}" fill="#ffffff"/>')
    if lid > 0.01:
        yt = ey - ry * 1.05 + ry * 2.1 * lid
        o.append(f'<path d="M{f(ex - rx - 4)} {f(ey - ry - 6)} L{f(ex + rx + 4)} {f(ey - ry - 6)} L{f(ex + rx + 4)} {f(yt - ry * .12)} '
                 f'Q{f(ex)} {f(yt + ry * .22)} {f(ex - rx - 4)} {f(yt - ry * .12)}Z" fill="{lid_c}"/>')
        o.append(line([(ex - rx * 1.02, yt - ry * .1), (ex, yt + ry * .1), (ex + rx * 1.02, yt - ry * .1)], lw * .95, INK, seed=seed + 3,
                      taper=.3, wmin=.5))
    if sq > 0.01:
        yb = ey + ry * 1.05 - ry * 0.9 * sq
        o.append(f'<path d="M{f(ex - rx - 4)} {f(ey + ry + 6)} L{f(ex + rx + 4)} {f(ey + ry + 6)} L{f(ex + rx + 4)} {f(yb + ry * .1)} '
                 f'Q{f(ex)} {f(yb - ry * .2)} {f(ex - rx - 4)} {f(yb + ry * .1)}Z" fill="{lid_c}"/>')
        o.append(line([(ex - rx * .9, yb + ry * .06), (ex, yb - ry * .1), (ex + rx * .9, yb + ry * .06)], lw * .7, INK, seed=seed + 5,
                      taper=.4, wmin=.5))
    o.append(f'</g><path d="{ink_closed(ep, lw * 0.9, seed=seed)}" fill="{INK}"/>')
    s.append("".join(o))
    if brow:
        # бровь-штрих над глазом: brow>0 — хитро приподнята к краю, <0 — домиком (растерянно)
        b = brow
        p0 = (ex - rx * .8, ey - ry * 1.35 + (8 * b if b > 0 else -6 * b))
        p1 = (ex, ey - ry * 1.55 - abs(b) * 4)
        p2 = (ex + rx * .9, ey - ry * 1.4 - (10 * b if b > 0 else 8 * b))
        s.append(line([p0, p1, p2], lw * 1.2, INK, taper=.6, wmin=.3, seed=seed + 11))
    return "".join(s)


def _mouth(kind, open_, lw, ph):
    """Рот у носа (x≈100): 'pout' — пухлые губки, open_ 0..1 — раскрыт; 'smile' — улыбка; 'grin' — хитрая полуулыбка."""
    s = []
    if kind == "smile":
        s.append(line([(80, 18), (90, 26), (100, 24), (106, 14)], lw * 1.0, INK, taper=.5, wmin=.35, seed=91))
        return "".join(s)
    if kind == "grin":
        s.append(line([(76, 14), (88, 24), (100, 22), (108, 8)], lw * 1.0, INK, taper=.5, wmin=.35, seed=92))
        s.append(line([(74, 8), (76, 16)], lw * .7, INK, taper=.5, wmin=.4, seed=93))
        return "".join(s)
    # пухлые губки золотой рыбки
    o = clamp(open_)
    lip = ellipse_pts(104, 6, 9 + 2 * o, 11 + 8 * o, 12)
    s.append(shape(lip, "#f08a52", "", w=lw * .8, seed=94))
    if o > 0.05:
        s.append(shape(ellipse_pts(106, 6, 4 + 3 * o, 3 + 10 * o, 10), "#4a1410", "", w=lw * .5, seed=95))
    else:
        s.append(line([(106, 0), (106, 12)], lw * .6, INK, seed=96))
    return "".join(s)


def draw(x, y, s, t, face=1.0, rot=0.0, swim=1.0, freq=1.6, look=(0.3, 0.0), lid=0.0, wink=0.0, happy=0.0, blank=0.0,
         mouth="pout", mouth_open=None, brow=0.0, lw=4.6, fin=1.0, medal=0.0, sq=0.0, ph=None):
    """Рыбка. (x, y) — центр тела в мире; s — масштаб; face — разворот (1 вправо, -1 влево, промежуточные — поворот
    через узкий профиль); swim — сила волны тела 0..1.5; lw — толщина контура в ЛОКАЛЬНЫХ единицах."""
    if ph is None:
        ph = t * freq * 2 * math.pi
    amp = 5.5 * swim
    tamp = 16 * swim + 5
    fa = face if abs(face) > 0.16 else math.copysign(0.16, face if face else 1)
    out = [f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(s * fa)} {f(s)})">']
    # хвост (за телом)
    tail = _bend(_TAIL, ph, amp, tamp)
    g = lin_grad([(0, FIN_PALE, 1), (0.55, FIN, 1), (1, "#f58a22", 1)], 0, 0, 1, 0)
    rays = []
    for k, a in enumerate(np.linspace(-1, 1, 9)):
        tip = (-250 + 20 * abs(a), 118 * a)
        mid = (-170, 60 * a)
        rays.append(line(_bend([(-96, a * 8), mid, tip], ph, amp, tamp), lw * .55, RAY, taper=.4, wmin=.2, seed=300 + k, peak=.3))
    out.append(shape(tail, f"url(#{g})", "".join(rays), w=lw, seed=301))
    # спинной, брюшные, анальный плавники (за телом)
    dors = _bend(_DORSAL, ph, amp, tamp)
    dors = [(p[0], p[1] + 3 * math.sin(ph * 1.3 + p[0] * 0.04) * (p[1] < -90)) for p in dors]
    rd = "".join(line(_bend([(20 - 30 * k, -66), (6 - 36 * k, -110 + 4 * k)], ph, amp, tamp), lw * .5, RAY, taper=.4, wmin=.2,
                      seed=310 + k) for k in range(4))
    out.append(shape(dors, f"url(#{g})", rd, w=lw, seed=311))
    pel = _rot(_bend(_PELVIC, ph, amp, tamp), 8, 60, 10 * math.sin(ph * 1.2) * fin)
    out.append(shape(pel, FIN, "", w=lw * .9, seed=312))
    an = _rot(_bend(_ANAL, ph, amp, tamp), -70, 44, 8 * math.sin(ph * 1.2 + 1) * fin)
    out.append(shape(an, FIN, "", w=lw * .9, seed=313))
    # тело
    body = _bend(_BODY, ph, amp, tamp)
    inner = []
    inner.append(blob(_bend(ellipse_pts(0, 44, 92, 34, 16), ph, amp, tamp), BELLY))
    inner.append(blob(_bend([(-110, 30), (-60, 52), (0, 62), (60, 54), (120, 30), (120, 120), (-110, 120)], ph, amp, tamp), BODY_SH))
    inner.append(blob(_bend(ellipse_pts(-6, -50, 64, 13, 14, rot=-4), ph, amp, tamp), BODY_HI))
    # чешуйки дугами
    for k, (sx_, sy_) in enumerate([(-10, -34), (-38, -28), (-64, -18), (-24, -6), (-50, 4), (-6, 18), (-34, 26), (-62, 26),
                                    (14, -12)]):
        pts = _bend([(sx_ + 6, sy_ - 9), (sx_ - 3, sy_), (sx_ + 6, sy_ + 9)], ph, amp, tamp)
        inner.append(line(pts, lw * .5, SCALE, taper=.6, wmin=.25, seed=320 + k))
    # жаберная дуга
    inner.append(line(_bend([(40, -50), (27, -16), (28, 20), (40, 48)], ph, amp, tamp), lw * .8, INK, taper=.6, wmin=.25, seed=330))
    out.append(shape(body, BODY, "".join(inner), w=lw, seed=331))
    # медалька-ракушка на ленте
    if medal > 0.01:
        m = clamp(medal)
        band = _bend([(16, -70, 1), (25, -71, 1), (31, 0), (29, 66, 1), (20, 66, 1), (22, 0)], ph, amp, tamp)
        out.append(shape(band, "#d6342c", "", w=lw * .6, seed=340))
        sw = 8 * math.sin(t * 3.1)
        mx, my = 27, 66 + 48 * m
        out.append(line([(25, 62), (mx + sw * .5, my - 26)], lw * .9, "#d6342c", seed=341, taper=.1, wmin=.9))
        disc = _rot(ellipse_pts(mx, my, 30, 30, 18), mx, my - 30, sw)
        inner = blob(_rot(ellipse_pts(mx + 8, my + 8, 24, 22, 14), mx, my - 30, sw), "#e0a21e")
        sh = [(mx - 15, my + 5), (mx - 13, my - 6), (mx - 6, my - 13), (mx, my - 15), (mx + 6, my - 13), (mx + 13, my - 6), (mx + 15, my + 5),
              (mx + 6, my + 9, 1), (mx - 6, my + 9, 1)]
        rib = "".join(line(_rot([(mx, my + 8), (mx + 11 * a, my - 10)], mx, my - 30, sw), lw * .4, "#b9781a", seed=342 + k,
                           taper=.2, wmin=.6) for k, a in enumerate((-0.9, -0.3, 0.3, 0.9)))
        inner += shape(_rot(sh, mx, my - 30, sw), "#fff0d0", rib, w=lw * .5, seed=345)
        inner += blob(_rot(ellipse_pts(mx - 14, my - 14, 6, 4, 8, rot=-40), mx, my - 30, sw), "#fff6c8")
        out.append(shape(disc, "#f6c443", inner, w=lw * .75, seed=343))
    # грудной плавник (ближний) — машет
    pa = 18 * math.sin(ph * 1.4) * fin - 6
    pect = _rot([(p[0] + 18, p[1] + 14) for p in _PECT], 18, 14, pa)
    out.append(shape(_bend(pect, ph, amp, tamp), FIN, line(_bend(_rot([(18, 16), (-12, 46)], 18, 14, pa), ph, amp, tamp), lw * .45, RAY,
                                                              seed=350), w=lw * .85, seed=351))
    # рот
    if mouth_open is None:
        mouth_open = 0.2 + 0.2 * math.sin(t * 5.3)
    out.append(_mouth(mouth, mouth_open, lw, ph))
    # глаза: дальний (выпуклый, за носом) и ближний
    ey0 = math.sin(ph - 60 * 0.022) * 0  # глаза на голове — изгиба нет
    closed_far = 1 if happy > 0.5 else 0
    closed_near = 1 if happy > 0.5 else (2 if wink > 0.92 else 0)
    lid_near = max(lid, min(1.0, wink * 1.1)) if wink <= 0.92 else lid
    out.append(_eye(88, -34 + ey0, 20, 26, lw, look, lid, closed_far, blank, 360, brow=brow * 0.8 if brow > 0 else 0.0, sq=sq))
    out.append(_eye(58, -26 + ey0, 29, 33, lw, look, lid_near, closed_near, blank, 370, brow=brow, sq=sq))
    out.append("</g>")
    return "".join(out)


def nose(x, y, s, face, rot=0.0):
    """Мировая точка носа рыбки (для нажатия рычажка и еды)."""
    fa = face if abs(face) > 0.16 else math.copysign(0.16, face)
    lx, ly = 108 * s * fa, 6 * s
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return x + lx * c - ly * sn, y + lx * sn + ly * c


def bubble(x, y, r, lw=3.2, seed=0):
    """Пузырёк: светлый круг с контуром и бликом (без полупрозрачности фигуры)."""
    s = shape(ellipse_pts(x, y, r, r, 12), "#d9f2f7", blob(ellipse_pts(x + r * .25, y + r * .3, r * .7, r * .55, 10), "#b5e1ec"),
              w=lw, seed=seed, ink_color="#2a5a6e")
    s += f'<circle cx="{f(x - r * .35)}" cy="{f(y - r * .35)}" r="{f(r * .28)}" fill="#ffffff"/>'
    return s


def sparkle(x, y, r, rot=0.0, color="#ffd84a", lw=3.0, seed=0):
    """Четырёхлучевая искорка с контуром."""
    pts = []
    for k in range(8):
        a = math.radians(rot + k * 45)
        rr = r if k % 2 == 0 else r * 0.32
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a), 1))
    return shape(pts, color, "", w=lw, seed=seed)


_unused = (DEFS, uid)
