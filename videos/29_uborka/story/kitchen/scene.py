"""Кухня рилса 29 «протру одну кружку»: планы s01 s02 s05 s06 s07 s08 s10 s11 s12 s13 s16 s17.
frame(sid, t) -> SVG 1080×1920 (t — общее время ролика). Мир — world.py, Дима — people.py (рилс 27), кот — cat.py.
Удары — на словах по voice/words.json. Камера у каждого плана своя, движется с первого кадра."""
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
import world as Wd  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wi(i):
    return WORDS[i]["start"]


T_KRUZHKU, T_PYL, T_SHKAF, T_POPALO = wi(4), wi(19), wi(27), wi(32)
T_HOLOD, T_TRI, T_KOT, T_PROSN = wi(42), wi(44), wi(53), wi(60)
T_ZVENIT = wi(77)

BS = 0.62
HIP = np.array([400.0, 1262.0])


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
    """Влёт камеры (правило 28/29): масштаб 1/(1+mx) → 1 за dur с перелётом 5 %, поворот rot → 0."""
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


def whip_in(t, t0, dur=0.2):
    """Хлёст на входе плана: сдвиг по x из-за кадра (мир px) — 0 после dur."""
    u = clamp((t - t0) / dur)
    return (1 - ease_out(u, 3))


# ═════════════════════════ Дима ═════════════════════════
def dima(t, hip=None, lean=0.08, arms=None, hands=None, expr=None, head_ang=0.0, feet=None, hood=0.0):
    hip = HIP if hip is None else np.array(hip, float)
    if feet is None:
        feet = {"n": ((hip[0] + 16, hip[1] + 376), 0.0), "f": ((hip[0] - 4, hip[1] + 372), 0.0)}
    p = dict(hip=tuple(hip), scale=BS, lean=lean, feet=feet, arms=arms, hands=hands or {}, expr=expr or {}, head_ang=head_ang,
             hood=hood, strings=(3 * osc(t, 1.3), 2 * osc(t, 1.1, 1)))
    return people.draw(p, "dima")


def kw_hand():
    people.C = people.PAL["dima"]
    return dict(shape_fn=people.shape, line_fn=people.line, skin=people.C["SKIN"], skin_sh=people.C["SKIN_SH"], skin_sh2=people.C["SKIN_SH2"])


def grip_mug(mx, my, mk, side=-1, k=None):
    """Пальцы ближней руки на кружке (mx, my — низ кружки). Возвращает (за кружкой, поверх)."""
    kw = kw_hand()
    sc = BS * (k or 1.0)
    old = people.LWK
    people.LWK = sc
    try:
        b, f = Hand.grip((mx, my - 64 * mk), 50 * mk, side, k=sc * 1.05, h=70, seed=2600, **kw)
    finally:
        people.LWK = old
    return b, f


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


def sweat(x, y, k, u):
    """Капля пота: u 0..1 — растёт и сползает."""
    if u <= 0:
        return ""
    yy = y + 40 * k * ease_in(u)
    r = 16 * k * min(1, u * 3)
    drop = [(x, yy - r * 2.2), (x + r, yy - r * .1), (x + r * .8, yy + r * .7), (x, yy + r), (x - r * .8, yy + r * .7), (x - r, yy - r * .1)]
    return shape(drop, "#bfe6fa", blob([(x - r * .4, yy - r * .6), (x - r * .1, yy - r * .9), (x - r * .1, yy - r * .2)], "#ffffff"), w=3, seed=3001)


def talk(t, t0, t1, rate=7.0):
    if t < t0 or t > t1:
        return 0.0
    v = .5 + .5 * math.sin(2 * math.pi * rate * (t - t0)) * (.7 + .3 * math.sin(t * 3.1))
    return clamp(v * smooth(t0, t0 + .08, t) * (1 - smooth(t1 - .08, t1, t)))


# ═════════════════════════ сборка кадра ═════════════════════════
def room(t, mode="night", cup_open=0.0, cup_empty=False, dust=1.0, wiped=0.0, wipe_x=(0, 0), fridge_open=0.0, foam=False, clock=(23, 50),
         lamp_sw=0.0, magnets=True):
    o = [Wd.wall(mode), Wd.window(mode, t), Wd.clock_wall(clock[0], clock[1], mode), Wd.counter(), Wd.floor(mode),
         Wd.shelf(dust, wiped, wipe_x), Wd.cupboard(cup_open, empty=cup_empty), Wd.fridge(fridge_open, foam=foam, magnets=magnets),
         Wd.switch(mode != "dark"), Wd.lamp(mode, t, lamp_sw)]
    return "".join(o)


def compose(world_svg, cam, light="night", front="", screen=""):
    cx, cy, s, r = cam
    set_ink(s)
    o = [f'<rect width="1080" height="1920" fill="#e7cfa3"/>',
         f'<g transform="{lib.cam(cx, cy, s, r)}">{world_svg}{Wd.lamp_glow(light)}{front}</g>', screen, vignette(light)]
    return lib.svg("".join(o))


def vignette(light):
    col = "#2a1408" if light != "dark" else "#0a0c20"
    g = lib.rad_grad([(0, col, 0), (.62, col, 0), (1, col, .4)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def stand(t, arms, hands, expr, lean=0.08, hip=None, head_ang=0.0):
    d = dima(t, hip=hip, lean=lean, arms=arms, hands=hands, expr=expr, head_ang=head_ang)
    return d


def layers(d, mid="", front=""):
    return d.get("legs", "") + d["arm_f"] + d["body"] + mid + d["arm_n"] + front


# ═════════════════════════ s01 / s02: кружка ═════════════════════════
MUG = (640.0, 1110.0, 0.9)


def mug_scene(t, cam, shine=0.0, expr=None, spark=0.0, rag_off=0.0):
    mx, my, mk = MUG
    my = my - 6 * osc(t, .9)
    rub = osc(t, 2.6) * (1 - rag_off)
    rub2 = osc(t, 2.6, 1.57) * (1 - rag_off)
    # ближняя рука держит кружку, дальняя с тряпкой трёт её по кругу (rag_off — тряпка отведена вниз-влево)
    wr_n = (mx + 50 * mk + 62 * BS, my - 64 * mk + 4)
    rag_c = (mx + 18 * rub - 150 * rag_off, my - 70 * mk + 30 * rub2 + 110 * rag_off)
    arms = {"n": ("ik", wr_n, -1), "f": ("ik", (rag_c[0] - 30, rag_c[1] + 20), -1)}
    hands = {"n": dict(kind="none"), "f": dict(kind="none")}
    d = dima(t, arms=arms, hands=hands, expr=expr, head_ang=.12 + .02 * osc(t, .7), lean=.1)
    gb, gf = grip_mug(mx, my, mk, side=1)
    w = room(t)
    mid = ""
    front = gb + Wd.mug(mx, my, mk, shine=shine, hs=-1) + gf + Wd.rag(rag_c[0], rag_c[1], .8, 20 * rub, t)
    if spark > 0:
        a = spark
        front += Wd.sparkle(mx - 30, my - 120 * mk, 46 * a, t * 2)
        front += Wd.sparkle(mx + 40, my - 60 * mk, 26 * a, -t * 3)
        for j in range(6):
            ang = j * math.pi / 3 + .3
            r0, r1 = 90 + 40 * (1 - a), 120 + 50 * (1 - a)
            front += line([(mx + r0 * math.cos(ang), my - 70 + r0 * math.sin(ang)), (mx + r1 * math.cos(ang), my - 70 + r1 * math.sin(ang))], 5, "#f2c23a",
                          seed=3100 + j, op=clamp(a * 1.4))
    return compose(w + layers(d, mid, front), cam)


def s01(t):
    z, r = hook_zoom(t, 0.0, .4, .22, -3.5)
    k = ease_io(clamp(t / 1.7))
    cam = (520 + 30 * k, 1010 - 20 * k, 1.75 * z * (1 + .05 * k), r + .4 * osc(t, .4))
    hit = bump(t, wi(2), .3)            # «протереть» — удар камерой
    cam = (cam[0], cam[1], cam[2] * (1 + .06 * hit), cam[3])
    ex = dict(lid=.55, look=(.6, .5), brows="calm", mouth="smile", smile=.6, closed=blink_at(t, 1.1))
    return mug_scene(t, cam, expr=ex)


def s02(t):
    u = clamp((t - 1.3) / 1.54)
    cam = (MUG[0] - 20 + 10 * u, MUG[1] - 150 - 10 * u, 3.0 + .5 * ease_io(u), .6 - 1.0 * u)
    sh = clamp((t - 1.5) / .5)
    spark = ease_out(clamp((t - 1.55) / .2)) * (1 - smooth(2.3, 2.84, t))
    ex = dict(lid=.75, look=(.7, .6), brows="up", mouth="grin", closed=0.0)
    return mug_scene(t, cam, shine=sh, expr=ex, spark=spark, rag_off=ease_io(clamp((t - 1.3) / .3)))


SHOTS = {"s01": s01, "s02": s02}


def frame(sid, t):
    lib.DEFS.clear()
    return SHOTS[sid](t)


# ═════════════════════════ лавина: предметы из шкафа ═════════════════════════
G = 5200.0
_rs = np.random.RandomState(29)
ITEMS = []
for _i, (_kind, _col) in enumerate([("pot", "#c44f3a"), ("lid", "#b9bec8"), ("bag", "#e9c46a"), ("pan", ""), ("pot", "#3f7a72"),
                                    ("lid", "#c9ced8"), ("bag", "#8ab6d6"), ("jar", "#e07a5f"), ("plate", ""), ("pot", "#e9c46a"),
                                    ("bag", "#9fc5a8"), ("plate", ""), ("jar", "#9fc5a8"), ("pan", "")]):
    x0 = 900 + _rs.uniform(-40, 140)
    y0 = 640 + _rs.uniform(-40, 180)
    land_y = Wd.FLOOR + 50 + _rs.uniform(0, 150)
    ITEMS.append(dict(kind=_kind, col=_col, x0=x0, y0=y0, vx=_rs.uniform(-1150, -150), vy=_rs.uniform(-700, -150), t0=T_SHKAF + _i * 0.045,
                      spin=_rs.uniform(-500, 500), land=land_y, k=_rs.uniform(.7, .95), rest=_rs.uniform(-25, 25)))
# что лежит на полу к трём часам ночи (из холодильника и ящиков — доносится к s11)
EXTRA = [("jar", "#e9c46a", 160, 1700, .8, -8), ("bottle", "#5f9a5a", 260, 1760, .8, 70), ("box", "", 980, 1800, 1.1, 0),
         ("bag", "#e07a5f", 60, 1780, .9, -15), ("pot", "#8ab6d6", -60, 1700, .8, 8), ("plate", "", 520, 1820, .9, 0),
         ("jar", "#8ab6d6", 1160, 1700, .7, 12), ("bottle", "#c44f3a", 1240, 1760, .75, -80), ("pan", "", 700, 1700, .85, 10),
         ("bag", "#9fc5a8", 1380, 1820, .9, 5), ("lid", "#b9bec8", 330, 1840, .9, -6)]


def item_state(it, t):
    """Положение предмета: полёт по параболе, удар о пол с одним отскоком, потом лежит (rest — угол)."""
    e = t - it["t0"]
    if e < 0:
        return None
    x0, y0, vx, vy = it["x0"], it["y0"], it["vx"], it["vy"]
    # время удара о пол
    a, b, c = .5 * G, vy, y0 - it["land"]
    te = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
    if e < te:
        return x0 + vx * e, y0 + vy * e + .5 * G * e * e, it["spin"] * e
    xl = x0 + vx * te
    vb = -(vy + G * te) * .3
    e2 = e - te
    tb = 2 * vb / G
    if e2 < tb:
        return xl + vx * .3 * e2, it["land"] - (vb * e2 - .5 * G * e2 * e2), it["spin"] * te + it["spin"] * .3 * e2
    ang0 = it["spin"] * (te + .3 * tb)
    u = clamp((e2 - tb) / .3)
    return xl + vx * .3 * tb, it["land"], ang0 * (1 - ease_out(u)) + it["rest"] * ease_out(u)


def draw_item(kind, col, x, y, k, rot):
    if kind == "pot":
        return Wd.pot_side(x, y, k, col, rot)
    if kind == "lid":
        return Wd.lid_side(x, y, k, rot, col)
    if kind == "bag":
        return Wd.bag(x, y, k, col, rot)
    if kind == "pan":
        return Wd.pan(x, y, k, rot)
    if kind == "jar":
        return Wd.jar(x, y, k, col, rot)
    if kind == "bottle":
        return Wd.bottle(x, y, k, col, rot)
    if kind == "plate":
        return Wd.plate(x, y, k, rot)
    if kind == "box":
        return Wd.box(x, y, k)
    return ""


def pile(t, extra=False, behind=None):
    """Предметы на полу. behind: None — все; True — только дальние (y < 1700); False — ближние."""
    out = []
    for it in ITEMS:
        st = item_state(it, t)
        if st is None:
            continue
        x, y, r = st
        out.append((y, draw_item(it["kind"], it["col"], x, y, it["k"], r)))
    if extra:
        for kind, col, x, y, k, r in EXTRA:
            if kind == "box":
                continue
            out.append((y, draw_item(kind, col, x, y, k, r)))
    out.sort(key=lambda q: q[0])
    if behind is True:
        out = [q for q in out if q[0] < 1700]
    elif behind is False:
        out = [q for q in out if q[0] >= 1700]
    return "".join(q[1] for q in out)


def lid_on_head(hx, hy, rot, k=.75):
    """Крышка на голове (ручкой вверх), центр — над макушкой."""
    return Wd.lid_side(hx, hy, k, rot)


# ═════════════════════════ s05: палец по пыльной полке ═════════════════════════
def s05(t):
    x0, x1, y = Wd.SHELF
    u = ease_io(clamp((t - 6.25) / (T_PYL - 6.25)))
    lift = smooth(T_PYL - .02, T_PYL + .16, t)
    tipx = 520 - 300 * u
    tipy = y - 4 - 30 * lift
    k = BS * 1.25
    d = np.array([-1.0, 0.18])
    d /= np.linalg.norm(d)
    n = np.array([-d[1], d[0]]) * -1
    Wr = np.array([tipx, tipy]) - d * 138 * k - n * (-25) * k
    kw = kw_hand()
    lib.INK_K[0] = 1.0 / 3.0 ** .62
    sl_end = Wr + np.array([420, 220])
    sleeve = people.limb_band(Wr - d * 10, sl_end, 112 * k, 130 * k, people.C["TOP"], False, 610)
    cuff = shape(lib.band([tuple(Wr - d * 34 * k), tuple(Wr + d * 4 * k)], 100 * k, 96 * k, step=3, cap=False), people.C["TOP_SH"], "", w=4, seed=611)
    hand_svg = Hand.hand(Wr, d, flip=-1, k=k, curl=(0, .95, .95, .9), spread=.05, thumb=.85, bend=.05, seed=620, **kw)
    w = room(t, wipe_x=(tipx, 520) if u > 0 else (0, 0))
    dust = ""
    if 0 < u:
        for j in range(5):
            ph = (t * 3 + j * .2) % 1
            dust += blob(ellipse_pts(tipx + 14 + 30 * ph, tipy - 10 - 26 * ph + 6 * j % 7, 8 * (1 - ph) + 3, 7 * (1 - ph) + 3, 8), "#a49c8e")
    if lift > 0:
        for j in range(6):
            a = j * math.pi / 3 - .2
            r = 24 + 60 * lift
            dust += blob(ellipse_pts(tipx + r * math.cos(a), tipy - 6 + r * .6 * math.sin(a), 10 * (1 - lift) + 2, 10 * (1 - lift) + 2, 8), "#a49c8e")
    front = sleeve + cuff + hand_svg + dust
    ww = whip_in(t, 6.04, .2)
    cam = (tipx + 60 + 120 * ww, y - 10, 3.1 + .25 * u, -1.5 + 1.5 * u)
    return compose(w + front, cam)


# ═════════════════════════ s06: Дима смотрит на палец в пыли ═════════════════════════
def s06(t):
    sh = smooth(T_PYL + .05, T_PYL + .3, t)
    hd = (458, 925)
    fin = (hd[0] + 150, hd[1] + 70 - 10 * sh)
    d_ = np.array([.25, -1.0])
    d_ /= np.linalg.norm(d_)
    nn = np.array([-d_[1], d_[0]]) * -1
    Wr = np.array(fin) - d_ * 138 * BS - nn * (-25) * BS
    arms = {"n": ("ik", tuple(Wr), -1), "f": ("ang", .15, .3)}
    hands = {"n": dict(kind="open", flip=-1, dir=tuple(d_), curl=(0, .95, .95, .9), spread=.05, thumb=.85, bend=.05)}
    ex = dict(lid=.55 + .45 * sh, look=(.75, .25 - .2 * sh), brows="up" if sh > .5 else "calm",
              mouth="talk" if sh > .3 else "smile", open=.75 * sh, smile=-.6 * sh)
    dm = dima(t, arms=arms, hands=hands, expr=ex, head_ang=.05 - .08 * sh, hood=4 * bump(t, T_PYL + .1, .3))
    dust = blob(ellipse_pts(fin[0] + 4, fin[1] - 6, 16, 12, 10), "#8f877a") + blob(ellipse_pts(fin[0] - 4, fin[1] - 10, 8, 6, 8), "#b3ab9c")
    sw = sweat(hd[0] - 70, hd[1] - 70, 1.0, clamp((t - 7.95) / .7))
    hit = ease_out(clamp((t - 7.64) / .15))
    s = 2.55 + .55 * hit + .08 * clamp((t - 7.8) / 1.1)
    shk = 6 * bump(t, 7.66, .3) * osc(t, 13)
    cam = (hd[0] + 40 + shk, hd[1] + 20, s, 1.2 * bump(t, 7.66, .3) * osc(t, 9))
    w = room(t, wipe_x=(220, 520))
    return compose(w + layers(dm, "", dust + sw), cam)


# ═════════════════════════ s07: трёт полку, касается шкафа — лавина ═════════════════════════
def s07(t):
    hip = (230.0, 1262.0)
    lv = smooth(T_SHKAF - .1, T_SHKAF + .15, t)
    rub = osc(t, 2.4)
    rag_p = np.array([480 + 45 * rub, 935 + 8 * osc(t, 4.8)])
    shock = smooth(T_SHKAF, T_SHKAF + .12, t)
    duck = smooth(T_SHKAF + .1, T_SHKAF + .3, t)
    hd0 = np.array([300.0, 860.0])
    if duck > 0:
        rag_p = rag_p * (1 - duck) + (hd0 + np.array([40, -40])) * duck
    arms = {"n": ("ik", (rag_p[0] - 20, rag_p[1] + 30), -1),
            "f": ("ang", .15 - 2.3 * duck, .3 + .9 * duck)}
    hands = {"n": dict(kind="none"), "f": dict(kind="open", flip=-1, dir=(.1 + .5 * duck, 1 - 2 * duck), curl=(.2, .25, .3, .35), spread=.25, thumb=.3)}
    ex = dict(lid=.6 + .4 * shock, look=(.7, .2 - .8 * shock), brows="up" if shock > .5 else "calm",
              mouth="talk" if shock > .2 else "smile", open=.9 * shock, smile=.5 * (1 - shock) - .7 * shock, hair=8 * shock * osc(t, 5))
    dm = dima(t, hip=hip, arms=arms, hands=hands, expr=ex, head_ang=.1 - .25 * shock, lean=.12 - .12 * duck)
    w = room(t, cup_open=ease_out(clamp((t - T_SHKAF + .02) / .12)), wipe_x=(rag_p[0] - 50 if duck < .01 else 380, 562))
    rag_svg = Wd.rag(rag_p[0], rag_p[1], .8, 15 * rub, t)
    fall = pile(t)
    lid_h = ""
    if t > T_SHKAF + .32:
        hx, hy = dm["head"]
        e = t - T_SHKAF - .32
        lid_h = lid_on_head(hx - 10, hy - 120, 14 * math.exp(-e * 6) * math.cos(e * 25) - 12, .7)
    elif t > T_SHKAF + .1:
        hx, hy = dm["head"]
        u = (t - T_SHKAF - .1) / .22
        lid_h = lid_on_head(hx - 10 + 220 * (1 - u), hy - 120 - 300 * (1 - u) ** 2, 200 * (1 - u) - 12, .7)
    k = ease_io(clamp((t - 8.48) / 1.6))
    shake = 14 * bump(t, T_SHKAF, .5)
    cam = (570 + 20 * k + shake * osc(t, 11), 1080 + shake * osc(t, 13, 1), 1.12 + .06 * k + .1 * bump(t, T_SHKAF, .3),
           1.5 * bump(t, T_SHKAF, .5) * osc(t, 7))
    return compose(w + layers(dm, "", rag_svg) + fall + lid_h, cam)


# ═════════════════════════ s08: всё на полу как попало, крышка на голове, кот выглядывает ═════════════════════════
def s08(t):
    hip = (440.0, 1262.0)
    sway = osc(t, .8)
    arms = {"n": ("ang", .25, .35), "f": ("ang", .18, .3)}
    hands = {"n": dict(kind="none"), "f": dict(kind="open", flip=-1, dir=(.1, 1), curl=(.3, .35, .4, .45), spread=.1, thumb=.4)}
    ex = dict(lid=.35, look=(.2, .7), brows="worry", mouth="flat", closed=blink_at(t, 11.0))
    dm = dima(t, hip=hip, arms=arms, hands=hands, expr=ex, head_ang=.12 + .02 * sway, lean=.03 + .02 * sway)
    wr = dm["wrist"]["n"]
    rag_svg = Wd.rag(wr[0] + 10, wr[1] + 30, .8, 80, t)
    hx, hy = dm["head"]
    e = t - T_POPALO
    if e < 0:
        lid_h = lid_on_head(hx - 10, hy - 120, -12 + 3 * sway, .7)
    else:
        u = clamp(e / .45)
        lx = hx - 10 + 260 * u
        ly = hy - 120 + 60 * u * (1 - u) * -4 + (Wd.FLOOR + 120 - (hy - 120)) * u * u
        lid_h = lid_on_head(lx, ly, -12 + 260 * u, .7) if u < 1 else \
            lid_on_head(hx + 250, Wd.FLOOR + 120, 6 * math.exp(-(e - .45) * 4) * math.cos((e - .45) * 30), .7)
    # кот выглядывает из-за холодильника
    cu = ease_out(clamp((t - 10.9) / .5))
    cx = 1330 - 110 * cu
    cst = dict(look=(-.8, .2), tilt=-12 * cu, ear=6 * bump(t, 11.7, .3), tail=5 * osc(t, .6), turn=-.4)
    cat_svg = Cat.draw(cx, Wd.FLOOR + 20, .55, cst, t)
    w = room(t, cup_open=1.0, cup_empty=True, wiped=1)
    k = ease_io(clamp((t - 10.36) / 2.2))
    jump = 10 * bump(t, T_POPALO, .3)
    cam = (830 - 30 * k, 1180 - 20 * k + jump, 1.08 + .06 * k, -.5 + .5 * k)
    # кот — за холодильником: рисуем до холодильника (холодильник в room, поэтому кот кладётся под копию его левой кромки)
    fridge_edge = Wd.fridge(0.0)
    body = w + cat_svg + fridge_edge + pile(t, behind=True) + layers(dm, "", rag_svg + lid_h) + pile(t, behind=False)
    return compose(body, cam)


# ═════════════════════════ s10: по пояс в холодильнике ═════════════════════════
def s10(t):
    out = smooth(T_HOLOD - .25, T_HOLOD + .05, t)
    scrub = osc(t, 3.2) * (1 - out)
    hip = (1250 - 170 * out, 1262.0)
    lean = .78 - .7 * out
    sp_in = (1420 + 40 * scrub, 1230 + 20 * osc(t, 6.4))
    sp_out = (hip[0] + 230, 980)
    sp = (sp_in[0] * (1 - out) + sp_out[0] * out, sp_in[1] * (1 - out) + sp_out[1] * out)
    arms = {"n": ("ik", (sp[0] - 30, sp[1] + 30), -1), "f": ("ik", (1380 - 120 * out, 1300 - 40 * out), -1)}
    hands = {"n": dict(kind="none"), "f": dict(kind="open", flip=-1, dir=(.4, 1), curl=(.3, .35, .4, .45), spread=.1, thumb=.4)}
    ex = dict(lid=.3 + .5 * out, look=(.6 - .6 * out, .2 * (1 - out)), brows="tired" if out < .5 else "up", mouth="grin" if out > .5 else "flat",
              hair=6 * bump(t, T_HOLOD, .4) * osc(t, 5), closed=blink_at(t, T_HOLOD + .5))
    dm = dima(t, hip=hip, arms=arms, hands=hands, expr=ex, head_ang=.25 * (1 - out) - .05 * out, lean=lean)
    hx, hy = dm["head"]
    foam = ""
    if out > .3:
        nx, ny = hx + 64 * BS * 1.0, hy + 50 * BS
        for j, (dx, dy, r) in enumerate([(0, 0, 18), (14, -10, 12), (-12, -8, 11), (6, 12, 10)]):
            foam += shape(ellipse_pts(nx + dx, ny + dy, r, r * .85, 10), "#ffffff", "", w=2.6, seed=3200 + j)
    w = room(t, cup_open=1.0, cup_empty=True, fridge_open=1.0, foam=True, clock=(2, 0), wiped=1)
    sponge = Wd.sponge(sp[0], sp[1], .8, 20 * scrub)
    k = ease_io(clamp((t - 14.2) / 1.8))
    ww = whip_in(t, 14.4, .2)
    hit = bump(t, T_HOLOD, .3)
    cam = (1180 + 20 * k - 200 * ww, 1060, 1.45 + .1 * k + .08 * hit, .8 - .8 * k)
    return compose(w + pile(t, behind=True) + layers(dm, "", sponge + foam) + pile(t, behind=False), cam)


# ═════════════════════════ s11: три часа ночи, вся кухня на полу ═════════════════════════
def s11(t):
    hip = (560.0, 1262.0)
    sway = osc(t, .7)
    arms = {"n": ("ang", .3 + .05 * sway, .5), "f": ("ang", .2, .3)}
    hands = {"n": dict(kind="none"), "f": dict(kind="open", flip=-1, dir=(.1, 1), curl=(.3, .35, .4, .45), spread=.1, thumb=.4)}
    ex = dict(lid=.15, look=(0, .1), brows="tired", mouth="talk", open=.25 + .1 * osc(t, .5), smile=-.4, hair=10 * osc(t, 1.4),
              closed=blink_at(t, 17.2, .3))
    dm = dima(t, hip=hip, arms=arms, hands=hands, expr=ex, head_ang=-.1 + .08 * sway, lean=.04 + .05 * sway, hood=8)
    wr = dm["wrist"]["n"]
    rag_svg = Wd.rag(wr[0] + 10, wr[1] + 30, .8, 80, t)
    hx, hy = dm["head"]
    sw = sweat(hx - 70, hy - 60, 1.0, clamp((t - 16.6) / .8))
    w = room(t, cup_open=1.0, cup_empty=True, fridge_open=1.0, clock=(3, 0), dust=0, wiped=1)
    cnt = (Wd.jar(150, Wd.CT_TOP, .7, "#e07a5f", -15) + Wd.bottle(1000, Wd.CT_TOP, .7, "#5f9a5a", 0) + Wd.pot_side(820, Wd.CT_TOP, .6, "#3f7a72") +
           Wd.bag(-80, Wd.CT_TOP, .7, "#e9c46a", 8))
    box = Wd.box(980, 1800, 1.1)
    k = ease_out(clamp((t - 15.96) / 1.9), 2)
    ww = whip_in(t, 15.96, .2)
    hit = bump(t, T_TRI, .3)
    cam = (600 + 180 * ww, 1220, (1.25 - .38 * k) * (1 + .05 * hit), -.6 * (1 - k))
    return compose(w + cnt + pile(t, True, behind=True) + layers(dm, "", rag_svg + sw) + pile(t, True, behind=False) + box, cam)


# ═════════════════════════ кот в коробке ═════════════════════════
BOX = (980.0, 1800.0, 1.1)


def cat_in_box(t, st, k=0.74):
    bx, by, bk = BOX
    return Wd.box(bx, by, bk, "back") + Cat.draw(bx - 6, by - 92, k, st, t) + Wd.box(bx, by, bk, "front")


def zzz(x, y, t):
    o = []
    for j in range(3):
        ph = (t * .55 + j / 3) % 1
        sz = 28 + 30 * ph
        a = math.sin(math.pi * ph)
        cx, cy = x + 40 * ph + 12 * math.sin(ph * 6 + j), y - 200 * ph
        o.append(f'<text x="{cx:.1f}" y="{cy:.1f}" font-family="IDB" font-size="{sz:.1f}" fill="#f6f1e3" stroke="{INK}" stroke-width="5" '
                 f'paint-order="stroke" opacity="{a:.3f}">Z</text>')
    return "".join(o)


def s12(t):
    st = dict(blink=1.0, tilt=10 + 2 * osc(t, .3), tail=3 * osc(t, .3), flame_e=.4, ear=0.0)
    w = room(t, cup_open=1.0, cup_empty=True, fridge_open=1.0, clock=(3, 10), dust=0, wiped=1)
    hx, hy = Cat.head_world(BOX[0] - 6, BOX[1] - 92, .74, st)
    found = smooth(T_KOT - .5, T_KOT + .1, t)
    u = ease_io(clamp((t - 17.56) / (T_KOT + .1 - 17.56)))
    cx = 120 + (BOX[0] - 120) * u
    cy = 1640 + (hy + 60 - 1640) * u
    s = 1.55 + .7 * found + .15 * clamp((t - T_KOT) / 1.8)
    cam = (cx, cy, s, .8 - .8 * u)
    # тёплое пятно огонька
    fx, fy = hx + 120, hy - 80
    g = lib.rad_grad([(0, "#ffb050", .3), (1, "#ffb050", 0)], fx, fy, 260, 260)
    glow = f'<rect x="{fx - 280:.1f}" y="{fy - 280:.1f}" width="560" height="560" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    return compose(w + pile(t, True) + cat_in_box(t, st) + glow + zzz(hx + 60, hy - 90, t), cam)


# ═════════════════════════ s13: утро, проснулся среди кастрюль ═════════════════════════
def s13(t):
    up = ease_out(clamp((t - T_PROSN) / .22), 3)
    over = .12 * bump(t, T_PROSN + .2, .3)
    hip = np.array([520.0, 1700.0])
    lean = -1.42 * (1 - up) + .1 + over
    feet = {"n": ((hip[0] + 360, hip[1] + 10), -1.3), "f": ((hip[0] + 345, hip[1]), -1.3)}
    arms = {"n": ("ang", -.2 * (1 - up) + .5 * up, .3), "f": ("ang", -.3 * (1 - up) + .4 * up, .4)}
    hands = {"n": dict(kind="open", flip=-1, dir=(.4, 1), curl=(.3, .35, .4, .45), spread=.1, thumb=.4),
             "f": dict(kind="open", flip=-1, dir=(.4, 1), curl=(.3, .35, .4, .45), spread=.1, thumb=.4)}
    snore = .2 + .15 * osc(t, .6)
    ex = dict(lid=.2 + .8 * up, closed=1.0 - up, look=(.1, -.2), brows="up" if up > .5 else "tired", mouth="talk", open=snore * (1 - up) + .85 * up,
              smile=-.6 * up, hair=12 * bump(t, T_PROSN, .5) * osc(t, 5))
    p = dict(hip=tuple(hip), scale=BS, lean=lean, feet=feet, arms=arms, hands=hands, expr=ex, head_ang=.0, hood=0)
    dm = people.draw(p, "dima")
    hx, hy = dm["head"]
    a = math.degrees(lean * .5)
    pot = Wd.pot_side(0, 0, .62, "#c44f3a", 180, handle=True)
    e = t - T_PROSN
    wob = 8 * math.exp(-max(e, 0) * 5) * math.cos(max(e, 0) * 25) if e > 0 else 0
    pot_svg = (f'<g transform="translate({hx:.1f} {hy:.1f}) rotate({a + wob:.2f}) translate(0 {-96:.1f})">{pot}</g>')
    w = room(t, mode="morning", cup_open=1.0, cup_empty=True, fridge_open=0.0, clock=(9, 30), dust=0, wiped=1)
    k = ease_io(clamp((t - 20.48) / 2.4))
    ww = whip_in(t, 20.68, .2)
    hit = bump(t, T_PROSN, .3)
    cam = (640 - 200 * ww + 20 * k, 1560 - 40 * up, 1.6 + .1 * k + .1 * hit, 1.2 * hit * osc(t, 8))
    return compose(w + pile(t, True, behind=True) + layers(dm, "", pot_svg) + pile(t, True, behind=False), cam, light="morning")


# ═════════════════════════ s16: вечер, порядок, таймер звенит, свет выключен ═════════════════════════
SWITCH2 = (720.0, 1030.0)


def s16(t):
    hip = (440.0, 1262.0)
    ring = smooth(T_ZVENIT - .02, T_ZVENIT + .04, t) * (1 - smooth(27.7, 27.9, t))
    put = smooth(27.5, 27.9, t)
    reach = smooth(28.1, 28.5, t)
    off = t >= 28.55
    rag_hand = np.array([560, 1150]) * (1 - put) + np.array([600, 1196]) * put
    sw_p = np.array(SWITCH2) + np.array([-24, 30])
    tgt_n = rag_hand * (1 - reach) + sw_p * reach
    if put >= 1:
        tgt_n = np.array([600, 1180]) * (1 - reach) + sw_p * reach
    arms = {"n": ("ik", (tgt_n[0] - 20, tgt_n[1] + 30), -1), "f": ("ang", .18, .3)}
    hands = {"n": dict(kind="open", flip=-1, dir=(.6, -1), curl=(0, .9, .9, .85), spread=.05, thumb=.8) if reach > .5 else dict(kind="none"),
             "f": dict(kind="open", flip=-1, dir=(.1, 1), curl=(.3, .35, .4, .45), spread=.1, thumb=.4)}
    ex = dict(lid=.6, look=(.6, .4 - .9 * reach), brows="calm", mouth="smile", smile=.5 + .5 * smooth(T_ZVENIT, T_ZVENIT + .3, t),
              closed=blink_at(t, 26.9) + blink_at(t, 28.9))
    dm = dima(t, hip=hip, arms=arms, hands=hands, expr=ex, head_ang=.12 - .12 * reach, lean=.1)
    mode = "dark" if off else "night"
    w = room(t, mode=mode, dust=0, wiped=1, clock=(21, 10))
    sw = shape(lib.rect_pts(SWITCH2[0] - 34, SWITCH2[1] - 46, SWITCH2[0] + 34, SWITCH2[1] + 46, 10), "#f6f1e6", "", w=3.6, seed=3301)
    ky = SWITCH2[1] + (14 if off else -14)
    sw += shape(lib.rect_pts(SWITCH2[0] - 11, ky - 16, SWITCH2[0] + 11, ky + 16, 5), "#e6dfd0", "", w=3, seed=3302)
    timer = Wd.egg_timer(860, Wd.CT_TOP + 20, .9, 0, ring, t)
    rag_svg = Wd.rag(rag_hand[0] + 20, rag_hand[1] + 10 * put, .8, 30 + 50 * put, t) if put < 1 else Wd.rag(620, 1206, .8, 80, 0)
    k = ease_io(clamp((t - 26.32) / 3.1))
    clk = 6 * bump(t, 28.55, .25)
    cam = (600 + 30 * k, 1020 + clk, 1.5 + .08 * k + .04 * bump(t, T_ZVENIT, .3), -.4 + .6 * k)
    if put < 1:
        front = rag_svg
        mid = ""
    else:
        front = ""
        mid = rag_svg
    return compose(w + sw + timer + mid + layers(dm, "", front), cam, light=mode)


# ═════════════════════════ s17: крупно кот в коробке, медленно моргает ═════════════════════════
def s17(t):
    bl = 0.0
    for c, half, hold in ((30.5, .4, .3), (31.95, .38, .25)):
        a = c - half
        if a <= t <= c + hold + half:
            bl = ease_io((t - a) / half) if t < c else (1.0 if t < c + hold else 1 - ease_io((t - c - hold) / half))
    st = dict(blink=bl, look=(0, 0), tilt=3 * osc(t, .25), tail=4 * osc(t, .45), ear=-10 * bump(t, 29.9, .35), smile=1.0 if t > 31.0 else 0.0)
    w = room(t, mode="night", dust=0, wiped=1, clock=(21, 20))
    hx, hy = Cat.head_world(BOX[0] - 6, BOX[1] - 92, .74, st)
    fx, fy = hx + 110, hy - 70
    g = lib.rad_grad([(0, "#ffb050", .35), (1, "#ffb050", 0)], fx, fy, 320, 320)
    glow = f'<rect x="{fx - 340:.1f}" y="{fy - 340:.1f}" width="680" height="680" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    u = clamp((t - 29.05) / 3.65)
    ww = whip_in(t, 29.25, .2)
    cam = (hx + 30 - 200 * ww, hy + 140 - 20 * u, 2.6 + .35 * ease_io(u), .6 - 1.0 * u)
    return compose(w + cat_in_box(t, st) + glow, cam, light="night")


SHOTS.update({"s05": s05, "s06": s06, "s07": s07, "s08": s08, "s10": s10, "s11": s11, "s12": s12, "s13": s13, "s16": s16, "s17": s17})
