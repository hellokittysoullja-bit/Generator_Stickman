"""Стол Димы рилса 43 «успешные встают в 5 утра» (агент C; основа — scene_desk рилса 41): s06 (день, почти полдень,
клюёт носом над ноутбуком с кружкой, на «спал» голова падает на клавиатуру, Z-Z-Z, кружка кренится), s14 (вечер,
закат, лампа: на «трудные» на стол падает папка-кирпич, Дима засучивает рукава и раскрывает её), s15 (ночь, луна:
бодро печатает, на «свежая» над головой зажигается лампочка, листы папки перелетают в стопку «готово»), s16 (список
дел у ноутбука: галочки на «сделано» и «больше», Дима довольно откидывается на стуле).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика; удары — на словах voice/words.json.
Мир — комната рилса 32 (den.py), день — светлые обои и дневное окно (den.window_day)."""
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

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["word"].strip(".,?!").lower() == word.lower() and w["start"] >= after - 1e-6:
            return w["start"]
    raise KeyError(word)


T_NEDELYU = wt("неделю")      # 7.04
T_SPAL = wt("спал")           # 8.96
T_TRUD = wt("трудные")        # 25.68
T_DELA = wt("дела")           # 26.08
T_SVEZH = wt("свежая")        # 28.00
T_SDEL = wt("сделано")        # 29.04
T_BOLSHE = wt("больше")       # 29.52

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


def doc_screen(t, chars, errs=1.0, scroll=0.0, glow=1.0, title="ОТЧЁТ", garbage=0.0):
    """Курсовая в редакторе: синяя шапка, белый лист, строки растут (chars — сколько строк набрано, дробное),
    красные волны под ошибками (errs 0..1 — сколько проявилось), лист уезжает вверх на scroll строк."""
    cid = lib.clip_rect(0, 0, SW, SH)
    o = [f'<g clip-path="url(#{cid})"><rect width="{SW}" height="{SH}" fill="#d9dde6"/>']
    o.append(f'<rect width="{SW}" height="56" fill="#2f63b8"/>')
    for k in range(3):
        o.append(f'<circle cx="{28 + k * 26}" cy="28" r="8" fill="#e8eefb" opacity=".85"/>')
    o.append(f'<text x="{SW / 2:.0f}" y="40" text-anchor="middle" font-family="IDB" font-size="28" fill="#ffffff" letter-spacing="2">{title}</text>')
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
    if garbage > 0:          # голова на клавиатуре: строки одной буквы
        r0 = int(chars) + 1
        n = int(garbage)
        for j in range(n + 1):
            y = top + 26 + (r0 + j) * 38 + 12
            cnt = 22 if j < n else int(22 * (garbage - n))
            if cnt <= 0 or y > SH + 20:
                continue
            o.append(f'<text x="{px0 + 35}" y="{y:.1f}" font-family="IDB" font-size="24" fill="#55585f" letter-spacing="1">{"ж" * cnt}</text>')
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
MODE = ["night"]
WALLS = {"night": ("#4d6170", "#3f5160", "#56697a"), "eve": ("#6a6478", "#59536a", "#756f84"), "day": ("#d9dcc4", "#c3c7ad", "#e3e5cf")}


def room_back(t, dawn=0.0, clock=(0.0, 0.0), clock_jolt=0.0):
    den.WALL, den.WALL_SH, den.WALL_ST = WALLS[MODE[0]]
    win = den.window_day(t) if MODE[0] == "day" else den.window(t, dawn)
    return "".join([den.wall(t), win, den.board(t), den.shelf(t), den.clock(clock[0], clock[1], clock_jolt, 0.0), den.floor()])


def world(t, d, *, dawn=0.0, clock=(0.0, 0.0), scr="", on_desk="", front="", desk_jump=0.0, floor_papers=True, lamp_on=1.0, back_desk=""):
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
    w.append(back_desk)
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
    if MODE[0] == "day":
        g2 = lib.rad_grad([(0, "#000000", 0), (.6, "#000000", 0), (1, "#2a2418", .3)], 700, 1000, 1300, 1300)
        sun = lib.rad_grad([(0, "#fff4c8", .35), (1, "#fff4c8", 0)], 220, 520, 700, 700)
        inner = (f'{wrld}<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{sun})" style="mix-blend-mode:screen"/>'
                 f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{g2})"/>')
        g = f'<g transform="{lib.cam(cam[0], cam[1], cam[2], cam[3])}">{inner}</g>'
        return lib.svg(f'<rect width="1080" height="1920" fill="#3a3a30"/>{g}{extra_front}')
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


# ═════════════════════════════════════ общее рилса 43 ═════════════════════════════════════
def zzz(t, x, y, t0, col="#3d5a9a", k=1.0):
    o = []
    for j in range(3):
        ph = (t - t0) / 1.5 - j / 3
        if ph < 0:
            continue
        ph %= 1
        sc = back_out(clamp(ph / .25), 2) * (1 - ease_in(clamp((ph - .75) / .25), 2)) * (.7 + .6 * ph) * k
        if sc < .03:
            continue
        cx = x + 80 * ph + 12 * math.sin(ph * 8 + j)
        cy = y - 190 * ph
        r = 22 * sc
        pts = [(cx - r, cy - r), (cx + r, cy - r), (cx - r, cy + r), (cx + r, cy + r)]
        o.append(line(pts, 9 * sc + 3, col, taper=.1, wmin=.8, seed=5800 + j))
    return "".join(o)


def jolt(t, t0, amp=1.0, dur=.4, fr=15.0):
    u = t - t0
    if u < 0 or u > dur:
        return 0.0
    return amp * math.exp(-u * 8) * math.sin(u * fr * 6.28)


# ═════════════════════════════════════ s06 — полдень: клюёт носом, на «спал» голова падает на клавиатуру ═════════════════════════════════════
MUG6 = (790.0, 1150.0, .46, "#d8483c")


def s06(t):
    MODE[0] = "day"
    ts = T_SPAL
    drop = clamp((t - (ts - .1)) / .14)
    dk = ease_in(drop, 2)
    bnc = jolt(t, ts + .04, .06, .45, 3.2)
    # клюёт носом: голова медленно оседает и вздёргивается (8.1→8.55), снова оседает к удару
    nod = .22 * smooth(8.1, 8.5, t) * (1 - smooth(8.5, 8.58, t)) + .26 * smooth(8.6, ts - .1, t)
    lean = .16 + .1 * nod + (.72 - .26) * dk + bnc
    head_ang = nod * .8 * (1 - dk) + .48 * dk + bnc * .5
    x2, y2, k2, c2 = MUG6
    tn, tf_ = type_targets(t, amp=0, rate=0)
    held = drop < .5
    if held:
        wr = np.array([x2 - 50 * k2 - 62 * BS + 8, y2 - 64 * k2 + 4])
        hn = dict(kind="none")
    else:
        u = ease_out(clamp((t - ts) / .3), 2)
        wr = np.array([x2 - 50 * k2 - 62 * BS + 8 - 40 * u, y2 - 64 * k2 + 4 + 34 * u])
        hn = dict(HN, curl=(.3, .35, .4, .45), dir=(.9, .3))
    lid = .12 - .1 * nod
    expr = dict(lid=max(.0, lid), look=(.5, .35), brows="tired", mouth="tired" if not held else "flat", closed=clamp(.35 + nod * 2.5) if held else 1.0,
                red=.5, hair=3 * math.sin(t * 2) + 10 * jolt(t, ts + .02, 1, .5, 4))
    d = dima(t, {"n": ("ik", tuple(wr), -1), "f": ("ik", tuple(tf_ + np.array([0, 6])), -1)}, {"n": hn, "f": HF}, expr, lean=lean, head_ang=head_ang)
    # кружка: держит — стоит; отпустил — кренится и качается, пара капель
    tilt = 0.0
    if not held:
        e = t - ts
        tilt = 16 * (1 - math.exp(-e * 9)) * math.cos(e * 11) * math.exp(-e * 1.5) + 5 * (1 - math.exp(-e * 4))
    m = mug(x2, y2, k2, c2, fill="coffee") if tilt == 0 else den.mug(x2, y2, k2, c2, fill="coffee", rot=tilt)
    front = ""
    on_desk = mug(1010.0, 1112.0, .4, "#5f8a5a")
    if held:
        gb, gf = grip_mug(x2, y2, k2)
        front = gb + m + gf
    else:
        on_desk += m
        e = t - ts
        for j in range(3):
            q = clamp((e - .05 - j * .05) / .35)
            if 0 < q < 1:
                px = x2 + 30 + j * 14 + 60 * q
                py = y2 - 64 * k2 * 2.4 + 120 * q * q - 50 * q
                front += blob(ellipse_pts(px, py, 7, 9, 8), "#5a3220")
    gar = 3.2 * clamp((t - ts) / .9)
    scr = doc_screen(t, 5.2 + .3 * clamp((t - 8.1) / .8), errs=.0, scroll=0.0, title="ОТЧЁТ", garbage=gar)
    clk = (11 * 30 + (55 + 2 * (t - 8.1)) * .5, (55 + 2 * (t - 8.1)) * 6)
    w = world(t, d, scr=scr, on_desk=on_desk, front=front, desk_jump=8 * bump(t, ts, .22), clock=clk, lamp_on=0.0, floor_papers=False)
    hd = d["head"]
    if t > ts:
        w += zzz(t, hd[0] + 10, hd[1] - 110, ts + .1)
    # удар — штрихи у головы
    e = clamp((t - ts) / .3)
    if 0 < e < 1:
        for q in range(3):
            a = math.radians(-120 + q * 30)
            r0 = 110 + 50 * e
            w += line([(hd[0] + math.cos(a) * r0, hd[1] + math.sin(a) * r0), (hd[0] + math.cos(a) * (r0 + 40), hd[1] + math.sin(a) * (r0 + 40))],
                      6 * (1 - e) + 1.5, INK, taper=.3, wmin=.4, seed=5900 + q)
    u = clamp((t - 8.1) / 2.26)
    k = ease_io(u)
    pk = bump(t, ts, .3)
    s = (1.55 + .2 * (.4 * u + .6 * k)) * (1 + .05 * pk)
    cam = (530 + 40 * k + 6 * jolt(t, ts, 1, .4, 13), 965 + 20 * k + 8 * jolt(t, ts, 1, .4, 11), s, -.5 + .8 * u + .8 * jolt(t, ts, 1, .4, 9))
    set_ink(s)
    return compose(w, cam, lamp_on=0.0, scr_on=.4)


# ═════════════════════════════════════ папка-кирпич ═════════════════════════════════════
FOLD_W, FOLD_D, FOLD_H = 214.0, .55, 74.0
F_BLUE, F_BLUE_SH, F_PAGE, F_PAGE_SH = "#3f6fb0", "#2c5288", "#fbf6e8", "#e4dcc6"


def folder(O, open_=0.0, sq=1.0, pages_left=1.0, sd=6100, label=True):
    """Толстая папка на столе (вид 3/4 как у ноутбука): O — передний левый нижний угол; обложка на петлях слева,
    open_ 0..1 — раскрыта (0 — закрыта, 1 — лежит раскрытой влево); sq — сплющивание при ударе; pages_left — доля стопки."""
    O = np.array(O, float)
    Wv = np.array([FOLD_W, -8.0])
    Dv = -FWD * FOLD_D
    h = FOLD_H * sq * (.25 + .75 * pages_left)
    up = np.array([0.0, -h])
    o = [blob([tuple(O + [-6, 4]), tuple(O + Wv + [10, 4]), tuple(O + Wv + Dv + [10, 2]), tuple(O + Dv + [-6, 2])], "#1a100a", .3, lib.blur(5))]
    # нижняя корка
    o.append(shape([tuple(O) + (1,), tuple(O + Wv) + (1,), tuple(O + Wv + [0, -10]) + (1,), tuple(O + [0, -10]) + (1,)], F_BLUE_SH, "", w=3.4, seed=sd))
    o.append(shape([tuple(O + Wv) + (1,), tuple(O + Wv + Dv) + (1,), tuple(O + Wv + Dv + [0, -10]) + (1,), tuple(O + Wv + [0, -10]) + (1,)], F_BLUE_SH, "",
                   w=3.0, seed=sd + 1))
    # стопка листов: передний и правый срез — полосы
    P0 = O + [6, -10]
    Pw = Wv - [12, 0]
    ph = up + [0, 10]
    stripes = "".join(line([tuple(P0 + ph * (k / 7)), tuple(P0 + Pw + ph * (k / 7))], 1.6, "#c9bfa6", seed=sd + 10 + k, op=.9) for k in range(1, 7))
    o.append(shape([tuple(P0) + (1,), tuple(P0 + Pw) + (1,), tuple(P0 + Pw + ph) + (1,), tuple(P0 + ph) + (1,)], F_PAGE, stripes, w=3.2, seed=sd + 2))
    o.append(shape([tuple(P0 + Pw) + (1,), tuple(P0 + Pw + Dv * .92) + (1,), tuple(P0 + Pw + Dv * .92 + ph) + (1,), tuple(P0 + Pw + ph) + (1,)],
                   F_PAGE_SH, "", w=3.0, seed=sd + 3))
    top = O + up
    # верхний лист (видно, когда обложка открыта): строки текста
    if open_ > 0.02:
        tl = top + [6, 0]
        tw = Wv - [12, 0]
        rows = ""
        for r in range(6):
            a = tl + tw * .1 + Dv * (.15 + r * .13)
            rows += line([tuple(a), tuple(a + tw * (.75 - .2 * (r % 3 == 2)))], 3.0, "#8a8f9c", seed=sd + 20 + r, op=.9, taper=.1, wmin=.7)
        o.append(shape([tuple(tl) + (1,), tuple(tl + tw) + (1,), tuple(tl + tw + Dv * .92) + (1,), tuple(tl + Dv * .92) + (1,)], F_PAGE, rows, w=3.0,
                       seed=sd + 4))
    # обложка: петля по левому краю, поворот вокруг оси глубины
    th = math.pi * .96 * ease_io(open_)
    cw = -Wv * math.cos(th) + np.array([0.0, -FOLD_W * .85]) * math.sin(th)
    c0 = top + Wv + [0, -2]
    cov = [tuple(c0) + (1,), tuple(c0 + cw) + (1,), tuple(c0 + cw + Dv) + (1,), tuple(c0 + Dv) + (1,)]
    inner = ""
    if open_ < .5:
        if label:
            lc = c0 + cw * .32 + Dv * .3
            inner += shape([tuple(lc) + (1,), tuple(lc + cw * .4) + (1,), tuple(lc + cw * .4 + Dv * .4) + (1,), tuple(lc + Dv * .4) + (1,)], "#fbf3df", "",
                           w=2.4, seed=sd + 6)
        inner += line([tuple(c0 + cw * .06 + Dv * .1), tuple(c0 + cw * .06 + Dv * .9)], 3, F_BLUE_SH, seed=sd + 7, op=.9)
        col = F_BLUE
    else:
        col = "#6f95cf"
        inner += blob([tuple(c0 + cw * .5), tuple(c0 + cw), tuple(c0 + cw + Dv), tuple(c0 + cw * .5 + Dv)], "#5b82bd", .8)
    cov_svg = shape(cov, col, inner, w=4.2, seed=sd + 8)
    o.append(cov_svg)
    return "".join(o)


def impact_lines(x, y, e, sd, n=7, r0=90, L=60, w=7.0, col=INK):
    if e <= 0 or e >= 1:
        return ""
    o = []
    for k in range(n):
        a = math.pi + k * math.pi / (n - 1)
        r = r0 + 80 * ease_out(e)
        Lk = L * (1 - e)
        o.append(line([(x + math.cos(a) * r, y + math.sin(a) * r * .7), (x + math.cos(a) * (r + Lk), y + math.sin(a) * (r + Lk) * .7)],
                      w * (1 - e) + 1.5, col, taper=.4, wmin=.3, seed=sd + k))
    return "".join(o)


def dust(x, y, e, sd):
    """Пыль от удара: плотные клубки разлетаются в стороны и тают размером (без прозрачности)."""
    if e <= 0 or e >= 1:
        return ""
    o = []
    for k in range(6):
        side = -1 if k % 2 else 1
        r = (10 + 4 * (k % 3)) * (1 - e) ** .8 * (1 + .6 * min(1, e * 4))
        if r < 1.5:
            continue
        cx = x + side * (120 + 90 * ease_out(e) * (1 + .4 * (k // 2)))
        cy = y - 8 - 50 * ease_out(e) * (k // 2 + .5)
        o.append(shape(ellipse_pts(cx, cy, r * 1.25, r, 10), "#efe6d2", "", w=2.2, seed=sd + k))
    return "".join(o)


# ═════════════════════════════════════ s14 — вечер: папка-кирпич на «трудные», засучил рукава, раскрыл ═════════════════════════════════════
FO14 = np.array([468.0, 1150.0])


def s14(t):
    MODE[0] = "eve"
    tt = T_TRUD
    fall = clamp((t - (tt - .32)) / .32)
    fy = -760 * (1 - fall ** 2)
    land = t >= tt
    sq = 1 - .22 * bump(t, tt, .16)
    opn = ease_io(clamp((t - (T_DELA + .1)) / .55))
    # рукава: засучивает до удара (24.9→25.55), руки перед грудью
    roll_f = ease_io(clamp((t - 24.97) / .28))
    roll_n = ease_io(clamp((t - 25.27) / .28))
    people.ROLL.update(n=roll_n, f=roll_f)
    sh = np.array(HIP) + np.array([140.0, -250.0])
    if t < tt:
        # одна рука тянет рукав другой: кисть ползёт по предплечью от запястья к локтю
        ph1 = ease_io(clamp((t - 24.95) / .3))
        ph2 = ease_io(clamp((t - 25.25) / .3))
        fw = sh + np.array([215.0, 40.0 - 50 * ph2])
        nw = sh + np.array([225.0, -40.0 + 30 * ph2])
        pf = dima(t, {"n": ("ik", tuple(nw), -1), "f": ("ik", tuple(fw), -1)}, {}, {}, lean=.12)
        if t < 25.25:
            tf_ = fw
            tn = pf["wrist"]["f"] + (pf["elbow"]["f"] - pf["wrist"]["f"]) * (.15 + .5 * ph1) + np.array([0, -18])
        else:
            tn = nw
            tf_ = pf["wrist"]["n"] + (pf["elbow"]["n"] - pf["wrist"]["n"]) * (.15 + .5 * ph2) + np.array([0, -18])
        hn = dict(kind="open", flip=1, dir=(-.6, .8) if t < 25.25 else (.9, -.3), curl=(.6, .65, .7, .7), spread=.05, thumb=.6, bend=.1)
        hf = dict(kind="open", flip=1, dir=(.9, -.3) if t < 25.25 else (-.6, .8), curl=(.6, .65, .7, .7), spread=.05, thumb=.6, bend=.1)
        expr = dict(lid=.6, look=(.7, .3), brows="det", mouth="flat", red=0.0, hair=2 * math.sin(t * 2), bags=True)
        lean = .12
    else:
        # после удара: дальняя рука ложится на папку, ближняя берёт край обложки и откидывает её
        top = FO14 + np.array([0, -FOLD_H])
        Wv = np.array([FOLD_W, -8.0])
        th = math.pi * .96 * min(opn, .55) / 1.0
        edge = top + Wv - Wv * math.cos(th) + np.array([0.0, -FOLD_W * .85]) * math.sin(th) + (-FWD * FOLD_D) * .4
        reach = ease_out(clamp((t - (tt + .12)) / .3), 2)
        back = ease_io(clamp((opn - .5) / .4))
        rest = sh + np.array([150.0, 20.0])
        page = top + Wv * .3 + (-FWD * FOLD_D) * .5 + np.array([0, -4])
        tn = rest + (edge + np.array([-6, 4]) - rest) * reach
        tn = tn + (page - tn) * back
        tf_ = sh + np.array([150.0, -10.0]) + (top + Wv * .55 + np.array([0, 2]) - sh - np.array([150.0, -10.0])) * ease_out(clamp((t - tt) / .3), 2)
        hn = dict(kind="open", flip=1, dir=(.9, -.1 - .8 * min(opn, .5) * (1 - back)), curl=(.45, .5, .55, .55), spread=.05, thumb=.5, bend=.12)
        hf = dict(HF, curl=(.15, .2, .25, .3))
        expr = dict(lid=.75, look=(.65, .5), brows="det", mouth="flat", red=0.0, hair=8 * jolt(t, tt, 1, .5, 4), bags=True)
        lean = .12 + .14 * reach
    expr["closed"] = blink_at(t, 25.05, .14)
    d = dima(t, {"n": ("ik", tuple(tn), -1), "f": ("ik", tuple(tf_), -1)}, {"n": hn, "f": hf}, expr, lean=lean, head_ang=.04 * math.sin(t * 1.3))
    people.ROLL.clear()
    fo = folder(FO14 + np.array([0, fy]), open_=opn, sq=sq)
    if t < tt:
        fo = f'<g transform="rotate({-8 * (1 - fall):.2f} {FO14[0] + 100:.1f} {FO14[1] + fy - 40:.1f})">{fo}</g>'
        if fall > 0:
            for k in range(3):
                x = FO14[0] + 40 + k * 70
                fo += line([(x, FO14[1] + fy - 140), (x, FO14[1] + fy - 140 - 120 * fall)], 5, INK, taper=.7, seed=6200 + k, op=.7)
    e = (t - tt) / .3
    fx = impact_lines(FO14[0] + 107, FO14[1] - 30, e, 6210)
    on_desk = mug(1010.0, 1112.0 - 14 * bump(t, tt, .2), .4, "#5f8a5a")
    scr = doc_screen(t, 3.0, errs=0, title="ОТЧЁТ")
    w = world(t, d, dawn=1.0, scr=scr, on_desk=on_desk, front=fo + fx, desk_jump=0, clock=(19 * 30 + 15, 30 * 6), lamp_on=1.0, floor_papers=False)
    u = clamp((t - 24.9) / 2.14)
    k = ease_io(u)
    pk = bump(t, tt, .3)
    s = (1.62 + .1 * k) * (1 + .05 * pk)
    cam = (515 + 20 * k + 6 * jolt(t, tt, 1, .4, 13), 990 + 12 * jolt(t, tt, 1, .4, 11), s, .5 - .7 * u + 1.0 * jolt(t, tt, 1, .4, 9))
    set_ink(s)
    return compose(w, cam, lamp_on=1.0, scr_on=.6, dawn=.85)


SCENES = {"s06": s06, "s14": s14}
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
