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

_sp = importlib.util.spec_from_file_location("alarm37", os.path.join(STORY, "clock", "alarm.py"))
AL = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(AL)

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after and w["word"].strip(".,!?").lower() == word:
            return w["start"]
    raise KeyError(word)


T_SEM = wt("семь")                 # 1.52
T_PRYATAL = wt("прятал")           # 7.92
T_PODUSHKU = wt("подушку")         # 9.00
T_KIDAL = wt("кидал")              # 9.68
T_UGOL = wt("угол")                # 10.40
T_VYKL = wt("выключил")            # 12.72
T_PROSN = wt("проснувшись")        # 13.96
T_KOT = wt("кот")                  # 15.36
T_LICO = wt("лицо")                # 16.64

BS = 0.62                          # масштаб Димы (L-единицы → мир)
HEAD = np.array([382.0, 1030.0])   # центр головы на подушке
HEAD_ROT = -50.0                   # лицо вверх, чуть к зрителю
PILLOW = (360.0, 1086.0)
SHOULDER = np.array([560.0, 1056.0])
ALX, ALS = B.ALARM
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
def compose(world, cam, shake=(0.0, 0.0, 0.0)):
    cx, cy, s, r = cam
    set_ink(s)
    o = [f'<rect width="1080" height="1920" fill="#8ea4b0"/>',
         f'<g transform="translate({shake[0]:.2f} {shake[1]:.2f}) rotate({shake[2]:.3f} 540 960)">'
         f'<g transform="{lib.cam(cx, cy, s, r)}">{world}{B.light()}</g></g>', vignette()]
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


# ═════════════════════════ s02: звенит; на «семь» морщится и тянет плед на голову ═════════════════════════
def s02(t):
    B.setup()
    lib.dyn_begin()
    wince = smooth(T_SEM - .06, T_SEM + .04, t)
    jolt = bump(t, T_SEM, .3)
    cover = ease_io(clamp((t - (T_SEM + .14)) / .42))
    hrot = HEAD_ROT + 5 * jolt + 2 * wince
    hpos = HEAD + np.array([-4 * jolt, -8 * jolt])
    if wince < .5:
        e = sleep_expr(t, brows="calm" if t < T_SEM - .3 else "det", mouth="flat", hair=0.0)
    else:
        e = dict(eyes="squeeze", brows="worry", mouth="grin", open=.0, hair=6 * jolt)
    head = head_svg(e, hpos, hrot) if cover < .98 else ""
    # кулак тянет край пледа: по краю шапки
    pts = plaid_pts(cover)
    front = ""
    if 0 < cover < 1 or (cover >= 1 and t < T_SEM + .9):
        lead = np.array(pts[0][:2], float)
        nxt = np.array(pts[1][:2], float)
        front = fingers_over(lead, nxt)
    wig = 4 * osc(t, 7) * clamp((t - T_SEM - .6) / .2) if cover >= 1 else 0.0
    pl = B.plaid([(p[0], p[1] - (wig if p[0] < 520 else 0)) + tuple(p[2:]) for p in pts],
                 [[(620, 1060), (700, 1100), (760, 1180)], [(880, 1070), (920, 1150), (930, 1230)]], seed=8090, shade_y=1158)
    w = bed_world(t, head=head, plaid=pl, front=front, stand=alarm_on_stand(t, 1.0))
    s = 2.05 + .12 * clamp((t - .8) / 1.5) + punch(t, T_SEM, .05, .05, .3)
    sh = shake_at(t, T_SEM, 7, .3)
    return compose(w, focus_cam(320, 1000, s, -.4 * jolt), (sh[0] + 1.5 * osc(t, 23), sh[1], sh[2]))



REST = (724.0, 1110.0)             # запястье, когда рука лежит поверх пледа
SH_W = np.array([500.0, 1060.0])   # плечо (под пледом)


def rest_arm():
    return arm_svg(SH_W, REST, dict(dir=(1, .15), curl=(.35, .4, .45, .5), spread=.05, thumb=.4), side=1, seed=0)


# ═════════════════════════ s07: прячет будильник под подушку, на «подушку» падает сверху ═════════════════════════
T7_GRAB, T7_UNDER, T7_OUT = T_PRYATAL, 8.72, 8.9


def s07(t):
    B.setup()
    lib.dyn_begin()
    grab_pt = np.array([ALX + 40, ALCY - 34])            # запястье над будильником
    under = np.array([318.0, 1056.0])                     # центр будильника под подушкой (левый край)
    # будильник
    if t < T7_GRAB:
        al_c, al_rot, carried = np.array([ALX, ALCY]), 0.0, False
    elif t < T7_UNDER:
        u = ease_io((t - T7_GRAB - .05) / (T7_UNDER - T7_GRAB - .05))
        mid = np.array([250.0, 930.0])
        p0 = np.array([ALX, ALCY])
        al_c = (1 - u) ** 2 * p0 + 2 * u * (1 - u) * mid + u * u * under
        al_rot, carried = -80 * u, True
    else:
        al_c, al_rot, carried = under, -80.0, False
    ring = 1.0
    # подушка: приподнята будильником, на «подушку» — голова падает
    lift = 0.0
    if t > T7_UNDER - .25:
        lift = 40 * ease_io((t - (T7_UNDER - .25)) / .3)
    drop = 0.0
    if t >= T_PODUSHKU:
        v = t - T_PODUSHKU
        drop = 14 * math.exp(-6 * v) * math.cos(v * 22)
        lift += 4 * osc(t, 11) * clamp(v / .1)
    head_up = 26 * smooth(T7_GRAB, T7_GRAB + .3, t) * (1 - smooth(T_PODUSHKU - .14, T_PODUSHKU, t))
    hpos = HEAD + np.array([0, -lift * .8 - head_up + drop])
    hrot = HEAD_ROT + 8 * head_up / 26
    e = sleep_expr(t, brows="det", mouth="flat")
    head = head_svg(e, hpos, hrot)
    # рука
    if t < T7_GRAB:
        u = ease_io((t - 7.56) / (T7_GRAB - 7.56))
        wr = lerp2(REST, grab_pt, u)
    elif t < T7_UNDER:
        wr = al_c + lerp2((40.0, -34.0), (-10.0, -62.0), smooth(T7_UNDER - .45, T7_UNDER - .1, t))
    elif t < T7_OUT:
        wr = under + np.array([-10.0, -62.0])
    else:
        wr = path(t, [(T7_OUT, under + np.array([-10.0, -62.0])), (T_PODUSHKU, (500.0, 960.0)), (T_PODUSHKU + .22, REST)])
    hd = lerp2((-.7, .7), (-.2, 1.0), smooth(T7_UNDER - .45, T7_UNDER - .1, t))
    curl = (.55, .6, .62, .65) if T7_GRAB - .03 < t < T7_OUT else (.2, .2, .25, .3)
    arm, _, _ = arm_svg(SH_W, wr, dict(dir=hd, curl=curl, spread=.08, thumb=.6), side=-1, seed=0)
    al_svg = alarm(al_c[0], al_c[1], ring=ring, t=t, rot=al_rot, uid="a7")
    stand = AL.shadow(ALX, B.NS[2] + 2, ALS, .3) if t < T7_GRAB else ""
    marks = ""
    if not carried and t < T7_GRAB:
        stand += al_svg + AL.ring_marks(ALX, ALCY, ALS, t, 1.0, seed=9)
        al_svg = ""
    under_p, front = "", ""
    if t >= T7_UNDER:
        under_p = al_svg
        marks = ring_lines(PILLOW[0] - 70, PILLOW[1] - lift - 40, 56, t, n=5, amp=.8)
    elif carried:
        front = al_svg + AL.ring_marks(al_c[0], al_c[1], ALS, t, .8, seed=19)
    w = bed_world(t, head=head, under_pillow=under_p, pillow_kw=dict(lift=lift, dent=.5, sq=1 + lift / 95), plaid=plaid_svg(), stand=stand,
                  front=front + marks, arm_back=arm)
    s = 2.05 + .1 * clamp((t - 7.56) / 2.3) + punch(t, T_PODUSHKU, .06, .05, .35)
    sh = shake_at(t, T_PODUSHKU, 8, .3)
    return compose(w, focus_cam(320, 1000, s), sh)


# ═════════════════════════ s08: общий план, швыряет будильник в угол на «угол» ═════════════════════════
T8_REL = 10.04
P8_HIT = np.array([B.CORNER_X - 52.0, 1110.0])
P8_FLOOR = np.array([B.CORNER_X - 90.0, B.FLOOR_Y + 30 - AL.FOOT_Y / 200 * ALS])


def s08(t):
    B.setup()
    lib.dyn_begin()
    hold = np.array([470.0, 770.0])
    wind = np.array([340.0, 800.0])
    thr = np.array([690.0, 780.0])
    if t < T_KIDAL + .05:
        wr = hold + np.array([6 * osc(t, 5), 4 * osc(t, 7)])
    elif t < 9.95:
        wr = lerp2(hold, wind, ease_io((t - T_KIDAL - .05) / (9.95 - T_KIDAL - .05)))
    elif t < T8_REL:
        wr = lerp2(wind, thr, ease_in((t - 9.95) / (T8_REL - 9.95), 2))
    else:
        wr = lerp2(thr, np.array(REST), ease_io((t - T8_REL - .1) / .55))
    head_up = 22 * (1 - smooth(T8_REL + .2, T8_REL + .6, t))
    hpos = HEAD + np.array([0, -head_up])
    head = head_svg(dict(eyes="sleep", brows="det", mouth="grin", open=0.0, hair=4 * bump(t, T8_REL, .3)), hpos, HEAD_ROT + 10 * head_up / 22)
    curl = (.6, .65, .68, .7) if t < T8_REL else (.1, .1, .15, .2)
    d_h = (0, -1) if t < 9.95 else (1, -.3)
    arm, _, _ = arm_svg(SH_W, wr, dict(dir=d_h, curl=curl, spread=.1, thumb=.5), side=-1, seed=0)
    # будильник
    trail = ""
    if t < T8_REL:
        al_c = wr + np.array([0.0, -72.0]) if t < 9.95 else wr + np.array([18.0, -70.0])
        al_rot, ring, sq = 12 * osc(t, 2), 1.0, 1.0
    elif t < T_UGOL:
        u = (t - T8_REL) / (T_UGOL - T8_REL)
        p0 = thr + np.array([18.0, -70.0])
        apex = np.array([1000.0, 520.0])
        al_c = (1 - u) ** 2 * p0 + 2 * u * (1 - u) * apex + u * u * P8_HIT
        al_rot, ring, sq = 540 * u, 1.0, 1.0
        for j in range(1, 5):          # штрихи полёта позади
            uu = max(0, u - j * .06)
            q = (1 - uu) ** 2 * p0 + 2 * uu * (1 - uu) * apex + uu * uu * P8_HIT
            q2 = (1 - (uu - .04)) ** 2 * p0 + 2 * (uu - .04) * (1 - (uu - .04)) * apex + (uu - .04) ** 2 * P8_HIT if uu > .04 else q
            trail += line([tuple(q2 + np.array([0, (j - 2.5) * 22])), tuple(q + np.array([0, (j - 2.5) * 22]))], 7, "#3a2a22", seed=9600 + j,
                          taper=.3, wmin=.3)
    else:
        v = t - T_UGOL
        if v < .08:
            al_c, sq = P8_HIT + np.array([8.0, 0]), .62 + 4.7 * v
            al_rot = 540
        else:
            u = clamp((v - .08) / .3)
            al_c = lerp2(P8_HIT + np.array([-20, 0]), P8_FLOOR, ease_in(u, 2)) + np.array([-50 * u, 0])
            al_rot, sq = 540 + 70 * u, 1.0
            if u >= 1:
                b = v - .38
                al_c = P8_FLOOR + np.array([0, -18 * abs(math.sin(b * 14)) * math.exp(-b * 9)])
        ring = .8
    al = alarm(al_c[0], al_c[1], ring=ring, t=t, rot=al_rot, squash=sq, uid="a8")
    fx = AL.ring_marks(al_c[0], al_c[1], ALS, t, ring * .9, seed=29) if t < T8_REL or t > T_UGOL + .4 else ""
    hit = ""
    if T_UGOL <= t < T_UGOL + .3:
        hit = click_star(P8_HIT[0] + 30, P8_HIT[1], (t - T_UGOL) / .3, k=2.2, col="#ffe08a")
    w = bed_world(t, head=head, plaid=plaid_svg(), arm_back=arm, front=trail + al + fx + hit, pillow_kw=dict(dent=.5))
    s = .78 + .04 * clamp((t - 9.48) / 1.6) + punch(t, T_UGOL, .05, .05, .35)
    sh = shake_at(t, T_UGOL, 18, .38)
    return compose(w, focus_cam(780, 900, s, 0.0, screen_y=800), sh)


# ═════════════════════════ s10: вслепую выключает будильник на «выключил» ═════════════════════════
def snore_mouth(t, f=.9):
    return .45 + .2 * osc(t, f)


def s10(t):
    B.setup()
    lib.dyn_begin()
    btn = np.array([ALX, ALCY - 1.06 * ALS])          # верх кнопки
    keys = [(12.06, REST), (12.3, (440, 920)), (12.5, (300, 880)), (12.64, (btn[0] + 56, btn[1] - 40)),
            (T_VYKL, (btn[0] + 50, btn[1] - 26)), (13.02, (btn[0] + 50, btn[1] - 26)), (13.5, REST)]
    wr = path(t, keys)
    wr = wr + np.array([5 * osc(t, 3.1), 4 * osc(t, 2.3)]) * (1 if 12.2 < t < 12.6 else 0)
    press = smooth(T_VYKL - .05, T_VYKL, t) * (1 - smooth(13.0, 13.12, t))
    ring = 1.0 - smooth(T_VYKL - .02, T_VYKL + .02, t)
    on_btn = 12.6 < t < 13.1
    hd = (-.86, .5) if on_btn else ((-.8, -.1) if t < 12.6 else (1, .3))
    curl = (0.0, .85, .9, .92) if 12.4 < t < 13.15 else (.25, .3, .35, .4)
    arm, _, _ = arm_svg(SH_W, wr, dict(dir=hd, curl=curl, spread=.02, thumb=.7, bend=.0), side=-1, seed=0)
    e = sleep_expr(t, brows="calm", mouth="talk", open=snore_mouth(t), smile=0.0)
    head = head_svg(e, HEAD, HEAD_ROT + 1.5 * osc(t, .9))
    st = alarm_on_stand(t, ring, press)
    fx = click_star(btn[0], btn[1] - 8, (t - T_VYKL) / .3, k=1.0)
    w = bed_world(t, head=head, plaid=plaid_svg(breath=4 * osc(t, .9)), stand=st, arm_back=arm, front=fx)
    s = 2.05 + .1 * clamp((t - 11.92) / 1.7) + punch(t, T_VYKL, .04, .05, .3)
    return compose(w, focus_cam(320, 990, s))


# ═════════════════════════ s11: крупно лицо, пузырь из носа, на «проснувшись» не лопается ═════════════════════════
def s11(t):
    B.setup()
    lib.dyn_begin()
    e = sleep_expr(t, brows="calm", mouth="talk", open=snore_mouth(t, .7) * .9, smile=0.0)
    hr = HEAD_ROT + 1.2 * osc(t, .7)
    head = head_svg(e, HEAD, hr)
    nost = head_pt((72, 58), HEAD, hr)
    grow = ease_out(clamp((t - 13.22) / (T_PROSN - 13.22)), 1.6)
    r = 6 + 40 * grow + 3 * osc(t, .7) * grow
    wob = 0.0
    if t >= T_PROSN:
        v = t - T_PROSN
        r = 46 + 7 * math.exp(-4 * v) * math.sin(v * 16) + 3 * osc(t, .7)
        wob = math.exp(-3.5 * v) * math.sin(v * 21)
    bub = bubble(nost[0], nost[1], r * .9, wob, ang=-32)
    zb = head_pt((10, -150), HEAD, hr)
    z = zzz(zb[0] + 10, zb[1] - 10, t, 13.0, scale=.4)
    w = bed_world(t, head=head, plaid=plaid_svg(breath=3 * osc(t, .7)), stand=alarm_on_stand(t, 0.0), over_head=bub + z)
    fc = head_pt((50, 20), HEAD, hr)
    s = 3.4 + .4 * clamp((t - 13.2) / 1.76) + punch(t, T_PROSN, .03, .06, .4)
    return compose(w, focus_cam(fc[0] + 30, fc[1] - 30, s, screen_y=820))


# ═════════════════════════ s12, s13: кот на спинке дивана, прыгает на «кот», садится на лицо ═════════════════════════
CAT_K = .46
CAT_BACK = np.array([434.0, 852.0])         # кот на спинке дивана (точка между задних лап)
CAT_FACE = np.array([480.0, 1006.0])        # кот сидит на лице


def cat_state(t, **kw):
    st = dict(tilt=0.0, turn=0.0, look=(0.0, 0.0), blink=0.0, ear=0.0, perk=0.0, tail=0.0, smile=0.0, flame_e=1.0)
    st.update(kw)
    return st


def cat_svg(x, y, k, st, t, sx=1.0, sy=1.0, rot=0.0):
    c = Cat.draw(0, 0, k, st, t)
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({sx:.4f} {sy:.4f})">{c}</g>'


def s12(t):
    B.setup()
    lib.dyn_begin()
    e = sleep_expr(t, brows="calm", mouth="talk", open=snore_mouth(t, .7) * .8, smile=0.0)
    head = head_svg(e, HEAD, HEAD_ROT + 1.2 * osc(t, .7))
    squint = smooth(14.85, 15.0, t) * .52
    blink = max(squint, 1.0 if abs(t - 14.68) < .06 else 0.0)
    crouch = smooth(15.1, T_KOT, t)
    st = cat_state(t, look=(.15, .95), blink=blink, tail=8 * osc(t, 1.4) + 14 * crouch, ear=6 * bump(t, 14.8, .25), tilt=-6 * squint,
                   perk=crouch)
    if t < T_KOT:
        c = cat_svg(CAT_BACK[0], CAT_BACK[1], CAT_K, st, t, sx=1 + .08 * crouch, sy=1 - .12 * crouch)
    else:
        u = clamp((t - T_KOT) / .36)
        apex = np.array([484.0, 760.0])
        p = (1 - u) ** 2 * CAT_BACK + 2 * u * (1 - u) * apex + u * u * CAT_FACE
        if u < 1:
            stretch = math.sin(math.pi * u)
            st2 = cat_state(t, look=(.1, .9), blink=0.0, tail=-20 * stretch, perk=1.0)
            c = cat_svg(p[0], p[1], CAT_K, st2, t, sx=1 - .08 * stretch, sy=1 + .14 * stretch, rot=14 * stretch)
        else:
            v = t - T_KOT - .36
            sq = .16 * math.exp(-7 * v) * math.cos(v * 20)
            st2 = cat_state(t, look=(0.0, .2), blink=.45 if v > .25 else 0.0, smile=1.0 if v > .25 else 0.0, tail=10 * osc(t, 1.2))
            c = cat_svg(CAT_FACE[0], CAT_FACE[1], CAT_K, st2, t, sx=1 + sq, sy=1 - sq)
    landed = t >= T_KOT + .36
    w = bed_world(t, head=head, plaid=plaid_svg(breath=3 * osc(t, .7)), stand=alarm_on_stand(t, 0.0),
                  front=c if landed else "", over_head="")
    if not landed:
        w = w + c
    s = 1.55 + .1 * clamp((t - 14.56) / 1.9) + punch(t, T_KOT + .36, .05, .05, .3)
    sh = shake_at(t, T_KOT + .36, 6, .3)
    return compose(w, focus_cam(470, 930, s, screen_y=820), sh)


def s13(t):
    B.setup()
    lib.dyn_begin()
    awake = smooth(T_LICO - .06, T_LICO, t)
    if awake < .5:
        e = sleep_expr(t, brows="calm", mouth="flat")
    else:
        e = dict(lid=1.0, look=(.55, -.85), brows="up", mouth="flat", hair=6 * bump(t, T_LICO, .3))
    jitter = 3 * osc(t, 9) * awake
    hr = HEAD_ROT + jitter
    head = head_svg(e, HEAD, hr)
    st = cat_state(t, look=(0.0, .1), blink=.5, smile=1.0, tail=14 * osc(t, 1.1), tilt=4 * osc(t, .6), ear=5 * bump(t, 16.9, .25))
    bob = 4 * awake * osc(t, 9, 1)
    c = cat_svg(CAT_FACE[0], CAT_FACE[1] + bob, CAT_K, st, t)
    arms = ""
    if t > T_LICO - .04:
        a = clamp((t - T_LICO + .04) / .12)
        for j, (S, base, f, ph) in enumerate([((540.0, 1066.0), (430.0, 880.0), 6.5, 0.0), ((600.0, 1050.0), (700.0, 860.0), 5.7, 1.7)]):
            tgt = np.array(base) + np.array([40 * osc(t, f, ph), 36 * osc(t, f * 1.3, ph + 1)])
            tgt = lerp2(REST, tgt, a)
            dd = tgt - np.array(S)
            arm_s, _, _ = arm_svg(S, tgt, dict(dir=(dd[0], dd[1]), curl=(.1, .1, .15, .2), spread=.35, thumb=.1), side=(1 if j == 0 else -1),
                                  seed=20 * j)
            arms += arm_s
    else:
        arms = rest_arm()[0]
    lines = ""
    if t > T_LICO:
        hp = head_pt((40, -40), HEAD, hr)
        lines = click_star(hp[0] - 20, hp[1] - 30, ((t - T_LICO) * 2.2) % 1.0, k=1.1, col="#ffffff")
    w = bed_world(t, head=head, plaid=plaid_svg(legs=-10 * awake * abs(osc(t, 4))), stand=alarm_on_stand(t, 0.0), arm_back=arms, front=c + lines)
    s = 1.75 + .08 * clamp((t - 16.08) / 1.5) + punch(t, T_LICO, .12, .05, .4)
    sh = shake_at(t, T_LICO, 16, .45)
    return compose(w, focus_cam(480, 940, s, screen_y=820), sh)


SHOTS = {"s02": s02, "s07": s07, "s08": s08, "s10": s10, "s11": s11, "s12": s12, "s13": s13}



def frame(sid, t):
    return SHOTS[sid](t)
