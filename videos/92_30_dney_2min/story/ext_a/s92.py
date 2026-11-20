"""Рилс 92 «30 дней по 2 минуты», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу); числа в коде — длительности движений.
Сквозной образ: настенный календарь из 30 клеток без цифр (закрашенная клетка с отпечатком лапы = день; клетки
закрашиваются всё быстрее) и секундомер на 2 минуты (оранжевый сектор без цифр). Рассказ от первого лица, в кадре Дима.
NOCAM=1 — без влёта, тряски и заголовка (замер движения рисунка); MASK=1 — только рисунок хука белым на чёрном."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(STORY)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
sys.path.insert(1, os.path.join(REPO, "scripts"))
import big_title  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import cat as CT  # noqa: E402
import props as PR  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
NOCAM = bool(os.environ.get("NOCAM"))
MASK = bool(os.environ.get("MASK"))


def W(i):
    return WORDS[i]["start"]


def WE(i):
    return WORDS[i]["end"]


def stress(i, u):
    return W(i) + (WE(i) - W(i)) * u


def T0(sid):
    return SHOT[sid]["t0"]


def T1(sid):
    return SHOT[sid]["t1"]


def ramp(t, a, d):
    return clamp((t - a) / d)


def bump(t, a, up=.08, down=.3):
    if a is None:
        return 0.0
    u = t - a
    if u <= 0:
        return 0.0
    return min(1.0, u / up) * (math.exp(-(u - up) / down) if u > up else 1.0)


def shake(t, a, amp=10.0, dur=.35, f=11.0):
    if a is None:
        return 0.0, 0.0
    u = t - a
    if u <= 0 or u > dur * 3:
        return 0.0, 0.0
    e = math.exp(-u / dur * 2.5)
    return amp * e * math.sin(2 * math.pi * f * u), amp * .6 * e * math.cos(2 * math.pi * f * .8 * u)


def pop(t, a, d=.24):
    u = clamp((t - a) / d)
    return lib.back_out(u, 2.2) if u < 1 else 1.0


def rect(x0, y0, x1, y1, col, op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{col}"{o}/>'


def tf(inner, x, y, k=1.0, rot=0.0):
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k:.4f})">{inner}</g>'


def title(t):
    if NOCAM or MASK:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, text=SH["title"]["text"], t_in=SH["title"]["t_in"], t_out=SH["title"]["t_out"], hits=hits)


def view(body, cx, cy, s, rot=0.0, over="", bg="#efe2c8"):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def times_acc(a, b, n, p=1.6):
    """n моментов от a до b, всё чаще (интервалы сжимаются)."""
    return [a + (b - a) * (1 - (1 - i / max(1, n - 1)) ** p) if n > 1 else a for i in range(n)]


def count(t, ts):
    """Число закрашенных клеток к моменту t (дробная часть — выскок последней)."""
    n = 0.0
    for x in ts:
        if t >= x:
            n += min(1.0, (t - x) / .22)
    return n


# ═════════════════════════ комната ═════════════════════════
FL = 1300.0
WALL, WALL_SH, FLOOR_C = "#efe2c8", "#e3d2b2", "#cdb48c"


def room(t, x0=-1400.0, x1=2600.0, dusk=0.0, MASKED=False):
    if MASKED:
        return ""
    wc = lib.mix(WALL, "#c9b6a8", dusk)
    o = [rect(x0, -1400, x1, FL, wc)]
    i0 = int(x0 // 120)
    for i in range(i0, int(x1 // 120) + 1):             # обои: полосы
        xa = i * 120
        o.append(rect(xa, -1400, xa + 46, FL, lib.mix(WALL_SH, "#b9a698", dusk), .55))
    o.append(rect(x0, FL - 46, x1, FL, "#d8c3a0"))
    o.append(line([(x0, FL - 46), (x1, FL - 46)], 3, seed=7))
    o.append(rect(x0, FL, x1, FL + 1400, lib.mix(FLOOR_C, "#8c7a66", dusk)))
    o.append(line([(x0, FL), (x1, FL)], 5, seed=11))
    for i in range(int(x0 // 300), int(x1 // 300) + 1):
        xa = i * 300
        o.append(line([(xa, FL + 20), (xa + (xa - 540) * .9, FL + 900)], 2.4, "#b0966c", seed=20 + i % 9, op=.8))
    return "".join(o)


# ═════════════════════════ календарь из 30 клеток ═════════════════════════
WEB = "#8e949c"
CC = 84.0                                    # клетка
GREEN, GREEN_SH = "#7cc46a", "#5aa24c"


def paw_print(x, y, s, col=CT.CAT):
    if s <= .02:
        return ""
    o = [blob(ellipse_pts(x, y + 8 * s, 15 * s, 12 * s, 14), col)]
    for dx, dy, r in ((-17, -10, 6.5), (-6, -19, 7), (7, -19, 7), (18, -10, 6.5)):
        o.append(blob(ellipse_pts(x + dx * s, y + dy * s, r * s, r * 1.2 * s, 10), col))
    return "".join(o)


def cell_xy(i):
    """Центр клетки i (0…29) в координатах календаря (центр сетки — 0, 0)."""
    return -2.5 * CC + (i % 6) * CC, -2 * CC + (i // 6) * CC


def calendar30(cx, cy, k, n, t, half=0, sweep=None, web=0.0, glow=0.0, dim=0.0):
    """Календарь (центр сетки cx, cy; масштаб k): n — закрашено клеток (дробь — выскок последней), первые half закрашены
    наполовину (бросал на второй минуте); sweep 0…1 — бегущая подсветка по клеткам; web — паутина в углу."""
    hw, hh = 3 * CC + 22, 2.5 * CC + 22
    o = []
    if glow > .01:
        o.append(PR.glow(0, 0, 420, glow, "#ffe28a"))
    paper = lib.mix("#fbf6e6", "#d9d2c4", dim)
    o.append(shape(lib.rrect(-hw, -hh - 96, hw, hh, 12), paper,
                   blob(lib.rrect(-hw - 6, -hh - 100, hw + 6, -hh - 10, 10), lib.mix("#d2523f", "#9a6a60", dim)) +
                   blob(lib.rrect(-hw - 6, hh - 18, hw + 6, hh + 6, 4), "#e4dac4"), w=5, seed=501))
    for j in range(5):                       # кольца переплёта
        rx = -hw + 50 + (2 * hw - 100) * j / 4
        o.append(line([(rx - 8, -hh - 80), (rx - 10, -hh - 116), (rx + 6, -hh - 124), (rx + 10, -hh - 100)], 7, "#868b96", taper=.1,
                      wmin=.8, seed=510 + j))
    for i in range(30):
        x, y = cell_xy(i)
        q = clamp(n - i)
        if sweep is not None:
            sw = math.exp(-((sweep * 34 - 2 - i) ** 2) / 3.0)
            if sw > .03:
                o.append(rect(x - CC / 2 + 4, y - CC / 2 + 4, x + CC / 2 - 4, y + CC / 2 - 4, "#ffe28a", .8 * sw))
        if q > 0:
            s = lib.back_out(q, 2.4) if q < 1 else 1.0
            a = CC / 2 - 6
            if i < half:
                pts = [(x - a * s, y - a * s), (x + a * s, y + a * s), (x - a * s, y + a * s)]
                o.append(blob(pts, GREEN))
                o.append(line([(x - a * s, y - a * s), (x + a * s, y + a * s)], 2.4, GREEN_SH, seed=600 + i))
                o.append(paw_print(x - 12, y + 14, .7 * s))
            else:
                o.append(blob(lib.rrect(x - a * s, y - a * s, x + a * s, y + a * s, 6), GREEN))
                o.append(blob(lib.rrect(x - a * s, y + a * s * .45, x + a * s, y + a * s, 6), GREEN_SH, .5))
                o.append(paw_print(x, y + 4, .95 * s))
    gx0, gy0 = -3 * CC, -2.5 * CC - CC / 2 + CC / 2
    gy0 = -2.5 * CC
    for r in range(6):
        o.append(line([(gx0, gy0 + CC * r), (gx0 + 6 * CC, gy0 + CC * r + .5)], 2.6, "#9c927c", taper=.1, wmin=.8, seed=520 + r))
    for c in range(7):
        o.append(line([(gx0 + CC * c, gy0), (gx0 + CC * c + .5, gy0 + 5 * CC)], 2.6, "#9c927c", taper=.1, wmin=.8, seed=530 + c))
    if web > .01:
        o.append(PR.cobweb(hw - 4, -hh - 4, 1.0 * web, tremble=.4, t=t, ang=95, span=80, L=170, seed=3, col=WEB))
    return tf("".join(o), cx, cy, k)


def cell_world(cx, cy, k, i):
    x, y = cell_xy(i)
    return cx + x * k, cy + y * k


def tap_ring(x, y, t, a, k=1.0):
    u = clamp((t - a) / .3)
    if u <= 0 or u >= 1:
        return ""
    r = (30 + 60 * u) * k
    return line(ellipse_pts(x, y, r, r, 20) + [ellipse_pts(x, y, r, r, 20)[0]], 5 * (1 - u) * k + .5, "#ffffff", taper=.05, wmin=.9,
                seed=700, op=1 - u)


def fly_sheet(x0, y0, t, a, seed=0, dx=1.0, dy=-.4, life=.6):
    """Листок календаря срывается и летит в камеру: растёт, вращается, уходит из кадра."""
    u = (t - a) / life
    if u <= 0 or u >= 1:
        return ""
    e = u * u
    x = x0 + dx * 900 * e + 30 * math.sin(seed * 2.1)
    y = y0 + dy * 900 * e - 120 * math.sin(math.pi * u)
    k = .9 + 4.5 * e
    rot = (1 if seed % 2 else -1) * (30 + 400 * e)
    flap = math.sin(u * 9 + seed)
    body = shape(lib.rrect(-42, -42, 42, 42, 4), "#fbf6e6", blob(lib.rrect(-34, -34, 34, 34, 5), GREEN) + paw_print(0, 4, .9), w=3.4, seed=800 + seed)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f} {k * (.65 + .35 * abs(flap)):.3f})">{body}</g>'


# ═════════════════════════ предметы ═════════════════════════
def envelope(x, y, k=1.0, rot=0.0, seed=0, col="#f3e4c6", dust=0.0):
    w, h = 120, 80
    inner = line([(-w / 2, -h / 2), (0, 6), (w / 2, -h / 2)], 3, "#b79e74", seed=900 + seed)
    inner += line([(-w / 2, h / 2), (-14, 0)], 2, "#c9b48c", seed=901 + seed) + line([(w / 2, h / 2), (14, 0)], 2, "#c9b48c", seed=902 + seed)
    inner += blob(lib.rrect(w / 2 - 30, -h / 2 + 8, w / 2 - 10, -h / 2 + 30, 2), "#d65a48")
    if dust > .01:
        inner += blob(lib.rrect(-w / 2, -h / 2, w / 2, h / 2), "#9a9488", .35 * dust)
    return tf(shape(lib.rrect(-w / 2, -h / 2, w / 2, h / 2, 5), col, inner, w=3.6, seed=910 + seed), x, y, k, rot)


PILE = [((i % 5 - 2) * 70 + (17 * i % 23) - 11, -30 - (i // 5) * 52 - (7 * i % 13), (i * 37 % 41) - 20) for i in range(24)]


def envelope_pile(x, y, k=1.0, n=24, melt=0.0, t=0.0, dust=0.0, shrink=1.0):
    """Гора конвертов (низ по центру x, y); melt 0…1 — конверты по одному улетают сверху."""
    o = []
    m = len(PILE)
    for i in range(min(n, m)):
        px, py, r = PILE[i]
        px *= 1 - .18 * (i // 5)
        g = clamp(melt * (m + 6) - (m - 1 - i))           # сначала уходят верхние
        if g >= 1:
            continue
        ex, ey = px + 220 * g * (1 if i % 2 else -1), py - 380 * g
        o.append(envelope(ex, ey, 1.0 - .7 * g, r + 200 * g * (1 if i % 2 else -1), seed=i, dust=dust))
    return tf("".join(o), x, y, k * shrink)


def bank_phone(x, y, k=1.0, rot=0.0, ring=0.0, t=0.0, dim=0.0):
    """Телефон с иконкой банка на экране (фронтон и колонны, без букв); ring — вибрирует."""
    j = 6 * ring * math.sin(t * 70)
    scr = lib.mix("#cfe3f7", "#8d98a6", dim)
    ic = [(-34, -44), (0, -66), (34, -44)]
    inner = blob(lib.rrect(-52, -100, 52, 96, 10), scr)
    inner += shape(ic + [(34, -40), (-34, -40)], "#ffffff", "", w=3, seed=950)
    for c in (-24, 0, 24):
        inner += shape(lib.rrect(c - 6, -36, c + 6, 4, 1), "#ffffff", "", w=2.6, seed=951 + c)
    inner += shape(lib.rrect(-40, 6, 40, 16, 2), "#ffffff", "", w=2.6, seed=955)
    o = [shape(lib.rrect(-62, -120, 62, 120, 18), "#2b2e35", inner, w=4, seed=960)]
    if ring > .02:
        for s in (-1, 1):
            for q in range(2):
                o.append(line([(s * (80 + 22 * q), -40), (s * (92 + 22 * q), -10), (s * (80 + 22 * q), 20)], 4, INK, seed=970 + q + s, op=ring))
    return tf("".join(o), x + j, y, k, rot + .6 * j)


def report(x, y, k=1.0, seed=0):
    o = [PR.paper_stack(0, 0, 1.0, n=7, seed=seed, mess=.25)]
    return tf("".join(o), x, y, k)


def stopwatch(x, y, k, prog, t=0.0, click=0.0, lap=0.0):
    """Секундомер на 2 минуты: prog 0…1 — сектор и стрелка; lap — сколько прошло сверх двух минут (зелёный сектор)."""
    a = 360 * clamp(prog) + 360 * lap
    o = PR.stopwatch(0, 0, 1.0, hand_a=a, sector_a=360 * clamp(prog), click=click, t=t)
    if lap > .005:
        n = max(3, int(lap * 72))
        pts = [(0, 0, 1)] + [(70 * math.sin(math.radians(360 * lap * i / n)), -70 * math.cos(math.radians(360 * lap * i / n))) for i in range(n + 1)]
        o += blob(pts, "#5fb35a", .9)
        hand = math.radians(a)
        o += line([(-20 * math.sin(hand), 20 * math.cos(hand)), (112 * math.sin(hand), -112 * math.cos(hand))], 6, "#c2382d", taper=.25, wmin=.35,
                  seed=81780)
    return tf(o, x, y, k)


def stool(x, y, k=1.0, col="#b98a5a"):
    o = [shape(lib.rrect(-90, -18, 90, 8, 6), col, "", w=4, seed=1001)]
    for s in (-1, 1):
        o.append(shape([(s * 60 - 9, 6, 1), (s * 60 + 9, 6, 1), (s * 70 + 9, 260, 1), (s * 70 - 9, 260, 1)], lib.mul(col, (.8, .8, .8)), "", w=3.4,
                       seed=1002 + s))
    return tf("".join(o), x, y, k)


def chair(x, y, k=1.0):
    o = [shape(lib.rrect(-100, -16, 110, 10, 6), "#a8774a", "", w=4, seed=1011)]
    o.append(shape([(-100, -16, 1), (-80, -16, 1), (-70, -330, 1), (-92, -330, 1)], "#a8774a", "", w=4, seed=1012))
    for s in (-1, 1):
        o.append(shape([(s * 80 - 9, 8, 1), (s * 80 + 9, 8, 1), (s * 86 + 9, 240, 1), (s * 86 - 9, 240, 1)], "#8a6038", "", w=3.4, seed=1013 + s))
    return tf("".join(o), x, y, k)


def shelf(x, y, w=260.0):
    return shape(lib.rrect(x - w / 2, y, x + w / 2, y + 22, 4), "#b98a5a", blob(lib.rrect(x - w / 2, y + 12, x + w / 2, y + 22, 3), "#8a6038"),
                 w=4, seed=1021) + line([(x - w / 2 + 30, y + 22), (x - w / 2 + 30, y + 80), (x - w / 2 + 80, y + 22)], 4, seed=1022) + \
        line([(x + w / 2 - 30, y + 22), (x + w / 2 - 30, y + 80), (x + w / 2 - 80, y + 22)], 4, seed=1023)


def cat(x, y, k, t, st=None):
    st = dict(dict(look=(-.6, -.3), tail=8 * math.sin(t * 1.7), flame_e=1.0), **(st or {}))
    return CT.draw(x, y, k, st, t)


def cat_tapping(x, y, k, t, taps, look=(-.9, -.2)):
    """Кот ставит лапу на клетку на каждом моменте из taps: лапа вверх-вниз."""
    p = 0.0
    for a in taps:
        p = max(p, bump(t, a - .1, .08, .16))
    return cat(x, y, k, t, dict(paw=.95 * p, paw_dx=-110, look=look, tilt=-6 * p))


def dima(x, ground, k, expr, pose, t, flip=False, head_add=0.0, lean=0.0, **kw):
    y = ground - (people.LEG_LEN - 12) * k - 6
    return people.dima82(x, y, k, expr, pose, t=t, feet="stand", flip=flip, head_add=head_add, lean_add=lean, **kw)


def dima_sit(x, hip, k, expr, t, pose="sit_desk", lean=0.0, head_add=0.0, flip=False):
    feet = people.sit_kw(x, hip, k)["feet"]
    return people.dima82(x, hip, k, expr, pose, t=t, feet=feet, lean_add=lean, head_add=head_add, flip=flip)


def dima_run(x, k, t, expr="rush82", lean=.32, period=.34):
    return people.dima82_run(x, FL - people.LEG_LEN * .9 * k, k, (t / period) % 1.0, t, expr=expr, boot=False, socks=None, sandwich=False, lean=lean)


# ═════════════════════════ хук: s01–s02 ═════════════════════════
CALX, CALY, CALK = 540.0, 560.0, 1.0
HIT01 = stress(1, .35)                       # «тРИдцать»: листок срывается и летит в камеру
HOOK_TAPS = sorted([-.2, .08, HIT01] + times_acc(.62, T1("s02") - .1, 11, 1.7))
HOOK_SHEETS = [-.42, -.22] + HOOK_TAPS[2:]
ITEMS = [("mail", 60.0), ("laptop", 560.0), ("phone", 1180.0)]
CAT_SHELF = (905.0, 780.0)


def run_x(t):
    """Дима бежит слева направо: у каждого дела притормаживает."""
    base = -220 + 560 * t
    return base - 40 * sum(math.sin(math.pi * clamp((base - px + 140) / 280)) for _, px in ITEMS)


def item_hit(t, px):
    """Момент, когда Дима пробегает мимо дела px."""
    for k in range(0, 200):
        tt = -0.5 + k * .02
        if run_x(tt) >= px - 40:
            return tt
    return None


def hook_world(t, masked=False):
    o = [room(t, MASKED=masked)]
    o.append(calendar30(CALX, CALY, CALK, count(t, HOOK_TAPS), t))
    o.append(shelf(*CAT_SHELF, 240))
    o.append(cat_tapping(CAT_SHELF[0], CAT_SHELF[1], .42, t, HOOK_TAPS))
    if HOOK_TAPS:
        n = int(clamp(count(t, HOOK_TAPS), 0, 29.99))
        for i, a in enumerate(HOOK_TAPS):
            if t >= a and i < 30:
                o.append(tap_ring(*cell_world(CALX, CALY, CALK, i), t, a))
        _ = n
    # дела: почта (гора конвертов на табурете), ноутбук на столе, телефон-банк на тумбе
    hm, hl, hp = (item_hit(t, px) for _, px in ITEMS)
    o.append(stool(60, FL - 260, 1.0))
    o.append(envelope_pile(60, FL - 280, .8, n=14))
    o.append(tf(envelope(0, 0, 1.1, -10, seed=3), 60, FL - 470 - 160 * bump(t, hm, .1, .3), 1.0, 30 * bump(t, hm, .1, .3)))
    o.append(PR.desk(560, FL - 300, w=420, depth=80, leg_h=260, seed=2))
    o.append(PR.laptop(560, FL - 330, .45, open_=1.0, screen="on" if t > (hl or 9) else "dark", t=t, glow=bump(t, hl, .05, .5)))
    o.append(stool(1180, FL - 260, 1.0, "#9a8a7a"))
    o.append(bank_phone(1180, FL - 400, .9, -8, ring=bump(t, hp, .05, .5) + .4 * (t > (hp or 9)), t=t))
    x = run_x(t)
    f = dima_run(x, .5, t, expr="rush82")
    o.append(f["svg"])
    hx, hy = people.hand_pos(f, "n", 40)
    o.append(stopwatch(hx + 10, hy - 20, .26, (t % 1.2) / 1.2, t, click=bump(t, HIT01, .04, .15)))
    o.append(PR.speed_arcs(x - 170, FL - 420, 1.0, 1.0, t, seed=2, n=3))
    for i, a in enumerate(HOOK_SHEETS):
        idx = max(0, min(29, i - 2)) if i >= 2 else (4 + i * 5)
        cx, cy = cell_world(CALX, CALY, CALK, idx)
        o.append(fly_sheet(cx, cy, t, a, seed=i, dx=(-1 if i % 2 else 1) * (.6 + .3 * (i % 3)), dy=(-.5 if i % 3 else .55)))
    return "".join(o)


def hook_cam_scene(t):
    """Камера сцены (часть рисунка): летит за Димой."""
    x = run_x(t)
    return 540 + .38 * (x - 540), 720 - 20 * clamp(t / 1.6), 1.08


def hook_wrap(body, t, hit, bg="#efe2c8"):
    import anim
    hc = anim.hook_cam(t, hit=hit)
    z, r, dx, dy = hc["zoom"], hc["rot"], hc["dx"], hc["dy"]
    piv = 960.0
    tr = f"translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) scale({z:.5f}) translate(-540 {-piv})"
    blur = ""
    amt = hc["zoom_blur"] / 0.07
    if amt > 0.03:
        for dk, op in ((.03, .30), (.06, .2), (.1, .12)):
            blur += (f'<use href="#hk92" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk92">{body}</g></g>{blur}'


MASK_F = '<filter id="mk92"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 9 0"/></filter>'


def frame_s01(t):
    cx, cy, s = hook_cam_scene(t)
    if MASK:
        lib.DEFS.append(MASK_F)
        return lib.svg(f'<rect width="1080" height="1920" fill="#000"/><g transform="{lib.cam(cx, cy, s, 0)}"><g filter="url(#mk92)">'
                       f'{hook_world(t, True)}</g></g>')
    body = hook_world(t)
    dx, dy = shake(t, HIT01, 14) if not NOCAM else (0, 0)
    v = f'<g transform="{lib.cam(cx + dx, cy + dy, s, 0)}">{body}</g>'
    if NOCAM:
        return lib.svg('<rect width="1080" height="1920" fill="#efe2c8"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT01) + title(t))


def frame_s02(t):
    """«любое дело всего с»: камера летит за Димой дальше — к телефону; кот ставит лапу всё чаще."""
    a, b = T0("s02"), T1("s02")
    u = ease_io(ramp(t, a, b - a))
    x = run_x(t)
    cx = 540 + .6 * (x - 540) + 20 * u
    dx, dy = shake(t, stress(5, .3), 7)
    return view(hook_world(t), cx + dx, 720 + dy - 20 * u, 1.08 + .1 * u, -1.5 + 2.5 * u, over=title(t))


# ═════════════════════════ s03: секундомер — «двух минут» ═════════════════════════
def frame_s03(t):
    a, b = T0("s03"), T1("s03")
    clk = W(8)
    prog = ease_io(ramp(t, clk, WE(9) - clk + .1))
    o = [room(t)]
    o.append(calendar30(300, 520, .8, count(t, HOOK_TAPS), t))
    o.append(PR.glow(540, 900, 520, .5 + .3 * bump(t, WE(9), .05, .4), "#fff4cf"))
    o.append(stopwatch(560, 930, 2.0, prog, t, click=bump(t, clk, .04, .2)))
    o.append(PR.sparkles(560, 930, 3.2, bump(t, WE(9) - .05, .05, .4), t, seed=2, n=6, r=300))
    p = pop(t, a - .05, .25)
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, clk, 9)
    return view("".join(o), 560 + dx, 880 + dy, .75 + .35 * p + .06 * u + .05 * bump(t, clk, .04, .3), 3 * (1 - p), over=title(t))


# ═════════════════════════ s04–s06: раньше — гора дел, паутина ═════════════════════════
def webbed_desk(t, web, rings=0.0, drop=None, ring_t=None, dim=0.0):
    """Стол дел: отчёт, гора конвертов, телефон-банк; web 0…1 — паутина растёт."""
    o = [PR.desk(560, FL - 300, w=760, depth=100, leg_h=260, seed=4)]
    o.append(envelope_pile(300, FL - 330, 1.0, n=24, dust=web))
    if drop is not None:                     # новые конверты падают на гору
        for j in range(3):
            g = ramp(t, drop + .12 * j, .3)
            if g > 0:
                o.append(envelope(300 + (j - 1) * 60, FL - 600 - 380 * (1 - g * g) + 80 * j, 1.0, (j - 1) * 30 * (1 - g), seed=30 + j))
    o.append(report(600, FL - 330, 1.2, seed=3))
    o.append(bank_phone(820, FL - 420, .8, 6, ring=rings, t=t, dim=dim))
    if web > .01:
        o.append(PR.cobweb(170, FL - 640, 1.4 * web, tremble=.5, t=t, ang=-10, span=70, L=200, seed=4, col=WEB))
        o.append(PR.cobweb(600, FL - 470, 1.0 * web, tremble=.5, t=t, ang=200, span=100, L=150, seed=5, col=WEB))
        o.append(PR.cobweb(820, FL - 545, 1.1 * web, tremble=.6, t=t, ang=-20, span=90, L=150, seed=6, col=WEB))
        o.append(PR.cobweb(330, FL - 300, 1.0 * web, tremble=.5, t=t, ang=-100, span=70, L=170, seed=7, col=WEB))
    return "".join(o)


def frame_s04(t):
    """«Раньше я неделями не мог сесть за»: календарь пустой, листы-недели переворачиваются, дела зарастают паутиной."""
    a, b = T0("s04"), T1("s04")
    web = ease_out(ramp(t, a, b - a), 2)
    o = [room(t, dusk=.25)]
    o.append(calendar30(540, 470, .9, 0, t, web=web, dim=.2))
    for j in range(4):                       # недели пролетают: верхний лист рвётся и улетает
        ft = W(12) + .16 * j
        u = ramp(t, ft, .35)
        if 0 < u < 1:
            o.append(tf(shape(lib.rrect(-270, -260, 270, 230, 10), "#f5efe0", line([(-200, 0), (200, 0)], 3, "#c9bfa9", seed=40 + j), w=4, seed=41 + j),
                        540 + 300 * u * (1 if j % 2 else -1), 470 - 500 * u, .9 * (1 - .4 * u), 50 * u * (1 if j % 2 else -1)))
    o.append(webbed_desk(t, web, dim=.2))
    f = dima(40, FL + 60, .5, "puzzled82", "d82_rest", t, flip=False, head_add=-.05)
    o.append(f["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(13), 5)
    return view("".join(o), 440 + dx, 880 + dy - 40 * u, 1.12 + .12 * u, -1 + 2 * u)


def frame_s05(t):
    """«отчёт, разобрать почту»: крупно отчёт в паутине → гора почты, на «почту» сверху сыплются ещё конверты."""
    a, b = T0("s05"), T1("s05")
    o = [room(t, dusk=.25)]
    o.append(calendar30(540, 470, .9, 0, t, web=1.0, dim=.2))
    o.append(webbed_desk(t, 1.0, drop=W(19) - .1))
    u = ease_io(ramp(t, W(18) - .1, .5))
    dx, dy = shake(t, W(19) + .2, 8)
    cx = 600 + (330 - 600) * u
    return view("".join(o), cx + dx, FL - 520 + dy, 1.5 + .1 * u + .05 * bump(t, W(19) + .2, .05, .3), 0)


def frame_s06(t):
    """«позвонить в банк»: телефон с банком звонит в паутине, Дима отшатывается."""
    a, b = T0("s06"), T1("s06")
    ring = ramp(t, a, .1) * (.6 + .4 * math.sin(t * 12) ** 2)
    o = [room(t, dusk=.25)]
    o.append(calendar30(540, 470, .9, 0, t, web=1.0, dim=.2))
    o.append(webbed_desk(t, 1.0, rings=ring))
    back = ease_out(ramp(t, W(23) - .1, .3))
    f = dima(990 + 70 * back, FL + 60, .5, "panic82" if back > .2 else "look82", "d82_shrug" if back > .2 else "d82_rest", t, flip=True,
             head_add=-.1 * back, lean=-.2 * back)
    o.append(f["svg"])
    if back > .1:
        o.append(PR.sweat(f["head"][0] - 50, f["head"][1] - 20, .8))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(23), 9)
    return view("".join(o), 820 + dx, FL - 520 + dy, 1.35 + .12 * u, 1.5 * math.sin(t * 9) * ring * .3)


# ═════════════════════════ s07–s09: правило двух минут, первая неделя ═════════════════════════
def frame_s07(t):
    """«Правило простое: делаю ровно»: Дима поднимает секундомер, щёлк на «ровно» — сектор пошёл."""
    a, b = T0("s07"), T1("s07")
    clk = stress(27, .3)
    lift = ease_out(ramp(t, a, .35))
    o = [room(t)]
    o.append(calendar30(250, 470, .75, 0, t))
    f = dima(560, FL + 60, .55, "sure82" if t > clk else "look82", ("d82_rest", "d82_hold"), t, u=lift, head_add=.05)
    o.append(f["svg"])
    hx, hy = people.hand_pos(f, "n", 40)
    prog = ramp(t, clk, 8.0)
    o.append(PR.glow(hx + 20, hy - 40, 260, .6 * bump(t, clk, .05, .5), "#fff4cf"))
    o.append(stopwatch(hx + 20, hy - 40, .5, prog, t, click=bump(t, clk, .04, .2)))
    o.append(PR.sparkles(hx + 20, hy - 40, 1.6, bump(t, clk, .05, .35), t, seed=3, n=5, r=160))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, clk, 8)
    return view("".join(o), 600 + dx, 800 + dy - 40 * u, 1.15 + .2 * u + .05 * bump(t, clk, .04, .3), 0)


def frame_s08(t):
    """«две минуты, и можно бросить»: Дима садится за отчёт, секундомер на столе дошёл до конца на «бросить» — дзынь."""
    a, b = T0("s08"), T1("s08")
    sit = ease_io(ramp(t, a - .1, .45))
    done = stress(32, .2)
    prog = ramp(t, a + .2, done - a - .2)
    o = [room(t)]
    o.append(calendar30(270, 430, .7, 0, t))
    o.append(chair(420, FL - 240, 1.0))
    hip = FL - 300 - 40 + 130 * (1 - sit) * 0
    if sit < .5:
        f = dima(420, FL + 60, .5, "look82", "d82_rest", t)
    else:
        f = dima_sit(420, FL - 290, .5, "calm82" if t < done else "wow82", t, lean=.1)
    _ = hip
    o.append(PR.desk(680, FL - 300, w=520, depth=100, leg_h=260, seed=6))
    o.append(f["svg"])
    o.append(PR.paper(640, FL - 345, 1.2, rot=4, seed=2, kind="lines", sy=.4))
    o.append(stopwatch(860, FL - 420, .5, prog, t, click=bump(t, done, .04, .2)))
    o.append(PR.sparkles(860, FL - 420, 1.4, bump(t, done, .05, .4), t, seed=4, n=5, r=140))
    o.append(PR.glow(860, FL - 420, 200, .8 * bump(t, done, .05, .5), "#ffe28a"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, done, 8)
    return view("".join(o), 620 + dx + 60 * u, 1000 + dy, 1.35 + .14 * u + .06 * bump(t, done, .04, .3), 0)


WEEK1 = times_acc(W(33), W(37) + .2, 7, 1.2)


def frame_s09(t):
    """«Первая неделя: бросал почти всегда»: на дзынь Дима встаёт и уходит; клетки первой недели закрашены наполовину."""
    a, b = T0("s09"), T1("s09")
    o = [room(t)]
    n = count(t, WEEK1)
    o.append(calendar30(540, 440, .95, n, t, half=7))
    o.append(shelf(*CAT_SHELF, 240))
    o.append(cat_tapping(CAT_SHELF[0], CAT_SHELF[1], .42, t, WEEK1))
    for i, ta in enumerate(WEEK1):
        if t >= ta:
            o.append(tap_ring(*cell_world(540, 440, .95, i), t, ta, .95))
    o.append(chair(300, FL - 240, 1.0))
    o.append(PR.desk(560, FL - 300, w=480, depth=100, leg_h=260, seed=6))
    up = W(35)                                   # «бросал»: встаёт и уходит
    cyc = ((t - a) % .55) / .55
    o.append(stopwatch(700, FL - 410, .42, min(1.0, cyc * 1.6), t, click=bump(t, a + .55 * int((t - a) / .55), .04, .15)))
    if t < up:
        f = dima_sit(300, FL - 290, .5, "squint82", t, lean=.1)
    else:
        w = t - up
        f = people.dima82_walk(300 - 520 * w, FL - (people.LEG_LEN - 12) * .5 - 6, .5, (w / .55) % 1.0, t=t, expr="calm82", mug=False, flip=True)
    o.append(f["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, up, 6)
    return view("".join(o), 580 + dx, 900 + dy, 1.12 + .1 * u, 0)


# ═════════════════════════ s10: призыв ═════════════════════════
def frame_s10(t):
    import story_cta_tg as tg
    press = W(41) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=os.path.join(STORY, "common"))


# ═════════════════════════ s11–s15: вторая и третья недели ═════════════════════════
def frame_s11(t):
    """«там весь мой дневник этих тридцати дней»: календарь крупно, подсветка бежит по всем 30 клеткам, кот следит."""
    a, b = T0("s11"), T1("s11")
    o = [room(t)]
    o.append(calendar30(540, 640, 1.25, 7, t, half=7, sweep=ramp(t, W(48), WE(50) - W(48)), glow=.3 * bump(t, W(49), .1, .5)))
    o.append(shelf(1000, 1030, 240))
    look = -.9 + 1.6 * ramp(t, W(48), WE(50) - W(48))
    o.append(cat(1000, 1030, .45, t, dict(look=(look, -.4), tilt=6 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 580 + 40 * u, 720, 1.15 + .1 * u, 0)


WEEK2 = times_acc(W(51), W(54), 7, 1.8)
LAP_AT = W(53)                                 # «третьей»: стрелка прошла две минуты


def frame_s12(t):
    """«Вторая: на третьей минуте»: вторая неделя закрашивается быстрее и целиком; секундомер проходит две минуты."""
    a, b = T0("s12"), T1("s12")
    o = [room(t)]
    n = 7 + count(t, WEEK2)
    o.append(calendar30(420, 520, .95, n, t, half=7))
    o.append(shelf(860, 860, 220))
    o.append(cat_tapping(860, 860, .4, t, WEEK2))
    for i, ta in enumerate(WEEK2):
        if t >= ta:
            o.append(tap_ring(*cell_world(420, 520, .95, 7 + i), t, ta, .95))
    prog = .55 + .45 * ramp(t, a, LAP_AT - a)
    lap = .25 * ramp(t, LAP_AT, b + .3 - LAP_AT)
    o.append(PR.glow(540, 1120, 260, .7 * bump(t, LAP_AT, .05, .5), "#c8f0b0"))
    o.append(stopwatch(540, 1120, .7, prog, t, click=0, lap=lap))
    o.append(PR.sparkles(540, 1120 - 150 * .7, 1.4, bump(t, LAP_AT, .05, .4), t, seed=5, n=5, r=120))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, LAP_AT, 7)
    return view("".join(o), 580 + dx, 800 + dy, 1.12 + .08 * u, 0)


def frame_s13(t):
    """«становилось не страшно, и я продолжал»: Дима увлечённо работает за ноутбуком, стрелка уже далеко за двумя минутами."""
    a, b = T0("s13"), T1("s13")
    o = [room(t)]
    o.append(calendar30(250, 420, .7, 7 + count(t, WEEK2), t, half=7))
    o.append(chair(330, FL - 240, 1.0))
    f = dima_sit(330, FL - 290, .5, "proud82" if t > W(57) else "sure82", t, lean=.12 + .03 * math.sin(t * 9))
    o.append(PR.desk(620, FL - 300, w=560, depth=100, leg_h=260, seed=7))
    o.append(f["svg"])
    o.append(PR.laptop(640, FL - 330, .5, open_=1.0, screen="on", lines=ramp(t, a, b - a), t=t))
    lap = .25 + .5 * ramp(t, a, b - a)
    o.append(stopwatch(880, FL - 420, .45, 1.0, t, lap=lap))
    for i in range(3):
        o.append(PR.check_mark(560 + i * 70, FL - 640 - i * 20, 1.4, ramp(t, W(58) + .3 * i, .2), seed=i))
    o.append(cat(980, FL - 300, .38, t, dict(look=(-.8, .1), smile=1.0 if t > W(60) else 0.0)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 620 + 40 * u, 950, 1.1 + .12 * u, 0)


WEEK3 = times_acc(W(61), W(64), 8, 2.0)
REST = times_acc(stress(66, .2), WE(68), 6, 2.2)        # «закрылись за вечер»: последние клетки до 28-й


def frame_s14(t):
    """«Третья: дела, которые висели месяц»: третья неделя летит; камера вниз — гора конвертов в паутине."""
    a, b = T0("s14"), T1("s14")
    o = [room(t, dusk=.3 * ramp(t, a, b - a))]
    n = 14 + count(t, WEEK3)
    o.append(calendar30(540, 470, .9, n, t, half=7))
    o.append(shelf(*CAT_SHELF, 240))
    o.append(cat_tapping(CAT_SHELF[0], CAT_SHELF[1], .42, t, WEEK3))
    for i, ta in enumerate(WEEK3):
        if t >= ta:
            o.append(tap_ring(*cell_world(540, 470, .9, 14 + i), t, ta, .9))
    o.append(webbed_desk(t, 1.0))
    u = ease_io(ramp(t, W(63) - .2, .7))
    return view("".join(o), 560 - 10 * u, 640 + 360 * u, .95 + .25 * u, 0)


def frame_s15(t):
    """«закрылись за вечер»: гора конвертов тает, паутина слетает, за окном вечер."""
    a, b = T0("s15"), T1("s15")
    mel = ease_io(ramp(t, a, b - a - .1))
    o = [room(t, dusk=.35)]
    o.append(calendar30(540, 470, .9, 22 + count(t, REST), t, half=7))
    o.append(PR.desk(560, FL - 300, w=760, depth=100, leg_h=260, seed=4))
    o.append(envelope_pile(300, FL - 330, 1.0, n=24, melt=mel))
    o.append(report(600, FL - 330, 1.2 * (1 - .6 * mel), seed=3))
    o.append(bank_phone(820, FL - 420, .8, 6, t=t))
    tear = ease_out(ramp(t, a, .5))
    for (x, y, ang, sp, L, sd) in ((170, FL - 640, -10, 70, 200, 4), (600, FL - 470, 200, 100, 150, 5), (820, FL - 545, -20, 90, 150, 6)):
        o.append(tf(PR.cobweb(0, 0, 1.2, tremble=1, torn=tear, t=t, ang=ang, span=sp, L=L, seed=sd, col=WEB), x + 200 * tear, y - 500 * tear, 1 - .5 * tear,
                    90 * tear))
    o.append(PR.sparkles(560, FL - 500, 2.2, bump(t, a + .3, .1, .5) + bump(t, WE(68) - .2, .1, .4), t, seed=7, n=6, r=300))
    f = dima(900, FL + 60, .5, "proud82", ("d82_rest", "d82_one"), t, u=ramp(t, W(68), .25), flip=True)
    o.append(f["svg"])
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 520 + 60 * u, 980 - 120 * u, 1.18 - .12 * u, 0)


# ═════════════════════════ s16: дверь картонная ═════════════════════════
def frame_s16(t):
    """«Оказалось, что страшно не делать, а начинать»: огромная дверь, Дима толкает — она картонная и падает."""
    a, b = T0("s16"), T1("s16")
    push = W(75)
    fall = ease_io(ramp(t, push + .05, .45)) ** 1.4
    o = [room(t)]
    o.append(calendar30(1080, 470, .7, 22 + count(t, REST), t, half=7))
    o.append(PR.glow(420, FL - 700, 700, .3 + .6 * fall, "#fff2c0"))
    o.append(rect(420 - 330, FL - 1350, 420 + 330, FL, lib.mix("#3b3440", "#fff3cf", fall)))
    if fall < .999:
        sy = math.cos(fall * math.pi / 2)
        door = PR.door(0, 0, 1.4, col="#6f4a33" if t < push else "#c9a26b")
        edge = ""
        if t >= push:
            edge = line([(-330, -20), (-300, -24), (-260, -18), (-220, -24), (-180, -18), (-140, -24), (-100, -18), (-60, -24), (-20, -18), (20, -24),
                         (60, -18), (100, -24), (140, -18), (180, -24), (220, -18), (260, -24), (300, -18), (330, -22)], 5, "#8a6a40", seed=1201)
        o.append(f'<g transform="translate(420 {FL:.1f}) scale(1 {sy:.4f})">{door}{edge}</g>')
    else:
        o.append(shape(lib.rrect(420 - 330, FL - 12, 420 + 330, FL + 22, 4), "#c9a26b", "", w=4, seed=1202))
    o.append(PR.dust_puff(420, FL - 30, 4.2, clamp((t - push - .45) / .6), seed=5))
    lean = .35 * ease_out(ramp(t, push - .35, .3))
    f = dima(760, FL + 60, .42, "squint82" if t < push else "wow82", ("d82_rest", "d82_press"), t, u=ramp(t, push - .35, .25), flip=True, lean=lean)
    o.append(f["svg"])
    u = ease_io(ramp(t, a, push - a))
    dx, dy = shake(t, push + .45, 14)
    cy = FL - 780 + 300 * u
    return view("".join(o), 560 + dx, cy + dy, .82 + .25 * u + .08 * bump(t, push + .45, .04, .3), 0)


# ═════════════════════════ s17–s18: тридцатый день, кот спит две минуты ═════════════════════════
LAST = stress(77, .3)                         # «тридцАтый»: кот ставит лапу на 30-ю клетку


def frame_s17(t):
    a, b = T0("s17"), T1("s17")
    o = [room(t, dusk=.15)]
    n = 28 + count(t, [a - .5, LAST])
    o.append(calendar30(540, 600, 1.15, n, t, half=7, glow=.6 * bump(t, LAST, .05, .7)))
    sx, sy = 980, 960
    o.append(shelf(sx, sy, 260))
    if t < W(81):
        o.append(cat_tapping(sx, sy, .48, t, [LAST], look=(-.9, -.4)))
    else:
        yawn = bump(t, W(81), .2, .5)
        o.append(CT.curl(sx - 30, sy, .42, dict(squint=1.0 - yawn, breath=1.0), t))
    o.append(tap_ring(*cell_world(540, 600, 1.15, 29), t, LAST, 1.3))
    o.append(PR.sparkles(*cell_world(540, 600, 1.15, 29), 1.6, bump(t, LAST, .05, .5), t, seed=8, n=5, r=120))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, LAST, 8)
    cx = 700 + (900 - 700) * ramp(t, W(80), .5)
    return view("".join(o), cx + dx, 820 + 60 * u + dy, 1.0 + .25 * u + .05 * bump(t, LAST, .04, .3), 0)


def frame_s18(t):
    """«две минуты, и тоже не бросил»: кот спит, мини-секундомер над ним проходит две минуты — не просыпается, дальше спит;
    камера отъезжает к ракурсу хука: весь календарь, Дима у стола."""
    a, b = T0("s18"), T1("s18")
    done = WE(83) - .05
    prog = ramp(t, a - .1, done - a + .1)
    o = [room(t, dusk=.15)]
    o.append(calendar30(CALX, CALY, CALK, 30, t, half=7, glow=.25))
    o.append(shelf(*CAT_SHELF, 240))
    o.append(CT.curl(CAT_SHELF[0] - 20, CAT_SHELF[1], .36, dict(squint=1.0, breath=1.2), t))
    o.append(stopwatch(CAT_SHELF[0] + 10, CAT_SHELF[1] - 200, .26, prog, t, click=bump(t, done, .04, .2), lap=.4 * ramp(t, done, 2.0)))
    o.append(PR.zzz(CAT_SHELF[0] - 60, CAT_SHELF[1] - 130, .8, t, ramp(t, done + .1, .3)))
    o.append(PR.desk(560, FL - 300, w=420, depth=80, leg_h=260, seed=2))
    o.append(PR.laptop(560, FL - 330, .45, open_=1.0, screen="on", t=t))
    f = dima(230, FL + 60, .5, "proud82", "d82_rest", t)
    o.append(f["svg"])
    u = ease_io(ramp(t, done - .2, b - done + .1))
    cx = CAT_SHELF[0] - 20 + (540 - CAT_SHELF[0] + 20) * u
    cy = CAT_SHELF[1] - 80 + (780 - CAT_SHELF[1] + 80) * u
    z = 2.0 + (1.05 - 2.0) * u
    return view("".join(o), cx, cy, z, 0)


FRAMES = {k[6:]: v for k, v in dict(globals()).items() if k.startswith("frame_s")}


def frame(sid, t):
    if sid not in ("s10",):
        lib.DEFS.clear()
    return FRAMES[sid](t)
