"""Стойка «desk» рилса 50 «это на 20 минут»: планы s01 s02 s06 s07 s16 s17 s18.
frame(sid, t) -> SVG 1080×1920 (t — общее время ролика). Мир — dworld.py, Дима — people.py (рилс 27), кот — cat.py (рилс 24–29).
Удары — на словах по voice/words.json рилса 50 (индексы другие, чем в 29!). Камера у каждого плана своя, движется с первого кадра."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat as Cat  # noqa: E402
import dworld as Dw  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import world as Wd  # noqa: E402
from hand import grip  # noqa: E402,F401
from lib import INK, back_out, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wi(i):
    return WORDS[i]["start"]


T_20, T_SEL = wi(5), wi(8)            # «двадцать» 1.60, «сел» 2.72
T_SIDEL = wi(24)                      # «сидел» 8.88
T_POCHEMU, T_USPEEM = wi(26), wi(32)  # 10.24, 12.00
T_KOT_SPIT = wi(85)                   # «кот» 32.04
T_NAPISHI = wi(88)                    # «Напиши» 33.81

BS = 0.62
HIP = np.array([400.0, 1262.0])
CATX = 1110.0
CATK = .78
CATX2 = 925.0
MUG_FAR = [(1230, "#c44f3a", 0)]


def osc(t, f, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


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
    u = clamp((t - t0) / dur)
    return (1 - ease_out(u, 3))


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


# ═════════════════════════ Дима ═════════════════════════
def dima(t, hip=None, lean=0.16, arms=None, hands=None, expr=None, head_ang=0.0, hood=0.0, head_off=(0, 0)):
    hip = HIP if hip is None else np.array(hip, float)
    feet = {"n": ((hip[0] + 16, hip[1] + 376), 0.0), "f": ((hip[0] - 4, hip[1] + 372), 0.0)}
    p = dict(hip=tuple(hip), scale=BS, lean=lean, feet=feet, arms=arms, hands=hands or {}, expr=expr or {}, head_ang=head_ang,
             hood=hood, strings=(3 * osc(t, 1.3), 2 * osc(t, 1.1, 1)), head_off=head_off)
    return people.draw(p, "dima")


def layers(d, mid="", front=""):
    return d.get("legs", "") + d["arm_f"] + d["body"] + mid + d["arm_n"] + front


def wrist_for_tip(tip, d, flip=-1):
    d = np.array(d, float)
    d /= np.linalg.norm(d)
    nn = np.array([-d[1], d[0]]) * flip
    return np.array(tip, float) - d * 138 * BS + nn * 25 * BS


KEYS_N = np.array([620.0, 1203.0])
KEYS_F = np.array([596.0, 1208.0])


def type_pose(t, amt=1.0, ph=0.0):
    """Руки на клавиатуре: запястья чуть качаются, пальцы щёлкают вразнобой."""
    b1 = osc(t, 6.4 + ph, 0.3)
    b2 = osc(t, 5.2, 1.7)
    b3 = osc(t, 7.3, 0.9)
    wn = KEYS_N + np.array([3 * b1 * amt, 2.5 * max(0, b1) * amt])
    wf = KEYS_F + np.array([3 * b2 * amt, 2.5 * max(0, b2) * amt])
    dr = (1.0, .55)
    c = .45 * amt + .1 * (1 - amt)
    hn = dict(kind="open", flip=-1, dir=dr, curl=(c + .35 * amt * b1, c + .3 * amt * b3, c + .35 * amt * (-b1), c + .3 * amt * b2),
              spread=.08, thumb=.35, bend=.06)
    hf = dict(kind="open", flip=-1, dir=dr, curl=(c + .3 * amt * b2, c + .35 * amt * (-b3), c + .3 * amt * b1, c + .3 * amt * (-b2)),
              spread=.08, thumb=.35, bend=.06)
    return wn, wf, hn, hf


def arms_from(wn, wf):
    return {"n": ("ik", tuple(wn), -1), "f": ("ik", tuple(wf), -1)}


# ═════════════════════════ сборка кадра ═════════════════════════
def vignette(u):
    col = "#2a1408" if u < .6 else "#0a0c20"
    g = lib.rad_grad([(0, col, 0), (.62, col, 0), (1, col, .4)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def compose(world_svg, cam, u, front="", over=""):
    cx, cy, s, r = cam
    o = [f'<rect width="1080" height="1920" fill="#e7cfa3"/>',
         f'<g transform="{lib.cam(cx, cy, s, r)}">{world_svg}{Dw.overlay(u)}{front}</g>', over, vignette(u)]
    return lib.svg("".join(o))


def screen_glow(u, k=1.0):
    """Свет экрана на лице и руках ночью (экран излучает)."""
    nk = Dw.night_k(u) * k
    if nk < .02:
        return ""
    g = lib.rad_grad([(0, "#a9c8ff", .34), (1, "#a9c8ff", 0)], 640, 1110, 360, 300)
    return f'<rect x="200" y="760" width="900" height="700" fill="url(#{g})" opacity="{nk:.3f}" style="mix-blend-mode:screen"/>'


def base_world(t, u, clock, open_, screen, mugs=(), balls=(), sheets=(), steam_at=None):
    return Dw.room(t, u, clock, mugs, balls, sheets, steam_at) + Dw.laptop(open_, screen)


MUG_DAY = [(900, "#c44f3a", 0)]
MUG_NIGHT = [(900, "#c44f3a", 0), (975, "#3f7a72", 0), (1240, "#e9c46a", 0)]


# ═════════════════════════ s01: хук, влёт; открывает ноутбук, тычет таймер, печатает ═════════════════════════
def s01_cam(t):
    z, r = hook_zoom(t, 0.0, .4, .22, -3.5)
    k = ease_io(clamp(t / 1.9))
    cam = (610 + 20 * k, 1060 - 10 * k, 1.8 * z * (1 + .05 * k), r + .4 * osc(t, .4))
    hit = bump(t, wi(3), .3)            # «отчёт» — удар камерой
    return (cam[0], cam[1], cam[2] * (1 + .05 * hit), cam[3])


def s01_pose(t):
    """Рука: у крышки (0–.45), к экрану (.45–.85), тычок (.85–1.0), назад на клавиатуру (1.0–1.3), печатает."""
    op = .55 + .45 * ease_out(clamp(t / .7))
    lid_top = np.array([LID_GRAB[0], Dw.HINGE - Dw.SCR_H * op + 12])
    poke = wrist_for_tip((688, 1098), (1, .1))
    wn, wf, hn, hf = type_pose(t, clamp((t - 1.2) / .4))
    if t < .45:
        w = lid_top
        hn = dict(kind="open", flip=-1, dir=(.3, -1), curl=(.5, .5, .5, .5), spread=.1, thumb=.5, bend=.05)
    elif t < .85:
        u = ease_io((t - .45) / .4)
        w = lerp2(lid_top, poke, u)
        hn = dict(kind="open", flip=-1, dir=(lerp(.3, 1, u), lerp(-1, .1, u)), curl=(0, .95 * u + .5 * (1 - u), .95 * u + .5 * (1 - u), .9 * u + .5 * (1 - u)),
                  spread=.05, thumb=.85, bend=.05)
    elif t < 1.3:
        u = ease_io((t - .85) / .45)
        press = 1 - smooth(0, .15, t - .85 - .12) * 0 - clamp((t - .95) / .1) * 0
        w = lerp2(poke + np.array([10 * math.sin(math.pi * clamp((t - .85) / .15)), 0]), wn, u)
        dr = (lerp(1, 1, u), lerp(.1, .55, u))
        c = lerp(.95, .45, u)
        hn = dict(kind="open", flip=-1, dir=dr, curl=(0, c, c, c - .05), spread=.05, thumb=lerp(.85, .35, u), bend=.05)
    else:
        w = wn
    return op, w, wf, hf, hn


LID_GRAB = (Dw.LX0 + 30, 0)


def s01(t):
    cam = s01_cam(t)
    set_ink(cam[2])
    op, wn, wf, hf, hn = s01_pose(t)
    arms = {"n": ("ik", tuple(wn), -1), "f": ("ik", tuple(wf), -1)}
    ex = dict(lid=.6, look=(.75, .3), brows="calm", mouth="smile", smile=.7, closed=blink_at(t, 1.25))
    dm = dima(t, lean=.16 + .02 * osc(t, .8), arms=arms, hands={"n": hn, "f": hf}, expr=ex, head_ang=.08 + .02 * osc(t, 1.1))
    press = clamp((t - .88) / .08) * (1 - clamp((t - 1.0) / .1)) + (1 if t > 1.0 else 0)
    scr = Dw.screen_timer(t, press=1.0 if t > .9 else 0.0, btn="СТАРТ" if t < .9 else "ИДЁТ", ring=1.0 if t < .9 else 1 - .02 * (t - .9))
    w = base_world(t, 0.0, (14, 0), op, scr, MUG_DAY, steam_at=900)
    return compose(w + layers(dm), cam, 0.0)


# ═════════════════════════ s02: крупно таймер «20 мин», Дима кивает и склоняется, золотой свет ═════════════════════════
def s02(t):
    u = lerp(.05, .5, ease_io(clamp((t - 1.3) / 2.86)))
    k = clamp((t - 1.3) / 2.86)
    hit = ease_out(clamp((t - T_20) / .18), 3)
    settle = ease_io(clamp((t - 2.0) / .7))
    out_ = ease_io(clamp((t - T_SEL) / .5))
    s = 1.8 + .1 * k + 0.7 * hit - .05 * settle - .12 * out_
    cx = lerp(600, 650, hit) - 10 * out_
    cy = lerp(1050, 1100, hit)
    cam = (cx, cy, s, -.6 * hit + .5 * out_ - .3 * k)
    set_ink(s)
    nod = bump(t, T_20 + .05, .55)
    lean = .16 + .02 * osc(t, .8) + .1 * ease_io(clamp((t - T_SEL) / .35))
    amt = clamp((t - T_SEL - .1) / .3) * .9 + .15
    wn, wf, hn, hf = type_pose(t, amt)
    arms = {"n": ("ik", tuple(wn), -1), "f": ("ik", tuple(wf), -1)}
    ex = dict(lid=.7, look=(.75, .3), brows="up" if hit > .2 and t < T_SEL else "calm", mouth="grin" if t < T_SEL else "smile",
              open=.6, smile=.8, closed=blink_at(t, 3.3))
    dm = dima(t, lean=lean, arms=arms, hands={"n": hn, "f": hf}, expr=ex, head_ang=.08 + .2 * nod - .03 * osc(t, 1.1), head_off=(0, 6 * nod))
    pop = bump(t, T_20, .45)
    ring = 1 - .02 * (t - .9)
    timer = Dw.screen_timer(t, pill_pop=pop, press=1.0, btn="ИДЁТ", ring=ring)
    doc = Dw.screen_doc(t, lines=clamp((t - T_SEL) * 2.4, 0, 20), chip="20:00")
    a = clamp((t - T_SEL) / .05)
    scr = timer if a <= 0 else timer + f'<g opacity="{a:.3f}">{doc}</g>'
    w = base_world(t, u, (14, 10) if t < 3 else (14, 20), 1.0, scr, MUG_DAY, steam_at=900)
    return compose(w + layers(dm), cam, u)


# ═════════════════════════ s06: ночь, 23:10, три кружки; роняет голову на ладонь на «сидел» ═════════════════════════
def chin_target(dm_head, lean, ha, off=(0, 0)):
    a = lean * .5 + ha
    c, s_ = math.cos(a), math.sin(a)
    lx, ly = 26.0, 78.0
    return np.array([dm_head[0] + (lx * c - ly * s_) * BS, dm_head[1] + (lx * s_ + ly * c) * BS])


def s06(t):
    u = 1.0
    drop = ease_in(clamp((t - T_SIDEL + .1) / .32), 2)
    hit = bump(t, T_SIDEL, .3)
    cam = (650 + 14 * ease_io(clamp((t - 8.2) / 1.8)), 1030, 1.5 + .12 * ease_io(clamp((t - 8.2) / 1.8)) + .05 * hit, 1.0 * hit * osc(t, 9))
    set_ink(cam[2])
    lean = lerp(.16, .3, drop) + .015 * osc(t, .6)
    ha = lerp(.1 + .03 * osc(t, .7), .42, drop)
    off = (0, 14 * drop)
    wn, wf, hn, hf = type_pose(t, (1 - drop) * .5)
    # подбородок: сначала считаем голову с прежними руками, потом ведём ближнюю руку под щёку
    ex = dict(lid=lerp(.42, .12, drop), look=(.6, .55), brows="tired", mouth="flat", red=1.0, closed=blink_at(t, 8.45, .22) + .85 * drop,
              hair=3 * hit * osc(t, 8))
    d0 = dima(t, lean=lean, arms=arms_from(wn, wf), hands={"n": hn, "f": hf}, expr=ex, head_ang=ha, head_off=off)
    chin = chin_target(d0["head"], lean, ha)
    dd = np.array([.35, -1.0])
    dd /= np.linalg.norm(dd)
    palm = wrist_for_tip(chin + dd * 70 * BS * 0 + np.array([6, -10 * BS]), dd)
    wn2 = lerp2(wn, palm, drop)
    hn2 = dict(kind="open", flip=-1, dir=(lerp(1, dd[0], drop), lerp(.55, dd[1], drop)), curl=(.35, .4, .45, .45), spread=.1, thumb=.4, bend=.1)
    dm = dima(t, lean=lean, arms=arms_from(wn2, wf), hands={"n": hn2, "f": hf}, expr=ex, head_ang=ha, head_off=off)
    lines_n = 15 + t * .3
    scr = Dw.screen_doc(t, lines=lines_n, chip="0:00" if int(t * 2) % 2 == 0 else "0:00", chip_col="#ff6b6b", scroll=(lines_n - 7) * 16)
    w = base_world(t, u, (23, 10), 1.0, scr, MUG_NIGHT, balls=[(715, 3), (1020, 5)], sheets=[(900, 4, 1), (960, -6, 2)])
    return compose(w + layers(dm), cam, u, front=screen_glow(u))


# ═════════════════════════ s07: кот на стойке смотрит в камеру, наклон на «почему», лапа на «успеем» ═════════════════════════
def s07(t):
    u = 1.0
    k = ease_io(clamp((t - 9.64) / 2.56))
    cam = (1060 - 10 * k, 1085 + 6 * k, 1.75 + .12 * k, -.5 + .5 * k + .3 * osc(t, .4))
    set_ink(cam[2])
    tilt = 15 * ease_out(clamp((t - T_POCHEMU) / .28), 3) * (1 - .0 * ease_io(clamp((t - 11.2) / .6)))
    tilt = tilt * (1 - .45 * ease_io(clamp((t - 11.3) / .5)))
    paw = ease_io(clamp((t - (T_USPEEM - .25)) / .3))
    st = dict(look=(0.0, .1), blink=blink_at(t, 9.95, .2) + blink_at(t, 11.4, .2), tilt=tilt, ear=-9 * bump(t, 10.7, .4), tail=5 * osc(t, .5),
              paw=paw, wave=osc(t, 4.0) * paw, flame_e=1.0)
    cat = Cat.draw(CATX, 1238, CATK, st, t)
    # Дима сзади (размыт): сидит над ноутбуком, подперев голову
    hip = (1010.0, 1262.0)
    ex = dict(lid=.15, look=(.4, .6), brows="tired", mouth="flat", red=1.0, closed=.7)
    dd = np.array([.35, -1.0])
    dd /= np.linalg.norm(dd)
    d0 = dima(t, hip=hip, lean=.3, arms={"n": ("ang", .3, .4), "f": ("ang", .2, .3)}, hands={"n": dict(kind="none"), "f": dict(kind="none")}, expr=ex,
              head_ang=.42, head_off=(0, 14))
    chin = chin_target(d0["head"], .3, .42)
    palm = wrist_for_tip(chin + np.array([6, -6]), dd)
    dm = dima(t, hip=hip, lean=.3, arms={"n": ("ik", tuple(palm), -1), "f": ("ang", .2, .3)},
              hands={"n": dict(kind="open", flip=-1, dir=tuple(dd), curl=(.35, .4, .45, .45), spread=.1, thumb=.4, bend=.1), "f": dict(kind="none")},
              expr=ex, head_ang=.42, head_off=(0, 14))
    back = f'<g {lib.blur(7)}>{layers(dm)}</g>'
    scr = Dw.screen_doc(t, lines=17, chip="0:00", chip_col="#ff6b6b", scroll=160)
    room = Dw.room(t, u, (23, 10), MUG_NIGHT, [(715, 3)], [(900, 4, 1)])
    w = room + Dw.laptop(1.0, scr) + back + cat
    return compose(w, cam, u, front=screen_glow(u, .7))


# ═════════════════════════ s16: закрывает ноутбук, потягивается; кот сворачивается и засыпает на «кот» ═════════════════════════
def s16(t):
    u = 0.0
    ww = whip_in(t, 31.92, .2)
    k = ease_io(clamp((t - 31.72) / 2.3))
    cam = (730 + 160 * ww - 10 * k, 930 + 20 * k, 1.2 + .1 * k + .05 * bump(t, T_KOT_SPIT, .4), .4 - .5 * k)
    set_ink(cam[2])
    close = ease_io(clamp((t - 32.3) / .45))
    op = 1.0 - close
    lid_top_y = Dw.HINGE - Dw.SCR_H * op + 10
    hand_lid = np.array([Dw.LX0 + 30, lid_top_y])
    stretch = ease_io(clamp((t - 32.85) / .5)) * (1 - ease_io(clamp((t - 33.45) / .45)))
    amt = (1 - clamp((t - 32.0) / .25)) * 1.0
    wn, wf, hn, hf = type_pose(t, amt)
    reach = ease_io(clamp((t - 32.15) / .2)) * (1 - ease_io(clamp((t - 32.75) / .2)))
    wn2 = lerp2(wn, hand_lid, reach)
    hn2 = dict(kind="open", flip=-1, dir=(.3, -1), curl=(.5, .5, .5, .5), spread=.1, thumb=.5, bend=.05)
    hnn = hn2 if reach > .3 else hn
    arms = {"n": ("ik", tuple(wn2), -1), "f": ("ik", tuple(wf), -1)}
    hands = {"n": hnn, "f": hf}
    if stretch > .02:
        th = lerp(.2, 2.75, stretch)
        arms = {"n": ("ang", th + .15, .15 * stretch), "f": ("ang", th - .1, .2 * stretch)}
        op_h = dict(kind="open", flip=-1, dir=(.25, -1), curl=(.2, .2, .2, .25), spread=.25, thumb=.2)
        hands = {"n": op_h, "f": op_h}
    ex = dict(lid=lerp(.6, .25, stretch), look=(.7, .3), brows="calm", mouth="talk" if stretch > .3 else "smile", open=.9 * stretch, smile=.8,
              closed=blink_at(t, 32.6) + .9 * stretch)
    dm = dima(t, lean=lerp(.16, -.1, stretch), arms=arms, hands=hands, expr=ex, head_ang=lerp(.08, -.22, stretch))
    sl = ease_io(clamp((t - T_KOT_SPIT) / 1.1))
    blink = ease_io(clamp((t - T_KOT_SPIT) / .8))
    st = dict(look=(-.4, .2), blink=blink, tilt=4 * osc(t, .4) * (1 - sl), tail=4 * osc(t, .5), sleep=sl, flame_e=lerp(1.0, .55, sl), ear=-6 * bump(t, 32.2, .3))
    cat = Cat.draw(CATX2, 1238, CATK, st, t)
    scr = Dw.screen_doc(t, lines=20, chip="ГОТОВО", chip_col="#7fd28a", scroll=220)
    w = Dw.room(t, u, (15, 0), MUG_FAR, [], []) + Dw.laptop(op, scr) + cat + layers(dm)
    return compose(w, cam, u)


# ═════════════════════════ s17: кот спит, Z-шки; Дима улыбается; плашка комментария «КОТ» ═════════════════════════
def zzz(x, y, t):
    o = []
    for j in range(3):
        ph = (t * .55 + j / 3) % 1
        sz = 36 + 40 * ph
        a = math.sin(math.pi * ph)
        cx, cy = x + 50 * ph + 14 * math.sin(ph * 6 + j), y - 190 * ph
        o.append(f'<text x="{cx:.1f}" y="{cy:.1f}" font-family="IDB" font-size="{sz:.1f}" fill="#f6f1e3" stroke="{INK}" stroke-width="5" '
                 f'paint-order="stroke" opacity="{a:.3f}">Z</text>')
    return "".join(o)


def plaque(t, t0):
    """Плашка комментария влетает снизу справа с поворотом и перелётом (экранные координаты)."""
    e = t - t0
    if e < 0:
        return ""
    u = clamp(e / .42)
    pos = back_out(u, 2.0)
    cx = lerp(1180, 540, pos)
    cy = lerp(980, 520, pos) + 6 * osc(t, .7) * u
    ang = lerp(24, -3.5, pos)
    sc = lerp(.55, 1.0, ease_out(u)) * (1 + .06 * bump(t, t0 + .35, .3))
    old = lib.INK_K[0]
    lib.INK_K[0] = 1.0
    card = shape(lib_rr(-380, -110, 380, 110, 44), "#fffaf0", blob(lib_rr(-380, 40, 380, 110, 30), "#efe6d2", .9), w=6, seed=4001)
    tail = shape([(-250, 100, 1), (-300, 170, 1), (-180, 108, 1)], "#fffaf0", "", w=5, seed=4002)
    av = shape(ellipse_pts(-300, -10, 60, 60, 20), "#3a3646", blob(ellipse_pts(-292, 8, 44, 40, 14), "#211e29", .5), w=5, seed=4003)
    av += shape([(-340, -50, 1), (-334, -92, 1), (-308, -62, 1)], "#3a3646", "", w=4, seed=4004)
    av += shape([(-262, -52, 1), (-270, -92, 1), (-292, -62, 1)], "#3a3646", "", w=4, seed=4005)
    av += f'<ellipse cx="-322" cy="-14" rx="11" ry="14" fill="#a9d84a"/><ellipse cx="-278" cy="-14" rx="11" ry="14" fill="#a9d84a"/>'
    av += f'<ellipse cx="-322" cy="-14" rx="4" ry="11" fill="#0b0a10"/><ellipse cx="-278" cy="-14" rx="4" ry="11" fill="#0b0a10"/>'
    name = (f'<text x="-210" y="-48" font-family="IDB" font-size="34" fill="#8a8374" font-weight="700">ты</text>'
            f'<text x="-210" y="52" font-family="IDB" font-size="118" fill="#2a2740" font-weight="900" letter-spacing="4">КОТ</text>')
    pop = back_out(clamp((e - .12) / .3), 2.2)
    heart = (f'<g transform="translate(288 10) scale({pop:.3f})">'
             + shape([(0, 30, 1), (-40, -6), (-40, -34), (-20, -50), (0, -30), (20, -50), (40, -34), (40, -6)], "#ee5a5a",
                     blob([(8, -30), (28, -44), (38, -30), (36, -12)], "#ff9a9a", .8), w=5, seed=4006) + '</g>')
    lib.INK_K[0] = old
    return (f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({ang:.2f}) scale({sc:.3f})">'
            f'<g transform="translate(14 18)" opacity=".25">{lib.blob(lib_rr(-380, -110, 380, 110, 44), "#000000")}</g>{tail}{card}{av}{name}{heart}</g>')


def lib_rr(x0, y0, x1, y1, r):
    return lib.rect_pts(x0, y0, x1, y1, r)


def s17(t):
    u = 0.0
    k = ease_io(clamp((t - 33.61) / 2.6))
    cam = (700 - 10 * k, 1020, 1.3 + .08 * k, -.4 + .6 * k)
    set_ink(cam[2])
    hit = bump(t, T_NAPISHI, .3)
    ex = dict(lid=.7, look=(.2, .15), brows="up" if hit > .1 else "calm", mouth="grin", open=.5, smile=1.0, closed=blink_at(t, 34.7))
    dm = dima(t, lean=.05 + .01 * osc(t, .6), arms={"n": ("ang", .22, .3), "f": ("ang", .18, .3)},
              hands={"n": dict(kind="open", flip=-1, dir=(.1, 1), curl=(.3, .35, .4, .45), spread=.1, thumb=.4),
                     "f": dict(kind="open", flip=-1, dir=(.1, 1), curl=(.3, .35, .4, .45), spread=.1, thumb=.4)},
              expr=ex, head_ang=-.05 + .03 * osc(t, .9), hood=2 * hit)
    st = dict(look=(0, 0), blink=1.0, tilt=0, tail=2 * osc(t, .4), sleep=1.0, flame_e=.5, ear=-4 * bump(t, 34.4, .4))
    cat = Cat.draw(CATX2, 1238, CATK, st, t)
    z = zzz(CATX2 + 40, 1238 - 300 * CATK + 40, t)
    scr = Dw.screen_doc(t, lines=20, chip="ГОТОВО", chip_col="#7fd28a", scroll=220)
    w = Dw.room(t, u, (15, 0), MUG_FAR, [], []) + Dw.laptop(0.0, scr) + cat + layers(dm) + z
    return compose(w, cam, u, over=plaque(t, T_NAPISHI))


# ═════════════════════════ s18: петля — Дима снова открывает ноутбук, на экране «20:00», часы 14:00 ═════════════════════════
def s18(t):
    u = 0.0
    a = 35.8
    k = ease_io(clamp((t - a) / (37.9 - a)))
    c0, c1 = (720.0, 1090.0, 2.2, 0.0), s01_cam(0.0)
    cam = tuple(lerp(c0[i], c1[i], k) for i in range(4))
    set_ink(cam[2])
    op = .55 * ease_io(clamp((t - 35.9) / 1.9))
    lid_top = np.array([Dw.LX0 + 30, Dw.HINGE - Dw.SCR_H * op + 12])
    wn, wf, hn, hf = type_pose(t, 0.0)
    wn = lerp2(lid_top, lid_top, 0)
    arms = {"n": ("ik", tuple(lid_top), -1), "f": ("ik", tuple(wf), -1)}
    hn = dict(kind="open", flip=-1, dir=(.3, -1), curl=(.5, .5, .5, .5), spread=.1, thumb=.5, bend=.05)
    hands = {"n": hn, "f": hf}
    ex = dict(lid=.6, look=(.75, .3), brows="calm", mouth="smile", smile=.7, closed=blink_at(t, 36.9))
    dm = dima(t, lean=.16 + .02 * osc(t, .8), arms=arms, hands=hands, expr=ex, head_ang=.08 + .02 * osc(t, 1.1))
    st = dict(look=(0, 0), blink=1.0, tilt=0, tail=2 * osc(t, .4), sleep=1.0, flame_e=.5)
    cat = Cat.draw(CATX, 1238, CATK, st, t)
    scr = Dw.screen_timer(t, press=0.0, btn="СТАРТ")
    w = Dw.room(t, u, (14, 0), MUG_DAY[:1], [], [], steam_at=900) + Dw.laptop(op, scr) + cat + layers(dm) + zzz(CATX + 40, 1238 - 300 * CATK + 40, t)
    return compose(w, cam, u)


SHOTS = {"s01": s01, "s02": s02, "s06": s06, "s07": s07, "s16": s16, "s17": s17, "s18": s18}


def frame(sid, t):
    lib.DEFS.clear()
    return SHOTS[sid](t)
