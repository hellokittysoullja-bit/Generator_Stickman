"""Стол Димы рилса 41 «всё в последнюю ночь» (агент A): s01 (хук, ночь, печатает), s05 (кофе и рассвет), s06 (лицо у
экрана, «стыдно»). frame(sid, t) -> SVG 1080×1920, t — общее время ролика; удары — на словах voice/words.json.

Мир — ночная комната рилса 32 (den.py: окно на город, часы, доска, полка, стол с лампой); Дима — people.py (лохматый,
щетина, мешки, горчичное худи) сидит слева лицом вправо; ноутбук — из рилса 30 (экран в 3/4 к Диме и зрителю), на
экране — курсовая: строки растут, ошибки подчёркнуты красной волной. Кружки и рука с кружкой — из рилса 32 (s03).
Окно умеет рассвет (den.window(t, dawn)).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat as Cat  # noqa: E402
import den  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import room  # noqa: E402
from ink import ellipse_pts, fill_d  # noqa: E402
from lib import INK, back_out, blob, clamp, ease_in, ease_io, ease_out, f, line, mix, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["word"].strip(".,?!").lower() == word.lower() and w["start"] >= after - 1e-6:
            return w["start"]
    raise KeyError(word)


T_DIMA = wt("дима")          # 0.16
T_MESYAC = wt("месяц")       # 0.64
T_PISAL = wt("писал")        # 1.12
T_KURS = wt("курсовую")      # 1.44
T_KOFE = wt("кофе")          # 6.40
T_RASSVET = wt("рассвет")    # 6.96
T_TEKST = wt("текст")        # 7.96
T_STYDNO = wt("стыдно")      # 8.72
T_SDAVAT = wt("сдавать")     # 9.12
T_ZNAESH = wt("знаешь")      # 10.08
T_POCHEMU = wt("почему")     # 10.40

den.DESK_X0 = 420.0           # стол ближе к Диме (таз правее, чем в 32)
BS = 0.6
HIP = np.array([300.0, 1262.0])


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def kick(t, t0, dur=.4, freq=2.2):
    u = t - t0
    if u <= 0 or u > dur:
        return 0.0
    return math.exp(-u * 9) * math.cos(2 * math.pi * freq * u)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


def hook_cam(t, hit):
    """Влёт (правила 28–29): 1/1.4 → 1.05 за 0.22 с, отскок к 1, поворот −3.4° → +1° → 0; второй удар +9 % на hit."""
    T = 0.22
    if t < T:
        u = t / T
        z = 1 / 1.4 + (1.055 - 1 / 1.4) * ease_out(u, 3)
        rot = -3.4 * (1 - ease_out(u, 2)) + 1.0 * ease_out(u, 2)
    else:
        u = t - T
        z = 1 + .055 * math.exp(-u * 9) * math.cos(2 * math.pi * 2.2 * u)
        rot = 1.0 * math.exp(-u * 7) * math.cos(2 * math.pi * 1.8 * u)
    z *= 1 + .09 * max(0.0, kick(t, hit, .5, 1.6))
    return z, rot


def blur_px(t):
    """Размытие влёта (px), пока камера летит."""
    return 6.0 * (1 - smooth(0.0, 0.2, t))


# ═════════════════════════════════════ НОУТБУК (рилс 30, вид 3/4) ═════════════════════════════════════
SW, SH = 780.0, 560.0
SO = np.array([505.0, 830.0])
SX = np.array([336.0, -26.0]) / SW
SY = np.array([8.0, 246.0]) / SH
FWD = np.array([-115.0, 48.0])
LID, LID_SH = "#3b4152", "#2a2f3d"
DECK, DECK_SH2, KEY = "#c9ccd6", "#8d92a3", "#454b5c"


def S2W(p):
    return SO + SX * p[0] + SY * p[1]


def red_wave(x0, x1, y, amp=4.0, per=16.0):
    pts = []
    x = x0
    k = 0
    while x <= x1:
        pts.append(f"{x:.1f} {y + (amp if k % 2 else -amp):.1f}")
        x += per / 2
        k += 1
    return f'<polyline points="{" ".join(pts)}" fill="none" stroke="#e0302a" stroke-width="3.6" stroke-linejoin="round" stroke-linecap="round"/>'


ROWS = [1.0, .93, .97, .58, 1.0, .9, .95, .72, 1.0, .88, .96, .64, .99, .91, .97, .5, 1.0, .93, .9, .7]
ERR = {1: (.15, .55), 2: (.4, .9), 5: (.05, .4), 6: (.5, .95), 9: (.2, .7), 10: (.55, .9), 13: (.1, .5), 14: (.3, .85), 17: (.4, .8)}


def doc_screen(t, chars, errs=1.0, scroll=0.0, glow=1.0):
    """Курсовая в редакторе: синяя шапка, белый лист, строки растут (chars — сколько строк набрано, дробное),
    красные волны под ошибками (errs 0..1 — сколько проявилось), лист уезжает вверх на scroll строк."""
    cid = lib.clip_rect(0, 0, SW, SH)
    o = [f'<g clip-path="url(#{cid})"><rect width="{SW}" height="{SH}" fill="#d9dde6"/>']
    o.append(f'<rect width="{SW}" height="56" fill="#2f63b8"/>')
    for k in range(3):
        o.append(f'<circle cx="{28 + k * 26}" cy="28" r="8" fill="#e8eefb" opacity=".85"/>')
    o.append(f'<text x="{SW / 2:.0f}" y="40" text-anchor="middle" font-family="IDB" font-size="28" fill="#ffffff" letter-spacing="2">КУРСОВАЯ</text>')
    o.append(f'<rect y="56" width="{SW}" height="34" fill="#eef1f6"/>')
    for k in range(6):
        o.append(f'<rect x="{30 + k * 44}" y="66" width="28" height="14" rx="4" fill="#b9c2d3"/>')
    px0, px1 = 120.0, 660.0
    top = 90 + 18 - scroll * 38
    o.append(f'<rect x="{px0}" y="{top - 18:.1f}" width="{px1 - px0}" height="2000" fill="#ffffff"/>')
    o.append(f'<rect x="{px1}" y="{top - 18:.1f}" width="10" height="2000" fill="#c3c8d3"/>')
    for r, wl in enumerate(ROWS):
        y = top + 26 + r * 38
        if y < 70 or y > SH + 20:
            continue
        u = clamp(chars - r)
        full = (px1 - px0 - 70) * wl
        o.append(f'<rect x="{px0 + 35}" y="{y:.1f}" width="{full:.1f}" height="12" rx="6" fill="#f0f0ee"/>')
        if u <= 0:
            continue
        o.append(f'<rect x="{px0 + 35}" y="{y:.1f}" width="{full * u:.1f}" height="12" rx="6" fill="#55585f"/>')
        if r in ERR and errs > 0:
            a, b = ERR[r]
            if u > a:
                xa, xb = px0 + 35 + full * a, px0 + 35 + full * min(b, u)
                e = clamp(errs * 3 - (r % 3) * .5)
                if e > 0 and xb > xa + 8:
                    o.append(f'<g opacity="{e:.3f}">{red_wave(xa, xb, y + 21)}</g>')
        if 0 < u < 1 and (t * 2.5) % 1 < .6:
            o.append(f'<rect x="{px0 + 37 + full * u:.1f}" y="{y - 6:.1f}" width="4" height="24" fill="{INK}"/>')
    o.append(f'<rect width="{SW}" height="{SH}" fill="#c8dcff" opacity="{.06 * glow:.3f}"/>')
    o.append("</g>")
    return "".join(o)


def laptop(scr, sd=1500):
    o = []
    A, B = S2W((0, SH)), S2W((SW, SH))
    o.append(blob([tuple(A + FWD + [0, 10]), tuple(B + FWD + [0, 10]), tuple(B + [20, 14]), tuple(A + [0, 10])], "#2a1a0e", .35, lib.blur(6)))
    deck = [tuple(A) + (1,), tuple(B) + (1,), tuple(B + FWD) + (1,), tuple(A + FWD) + (1,)]
    keys = ""
    for r in range(4):
        for c in range(9):
            u0, u1 = .08 + c * .093, .08 + c * .093 + .08
            v0, v1 = .12 + r * .13, .12 + r * .13 + .1
            q = [A + (B - A) * u + FWD * v for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))]
            keys += f'<path d="{fill_d([tuple(p) + (1,) for p in q])}" fill="{KEY}"/>'
    o.append(shape(deck, DECK, keys, w=4.4, seed=sd + 1))
    o.append(shape([tuple(A + FWD) + (1,), tuple(B + FWD) + (1,), tuple(B + FWD + [0, 12]) + (1,), tuple(A + FWD + [0, 12]) + (1,)], DECK_SH2, "",
                   w=3.6, seed=sd + 2))
    m = 22
    TL, TR, BR, BL = S2W((-m, -m)), S2W((SW + m, -m)), S2W((SW + m, SH + m * .5)), S2W((-m, SH + m * .5))
    o.append(shape([tuple(TR) + (1,), tuple(TR + [16, 6]) + (1,), tuple(BR + [16, 6]) + (1,), tuple(BR) + (1,)], LID_SH, "", w=3.6, seed=sd + 3))
    o.append(shape([tuple(TL) + (1,), tuple(TR) + (1,), tuple(BR) + (1,), tuple(BL) + (1,)], LID, "", w=4.6, seed=sd + 4))
    mtx = f"matrix({SX[0]:.5f} {SX[1]:.5f} {SY[0]:.5f} {SY[1]:.5f} {SO[0]:.3f} {SO[1]:.3f})"
    o.append(f'<g transform="{mtx}">{scr}<rect width="{SW}" height="{SH}" fill="none" stroke="#15171f" stroke-width="5"/></g>')
    return "".join(o)


def screen_light(on=1.0):
    """Холодный свет экрана: на Диму и стол (screen-смешение)."""
    if on <= 0:
        return ""
    c = S2W((SW * .45, SH * .5))
    g = lib.rad_grad([(0, "#9fc4ff", .26 * on), (.5, "#7aa6f0", .1 * on), (1, "#7aa6f0", 0)], c[0] - 170, c[1] - 30, 420, 340)
    return f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def type_targets(t, amp=1.0, rate=1.0):
    A, B = S2W((0, SH)), S2W((SW, SH))
    base_n = A + (B - A) * .26 + FWD * .92
    base_f = A + (B - A) * .46 + FWD * .7
    jn = np.array([10 * math.sin(t * 2.6 * rate), -11 * max(0, math.sin(t * 15.0 * rate)) * amp])
    jf = np.array([10 * math.sin(t * 2.1 * rate + 1), -11 * max(0, math.sin(t * 13.6 * rate + 1.3)) * amp])
    return base_n + jn, base_f + jf


HN = dict(kind="open", flip=1, dir=(.95, -.05), curl=(.35, .4, .45, .5), spread=.08, thumb=.5, bend=.15)
HF = dict(kind="open", flip=1, dir=(.95, -.1), curl=(.35, .4, .45, .5), spread=.08, thumb=.5, bend=.15)


def dima(t, arms, hands=None, expr=None, lean=0.14, head_ang=0.0, head_off=(0, 0)):
    p = dict(hip=tuple(HIP), scale=BS, lean=lean, feet={"n": ((560, 1468), 0.0), "f": ((535, 1462), 0.0)}, arms=arms, hands=hands or {},
             expr=expr or {}, head_ang=head_ang, head_off=head_off, hood=0.0, strings=(2 * osc(t, 1.3), 1.5 * osc(t, 1.1, 1)))
    return people.draw(p, "dima")


# ═════════════════════════════════════ ПРЕДМЕТЫ ═════════════════════════════════════
def crumple(x, y, r, sd, rot=0.0):
    """Скомканный лист: неровный ком, складки, тень (низ-центр x, y)."""
    rs = np.random.RandomState(sd)
    n = 11
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + rot
        rr = r * rs.uniform(.78, 1.08)
        pts.append((x + rr * math.cos(a), y - r * .9 + rr * .86 * math.sin(a), 1 if i % 3 == 0 else 0))
    inner = blob([(x - r * 1.2, y - r * .7), (x + r * 1.2, y - r * .9), (x + r * 1.2, y + r), (x - r * 1.2, y + r)], "#d9d3c4", .9)
    for j in range(4):
        a0 = rs.uniform(0, 6.28)
        p0 = (x + r * .7 * math.cos(a0), y - r * .9 + r * .6 * math.sin(a0))
        p1 = (x + rs.uniform(-.2, .2) * r, y - r * .9 + rs.uniform(-.2, .2) * r)
        p2 = (x + r * .6 * math.cos(a0 + 2.2), y - r * .9 + r * .5 * math.sin(a0 + 2.2))
        inner += line([p0, p1, p2], 2.2, "#a8a091", seed=sd + 10 + j, op=.9)
    o = blob(ellipse_pts(x + 4, y + 2, r * 1.05, r * .22, 12), "#1a100a", .3)
    return o + shape(pts, "#f4f0e6", inner, w=3.4, seed=sd)


def mug(x, y, k, col, fill=None, steam_t=None, ring=True):
    return den.mug(x, y, k, col, fill=fill, steam_t=steam_t, ring=ring and fill is None)


# батарея пустых кружек (s01 — три, s05 — пять + новая)
MUGS_BACK = [(985.0 + 120, 1096.0, .42, "#5f6fa8"), (1170.0, 1104.0, .44, "#8a5a8a")]
MUGS_FRONT = [(712.0, 1138.0, .4, "#c44f3a"), (770.0, 1146.0, .42, "#e0a93a"), (828.0, 1140.0, .4, "#3f7a72")]


def mugs(t, jump=0.0, n_front=3, extra=()):
    o = []
    for i, (x, y, k, c) in enumerate(list(MUGS_BACK) + list(MUGS_FRONT[:n_front]) + list(extra)):
        dy = jump * (8 + 4 * (i % 2))
        o.append(mug(x, y - dy, k, c))
    return "".join(o)


def kw_hand():
    people.C = people.PAL["dima"]
    return dict(shape_fn=people.shape, line_fn=people.line, skin=people.C["SKIN"], skin_sh=people.C["SKIN_SH"], skin_sh2=people.C["SKIN_SH2"])


def grip_mug(mx, my, mk, side=-1):
    kw = kw_hand()
    old = people.LWK
    people.LWK = BS
    try:
        b, fr = Hand.grip((mx, my - 64 * mk), 50 * mk, side, k=BS * 1.05, h=70, seed=2600, **kw)
    finally:
        people.LWK = old
    return b, fr


# ═════════════════════════════════════ МИР ═════════════════════════════════════
def room_back(t, dawn=0.0, clock=(0.0, 0.0)):
    return "".join([den.wall(t), den.window(t, dawn), den.board(t), den.shelf(t), den.clock(clock[0], clock[1], 0.0, 0.0), den.floor()])


def world(t, d, *, dawn=0.0, clock=(0.0, 0.0), scr="", on_desk="", front="", desk_jump=0.0, floor_papers=True, lamp_on=1.0):
    w = [room_back(t, dawn, clock)]
    w.append(room.chair(HIP[0], HIP[1] + 4, 1, 2300))
    w.append(den.desk_back())
    w.append(d.get("legs", ""))
    if floor_papers:
        w.append(crumple(640, 1350, 26, 5101, .4) + crumple(705, 1392, 22, 5102, 1.3) + crumple(560, 1410, 20, 5103, 2.1))
    w.append(den.desk_top())
    dj = f'<g transform="translate(0 {-desk_jump:.2f})">'
    w.append(dj + crumple(1250, 1112, 22, 5104, .2) + crumple(1215, 1140, 18, 5105, 1.0) + "</g>")
    w.append(den.lamp(t, lamp_on))
    w.append(laptop(scr))
    w.append(on_desk)
    w.append(d["arm_f"])
    w.append(d["body"])
    w.append(d["arm_n"])
    w.append(d.get("hand_n", ""))
    w.append(front)
    return "".join(w)


def compose(wrld, cam, *, lamp_on=1.0, scr_on=1.0, dawn=0.0, blur=0.0, extra_front=""):
    cx, cy, s, r = cam
    inner = f'{wrld}{den.lamp_cone(0, lamp_on)}{den.glow(lamp_on * (1 - .5 * dawn))}{screen_light(scr_on)}'
    if dawn > 0:
        g = lib.rad_grad([(0, "#ffb07a", .38 * dawn), (.6, "#ff9a7a", .16 * dawn), (1, "#ff9a7a", 0)], 210, 520, 900, 900)
        inner += f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    night = f'<rect x="-600" y="-600" width="2400" height="3400" fill="#14183a" opacity="{.1 * (1 - .8 * dawn):.3f}"/>'
    g = f'<g transform="{lib.cam(cx, cy, s, r)}">{inner}{night}</g>'
    if blur > .05:
        fid = lib.uid("bl")
        lib.DEFS.append(f'<filter id="{fid}" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="{blur:.2f}"/></filter>')
        g = f'<g filter="url(#{fid})">{g}</g>'
    o = ['<rect width="1080" height="1920" fill="#1c2236"/>', g, extra_front, vignette()]
    return lib.svg("".join(o))


def vignette():
    g = lib.rad_grad([(0, "#0a0c1e", 0), (.6, "#0a0c1e", 0), (1, "#0a0c1e", .45)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


# ═════════════════════════════════════ s01 — хук: ночь, печатает как бешеный ═════════════════════════════════════
def s01(t):
    hit = T_PISAL
    z, rot = hook_cam(t, hit)
    k = clamp(t / 1.7)
    s = 1.42 * z * (1 + .03 * k)
    sh = bump(t, hit, .3)
    cam = (612 - 30 * (1 - z) + 10 * k + 5 * sh * osc(t, 13), 935 + 40 * (1 - z) - 8 * k + 4 * sh * osc(t, 17, 1), s,
           rot + .25 * osc(t, .6) + 1.0 * sh * osc(t, 9))
    set_ink(s)
    # печатает: очень быстро, на «писал» — удар обеими руками по клавишам (рывок вверх и вниз)
    slam = bump(t, hit - .14, .14)
    tn, tf_ = type_targets(t, amp=1.4, rate=1.35)
    tn = tn + np.array([0, -40 * slam])
    tf_ = tf_ + np.array([0, -36 * slam])
    hn = dict(HN, curl=(.3, .35, .4, .45))
    expr = dict(lid=.62 + .2 * bump(t, hit, .3), look=(.62, .22), brows="worry", mouth="flat" if t < hit else "tired",
                closed=blink_at(t, .82, .12), hair=5 * osc(t, 6) + 8 * sh * osc(t, 11), red=1.0)
    lean = .2 + .01 * osc(t, 5.5)
    d = dima(t, {"n": ("ik", tuple(tn), -1), "f": ("ik", tuple(tf_), -1)}, {"n": hn, "f": HF}, expr, lean=lean,
             head_ang=.05 + .025 * osc(t, 3.1) - .04 * sh)
    chars = 2.2 + 3.4 * t + 1.2 * smooth(hit - .05, hit + .1, t)
    scr = doc_screen(t, chars, errs=clamp(t / 1.2), scroll=max(0.0, chars - 8.5))
    jump = bump(t, hit, .24)
    on_desk = mugs(t, jump, 3)
    on_desk += mug(1040.0, 1150.0, .46, "#e2c04a", fill="coffee", steam_t=t)
    w = world(t, d, scr=scr, on_desk=on_desk, desk_jump=10 * jump, clock=(3.0 * 30 + 15 * t, (t * 360 * .2) % 360))
    return compose(w, cam, blur=blur_px(t))


# ═════════════════════════════════════ s05 — «Кофе»: ещё одна кружка; «рассвет»: небо розовеет ═════════════════════════════════════
NEW_MUG = (648.0, 1148.0, .46, "#d8483c")
BATTERY = [(1050.0, 1150.0, .44, "#5f8a5a"), (1112.0, 1142.0, .4, "#c48a3a"), (882.0, 1148.0, .42, "#6a6fb0")]


def mug_path(t, t_land, x, y, x0, y0, dur=.3):
    u = clamp((t - (t_land - dur)) / dur)
    return x0 + (x - x0) * ease_out(u, 2), y0 + (y - y0) * ease_in(u, 1.6) - 30 * math.sin(math.pi * u)


def s05(t):
    tk = T_KOFE
    dawn = ease_io(clamp((t - T_RASSVET) / .75))
    lamp_on = 1 - .7 * dawn
    x2, y2, k2, c2 = NEW_MUG
    if t < tk:
        mx, my = mug_path(t, tk, x2, y2, x2 - 130, y2 - 170, .32)
    else:
        mx, my = x2, y2
    hold = t < tk + .14
    # рука: несёт кружку → отпускает → назад к клавиатуре
    tn, tf_ = type_targets(t, amp=.5, rate=.8)
    if hold:
        wr = np.array([mx - 50 * k2 - 62 * BS + 8, my - 64 * k2 + 4])
        hn = dict(kind="none")
    else:
        u = ease_io(clamp((t - tk - .14) / .5))
        rel = np.array([x2 - 50 * k2 - 62 * BS - 10, y2 - 64 * k2 - 30])
        wr = rel + (tn - rel) * u
        hn = dict(HN, curl=(.2 + .15 * u, .25 + .15 * u, .3 + .15 * u, .35 + .15 * u))
    squint = smooth(T_RASSVET + .2, T_RASSVET + .7, t)
    expr = dict(lid=.3 - .12 * squint, look=(.6, .25), brows="tired", mouth="tired", closed=blink_at(t, 7.85, .18), red=1.0,
                hair=2 * osc(t, 1.5))
    d = dima(t, {"n": ("ik", tuple(wr), -1), "f": ("ik", tuple(tf_), -1)}, {"n": hn, "f": HF}, expr, lean=.26 if hold else .26 - .08 * clamp((t - tk - .14) / .5),
             head_ang=.04 + .02 * osc(t, .7))
    jump = bump(t, tk, .22)
    on_desk = mugs(t, jump, 3) + "".join(mug(x, y - 8 * jump, k, c) for (x, y, k, c) in BATTERY)
    sq = 1 - .07 * bump(t, tk, .14)
    m = (f'<g transform="translate({mx:.1f} {my:.1f}) scale(1 {sq:.3f}) translate({-mx:.1f} {-my:.1f})">' +
         mug(mx, my, k2, c2, fill="coffee", steam_t=t if t > tk - .05 else None) + "</g>")
    front = ""
    if hold:
        gb, gf = grip_mug(mx, my, k2)
        front = gb + m + gf
    else:
        on_desk += m
    # удар кружки — штрихи
    e = clamp((t - tk) / .28)
    if 0 < e < 1:
        for q in range(3):
            r0 = 40 + 30 * e + q * 12
            front += line([(x2 - r0 - 16, y2 - 12 - q * 20), (x2 - r0 - 40, y2 - 20 - q * 28)], 4.4 * (1 - e) + 1, "#3a2a22", seed=5300 + q, taper=.3, wmin=.4)
            front += line([(x2 + r0 + 16, y2 - 12 - q * 20), (x2 + r0 + 40, y2 - 20 - q * 28)], 4.4 * (1 - e) + 1, "#3a2a22", seed=5310 + q, taper=.3, wmin=.4)
    scr = doc_screen(t, 9.3 + .35 * (t - 6.2), errs=1.0, scroll=1.2, glow=1 - .5 * dawn)
    w = world(t, d, dawn=dawn, scr=scr, on_desk=on_desk, front=front, desk_jump=6 * jump, clock=(5.6 * 30 + 1.0 * dawn * 30, (36 * 6 + 60 * dawn) % 360),
              lamp_on=lamp_on)
    u = clamp((t - 6.2) / 2.0)
    k = ease_io(u)
    pk = bump(t, tk, .3)
    s = (1.62 + .16 * (.4 * u + .6 * k)) * (1 + .03 * pk)
    cam = (478 + 40 * k, 890 + 20 * k + 4 * pk * osc(t, 15), s, -.6 + .9 * u + .6 * pk * osc(t, 10))
    set_ink(s)
    return compose(w, cam, lamp_on=lamp_on, scr_on=1 - .6 * dawn, dawn=dawn)


# ═════════════════════════════════════ s06 — лицо у экрана: «стыдно» — ладонь на лицо, «сдавать» — сквозь пальцы ═════════════════════════════════════
def s06(t):
    ts, td = T_STYDNO, T_SDAVAT
    slap = ease_out(clamp((t - (ts - .14)) / .14), 2)          # рука взлетает к лицу к «стыдно»
    peek = ease_io(clamp((t - (td - .08)) / .22))                # пальцы раздвигаются к «сдавать»
    jolt = bump(t, ts, .3)
    lean = .3 - .06 * slap + .02 * osc(t, .5)
    head_ang = .06 - .1 * jolt + .03 * osc(t, .45) - .05 * slap
    if t < ts - .05:
        read = smooth(7.9, 8.4, t)
        expr = dict(lid=.45 + .4 * read, look=(.7, .2), brows="worry" if read > .3 else "tired", mouth="flat", red=1.0,
                    closed=blink_at(t, 8.1, .14), hair=2 * osc(t, 1.4))
    else:
        expr = dict(lid=.25 + .6 * peek, look=(.75, .25), brows="worry", mouth="sheep", smile=-.2, red=1.0, closed=(1 - peek) * .97,
                    hair=6 * jolt * osc(t, 10))
    tn, tf_ = type_targets(t, amp=.2, rate=.5)
    probe = dima(t, {"n": ("ik", tuple(tn), -1), "f": ("ik", tuple(tf_), -1)}, {"n": HN, "f": HF}, expr, lean=lean, head_ang=head_ang)
    ang = lean * .5 + head_ang
    hc = probe["head"]

    def hp(x, y):
        return hc + people.rot(np.array([x, y]), ang) * BS

    # ладонь: запястье у подбородка, пальцы вверх по лицу; на «сдавать» кисть чуть ниже и пальцы веером
    wr_face = hp(60 - 6 * peek, 128 + 6 * peek)
    fdir = people.rot(np.array([-.12, -1.0]), ang)
    if slap < 1:
        wr = tn + (wr_face - tn) * slap
        dd = np.array(HN["dir"]) * (1 - slap) + fdir * slap
    else:
        wr = wr_face + np.array([0, 3 * math.sin(t * 9) * (1 - peek)])
        dd = fdir
    face = slap > .55
    hn = dict(kind="open", flip=-1, dir=tuple(dd), curl=(.05, .04, .06, .1), spread=.06 + .42 * peek, thumb=.55, bend=.06, front=face, nails=True)
    d = dima(t, {"n": ("ik", tuple(wr), -1), "f": ("ik", tuple(tf_), -1)}, {"n": hn if slap > 0 else HN, "f": HF}, expr, lean=lean, head_ang=head_ang)
    errs = clamp((t - T_TEKST) / .5)
    scr = doc_screen(t, 12.6 + .05 * (t - 7.8), errs=.3 + .7 * errs, scroll=4.2)
    w = world(t, d, dawn=1.0, scr=scr, on_desk=mugs(t, 0.0, 3) + "".join(mug(x, y, k, c) for (x, y, k, c) in BATTERY), lamp_on=.3)
    u = clamp((t - 7.8) / 2.4)
    k = ease_io(u)
    s = (2.85 + .25 * k) * (1 + .04 * jolt)
    cam = (458 - 12 * k + 3 * jolt * osc(t, 14), 958 - 8 * k, s, .5 - .9 * u + .8 * jolt * osc(t, 9))
    set_ink(s)
    return compose(w, cam, lamp_on=.3, scr_on=1.0, dawn=1.0)


# ═════════════════════════════════════ s07 — кот на столе у ноутбука, рассвет; «почему» — наклон головы ═════════════════════════════════════
CAT7 = (972.0, 1128.0, .6)


def s07(t):
    x, y, sc = CAT7
    old_lamp = den.LAMP_B
    den.LAMP_B = (1235.0, 1084.0)
    tn, tf_ = type_targets(t, amp=0, rate=0)
    d = dima(t, {"n": ("ik", tuple(tn), -1), "f": ("ik", tuple(tf_), -1)}, {"n": HN, "f": HF}, {"red": 1.0}, lean=.2)
    scr = doc_screen(t, 12.6, errs=1.0, scroll=4.2)
    u = clamp((t - 9.8) / 2.4)
    k = ease_io(u)
    e = t - T_POCHEMU
    s = 4.0 + .3 * (.4 * u + .6 * k)
    if e > 0:
        s *= 1 + .035 * math.exp(-e * 6) * math.sin(min(e * 10, math.pi))
    hc = Cat.to_world((836, 1100), x, y, sc)
    cam = (hc[0] - 6 + 12 * k, hc[1] + 30 - 10 * k, s, 1.0 - 1.6 * u)
    set_ink(s)
    # рассветный луч из окна на стене за котом
    beam = lib.lin_grad([(0, "#ffc890", .5), (1, "#ffb080", .0)], 0, 0, 1, 0)
    pts = [(820, 760), (1010, 700), (1130, 1060), (900, 1080)]
    beam_svg = f'<path d="{lib.fill_d([p + (1,) for p in pts])}" fill="url(#{beam})" style="mix-blend-mode:screen" {lib.blur(16)}/>'
    w_no_cat = world(t, d, dawn=1.0, scr=scr, on_desk=beam_svg, lamp_on=.25, floor_papers=False)
    den.LAMP_B = old_lamp
    # кот: смотрит в камеру; «Знаешь» — ухо и взгляд; «почему» — наклон головы с пружиной
    tilt = -1.5 + 1.0 * math.sin(t * 1.4)
    if e > -0.08:
        q = e + 0.08
        tilt += 11 * (1 - math.exp(-q * 7) * math.cos(q * 13)) * (1 - smooth(11.3, 11.8, t) * .35)
    look = (0.06 * math.sin(t * .8), -0.05 + 0.08 * smooth(T_POCHEMU, T_POCHEMU + .3, t))
    blink = 0.0
    for c, half, hold in ((9.95, 0.06, 0.0), (11.45, 0.1, 0.04)):
        a = c - half
        if a <= t <= c + hold + half:
            blink = ease_io((t - a) / half) if t < c else (1.0 if t < c + hold else 1 - ease_io((t - c - hold) / half))
    flick = 0.0
    for c in (T_ZNAESH + .02, T_POCHEMU + .06):
        q = t - c
        if 0 <= q < 0.5:
            flick += -14 * math.exp(-q * 9) * math.sin(q * 34)
    tail = 6 * math.sin(t * 2.1) + 3 * math.sin(t * 3.7 + 1)
    fx, fy = Cat.flame_world(x, y, sc, tail)
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    g = lib.rad_grad([(0, "#ffb050", .34 * fl), (1, "#ffb050", 0)], fx, fy, 200, 200)
    glow = f'<rect x="{fx - 220:.1f}" y="{fy - 220:.1f}" width="440" height="440" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    old = lib.INK_K[0]
    lib.INK_K[0] = 1.0
    catsvg = Cat.draw(x, y, sc, t, look=look, blink=blink, tilt=tilt, tail=tail, flick=flick)
    lib.INK_K[0] = old
    return compose(w_no_cat + glow + catsvg, cam, lamp_on=.25, scr_on=.8, dawn=1.0)


SCENES = {"s01": s01, "s05": s05, "s06": s06, "s07": s07}
_INIT = []


def frame(sid, t):
    if not _INIT:
        lib.DEFS.clear()
        lib.INK_K[0] = 1.0
        Cat.static_parts()
        lib.static_done()
        _INIT.append(1)
    lib.dyn_begin()
    return SCENES[sid](t)
