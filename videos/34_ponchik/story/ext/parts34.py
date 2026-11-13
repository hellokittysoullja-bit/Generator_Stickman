"""Общие предметы 2D-сцен рилса 34: пончик (розовая глазурь с посыпкой, шоколадный, белый; надкушенный — маской),
тучка с дождём, облачко речи с текстом кодом (шрифт IDB, как в рилсах 23–32), сердечко, галочка, конфета в фантике,
фантик, время слов из voice/words.json. Всё в своих координатах, центр (0, 0), если не сказано иное."""
import json
import math
import os

import numpy as np

import lib
from lib import DEFS, INK, blob, clamp, ellipse_pts, f, line, shape, uid

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    """Начало слова (первое после after) по words.json."""
    for w in WORDS:
        if w["word"].strip(".,?!:«»").lower() == word.lower() and w["start"] >= after - 1e-6:
            return w["start"]
    raise KeyError(word)


def bump(t, t0, dur=0.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def kick(t, t0, k=7.0, fr=14.0):
    """Затухающий толчок после t0 (0 до t0): 0 → +1 → затухает."""
    e = t - t0
    if e <= 0:
        return 0.0
    return math.exp(-e * k) * math.sin(min(e * fr, math.pi))


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def sausage(pts, w0, w1, n=24):
    """Контур пальца: гладкая средняя линия, толщина w0 → w1, кончик — полукруг (из scene_brain рилса 32)."""
    S = lib.sample(pts, False, 2.0)
    T = np.gradient(S, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    Wd = np.linspace(w0, w1, len(S))[:, None] / 2
    L, R = S + N * Wd, S - N * Wd
    end, tn, nn = S[-1], T[-1], N[-1]
    r = w1 / 2
    cap = [tuple(end + nn * r * math.cos(a) + tn * r * math.sin(a)) for a in np.linspace(0, math.pi, 9)[1:-1]]
    step = max(1, len(S) // 8)
    return [tuple(p) for p in L[::step]] + [tuple(L[-1])] + cap + [tuple(R[-1])] + [tuple(p) for p in R[::-step]]


# ═══════════════════════════════ пончик
GLAZE = {"pink": ("#f58fbb", "#dc6c9c", "#ffc6dc"), "choc": ("#6b3b22", "#4e2914", "#9a6040"), "white": ("#f7f1e6", "#ddd3c2", "#ffffff")}
DOUGH, DOUGH_SH, CRUMB = "#e0a259", "#b9763a", "#f6d9a2"
SPRINKLE = ["#ffd23a", "#4fb3e8", "#7ad15a", "#ffffff", "#e8413a", "#a46be0"]


def donut(kind="pink", sd=0, bites=(), sc=1.0):
    """Пончик в 3/4 сверху, ~[-62, 62]×[-44, 44]. bites — список (x, y, r) укусов в координатах пончика: часть
    пончика маской убирается, по краю укуса — светлая мякоть и тушь (без двойного контура: тушь только по краю укуса)."""
    g, gsh, ghi = GLAZE[kind]
    rx, ry = 62, 42
    outer = ellipse_pts(0, 0, rx, ry, 22)
    hole = ellipse_pts(0, -4, 17, 9, 12)
    s = []
    # тесто (бок снизу) и низ-тень
    sil = []          # силуэт одним контуром: верх — эллипс на y=0, низ — тот же эллипс на y=10 (толщина бока)
    for k in range(28):
        a = 2 * math.pi * k / 28
        sil.append((rx * math.cos(a), ry * math.sin(a) + (10 * math.sin(a) if math.sin(a) > 0 else 0)))
    inner = blob([(rx * math.cos(a), ry * math.sin(a) * .55 + 6) for a in np.linspace(0, math.pi, 14)] +
                 [(rx * math.cos(a), ry * math.sin(a) + 10) for a in np.linspace(math.pi, 0, 14)], DOUGH_SH, .85)
    inner += blob(ellipse_pts(20, 30, rx * .6, 12, 12), "#9a5f2c", .5)
    s.append(shape(sil, DOUGH, inner, w=4.2, seed=sd + 2))
    # глазурь: волнистый край
    gp = []
    rs = np.random.RandomState(sd + 7)
    for k in range(30):
        a = 2 * math.pi * k / 30
        wob = 1 + (0.06 * math.sin(a * 5 + sd) if math.sin(a) > 0.1 else 0.0)
        drip = 0.10 if (math.sin(a) > 0.3 and k % 4 == 1) else 0.0
        gp.append((rx * .9 * math.cos(a), -3 + ry * .84 * math.sin(a) * (wob + drip)))
    inner = blob(ellipse_pts(16, 14, rx * .75, ry * .5, 14), gsh, .75)
    inner += blob(ellipse_pts(-26, -18, 16, 6, 8, rot=-20), ghi, .9)
    if kind == "pink":
        for k in range(26):
            a = rs.uniform(0, 2 * math.pi)
            r = rs.uniform(0.42, 0.95)
            x, y = rx * .82 * r * math.cos(a), -3 + ry * .72 * r * math.sin(a)
            if (x / 22) ** 2 + ((y + 4) / 13) ** 2 < 1:
                continue
            ang = rs.uniform(0, 180)
            c = SPRINKLE[k % len(SPRINKLE)]
            inner += f'<rect x="{f(x - 5)}" y="{f(y - 1.8)}" width="10" height="3.6" rx="1.8" fill="{c}" transform="rotate({ang:.0f} {f(x)} {f(y)})"/>'
    elif kind == "white":
        for k in range(5):
            x0 = -44 + k * 22
            inner += line([(x0, -20), (x0 + 10, -6), (x0 + 4, 10)], 3, "#c7843f", seed=sd + 30 + k, op=.9)
    s.append(shape(gp, g, inner, w=3.8, seed=sd + 3))
    # дырка
    s.append(shape(hole, "#7a4a24", blob(ellipse_pts(0, -1, 17, 6, 10), "#4a2a14", .9), w=3.6, seed=sd + 4))
    body = "".join(s)
    if not bites:
        return f'<g transform="scale({f(sc)})">{body}</g>'
    mid = uid("m")
    cut = "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#000"/>' for x, y, r in bites)
    DEFS.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-200" y="-200" width="400" height="400">'
                f'<rect x="-200" y="-200" width="400" height="400" fill="#fff"/>{cut}</mask>')
    cl = lib.clip_of(ellipse_pts(0, 4, rx + 2, ry + 6, 22))
    crumb = "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r + 9)}" fill="{CRUMB}"/>' for x, y, r in bites)
    edge = ""
    for k, (x, y, r) in enumerate(bites):
        pts = [(x + r * math.cos(a), y + r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40)]
        edge += f'<path d="{lib.ink_open(pts, 3.6 * lib.INK_K[0], taper=.05, wmin=.8, seed=sd + 50 + k)}" fill="{INK}"/>'
    holes = "".join(f'<circle cx="{f(x + r * .5 * math.cos(a))}" cy="{f(y + r * .5 * math.sin(a))}" r="2.6" fill="#d9b27a"/>'
                    for k2, (x, y, r) in enumerate(bites) for a in (0.3 + k2, 2.2 + k2, 4.1 + k2))
    return (f'<g transform="scale({f(sc)})"><g mask="url(#{mid})">{body}<g clip-path="url(#{cl})">{crumb}{holes}</g></g>'
            f'<g clip-path="url(#{cl})" mask="url(#{mid})">{edge}</g></g>')


def plate(sd=0, w=110):
    """Тарелка в 3/4 сверху, центр (0, 0)."""
    s = shape(ellipse_pts(0, 6, w, w * .36, 24), "#d9dde6", "", w=3.8, seed=sd + 1)
    s += shape(ellipse_pts(0, 0, w, w * .34, 24), "#ffffff", blob(ellipse_pts(0, 2, w * .66, w * .2, 18), "#eef1f6") +
               line([(-w * .6, -w * .12), (-w * .2, -w * .26)], 3, "#ffffff", seed=sd + 3), w=3.8, seed=sd + 2)
    s += line([(-w * .66, 4), (-w * .3, w * .2), (w * .3, w * .2), (w * .66, 4)], 2.2, "#c9ceda", seed=sd + 4, op=.9)
    return s


# ═══════════════════════════════ облака, тучка, дождь
def cloud_pts(x, y, rx, ry, n=7, sd=0):
    rs = np.random.RandomState(sd)
    pts = []
    for j in range(n):
        a0, a1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
        bump_ = 0.2 + 0.06 * rs.uniform(-1, 1)
        for k in range(6):
            u = k / 6
            a = a0 + (a1 - a0) * u
            r = 1 + bump_ * math.sin(math.pi * u)
            pts.append((x + rx * math.cos(a) * r, y + ry * math.sin(a) * r) + ((1,) if k == 0 else ()))
    return pts


def storm(x, y, sc, dark, t, rain, sd=0, rain_len=230):
    """Тучка с дождём: dark 0..1 — от серо-голубой к грозовой; rain 0..1 — сила дождя (капли-штрихи падают)."""
    if sc < 0.02:
        return ""
    c = lib.mix("#9aa7c4", "#5d6684", dark)
    csh = lib.mix("#7d89aa", "#454c68", dark)
    s = []
    if rain > 0.01:
        rs = np.random.RandomState(sd + 3)
        n = int(16 * rain) + 1
        for k in range(n):
            x0 = rs.uniform(-85, 85) * sc
            ph = rs.uniform(0, 1)
            sp = rs.uniform(1.6, 2.2)
            u = (t * sp + ph) % 1.0
            yy = y + 30 * sc + u * rain_len * sc
            L = 26 * sc
            op = min(1.0, (1 - u) * 4)
            s.append(line([(x + x0 - 3 * sc * u, yy), (x + x0 - 6 * sc - 3 * sc * u, yy + L)], 5.5 * sc, "#6fb4f0", taper=.35, wmin=.4,
                          seed=sd + 10 + k, op=op))
    inner = blob(ellipse_pts(x + 14 * sc, y + 26 * sc, 92 * sc, 26 * sc, 14), csh, .9)
    inner += blob(ellipse_pts(x - 40 * sc, y - 26 * sc, 30 * sc, 12 * sc, 10, rot=-15), lib.mix("#c3cce0", "#7c86a6", dark), .8)
    s.append(shape(cloud_pts(x, y, 100 * sc, 52 * sc, 7, sd), c, inner, w=4.4 * max(sc, .5), seed=sd))
    return "".join(s)


def speech(x, y, w, h, text, fs, sc, tail=(-60, 90), sd=0, col="#ffffff"):
    """Облачко речи со скруглёнными краями и хвостиком к говорящему (tail — смещение кончика от низа-центра), текст —
    шрифт IDB жирный. (x, y) — центр облачка, sc — появление 0..1 (масштаб от кончика хвоста)."""
    if sc < 0.02:
        return ""
    x0, y0, x1, y1 = x - w / 2, y - h / 2, x + w / 2, y + h / 2
    tx, ty = x + tail[0], y1 + tail[1]
    body = lib.rect_pts(x0, y0, x1, y1, h * .45)
    tl = [(x - 70, y1 - 30), (tx, ty, 1), (x - 6, y1 - 20)]
    s = shape(tl, col, "", w=4.6, seed=sd + 1)
    s += shape(body, col, "", w=5, seed=sd + 2)
    s += lib.blob([(x - 64, y1 - 34), (x - 4, y1 - 30), (x - 8, y1 + 1), (x - 60, y1 + 1)], col)       # стык хвоста без туши
    s += (f'<text x="{f(x)}" y="{f(y + fs * .36)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="{fs}" '
          f'fill="{INK}">{text}</text>')
    return f'<g transform="translate({f(tx)} {f(ty)}) scale({sc:.4f}) translate({f(-tx)} {f(-ty)})">{s}</g>'


def heart(cx, cy, sc, rot=0.0, sd=0):
    pts = []
    for k in range(20):
        a = 2 * math.pi * k / 20
        hx = 16 * math.sin(a) ** 3
        hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((hx, hy) + ((1,) if k in (0, 10) else ()))
    P = lambda q: lib.T(q, cx, cy, sc, rot)   # noqa: E731
    hl = blob(P([(-11, -8), (-6, -12), (-3, -8), (-8, -3)]), "#ffb3a8")
    return shape(P(pts), "#e8413a", blob(P([(2, -6), (16, -6), (16, 16), (0, 16)]), "#c22a26") + hl, w=3.6, seed=sd)


def check(cx, cy, sc, prog=1.0, sd=0, col="#3cbf63", col_sh="#279a4a"):
    """Зелёная галочка-маркер толстой линией с тушью; prog — дорисовка 0..1."""
    p0, p1, p2 = (-60, 0), (-18, 44), (70, -60)
    L1 = math.dist(p0, p1)
    L2 = math.dist(p1, p2)
    d = prog * (L1 + L2)
    if d < L1:
        u = max(d / L1, 0.05)
        pts = [p0, (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u)]
    else:
        u = (d - L1) / L2
        pts = [p0, p1, (p1[0] + (p2[0] - p1[0]) * u, p1[1] + (p2[1] - p1[1]) * u)]
    P = [(cx + x * sc, cy + y * sc) for x, y in pts]
    o = line(P, 40 * sc, INK, taper=.08, wmin=.85, seed=sd + 2)
    o += line(P, 28 * sc, col, taper=.08, wmin=.85, seed=sd + 3)
    o += line([(x - 4 * sc, y - 6 * sc) for x, y in P[:2]], 6 * sc, "#bff0c8", taper=.3, wmin=.4, seed=sd + 4, op=.9)
    return o


CANDY = [("#e8413a", "#b8261f"), ("#ffcf3a", "#d9a020"), ("#4fb3e8", "#2f86c0"), ("#7ad15a", "#4f9a3a"), ("#a46be0", "#7a46b0"),
         ("#ff8fb8", "#d9608c")]


def candy(x, y, rot, ci, sd=0, sc=1.0):
    """Конфета в фантике: овальное тело + два «хвостика»-банта, полоска блика."""
    c, csh = CANDY[ci % len(CANDY)]
    s = []
    for side in (-1, 1):
        wing = [(side * 26, -6), (side * 50, -22), (side * 56, -4), (side * 52, 16), (side * 50, 22), (side * 26, 6)]
        if side < 0:
            wing = wing[::-1]
        s.append(shape(wing, csh, line([(side * 32, 0), (side * 50, -12)], 2, lib.mul(csh, (.8, .8, .8)), seed=sd + 5 + side, op=.8), w=3.2,
                       seed=sd + 2 + side))
    s.append(shape(ellipse_pts(0, 0, 30, 21, 16), c, blob(ellipse_pts(6, 8, 24, 11, 12), csh, .8) +
                   line([(-16, -10), (8, -13)], 4.4, "#ffffff", seed=sd + 9, op=.75), w=3.6, seed=sd + 1))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">{"".join(s)}</g>'


def wrapper(x, y, rot, ci, sd=0, sc=1.0):
    """Пустой смятый фантик: плоская мятая «бабочка» с изломами."""
    c, csh = CANDY[ci % len(CANDY)]
    pts = [(-46, -14), (-30, -22), (-18, -8), (-2, -18), (12, -6), (30, -20), (48, -10), (40, 4), (50, 16), (28, 18), (12, 8), (-6, 18),
           (-22, 8), (-40, 18), (-50, 4)]
    inner = blob([(-46, 4), (50, 4), (50, 18), (-46, 18)], csh, .8)
    inner += line([(-18, -8), (-6, 18)], 2.2, lib.mul(csh, (.75, .75, .75)), seed=sd + 2, op=.9)
    inner += line([(12, -6), (12, 8)], 2.2, lib.mul(csh, (.75, .75, .75)), seed=sd + 3, op=.9)
    inner += line([(-36, -12), (-24, -16)], 3, "#ffffff", seed=sd + 4, op=.7)
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">{shape(pts, c, inner, w=3.2, seed=sd + 1)}</g>'


def sparkle(x, y, r, col="#ffd84a", sd=0, rot=0.0):
    pts = []
    for k in range(8):
        a = math.radians(rot + k * 45)
        rr = r if k % 2 == 0 else r * .38
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a), 1))
    return shape(pts, col, "", w=3.2, seed=sd)


def pop_lines(x, y, e, r0=70, r1=120, n=6, a0=-math.pi / 2, spread=2 * math.pi, col=INK, w=6, sd=0):
    """Штрихи «удара»: короткие лучи от центра, вылетают и гаснут за 0.3 с."""
    if e < 0 or e > 0.32:
        return ""
    u = e / 0.32
    s = []
    for k in range(n):
        a = a0 + spread * (k + 0.5) / n - spread / 2 if spread < 6.2 else a0 + 2 * math.pi * k / n
        ra, rb = r0 + (r1 - r0) * u * .6, r0 + (r1 - r0) * min(1, u * 1.4)
        s.append(line([(x + ra * math.cos(a), y + ra * math.sin(a)), (x + rb * math.cos(a), y + rb * math.sin(a))], w * (1 - u * .5), col,
                      taper=.3, wmin=.4, seed=sd + k))
    return "".join(s)


# ═══════════════════════════════ кисть «грозит пальцем»
DIMA_SKIN = ("#ecc4a2", "#d39f83", "#bf8a74", "#f1cdbd")


def point_hand(Wr, d, k=1.0, skin=DIMA_SKIN, sd=0, flip=1, index=True):
    """Кулак с поднятым указательным: запястье Wr, ось d — от запястья к пальцам (указательный идёт вдоль d),
    flip — сторона большого пальца. Единицы — L героя (голова ~300), k — масштаб. Без «варежки»: три согнутых пальца
    отдельными подушечками, большой палец поверх них, указательный — колбаской с ногтем."""
    sk, ssh, ssh2, nail = skin
    d = np.array(d, float)
    d /= np.linalg.norm(d) + 1e-9
    n = np.array([-d[1], d[0]]) * flip
    W_ = np.array(Wr, float)

    def tf(x, y):
        p = W_ + d * x * k + n * y * k
        return (float(p[0]), float(p[1]))

    o = []
    if not index:          # просто кулак: четвёртая подушечка вместо указательного
        pass
    # указательный (сзади кулака не виден — корень под ладонью)
    idx = [tf(40, -22), tf(80, -24), tf(118, -22), tf(146, -18)]
    if index:
        o.append(shape(sausage(idx, 21 * k, 18 * k), sk, line([tf(96, -14), tf(100, -22), tf(96, -30)], 1.6, ssh2, seed=sd + 3, op=.8) +
                   f'<path d="{lib.fill_d(ellipse_pts(*tf(138, -19), 6.5 * k, 5 * k, 10, rot=math.degrees(math.atan2(d[1], d[0]))))}" fill="{nail}"/>',
                       w=3.0, seed=sd + 2))
    # ладонь-кулак
    palm = [tf(-4, -30), tf(30, -36), tf(58, -32), tf(76, -22), tf(84, -2), tf(82, 20), tf(70, 34), tf(36, 38), tf(4, 32)]
    o.append(shape(palm, sk, blob([tf(-6, 12), tf(84, 10), tf(84, 40), tf(-6, 40)], ssh, .8), w=3.4, seed=sd + 4))
    # три согнутых пальца — подушечки у костяшек
    for i, y in enumerate(((-23,) if not index else ()) + (-8, 8, 23)):
        fp = [tf(56, y - 8), tf(80, y - 9), tf(88, y), tf(80, y + 8), tf(56, y + 7)]
        o.append(shape(fp, sk, blob([tf(56, y + 2), tf(88, y + 2), tf(80, y + 8), tf(56, y + 7)], ssh, .7), w=2.8, seed=sd + 10 + i))
    # большой палец поперёк согнутых
    th = [tf(16, -30), tf(40, -18), tf(62, -10)]
    o.append(shape(sausage(th, 22 * k, 17 * k), sk, line([tf(44, -24), tf(46, -16), tf(44, -8)], 1.4, ssh2, seed=sd + 21, op=.7), w=3.0,
                   seed=sd + 20))
    return "".join(o)
