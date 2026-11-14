"""Рилс 57 «вода», группа A: кухня и комната Димы, Дима в среднем плане.
s01 (0–1.4) хук: восемь стаканов на кухонном столе, Дима льёт из кувшина вдоль ряда, брызги, влёт камеры 0.22 с.
s03 (3.44–5.2) Дима допивает огромный стакан через силу, на «силу» (5.18) давится.
s07 (11.0–12.8) суп за кухонным столом, пар, яблоко, чашка, капельки «вода и в еде».
s11 (19.1–21.5) диван, книга, на «хочется» (20.96) капля-значок, глоток из стакана на столике.
s13 (23.8–26.6) стол днём, на «бутылка» (25.8) встаёт бутылка, блик, капелька.
s14 (26.6–28.9) Дима берёт бутылку, пьёт («пьёт» 27.32), смотрит в окно, на «хочет» (28.0) улыбается, ставит.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Общие предметы — common/props.py."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import base_d as D  # noqa: E402
import room as ROOM  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props  # noqa: E402
import s56 as S  # noqa: E402
from lib import (blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts, shape, smooth,  # noqa: E402
                 svg, back_out, spring)

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))
T = {i: w["start"] for i, w in enumerate(WORDS)}
INK = lib.INK
FLOOR_Y = 1440
G, kf, rnd, lerp = S.G, S.kf, S.rnd, S.lerp
hand_spec, stand, dima_layers, head_w, wrist_w = S.hand_spec, S.stand, S.dima_layers, S.head_w, S.wrist_w
sweat_drop, stress_marks, dust = S.sweat_drop, S.stress_marks, S.dust
_ST = {}


def whip(out, t, t0, dist=260):
    return S.whip(out, t, t0, dist)


# ═════════════════════════ кухня ═════════════════════════
def kitchen_static():
    o = []
    o.append('<rect x="-1600" y="-2200" width="4400" height="3600" fill="#EADFC6"/>')
    # плитка фартука
    o.append('<rect x="-1600" y="780" width="4400" height="560" fill="#F6F1E4"/>')
    for k in range(-24, 40):
        o.append(line([(k * 75, 780), (k * 75, 1330)], 2.2, "#D8CDB4", taper=.02, wmin=.95, seed=9000 + k, op=.8))
    for k in range(8):
        o.append(line([(-1600, 780 + k * 70), (2800, 780 + k * 70)], 2.2, "#D8CDB4", taper=.02, wmin=.95, seed=9100 + k, op=.8))
    o.append(shape(rect_pts(-1600, 770, 2800, 792), "#5E9B92", blob(rect_pts(-1600, 784, 2800, 792), "#437A72"), w=3.6, seed=9150))
    # окно слева: дневное небо, облака, солнце
    x0, y0, x1, y1 = 90, 250, 480, 700
    sky = lin_grad([(0, "#8EC9EE", 1), (1, "#D7EEF8", 1)], 0, 0, 0, 1)
    inn = f'<rect x="{x0 - 10}" y="{y0 - 10}" width="{x1 - x0 + 20}" height="{y1 - y0 + 20}" fill="url(#{sky})"/>'
    inn += blob(ellipse_pts(180, 340, 46, 46, 18), "#FFF0A8") + blob(ellipse_pts(330, 420, 70, 22, 14), "#FFFFFF") + blob(ellipse_pts(250, 520, 56, 18, 14), "#FFFFFF")
    inn += blob([(x0 - 10, 640), (160, 620), (160, 570), (260, 570), (260, 630), (360, 610), (360, 540), (440, 540), (440, 620), (x1 + 10, 620),
                 (x1 + 10, y1 + 10), (x0 - 10, y1 + 10)], "#8FB4C6")
    inn += blob(rect_pts(284, y0, 306, y1), "#F6F1E4") + blob(rect_pts(x0, 440, x1, 462), "#F6F1E4")
    o.append(shape(rect_pts(x0, y0, x1, y1, 8), "#F6F1E4", inn, w=5, seed=9200))
    o.append(shape(rect_pts(x0 - 24, y1 - 2, x1 + 24, y1 + 26, 6), "#F6F1E4", "", w=4.2, seed=9201))
    # верхний шкаф справа
    for k in range(3):
        xx = 640 + k * 150
        o.append(shape(rect_pts(xx, 200, xx + 146, 560, 6), "#D98C6A", blob(rect_pts(xx + 100, 200, xx + 146, 560), "#B9694C", .8) +
                       blob(rect_pts(xx + 14, 214, xx + 132, 546, 4), "#E5A083", .6), w=4.2, seed=9210 + k))
        o.append(shape(rect_pts(xx + 112 - 30 * (k % 2), 360, xx + 124 - 30 * (k % 2), 430, 4), "#EFE6D6", "", w=3, seed=9220 + k))
    # рейка с половником и лопаткой
    o.append(line([(560, 690), (1120, 690)], 8, INK, taper=.02, wmin=.95, seed=9230))
    o.append(line([(560, 690), (1120, 690)], 4, "#C4C9CF", taper=.02, wmin=.95, seed=9231))
    for k, (hx, col) in enumerate(((650, "#C4C9CF"), (760, "#C28A52"), (1010, "#8FA8B0"))):
        o.append(line([(hx, 694), (hx, 780)], 6, INK, taper=.05, wmin=.9, seed=9240 + k))
        o.append(line([(hx, 694), (hx, 780)], 3, col, taper=.05, wmin=.9, seed=9250 + k))
        o.append(shape(ellipse_pts(hx, 806, 22, 28, 12), col, "", w=3.4, seed=9260 + k))
    # столешница у стены и шкафчики
    o.append(shape(rect_pts(-1600, 1010, 2800, 1042), "#C88A58", blob(rect_pts(-1600, 1030, 2800, 1042), "#A8693F"), w=4.6, seed=9270))
    o.append(shape(rect_pts(-1600, 1042, 2800, 1330), "#EFE6D6", "", w=4, seed=9271))
    for k in range(-8, 14):
        o.append(shape(rect_pts(k * 190 + 10, 1062, k * 190 + 180, 1300, 6), "#F8F2E6", blob(rect_pts(k * 190 + 130, 1062, k * 190 + 180, 1300), "#E4D8C2", .9),
                       w=3.2, seed=9280 + k))
        o.append(shape(rect_pts(k * 190 + 150, 1090, k * 190 + 160, 1130, 4), "#9AA2AA", "", w=2.6, seed=9330 + k))
    # чайник на столешнице
    o.append(shape([(820, 1008, 1), (930, 1008, 1), (924, 920), (860, 892), (826, 930)], "#C4C9CF", blob([(900, 1008), (930, 1008), (924, 920), (900, 910)], "#9AA2AA", .8),
                   w=3.8, seed=9340))
    o.append(shape(rect_pts(868, 884, 886, 898, 3), "#2f3340", "", w=3, seed=9341))
    # пол
    o.append('<rect x="-1600" y="1330" width="4400" height="1200" fill="#B58A5E"/>')
    for k, y in enumerate(range(1380, 1740, 62)):
        o.append(line([(-1600, y), (2800, y + 2)], 2.6, "#8F6842", taper=.05, wmin=.9, seed=9350 + k, op=.8))
    o.append(shape(rect_pts(-1600, 1318, 2800, 1344), "#EFE6D6", "", w=4.2, seed=9360))
    return "".join(o)


def table_parts(x0=40, x1=1100, back=1150, front=1215):
    """Кухонный стол спереди-чуть-сверху: (ножки, крышка+фартук)."""
    legs = []
    for k, x in enumerate((x0 + 40, x1 - 40)):
        legs.append(shape([(x - 20, front + 40, 1), (x + 20, front + 40, 1), (x + 14, FLOOR_Y + 40, 1), (x - 14, FLOOR_Y + 40, 1)], "#A8693F",
                          blob([(x + 4, front + 40), (x + 20, front + 40), (x + 14, FLOOR_Y + 40), (x + 4, FLOOR_Y + 40)], "#7F4B2B", .8), w=3.8, seed=9400 + k))
    top = []
    top.append(shape([(x0 + 30, back, 1), (x1 - 30, back, 1), (x1 + 20, front, 1), (x0 - 20, front, 1)], "#E3B27A",
                     "".join(line([(x0, back + 10 + k * 16), (x1, back + 10 + k * 16)], 2, "#C98F56", taper=.1, wmin=.8, seed=9420 + k, op=.7) for k in range(3)), w=4.4, seed=9410))
    top.append(shape([(x0 - 20, front, 1), (x1 + 20, front, 1), (x1 + 20, front + 50, 1), (x0 - 20, front + 50, 1)], "#BD7F4C",
                     blob(rect_pts(x0 - 20, front + 32, x1 + 20, front + 50), "#8F5A33", .8), w=4.6, seed=9411))
    return "".join(legs), "".join(top)


def light_k(t):
    """Дневной луч из окна (мягкий screen) — живое пятно света на кухне."""
    g = lin_grad([(0, "#FFF3C4", .0), (.3, "#FFF3C4", .22), (1, "#FFF3C4", .05)], 0, 0, 0, 1)
    return f'<path d="M90 250 L480 250 L1000 1330 L420 1330 Z" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def motes(t, box=(140, 300, 900, 1250), n=24, seed=11):
    rs = np.random.RandomState(seed)
    o = []
    for i in range(n):
        x0, y0 = rs.uniform(box[0], box[2]), rs.uniform(box[1], box[3])
        sp, ph, r = rs.uniform(10, 24), rs.uniform(0, 6.28), rs.uniform(2.2, 4.4)
        y = box[1] + (y0 - box[1] - sp * t) % (box[3] - box[1])
        x = x0 + 16 * math.sin(t * .7 + ph)
        a = (0.55 + 0.35 * math.sin(t * 2.2 + ph)) * smooth(box[1], box[1] + 80, y) * (1 - smooth(box[3] - 100, box[3], y))
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#fff6d8" opacity="{a * .8:.2f}"/>')
    return "".join(o)


# ═════════════════════════ кувшин, струя, капли ═════════════════════════
def jug(x, y, k=1.0, rot=0.0, level=.7):
    """Кувшин: (x, y) — дно по центру. Носик справа-вверху (у +x), ручка слева. Вода и сплошные заливки."""
    o = []
    body = [(-44, 0, 1), (44, 0, 1), (50, -20), (50, -140), (66, -176, 1), (40, -168), (-50, -168, 1), (-52, -140), (-50, -20)]
    inn = blob([(24, -176), (66, -176), (50, -140), (50, -20), (44, 0), (22, 0)], props.C_GLASS_SH)
    w_top = -168 + (1 - level) * 150
    inn += blob([(-60, w_top, 1), (60, w_top, 1), (60, 10, 1), (-60, 10, 1)], props.C_WATER)
    inn += blob([(18, w_top, 1), (60, w_top, 1), (60, 10, 1), (22, 10, 1)], props.C_WATER_SH)
    inn += blob(ellipse_pts(0, w_top, 48, 6, 14), props.C_WATER_TOP)
    handle = [(-50, -150), (-96, -140), (-102, -70), (-52, -40)]
    o.append(line(handle, 14, INK, taper=.1, wmin=.8, seed=9500))
    o.append(line(handle, 7, props.C_GLASS, taper=.1, wmin=.8, seed=9501))
    o.append(shape(body, props.C_GLASS, inn, w=3.8, seed=9502))
    o.append(line([(-34, -154), (-36, -40)], 7, props.C_WHITE, taper=.5, wmin=.3, seed=9503, peak=.5))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({k:.4f})">{"".join(o)}</g>'


def jug_spout(x, y, k, rot):
    a = math.radians(rot)
    px, py = 64 * k, -172 * k
    return (x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a))


def stream(x0, y0, y1, wob, w=14, seed=0):
    """Струя воды от (x0, y0) вниз до y1: чуть дугой, сплошная, с белой серединой."""
    pts = [(x0, y0), (x0 + 6 + wob, (y0 + y1) / 2), (x0 + 4 + wob * .5, y1)]
    return line(pts, w, props.C_WATER, taper=.2, wmin=.55, seed=9600 + seed, peak=.4) + line(pts, w * .35, props.C_WATER_TOP, taper=.3, wmin=.4, seed=9610 + seed, peak=.5)


def splash(x, y, t, t0, n=6, k=1.0, dur=.45, seed=0):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return ""
    o = []
    for i in range(n):
        a = -math.pi * (.12 + .76 * (i + rnd(seed + i) * .6) / n)
        v = 90 * k * (.7 + .5 * rnd(seed + 3 * i))
        px = x + v * math.cos(a) * u * 1.0
        py = y + v * math.sin(a) * u + 160 * k * u * u
        o.append(props.droplet(px, py, .55 * k * (1 - .4 * u), rot=math.degrees(a) + 90, seed=i))
    return "".join(o)


def expr_of(**kw):
    e = dict(lid=.9, look=(.5, .1), brows="worry", mouth="flat", flush=.0)
    e.update(kw)
    return e


# ═════════════════════════ s01 ═════════════════════════
GX = [200 + 97 * i for i in range(8)]
G_BASE = 1196


def table_row(t, levels, wob_i=-1, k=1.2):
    o = []
    for i, x in enumerate(GX):
        sl = 0.0
        o.append(props.glass(x, G_BASE, k, level=levels[i], slosh=sl + (6 * math.sin(t * 38 + i) if i == wob_i else 0), wet=(i % 2 == 0), seed=i))
    return "".join(o)


def pt_of(x, y, k, rot, lx, ly):
    a = math.radians(rot)
    return (x + k * (lx * math.cos(a) - ly * math.sin(a)), y + k * (lx * math.sin(a) + ly * math.cos(a)))


def frame01(t):
    base_z = 1.36
    if t < .22:
        z = base_z / 1.4 + (base_z - base_z / 1.4) * ease_out(t / .22, 3)
    else:
        z = base_z + .05 * ease_io(clamp((t - .22) / 1.5))
    rot = -3.4 * (1 - ease_out(t / .45, 2.5)) + .5 * math.sin(t * 9) * math.exp(-t * 1.5)
    prog = clamp((t + .05) / 1.5)
    pos = prog * 7.0
    cur = min(7, int(round(pos)))
    jk = 1.15
    jx = GX[0] + (GX[7] - GX[0]) * prog + 30
    jy = 905 + 12 * math.sin(t * 22)
    tilt = 50 + 6 * math.sin(t * 17)
    sp = jug_spout(jx, jy, jk, tilt)
    levels = []
    for i in range(8):
        if i < pos - .5:
            lv = .82
        elif i > pos + .5:
            lv = .0 if i > 1 else .6
        else:
            lv = lerp(.05 if i > 1 else .55, .82, smooth(-.5, .5, pos - i))
        levels.append(lv)
    Dx = lerp(120, 560, prog) - 40
    stride = t * 3.6
    ex = expr_of(lid=1.0, look=(.4 + .4 * math.sin(t * 6), .6), brows="up", mouth="talk", open=.55 + .3 * math.sin(t * 21), smile=.7, flush=.25)
    lean = .12 + .03 * math.sin(t * 8)
    hnd = pt_of(jx, jy, jk, tilt, -92, -92)
    n_t = (hnd[0] - 8, hnd[1] + 8)
    f_t = (Dx - 120, 730 + 26 * math.sin(t * 15))
    d = stand(t, Dx, lean=lean, ha=.05 * math.sin(t * 12), expr=ex, n_t=n_t, f_t=f_t, run=.4, ph=stride, hands={"n": hand_spec(.75, (.5, -.8)), "f": hand_spec(.15, (-.3, -1))},
              bob=-7 * abs(math.sin(2 * math.pi * stride)), hip_dy=-10)
    lg, af, bd, an = dima_layers(d)
    legs_t, top_t = table_parts()
    o = [_ST["kit"], light_k(t), legs_t, lg, af, bd, top_t]
    o.append(table_row(t, levels, wob_i=cur))
    o.append(jug(jx, jy, jk, tilt))
    o.append(an)
    gl_top = G_BASE - 84 * 1.2 + 8
    o.append(stream(sp[0], sp[1], gl_top + 24, 3 * math.sin(t * 40), seed=1))
    for i in range(8):
        o.append(splash(GX[i], gl_top, t, (i - .5) / 7.0 * 1.4 - .05, n=5, k=1.1, seed=i * 7))
    cam = (lerp(330, 730, prog) + 22 * math.sin(t * 5) * math.exp(-t), 1050, z, rot)
    D.set_ink(z)
    return f'<g transform="{lib.cam(*cam)}">{"".join(o)}{motes(t)}</g>'


# ═════════════════════════ общее для питья ═════════════════════════
def rotv(v, a):
    c, sn = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * sn, v[0] * sn + v[1] * c)


def mouth_pt(d, lean, ha, off=(64.0, 92.0)):
    """Рот героя в мире: голова повёрнута на lean/2 + ha."""
    h = d["head"]
    v = rotv(off, lean * .5 + ha)
    return (h[0] + v[0] * S.BS, h[1] + v[1] * S.BS)


def glass_at_mouth(mouth, k, rot_deg, push=0.0):
    """Нижний центр стакана, чтобы его край лёг на рот (rot — по часовой, 0 — вертикально); push — сдвиг вдоль оси к лицу."""
    a = math.radians(rot_deg)
    rim = (0.0, -props.GLASS_H * k)
    v = rotv(rim, a)
    return (mouth[0] - v[0] - push * math.sin(a) * 0, mouth[1] - v[1])


def hand_pt_on_glass(org, k, rot_deg, lx, ly):
    a = math.radians(rot_deg)
    v = rotv((lx * k, ly * k), a)
    return (org[0] + v[0], org[1] + v[1])


def back_counter_glasses(n=5, x0=150, step=130, k=1.2, levels=None):
    return "".join(props.glass(x0 + step * i, 1034, k, level=0.0 if levels is None else levels[i], seed=20 + i, wet=(i % 2 == 1)) for i in range(n))


# ═════════════════════════ s03 ═════════════════════════
def frame03(t):
    tt = t - 3.24
    T_SILU = T[12]                    # «силу» 5.18
    lift = smooth(3.24, 3.78, t)
    drink = smooth(3.7, 4.95, t)
    pre = smooth(4.85, 5.1, t)
    cough = clamp((t - T_SILU) / .45)
    cough_on = t >= T_SILU
    puffk = smooth(4.55, 5.1, t) * (1 - smooth(T_SILU, T_SILU + .12, t))
    gulp = max(0.0, math.sin((t - 3.9) * 2 * math.pi * 2.1)) ** 3 * smooth(3.9, 4.0, t) * (1 - smooth(4.9, 5.0, t))
    Dx = 560
    lean = .08 - .05 * drink + .1 * cough_on * (1 - ease_out(cough)) + .02 * math.sin(t * 9) * (1 - lift)
    ha = -.34 * drink * (1 - pre * .55) + (.3 * math.exp(-(t - T_SILU) * 6) * (t >= T_SILU)) + .03 * gulp
    shake = (7 * math.sin(t * 58) * math.exp(-(t - T_SILU) * 5) * cough_on, 6 * math.sin(t * 49 + 1) * math.exp(-(t - T_SILU) * 5) * cough_on)
    ex = expr_of(lid=1.0, look=(.2, -.7 * drink), brows="worry", mouth="flat" if not cough_on else "talk", open=.9 * (1 - cough * .3), smile=0, flush=.2 + .7 * drink,
                 puff=puffk, bulge=.2 + .35 * (pre + (1 - cough) * cough_on * .5), closed=0.0 if not cough_on else .4 * math.sin(t * 30) ** 2)
    # первый проход, чтобы узнать, где рот; руки пересчитаются во втором
    def build(n_t, f_t):
        return stand(t, Dx, lean=lean, ha=ha, expr=ex, n_t=n_t, f_t=f_t, hands={"n": hand_spec(.78, (.2, -1)), "f": hand_spec(.7, (.3, -1))},
                     bob=-4 * gulp + 3 * math.sin(t * 6), hip_off=None if False else 0.0) if False else stand(
            t, Dx, lean=lean, ha=ha, expr=ex, n_t=n_t, f_t=f_t, hands={"n": hand_spec(.8, (.1, -1)), "f": hand_spec(.7, (.4, -1))}, bob=-4 * gulp + 3 * math.sin(t * 6),
            head_off=(0, 3 * gulp))
    d0 = build((Dx + 230, 1050), (Dx + 160, 1040))
    mp = mouth_pt(d0, lean, ha)
    k = 1.75
    rot_d = lerp(-12, -104, drink) + 34 * pre
    rot_d += 55 * (1 - ease_out(cough, 2)) * cough_on * 0   # после кашля стакан уходит вниз
    org_up = glass_at_mouth(mp, k, rot_d)
    org_up = (org_up[0] + 70 * pre, org_up[1] + 50 * pre)
    org_tab = (Dx + 250, 1190)
    after = smooth(T_SILU - .02, T_SILU + .35, t) * cough_on
    org_low = (Dx + 280, 1130)
    org = (lerp(org_tab[0], org_up[0], lift), lerp(org_tab[1], org_up[1], lift))
    org = (lerp(org[0], org_low[0], after), lerp(org[1], org_low[1], after))
    rot_g = lerp(0, rot_d, lift)
    rot_g = lerp(rot_g, -8, after)
    lvl = .94 * (1 - .93 * drink) if not cough_on else .02
    n_h = hand_pt_on_glass(org, k, rot_g, 20, -56)
    f_h = hand_pt_on_glass(org, k, rot_g, -4, -14)
    d = build((n_h[0] + 8, n_h[1] + 6), (f_h[0] - 6, f_h[1] + 14))
    lg, af, bd, an = dima_layers(d)
    legs_t, top_t = table_parts()
    o = [_ST["kit"], light_k(t), back_counter_glasses(4, 760, 120, 1.1), legs_t, lg, af, bd, top_t]
    # пустые стаканы на столе перед Димой
    for i, x in enumerate((130, 270, 640, 800, 960)):
        o.append(props.glass(x, G_BASE + 4, 1.2, level=0.0, seed=40 + i, tilt=(-6 if i == 2 else 0)))
    o.append(props.glass(org[0], org[1], k, level=lvl, tilt=rot_g, slosh=5 * math.sin(t * 30) * drink, wet=True, seed=3))
    o.append(an)
    # водяной бунт у рта при кашле
    mp2 = mouth_pt(d, lean, ha)
    if cough_on:
        u = (t - T_SILU)
        for i in range(26):
            a = math.radians(-50 + 100 * rnd(i + 3) + 10)
            v = 700 * (.4 + .9 * rnd(i + 8))
            px = mp2[0] + 30 + v * math.cos(a) * u
            py = mp2[1] + v * math.sin(a) * u * .5 + 620 * u * u
            if u < .7:
                o.append(props.droplet(px, py, .8 - .4 * u + .25 * rnd(i), rot=math.degrees(a) + 90, seed=i))
    cx_ = 690 + shake[0]
    cam = (cx_, 880 + shake[1], 1.95 + .12 * ease_io(clamp(tt / 1.8)) + .05 * math.exp(-(t - T_SILU) * 6) * cough_on, 1.0 * math.sin(t * 7) * cough_on * math.exp(-(t - T_SILU) * 4))
    D.set_ink(cam[2])
    return f'<g transform="{lib.cam(*cam)}">{"".join(o)}{motes(t, seed=5)}</g>'


# ═════════════════════════ сидящий Дима и мелочи ═════════════════════════
def sit(t, x, hip_y, *, lean=.05, ha=0.0, expr=None, n_t, f_t, hands=None, head_off=(0, 0), bob=0.0, fx=(215, 190), floor=1468, torso_k=1.0, sn=None, sf=None):
    e = expr_of()
    if expr:
        e.update(expr)
    hands = hands or {"n": hand_spec(.35), "f": hand_spec(.35)}
    shx = x + 240 * math.sin(lean) + 6
    sn = sn if sn is not None else (-1 if n_t[0] >= shx else 1)
    sf = sf if sf is not None else (-1 if f_t[0] >= shx else 1)
    p = dict(hip=(x, hip_y + bob), scale=S.BS, lean=lean, torso_k=torso_k, feet={"n": ((x + fx[0], floor), 0.0), "f": ((x + fx[1], floor - 5), 0.0)},
             arms={"n": ("ik", n_t, sn), "f": ("ik", f_t, sf)}, hands=hands, expr=e, head_ang=ha, head_off=head_off, hood=0.0, strings=(0, 0))
    d = people.draw(p, "dima")
    d["x"], d["sx"] = x, 1.0
    return d


def steam(x, y, t, n=3, k=1.0, seed=0):
    o = []
    for j in range(n):
        ph = t * 1.1 + j * 1.9
        u = (ph) % 1.0
        pts = [(x + (j - 1) * 22 * k + 9 * math.sin(ph * 3 + q * .9), y - q * 24 * k - u * 20) for q in range(6)]
        o.append(line(pts, 7 * k, "#FFFFFF", taper=.8, wmin=.1, seed=9700 + seed * 5 + j, peak=.4))
    return "".join(o)


def apple(x, y, k=1.0):
    o = [blob(ellipse_pts(x + 4, y + 2, 38 * k, 7 * k, 12), "#000000", .0)]
    body = [(x, y - 62 * k, 1), (x + 30 * k, y - 70 * k), (x + 46 * k, y - 36 * k), (x + 30 * k, y - 4 * k), (x, y - 10 * k, 1), (x - 30 * k, y - 4 * k), (x - 46 * k, y - 36 * k),
            (x - 30 * k, y - 70 * k)]
    o.append(shape(body, "#D8453A", blob([(x + 14 * k, y - 66 * k), (x + 46 * k, y - 36 * k), (x + 30 * k, y - 4 * k), (x + 8 * k, y - 12 * k)], "#A9302A", .9) +
                   blob(ellipse_pts(x - 22 * k, y - 46 * k, 5 * k, 10 * k, 8), "#FFD8CC"), w=3.6, seed=9800))
    o.append(line([(x, y - 62 * k), (x + 4 * k, y - 84 * k)], 5, "#5B3A22", taper=.1, wmin=.8, seed=9801))
    o.append(shape([(x + 6 * k, y - 80 * k), (x + 34 * k, y - 96 * k), (x + 30 * k, y - 76 * k)], "#5FA05A", "", w=3, seed=9802))
    return "".join(o)


def soup_bowl(x, y, k, t, ripple=0.0, spoon_in=0.0):
    """Глубокая тарелка с оранжевым супом (дно в x,y): ширина 220·k."""
    o = []
    RX, RY, HH = 110, 20, 62
    body = [(-RX, -HH, 1), (RX, -HH, 1), (RX - 12, -34), (RX - 36, -10), (RX - 56, 0, 1), (-RX + 56, 0, 1), (-RX + 36, -10), (-RX + 12, -34)]
    inn = blob([(RX * .3, -HH), (RX, -HH), (RX - 12, -34), (RX - 36, -10), (RX - 56, 0), (RX * .25, 0)], "#DDD3C0") + blob(rect_pts(-RX - 4, -HH, RX + 4, -HH + 12), "#4F7FA8")
    o.append(shape(body, "#F7F2E6", inn, w=3.8, seed=9810))
    rim = ellipse_pts(0, -HH, RX, RY, 24)
    rin = blob(ellipse_pts(0, -HH + 1, RX - 8, RY - 4, 22), "#E8A24A")
    rin += blob(ellipse_pts(-12, -HH + 3, RX - 40, RY - 11, 20), "#F0B866")
    for j, (cx, cy) in enumerate(((-52, 2), (-8, -3), (40, 4), (66, -2))):
        rin += blob(ellipse_pts(cx + 3 * math.sin(t * 2 + j), -HH + cy + 2, 11, 5, 8), "#E0672A")
    for j in range(3):
        rin += line([(-70 + j * 50, -HH + 5), (-50 + j * 50 + 6 * math.sin(t * 3 + j), -HH + 1), (-30 + j * 50, -HH + 6)], 3.4, "#F7D98E", taper=.5, wmin=.3, seed=9820 + j)
    o.append(shape(rim, "#F7F2E6", rin, w=3.4, seed=9811))
    return f'<g transform="translate({f(x)} {f(y)}) scale({k:.4f})">{"".join(o)}</g>'


def spoon(tip, ang_deg, scale=1.0, soup=True):
    """Ложка: tip — кончик (чаша), ang — направление от чаши к ручке (рад. по часовой, 0 — вправо)."""
    a = math.radians(ang_deg)
    ux, uy = math.cos(a), math.sin(a)
    L = 150 * scale
    h1 = (tip[0] + ux * 18 * scale, tip[1] + uy * 18 * scale)
    h2 = (tip[0] + ux * L, tip[1] + uy * L)
    o = [line([h1, h2], 10, INK, taper=.15, wmin=.7, seed=9830), line([h1, h2], 5, "#C9CED4", taper=.15, wmin=.7, seed=9831)]
    o.append(shape(ellipse_pts(tip[0] + ux * 8 * scale, tip[1] + uy * 8 * scale, 24 * scale, 15 * scale, 14, rot=ang_deg), "#C9CED4",
                   blob(ellipse_pts(tip[0] + ux * 8 * scale, tip[1] + uy * 8 * scale, 17 * scale, 9 * scale, 12, rot=ang_deg), "#E8A24A") if soup else "", w=3.4, seed=9832))
    return "".join(o)


# ═════════════════════════ s07 ═════════════════════════
def frame07(t):
    T0 = 11.0
    u = clamp((t - 10.8) / 2.2)
    Dx = 300
    per = .95
    ph = ((t - 10.8) / per) % 1.0
    # 0–.25 зачерпнул, .25–.6 несёт ко рту, .6–.8 хлебает, .8–1 назад
    to_mouth = smooth(.22, .55, ph) * (1 - smooth(.78, 1.0, ph))
    slurp = smooth(.55, .62, ph) * (1 - smooth(.78, .86, ph))
    lean = .1 + .05 * to_mouth + .01 * math.sin(t * 7)
    ha = .04 * to_mouth + .02 * math.sin(t * 5)
    ex = expr_of(lid=.75, look=(.65, .35 - .5 * to_mouth), brows="calm", mouth="smile" if slurp < .3 else "talk", open=.5 * slurp + .1, smile=.6, blush=.5)
    bowl_c = (Dx + 400, 1160)
    sp_dip = (bowl_c[0] - 18, bowl_c[1] - 58)
    # вторая сборка: узнать рот
    def mk(n_t):
        return sit(t, Dx, 1244, lean=lean, ha=ha, expr=ex, n_t=n_t, f_t=(Dx + 290, 1135), hands={"n": hand_spec(.82, (-.7, -.4)), "f": hand_spec(.3, (.6, .5))},
                   bob=2 * math.sin(t * 6), head_off=(0, 2 * slurp))
    d0 = mk((Dx + 380, 1050))
    mp = mouth_pt(d0, lean, ha)
    tip_mouth = (mp[0] + 14, mp[1] + 14)
    tip = (lerp(sp_dip[0], tip_mouth[0], to_mouth), lerp(sp_dip[1], tip_mouth[1], to_mouth) - 36 * math.sin(math.pi * clamp(to_mouth)) * (1 - slurp))
    ang = lerp(-20, 6, to_mouth) * 0 + 8 + 14 * (1 - to_mouth)   # ручка уходит вправо (и чуть вниз)
    wr = (tip[0] + 110 * math.cos(math.radians(ang)) + 6, tip[1] + 110 * math.sin(math.radians(ang)) + 4)
    d = mk(wr)
    lg, af, bd, an = dima_layers(d)
    ls, ts = table_parts(Dx + 230, 1060, 1150, 1215)
    o = [_ST["kit"], light_k(t), room_chair(Dx), ls, lg, af, bd, ts]
    o.append(apple(Dx + 590, 1168, 1.1))
    o.append(room_cup(Dx + 680, 1172, t))
    o.append(soup_bowl(bowl_c[0], 1190, 1.1, t))
    o.append(spoon(tip, ang, 1.0, soup=to_mouth < .96 and (to_mouth > .02 or ph > .1)))
    o.append(an)
    o.append(steam(bowl_c[0], 1112, t, 3, 1.1, 1))
    # капельки «вода и в еде»: поднимаются над тарелкой, мерцают
    for j in range(5):
        pu = ((t * .55 + j * .2) % 1.0)
        px = bowl_c[0] + (j - 2) * 30 + 10 * math.sin(t * 2 + j)
        py = 1050 - pu * 150
        sc = 1.0 * math.sin(math.pi * clamp(pu * 1.05)) ** .6
        if sc > .15:
            o.append(props.droplet(px, py, 1.25 * sc, seed=j))
    o.append(props.shine_star(bowl_c[0] + 80, 940, 1.2, (t * 1.6) % 1.0))
    cam = (lerp(600, 640, u), lerp(1070, 1040, u), 1.36 + .07 * u, -.5 + 1.0 * u)
    D.set_ink(cam[2])
    out = f'<g transform="{lib.cam(*cam)}">{"".join(o)}{motes(t, seed=9)}</g>'
    return out


def room_chair(x, seat=1248):
    import room as R
    return R.chair(x, seat, 1, 9900)


def room_cup(x, y, t):
    import room as R
    return R.cup(x, y, 1.05, latte=False, steam_t=t, heart=False)


# ═════════════════════════ комната: диван ═════════════════════════
def sofa_static_back():
    o = []
    o.append(shape([(20, 930, 1), (210, 930, 1), (222, 1370, 1), (20, 1370, 1)], "#4F8C82", blob([(150, 930), (210, 930), (222, 1370), (150, 1370)], "#3A6E66", .8), w=5, seed=9910))
    o.append(shape(rect_pts(20, 1280, 520, 1384, 14), "#5F9A8E", blob(rect_pts(20, 1356, 520, 1384), "#3A6E66", .9) + blob(rect_pts(480, 1280, 520, 1384), "#4F8C82", .8), w=5, seed=9911))
    o.append(shape(rect_pts(190, 1250, 512, 1296, 20), "#74B0A3", blob(rect_pts(190, 1280, 512, 1296), "#4F8C82", .9), w=4.4, seed=9912))
    o.append(shape([(140, 1010, 1), (250, 1020, 1), (270, 1240), (140, 1250)], "#E8B04A", blob([(220, 1014), (250, 1020), (270, 1240), (210, 1246)], "#C48A2A", .8), w=4.4, seed=9916))
    for k, x in enumerate((50, 470)):
        o.append(shape(rect_pts(x, 1384, x + 26, 1440, 4), "#6B4A2E", "", w=3.6, seed=9914 + k))
    return "".join(o)


def sofa_static_front():
    return ""


def side_table(x, t_y=1215):
    o = []
    o.append(shape([(x - 20, t_y + 12, 1), (x + 20, t_y + 12, 1), (x + 16, 1440, 1), (x - 16, 1440, 1)], "#8B5A36", blob([(x + 2, t_y + 12), (x + 20, t_y + 12), (x + 16, 1440), (x + 2, 1440)], "#6B4224", .8), w=3.8, seed=9930))
    o.append(shape(ellipse_pts(x, t_y, 112, 26, 18), "#C88A58", blob(ellipse_pts(x, t_y + 8, 104, 14, 16), "#A8693F", .8), w=4.4, seed=9931))
    return "".join(o)


def book(cx, cy, k=1.0, tilt=0.0, page_t=0.0, seed=0):
    """Раскрытая книга, корешком вниз, обращена к читателю: две страницы со строками-штрихами (букв нет)."""
    o = []
    cover = [(-118, 6, 1), (118, 6, 1), (122, 14, 1), (-122, 14, 1)]
    o.append(shape(cover, "#B9694C", "", w=4, seed=9940 + seed))
    pl = [(-114, -88, 1), (-6, -80), (-6, 6, 1), (-114, 6, 1)]
    pr = [(6, -80), (114, -88, 1), (114, 6, 1), (6, 6, 1)]
    for pts, sd, xs in ((pl, 1, -1), (pr, 2, 1)):
        ln = ""
        for j in range(5):
            y = -64 + j * 14
            x0, x1 = (-96, -26) if xs < 0 else (26, 96)
            ln += line([(x0, y), (x1 - 10 * ((j + seed) % 3), y + 1)], 4, "#9C96A6", taper=.2, wmin=.7, seed=9950 + sd * 9 + j, op=.9)
        o.append(shape(pts, "#F7F2E4", ln + blob([(-6, -80), (6, -80), (6, 6), (-6, 6)], "#D8CFB8"), w=3.6, seed=9941 + sd))
    return f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(tilt)}) scale({k:.4f})">{"".join(o)}</g>'


def drop_icon(x, y, u, t):
    """Значок «хочу пить»: капля в кружке с тремя лучами, вспыхивает пружиной."""
    if u <= 0:
        return ""
    sc = spring(u, 2.4, 5.0)
    o = [props.droplet(0, 0, 3.4, seed=3)]
    ring = ellipse_pts(0, 6, 62, 62, 20)
    o.insert(0, shape(ring, "#FFFFFF", "", w=4.2, seed=9960))
    for i, ang in enumerate((-150, -90, -30)):
        a = math.radians(ang)
        o.append(line([(78 * math.cos(a), 6 + 78 * math.sin(a)), (112 * math.cos(a), 6 + 112 * math.sin(a))], 8, props.C_WATER, taper=.5, wmin=.3, seed=9970 + i, peak=.5))
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(max(0.01, sc))}) rotate({f(6 * math.sin(t * 9))})">{"".join(o)}</g>'


def frame11(t):
    T0 = 19.1
    T_HOCHETSYA = T[50]       # 20.96
    u = clamp((t - 18.9) / 2.8)
    read = 1 - smooth(20.7, 21.05, t)
    reach = smooth(T_HOCHETSYA + .02, T_HOCHETSYA + .45, t)
    lift = smooth(T_HOCHETSYA + .45, T_HOCHETSYA + .78, t)
    Dx = 440
    lean = .06 + .02 * math.sin(t * 2.3) + .13 * reach
    gaze = .5 + .4 * math.sin(t * 3.1) * read
    look_up = smooth(20.55, 20.9, t)
    ex = expr_of(lid=.62 + .3 * look_up, look=(.5 + .35 * lift, .55 * read - .3 * look_up), brows="calm" if look_up < .5 else "up", mouth="flat" if t < 21.4 else "smile", smile=.5, blush=.3 * lift)
    gl_c = (Dx + 360, 1196)
    book_c = (Dx + 360, 1130 + 10 * (1 - read) + 150 * (1 - read) * smooth(20.95, 21.25, t))
    book_c = (Dx + 250, lerp(1130, 1300, smooth(20.95, 21.25, t)))
    n_book = (Dx + 190, book_c[1] + 10)
    f_book = (Dx + 196, book_c[1] - 20)
    def mk(n_t, ha_=0.0):
        return sit(t, Dx, 1290, lean=lean, ha=ha_, expr=ex, n_t=n_t, f_t=f_book if reach < .5 else (Dx + 230, 1230), hands={"n": hand_spec(.78, (.5, -.6)), "f": hand_spec(.4, (.5, -.3))},
                   bob=1.5 * math.sin(t * 2.4), head_off=(0, 0), fx=(205, 180), floor=1440)
    ha0 = 0.04 * math.sin(t * 2) - .12 * look_up * 0
    d0 = mk(n_book, ha0)
    mp = mouth_pt(d0, lean, ha0)
    gk = 1.15
    grab = (gl_c[0] - 20, gl_c[1] - 70 * gk)
    tipg = (mp[0] + 40, mp[1] + 8)
    # стакан едет со столика ко рту: ось вверх -> наклон
    rot_g = lerp(0, -62, lift)
    org_up = glass_at_mouth(mp, gk, rot_g)
    org_up = (org_up[0] + 18, org_up[1] + 8)
    org = (lerp(gl_c[0], org_up[0], lift), lerp(gl_c[1], org_up[1], lift))
    hand_g = hand_pt_on_glass(org, gk, rot_g, 20, -44)
    n_t = (lerp(n_book[0], hand_g[0] + 6, reach), lerp(n_book[1], hand_g[1] + 8, reach))
    d = mk(n_t, ha0)
    lg, af, bd, an = dima_layers(d)
    o = [D_room(t), f'<g transform="translate(150 0)">{_ST["sofa_b"]}</g>', side_table(gl_c[0]), lg, af, bd]
    o.append(_ST["sofa_f"])
    o.append(props.glass(org[0], org[1], gk, level=.7 - .08 * lift, tilt=rot_g, wet=True, seed=11))
    o.append(book(book_c[0], book_c[1], .95, -4, seed=1) if reach < .9 or True else "")
    o.append(an)
    # значок «хочу пить»
    hp = head_w(d)
    o.append(drop_icon(hp[0] + 40, hp[1] - 215, (t - T_HOCHETSYA) / .5, t))
    cam = (lerp(690, 670, u), lerp(1060, 1040, u), 1.78 + .08 * ease_io(u), 1.2 * (1 - u))
    D.set_ink(cam[2])
    out = f'<g transform="{lib.cam(*cam)}">{"".join(o)}{S.sun_motes(t)}</g>'
    return whip(out, t, T0)


def D_room(t):
    return _ST["room_day"]


# ═════════════════════════ стол Димы днём: s13, s14 ═════════════════════════
BOT_X, BOT_Y, BOT_K = 600, 1146, 1.45


def desk_room(t):
    return "".join([_ST["room_day"], _ST["desk_legs"], f'<g>{S.window_sun(t, 1.0)}</g>', D.lamp(t), ])


def notebook(x, y, t, flutter=1.0):
    """Блокнот на столе, лежит раскрытый (вид сверху-спереди), карандаш рядом; уголок страницы чуть шевелится."""
    o = [blob(ellipse_pts(x + 8, y + 12, 150, 14, 14), "#2a1408", .0)]
    cover = [(x - 150, y - 12, 1), (x + 150, y - 14, 1), (x + 176, y + 30, 1), (x - 176, y + 32, 1)]
    o.append(shape(cover, "#4F7FA8", "", w=4, seed=9980))
    pl = [(x - 166, y - 8, 1), (x - 4, y - 14, 1), (x - 4, y + 28, 1), (x - 168, y + 28, 1)]
    pr = [(x + 4, y - 14, 1), (x + 160, y - 8, 1), (x + 166, y + 28, 1), (x + 4, y + 28, 1)]
    for sd, pts, xs in ((1, pl, -1), (2, pr, 1)):
        ln = "".join(line([(x + xs * 20 + (0 if xs > 0 else -126), y + 4 + j * 8), (x + xs * 20 + (116 if xs > 0 else -10), y + 4 + j * 8)], 2.6, "#A9A4B8", taper=.2, wmin=.7, seed=9990 + sd * 7 + j) for j in range(3))
        o.append(shape(pts, "#F7F2E4", ln, w=3.4, seed=9981 + sd))
    fl = 6 * math.sin(t * 3.1) * flutter
    o.append(shape([(x + 160, y - 8, 1), (x + 120 + fl, y - 22 - fl, 1), (x + 126, y + 8, 1)], "#EDE5D0", "", w=3, seed=9985))
    o.append(shape([(x - 150, y + 12, 1), (x - 10, y + 6, 1), (x - 6, y + 14, 1), (x - 150, y + 20, 1)], "#E8B04A", "", w=3.2, seed=9986))
    return "".join(o)


def bottle_drop_state(t, t_land):
    """Положение бутылки при падении на стол: (y_центра_дна, sx, sy, tilt, shadow_k). До падения — спрятана."""
    fall = .34
    t0 = t_land - fall
    if t < t0:
        return None
    if t < t_land:
        u = (t - t0) / fall
        y = BOT_Y - 560 * (1 - u * u)
        return y, .94, 1.08, 6 * (1 - u), u
    d = t - t_land
    sq = math.exp(-d * 10) * math.cos(d * 38)
    hop = 26 * abs(math.sin(d * 14)) * math.exp(-d * 6) if d < .5 else 0
    return BOT_Y - hop, 1 + .12 * sq, 1 - .14 * sq, 0.0, 1.0


def frame13(t):
    T0 = 23.8
    T_B = T[63]
    u = clamp((t - 23.6) / 3.2)
    st = bottle_drop_state(t, T_B)
    o = [desk_room(t), _ST["desk_top"], D.mug(t) if False else ""]
    o.append(notebook(800, 1138, t))
    if st:
        y, sx, sy, tl, shk = st
        o.append(f'<ellipse cx="{BOT_X + 8}" cy="{BOT_Y + 4}" rx="{50 * (.4 + .9 * shk):.1f}" ry="{9 * (.4 + .9 * shk):.1f}" fill="#7b4a26" opacity="{.35 + .3 * shk:.2f}"/>')
        o.append(f'<g transform="translate({BOT_X} {y:.2f}) scale({sx:.4f} {sy:.4f}) translate({-BOT_X} {-y:.2f})">{props.bottle(BOT_X, y, BOT_K, level=.85, tilt=tl, drops=(t > T_B + .15), seed=4)}</g>')
        d = t - T_B
        if d > -.02:
            o.append(dust(t, T_B, BOT_X, BOT_Y + 2, 7, .5))
            # блик по стенке: белая полоса бежит вверх, и две вспышки-звезды
            if .08 < d < .9:
                gp = ease_io((d - .08) / .8)
                yy = BOT_Y - 20 * BOT_K - gp * 85 * BOT_K
                o.append(line([(BOT_X - 17 * BOT_K, yy + 18), (BOT_X - 13 * BOT_K, yy - 14)], 6, "#FFFFFF", taper=.4, wmin=.3, seed=9995))
            o.append(props.shine_star(BOT_X - 22 * BOT_K, BOT_Y - 110 * BOT_K, 1.6, clamp((d - .05) / .5)))
            o.append(props.shine_star(BOT_X + 26 * BOT_K, BOT_Y - 58 * BOT_K, 1.2, clamp((d - .35) / .5)))
            if d > .25:
                dp = clamp((d - .25) / .9)
                o.append(props.droplet(BOT_X + 15 * BOT_K, BOT_Y - 92 * BOT_K + dp * 56 * BOT_K, .9, seed=6))
    else:
        # предчувствие: тень от лампы дрожит на столе, пылинки в луче
        pass
    o.append(S.sun_motes(t, box=(700, 520, 1250, 1130)))
    cam = (lerp(800, 780, u), lerp(1040, 1030, u), 1.9 + .35 * ease_io(u), 1.4 * (1 - u) - .6 * u)
    D.set_ink(cam[2])
    return f'<g transform="{lib.cam(*cam)}">{"".join(o)}</g>'


def small_cap(x, y, rot=0.0):
    pts = [(-12.5, -10, 1), (12.5, -10, 1), (12.5, 10, 1), (-12.5, 10, 1)]
    inn = blob(rect_pts(4, -10, 13, 10), props.C_CAP_SH)
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({BOT_K})">{shape(pts, props.C_CAP, inn, w=3.2, seed=9996)}</g>'


def frame14(t):
    T0 = 26.6
    T_P, T_H = T[69], T[71]            # 27.32 «пьёт», 28.0 «хочет»
    u = clamp((t - 26.4) / 2.7)
    reach = smooth(26.5, 26.92, t)
    uncap = smooth(26.9, 27.05, t)
    up = smooth(27.0, 27.4, t) * (1 - smooth(T_H - .15, T_H + .25, t))
    back = smooth(T_H + .15, T_H + .75, t)
    drink = smooth(27.35, 27.6, t) * (1 - smooth(T_H - .1, T_H + .15, t))
    lean = .1 - .03 * up
    ha = -.16 * drink + .03 * math.sin(t * 1.7)
    smile = smooth(T_H - .05, T_H + .25, t)
    ex = expr_of(lid=.66 - .2 * drink, look=(.92, -.12), brows="calm", mouth="smile" if smile > .1 or up < .5 else "flat", smile=.2 + .8 * smile, blush=.4 * smile,
                 closed=0.0)
    hold = (BOT_X + 4, BOT_Y - 66 * BOT_K)

    def mk(n_t):
        r = mk0(n_t)
        r["x"], r["sx"] = 250, 1.0
        return r

    def mk0(n_t):
        return D.dima(lean, {"n": ("ik", n_t), "f": ("ik", (560, S.FLOOR_Y if False else 1120))}, {"n": hand_spec(.82, (0, -1)), "f": D.fist(.35)}, ex, head_ang=ha,
                      head_off=(0, 0), hip_off=(0, 2 * math.sin(t * 1.6)))
    d0 = mk((hold[0] - 40, hold[1] + 40))
    mp = mouth_pt(d0, lean, ha)
    rot_b = lerp(0, -118, smooth(.0, 1.0, drink)) * 1.0 + (-18 * (up - drink) if False else 0)
    rot_b = -20 * up * (1 - drink) + (-100) * drink
    rim = (0.0, -124 * BOT_K)
    a = math.radians(rot_b)
    v = rotv(rim, a)
    org_up = (mp[0] + 6 - v[0], mp[1] + 6 - v[1])
    org_desk = (BOT_X, BOT_Y)
    liftk = up
    org = (lerp(org_desk[0], org_up[0], liftk), lerp(org_desk[1], org_up[1], liftk))
    rot_g = rot_b * 1.0
    hnd = hand_pt_on_glass(org, BOT_K, rot_g, 22, -62)
    n_t = (lerp(hold[0] - 60, hnd[0] - 6, reach), lerp(hold[1] + 70, hnd[1] + 10, reach))
    d = mk(n_t)
    lg, af, bd, an = dima_layers(d)
    # крышка: на «откручивании» подскакивает и ложится на стол
    cap_up = uncap
    capped = t < 26.92
    o = [desk_room(t)]
    o.append(ROOM.chair(250, 1266, 1, 2300))
    o.extend([_ST["desk_legs"] if False else "", lg, af, bd, _ST["desk_top"]])
    bub = ""
    if t > T_P - .05 and drink > .2:
        for j in range(4):
            bu = ((t - T_P) * 2.4 + j * .27) % 1.0
            bub += f'<circle cx="{(-6 + 7 * math.sin(j * 2 + t * 5)):.1f}" cy="{(-30 - bu * 70):.1f}" r="{(3 + 2 * j % 3):.1f}" fill="#FFFFFF"/>'
    bt = props.bottle(org[0], org[1], BOT_K, level=.85 - .22 * drink - .1 * (1 if t > T_H else 0), tilt=rot_g, cap=capped, cap_open=cap_up if capped else 0, drops=True, seed=4)
    o.append(bt)
    if bub:
        o.append(f'<g transform="translate({f(org[0])} {f(org[1])}) rotate({f(rot_g)}) scale({BOT_K})">{bub}</g>')
    if not capped:
        cp = clamp((t - 26.92) / .38)
        cx_ = lerp(BOT_X + 10, 760, ease_out(cp, 1.4))
        cy_ = BOT_Y - 4 - 4 - 160 * math.sin(math.pi * cp) + 0
        if cp < 1:
            o.append(small_cap(cx_, cy_ if cp < 1 else BOT_Y, 720 * cp))
        else:
            o.append(small_cap(760, BOT_Y - 10 * BOT_K, 0))
        o.append(dust(t, 27.3, 760, BOT_Y, 5, .35))
    o.append(an)
    # глоток: булькающие штрихи у горла
    if drink > .3:
        hp = head_w(d)
        gp = abs(math.sin((t - T_P) * 2 * math.pi * 2.0)) ** 2
        for j in range(2):
            o.append(line([(hp[0] + 30 + 12 * j, hp[1] + 82 + 16 * j), (hp[0] + 40 + 12 * j, hp[1] + 78 + 14 * j - 10 * gp)], 6, props.C_WATER, taper=.5, wmin=.3, seed=9997 + j))
    cam = (lerp(500, 540, u), lerp(1040, 1020, u), 1.5 + .05 * ease_io(u) + .04 * math.exp(-(t - T_P) * 8) * (t >= T_P), -.8 + 1.0 * u + 1.2 * math.sin(t * 40) * math.exp(-(t - T_P) * 12) * (t >= T_P))
    D.set_ink(cam[2])
    return f'<g transform="{lib.cam(*cam)}">{"".join(o)}{S.sun_motes(t, box=(600, 520, 1250, 1130))}</g>'


# ═════════════════════════ диспетчер ═════════════════════════
def frame(sid, t):
    if not _ST.get("init"):
        D.DAY[0] = True
        _ST["kit"] = kitchen_static()
        _ST["room_day"] = D.room_static()
        _ST["desk_legs"], _ST["desk_top"] = D.desk_static()
        _ST["sofa_b"] = sofa_static_back()
        _ST["sofa_f"] = sofa_static_front()
        lib.static_done()
        _ST["init"] = True
    lib.dyn_begin()
    body = {"s01": frame01, "s03": frame03, "s07": frame07, "s11": frame11, "s13": frame13, "s14": frame14}[sid](t)
    return svg(f'<rect width="1920" height="1920" fill="#2a1f2a"/>{body}')
