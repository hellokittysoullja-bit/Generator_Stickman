"""Рилс 45 «сходил за хлебом»: все планы. frame(sid, t) -> SVG 1080×1920 (t — общее время ролика).
Дима — people.py (рилс 27), кот — cat.py, миры и предметы — props.py (улица, магазин) и world.py (кухня рилса 29).
Удары — на словах по voice/words.json."""
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
import props as Pr  # noqa: E402
import world as Wd  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, smooth, back_out  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wi(i):
    return WORDS[i]["start"]


BS = 0.62


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


def whip_in(t, t0, dur=0.2):
    return 1 - ease_out(clamp((t - t0) / dur), 3)


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


def sweat(x, y, k, u):
    if u <= 0:
        return ""
    yy = y + 40 * k * ease_in(u)
    r = 16 * k * min(1, u * 3)
    drop = [(x, yy - r * 2.2), (x + r, yy - r * .1), (x + r * .8, yy + r * .7), (x, yy + r), (x - r * .8, yy + r * .7), (x - r, yy - r * .1)]
    return shape(drop, "#bfe6fa", blob([(x - r * .4, yy - r * .6), (x - r * .1, yy - r * .9), (x - r * .1, yy - r * .2)], "#ffffff"), w=3, seed=3001)


# ═════════════════════════ Дима ═════════════════════════
HAND_N = dict(kind="open", flip=-1, dir=(.3, 1), curl=(.3, .35, .4, .45), spread=.1, thumb=.4)
HAND_NONE = dict(kind="none")


def dima(t, hip, lean=0.08, arms=None, hands=None, expr=None, head_ang=0.0, feet=None):
    hip = np.array(hip, float)
    if feet is None:
        feet = {"n": ((hip[0] + 16, hip[1] + 376), 0.0), "f": ((hip[0] - 4, hip[1] + 372), 0.0)}
    arms = arms or {"n": ("ang", .1, .3), "f": ("ang", .0, .3)}
    p = dict(hip=tuple(hip), scale=BS, lean=lean, feet=feet, arms=arms, hands=hands or {"n": HAND_N, "f": HAND_N}, expr=expr or {}, head_ang=head_ang,
             hood=0.0, strings=(3 * osc(t, 1.3), 2 * osc(t, 1.1, 1)))
    return people.draw(p, "dima")


def kw_hand():
    people.C = people.PAL["dima"]
    return dict(shape_fn=people.shape, line_fn=people.line, skin=people.C["SKIN"], skin_sh=people.C["SKIN_SH"], skin_sh2=people.C["SKIN_SH2"])


def walker(t, xfn, hy, expr=None, arms_extra=None, hands=None, lean=.1, head_ang=.04, stride=95.0, gait=380.0):
    """Дима идёт вправо: xfn(t) — x бёдер (px мира). Фаза шага привязана к пройденному пути, амплитуда шага падает с остановкой."""
    x = xfn(t)
    sp = (xfn(t + .03) - xfn(t - .03)) / .06
    ph = 2 * math.pi * x / gait
    amp = stride * clamp(abs(sp) / 220.0)
    bob = 7 * amp / stride * abs(math.sin(ph))
    hip = (x, hy - bob)
    gy = hy + 376

    def foot(p):
        s, c = math.sin(p), math.cos(p)
        return ((x + amp * s + 14, gy - 58 * amp / stride * max(0.0, c)), .22 * c * amp / stride)
    feet = {"n": foot(ph), "f": foot(ph + math.pi)}
    sw = amp / stride
    arms = {"n": ("ang", .5 * sw * math.sin(ph + math.pi) + .1, .35 + .2 * sw), "f": ("ang", .5 * sw * math.sin(ph) + .05, .3 + .2 * sw)}
    if arms_extra:
        arms.update(arms_extra)
    d = dima(t, hip, lean=lean, arms=arms, hands=hands, expr=expr, head_ang=head_ang, feet=feet)
    return d


def layers(d, mid="", front=""):
    return d.get("legs", "") + d["arm_f"] + d["body"] + mid + d["arm_n"] + front


def vignette(col="#2a1408", a=.32):
    g = lib.rad_grad([(0, col, 0), (.66, col, 0), (1, col, a)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def compose(world_svg, cam, front="", screen="", vig=("#2a1408", .3)):
    cx, cy, s, r = cam
    set_ink(s)
    o = [f'<rect width="1080" height="1920" fill="#e7cfa3"/>',
         f'<g transform="{lib.cam(cx, cy, s, r)}">{world_svg}{front}</g>', screen, vignette(*vig)]
    return lib.svg("".join(o))


def lookat(d, tx, ty, scale=1.0):
    """look-вектор зрачков на точку мира (тx, ty) от головы."""
    hx, hy = d["head"]
    v = np.array([tx - hx, ty - hy], float)
    n = np.linalg.norm(v) + 1e-6
    return (float(np.clip(v[0] / n * scale, -1, 1)), float(np.clip(v[1] / n * scale, -1, 1)))


# ═════════════════════════ s01–s02: улица ═════════════════════════
def x_street(t):
    """x бёдер на улице (s01 — s02): идёт, у входа тормозит и встаёт под растяжкой."""
    if t < 2.1:
        return 90 + 380 * t
    u = clamp((t - 2.1) / 1.0)
    return 90 + 380 * 2.1 + 150 * (1 - (1 - u) ** 2) * 1.0


def street_dima(t, expr, bubble_on=1.0, look=None):
    d = walker(t, x_street, 1290, expr=expr, lean=.09, head_ang=.05)
    return d


def s01(t):
    z, r = hook_zoom(t, 0.0, .4, .22, -3.5)
    d = walker(t, x_street, 1290, expr=dict(lid=.7, look=(.9, -.1), brows="calm", mouth="smile", smile=.6, closed=blink_at(t, .9)), lean=.1)
    hx, hy = d["head"]
    k = back_out(clamp((t - .12) / .3), 1.9)
    bub = Pr.bubble(hx + 60, hy - 330, 340, 250, (hx + 40, hy - 120), k=k, content=Pr.loaf(hx + 60, hy - 290, .9, 0), wob=t * 2)
    cx = hx + 220 + 20 * ease_io(clamp(t / 1.5))
    cam = (cx, 1180 - 10 * t, 1.35 * z, r + .4 * osc(t, .4))
    hit = bump(t, wi(2), .3)
    cam = (cam[0], cam[1], cam[2] * (1 + .05 * hit), cam[3])
    return compose(Pr.street(t, banner=0) + layers(d) + bub, cam, vig=("#3a2410", .22))


def s02(t):
    hx0 = x_street(t)
    d = walker(t, x_street, 1290, expr=dict(lid=.9, look=(.3, -.85), brows="up", mouth="talk", open=.25, closed=blink_at(t, 2.3)), lean=.04 * (1 - smooth(2.1, 3.0, t)) + .02,
               head_ang=-.12 * smooth(2.0, 2.8, t) + .05)
    sw = math.sin(t * 5) * (.5 + 1.2 * bump(t, wi(9), .5))
    u = ease_io(clamp((t - 1.3) / 2.2))
    cam = (hx0 + 130 + 20 * u, 1230 - 190 * u, 1.35 + .55 * u, .6 - .8 * u)
    wi9 = wi(9)
    flash = Pr.glow(1070, 760, 460, "#ffe27a", .6 * bump(t, wi9, .6))
    return compose(Pr.street(t, banner_sw=sw, banner=smooth(2.05, 2.2, t)) + layers(d) + flash, cam, vig=("#3a2410", .22))



# ═════════════════════════ магазин ═════════════════════════
CART = (720.0, 1560.0, 1.25)


def cart_svg(t, items=(), extra_front="", x=None, shake=0.0):
    cx, cy, ck = CART
    if x is not None:
        cx = x
    cy += 4 * math.sin(t * 20) * shake
    mid = ""
    if "cheese" in items:
        mid += Pr.cheese_wheel(cx + 20, cy - 52 * ck, .5 * ck)
    if "flam" in items:
        mid += Pr.flamingo(cx - 10, cy - 60 * ck, .55 * ck, 14, smile=.0, t=t, wob=.6)
    if "garl" in items:
        mid += Pr.garland([(cx - 130 * ck, cy - 150 * ck), (cx - 40 * ck, cy - 110 * ck), (cx + 60 * ck, cy - 130 * ck), (cx + 150 * ck, cy - 160 * ck)], t, 1.0)
    if "feed" in items:
        mid += Pr.feeder(cx + 90 * ck, cy - 52 * ck, .42 * ck)
    return Pr.cart_back(cx, cy, ck) + mid + extra_front + Pr.cart_front(cx, cy, ck)


def arc(p0, p1, u, h):
    u = clamp(u)
    return (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u - h * 4 * u * (1 - u))


def table(x0, x1, y):
    o = Pr.shape(Pr.rect_pts(x0, y, x1, y + 36, 6), "#d9b27c", "", w=4.6, seed=7000)
    o += Pr.shape(Pr.rect_pts(x0 + 30, y + 36, x1 - 30, y + 260), "#f2e8d5", "", w=4.4, seed=7001)
    o += Pr.shape(Pr.rect_pts(x0 + 40, y + 260, x0 + 80, 1650), "#9aa6b0", "", w=4, seed=7002)
    o += Pr.shape(Pr.rect_pts(x1 - 80, y + 260, x1 - 40, 1650), "#9aa6b0", "", w=4, seed=7003)
    return o


def s03(t):
    tg, tt = 4.2, 4.64
    reach = smooth(3.85, 4.2, t) * (1 - smooth(4.4, 4.6, t))
    hip = (380.0, 1262.0)
    tgt = (1050, 1190)
    wr = (tgt[0] * reach + 640 * (1 - reach), tgt[1] * reach + 1330 * (1 - reach))
    arms = {"n": ("ik", wr, -1), "f": ("ang", .15, .3)}
    d = dima(t, hip, lean=.12 + .06 * reach, arms=arms, hands={"n": dict(kind="open", flip=-1, dir=(1, .2), curl=(.5, .5, .5, .5), spread=.1, thumb=.5), "f": HAND_N},
             expr=dict(lid=.9, look=(.9, .1), brows="up", mouth="grin" if t > 4.0 else "smile", smile=.8, closed=blink_at(t, 3.8)), head_ang=.1)
    mid = ""
    flying = 4.28 < t < tt
    landed = t >= tt
    wheels = []
    wheels.append(Pr.cheese_wheel(1180, 1215, .75, -4))
    if not (flying or landed):
        wheels.append(Pr.cheese_wheel(1180, 1150, .75, 3, shine=bump(t, wi(11), .5)))
    else:
        wheels.append("")
    fl = ""
    if flying:
        p = arc((1100, 1140), (740, 1430), (t - 4.28) / (tt - 4.28), 260)
        fl = Pr.cheese_wheel(p[0], p[1], .5 * CART[2], 540 * (t - 4.28))
    sh = 9 * bump(t, tt, .3) * osc(t, 9)
    u = ease_io(clamp((t - 3.4) / 1.9))
    ww = whip_in(t, 3.5, .2)
    cam = (850 - 240 * ww + 30 * u, 1300 + sh, 1.25 + .1 * u, .5 - .6 * u)
    tabsvg = table(960, 1560, 1250) + "".join(wheels) + Pr.price_tag(1380, 1190, 1.0, -5)
    return compose(Pr.store(t) + Pr.sale_sign(1000, 520, t, 1.0) + tabsvg + cart_svg(t, ("cheese",) if landed else (), shake=bump(t, tt, .3)) + layers(d) + fl, cam,
                   vig=("#222a30", .22))


def s04(t):
    hip = (440.0, 1262.0)
    pull = smooth(5.7, 6.4, t)
    drape = smooth(6.2, 6.7, t)
    wr = (700 - 150 * drape, 1010 + 150 * drape)
    arms = {"n": ("ik", wr, -1), "f": ("ang", .1, .35)}
    d = dima(t, hip, lean=.06, arms=arms, hands={"n": dict(kind="open", flip=-1, dir=(.4, -1), curl=(.5, .6, .6, .6), spread=.1, thumb=.5), "f": HAND_N},
             expr=dict(lid=.85, look=(.7, -.2), brows="up", mouth="grin", smile=.8, closed=blink_at(t, 6.9)), head_ang=-.05)
    hx, hy = d["head"]
    if drape < .5:
        sag = 200 * (1 - pull * .6)
        pts = [(1250, 780), (1100, 780 + sag * .7), (950, 780 + sag), (820, 780 + sag * .7), (wr[0] + 20, wr[1] - 20)]
    else:
        pts = [(hx - 120, hy + 110), (hx - 70, hy + 250), (hx + 10, hy + 330), (hx + 110, hy + 280), (hx + 140, hy + 150)]
    fl = bump(t, wi(21), .6)
    on = smooth(5.55, 5.9, t)
    gar = Pr.garland(pts, t, on, flash=fl)
    u = ease_io(clamp((t - 5.1) / 2.7))
    ww = whip_in(t, 5.2, .2)
    cam = (560 + 60 * u - 250 * ww, 1150 - 40 * u, 1.3 + .3 * u + .08 * fl, -.6 + .8 * u)
    return compose(Pr.store(t) + layers(d, gar), cam, vig=("#222a30", .22))


FL_X = 900.0


def s05(t):
    pop = back_out(clamp((t - wi(23) + .25) / .35), 2.2)
    k = 1.25 * pop
    hip = (360.0, 1262.0)
    d = dima(t, hip, lean=-.02, arms={"n": ("ang", .1, .3), "f": ("ang", .0, .3)},
             expr=dict(lid=1.0, look=(.8, -.6), brows="up", mouth="talk", open=.3, closed=blink_at(t, 9.0)), head_ang=-.14)
    u = ease_io(clamp((t - 7.7) / 1.8))
    ww = whip_in(t, 7.8, .2)
    cam = (680 - 200 * ww, 1250 - 60 * u, 1.35 - .1 * u, -.5 + .5 * u)
    fl = Pr.flamingo(FL_X, 1600, k, 0, smile=0, t=t, wob=1.0 if pop > .9 else 0) if pop > .02 else ""
    return compose(Pr.store(t) + fl + layers(d), cam, vig=("#222a30", .22))


def s06(t):
    sm = smooth(wi(28), wi(28) + .3, t)
    d = dima(t, (470.0, 1262.0), lean=0.0, arms={"n": ("ang", .1, .3), "f": ("ang", .0, .3)},
             expr=dict(lid=.9, look=(.9, -.4), brows="up", mouth="smile", smile=.2 + .8 * sm, blush=sm, closed=blink_at(t, 9.8)), head_ang=-.1)
    u = ease_io(clamp((t - 9.3) / 1.7))
    cam = (690 + 20 * u, 850 + 20 * u, 1.5 + .4 * u, .8 - 1.2 * u)
    fl = Pr.flamingo(780, 1600, 1.25, 0, smile=sm, t=t, wob=.6 * (1 - sm))
    fx, fy = 780 + 100, 1600 - 740
    spark = Pr.sparkle(fx + 120, fy - 80, 50 * bump(t, wi(28) + .1, .5), t * 2) if sm > 0 else ""
    return compose(Pr.store(t) + fl + layers(d) + spark, cam, vig=("#222a30", .2))


def s07(t):
    grab = wi(31)
    reach = smooth(grab - .3, grab, t) * (1 - smooth(grab + .5, grab + .7, t))
    tgt = (1060, 1130)
    wr = (tgt[0] * reach + 640 * (1 - reach), tgt[1] * reach + 1330 * (1 - reach))
    d = dima(t, (380.0, 1262.0), lean=.12 + .06 * reach,
             arms={"n": ("ik", wr, -1), "f": ("ang", .15, .3)},
             hands={"n": dict(kind="open", flip=-1, dir=(1, .2), curl=(.5, .5, .5, .5), spread=.1, thumb=.5), "f": HAND_N},
             expr=dict(lid=.85, look=(.9, .1), brows="up", mouth="smile", smile=.7, closed=blink_at(t, 12.5)), head_ang=.08)
    fly0, fly1 = grab + .3, grab + .75
    flying = fly0 < t < fly1
    landed = t >= fly1
    items = ("cheese", "flam", "garl") + (("feed",) if landed else ())
    fe = ""
    if not (flying or landed):
        fe = Pr.feeder(1180, 1250, 1.0)
    if flying:
        p = arc((1120, 1160), (800, 1450), (t - fly0) / (fly1 - fly0), 260)
        fe = Pr.feeder(p[0], p[1], 1.0 - .55 * ease_io((t - fly0) / (fly1 - fly0)), 360 * (t - fly0))
    u = ease_io(clamp((t - 10.9) / 2.0))
    ww = whip_in(t, 11.0, .2)
    cam = (720 - 240 * ww + 30 * u, 1280, 1.3 + .12 * u, .5 - .5 * u)
    sh = 8 * bump(t, fly1, .3) * osc(t, 9)
    cam = (cam[0], cam[1] + sh, cam[2], cam[3])
    shelf = table(960, 1560, 1250) + fe
    return compose(Pr.store(t) + shelf + cart_svg(t, items, shake=bump(t, fly1, .3)) + layers(d), cam, vig=("#222a30", .22))


def s08(t):
    d = dima(t, (330.0, 1262.0), lean=.02, arms={"n": ("ik", (560, 1300), -1), "f": ("ang", .15, .3)},
             hands={"n": HAND_NONE, "f": HAND_N},
             expr=dict(lid=.55, look=(.9, .2), brows="det", mouth="flat", closed=blink_at(t, 13.3)), head_ang=.04)
    hx, hy = d["head"]
    k = back_out(clamp((t - 13.2) / .3), 1.8)
    cx, cy = hx + 140, hy - 380
    cont = (Pr.shape(ellipse_pts(cx, cy + 90, 110, 30, 12), "#e8863a", "", w=4, seed=8000) +
            "".join(blob(ellipse_pts(cx - 60 + i * 24, cy + 70 + 4 * (i % 2), 8, 6, 6), "#a8683a", 1) for i in range(6)) +
            Cat.draw(cx - 70, cy + 70, .27, dict(blink=blink_at(t, 13.9), tilt=0, tail=4 * osc(t, .6), flame_e=.6, smile=1), t))
    bub = Pr.bubble(cx, cy, 420, 300, (hx + 40, hy - 130), k=k, content=cont, wob=t)
    u = ease_io(clamp((t - 12.8) / 1.4))
    ww = whip_in(t, 12.9, .2)
    cam = (600 - 160 * ww, 1060 - 30 * u, 1.4 + .08 * u, .0)
    return compose(Pr.store(t) + cart_svg(t, ("cheese", "flam", "garl", "feed"), x=760) + layers(d) + bub, cam, vig=("#222a30", .22))


# ═════════════════════════ кухня Димы ═════════════════════════
def room(t, mode="morning"):
    o = [Wd.wall(mode), Wd.window(mode, t), Wd.clock_wall(10, 40, mode), Wd.counter(), Wd.floor(mode), Wd.shelf(0, 1, (0, 0)), Wd.cupboard(0.0),
         Wd.fridge(0.0), Wd.switch(True), Wd.lamp(mode, t, 0.0)]
    return "".join(o)


def s09(t):
    hip = (520.0, 1262.0)
    cyc = (t - 14.2) * 1.5
    ph = math.sin(math.pi * 2 * cyc * .5)
    wr = (650 + 120 * max(0, ph), 1180 + 40 * (1 - max(0, ph)))
    d = dima(t, hip, lean=.12, arms={"n": ("ik", wr, -1), "f": ("ang", .25, .3)}, hands={"n": HAND_NONE, "f": HAND_N},
             expr=dict(lid=.7, look=(.9, .5), brows="calm", mouth="smile", smile=.5, closed=blink_at(t, 15.2)), head_ang=.14)
    shown = [wi(40) + .25, wi(41), wi(41) + .45, wi(41) + .9]
    o = ""
    ct = Wd.CT_TOP
    o += Wd.bag(760, ct, 1.4, "#e9c46a", 3) + Wd.bag(900, ct, 1.3, "#81b29a", -4)
    if t > shown[0]:
        o += Pr.cheese_wheel(1010, ct, .45)
    if t > shown[1]:
        o += Pr.feeder(1120, ct, .55)
    if t > shown[2]:
        o += Pr.flamingo(1230, ct, .85, 0, smile=0, t=t, wob=.5)
    if t > shown[3]:
        o += Pr.garland([(560, ct - 60), (620, ct - 20), (700, ct - 14), (780, ct - 30)], t, 1.0)
    u = ease_io(clamp((t - 14.0) / 1.9))
    ww = whip_in(t, 14.1, .2)
    cam = (880 - 260 * ww + 20 * u, 1100, 1.2 + .2 * u, -.4 + .5 * u)
    return compose(room(t) + o + layers(d), cam, vig=("#2a1408", .28))


def s10(t):
    realize = smooth(wi(43), wi(43) + .25, t)
    no = wi(46)
    d = dima(t, (480.0, 1262.0), lean=.1, arms={"n": ("ik", (720, 1130), -1), "f": ("ang", .25, .3)}, hands={"n": HAND_NONE, "f": HAND_N},
             expr=dict(lid=.6 + .45 * realize, look=(.4, .9), brows="worry" if realize > .5 else "calm", mouth="talk" if realize > .5 else "flat", open=.5 * realize,
                       closed=blink_at(t, 16.3)), head_ang=.2 - .1 * realize)
    hx, hy = d["head"]
    bag = Wd.bag(720, 1226, 1.35, "#e9c46a", 14)
    sw = sweat(hx + 120, hy - 110, 1.2, clamp((t - 16.4) / 1.0))
    k = back_out(clamp((t - no + .05) / .3), 1.9)
    bub = Pr.bubble(hx + 260, hy - 330, 360, 260, (hx + 60, hy - 110), k=k, content=Pr.loaf(hx + 260, hy - 290, .9, 0, cross=1.0))
    u = ease_io(clamp((t - 15.7) / 1.9))
    cam = (hx + 140, hy + 20 - 20 * u, 1.55 + .2 * u + .08 * bump(t, no, .3), .5 - .6 * u)
    return compose(room(t) + layers(d, "", bag) + sw + bub, cam, vig=("#2a1408", .28))


RING = (560.0, 1760.0)


def cat_in_ring(t, st, k=.85, drop=0.0):
    x, y = RING
    return (Pr.flamingo_ring(x, y, 1.0, t, "back", smile=0) +
            Cat.draw(x - 20, y - 20 - 500 * drop, k, st, t) +
            Pr.flamingo_ring(x, y, 1.0, t, "front"))


def s11(t):
    tj = wi(48)
    drop = max(0.0, 1 - ease_in(clamp((t - tj + .22) / .22)))
    sq = bump(t, tj + .02, .35)
    st = dict(blink=blink_at(t, 18.6), tilt=8 + 2 * osc(t, .3) + 6 * sq, tail=4 * osc(t, .5), flame_e=.5, look=(-.6, .1), smile=0)
    u = ease_io(clamp((t - 17.5) / 1.9))
    ww = whip_in(t, 17.6, .2)
    cam = (700 + 220 * ww, 1600 - 30 * u, 1.3 + .15 * u, -.7 + .8 * u)
    rup = 8 * bump(t, tj + .15, .35)
    cam = (cam[0], cam[1] + rup, cam[2], cam[3])
    return compose(room(t) + cat_in_ring(t, st, .85, drop), cam, vig=("#2a1408", .28))


def s12(t):
    bl = 0.0
    for c, half, hold in ((20.2, .3, .25),):
        a = c - half
        if a <= t <= c + hold + half:
            bl = ease_io((t - a) / half) if t < c else (1.0 if t < c + hold else 1 - ease_io((t - c - hold) / half))
    st = dict(blink=bl, tilt=6 + 2 * osc(t, .25), tail=3 * osc(t, .4), flame_e=.5, look=(-.9, .15), ear=-12 * bump(t, wi(55) + .15, .35), smile=0)
    x, y = RING
    hx, hy = Cat.head_world(x - 20, y - 20, .85, st)
    u = clamp((t - 19.3) / 2.2)
    cam = (hx + 20, hy + 60 - 20 * u, 3.0 + .4 * ease_io(u), .6 - .9 * u)
    return compose(room(t) + cat_in_ring(t, st, .85, 0), cam, vig=("#2a1408", .3))


# ═════════════════════════ улица: дорога обратно ═════════════════════════
def x_back(t):
    return 140 + 400 * (t - 21.5)


def paper_small(x, y, k=1.0, rot=0.0, w=1.0):
    pts = lib.T([(-40, -52, 1), (40, -52, 1), (40, 52, 1), (-40, 52, 1)], x, y, k, rot)
    o = shape(pts, "#fffdf2", "", w=3.2, seed=9000, var=.15)
    o += line(lib.T([(-22, -4), (24, -4)], x, y, k, rot), 4 * w, "#2b4a8a", seed=9001, taper=.1, wmin=.9)
    return o


def s13(t):
    d = walker(t, x_back, 1290, expr=dict(lid=.75, look=(.9, 0), brows="calm", mouth="smile", smile=.3, closed=blink_at(t, 22.5)), lean=.12,
               hands={"n": HAND_NONE, "f": HAND_N}, arms_extra={"n": ("ik", (x_back(t) + 150, 1180 + 20 * osc(t, 1.0)), -1)})
    wx, wy = d["wrist"]["n"]
    pap = paper_small(wx + 10, wy - 10, 1.0, -8)
    u = ease_io(clamp((t - 21.4) / 2.3))
    ww = whip_in(t, 21.5, .2)
    cam = (x_back(t) + 240 - 300 * ww, 1190, 1.3 + .1 * u, .5 - .6 * u)
    return compose(Pr.street(t) + layers(d, "", pap), cam, vig=("#3a2410", .22))


def s14(t):
    wr_t = wi(66)
    wrote = smooth(wr_t - .1, wr_t + .9, t)
    squeeze = smooth(wi(69) - .1, wi(69) + .3, t)
    jit = 3 * osc(t, 3.0) * (1 - squeeze) + 6 * bump(t, wr_t, .3)
    pap_x, pap_y = 540 + jit, 930
    paper = Pr.shape(Pr.rect_pts(-300, -430, 300, 430, 8), "#fffdf2",
                     "".join(line([(-260, -330 + 80 * i), (260, -330 + 80 * i)], 3, "#b8c6e6", seed=9100 + i, taper=.05, wmin=.9) for i in range(9)) +
                     line([(-210, -430), (-210, 430)], 3, "#e8a0a0", seed=9120, taper=.05, wmin=.9), w=5.4, seed=9101, var=.1)
    cid = lib.clip_of([(-300 + 600 * wrote - 600, -200, 1), (-300 + 600 * wrote, -200, 1), (-300 + 600 * wrote, 100, 1), (-300 + 600 * wrote - 600, 100, 1)]) if wrote > 0 else None
    text = ""
    if cid:
        text = (f'<g clip-path="url(#{cid})">' + Pr.txt(0, 30, "ХЛЕБ", 165, "#2b4a8a", rot=-2) +
                line([(-170, 60), (170, 66)], 9, "#2b4a8a", seed=9130, taper=.3) + "</g>")
    box = Pr.shape(Pr.rect_pts(-250, -60, -190, 0, 4), "none", "", w=4, seed=9140)
    pg = (f'<g transform="translate({pap_x:.1f} {pap_y:.1f}) rotate({-3 + 2 * osc(t, .5):.2f}) scale({1 - .06 * squeeze:.3f})">{paper}{text}</g>')
    kw = kw_hand()
    old = people.LWK
    people.LWK = 2.6
    try:
        hnd = Hand.hand((500, 1620 - 60 * squeeze), (.2, -1), flip=1, k=3.4, curl=(.35 + .55 * squeeze, .4 + .5 * squeeze, .45 + .5 * squeeze, .5 + .5 * squeeze),
                        spread=.12, thumb=.3 + .5 * squeeze, bend=.1, seed=9150, nails=True, **kw)
    finally:
        people.LWK = old
    u = ease_io(clamp((t - 23.4) / 2.4))
    ww = whip_in(t, 23.6, .2)
    cam = (540 - 220 * ww, 1000 - 20 * u, 1.0 + .22 * u, .5 - .5 * u)
    bgc = f'<rect x="-1500" y="-1500" width="4000" height="4400" fill="#cfe2d6"/>' + Pr.glow(540, 700, 900, "#fff6d6", .4)
    return compose(bgc + pg + hnd, cam, vig=("#2a3a30", .25))


def x_pass(t):
    if t < 26.3:
        return 330 + 340 * (t - 25.6)
    u = clamp((t - 26.3) / .6)
    return 330 + 340 * .7 + 40 * (1 - (1 - u) ** 2)


def s15(t):
    turn = smooth(26.3, 26.7, t)
    sm = smooth(26.35, 26.6, t)
    x = x_pass(t)
    d = walker(t, x_pass, 1290, expr=dict(lid=.8 + .2 * turn, look=(.9, 0.0 + .3 * turn), brows="up" if turn > .5 else "calm", mouth="talk" if turn > .5 else "smile",
                                          open=.3, smile=.3, closed=blink_at(t, 26.0)), lean=.1 - .06 * turn, head_ang=.0,
               hands={"n": HAND_NONE, "f": HAND_N}, arms_extra={"n": ("ik", (x + 150, 1190), -1)})
    wx, wy = d["wrist"]["n"]
    pap = paper_small(wx + 10, wy - 10, 1.0, -8)
    u = ease_io(clamp((t - 25.5) / 2.2))
    ww = whip_in(t, 25.6, .2)
    cam = (760 - 220 * ww + 40 * u, 1260 - 30 * u, 1.5 + .25 * u, -.5 + .6 * u)
    return compose(Pr.street(t, banner=1, window_flamingo=1.0, flam_smile=sm, banner_sw=.3 * math.sin(t * 4)) + layers(d, "", pap) +
                   (Pr.sparkle(930, 1250, 36 * bump(t, 26.4, .6), t * 2) if sm > 0 else ""), cam, vig=("#3a2410", .22))


def x_home(t):
    return 120 + 330 * (t - 27.7)


def s16(t):
    x = x_home(t)
    pop = back_out(clamp((t - wi(81) + .1) / .3), 1.9)
    d = walker(t, x_home, 1290, expr=dict(lid=.8, look=(.9, 0), brows="calm", mouth="grin", smile=.8, closed=blink_at(t, 28.5)), lean=.14, head_ang=.0,
               hands={"n": HAND_NONE, "f": HAND_N}, arms_extra={"n": ("ik", (x + 180, 1240), -1), "f": ("ik", (x + 190, 1360), -1)})
    fl = Pr.flamingo(x + 280, 1665, .9, 5 + 2 * osc(t, 1.9), smile=1.0, t=t, wob=1.0)
    wx, wy = d["wrist"]["f"]
    pap = paper_small(wx + 20, wy - 90, 1.6, 10 + 8 * osc(t, 3))
    hx, hy = d["head"]
    bub = Pr.bubble(hx - 60, hy - 330, 340, 250, (hx + 20, hy - 110), k=pop, content=Pr.loaf(hx - 60, hy - 290, .9, 0, cross=1.0))
    u = ease_io(clamp((t - 27.6) / 2.3))
    ww = whip_in(t, 27.7, .2)
    cam = (x + 230 - 260 * ww - 40 * u, 1150, 1.2 - .12 * u, -.4 + .5 * u)
    return compose(Pr.street(t, banner=0) + layers(d, "", pap) + fl + bub, cam, vig=("#3a2410", .22))


SHOTS = {"s01": s01, "s02": s02, "s03": s03, "s04": s04, "s05": s05, "s06": s06, "s07": s07, "s08": s08, "s09": s09, "s10": s10, "s11": s11, "s12": s12,
         "s13": s13, "s14": s14, "s15": s15, "s16": s16}


def frame(sid, t):
    lib.DEFS.clear()
    return SHOTS[sid](t)
