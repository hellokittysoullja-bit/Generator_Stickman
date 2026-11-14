"""Кабинет Димы рилса 48 «зубрёжка»: планы s01 s02 s06 s14 (группа A).
s01 — ночь, конспект, красные глаза, часы 03:10; s02 — экзаменационный лист, штамп «5»; s06 — экзамен, пустой лист;
s14 — день, спокойное повторение. frame(sid, t) -> SVG 1080×1920 (t — общее время ролика). Удары — на словах words.json."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat as Cat  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import world as Wd  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, mix, rect_pts, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wi(i):
    return WORDS[i]["start"]


T_UCHIL, T_NOCH, T_SDAL = wi(1), wi(3), wi(7)
T_NICHEGO = wi(21)
T_POVTOR = wi(67)

BS = 0.62
FLOOR = Wd.FLOOR
HIP = np.array([470.0, 1372.0])
DESK_Y = 1290            # ближний край столешницы
PAPER = [(610, 1292), (1010, 1292), (1090, 1190), (700, 1190)]    # лист: ближний край, дальний край


def osc(t, f, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


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


def whip(t, t0, dur=0.22):
    return 1 - ease_out(clamp((t - t0) / dur), 3)


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


# ── красные глаза: подмена people.eyes (прожилки и розоватый белок, expr["red"] 0..1)
_orig_eyes = people.eyes


def _eyes_red(expr, EN, EF, bags=True, lash_col=INK):
    s = _orig_eyes(expr, EN, EF, bags, lash_col)
    r = expr.get("red", 0.0)
    if r <= 0:
        return s
    s = s.replace("#f6f2ea", mix("#f6f2ea", "#f1a79b", .55 * r))
    if expr.get("closed", 0.0) < .5 and expr.get("laugh", 0.0) < .5:
        for (cx, cy, rx, ry) in (EN, EF):
            for k, (a0, a1) in enumerate([(-.92, -.5), (-.85, -.42), (.9, .5), (.82, .4)]):
                y0 = cy + ry * (.15 + .22 * (k % 2))
                s += line([(cx + rx * a0, y0), (cx + rx * (a0 + a1) / 2, y0 + ry * .22), (cx + rx * a1, y0 + ry * .3)], 1.9, "#d4443c", seed=3200 + k, op=.75 * r, taper=.5)
    return s


people.eyes = _eyes_red


# ═════════════════════════ Дима ═════════════════════════
def dima(t, hip=None, lean=0.05, arms=None, hands=None, expr=None, head_ang=0.0, feet=None):
    hip = HIP if hip is None else np.array(hip, float)
    if feet is None:
        feet = {"n": ((hip[0] + 255, FLOOR + 22), 0.0), "f": ((hip[0] + 205, FLOOR + 12), 0.0)}
    p = dict(hip=tuple(hip), scale=BS, lean=lean, feet=feet, arms=arms, hands=hands or {}, expr=expr or {}, head_ang=head_ang,
             hood=0.0, strings=(3 * osc(t, 1.3), 2 * osc(t, 1.1, 1)))
    return people.draw(p, "dima")


def kw_hand():
    people.C = people.PAL["dima"]
    return dict(shape_fn=people.shape, line_fn=people.line, skin=people.C["SKIN"], skin_sh=people.C["SKIN_SH"], skin_sh2=people.C["SKIN_SH2"])


def text(x, y, s, size, fill, rot=0.0, anchor="middle", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="IDB" font-weight="900" font-size="{size:.1f}" fill="{fill}" text-anchor="{anchor}" '
            f'transform="rotate({rot:.2f} {x:.1f} {y:.1f})" {extra}>{s}</text>')


def sweat(x, y, k, u):
    if u <= 0:
        return ""
    yy = y + 40 * k * ease_in(u)
    r = 16 * k * min(1, u * 3)
    drop = [(x, yy - r * 2.2), (x + r, yy - r * .1), (x + r * .8, yy + r * .7), (x, yy + r), (x - r * .8, yy + r * .7), (x - r, yy - r * .1)]
    return shape(drop, "#bfe6fa", blob([(x - r * .4, yy - r * .6), (x - r * .1, yy - r * .9), (x - r * .1, yy - r * .2)], "#ffffff"), w=3, seed=3001)


# ═════════════════════════ комната ═════════════════════════
def quad(p, fill, inner="", w=4.4, seed=0):
    return shape([(x, y, 1) for x, y in p], fill, inner, w=w, seed=seed)


def book(x, y, w, h, col, rot=0.0, seed=0, label=True):
    """Книга корешком к зрителю: (x, y) — левый-нижний угол."""
    pts = T_rect(x, y, w, h, rot)
    inner = blob(T_rect(x + w * .08, y - h * .78, w * .84, h * .12, rot), mix(col, "#ffffff", .55), .85)
    inner += blob(T_rect(x + w * .08, y - h * .26, w * .84, h * .1, rot), mix(col, "#ffffff", .5), .8)
    inner += blob(T_rect(x + w * .86, y - h, w * .14, h, rot), mix(col, "#000000", .22), .9)
    return shape(pts, col, inner, w=3.6, seed=seed)


def T_rect(x, y, w, h, rot=0.0):
    pts = [(x, y - h), (x + w, y - h), (x + w, y), (x, y)]
    return lib.T([(a, b, 1) for a, b in pts], 0, 0, 1, rot, x + w / 2, y)


BOOKCOL = ["#c4573f", "#3f7a72", "#d4a23e", "#4f6fa5", "#8a5a9c", "#5f9a5a", "#b9503e", "#e08a4a"]


def stack(x, y, n, seed, wob=0.0, wmax=170, h=34, t=0.0):
    """Стопка книг (лёжа), (x, y) — центр низа. wob — покачивание."""
    o = ""
    yy = y
    rs = np.random.RandomState(seed)
    for i in range(n):
        w = wmax * rs.uniform(.72, 1.0)
        dx = rs.uniform(-14, 14) + wob * (i / max(1, n)) ** 1.3 * math.sin(t * 7 + i)
        col = BOOKCOL[(i + seed) % len(BOOKCOL)]
        pts = [(x + dx - w / 2, yy - h), (x + dx + w / 2, yy - h), (x + dx + w / 2, yy), (x + dx - w / 2, yy)]
        inner = blob([(x + dx - w / 2 + 6, yy - h + 6), (x + dx + w / 2 - 12, yy - h + 6), (x + dx + w / 2 - 12, yy - 8), (x + dx - w / 2 + 6, yy - 8)],
                     "#f1e7d0", .95)
        inner += blob([(x + dx + w / 2 - 12, yy - h), (x + dx + w / 2, yy - h), (x + dx + w / 2, yy), (x + dx + w / 2 - 12, yy)], mix(col, "#000000", .2))
        o += shape([(a, b, 1) for a, b in pts], col, inner, w=3.4, seed=seed * 10 + i)
        yy -= h - 2
    return o, yy


def bookcase(mode):
    x0, x1, y0, y1 = 930, 1370, 580, 1260
    o = shape(rect_pts(x0, y0, x1, y1, 6), "#8f5f3a", blob(rect_pts(x0 + 14, y0 + 14, x1 - 14, y1 - 14), "#5b3a22"), w=5, seed=3300)
    rs = np.random.RandomState(48)
    for r_, ys in enumerate([y0 + 170, y0 + 360, y0 + 550]):
        o += shape(rect_pts(x0 + 8, ys, x1 - 8, ys + 14), "#a8723f", "", w=3.4, seed=3310 + r_)
        x = x0 + 24
        while x < x1 - 70:
            w = rs.uniform(26, 46)
            h = rs.uniform(110, 160)
            col = BOOKCOL[rs.randint(0, len(BOOKCOL))]
            o += book(x, ys, w, h, col, rot=rs.uniform(-1, 1) if rs.rand() < .15 else 0, seed=3400 + int(x))
            x += w + 2
    return o


def window_night(mode, t):
    return f'<g transform="translate(760 -310) scale(1.0)">{Wd.window(mode if mode == "night" else "morning", t)}</g>'


def clock_face(h, m, sec, mode, x=815, y=690, k=.95):
    o = Wd.clock_wall(h, m, mode, k=k, x=x, y=y)
    # секундная стрелка
    r = 92 * k
    a = math.radians(sec * 6 - 90)
    o += line([(x - 14 * math.cos(a), y - 14 * math.sin(a)), (x + r * .8 * math.cos(a), y + r * .8 * math.sin(a))], 3.4, "#c44f3a", taper=.2, wmin=.5, seed=3501)
    o += blob(ellipse_pts(x, y, 7, 7, 8), "#c44f3a")
    return o


def room_bg(t, mode="night"):
    w = "#6b6590" if mode == "night" else "#f0dcb4"
    wsh = "#5a5580" if mode == "night" else "#e2c996"
    o = [f'<rect x="-1400" y="-1400" width="4200" height="{FLOOR + 1400}" fill="{w}"/>',
         f'<rect x="-1400" y="{FLOOR - 230}" width="4200" height="230" fill="{wsh}"/>',
         line([(-1400, FLOOR - 230), (2800, FLOOR - 230)], 4, INK, taper=.05, wmin=.9, seed=3010),
         shape(rect_pts(-1400, -40, 2800, -10), mix(w, "#000000", .12), "", w=3.6, seed=3011),
         window_night(mode, t), bookcase(mode), Wd.floor("night" if mode == "night" else "morning")]
    return "".join(o)


def poster(t):
    o = shape(rect_pts(540, 430, 740, 640, 4), "#f1e7d0", "", w=4, seed=3600)
    for k in range(5):
        o += line([(560, 470 + 30 * k), (700 - 14 * (k % 2) * 3, 470 + 30 * k)], 4.4, "#8a8070", seed=3610 + k, op=.85)
    o += shape(ellipse_pts(640, 442, 9, 9, 8), "#c44f3a", "", w=2.5, seed=3620)
    return o


def chair():
    o = shape(rect_pts(392, 1090, 424, 1560, 4), "#8a5a30", "", w=4.4, seed=3700)
    o += shape(rect_pts(392, 1130, 440, 1290, 8), "#b9503e", blob(rect_pts(420, 1134, 440, 1286), "#8e3a2c"), w=4.4, seed=3701)
    o += shape(rect_pts(392, 1384, 600, 1412, 6), "#b9503e", blob(rect_pts(392, 1402, 600, 1412), "#8e3a2c"), w=4.4, seed=3702)
    o += shape(rect_pts(404, 1412, 426, FLOOR + 44, 3), "#8a5a30", "", w=4, seed=3703)
    o += shape(rect_pts(566, 1412, 588, FLOOR + 44, 3), "#8a5a30", "", w=4, seed=3704)
    return o


def desk_back(t, shake=0.0):
    """Стопки на столе (до рук): справа от листа."""
    o = ""
    st, top = stack(1050, DESK_Y - 8, 6, 5, wob=shake, wmax=150, t=t)
    o += st
    st2, top2 = stack(1150, DESK_Y - 56, 4, 11, wob=shake, wmax=130, t=t)
    o += st2
    return o


def desk(mode):
    top_pts = [(560, DESK_Y), (1250, DESK_Y), (1330, 1195), (640, 1195)]
    wood, wsh = "#b27a46", "#8e5b30"
    o = ""
    # ножки и тумба
    o += shape(rect_pts(582, DESK_Y + 40, 616, FLOOR + 36, 3), wsh, "", w=4.4, seed=3801)
    o += shape(rect_pts(980, DESK_Y + 40, 1240, FLOOR + 20, 4), wood,
               blob(rect_pts(980, DESK_Y + 40, 1000, FLOOR + 20), wsh, .9) + "".join(
                   shape(rect_pts(1000, DESK_Y + 56 + 90 * k, 1222, DESK_Y + 56 + 90 * k + 76, 4), mix(wood, "#ffffff", .12), "", w=3.6, seed=3810 + k) +
                   shape(rect_pts(1088, DESK_Y + 84 + 90 * k, 1134, DESK_Y + 94 + 90 * k, 4), "#4a3a2c", "", w=3, seed=3820 + k) for k in range(3)),
               w=4.6, seed=3802)
    o += quad(top_pts, mix(wood, "#ffffff", .08), blob([(560, DESK_Y), (1250, DESK_Y), (1260, DESK_Y - 14), (566, DESK_Y - 14)], mix(wood, "#ffffff", .25), .8) +
              line([(700, 1230), (1280, 1230)], 2.6, wsh, taper=.1, wmin=.8, seed=3830, op=.5), w=4.8, seed=3800)
    o += shape(rect_pts(560, DESK_Y, 1250, DESK_Y + 36, 3), wsh, "", w=4.8, seed=3803)
    return o


def desk_lamp(t, flick=0.0):
    bx, by = 1230, 1204
    sx, sy = 880 + 4 * flick, 1010
    o = shape(ellipse_pts(bx, by, 58, 16, 14), "#2f6f63", "", w=4, seed=3900)
    o += line([(bx, by - 6), (1160, 1050), (sx + 90, sy - 70)], 11, "#2a2a32", taper=.02, wmin=1, seed=3901)
    shade = lib.T([(-70, 0), (-46, -50), (50, -50), (74, 0)], sx, sy, 1, -18, 0, 0)
    o += shape(shade, "#2f6f63", blob(lib.T([(30, -50), (50, -50), (74, 0), (44, 0)], sx, sy, 1, -18, 0, 0), "#225449", .9), w=4.4, seed=3902)
    o += shape(lib.T(ellipse_pts(0, 6, 56, 10, 12), sx, sy, 1, -18, 0, 0), "#fff4c8", "", w=3, seed=3903)
    return o, (sx, sy)


def light_cone(sx, sy, k=1.0):
    pts = [(sx - 60, sy + 6), (sx + 56, sy + 4), (1160, 1282), (610, 1286)]
    g = lib.lin_grad([(0, "#ffe7a0", .55 * k), (1, "#ffe7a0", .1 * k)], 0, 0, 0, 1)
    return f'<path d="{ellipse_to(pts)}" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def ellipse_to(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def mug_cold(x, y, k=1.0, steam=0.0, t=0.0, col="#d94f3a"):
    o = Wd.mug(x, y, k, col=col, hs=-1)
    if steam > 0:
        for j in range(3):
            ph = (t * .7 + j * .33) % 1
            xx = x - 16 + j * 16 + 8 * math.sin(ph * 6 + j)
            o += line([(xx, y - 130 * k - 40 * ph), (xx + 7 * math.sin(ph * 9), y - 150 * k - 60 * ph), (xx - 5, y - 175 * k - 70 * ph)], 5, "#ffffff",
                      taper=.9, wmin=.1, seed=3950 + j, op=.7 * steam * (1 - ph))
    return o


def paper_lines(n, upto, wob=0.0, seed=0, col="#3b4a80"):
    """Строчки рукописного текста на листе (в системе листа 0..1 по ширине, 0..1 по глубине)."""
    o = ""
    for i in range(n):
        v = .12 + .8 * i / max(1, n - 1) * .9
        full = clamp(upto - i)
        if full <= 0:
            continue
        a = _pp(.08, v)
        b = _pp(.08 + .84 * full * (.72 + .28 * ((i * 37 + seed) % 10) / 10), v)
        mid = [(a[0] + (b[0] - a[0]) * s / 5, a[1] + (b[1] - a[1]) * s / 5 + 2.6 * math.sin(s * 2.4 + i)) for s in range(6)]
        o += line(mid, 3.6, col, taper=.3, wmin=.5, seed=4000 + i + seed, op=.92)
    return o


def _pp(u, v):
    """Точка листа: u вдоль ширины (0..1), v вглубь (0 — ближний край, 1 — дальний)."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = PAPER
    xb = x0 + (x1 - x0) * u
    xt = x3 + (x2 - x3) * u
    yb = y0 + (y1 - y0) * u
    yt = y3 + (y2 - y3) * u
    return xb + (xt - xb) * v, yb + (yt - yb) * v


def paper_sheet(inner="", fill="#fbf6ea", seed=4100):
    return quad(PAPER, fill, inner, w=4.2, seed=seed)


# ═════════════════════════ сборка кадра ═════════════════════════
def compose(world_svg, cam, mode="night", front="", glow=None, vig=True):
    cx, cy, s, r = cam
    set_ink(s)
    o = ['<rect width="1080" height="1920" fill="#d8c7a0"/>',
         f'<g transform="{lib.cam(cx, cy, s, r)}">{world_svg}{glow or ""}{front}</g>']
    if vig:
        col = "#1a1030" if mode == "night" else "#2a1408"
        g = lib.rad_grad([(0, col, 0), (.6, col, 0), (1, col, .42 if mode == "night" else .25)], 540, 900, 1180, 1400)
        o.append(f'<rect width="1080" height="1920" fill="url(#{g})"/>')
    return lib.svg("".join(o))


def night_glow(lampxy, flick=0.0):
    g = lib.rad_grad([(0, "#ffd890", .42 + .05 * flick), (.5, "#ffbe6a", .15), (1, "#ffbe6a", 0)], lampxy[0] - 40, lampxy[1] + 160, 720, 640)
    g2 = lib.rad_grad([(0, "#000000", 0), (.5, "#000000", 0), (1, "#120a30", .55)], lampxy[0] - 80, lampxy[1] + 120, 1500, 1400)
    return (f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g})" style="mix-blend-mode:screen"/>'
            f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g2})"/>')


def day_glow():
    x0 = 900 - 560
    pts = [(x0 + 60, 300), (x0 + 240, 300), (x0 + 1000, FLOOR + 200), (x0 + 700, FLOOR + 200)]
    g = lib.rad_grad([(0, "#fff0c8", .35), (1, "#fff0c8", 0)], 500, 500, 1300, 1100)
    return (blob(pts, "#fff2c0", .2, 'style="mix-blend-mode:screen"') +
            f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g})" style="mix-blend-mode:screen"/>')


def pen(tip, ang=-48, k=1.0):
    """Ручка (кончик — в tip, корпус уходит вверх-вправо)."""
    a = math.radians(ang)
    ex, ey = tip[0] + 130 * k * math.cos(a), tip[1] + 130 * k * math.sin(a)
    o = line([tip, (ex, ey)], 12 * k, INK, taper=.05, wmin=1, seed=4200)
    o += line([(tip[0] + 10 * math.cos(a), tip[1] + 10 * math.sin(a)), (ex, ey)], 7 * k, "#d94f3a", taper=.05, wmin=1, seed=4201)
    return o


def cat_sleep(t, x=880, k=.42, z=True):
    st = dict(blink=1.0, look=(0, .3), tilt=16 + 1.5 * osc(t, .4), tail=3 * osc(t, .5), ear=-4 * bump(t % 1.7, .3, .3), smile=0)
    o = Cat.draw(x, FLOOR + 24, k, st, t)
    if z:
        for j in range(3):
            ph = (t * .45 + j / 3) % 1
            zx = x + 60 + 50 * ph + 10 * math.sin(ph * 7)
            zy = FLOOR - 100 - 150 * ph
            sz = 34 + 40 * ph
            o += text(zx, zy, "Z", sz, "#f3ecff", rot=-10 + 20 * ph, extra=f'stroke="{INK}" stroke-width="{3 + ph * 2:.1f}" paint-order="stroke" opacity="{(1 - ph) * min(1, ph * 6):.2f}"')
    return o


# ═════════════════════════ s01 ═════════════════════════
def write_tip(t, row_v=.42, rate=1.1):
    """Кончик ручки — быстрый «строчащий» зигзаг вдоль строки."""
    prog = (t * rate) % 1.0
    u = .12 + .6 * prog + .02 * osc(t, 9)
    v = row_v + .03 * osc(t, 7)
    return _pp(u, v), prog


def writing_arm(tip, ang_dir=(.62, .78)):
    d = np.array(ang_dir, float)
    d /= np.linalg.norm(d)
    return tuple(np.array(tip) - d * 62), tuple(d)


def s01(t):
    z, r = hook_zoom(t, 0.0, .45, .22, -4.0)
    k = ease_io(clamp(t / 1.7))
    hit = bump(t, T_UCHIL, .3) + bump(t, T_NOCH, .3)
    cam = (730 + 20 * k, 1090 - 10 * k, 1.6 * z * (1 + .06 * k + .05 * hit), r + .5 * osc(t, .5))
    tip, prog = write_tip(t, rate=1.3)
    wr, d = writing_arm(tip)
    arms = {"n": ("ik", wr, -1), "f": ("ik", (700, 1276), -1)}
    hands = {"n": dict(kind="open", flip=-1, dir=d, curl=(.55, .75, .85, .9), spread=.04, thumb=.35, bend=.05),
             "f": dict(kind="open", flip=-1, dir=(.95, .25), curl=(.15, .2, .25, .3), spread=.1, thumb=.3)}
    nod = .05 + .04 * osc(t, .9) + .03 * bump(t, T_NOCH, .4)
    ex = dict(lid=.28 + .05 * osc(t, 1.7), look=(.55, .85), brows="tired", mouth="flat", closed=blink_at(t, 0.9, .22) + blink_at(t, 1.5, .2) * .8, red=1.0)
    dm = dima(t, arms=arms, hands=hands, expr=ex, head_ang=nod, lean=.1 + .02 * osc(t, 1.2))
    lamp_svg, lxy = desk_lamp(t, flick=osc(t, 17) * .6)
    flick = osc(t, 13) * .6
    cone = light_cone(*lxy, k=1.0 + .08 * flick)
    lines_ = paper_lines(6, 4.5 + 1.0 * prog + .5 * t, seed=1) if False else paper_lines(6, 3.2 + prog, seed=1)
    sheet = paper_sheet(lines_)
    mug = mug_cold(780 - 200 + 0, 1262, .55, steam=0, col="#d94f3a")
    cans = ""
    sx = clock_face(3, 10, (t * 6) % 60 * 1.0, "night")
    sh = .6 * bump(t, T_NOCH, .4) * 6
    bg = room_bg(t) + sx
    layers = (chair() + dm["legs"] + cat_sleep(t) + desk("night") + desk_back(t, shake=sh) + sheet + mug + cone + lamp_svg + dm["arm_f"] + dm["body"] + dm["arm_n"] +
              pen(tip, -50))
    cat = cat_sleep(t)
    w = bg + layers
    return compose(w, cam, "night", glow=night_glow(lxy, flick))


# ═════════════════════════ s02 ═════════════════════════
def stamp_obj(x, y, rot=0.0):
    """Штамп: деревянная ручка, диск-основа. (x, y) — низ основы."""
    o = shape(rect_pts(x - 58, y - 30, x + 58, y, 8), "#2b2b34", "", w=4, seed=4300)
    o += shape([(x - 34, y - 30, 1), (x + 34, y - 30, 1), (x + 28, y - 120), (x - 28, y - 120)], "#a8723f",
               blob([(x + 10, y - 30), (x + 34, y - 30), (x + 28, y - 120), (x + 10, y - 120)], "#7c5028", .9), w=4.2, seed=4301)
    o += shape(ellipse_pts(x, y - 140, 40, 34, 12), "#c98f5a", blob(ellipse_pts(x + 12, y - 134, 20, 16, 8), "#a8723f", .8), w=4.2, seed=4302)
    return o


def stamp_five(cx, cy, sc, rot, a=1.0):
    col = "#d02a2a"
    o = f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.2f}) scale({sc:.4f})" opacity="{a:.2f}">'
    ring = ellipse_pts(0, 0, 84, 62, 22, jitter=.015, seed=5)
    o += f'<path d="{lib.fill_d(ring)}" fill="none" stroke="{col}" stroke-width="9"/>'
    ring2 = ellipse_pts(0, 0, 70, 50, 20, jitter=.015, seed=9)
    o += f'<path d="{lib.fill_d(ring2)}" fill="none" stroke="{col}" stroke-width="3"/>'
    o += text(0, 30, "5", 96, col)
    o += "</g>"
    return o


def s02(t):
    u = clamp((t - 1.3) / 2.1)
    if t < T_SDAL:
        st_y = 1245 - 700 * (1 - ease_in(clamp((t - 2.0) / (T_SDAL - 2.0)), 2.2))
    else:
        st_y = 1245 - 900 * ease_in(clamp((t - T_SDAL - .12) / .45), 2)
    hit = bump(t, T_SDAL, .35)
    cam = (650 + 40 * u + 10 * hit * osc(t, 17), 1060 + 20 * u + 8 * hit * osc(t, 21), 1.7 + .35 * ease_io(u) + .1 * hit, .7 - 1.2 * u + 1.2 * hit * osc(t, 11))
    after = clamp((t - T_SDAL) / .55)
    # пишет ответы до штампа, потом отпускает ручку и вскидывает кулак
    pw = 1 - smooth(T_SDAL - .12, T_SDAL + .1, t)
    tip, prog = write_tip(t, row_v=.5, rate=2.2)
    wr, d = writing_arm(tip)
    fist = ease_out(clamp((t - T_SDAL - .05) / .22)) * (1 - 0 * after)
    up = (600 + 50 * fist, 1130 - 230 * fist)
    wr2 = (wr[0] * (1 - fist) + up[0] * fist, wr[1] * (1 - fist) + up[1] * fist)
    pump = 1.0 + 0.25 * after * math.sin(10 * (t - T_SDAL))
    arms = {"n": ("ik", wr2, -1), "f": ("ik", (700, 1276), -1)}
    hands = {"n": dict(kind="open", flip=-1, dir=(d[0] * (1 - fist) + .1 * fist, d[1] * (1 - fist) - 1.0 * fist),
                       curl=(.55 + .45 * fist, .75 + .25 * fist, .85 + .15 * fist, .9 + .1 * fist), spread=.04 * (1 - fist), thumb=.35 + .6 * fist, bend=.05),
             "f": dict(kind="open", flip=-1, dir=(.95, .25), curl=(.15, .2, .25, .3), spread=.1, thumb=.3)}
    ex = dict(lid=.5 + .45 * after, look=(.55, .85 - 1.2 * after), brows="up" if after > .3 else "calm",
              mouth="grin" if after > .3 else "flat", closed=blink_at(t, 1.8, .18) * (1 - after), red=1.0 - .8 * after,
              laugh=0.0)
    if after > .6:
        ex["mouth"] = "laugh"
        ex["open"] = .7
    dm = dima(t, arms=arms, hands=hands, expr=ex, head_ang=.06 - .14 * after + .02 * osc(t, 1.1), lean=.1 - .1 * after)
    lamp_svg, lxy = desk_lamp(t)
    cone = light_cone(*lxy, k=.9)
    inner = paper_lines(7, 6.0 * clamp((t - 1.0) / 1.5) + 1, seed=3)
    # шапка листа
    hdr = line([_pp(.08, .93), _pp(.5, .93)], 7, "#2b2b34", seed=4400, taper=.2, wmin=.6)
    hdr += line([_pp(.58, .93), _pp(.9, .93)], 4, "#8a8070", seed=4401, op=.8)
    paper_bump = -6 * bump(t, T_SDAL, .22)
    sheet = f'<g transform="translate(0 {paper_bump:.2f})">{paper_sheet(inner + hdr)}'
    # оттиск
    if t >= T_SDAL:
        e = t - T_SDAL
        sc = 1.0 + .7 * math.exp(-e * 24) + 0.04 * math.sin(e * 20) * math.exp(-e * 8)
        sheet += stamp_five(*_pp(.5, .55), .78 * sc, -12, a=min(1.0, e * 14))
    sheet += "</g>"
    bg = room_bg(t) + clock_face(3, 52, (t * 6) % 60, "night")
    st_x, st_y2 = _pp(.5, .55)[0], st_y
    stamp = stamp_obj(st_x, st_y2) if t > 2.0 and st_y2 > 250 else ""
    layers = (chair() + dm["legs"] + cat_sleep(t) + desk("night") + desk_back(t) + sheet + cone + lamp_svg + dm["arm_f"] + dm["body"] + dm["arm_n"] +
              (pen(tip, -50) if pw > .5 else "") + stamp)
    # ударная вспышка и штрихи
    fx = ""
    if T_SDAL <= t < T_SDAL + .5:
        e = (t - T_SDAL) / .5
        cx, cy = _pp(.5, .55)
        for j in range(12):
            a = j * math.pi / 6 + .2
            r0, r1 = 90 + 150 * ease_out(e), 130 + 210 * ease_out(e)
            fx += line([(cx + r0 * math.cos(a), cy + r0 * .72 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * .72 * math.sin(a))], 7, "#f2c23a",
                       seed=4500 + j, op=(1 - e) ** .8)
    return compose(bg + layers + fx, cam, "night", glow=night_glow(lxy))


# ═════════════════════════ s06: экзамен ═════════════════════════
def classroom(t):
    wall, wsh = "#dfe3c6", "#c8cfa8"
    o = f'<rect x="-1400" y="-1400" width="4200" height="{FLOOR + 1400}" fill="{wall}"/>'
    o += f'<rect x="-1400" y="{FLOOR - 250}" width="4200" height="250" fill="{wsh}"/>'
    o += line([(-1400, FLOOR - 250), (2800, FLOOR - 250)], 4, INK, taper=.05, wmin=.9, seed=5010)
    # доска
    o += shape(rect_pts(120, 520, 760, 940, 8), "#3f6a58", blob(rect_pts(120, 880, 760, 940), "#a8723f") + blob(rect_pts(140, 540, 740, 900), "#4b7a66", .6), w=5, seed=5011)
    for k, y in enumerate((620, 700, 780)):
        o += line([(180, y), (180 + 380 - 70 * k, y + 6 * osc(0, 1, k))], 5, "#f4f1e4", seed=5020 + k, op=.7)
    # окно дневное
    o += f'<g transform="translate(1250 -80)">{Wd.window("morning", t)}</g>'
    # часы
    o += clock_face(10, 50, (t * 6) % 60, "morning", x=1000, y=380, k=1.1)
    # ряды парт и спины других (бледные)
    for i, (px, col, hcol) in enumerate([(240, "#7f9ac2", "#4a3220"), (640, "#c47a6a", "#2a2a2a"), (980, "#8fb58a", "#a8723f")]):
        by = 1330
        sway = 4 * osc(t, .35 + .1 * i, i)
        o += shape(rect_pts(px - 60 + sway, by - 110, px + 60 + sway, by + 70, 28), col, "", w=4, seed=5100 + i)
        o += shape(ellipse_pts(px + sway * 1.2, by - 160, 46, 52, 14), hcol, "", w=4, seed=5110 + i)
        o += shape(rect_pts(px - 130, by + 40, px + 130, by + 66, 4), "#a8723f", "", w=4, seed=5120 + i)
    o += Wd.floor("morning")
    return o


def exam_desk():
    o = shape(rect_pts(560, 1196, 1250, 1230, 4), "#c98f5a", blob(rect_pts(560, 1220, 1250, 1230), "#a8723f"), w=4.8, seed=5200)
    o += shape(rect_pts(590, 1230, 612, FLOOR + 34, 3), "#6a6f7a", "", w=4.4, seed=5201)
    o += shape(rect_pts(1180, 1230, 1202, FLOOR + 34, 3), "#6a6f7a", "", w=4.4, seed=5202)
    return o


def thought_bubble(cx, cy, u, t):
    if u <= 0:
        return ""
    s = ease_out(u, 3) * (1 + .12 * math.sin(u * 9) * (1 - u)) if u < 1 else 1.0
    s = max(.01, ease_out(clamp(u * 1.4), 3) + .08 * math.sin(clamp(u * 1.4) * 6) * (1 - clamp(u * 1.4))) * (1 + .02 * osc(t, 1.4))
    o = f'<g transform="translate({cx:.1f} {cy:.1f}) scale({s:.4f})">'
    cloud = ellipse_pts(0, 0, 170, 105, 22)
    o += shape(cloud, "#fbf6ea", blob(ellipse_pts(30, 36, 170, 90, 18), "#e9e1cf", .7), w=5, seed=5300)
    for j, (dx, dy, r) in enumerate([(-130, 160, 34), (-170, 226, 22), (-196, 270, 13)]):
        o += shape(ellipse_pts(dx, dy, r, r, 10), "#fbf6ea", "", w=4, seed=5310 + j)
    o += text(0, 56, "?", 190, "#9aa0a8", extra=f'stroke="{INK}" stroke-width="5" paint-order="stroke"')
    o += "</g>"
    return o


def s06(t):
    a = clamp((t - T_NICHEGO) / .35)
    hip = np.array([470.0, 1372.0])
    look_up = ease_io(clamp((t - 7.95) / .45))
    tap = osc(t, 3.2)
    arms = {"n": ("ik", (700 + 4 * tap, 1198), -1), "f": ("ik", (740, 1196), -1)}
    hands = {"n": dict(kind="open", flip=-1, dir=(.9, .4), curl=(.55, .75, .85, .9), spread=.04, thumb=.35, bend=.05),
             "f": dict(kind="open", flip=-1, dir=(.9, .3), curl=(.3, .35, .4, .45), spread=.1, thumb=.4)}
    ex = dict(lid=.7 + .25 * a, look=(.45 + .3 * osc(t, .8), -.8 * look_up + .2 * (1 - look_up)), brows="worry" if look_up > .3 else "calm",
              mouth="talk" if a > .2 else "flat", open=.5 * a, smile=-.5, closed=blink_at(t, 8.9, .18))
    dm = dima(t, hip=hip, arms=arms, hands=hands, expr=ex, head_ang=-.28 * look_up + .02 * osc(t, 1.3), lean=.04 - .04 * look_up,
              feet={"n": ((hip[0] + 255 + 6 * tap, FLOOR + 22), 0.0), "f": ((hip[0] + 205, FLOOR + 12), 0.0)})
    sheet = paper_sheet(line([_pp(.1, .9), _pp(.46, .9)], 6, "#2b2b34", seed=5400, taper=.2, wmin=.6) +
                        line([_pp(.54, .9), _pp(.7, .9)], 4, "#8a8070", seed=5401, op=.8), seed=5402)
    sw = sweat(520, 880, 1.0, clamp((t - 8.0) / .8)) if False else ""
    hx, hy = dm["head"]
    sw = sweat(hx + 120, hy - 70, 1.3, clamp((t - 7.95) / .9)) + sweat(hx - 60, hy - 90, 1.0, clamp((t - 8.7) / .9))
    bub = thought_bubble(hx + 130, hy - 290 - 10 * a, clamp((t - T_NICHEGO) / .5), t)
    chair_ = chair()
    layers = chair_ + dm["legs"] + exam_desk() + sheet + dm["arm_f"] + dm["body"] + dm["arm_n"] + pen((700 + 4 * tap, 1198), -40) + sw + bub
    u = clamp((t - 7.7) / 1.9)
    hit = bump(t, T_NICHEGO, .3)
    cam = (hx + 190 + 12 * hit * osc(t, 15), hy + 40 + 8 * hit * osc(t, 19), 1.45 + .3 * ease_io(u) + .12 * hit, -1.0 + 1.5 * u)
    g = lib.rad_grad([(0, "#fff0c8", .3), (1, "#fff0c8", 0)], 1000, 500, 1300, 1100)
    glow = f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    return compose(classroom(t) + layers, cam, "day", glow=glow)


# ═════════════════════════ s14: день, спокойно ═════════════════════════
def checkbox(u, v, done, seed):
    c = _pp(u, v)
    sz = 30
    o = shape(rect_pts(c[0] - sz / 2, c[1] - sz * .35, c[0] + sz / 2, c[1] + sz * .35, 3), "#fffdf5", "", w=3.4, seed=seed)
    if done > 0:
        p0, p1, p2 = (c[0] - 12, c[1] - 2), (c[0] - 3, c[1] + 8), (c[0] + 18, c[1] - 20)
        pts = [p0, p1, p2]
        if done < .5:
            f = done / .5
            pts = [p0, (p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f)]
        else:
            f = (done - .5) / .5
            pts = [p0, p1, (p1[0] + (p2[0] - p1[0]) * f, p1[1] + (p2[1] - p1[1]) * f)]
        o += line(pts, 9, "#2f9a55", taper=.1, wmin=.8, seed=seed + 1)
    return o


def s14(t):
    wh = whip(t, 24.8, .24)
    u = clamp((t - 24.8) / 2.8)
    # 24.8–25.95: пьёт чай; 26.0–26.6: ставит и ставит галочку на «повторяет»
    sip = ease_io(clamp((t - 25.0) / .35)) * (1 - ease_io(clamp((t - 25.65) / .3)))
    place = ease_io(clamp((t - 25.8) / .25))
    tick = ease_out(clamp((t - T_POVTOR) / .35))
    mug_rest = (840, 1262)
    mouth_pt = (610, 1062)
    mx = mug_rest[0] + (mouth_pt[0] - mug_rest[0] + 0) * sip
    my = mug_rest[1] + (mouth_pt[1] + 128 * .6 - mug_rest[1]) * sip
    mk = .62
    # рука с чашкой (до 25.95), потом рука с ручкой на галочке
    pen_tip = _pp(.07 + .0, .55)
    cb = _pp(.1, .78)
    q0, q1, q2 = (cb[0] - 12, cb[1] - 2), (cb[0] - 3, cb[1] + 8), (cb[0] + 18, cb[1] - 20)
    if tick < .5:
        f_ = tick / .5
        tp = (q0[0] + (q1[0] - q0[0]) * f_, q0[1] + (q1[1] - q0[1]) * f_)
    else:
        f_ = (tick - .5) / .5
        tp = (q1[0] + (q2[0] - q1[0]) * f_, q1[1] + (q2[1] - q1[1]) * f_)
    if t < T_POVTOR:
        tp = (q0[0] - 40 * (1 - clamp((t - 25.9) / .25)), q0[1] - 30 * (1 - clamp((t - 25.9) / .25)))
    carry = 1.0 - place
    wr_cup = (mx + 50 * mk + 62 * BS, my - 64 * mk + 4)
    wr_pen, d_pen = writing_arm(tp)
    wr = (wr_cup[0] * carry + wr_pen[0] * (1 - carry), wr_cup[1] * carry + wr_pen[1] * (1 - carry))
    arms = {"n": ("ik", wr, -1), "f": ("ik", (860, 1260), -1)}
    hands = {"n": dict(kind="none") if carry > .5 else dict(kind="open", flip=-1, dir=d_pen, curl=(.55, .75, .85, .9), spread=.04, thumb=.35, bend=.05),
             "f": dict(kind="open", flip=-1, dir=(.9, .4), curl=(.2, .25, .3, .35), spread=.12, thumb=.3)}
    ex = dict(lid=.85, look=(.7, .55 - .5 * sip), brows="calm", mouth="smile", smile=.9, closed=blink_at(t, 26.9, .2), blush=.4 * tick)
    dm = dima(t, arms=arms, hands=hands, expr=ex, head_ang=.04 + .05 * sip + .02 * osc(t, .5), lean=.06 - .08 * sip + .03 * tick)
    lamp_svg, lxy = desk_lamp(t)
    boxes = ""
    todo = ""
    for i, ts in enumerate(("1", "3", "7")):
        done = tick if i == 0 else 0
        boxes += checkbox(.1, .78 - .2 * i, done, 5500 + 5 * i)
        a, b = _pp(.2, .78 - .2 * i), _pp(.7, .78 - .2 * i)
        todo += line([a, (a[0] + (b[0] - a[0]) * .5, a[1] + 3), b], 4, "#3b4a80", taper=.2, wmin=.5, seed=5510 + i, op=.9)
    sheet = paper_sheet(boxes + todo + line([_pp(.1, .96), _pp(.55, .96)], 6, "#2b2b34", seed=5520, taper=.2, wmin=.6), seed=5521)
    mug = ""
    if carry > .5:
        gb, gf = grip(mx, my, mk)
        mug = gb + mug_cold(mx, my, mk, steam=1.0, t=t, col="#d94f3a") + gf
    else:
        mug = mug_cold(mx, my, mk, steam=1.0, t=t, col="#d94f3a")
    bg = room_bg(t, "day") + clock_face(2, 15, (t * 6) % 60, "morning")
    # рядом на столе: аккуратная стопка
    st, _ = stack(1100, DESK_Y - 8, 3, 7, wmax=150)
    layers = (chair() + dm["legs"] + desk("day") + st + sheet + (mug if carry <= .5 else "") + dm["arm_f"] + dm["body"] + (mug if carry > .5 else "") +
              dm["arm_n"] + (pen(tp, -50) if carry <= .5 else ""))
    plant = ""
    k = ease_io(u)
    cam = (720 + 20 * k + 260 * wh, 1110 - 10 * k, 1.55 + .25 * k, -.5 + .5 * k + 2.0 * wh)
    cat = cat_sleep(t, z=False) if False else ""
    sparks = ""
    if t > T_POVTOR:
        e = t - T_POVTOR
        cx, cy = _pp(.1, .78)
        for j in range(6):
            a = j * math.pi / 3 + .3
            r0, r1 = 30 + 40 * ease_out(e * 2), 55 + 60 * ease_out(e * 2)
            sparks += line([(cx + r0 * math.cos(a), cy + r0 * .7 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * .7 * math.sin(a))], 5, "#f2c23a",
                           seed=5600 + j, op=clamp(1 - e * 2.2))
    return compose(bg + layers + sparks, cam, "day", glow=day_glow())


def grip(mx, my, mk, side=1):
    import hand as Hand
    kw = kw_hand()
    sc = BS
    old = people.LWK
    people.LWK = sc
    try:
        b, f = Hand.grip((mx, my - 64 * mk), 50 * mk, side, k=sc * 1.05, h=70, seed=2600, **kw)
    finally:
        people.LWK = old
    return b, f


SHOTS = {"s01": s01, "s02": s02, "s06": s06, "s14": s14}


def frame(sid, t):
    lib.DEFS.clear()
    return SHOTS[sid](t)
