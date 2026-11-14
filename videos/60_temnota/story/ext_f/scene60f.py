"""Рилс 60 «темнота», группа F: s15 (подоконник), s16 (кот крупно), s17 (призыв, рукописное «кот»).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Слова — voice/words.json."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
for d in (os.path.join(STORY, "common"), os.path.join(STORY, "..", "..", "59_podarok", "story", "common")):
    if os.path.isdir(d):
        sys.path.insert(0, d)
import cat as Cat  # noqa: E402
import catf  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import room  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, rrect, shape  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
WI = {}
for i_, w_ in enumerate(WORDS):
    WI.setdefault(w_["word"].strip(".,!?").lower(), []).append(i_)


def wt(word, k=0):
    return WORDS[WI[word][k]]["start"]


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if (u <= 0 or u >= 1) else math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


# ═══════════════════════════════ s16: кот крупно ═══════════════════════════════
T_HOTYA, T_NE, T_NUZH = wt("хотя"), wt("не", 1), wt("нужно")


def lazy_blink(t, a, dur=.42):
    """Ленивое моргание: веки опускаются медленно, на секунду замирают и поднимаются."""
    u = (t - a) / dur
    if not 0 < u < 1:
        return 0.0
    return math.sin(math.pi * u) ** .6 if u < .5 else math.sin(math.pi * u) ** 1.4


def wall_window(t, z):
    """Тёплая стена вечера, слева окно с синим вечерним светом, внизу доска подоконника (кот сидит на ней)."""
    o = []
    g = lib.lin_grad([(0, "#e3d6bb", 1), (1, "#d6c4a2", 1)])
    o.append(f'<rect x="-900" y="-900" width="3200" height="3600" fill="url(#{g})"/>')
    # окно: синий вечер, перекрестье рамы
    wx0, wy0, wx1, wy1 = -330, 330, 300, 1300
    gg = lib.lin_grad([(0, "#6f88b5", 1), (.55, "#a9bddb", 1), (1, "#d9cfc0", 1)])
    o.append(shape(rrect(wx0 - 34, wy0 - 34, wx1 + 34, wy1 + 34, 8), "#f1eadb", w=5, seed=601))
    o.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="url(#{gg})"/>')
    for (x, y, r) in [(-200, 420, 4), (-60, 380, 3), (140, 500, 4), (-240, 600, 3)]:
        o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff6d8" opacity=".85"/>')
    o.append(blob(ellipse_pts(110, 560, 64, 64, 14), "#fff3cf", .95))
    o.append(blob(ellipse_pts(136, 552, 56, 60, 14), "#a9bddb", 1))
    o.append(f'<rect x="{wx0}" y="{(wy0 + wy1) // 2 - 7}" width="{wx1 - wx0}" height="14" fill="#f1eadb"/>')
    o.append(f'<rect x="-14" y="{wy0}" width="28" height="{wy1 - wy0}" fill="#f1eadb"/>')
    o.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="none" stroke="{INK}" stroke-width="4"/>')
    # свет окна на стене
    o.append(blob([(330, 300), (900, 360), (1000, 1200), (330, 1180)], "#aebfdc", .22))
    # подоконник — доска, на ней сидит кот
    top = [(-900, 1306), (1900, 1306), (1900, 1380), (-900, 1380)]
    o.append(shape(top, "#b98a5c", blob([(-900, 1344), (1900, 1344), (1900, 1380), (-900, 1380)], "#8d6440"), w=5, seed=605))
    o.append(blob([(-900, 1306), (1900, 1306), (1900, 1318), (-900, 1318)], "#d6a878"))
    o.append(blob([(-900, 1380), (1900, 1380), (1900, 1700), (-900, 1700)], "#cdbd9c"))
    return "".join(o)


def frame16(t):
    # кот крупно: поворот от окна к зрителю, ленивое моргание, зевок, довольный прищур
    turn_u = sm(t, 26.55, 27.15)
    turn = -1.0 * (1 - turn_u)
    look = (-1.0 * (1 - turn_u) + .0 * turn_u, -.25 * (1 - turn_u))
    blink = lazy_blink(t, T_HOTYA - .05, .46)
    yawn = sm(t, T_NE - .02, T_NE + .2) * (1 - sm(t, T_NE + .36, T_NE + .58))
    happy = sm(t, T_NE + .4, T_NE + .62)
    if yawn > .02:
        happy = max(happy, 0.0)
    if t < T_NUZH + .6:
        eyes_happy = happy * (1 - 0)
    else:
        eyes_happy = happy
    st = dict(turn=turn, look=look, blink=blink, yawn=yawn, happy=eyes_happy if yawn < .3 else 0.0,
              ear=2.5 * math.sin(t * 17) * bump(t, T_NE - .1, .5) + 4 * bump(t, T_HOTYA + .2, .3), perk=.35 * (1 - turn_u),
              tilt=-5 * (1 - turn_u) + 3 * math.sin(t * 1.4) + 5 * bump(t, T_NUZH, .5), drop=-.12 * yawn + .03 * bump(t, T_NUZH, .4),
              tail=10 * math.sin(t * 2.2) + 5 * bump(t, 27.4, .5), flame_e=1.1 + .5 * bump(t, T_NUZH, .5), smile=happy)
    z = 1.0 + .26 * sm(t, 26.7, 28.6)
    set_ink(z * 2.9)
    body = wall_window(t, z)
    ck = 2.9
    cxs, cys = 395 + 8 * math.sin(t * 1.1), 1480
    sq = 1 + .02 * bump(t, T_NE, .5)
    body += catf.draw2(cxs, cys, ck * sq, st, t)
    fx, fy = 395 + (180 + 28) * 0, 0
    cam_cx = 560 + 30 * sm(t, 26.7, 28.6) + (-60) * 0
    cam_cy = 960 + (-40) * sm(t, 26.7, 28.6)
    cam = lib.cam(cam_cx, cam_cy, z, 1.2 * math.sin(t * 1.3) - 2.0 * bump(t, T_NE, .5) + 1.4 * bump(t, T_NUZH, .3))
    return f'<g transform="{cam}">{body}</g>'


# ═══════════════════════════════ s15: подоконник, Дима и кот спиной ═══════════════════════════════
T_KOT15, T_OKNO = wt("кот"), wt("окно")
DP = people.PAL["dima"]
SILL_TOP = room.WIN[3] + 18          # верх доски подоконника (мир)
CAT_K15 = .56


def dima_back(t, turn=0.0):
    """Взрослый Дима со спины у окна: горчичное худи с капюшоном, лохматый затылок, локти на подоконнике. turn 0..1 — голова к коту (вправо)."""
    o = []
    hx, hy = 676 + 14 * turn, 902 + 2 * math.sin(t * 1.7)
    br = 3 * math.sin(t * 2 * math.pi / 3.4)
    # руки: плечо → локоть на подоконнике (предплечья лежат на доске, уходят от нас)
    for sx, sd in ((-1, 501), (1, 502)):
        sh = (676 + sx * 128, 1050 + br)
        el = (676 + sx * 176, SILL_TOP + 8)
        arm = [(sh[0] - 46, sh[1] - 8), (sh[0] + 40, sh[1] - 14), (el[0] + 38 * (1 if sx > 0 else .7), el[1] - 10), (el[0] + 22, el[1] + 30),
               (el[0] - 24, el[1] + 34), (el[0] - 40 * (1 if sx < 0 else .7), el[1])]
        o.append(shape(arm, DP["TOP"], blob([(el[0] + sx * 6, sh[1]), (el[0] + sx * 60, sh[1]), (el[0] + sx * 60, el[1] + 40), (el[0] + sx * 10, el[1] + 40)],
                                         DP["TOP_SH"], .8) + line([(el[0] - 16, el[1] + 4), (el[0] + 14, el[1] + 10)], 2.6, DP["FOLD"], seed=sd + 9, op=.7),
                       w=5, seed=sd))
    # спина худи
    bk = [(548, 1074 + br), (600, 1034 + br), (752, 1034 + br), (804, 1074 + br), (826, 1220), (838, 1500), (514, 1500), (526, 1220)]
    inner = blob([(700, 1030), (840, 1060), (850, 1500), (720, 1500), (730, 1200)], DP["TOP_SH"], .75)
    inner += line([(600, 1260), (640, 1330), (630, 1420)], 3, DP["FOLD"], seed=511, op=.6)
    inner += line([(760, 1250), (742, 1340)], 3, DP["FOLD"], seed=512, op=.6)
    o.append(shape(bk, DP["TOP"], inner, w=5.4, seed=510))
    # капюшон лежит на спине
    hood = [(588, 1040 + br), (676, 1022 + br), (764, 1040 + br), (750, 1130 + br), (676, 1170 + br), (602, 1130 + br)]
    o.append(shape(hood, DP["TOP"], blob([(676, 1020), (780, 1040), (770, 1180), (690, 1180)], DP["TOP_SH"], .7) +
                   line([(612, 1060 + br), (676, 1138 + br), (740, 1060 + br)], 3, DP["TOP_SH2"], seed=515, op=.9), w=5, seed=514))
    # шея
    o.append(shape([(640, 1000), (712, 1000), (716, 1046 + br), (636, 1046 + br)], DP["SKIN_SH"], w=4, seed=516))
    # уши
    for sx, sd in ((-1, 520), (1, 521)):
        ex = hx + sx * 92 - 6 * turn * (1 if sx > 0 else -1)
        o.append(shape(ellipse_pts(ex, hy + 18, 20, 30, 10, rot=sx * 12), DP["SKIN"], blob(ellipse_pts(ex + sx * 4, hy + 20, 9, 16, 8), DP["SKIN_SH"], .8),
                       w=4, seed=sd))
    # щека видна при повороте головы к коту
    if turn > .05:
        o.append(shape([(hx + 66, hy + 20), (hx + 92, hy + 40), (hx + 86, hy + 90), (hx + 62, hy + 100)], DP["SKIN"], w=4, seed=523))
    # затылок: волосы лохматые
    hair = [(hx - 92, hy + 40), (hx - 104, hy - 10, 1), (hx - 90, hy - 60), (hx - 110, hy - 92, 1), (hx - 62, hy - 96), (hx - 64, hy - 136, 1), (hx - 20, hy - 112),
            (hx + 4, hy - 150, 1), (hx + 30, hy - 112), (hx + 70, hy - 132, 1), (hx + 76, hy - 92), (hx + 112, hy - 84, 1), (hx + 98, hy - 40),
            (hx + 106, hy + 6, 1), (hx + 88, hy + 48), (hx + 60, hy + 82), (hx + 30, hy + 74, 1), (hx + 10, hy + 100), (hx - 18, hy + 76, 1),
            (hx - 44, hy + 98), (hx - 60, hy + 70, 1)]
    hi = "".join(line(p, 3, DP["HAIR_HI"], seed=530 + i, op=.85) for i, p in enumerate([
        [(hx - 50, hy - 70), (hx - 30, hy - 20)], [(hx + 10, hy - 90), (hx + 16, hy - 40)], [(hx + 52, hy - 60), (hx + 44, hy - 10)], [(hx - 70, hy + 10), (hx - 56, hy + 50)]]))
    hi += "".join(line(p, 2.6, DP["HAIR_SH"], seed=540 + i) for i, p in enumerate([
        [(hx - 20, hy - 40), (hx - 10, hy + 20)], [(hx + 30, hy - 30), (hx + 24, hy + 30)], [(hx - 60, hy - 30), (hx - 48, hy + 10)]]))
    o.append(shape(hair, DP["HAIR"], blob([(hx + 20, hy - 140), (hx + 120, hy - 80), (hx + 110, hy + 60), (hx + 40, hy + 90)], DP["HAIR_SH"], .6) + hi,
                   w=5.2, seed=528))
    return "".join(o)


def cat15(t):
    """Кот: идёт по полу к окну, приседает, на «кот» прыгает (толчок, дуга, лапы вытянуты), приземляется с осадкой, садится и смотрит в окно."""
    x_floor0, x_floor1 = 1050.0, 952.0
    xs, ys = 952.0, room.FL - 6
    xe, ye = 884.0, SILL_TOP + 2
    tj0, tj1 = T_KOT15 - .02, T_KOT15 + .30
    st = dict(tail=6 * math.sin(t * 2.0), flame_e=1.0, ear=0.0)
    if t < 24.98:          # шаги
        u = clamp((t - 24.6) / .38)
        x = x_floor0 + (x_floor1 - x_floor0) * u
        y = ys - 6 * abs(math.sin(t * 2 * math.pi * 2.2))
        st.update(walk=t * 2.2, rot=2.5 * math.sin(t * 2 * math.pi * 2.2), head_dy=4 * math.sin(t * 2 * math.pi * 4.4))
        k = CAT_K15
    elif t < tj0:          # присед перед прыжком: голова вниз, тело сжато
        u = ease_out(clamp((t - 24.98) / (tj0 - 24.98)))
        x, y = x_floor1, ys
        st.update(sx=1 + .1 * u, sy=1 - .2 * u, head_dy=24 * u, tail=-14 * u)
        k = CAT_K15
    elif t < tj1:          # полёт по дуге
        u = (t - tj0) / (tj1 - tj0)
        x = xs + (xe - xs) * u
        apex = ye - 70
        # квадратичная дуга через (0, ys), (.62, apex), (1, ye)
        a0, a1, a2 = ys, apex, ye
        um = .62
        L0 = (u - um) * (u - 1) / ((0 - um) * (0 - 1))
        L1 = (u - 0) * (u - 1) / ((um - 0) * (um - 1))
        L2 = (u - 0) * (u - um) / ((1 - 0) * (1 - um))
        y = a0 * L0 + a1 * L1 + a2 * L2
        str_ = math.sin(math.pi * clamp(u * 1.1))
        st.update(sx=1 - .12 * str_, sy=1 + .22 * str_, legs=clamp(1.6 * str_), head_dy=-10 * str_, rot=-8 * math.sin(math.pi * u), tail=-30 * str_ + 10)
        k = CAT_K15
    else:                  # приземление: осадка и пружина
        e = t - tj1
        sq = math.exp(-7 * e) * math.cos(2 * math.pi * 2.6 * e)
        x, y = xe, ye
        st.update(sx=1 + .12 * sq, sy=1 - .2 * sq, head_dy=14 * max(0, sq), tail=10 * sq + 5 * math.sin(t * 2.0))
        k = CAT_K15
    # «окно»: хвост качнулся, огонёк вспыхнул
    st["tail"] += 22 * bump(t, T_OKNO - .05, .55) - 8 * bump(t, T_OKNO + .4, .5)
    st["flame_e"] = 1.0 + 1.6 * bump(t, T_OKNO - .05, .55)
    st["ear"] = 10 * bump(t, T_OKNO + .2, .25) + 8 * bump(t, 26.5, .25)
    st["head_dx"] = st.get("head_dx", 0.0) + (-10 * sm(t, 25.9, 26.5))
    st["tilt"] = -4 * sm(t, 25.9, 26.5)
    return x, y, k, st


def frame15(t):
    o = [room.wall_floor(), room.window_view(t, par=.12 * sm(t, 24.7, 27.1)), room.window_frame(t, curtains=True, plant=True)]
    x, y, k, st = cat15(t)
    # тень кота на полу/подоконнике
    gy = room.FL if t < T_KOT15 + .1 else SILL_TOP + 4
    hh = abs(gy - y)
    o.append(blob(ellipse_pts(x + 6, gy + 2, 110 * k * max(.4, 1 - hh / 500), 10, 12), "#3a2a1e", .28))
    o.append(dima_back(t, turn=sm(t, 26.1, 26.6)))
    o.append(catf.draw_back(x, y, k, st, t))
    u = sm(t, 24.7, 27.1)
    z = 1.12 + .3 * u
    cx = 640 + 170 * u
    cy = 1090 - 150 * u
    set_ink(z)
    cam = lib.cam(cx, cy, z, .8 - 1.6 * u)
    return f'<g transform="{cam}">{"".join(o)}</g>'


FRAMES = {"s15": frame15, "s16": frame16}


def frame(sid, t):
    lib.dyn_begin()
    body = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#d9c9a8"/>{body}')
