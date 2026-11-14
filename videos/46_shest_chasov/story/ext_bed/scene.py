"""Сцена bed рилса 37 «девять раз ещё 5 минут»: планы s02, s07, s08, s10, s11, s12, s13. frame(sid, t) -> SVG 1080×1920
(t — общее время ролика). Мир — bedroom.py (комната утром, диван-кровать, тумбочка), Дима — голова и руки из
people.py рилса 33 (лежит на спине головой влево, лицо вверх, тело под пледом), кот — desk/cat.py рилса 33 (эталон
look/hero.png: ЛЕВОЕ от зрителя ухо загнуто), будильник — clock/alarm.py соседней сцены (один предмет во всех сценах).
Удары — на словах по voice/words.json.
"""
import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import bedroom as B  # noqa: E402  (кладёт desk рилса 33 в sys.path)
import cat as Cat  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, smooth  # noqa: E402

_sp = importlib.util.spec_from_file_location("alarm37", os.path.join(HERE, "alarm.py"))
AL = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(AL)

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after and w["word"].strip(".,!?").lower() == word:
            return w["start"]
    raise KeyError(word)


BS = 0.62                          # масштаб Димы (L-единицы → мир)
HEAD = np.array([382.0, 1030.0])   # центр головы на подушке
HEAD_ROT = -50.0                   # лицо вверх, чуть к зрителю
PILLOW = (360.0, 1086.0)
SHOULDER = np.array([560.0, 1056.0])
ALX, ALS = 141.0, 62.0                         # будильник рилса 46 крупнее, по центру тумбочки
ALCY = B.NS[2] - AL.FOOT_Y / 200 * ALS        # центр циферблата будильника на тумбочке


# ═════════════════════════ мелочи ═════════════════════════
def osc(t, f, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def punch(t, t0, amp=.08, up=.06, down=.35):
    if t < t0:
        return 0.0
    if t < t0 + up:
        return amp * ease_out((t - t0) / up, 2)
    return amp * (1 - ease_io(clamp((t - t0 - up) / down)))


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return np.array(a, float) + (np.array(b, float) - np.array(a, float)) * u


def step12(t):
    return math.floor(t * 12) / 12


# ═════════════════════════ глаза-оверрайды для лежащего Димы ═════════════════════════
_eyes0 = people.eyes


def eyes37(expr, EN, EF, bags=True, lash_col=INK):
    mode = expr.get("eyes")
    if mode not in ("sleep", "squeeze"):
        return _eyes0(expr, EN, EF, bags, lash_col)
    C = people.C
    s = []
    for (cx, cy, rx, ry), sd in [(EF, 160), (EN, 161)]:
        if bags:
            bag = [(cx - rx * .85, cy + ry * .55), (cx, cy + ry * 1.38), (cx + rx * .85, cy + ry * .55), (cx, cy + ry * .9)]
            s.append(blob(bag, "#a77f8c", .78))
        if mode == "sleep":
            # сомкнутые веки: дуга ресниц вниз, складка века над ней
            s.append(people.line([(cx - rx * .95, cy + ry * .05), (cx - rx * .3, cy + ry * .42), (cx + rx * .35, cy + ry * .42),
                                  (cx + rx * .95, cy + ry * .02)], 6.2, seed=sd + 80, taper=.4, wmin=.3))
            s.append(people.line([(cx - rx * .6, cy - ry * .35), (cx, cy - ry * .2), (cx + rx * .6, cy - ry * .32)], 2.4, C["SKIN_SH2"],
                                 seed=sd + 81, op=.8))
        else:
            # зажмурился: глаз — сжатая складка «>», морщинки у внешнего угла
            s.append(people.line([(cx - rx * .9, cy - ry * .3), (cx - rx * .1, cy + ry * .05), (cx + rx * .9, cy - ry * .25)], 6.8,
                                 seed=sd + 82, taper=.35, wmin=.35))
            s.append(people.line([(cx - rx * .7, cy + ry * .4), (cx, cy + ry * .22), (cx + rx * .7, cy + ry * .38)], 2.6, C["SKIN_SH2"],
                                 seed=sd + 83, op=.9))
            for j, dy in enumerate((-.3, .05, .4)):
                s.append(people.line([(cx + rx * 1.0, cy + ry * dy * .6), (cx + rx * 1.35, cy + ry * dy)], 2.2, C["SKIN_SH2"], seed=sd + 84 + j))
    return "".join(s)


people.eyes = eyes37


_LAST_HEAD = [HEAD, HEAD_ROT]


def head_svg(expr, pos=HEAD, rot=HEAD_ROT, k=BS):
    people.C = people.PAL["dima"]
    _LAST_HEAD[:] = [np.array(pos, float), rot]
    return f'<g transform="translate({pos[0]:.2f} {pos[1]:.2f}) rotate({rot:.3f}) scale({k:.4f})">{people.dima_head(expr)}</g>'


def head_pt(p, pos=HEAD, rot=HEAD_ROT, k=BS):
    """Точка головы (L-единицы) → мир."""
    a = math.radians(rot)
    x, y = p[0] * k, p[1] * k
    return np.array([pos[0] + x * math.cos(a) - y * math.sin(a), pos[1] + x * math.sin(a) + y * math.cos(a)])


def neck_svg(pos=HEAD, rot=HEAD_ROT):
    """Шея и ворот худи между подбородком и пледом."""
    people.C = people.PAL["dima"]
    a = head_pt((-6, 116), pos, rot)
    b = head_pt((-40, 190), pos, rot)
    nk = lib.band([tuple(a), tuple((a + b) / 2), tuple(b)], 80 * BS, 86 * BS, step=4, cap=False)
    o = shape(nk, people.C["SKIN"], blob([tuple(p) for p in nk[len(nk) // 2:]], people.C["SKIN_SH"], .9), w=4.0, seed=890)
    return o


# ═════════════════════════ рука ═════════════════════════
def arm_svg(S, target, hs, side=-1, far=False, seed=0):
    """Рука от плеча S (мир) к запястью target (мир): рукав худи + кисть (hand.py). hs — dict кисти: dir, curl, spread,
    thumb, bend, flip; kind='open' | 'none'."""
    people.C = people.PAL["dima"]
    S = np.array(S, float)
    L = (np.array(target, float) - S) / BS
    E, Wr = people.ik2((0, 0), L, people.UPPER, people.FORE, side)
    d = (Wr - E) / np.linalg.norm(Wr - E)
    if hs.get("dir") is not None:
        d = np.array(hs["dir"], float)
        d /= np.linalg.norm(d)
    o = people.sleeve(np.array([0.0, 0.0]), E, Wr, far, 600 + seed, "dima")
    if hs.get("kind", "open") == "open":
        kw = people.hand_kw()
        o += Hand.hand(Wr + d * 2, d, flip=hs.get("flip", 1), k=hs.get("k", 1.0), curl=hs.get("curl", (.15, .1, .15, .2)),
                       spread=hs.get("spread", .2), thumb=hs.get("thumb", .2), bend=hs.get("bend", .1), seed=700 + seed, nails=True, **kw)
    wr_w = S + Wr * BS
    return f'<g transform="translate({S[0]:.2f} {S[1]:.2f}) scale({BS})">{o}</g>', wr_w, S + (Wr + d * 70) * BS


# ═════════════════════════ плед на Диме ═════════════════════════
BODY_TOP = [(512, 1078), (540, 1026), (600, 1000), (690, 994), (790, 1004), (890, 1018), (980, 1040), (1060, 1050), (1102, 1034, 1), (1128, 1008),
            (1158, 1012), (1170, 1048), (1176, 1100)]
HEM = [(1180, 1160), (1172, 1236), (1110, 1250), (1000, 1236), (880, 1252), (760, 1238), (640, 1254), (548, 1240), (508, 1196), (500, 1130)]
CAP = [(512, 1012), (482, 972), (430, 940), (364, 934), (306, 960), (280, 1022), (286, 1080)]


PDX = -36.0
BODY_TOP = [(p[0] + PDX * (1 - max(0, p[0] - 900) / 280), p[1]) + tuple(p[2:]) for p in BODY_TOP]
HEM = [(p[0] + PDX * (1 - max(0, p[0] - 900) / 280), p[1]) for p in HEM]
CAP = [(p[0] + PDX, p[1]) for p in CAP]


def plaid_pts(cover=0.0, breath=0.0, legs=0.0):
    top = [(x, y - breath * (1 if 560 < x < 900 else 0) + (legs if x > 1000 else 0)) + tuple(p[2:]) for (x, y, *_), p in
           zip(BODY_TOP, BODY_TOP)]
    if cover <= 0.01:
        return top + HEM
    # плед натянут на голову: шапка идёт от плеча к затылку, доля cover
    n = len(CAP)
    m = cover * (n - 1)
    cap = []
    for i in range(int(m) + 1):
        cap.append(CAP[i])
    if m - int(m) > 1e-3 and int(m) + 1 < n:
        a, b = np.array(CAP[int(m)]), np.array(CAP[int(m) + 1])
        cap.append(tuple(a + (b - a) * (m - int(m))))
    # от края шапки — вниз к подушке
    edge = cap[-1]
    left = [(edge[0] - 6, edge[1] + 30), (edge[0] - 2, 1110), (edge[0] + 30, 1150)] if cover < .99 else [(276, 1110), (300, 1150)]
    return list(reversed(cap)) + top[1:] + HEM[:-2] + [(HEM[-2][0], HEM[-2][1]), left[-1]] + list(reversed(left[:-1]))


def plaid_svg(cover=0.0, breath=0.0, legs=0.0, seed=8090):
    pts = plaid_pts(cover, breath, legs)
    folds = [[(620, 1060), (700, 1100), (760, 1180)], [(880, 1070), (920, 1150), (930, 1230)], [(1040, 1090), (1090, 1170)]]
    return B.plaid(pts, folds, seed=seed, shade_y=1158)


# ═════════════════════════ будильник ═════════════════════════
def alarm(cx, cy, size=ALS, ring=0.0, t=0.0, press=0.0, rot=0.0, hh=7.0, mm=0.0, uid="ab", squash=1.0):
    return AL.alarm(cx, cy, size=size, hh=hh, mm=mm, ring=ring, t=t, press=press, rot=rot, uid=uid, squash=squash)


def alarm_on_stand(t, ring=1.0, press=0.0, marks=True, hh=7.0, mm=0.0):
    o = AL.shadow(ALX, B.NS[2] + 2, ALS, .3)
    o += alarm(ALX, ALCY, ring=ring, t=t, press=press, hh=hh, mm=mm)
    if marks and ring > 0.05:
        o += AL.ring_marks(ALX, ALCY, ALS, t, ring, seed=9)
    return o


# ═════════════════════════ кадр ═════════════════════════
def setup(mode="night", u=1.0):
    """Комната: ночь / рассвет (evening с u от 1 к 0) / вечер."""
    B.den.set_tod(mode, u)
    B.den.WIN = (600.0, 250.0, 960.0, 770.0)
    B.den.MOON = None


def compose(world, cam, shake=(0.0, 0.0, 0.0), dark=0.0, glows="", tint="#1b2557", over=""):
    """dark 0..1 — ночное затемнение (multiply), glows — свет поверх (screen) в мировых координатах, over — экранный слой."""
    cx, cy, s, r = cam
    set_ink(s)
    dk = ""
    if dark > 0.005:
        dk = (f'<rect x="-1400" y="-1600" width="4600" height="4400" fill="{tint}" opacity="{dark:.3f}" '
              f'style="mix-blend-mode:multiply"/>')
    o = [f'<rect width="1080" height="1920" fill="#0e1430"/>',
         f'<g transform="translate({shake[0]:.2f} {shake[1]:.2f}) rotate({shake[2]:.3f} 540 960)">'
         f'<g transform="{lib.cam(cx, cy, s, r)}">{world}{dk}{glows}</g></g>', vignette(), over]
    return lib.svg("".join(o))


def vignette():
    g = lib.rad_grad([(0, "#0a0c1e", 0), (.62, "#0a0c1e", 0), (1, "#0a0c1e", .28)], 540, 880, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def focus_cam(fx, fy, s, rot=0.0, screen_y=820.0):
    """Точка мира (fx, fy) — на экранную высоту screen_y (над полосой субтитров)."""
    return (fx, fy + (960 - screen_y) / s, s, rot)


def shake_at(t, t0, amp=14.0, dur=.35, f=19.0):
    b = bump(t, t0, dur) if t >= t0 else 0.0
    if t >= t0 and t < t0 + dur * .5:
        b = max(b, 1 - (t - t0) / (dur * .5) * .3)
    return (amp * b * osc(t, f), amp * .7 * b * osc(t, f * 1.3, 1), .8 * b * osc(t, f * .8, 2))


def bed_world(t, *, head="", under_pillow="", pillow_kw=None, arm_back="", plaid="", front="", stand="", over_head=""):
    pk = dict(k=1.0, dent=.5)
    pk.update(pillow_kw or {})
    w = [B.back_world(t), stand, under_pillow, B.pillow(*PILLOW, **pk), neck_svg(*_LAST_HEAD), head, over_head, arm_back, plaid, front]
    return "".join(w)


# ═════════════════════════ планы ═════════════════════════
def sleep_expr(t, **kw):
    e = dict(eyes="sleep", brows="calm", mouth="flat", hair=0.0)
    e.update(kw)
    return e


def fingers_over(a, b, k=1.0):
    """Кончики четырёх пальцев, загнутые через край пледа (кисть — под пледом): край от a к b."""
    people.C = people.PAL["dima"]
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    d /= np.linalg.norm(d) + 1e-9
    n = np.array([d[1], -d[0]])          # наружу от пледа
    o = []
    for i in range(4):
        c = a + d * (14 + i * 15) * k
        root = c - n * 4 * k
        tip = c + n * (13 - 2 * abs(i - 1.5)) * k
        pts = lib.band([tuple(root), tuple((root + tip) / 2), tuple(tip)], 15 * k, 13 * k, step=2, cap=True)
        nail = ellipse_pts(*(tip - n * 3 * k), 4 * k, 3 * k, 8)
        o.append(shape(pts, people.C["SKIN"], blob(nail, people.C["NAIL"]) +
                       blob([tuple(c - n * 6 * k + d * 6 * k), tuple(tip + d * 6 * k), tuple(tip + d * 8 * k), tuple(c - n * 6 * k + d * 9 * k)],
                            people.C["SKIN_SH"], .7), w=2.8, seed=9500 + i))
    return "".join(o)


def path(t, keys, ease=ease_io):
    """Кусочно-гладкий путь по ключам [(t, (x, y)), ...]."""
    if t <= keys[0][0]:
        return np.array(keys[0][1], float)
    for (ta, a), (tb, b) in zip(keys, keys[1:]):
        if t <= tb:
            return lerp2(a, b, ease((t - ta) / (tb - ta)))
    return np.array(keys[-1][1], float)


def ring_lines(cx, cy, r, t, n=6, amp=1.0, col=INK, seed=9100):
    """Короткие штрихи звона вокруг точки (приглушённый звон из-под подушки / одеяла)."""
    o = []
    for j in range(n):
        a = -math.pi * (0.1 + 0.8 * j / max(1, n - 1))
        ph = (t * 8 + j * .37) % 1.0
        r0 = r + 10 * ph
        L = 22 * amp * (1 - .5 * ph)
        p0 = (cx + r0 * math.cos(a), cy + r0 * math.sin(a))
        p1 = (cx + (r0 + L) * math.cos(a), cy + (r0 + L) * math.sin(a))
        o.append(line([p0, p1], 5.5 * amp, col, seed=seed + j, taper=.3, wmin=.4))
    return "".join(o)


def click_star(x, y, u, k=1.0, col="#ffd36a"):
    if u <= 0 or u >= 1:
        return ""
    o = []
    for j in range(7):
        a = math.radians(-90 + (j - 3) * 26)
        r0, r1 = (18 + 30 * u) * k, (34 + 46 * u) * k
        w = 7 * k * (1 - u * .6)
        o.append(line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))], w + 3, INK, seed=9200 + j,
                      taper=.3, wmin=.4))
        o.append(line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))], w, col, seed=9210 + j,
                      taper=.3, wmin=.4))
    return "".join(o)


def zee(x, y, h, seed=0, col="#3d4f86"):
    """Буква Z пером (не шрифт): верх, диагональ, низ."""
    w = h * .8
    pts = [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2, 1), (x - w / 2, y + h / 2, 1), (x + w / 2, y + h / 2)]
    return (line(pts, h * .26, INK, taper=.15, wmin=.7, seed=seed) + line(pts, h * .15, col, taper=.15, wmin=.7, seed=seed + 1))


def zzz(x, y, t, t0, scale=1.0):
    o = []
    for j in range(4):
        st = t0 + j * .42
        u = (t - st) / 1.3
        if u <= 0 or u >= 1:
            continue
        sc = scale * (0.5 + 0.7 * u) * (1 if u < .82 else 1 - (u - .82) / .18)
        if sc <= .05:
            continue
        o.append(zee(x + 40 * scale * u + 12 * scale * osc(t, 1.2, j), y - 150 * scale * u, 46 * sc, seed=9300 + 7 * j))
    return "".join(o)


def bubble(x, y, r, wob=0.0, ang=-40.0):
    """Пузырь из носа: x, y — у ноздри, растёт вдоль ang (град, мир)."""
    if r < 1:
        return ""
    a = math.radians(ang)
    cx, cy = x + math.cos(a) * r * .92, y + math.sin(a) * r * .92
    sx, sy = 1 + .12 * wob, 1 - .12 * wob
    pts = ellipse_pts(0, 0, r * sx, r * sy, 24)
    pts = [(cx + p[0] * math.cos(a) - p[1] * math.sin(a), cy + p[0] * math.sin(a) + p[1] * math.cos(a)) for p in pts]
    o = f'<path d="{lib.fill_d(pts)}" fill="#bfe3f5" fill-opacity=".42"/>'
    o += blob(ellipse_pts(cx - r * .35, cy - r * .38, r * .2, r * .12, 10, rot=-35), "#ffffff", .95)
    o += blob(ellipse_pts(cx + r * .4, cy + r * .3, r * .07, r * .05, 8), "#ffffff", .9)
    o += f'<path d="{lib.ink_closed(pts, 3.4 * lib.INK_K[0], seed=9400)}" fill="#3d6f8a"/>'
    return o



CAT_K = .46
CAT_BACK = np.array([434.0, 852.0])         # кот на спинке дивана (точка между задних лап)
CAT_FACE = np.array([468.0, 1030.0])        # кот сидит на лице


def cat_state(t, **kw):
    st = dict(tilt=0.0, turn=0.0, look=(0.0, 0.0), blink=0.0, ear=0.0, perk=0.0, tail=0.0, smile=0.0, flame_e=1.0)
    st.update(kw)
    return st


def cat_svg(x, y, k, st, t, sx=1.0, sy=1.0, rot=0.0):
    c = Cat.draw(0, 0, k, st, t)
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({sx:.4f} {sy:.4f})">{c}</g>'




# ═════════════════════════ рилс 46: общие помощники ═════════════════════════
def hook_zoom(t, t0=0.0, mx=0.4, dur=0.22, rot=-3.0):
    """Влёт (правила 28/29): масштаб 1/(1+mx) → 1.05 за dur, отскок к 1; поворот rot → +0.8 → 0."""
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


def whip_in(t, t0, dur=0.2):
    return 1 - ease_out(clamp((t - t0) / dur), 3)


def glow_at(x, y, r, col, op, rx=None, ry=None):
    g = lib.rad_grad([(0, col, op), (1, col, 0)], x, y, rx or r, ry or r)
    return f'<rect x="{x - (rx or r):.0f}" y="{y - (ry or r):.0f}" width="{2 * (rx or r):.0f}" height="{2 * (ry or r):.0f}" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def digital(txt, x=540, y=300, size=150, col="#ffe9a8", bg="#14182e", pop=0.0, rot=0.0):
    """Экранная плашка с цифрами времени (кодом, шрифт IDB): крупно, читается без звука."""
    k = 1 + .12 * pop
    w, h = size * 3.3, size * 1.35
    return (f'<g transform="translate({x} {y}) rotate({rot:.2f}) scale({k:.3f})">'
            f'<rect x="{-w / 2 + 8}" y="{-h / 2 + 12}" width="{w}" height="{h}" rx="{h * .22}" fill="#000" opacity=".28"/>'
            f'<rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="{h * .22}" fill="{bg}" stroke="#1c1622" stroke-width="7"/>'
            f'<rect x="{-w / 2 + 12}" y="{-h / 2 + 12}" width="{w - 24}" height="{h - 24}" rx="{h * .16}" fill="none" stroke="#ffffff" opacity=".12" stroke-width="3"/>'
            f'<text x="0" y="{size * .36}" text-anchor="middle" font-family="IDB" font-size="{size}" fill="{col}" letter-spacing="2">{txt}</text></g>')


mix_c = B.mix_c


def sconce(on=1.0, x=140.0, y=790.0):
    """Настенное бра над тумбочкой: кронштейн, абажур; on — свет (0..1)."""
    o = [shape([(x - 8, y - 150), (x + 8, y - 150), (x + 8, y - 20), (x - 8, y - 20)], "#6b4a2c", "", w=3.4, seed=4601)]
    sh = [(x - 30, y - 10, 1), (x + 30, y - 10, 1), (x + 62, y + 52), (x - 62, y + 52)]
    col = mix_c("#c9a35e", "#ffe9a8", on)
    o.append(shape(sh, col, blob([(x + 14, y - 10), (x + 30, y - 10), (x + 62, y + 52), (x + 30, y + 52)], "#9e7c3c", .7 * (1 - .4 * on)), w=4.0, seed=4602))
    o.append(blob(ellipse_pts(x, y + 53, 60, 9, 14), "#fff4c8" if on > .3 else "#6e5d3a", .95 if on > .3 else .8))
    return "".join(o)


def sconce_light(on, x=140.0, y=790.0):
    if on <= 0.01:
        return ""
    cone = [(x - 55, y + 52), (x + 55, y + 52), (x + 330, 1330), (x - 330, 1330)]
    g = lib.lin_grad([(0, "#ffdc90", .5 * on), (1, "#ffdc90", 0)], 0, 0, 0, 1)
    return (f'<path d="{lib.fill_d([p + (1,) for p in cone])}" fill="url(#{g})" style="mix-blend-mode:screen" {lib.blur(14)}/>' +
            glow_at(x, y + 60, 300, "#ffd27a", .5 * on))


def stand46(t, ring=0.0, press=0.0, hh=0.0, mm=0.0, marks=True):
    o = AL.shadow(ALX, B.NS[2] + 2, ALS, .3)
    o += alarm(ALX, ALCY, ring=ring, t=t, press=press, hh=hh, mm=mm, size=ALS)
    if marks and ring > 0.05:
        o += AL.ring_marks(ALX, ALCY, ALS, t, ring, seed=9)
    return o


def snore_open(t, f=.9):
    return .5 + .5 * math.sin(2 * math.pi * f * t)


# ═════════════════════════ s01: хук, часы 00:00 → 06:00, луна гаснет, светает ═════════════════════════
def s01(t):
    u = clamp(t / 1.45)
    k = 1 - (1 - u) ** 2.3
    M = 360.0 * k                          # минут: 0 → 360 (6 часов)
    sk = 1.0 - smooth(0.0, 1.45, t)        # 1 ночь → 0 рассвет
    setup("evening", .001 + .999 * sk)
    B.den.MOON = (700.0, 330 + 420 * (1 - sk), 34.0, clamp(sk * 1.6))
    lib.dyn_begin()
    ring = smooth(1.28, 1.42, t)
    hh, mm = 0.0, M
    breath = 3.4 * osc(t, 1.7)
    e = sleep_expr(t, brows="calm", mouth="talk", open=snore_open(t, 1.5) * .6)
    head = head_svg(e, HEAD, HEAD_ROT + 1.6 * osc(t, 1.7))
    stand = stand46(t, ring, hh=hh, mm=mm)
    # размытие вращения: клин за минутной стрелкой
    sweep = ""
    if u < .98:
        ang = math.radians((M % 60) * 6 - 90)
        r0 = ALS * 1.18
        wedge = [(ALX, ALCY)] + [(ALX + r0 * math.cos(ang - a), ALCY + r0 * math.sin(ang - a)) for a in np.linspace(0, 1.9, 9)]
        sweep = lib.blob(wedge, "#fbf0d6", .45 * (1 - u))
    w = bed_world(t, head=head, plaid=plaid_svg(breath=breath), stand=stand + sweep,
                  over_head=zzz(HEAD[0] + 40, HEAD[1] - 80, t, -0.6, 1.1))
    zf, zr = hook_zoom(t, 0.0)
    s = 1.13 * zf
    dark = .16 + .62 * sk
    gl = glow_at(780, 520, 520, "#ffb878", .5 * (1 - sk) ** .8, 520, 420)
    gl += glow_at(ALX, ALCY, 150, "#fff1c0", .22 * sk + .1)
    gl += glow_at(780, 520, 460, "#9db8ff", .22 * sk)
    hx, mn = int(M // 60), int(M % 60)
    over = digital(f"{hx:02d}:{mn:02d}", 540, 215, 130, pop=bump(t, 1.4, .25) if t > 1.4 else 0.0)
    return compose(w, focus_cam(505, 880, s, zr, screen_y=800), (1.2 * osc(t, 21) * (1 - u), 0, 0), dark=dark, glows=gl, over=over)


SHOTS = {"s01": s01}


def frame(sid, t):
    return SHOTS[sid](t)


# ═════════════════════════ s02: звонок, Дима садится, «хватает» — большой палец и зевок ═════════════════════════
SIT_HIP = np.array([500.0, 1112.0])


def sit_plaid(hip, k=1.0, wob=0.0):
    """Плед на ногах Димы, сидящего в кровати: от бедра вправо горкой коленей до края дивана."""
    x0 = hip[0] - 70
    top = [(x0, hip[1] + 10, 1), (x0 + 40, hip[1] - 30), (x0 + 150, hip[1] - 54 + wob), (x0 + 300, hip[1] - 66 + wob), (x0 + 440, hip[1] - 52),
           (x0 + 560, hip[1] - 20 - wob), (1150, hip[1] + 10), (1180, hip[1] + 60, 1), (1176, 1236), (1000, 1246), (800, 1240), (600, 1250),
           (x0 + 10, 1236), (x0 - 10, 1160)]
    return B.plaid(top, [[(x0 + 150, hip[1] - 30), (x0 + 220, hip[1] + 40), (x0 + 250, hip[1] + 120)],
                         [(x0 + 420, hip[1] - 20), (x0 + 470, hip[1] + 60)]], seed=8090, shade_y=1158)


def dima_sit(t, lean, expr, arm_n, hand_n, arm_f=("ik", (700, 1090)), hand_f=None, hip=SIT_HIP, head_ang=0.0):
    p = dict(hip=tuple(hip), scale=BS, lean=lean, feet=None, arms={"n": arm_n, "f": arm_f}, hands={"n": hand_n, "f": hand_f or dict(kind="open", dir=(1, .2), curl=(.3, .35, .4, .45), spread=.05, thumb=.4)},
             expr=expr, head_ang=head_ang, hood=0.0, strings=(2 * osc(t, 1.3), 1.5 * osc(t, 1.1, 1)), pelvis=False)
    return people.draw(p, "dima")


T_HVAT = 2.84


def s02(t):
    setup("evening", .001)
    lib.dyn_begin()
    ring = 1.0 if t < T_HVAT + .5 else 0.0
    rise = ease_io(clamp((t - 1.32) / .55))
    lean = -1.45 * (1 - rise) - .06 * rise
    yawn = smooth(T_HVAT - .35, T_HVAT - .1, t) * (1 - smooth(T_HVAT + .9, T_HVAT + 1.15, t))
    e = dict(lid=.18 + .1 * yawn, look=(.3, .3), brows="tired", mouth="grin" if yawn > .2 else "tired", open=yawn, closed=0.0, hair=4 * rise)
    if yawn > .3:
        e["lid"] = 0.0
        e["closed"] = 1.0
    tu = smooth(T_HVAT - .1, T_HVAT + .15, t)
    # большой палец вверх
    arm_n = ("ik", tuple(SIT_HIP + np.array([250 - 40 * (1 - tu), -150 - 80 * tu + 60 * (1 - tu)])), -1)
    hand_n = dict(kind="open", dir=(1, -.2 * tu), curl=(.95, .95, .95, .95), spread=0.0, thumb=0.0 * tu + .7 * (1 - tu), bend=.0, flip=1)
    hp = SIT_HIP + np.array([160.0 * (1 - rise), 0.0])
    d = dima_sit(t, lean, e, arm_n, hand_n, hip=hp)
    cat = cat_svg(930, 862, .46, cat_state(t, look=(-.4, .4), blink=.62, tail=6 * osc(t, 1.3), ear=3 * bump(t, 2.1, .3), tilt=-4), t)
    lay = d["legs"] if "legs" in d else ""
    world = "".join([B.back_world(t), stand46(t, ring, hh=0.0, mm=360.0), B.pillow(*PILLOW, k=1.0, dent=.2 * (1 - rise)), cat,
                     d["arm_f"], d["body"], sit_plaid(hp, wob=2 * osc(t, 5) * ring), d["arm_n"]])
    s = 1.12 + .1 * clamp((t - 1.3) / 2.0)
    sh = shake_at(t, T_HVAT, 6, .3)
    gl = glow_at(780, 520, 460, "#ffb878", .4, 460, 380)
    return compose(world, focus_cam(560, 960, s, screen_y=820), (sh[0] + 1.5 * osc(t, 23) * ring, sh[1], sh[2]), dark=.2, glows=gl)


SHOTS["s02"] = s02


# ═════════════════════════ Дима стоит (s12, s13) ═════════════════════════
FLOOR_STAND = 1450.0
T_ZVEN, T_LECH = 27.52, 30.32


def note(x, y, s, col="#ffd36a", rot=0.0, seed=0):
    """Нота пером: головка-эллипс, штиль, флажок."""
    hd = ellipse_pts(0, 0, 15 * s, 11 * s, 12, rot=-25)
    o = blob([(x + p[0], y + p[1]) for p in hd], col)
    o += line([(x + 12 * s, y - 3 * s), (x + 13 * s, y - 56 * s), (x + 34 * s, y - 40 * s), (x + 30 * s, y - 26 * s)], 6 * s, INK, taper=.15, wmin=.7, seed=seed)
    o += line([(x + 12 * s, y - 3 * s), (x + 13 * s, y - 56 * s)], 3 * s, col, taper=.1, wmin=.9, seed=seed + 1)
    return f'<g transform="rotate({rot:.1f} {x:.1f} {y:.1f})">{o}</g>'


def dima_stand(t, hx, flip_x, expr, arm_n, hand_n, arm_f, hand_f, lean=0.04, feet=None, hip_y=None, head_ang=0.0, extra_back="", extra_front=""):
    hip_y = FLOOR_STAND - 356 if hip_y is None else hip_y
    hip = (hx, hip_y)
    feet = feet or {"n": ((hx + 36, FLOOR_STAND), 0.0), "f": ((hx - 30, FLOOR_STAND - 4), 0.0)}
    p = dict(hip=hip, scale=BS, lean=lean, feet=feet, arms={"n": arm_n, "f": arm_f}, hands={"n": hand_n, "f": hand_f}, expr=expr, head_ang=head_ang,
             hood=0.0, strings=(2 * osc(t, 1.3), 1.5 * osc(t, 1.1, 1)))
    d = people.draw(p, "dima")
    return d


def wrap_flip(svg, hx, sx):
    sx = max(.1, sx) if sx >= 0 else min(-.1, sx)
    return f'<g transform="translate({hx:.1f} 0) scale({sx:.4f} 1) translate({-hx:.1f} 0)">{svg}</g>'


def toothbrush(a, b, w=11.0):
    """Щётка от щетинок a (во рту) к концу ручки b."""
    a, b = np.array(a, float), np.array(b, float)
    d = (b - a) / (np.linalg.norm(b - a) + 1e-9)
    n = np.array([-d[1], d[0]])
    hd = [tuple(a + n * w * .7), tuple(a + d * 26 + n * w * .7), tuple(a + d * 26 - n * w * .7), tuple(a - n * w * .7)]
    o = shape([tuple(q) for q in [a + d * 20 + n * w * .45, b + n * w * .3, b - n * w * .3, a + d * 20 - n * w * .45]], "#4fa3d8",
              blob([tuple(a + d * 20), tuple(b), tuple(b - n * w * .3), tuple(a + d * 20 - n * w * .45)], "#2f7fb3", .8), w=3.0, seed=4620)
    o += shape([(hd[0]), hd[1], hd[2], hd[3]], "#ffffff", blob([hd[1], hd[2], tuple(a + d * 14 - n * w * .7), tuple(a + d * 14 + n * w * .7)], "#cfe3f0", .9), w=3.0, seed=4621)
    return o


def foam(x, y, k, t):
    if k <= .02:
        return ""
    o = ""
    for j, (dx, dy, r) in enumerate(((-26, 4, 13), (-8, 16, 15), (16, 14, 14), (34, 0, 12), (-40, -14, 10), (6, 26, 9))):
        rr = r * k * (1 + .08 * math.sin(t * 9 + j))
        o += shape(ellipse_pts(x + dx * k, y + dy * k, rr, rr, 10), "#ffffff", "", w=2.4, seed=4630 + j)
    return o


def s12(t):
    sk = 1.0
    setup("evening", .98)
    B.den.MOON = (700.0, 330, 34.0, 1.0)
    lib.dyn_begin()
    tick = 27.04
    mm = 59.0 + clamp((t - 26.7) / .34) ** 2
    hh = 10.0 if t < tick else 11.0
    if t >= tick:
        mm = 0.0
    ring = 1.0 if t >= T_ZVEN else 0.0
    flip = ease_io(clamp((t - (T_ZVEN - .05)) / .22))
    sx = math.cos(math.pi * flip)
    hx = 700.0
    brushing = t < T_ZVEN - .1
    stroke = 22 * osc(t, 3.2) if brushing else 0.0
    e_b = dict(lid=.25, look=(.3, .2), brows="tired", mouth="flat", closed=0.0, hair=0.0)
    e_s = dict(lid=1.0, look=(-.6, 0.1), brows="up", mouth="flat", closed=0.0, hair=6 * bump(t, T_ZVEN, .3))
    e = e_b if t < T_ZVEN - .05 else e_s
    # цель руки с щёткой — у рта
    probe = dima_stand(t, hx, 1, e, ("ik", (hx + 120, 1140), -1), dict(kind="none"), ("ik", (hx - 40, 1250)), dict(kind="none"))
    mouth = probe["head"] + np.array([64.0, 88.0]) * BS
    k_up = 1 - flip
    tgt = np.array([mouth[0] + 78, mouth[1] + 50]) * k_up + np.array([hx + 60, 1220]) * flip
    tgt = tgt + np.array([stroke * .8, stroke * .45]) * k_up
    hd = np.array([-.85, -.5]) if k_up > .5 else np.array([-.1, -1])
    d = dima_stand(t, hx, 1, e, ("ik", tuple(tgt), -1), dict(kind="open", dir=tuple(hd), curl=(.9, .92, .94, .95), spread=0.0, thumb=.6, flip=1),
                   ("ik", (hx - 50, 1250)), dict(kind="open", dir=(0, 1), curl=(.3, .35, .4, .4), spread=.05, thumb=.4))
    brush_a = mouth + np.array([6.0, 4.0]) + np.array([stroke * .6, stroke * .33]) * k_up
    brush_b = tgt + np.array(hd) * -1 * 0 + np.array([40.0, 24.0]) if k_up > .5 else tgt + np.array([6.0, -70.0])
    if k_up > .5:
        brush_a = brush_a
    brushsvg = toothbrush(brush_a, brush_b) if k_up > .5 else toothbrush(tgt + np.array([0.0, -50.0]), tgt + np.array([12.0, 20.0]))
    dm = "".join([d["legs"], d["arm_f"], d["body"], foam(mouth[0] + 2, mouth[1] + 4, (clamp((t - 25.9) / 1.2) * .5 + .2) * .8, t), brushsvg, d["arm_n"]])
    dm = wrap_flip(dm, hx, sx)
    world = "".join([B.back_world(t), stand46(t, ring, hh=hh, mm=mm), dm])
    # ноты
    nts = ""
    if t >= T_ZVEN:
        for j in range(5):
            u = ((t - T_ZVEN) * 1.5 + j * .21) % 1.0
            nts += note(ALX + 30 + 200 * u * (1 if j % 2 else .6) + 30 * math.sin(6 * u + j), ALCY - 120 - 260 * u, .9 * (.6 + u * .5), rot=12 * math.sin(5 * u + j), seed=4640 + j)
    zf = 1.0
    sh = shake_at(t, T_ZVEN, 8, .4) if t >= T_ZVEN else (0, 0, 0)
    cam = focus_cam(470, 1000, 1.15 + .06 * clamp((t - 25.7) / 3.3) + .06 * punch(t, T_ZVEN, 1, .06, .3), screen_y=640)
    gl = glow_at(ALX, ALCY, 200, "#fff1c0", .3 + .2 * ring)
    over = digital("23:00" if t >= tick else "22:59", 540, 215, 130, pop=bump(t, tick, .3), col="#ffe9a8" if t < tick else "#ff8a6a")
    # слой «вечерний свет» — лёгкий затемняющий
    return compose(world + nts, cam, (sh[0] + 1.2 * osc(t, 23) * ring, sh[1], sh[2]), dark=.5, glows=gl, over=over)


SHOTS["s12"] = s12


# ═════════════════════════ s13: Дима ныряет в кровать на «лечь», плед взлетает и опадает ═════════════════════════
T_JUMP, T_LAND = 30.16, 30.50
HX13 = 700.0
FOLD_X, FOLD_Y = (900.0, 1130.0), (1060.0, 1112.0)


def plaid_morph(u, t_fly):
    """u 0 — плед сложен на ногах кровати, 1 — накрывает Диму; между — взлетает дугой с трепетом."""
    full = plaid_pts(0.0, 0.0, 0.0)
    xs = [p[0] for p in full]
    x_lo, x_hi = min(xs), max(xs)
    ys = [p[1] for p in full]
    y_lo, y_hi = min(ys), max(ys)
    out = []
    for i, p in enumerate(full):
        fx = FOLD_X[0] + (p[0] - x_lo) / (x_hi - x_lo) * (FOLD_X[1] - FOLD_X[0])
        fy = FOLD_Y[0] + (p[1] - y_lo) / (y_hi - y_lo) * (FOLD_Y[1] - FOLD_Y[0])
        e = ease_io(u)
        x = fx + (p[0] - fx) * e
        y = fy + (p[1] - fy) * e
        lift = -230 * math.sin(math.pi * clamp(u)) ** 1.3
        flut = 22 * math.sin(math.pi * u) * math.sin(3.2 * i + t_fly * 14)
        out.append((x, y + lift + flut) + tuple(p[2:]))
    return out


def s13(t):
    setup("evening", .98)
    B.den.MOON = (700.0, 330, 34.0, 1.0)
    lib.dyn_begin()
    # фазы тела
    crouch = smooth(29.75, 30.08, t) * (1 - smooth(T_JUMP, T_JUMP + .04, t))
    fl = clamp((t - T_JUMP) / (T_LAND - T_JUMP))                 # полёт 0..1
    landed = t >= T_LAND
    lean = .04 + (1.5 - .04) * ease_io(clamp(fl * 1.15)) if t >= T_JUMP else .04 - .22 * crouch
    stretch = smooth(28.9, 29.45, t) * (1 - smooth(29.55, 29.85, t))
    hip_y = FLOOR_STAND - 356 + 62 * crouch
    hx = HX13
    if t >= T_JUMP:
        hip_y = (FLOOR_STAND - 356 + 0) * (1 - fl) + 1085 * fl - 190 * math.sin(math.pi * fl)
        hx = HX13 + (690 - HX13) * fl
    hip = np.array([hx, hip_y])
    ang = lean
    # ноги: стопы от бедра вдоль «назад-вниз» тела
    def foot(side_dx, lag):
        a = ang * (1 - .0) + lag
        rel = np.array([-356 * math.sin(a), 356 * math.cos(a)])
        if t < T_JUMP:
            return ((hx + side_dx, FLOOR_STAND - (0 if side_dx > 0 else 4)), 0.0)
        return ((hip[0] + rel[0] - (0 if side_dx > 0 else 18), hip[1] + rel[1]), ang * .9)
    feet = {"n": foot(36, .0), "f": foot(-30, -.25)}
    if landed:
        feet = {"n": ((hip[0] - 359 + 0, hip[1] + 30), 1.3), "f": ((hip[0] - 340, hip[1] + 50), 1.3)}
    # руки: потягивание вверх → вперёд-вверх в полёте → раскинуты
    sh_y = hip_y - 248
    if t < T_JUMP:
        up_t = (hx + 40, sh_y - 270)
        down_t = (hx + 60, hip_y + 150 + 20 * crouch)
        an = tuple(np.array(down_t) * (1 - stretch) + np.array(up_t) * stretch)
        af = (hx - 30, hip_y + 170 - 240 * stretch)
        sw = -60 * crouch
        an = (an[0] + sw, an[1])
    else:
        a = ang
        an = (hx + 300 * math.cos(a - .3 - .6 * (1 - fl)) * .9, hip_y - 300 * math.sin(a * .7) + 80)
        an = (hip[0] + 410 * math.sin(a) + 10, hip[1] - 410 * math.cos(a) + 60)
        af = (hip[0] + 380 * math.sin(a), hip[1] - 380 * math.cos(a) + 40)
    if t < T_JUMP:
        e = dict(lid=.2 + .6 * stretch * 0, look=(-.4, .2), brows="tired", mouth="grin" if stretch > .3 else "tired", open=stretch, closed=1.0 if stretch > .4 else 0.0, hair=0.0)
    else:
        e = dict(lid=0.0, look=(0, 0), brows="calm", mouth="smile", smile=1.0, closed=1.0, hair=8 * bump(t, T_LAND, .3))
    arm_n = ("ik", an, -1)
    arm_f = ("ik", af, -1)
    hn = dict(kind="open", dir=(0, -1), curl=(.2, .25, .3, .3), spread=.3, thumb=.3, flip=1)
    d = dima_stand(t, hx, 1, e, arm_n, hn, arm_f, hn, lean=lean, feet=feet, hip_y=hip_y)
    parts = [d["legs"], d["arm_f"], d["body"], d["arm_n"]]
    dm = wrap_flip("".join(parts), hx, -1.0)
    sq = .16 * math.exp(-7 * (t - T_LAND)) * math.cos((t - T_LAND) * 22) if landed else 0.0
    pil = B.pillow(*PILLOW, k=1.0, dent=.25 + 3 * sq, lift=-20 * sq, sq=1 - 2 * sq)
    pu = clamp((t - (T_LAND - .02)) / .62)
    pl_pts = plaid_morph(pu, t) if pu < 1 else plaid_pts(0.0, 3 * osc(t, 1.7) * smooth(0.95, 1, pu))
    pid_folds = [[(620, 1060), (700, 1100), (760, 1180)], [(880, 1070), (920, 1150), (930, 1230)]]
    pl = B.plaid(pl_pts, pid_folds if pu >= .6 else (), seed=8090, shade_y=1158)
    # кот на спинке: вздрагивает от удара
    cj = bump(t, T_LAND + .02, .35)
    cat = cat_svg(930, 862 - 26 * cj, .46, cat_state(t, look=(-.4, .5), blink=.55 if cj < .1 else 0.0, tail=8 * osc(t, 1.3) + 16 * cj, perk=cj, ear=6 * cj, smile=0.0), t,
                  sx=1 - .05 * cj, sy=1 + .09 * cj)
    # дугой «хлоп»: пыль и звёзды удара
    star = click_star(520, 1010, clamp((t - T_LAND) / .35), k=1.5, col="#fff3c0") if landed else ""
    world = "".join([B.back_world(t), sconce(1.0), stand46(t, 0.0, hh=11.0, mm=0.0, marks=False), pil, cat, dm, pl, star])
    sh = shake_at(t, T_LAND, 12, .4) if landed else (0, 0, 0)
    cam = focus_cam(500, 1040, 1.15 + .05 * clamp((t - 28.8) / 2.4), screen_y=760)
    gl = sconce_light(1.0) + glow_at(ALX, ALCY, 140, "#fff1c0", .2)
    return compose(world, cam, sh, dark=.45, glows=gl)


SHOTS["s13"] = s13


# ═════════════════════════ s15: кот доволен, на «гаснет» лампа гаснет, остаётся огонёк на хвосте ═════════════════════════
T_GASN = 34.16


def s15(t):
    setup("evening", .99)
    B.den.MOON = (700.0, 330, 34.0, 1.0)
    lib.dyn_begin()
    off = smooth(T_GASN - .02, T_GASN + .1, t)
    flick = 1.0 if t < T_GASN - .3 else (1.0 - .5 * (math.sin((t - T_GASN) * 60) > 0) * smooth(T_GASN - .3, T_GASN - .05, t))
    on = (1 - off) * flick
    CX_, CY_, CK = 650.0, 1022.0, .95
    st = cat_state(t, look=(.1, .1), blink=.55 + .1 * osc(t, .5), smile=1.0, tail=10 * osc(t, 1.1), tilt=3 * osc(t, .45), ear=6 * bump(t, 33.6, .3) + 5 * bump(t, 34.6, .3),
                   flame_e=1.0 + .25 * off)
    cat = cat_svg(CX_, CY_, CK, st, t)
    body = plaid_pts(1.0, 2.2 * osc(t, .9))
    pl = B.plaid(body, [[(620, 1060), (700, 1100), (760, 1180)], [(880, 1070), (920, 1150), (930, 1230)]], seed=8090, shade_y=1158)
    world = "".join([B.back_world(t), sconce(on), stand46(t, 0.0, hh=11.0, mm=0.0, marks=False), B.pillow(*PILLOW, k=1.0, dent=.3), pl, cat])
    fx, fy = CX_ + (995 - 836) * CK, CY_ + (1076 - 1306) * CK
    gl = sconce_light(on) + glow_at(ALX, ALCY, 140, "#fff1c0", .18 + .08 * off)
    gl += glow_at(fx, fy, 260, "#ff9a3c", .15 + .5 * off) + glow_at(fx, fy, 90, "#ffd27a", .3 + .4 * off)
    gl += glow_at(780, 520, 420, "#9db8ff", .12 + .12 * off, 420, 380)
    cam = focus_cam(430 + 40 * clamp((t - 32.8) / 2.7), 880, 1.0 + .3 * ease_io(clamp((t - 32.8) / 2.9)), screen_y=760)
    star = click_star(140, 850, clamp((t - T_GASN) / .35), k=1.3, col="#fff3c0") if t >= T_GASN else ""
    sh = shake_at(t, T_GASN, 4, .25) if t >= T_GASN else (0, 0, 0)
    return compose(world + star, cam, sh, dark=.45 + .38 * off, glows=gl)


SHOTS["s15"] = s15
