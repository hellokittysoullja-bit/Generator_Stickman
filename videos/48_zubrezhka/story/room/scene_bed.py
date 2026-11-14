"""Рилс 48, группа D: s16 (Дима спит, луна), s17 (кот на конспектах), s18 (поле комментария «кот», лапа жмёт «отправить»).
frame(sid, t) -> SVG 1080×1920 (t — общее время ролика). Герои — people.dima_head (Дима, голова лёжа: поворот −90°) и cat.py (кот как look/hero.png).
Удары — на словах по voice/words.json: «спокойно» 31.68, «кот» 32.96, «Напиши» 34.92, «кот» (печать) 35.44."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat as Cat  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, mix, rect_pts, shape, smooth  # noqa: E402

T_SPOKOYNO, T_KOT, T_NAPISHI, T_TYPE = 31.68, 32.96, 34.92, 35.44


def osc(t, f, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def whip_in(t, t0, dur=0.2):
    return 1 - ease_out(clamp((t - t0) / dur), 3)


def hook_zoom(t, t0, mx=0.4, dur=0.22, rot=-3.0):
    u = (t - t0) / dur
    if u <= 0:
        return 1 / (1 + mx), rot
    if u < 1:
        e = ease_out(u, 3)
        return 1 / (1 + mx) + (1.05 - 1 / (1 + mx)) * e, rot * (1 - e) - 1.2 * e
    v = (t - t0 - dur) / 0.3
    if v < 1:
        return 1.05 - .05 * ease_io(v), -1.2 * (1 - ease_io(v))
    return 1.0, 0.0


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


# ═════════════════════════ палитра ночи ═════════════════════════
WALL, WALL_SH = "#3a4378", "#2e3563"
FLOOR_C, FLOOR_L = "#2b2548", "#3a3262"
WOOD, WOOD_SH = "#8a5a36", "#6a4226"
BLANKET, BLANKET_SH, BLANKET_ST = "#c9654a", "#a24c36", "#e8a27a"
SHEET, SHEET_SH = "#e9e3f0", "#bdb6d4"
PAPER, PAPER_SH = "#f4efe2", "#cfc7b0"
FLOOR_Y = 1520


def stars(t):
    o = []
    pts = [(350, 400), (700, 380), (430, 560), (740, 600), (360, 700), (680, 740), (560, 430)]
    for k, (x, y) in enumerate(pts):
        r = 5 + 2 * math.sin(t * 3 + k * 1.7)
        o.append(blob([(x, y - r * 1.7, 1), (x + r * .45, y - r * .45), (x + r * 1.7, y, 1), (x + r * .45, y + r * .45),
                       (x, y + r * 1.7, 1), (x - r * .45, y + r * .45), (x - r * 1.7, y, 1), (x - r * .45, y - r * .45)], "#f6efd2"))
    return "".join(o)


def moon():
    cx, cy, r = 585, 520, 78
    g = lib.rad_grad([(0, "#fff4c8", .5), (1, "#fff4c8", 0)], cx, cy, 190, 190)
    o = [f'<rect x="{cx - 200}" y="{cy - 200}" width="400" height="400" fill="url(#{g})"/>']
    lib.DEFS.append(f'<mask id="mnm"><rect x="{cx - 200}" y="{cy - 200}" width="400" height="400" fill="#fff"/>'
                    f'<ellipse cx="{cx + 36}" cy="{cy - 14}" rx="{r * .84}" ry="{r * .9}" fill="#000"/></mask>')
    o.append(f'<g mask="url(#mnm)"><ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r}" fill="#f8efc9"/></g>')
    return "".join(o)


def window(t):
    x0, x1, y0, y1 = 320, 850, 330, 840
    sky = lib.lin_grad([(0, "#0f1736", 1), (1, "#2b3d7a", 1)], 0, 0, 0, 1)
    inner = f'<rect x="{x0 - 10}" y="{y0 - 10}" width="{x1 - x0 + 20}" height="{y1 - y0 + 20}" fill="url(#{sky})"/>'
    inner += stars(t) + moon()
    inner += blob([(x0 - 10, y1 - 90), (x0 + 120, y1 - 120), (x0 + 120, y1 - 160), (x0 + 250, y1 - 160), (x0 + 250, y1 - 100), (x1 + 10, y1 - 130),
                   (x1 + 10, y1 + 10), (x0 - 10, y1 + 10)], "#0e1430")
    for k, (x, y) in enumerate([(x0 + 150, y1 - 110), (x0 + 400, y1 - 90), (x0 + 60, y1 - 50)]):
        inner += blob(rect_pts(x, y, x + 24, y + 30), "#f2c46a")
    fr = "#e8e0d2"
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    inner += blob(rect_pts(mx - 12, y0, mx + 12, y1), fr) + blob(rect_pts(x0, my - 12, x1, my + 12), fr)
    o = [shape(rect_pts(x0, y0, x1, y1, 12), fr, inner, w=5.5, seed=906)]
    o.append(shape(rect_pts(x0 - 30, y1 - 4, x1 + 30, y1 + 34, 6), fr, blob(rect_pts(x0 - 30, y1 + 20, x1 + 30, y1 + 34), "#c8bfae"), w=4.4, seed=907))
    # шторы
    for sx, xa in ((-1, x0 - 30), (1, x1 + 30)):
        cur = [(xa, y0 - 30, 1), (xa + sx * 150, y0 - 30, 1), (xa + sx * 170, y1 + 40), (xa + sx * 120, y1 + 120, 1), (xa, y1 + 60, 1)]
        if sx == -1:
            cur = [(xa, y0 - 30, 1), (xa - 150, y0 - 30, 1), (xa - 170, y1 + 40), (xa - 120, y1 + 120, 1), (xa, y1 + 60, 1)]
        fold = "".join(line([(xa + sx * 30 * i * 1.2, y0 - 20), (xa + sx * (30 * i * 1.2 + 10), (y0 + y1) / 2), (xa + sx * 30 * i * 1.2, y1 + 50)],
                            3, mix("#7a4a8a", "#000000", .25), seed=920 + i + (3 if sx > 0 else 0), op=.7) for i in range(1, 5))
        o.append(shape(cur, "#7a4a8a", blob([(xa, y0), (xa + sx * 40, y0), (xa + sx * 60, y1 + 40), (xa, y1 + 50)], "#5e3a6e", .6) + fold, w=4.6,
                       seed=925 + (1 if sx > 0 else 0)))
    return "".join(o)


def wall_deco(t):
    o = []
    # часы
    cx, cy, r = 150, 560, 62
    o.append(shape(ellipse_pts(cx, cy, r, r, 18), "#f3ecd8", blob(ellipse_pts(cx + 14, cy + 12, r * .9, r * .8, 14), "#d8cfb4", .6), w=5, seed=930))
    for k in range(12):
        a = k * math.pi / 6
        o.append(line([(cx + math.sin(a) * r * .78, cy - math.cos(a) * r * .78), (cx + math.sin(a) * r * .9, cy - math.cos(a) * r * .9)], 3, seed=940 + k))
    ah, am = math.radians(-30), math.radians(180)   # 23:30 -> около половины
    o.append(line([(cx, cy), (cx + math.sin(ah) * r * .5, cy - math.cos(ah) * r * .5)], 5, seed=951, taper=.1, wmin=.9))
    o.append(line([(cx, cy), (cx + math.sin(am) * r * .75, cy - math.cos(am) * r * .75)], 3.6, seed=952, taper=.1, wmin=.9))
    # полка с книгами над кроватью
    o.append(shape(rect_pts(40, 800, 300, 826, 4), WOOD, "", w=4, seed=953))
    cols = ["#4c9a8a", "#d4a23e", "#c44f3a", "#6a7ac8", "#8abf6a"]
    x = 62
    for i, (w_, h_) in enumerate([(34, 110), (28, 96), (38, 120), (30, 100), (34, 112)]):
        o.append(shape(rect_pts(x, 800 - h_, x + w_, 800, 3), cols[i], line([(x + 6, 800 - h_ + 14), (x + w_ - 6, 800 - h_ + 14)], 2.4, mix(cols[i], "#000000", .3),
                                                                           seed=960 + i), w=3.8, seed=955 + i))
        x += w_ + 6
    return "".join(o)


def floor_room():
    o = [f'<rect x="-1400" y="-1400" width="4200" height="{FLOOR_Y + 1400}" fill="{WALL}"/>']
    o.append(blob(rect_pts(-1400, -1400, 2800, 300), WALL_SH, .35))
    o.append(shape(rect_pts(-1400, FLOOR_Y - 18, 2800, FLOOR_Y + 14), mix(WALL, "#000000", .25), "", w=3.4, seed=900))
    o.append(f'<rect x="-1400" y="{FLOOR_Y + 14}" width="4200" height="1500" fill="{FLOOR_C}"/>')
    for k in range(8):
        y = FLOOR_Y + 60 + k * 70
        o.append(line([(-1400, y), (2800, y + 8)], 3, FLOOR_L, taper=0, wmin=1, seed=970 + k, op=.8))
    return "".join(o)


# ═════════════════════════ кровать, Дима ═════════════════════════
HEAD_C = (258.0, 1148.0)


def sleep_eyes(expr, EN, EF, bags=True, lash_col=INK):
    """Закрытые во сне глаза: дуги «∪» с ресницами и мешки под ними (людям Димы в профиль-3/4)."""
    o = []
    for (cx, cy, rx, ry), sd in ((EF, 160), (EN, 161)):
        o.append(blob([(cx - rx * .8, cy + ry * .55), (cx, cy + ry * 1.3), (cx + rx * .8, cy + ry * .55), (cx, cy + ry * .85)], "#a77f8c", .7))
        arc = [(cx - rx * .85, cy - ry * .1), (cx - rx * .4, cy + ry * .28), (cx + rx * .1, cy + ry * .36), (cx + rx * .85, cy - ry * .06)]
        o.append(line(arc, 6.4, INK, seed=sd, taper=.4, wmin=.4))
        for j in (-1, 0, 1):
            o.append(line([(cx + rx * (.2 + .3 * j), cy + ry * .3), (cx + rx * (.26 + .34 * j), cy + ry * .52)], 2.4, INK, seed=sd + 5 + j, op=.9))
    return "".join(o)


def dima_head_lying(t, closed=1.0, k=.86, rot=-86.0, dy=0.0):
    people.C = people.PAL["dima"]
    ex = dict(lid=-1.15, closed=0.0, look=(0, 0), brows="calm", mouth="flat", hair=2.0 * osc(t, .3))
    # во сне рот чуть приоткрыт — дышит
    ex.update(mouth="talk", open=.12 + .07 * osc(t, .32), smile=.0)
    old = people.eyes
    people.eyes = sleep_eyes
    try:
        h = people.dima_head(ex)
    finally:
        people.eyes = old
    return f'<g transform="translate({HEAD_C[0]:.1f} {HEAD_C[1] + dy:.1f}) rotate({rot:.2f}) scale({k})">{h}</g>'


def bed_back():
    o = []
    # каркас: изголовье, изножье, ножки
    o.append(shape(rect_pts(36, 1010, 118, FLOOR_Y - 20, 8), WOOD, blob(rect_pts(88, 1010, 118, FLOOR_Y - 20), WOOD_SH, .8) +
                   line([(60, 1060), (60, 1440)], 3, mix(WOOD, "#000000", .3), seed=981, op=.7), w=5, seed=980))
    o.append(shape(rect_pts(780, 1280, 842, FLOOR_Y - 20, 8), WOOD, blob(rect_pts(814, 1280, 842, FLOOR_Y - 20), WOOD_SH, .8), w=5, seed=982))
    o.append(shape(rect_pts(110, 1370, 790, 1470, 10), WOOD, blob(rect_pts(110, 1440, 790, 1470), WOOD_SH, .8), w=5, seed=983))
    # матрас
    o.append(shape(rect_pts(110, 1262, 790, 1384, 26), SHEET, blob(rect_pts(110, 1344, 790, 1384), SHEET_SH, .9), w=5, seed=984))
    return "".join(o)


def pillow(t):
    pts = [(130, 1240), (150, 1150), (230, 1118), (330, 1128), (394, 1170), (398, 1250, 1), (140, 1262, 1)]
    inner = blob([(250, 1200), (394, 1190), (398, 1262), (250, 1262)], "#d3cde4", .8)
    inner += line([(190, 1180), (260, 1160), (330, 1170)], 2.6, "#bdb6d4", seed=990, op=.8)
    return shape(pts, "#f1ecf8", inner, w=5, seed=991)


def blanket(t, breath=0.0, up=0.0, shiver=0.0):
    """Одеяло от шеи до ног; breath — подъём груди (px), up — вздох на «спокойно»."""
    lift = breath + up
    top = [(372, 1262, 1), (392, 1196 - lift * .8), (450, 1176 - lift), (540, 1178 - lift * 1.1), (640, 1186 - lift * .6), (730, 1180 - lift * .3),
           (808, 1196), (822, 1262, 1)]
    fall = [(822, 1262, 1), (840, 1340), (824, 1420, 1), (700, 1432), (520, 1440), (380, 1428), (372, 1380), (372, 1262, 1)]
    pts = top[:-1] + fall[:-1]
    inner = blob([(560, 1180), (824, 1190), (840, 1420), (560, 1430)], BLANKET_SH, .7)
    for i in range(5):
        x = 430 + i * 88
        inner += line([(x, 1190 - lift * (1 - i * .15)), (x - 10, 1300), (x - 20, 1430)], 9, BLANKET_ST, taper=0, wmin=1, seed=1000 + i, op=.65)
    inner += line([(372, 1262), (392, 1210 - lift * .8)], 3, "#7a3a2a", seed=1010, op=.6)
    o = shape(pts, BLANKET, inner, w=5.4, seed=1011)
    # отворот у шеи
    o += shape([(372, 1232), (392, 1202 - lift * .8), (452, 1190 - lift), (456, 1226), (392, 1250)], mix(BLANKET, "#ffffff", .22),
               "", w=4, seed=1012)
    return o


def hand_on_blanket(lift):
    """Рука поверх одеяла у груди (спокойно лежит)."""
    people.C = people.PAL["dima"]
    x, y = 470.0, 1186.0 - lift * 1.0
    sl = shape([(x - 80, y + 14, 1), (x - 70, y - 26), (x + 14, y - 34), (x + 30, y + 4, 1), (x - 10, y + 22)], people.C["TOP"],
               blob([(x - 70, y + 8), (x + 30, y + 4), (x - 10, y + 22)], people.C["TOP_SH"], .8), w=4.6, seed=1020)
    fist = shape(ellipse_pts(x + 52, y - 4, 34, 24, 12, rot=-10), people.C["SKIN"], blob(ellipse_pts(x + 56, y + 8, 28, 12, 10), people.C["SKIN_SH"], .8),
                 w=4.4, seed=1021)
    fing = "".join(line([(x + 34 + i * 14, y - 12 + i * 2), (x + 38 + i * 14, y + 6 + i)], 2.2, seed=1022 + i, op=.9) for i in range(3))
    return sl + fist + fing


def zzz(x, y, t, e=1.0):
    o = []
    for j in range(3):
        ph = (t * .5 + j / 3) % 1
        sz = 44 + 50 * ph
        a = math.sin(math.pi * ph) * e
        cx, cy = x + 120 * ph + 14 * math.sin(ph * 6 + j), y - 300 * ph
        o.append(f'<text x="{cx:.1f}" y="{cy:.1f}" font-family="IDB" font-size="{sz:.1f}" fill="#f6f1e3" stroke="{INK}" stroke-width="6" '
                 f'paint-order="stroke" opacity="{a:.3f}">Z</text>')
    return "".join(o)


def chair(stack_extra=0.0):
    o = []
    cx0, cx1 = 850, 1070
    o.append(shape(rect_pts(cx1 - 40, 1010, cx1, 1404, 6), WOOD, blob(rect_pts(cx1 - 14, 1010, cx1, 1404), WOOD_SH, .8), w=5, seed=1030))
    o.append(shape(rect_pts(cx1 - 40, 1060, cx1, 1090, 4), WOOD_SH, "", w=3.6, seed=1031))
    o.append(shape(rect_pts(cx0, 1396, cx1, 1430, 8), WOOD, blob(rect_pts(cx0, 1418, cx1, 1430), WOOD_SH, .8), w=5, seed=1032))
    for x, sd in ((cx0 + 14, 1033), (cx1 - 40, 1034)):
        o.append(shape(rect_pts(x, 1426, x + 20, FLOOR_Y - 10, 4), WOOD, blob(rect_pts(x + 10, 1426, x + 20, FLOOR_Y - 10), WOOD_SH, .8), w=4.4, seed=sd))
    return "".join(o)


STACK = (930.0, 1396.0)       # центр низа стопки на сиденье


def notes_stack(t=0.0, crush=0.0):
    """Стопка конспектов: листы чуть сдвинуты, на каждом строки каракулей (без букв)."""
    x, y = STACK
    o = []
    specs = [(0, 176, 26, "#f4efe2", -1.2), (1, 168, 24, "#efe8d6", 1.6), (2, 172, 26, "#f4efe2", -.6), (3, 160, 24, "#e9e1cb", 2.0),
             (4, 164, 24, "#f4efe2", -1.4)]
    yy = y
    for i, w_, h_, col, rot in specs:
        h_ = h_ * (1 - crush * .12)
        yy -= h_
        pts = rect_pts(x - w_ / 2, yy, x + w_ / 2, yy + h_, 5)
        ln = "".join(line([(x - w_ / 2 + 16, yy + 8 + j * 7), (x + w_ / 2 - 20 - 14 * ((i + j) % 3), yy + 8 + j * 7)], 2, "#6a7ac8", seed=1040 + i * 4 + j, op=.8)
                     for j in range(2))
        o.append(f'<g transform="rotate({rot} {x} {yy + h_ / 2})">' + shape(pts, col, blob(rect_pts(x - w_ / 2, yy + h_ - 6, x + w_ / 2, yy + h_), PAPER_SH, .9) + ln,
                                                                           w=3.8, seed=1050 + i) + "</g>")
    # скрепка-закладка сверху
    o.append(shape(rect_pts(x + 40, yy - 8, x + 62, yy + 34, 3), "#d8483c", "", w=3.2, seed=1060))
    return "".join(o), yy


def moon_beam():
    g = lib.lin_grad([(0, "#cfe0ff", .22), (1, "#cfe0ff", 0)], 0, 0, 0, 1)
    pts = [(420, 800), (760, 800), (1000, 1500), (180, 1500)]
    return f'<path d="{lib.fill_d(pts)}" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def night_overlay():
    g = lib.rad_grad([(0, "#0a0c20", 0), (.5, "#0a0c20", 0), (1, "#0a0c20", .55)], 540, 1000, 1300, 1500)
    return f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g})"/>'


def room_world(t, cat_svg="", cat_front="", cat_extra="", breath=0.0, up=0.0, closed=1.0, zz=1.0, crush=0.0):
    stack, _ = notes_stack(t, crush)
    o = floor_room() + window(t) + wall_deco(t) + moon_beam()
    o += bed_back() + pillow(t) + dima_head_lying(t, closed) + blanket(t, breath, up) + hand_on_blanket(breath + up)
    o += chair() + stack + cat_svg + cat_extra
    o += zzz(HEAD_C[0] + 120, HEAD_C[1] - 150, t, zz)
    return o


def compose(world, cam, extra="", vig=True):
    cx, cy, s, r = cam
    set_ink(s)
    body = [f'<rect width="1080" height="1920" fill="{WALL}"/>', f'<g transform="{lib.cam(cx, cy, s, r)}">{world}{night_overlay()}{extra}</g>']
    if vig:
        g = lib.rad_grad([(0, "#120a1c", 0), (.62, "#120a1c", 0), (1, "#120a1c", .42)], 540, 900, 1180, 1400)
        body.append(f'<rect width="1080" height="1920" fill="url(#{g})"/>')
    return lib.svg("".join(body))


# ═════════════════════════ s16: Дима спит ═════════════════════════
def s16(t):
    sig = bump(t, T_SPOKOYNO - .15, .9)               # вздох: грудь поднимается и опускается
    breath = 5 * osc(t, .33) + 2
    zz = 1.0
    world = room_world(t, breath=breath, up=22 * sig, closed=1.0, zz=zz)
    # лёгкое облачко выдоха на вздохе
    puff = ""
    if sig > .02:
        px, py = HEAD_C[0] + 210 * 0 + 128, HEAD_C[1] - 60
        for j in range(0):
            ph = clamp((t - (T_SPOKOYNO - .05) - j * .12) / .7)
            if 0 < ph < 1:
                r = 14 + 26 * ph + 4 * j
                puff += blob(ellipse_pts(px + 90 * ph + 12 * j, py - 70 * ph - 20 * j, r, r * .8, 12), "#f6f1e3", .55 * (1 - ph))
    s, rot = hook_zoom(t, 30.3, .35, .24, -3.0)
    ww = whip_in(t, 30.3, .2)
    u = ease_io(clamp((t - 30.3) / 2.6))
    cam = (470 + 120 * ww - 90 * u, 1180 - 30 * u, (1.0 + .5 * u) * s, rot - .5 * u)
    cam = (cam[0], cam[1], 1.12 * cam[2], cam[3])
    return compose(world, cam, extra=puff)


# ═════════════════════════ s17: кот на конспектах ═════════════════════════
def cat_state(t):
    bl = 0.0
    for c, half, hold in ((T_KOT, .30, .22), (34.0, .26, .2)):
        a = c - half
        if a <= t <= c + hold + half:
            bl = ease_io((t - a) / half) if t < c else (1.0 if t < c + hold else 1 - ease_io((t - c - hold) / half))
    settle = .6 + .4 * math.cos(math.pi * clamp((t - 32.5) / 1.2))
    return dict(blink=max(bl, .5 * smooth(32.9, 33.1, t) * 0), tilt=4 + 3 * osc(t, .22), tail=5 * osc(t, .45), ear=-8 * bump(t, 33.2, .4),
                look=(0, .3), smile=1.0 if t > 33.4 else 0.0, flame_e=.9 + .2 * osc(t, 1.7), turn=-.1 + .05 * osc(t, .2) * settle)


CAT_K = .78


def cat_pos(t, drop=None):
    x, y = STACK
    _, top = notes_stack()
    return x - 4, top + 14


def cat_on_stack(t, st):
    x, y = cat_pos(t)
    # хвост кот держит свёрнутым вдоль конспектов; поверх листов — лапки впереди
    return Cat.draw(x, y, CAT_K, st, t)


def s17(t):
    st = cat_state(t)
    # приземление: кот «садится» на стопку с лёгким сжатием стопки на 32.7–33.0
    land = bump(t, 32.62, .5)
    cat_svg = cat_on_stack(t, st)
    stack_crush = land
    stack_svg, top = notes_stack(t, stack_crush)
    x, y = cat_pos(t)
    hx, hy = Cat.head_world(x, y, CAT_K, st)
    fx, fy = hx + 120 * CAT_K, hy - 80 * CAT_K
    g = lib.rad_grad([(0, "#ffb050", .38), (1, "#ffb050", 0)], fx, fy, 260, 260)
    glow = f'<rect x="{fx - 280:.1f}" y="{fy - 280:.1f}" width="560" height="560" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    o = floor_room() + window(t) + wall_deco(t) + moon_beam()
    o += bed_back() + pillow(t) + dima_head_lying(t, 1.0) + blanket(t, 5 * osc(t, .33) + 2, 0) + hand_on_blanket(5 * osc(t, .33) + 2)
    o += chair() + stack_svg + cat_svg
    o += zzz(HEAD_C[0] + 120, HEAD_C[1] - 150, t, .9)
    u = clamp((t - 32.5) / 2.8)
    ww = whip_in(t, 32.7, .2)
    bu = bump(t, T_KOT, .3)
    cam = (hx - 20 + 0 * u - 240 * ww, hy + 120 - 28 * u, (2.35 + .45 * ease_io(u)) * (1 + .04 * bu), .8 - 1.2 * u + 1.0 * bu * osc(t, 7))
    return compose(o + "", cam, extra=glow)


# ═════════════════════════ s18: поле комментария ═════════════════════════
UI_BG = "#1b1f3d"
FIELD = (70, 640, 1010, 860)        # x0, y0, x1, y1
SEND = (905.0, 750.0, 62.0)


def typed(t):
    n = 0
    for i, tt in enumerate((T_TYPE, T_TYPE + .16, T_TYPE + .32)):
        if t >= tt:
            n = i + 1
    return "кот"[:n]


def heart(x, y, k, rot=0.0, col="#ff4f6d"):
    pts = [(0, 40), (-14, 26), (-40, 6), (-44, -22), (-28, -42), (0, -26, 1), (28, -42), (44, -22), (40, 6), (14, 26)]
    pts = [(x + p[0] * k, y + p[1] * k) + ((1,) if len(p) > 2 else ()) for p in pts]
    sh = blob([(x - 4 * k, y - 36 * k), (x - 34 * k, y - 38 * k), (x - 40 * k, y - 16 * k), (x - 22 * k, y - 20 * k)], "#ff9fb2", .9)
    return f'<g transform="rotate({rot:.1f} {x:.1f} {y:.1f})">' + shape(pts, col, sh, w=5, seed=1100) + "</g>"


def paw(x, y, press):
    """Лапа кота (шерсть как у look/hero.png, оранжевые подушечки): предплечье из-за нижнего правого края, кончик пальцев в (x, y)."""
    CAT, SH = Cat.CAT, Cat.CAT_SH
    y = y + 6 * press
    arm = [(x - 80, y + 40), (x - 90, y + 300), (x - 70, y + 1100, 1), (x + 210, y + 1100, 1), (x + 150, y + 300), (x + 84, y + 40)]
    o = shape(arm, CAT, blob([(x + 20, y + 40), (x + 74, y + 40), (x + 150, y + 300), (x + 210, y + 1100), (x + 60, y + 1100)], SH, .8), w=5.6, seed=1110)
    for i in range(7):
        yy = y + 150 + i * 110
        o += line([(x - 40 + 8 * i, yy), (x - 34 + 8 * i, yy + 22)], 2.6, Cat.CAT_EDGE, seed=1130 + i, op=.8)
    top = [(x - 74, y + 40, 1), (x - 82, y - 20), (x - 60, y - 74), (x - 20, y - 94), (x + 24, y - 94), (x + 62, y - 74), (x + 82, y - 20), (x + 74, y + 40, 1)]
    o += shape(top, CAT, blob([(x + 20, y - 94), (x + 62, y - 74), (x + 82, y - 20), (x + 74, y + 40), (x + 20, y + 40)], SH, .7), w=5.6, seed=1111)
    for k, dx in enumerate((-26, 0, 26)):
        o += line([(x + dx, y - 92), (x + dx + 2, y - 60)], 2.8, seed=1120 + k, op=.9)
    o += blob(ellipse_pts(x, y - 2, 40, 32, 12), "#e8823a")
    for dx in (-46, -16, 16, 46):
        o += blob(ellipse_pts(x + dx * .9, y - 58 + abs(dx) * .25, 11, 13, 8), "#e8823a")
    return f'<g transform="rotate(-22 {x} {y})">{o}</g>'


def ui(t):
    x0, y0, x1, y1 = FIELD
    o = []
    # заголовок
    o.append(f'<text x="{x0}" y="{y0 - 70}" font-family="IDB" font-size="58" fill="#f6f1e3">Комментарии</text>')
    o.append(f'<text x="{x0 + 450}" y="{y0 - 70}" font-family="IDB" font-size="58" fill="#8d93c6">{1 if t > 36.4 else 0}</text>')
    sent = t >= 36.42
    # карточка поля
    card = shape(rect_pts(x0, y0, x1, y1, 40), "#f7f4ec", blob(rect_pts(x0, y1 - 40, x1, y1, 30), "#dcd5c3", .9), w=5.2, seed=1130)
    o.append(card)
    # аватар
    av = ellipse_pts(x0 + 90, (y0 + y1) / 2, 52, 52, 16)
    o.append(shape(av, "#d4a23e", f'<text x="{x0 + 90}" y="{(y0 + y1) / 2 + 22}" font-family="IDB" font-size="62" text-anchor="middle" fill="#3d2418">Д</text>', w=4.6, seed=1131))
    txt = "" if sent else typed(t)
    tx = x0 + 180
    ty = (y0 + y1) / 2 + 34
    if txt:
        o.append(f'<text x="{tx}" y="{ty}" font-family="IDB" font-size="104" fill="#1c1622">{txt}</text>')
    else:
        if not sent:
            o.append(f'<text x="{tx}" y="{ty - 4}" font-family="IDB" font-size="56" fill="#a49fb4">Напиши…</text>')
    cw = {"": 0, "к": 58, "ко": 118, "кот": 168}[txt]
    if not sent and int((t - T_NAPISHI) * 2.6) % 2 == 0:
        o.append(f'<rect x="{tx + cw + 8 + (14 if not txt else 0) * 0}" y="{ty - 90}" width="6" height="110" rx="3" fill="#3a4378"/>')
    # кнопка «отправить»
    sx, sy, sr = SEND
    press = ease_io(clamp((t - 36.08) / .12)) * (1 - ease_io(clamp((t - 36.3) / .15)))
    active = txt == "кот"
    col = "#3fa58f" if active else "#aab0c4"
    bs = 1 - .1 * press
    o.append(f'<g transform="translate({sx} {sy}) scale({bs:.3f}) translate({-sx} {-sy})">' +
             shape(ellipse_pts(sx, sy, sr, sr, 18), col, blob(ellipse_pts(sx + 10, sy + 14, sr * .8, sr * .6, 12), mix(col, "#000000", .25), .5), w=4.6, seed=1132) +
             blob([(sx - 24, sy - 28), (sx + 30, sy, 1), (sx - 24, sy + 28), (sx - 14, sy)], "#ffffff") + "</g>")
    # кольцо от нажатия
    ph = clamp((t - 36.22) / .5)
    if 0 < ph < 1:
        r = sr * (1 + 1.3 * ph)
        o.append(f'<circle cx="{sx}" cy="{sy}" r="{r:.1f}" fill="none" stroke="#7fe0c8" stroke-width="{10 * (1 - ph):.1f}" opacity="{1 - ph:.2f}"/>')
    # опубликованный комментарий
    if sent:
        e = t - 36.42
        k = ease_out(clamp(e / .25), 3)
        cy = y1 + 110 + (1 - k) * 60
        o.append(f'<g opacity="{k:.2f}">')
        o.append(shape(rect_pts(x0, cy - 20, x1, cy + 200, 34), "#2a3060", blob(rect_pts(x0, cy + 150, x1, cy + 200, 30), "#222850", .9), w=4.6, seed=1140))
        o.append(shape(ellipse_pts(x0 + 72, cy + 60, 42, 42, 16), "#d4a23e",
                       f'<text x="{x0 + 72}" y="{cy + 82}" font-family="IDB" font-size="52" text-anchor="middle" fill="#3d2418">Д</text>', w=4.2, seed=1141))
        o.append(f'<text x="{x0 + 140}" y="{cy + 48}" font-family="IDB" font-size="40" fill="#a9afe0">Дима · сейчас</text>')
        o.append(f'<text x="{x0 + 140}" y="{cy + 128}" font-family="IDB" font-size="76" fill="#f6f1e3">кот</text>')
        hk = .9 + .12 * osc(t, 1.8)
        if e > .3:
            hk *= .7 + .3 * ease_out(clamp((e - .3) / .3))
        o.append(heart(x1 - 90, cy + 100, .8 * hk))
        o.append("</g>")
    return "".join(o)


def big_hearts(t):
    e = t - 36.55
    if e <= 0:
        return ""
    o = []
    sp = lib.spring(e, 2.2, 5.5)
    o.append(heart(540, 410, 2.7 * sp * (1 - .0 * e), -6 + 5 * osc(t, 1.1)))
    for j in range(6):
        ph = clamp((t - 36.7 - j * .14) / 1.3)
        if 0 < ph < 1:
            x = 220 + j * 120 + 30 * math.sin(ph * 5 + j)
            y = 560 - 440 * ph
            o.append(f'<g opacity="{math.sin(math.pi * ph):.2f}">{heart(x, y, .5 + .22 * (j % 3), 12 * math.sin(ph * 4 + j), "#ff7c94")}</g>')
    return "".join(o)


def s18(t):
    # фон — та же ночная комната, тёмная и размытая
    st = dict(blink=1.0)
    bgw = floor_room() + window(t) + wall_deco(t) + bed_back() + pillow(t) + dima_head_lying(t, 1.0) + blanket(t, 5 * osc(t, .33) + 2, 0)
    bgw += chair() + notes_stack(t)[0]
    bl = lib.blur(7)
    shade = f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="{UI_BG}" opacity=".78"/>'
    set_ink(1.0)
    ww = whip_in(t, 35.0, .2)
    u = ease_io(clamp((t - 34.8) / 3.9))
    sc = 1.0 + .08 * u + .03 * bump(t, T_TYPE, .3) + .03 * bump(t, 36.22, .3)
    shake = 8 * bump(t, 36.2, .25) * osc(t, 11)
    cx, cy = 540 + 220 * ww + shake, 780 + 20 * u
    press = bump(t, 36.04, .35) if t > 36.04 else 0.0
    # лапа приходит с 35.8, жмёт ~36.1, уходит после 36.5
    come = ease_out(clamp((t - 35.75) / .38), 3) * (1 - ease_in(clamp((t - 36.6) / .35), 2))
    px = SEND[0] + 4 * (1 - come)
    py = SEND[1] + 70 + 330 * (1 - come)
    pr = clamp((t - 36.08) / .1) * (1 - clamp((t - 36.3) / .15))
    wobble = 3 * osc(t, 3)
    paw_svg = paw(px, py + wobble * (1 - pr) - 70 * pr, pr) if come > .01 else ""
    cam = lib.cam(cx, cy, sc, -.8 * (1 - u))
    body = [f'<rect width="1080" height="1920" fill="{UI_BG}"/>',
            f'<g {bl}><g transform="{lib.cam(540, 1000, 1.0, 0)}">{bgw}{night_overlay()}</g></g>', shade,
            f'<g transform="{cam}">{ui(t)}{paw_svg}{big_hearts(t)}</g>']
    return lib.svg("".join(body))


SHOTS = {"s16": s16, "s17": s17, "s18": s18}


def frame(sid, t):
    lib.DEFS.clear()
    return SHOTS[sid](t)
