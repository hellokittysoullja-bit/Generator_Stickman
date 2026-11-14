"""Рилс 57 группа B: s02 (1.4–3.44) восемь стаканов в ряд наливаются слева направо кувшином, s06 (8.7–11.0) миф: восемь стаканов на двух полках дрожат
на «правила» (9.41), на «нет» (10.32) жирный красный крест перечёркивает, стаканы разъезжаются. Предметы — common/props.py."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "story", "common"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import fxprops as fp  # noqa: E402
import lib  # noqa: E402
import props  # noqa: E402
from lib import INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, spring, svg  # noqa: E402

SEED = 8000


def lerp(a, b, u):
    return a + (b - a) * u


def rnd(i):
    return abs(math.sin(i * 12.9898) * 43758.5453) % 1.0


# ═════════════════════════ кувшин, струя, капли (тот же вид, что в сцене s01 группы A) ═════════════════════════
def jug(x, y, k=1.0, rot=0.0, level=.7):
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
        px = x + v * math.cos(a) * u
        py = y + v * math.sin(a) * u + 160 * k * u * u
        o.append(props.droplet(px, py, .55 * k * (1 - .4 * u), rot=math.degrees(a) + 90, seed=i))
    return "".join(o)


def hop(t, te, amp, freq=15.0, damp=7.0):
    e = t - te
    if e <= 0:
        return 0.0
    return amp * math.exp(-damp * e) * abs(math.sin(freq * e))


# ═════════════════════════ s02 ═════════════════════════
KG2 = 2.5                     # масштаб стакана
SP2 = 150.0                   # шаг ряда
GY2 = 860.0                   # дно стаканов на столе
GX2 = [540 + (i - 3.5) * SP2 for i in range(8)]
T2 = 1.2                      # начало клипа
DW2 = 0.22                    # на один стакан


def bg_kitchen(light=(540, 360)):
    s = []
    g = lin_grad([(0, "#dcf0f4", 1), (1, "#bfe0ea", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-1500" y="-1500" width="4200" height="{1500 + 900}" fill="url(#{g})"/>')
    for x in range(-1400, 2600, 150):
        s.append(f'<rect x="{x}" y="-1500" width="64" height="{1500 + 900}" fill="#c9e6ee" opacity=".7"/>')
    gl = rad_grad([(0, "#fff8dc", .7), (1, "#fff8dc", 0)], light[0], light[1], 760, 620)
    s.append(f'<rect x="-1500" y="-1500" width="4200" height="3200" fill="url(#{gl})" style="mix-blend-mode:screen"/>')
    return "".join(s)


def table2(y_top=800):
    s = []
    g = lin_grad([(0, "#e3b878", 1), (1, "#c98f4c", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-1500" y="{y_top}" width="4200" height="170" fill="url(#{g})"/>')
    for k in range(7):
        s.append(line([(-1500, y_top + 22 + k * 24), (2700, y_top + 24 + k * 24)], 3, "#a8703a", taper=.05, wmin=.9, seed=SEED + k, op=.5))
    s.append(line([(-1500, y_top), (2700, y_top)], 5, INK, taper=.02, wmin=1, seed=SEED + 20))
    s.append(f'<rect x="-1500" y="{y_top + 170}" width="4200" height="90" fill="#8a5a2e"/>')
    s.append(line([(-1500, y_top + 170), (2700, y_top + 170)], 5, INK, taper=.02, wmin=1, seed=SEED + 21))
    s.append(f'<rect x="-1500" y="{y_top + 260}" width="4200" height="1400" fill="#5d8f9c"/>')
    s.append(line([(-1500, y_top + 260), (2700, y_top + 260)], 5, INK, taper=.02, wmin=1, seed=SEED + 22))
    for k in range(-3, 5):   # дверцы шкафа с ручками
        x = k * 380
        s.append(line([(x, y_top + 260), (x, y_top + 1600)], 5, INK, taper=.02, wmin=1, seed=SEED + 30 + k))
        s.append(blob(rect_pts(x + 28, y_top + 300, x + 352, y_top + 1100, 12), "#6aa0ad"))
        s.append(shape(rect_pts(x + 150, y_top + 320, x + 230, y_top + 346, 12), "#d9d4c6", "", w=3.6, seed=SEED + 40 + k))
    return "".join(s)


def pour_state(t):
    """Кувшин: x носика, номер стакана под ним, доля шага."""
    ph = (t - T2) / DW2
    if ph < 0:
        return GX2[0], 0, 0.0
    i = int(ph)
    if i >= 7:
        return GX2[7], 7, 0.0 if ph < 8 else 1.0
    f_ = ph - i
    mv = smooth(0.62, 1.0, f_)
    return lerp(GX2[i], GX2[i + 1], mv), i, f_


def s02_frame(t):
    s = [bg_kitchen(), table2(GY2 - 60)]
    xs, ci, fr = pour_state(t)
    done = [clamp((t - (T2 + i * DW2 + 0.02)) / 0.2) for i in range(8)]
    pouring = t < T2 + 7 * DW2 + 0.16
    # тени стаканов
    for i in range(8):
        s.append(fp.shadow(GX2[i] + 18, GY2 + 8, 62, 12, .3, 6))
    # вспышки «восемь» / «стаканов» — ряд подпрыгивает
    for i in range(8):
        h = hop(t, 1.92, 16) * (done[i] > .9) + hop(t, 2.29, 24) * (done[i] > .9)
        if t > 3.0:
            h += hop(t, 3.0 + i * 0.03, 12)
        lv = .78 * ease_out(done[i], 2)
        sl = 7 * math.sin(t * 22 + i) * math.exp(-max(0.0, t - (T2 + i * DW2 + .2)) * 2.4) * (done[i] > 0)
        wob = 1.2 * math.sin(t * 6.3 + i * 1.7) if done[i] >= 1 else 0
        s.append(props.glass(GX2[i], GY2 - h, KG2, lv, tilt=wob, slosh=sl, wet=True, seed=i))
    # блики на полных стаканах
    for i in range(8):
        te = T2 + i * DW2 + .26
        if te < t < te + .4:
            s.append(props.shine_star(GX2[i] + 18, GY2 - 150, 2.1, (t - te) / .4))
    # кувшин: носик над текущим стаканом, корпус уходит влево-вверх; струя падает в воду
    JK = 1.9
    rot = 55 + 2.5 * math.sin(t * 9)
    sp0 = jug_spout(0, 0, JK, rot)
    lift = ease_in(clamp((t - 2.97) / 0.45), 1.7)
    rot = rot * (1 - lift) + 8 * lift
    sy = GY2 - 390 + 6 * math.sin(t * 13) - 700 * lift
    jx, jy = xs - sp0[0], sy - sp0[1]
    jlevel = .74 - .38 * clamp((t - T2) / (8 * DW2))
    s.append(jug(jx, jy, JK, rot, jlevel))
    if pouring and fr < 0.74:
        lv = .78 * ease_out(done[ci], 2)
        wy = GY2 - (props.GLASS_H - 12) * KG2 * lv - 8 * KG2 * 0.4
        s.append(stream(xs - 2, sy + 6, wy, 3 * math.sin(t * 40), 22, seed=ci))
    # брызги при начале налива в каждый стакан
    for i in range(8):
        s.append(splash(GX2[i], GY2 - 190, t, T2 + i * DW2 + .04, 7, 1.7, .5, seed=i * 9))
    # у «восемь» и «стаканов» — полоски-акценты по ряду
    for te, nn in ((1.92, 0), (2.29, 1)):
        e = (t - te) / .35
        if 0 < e < 1:
            for i in range(8):
                if done[i] > .9:
                    s.append(fp.burst(GX2[i], GY2 - 110, e, 6, 130, 220, 9, "#ffffff", SEED + 50 + i + nn * 10, a0=-80, spread=160))
    # камера: панорама за кувшином, отъезд на «восемь стаканов», наезд на последнем
    u = ease_io(clamp((t - T2) / 1.75))
    sc = lerp(1.55, 0.9, u)
    cx = lerp(xs * 0.9 + 54, 540, u)
    if t > 2.95:
        v = ease_in(clamp((t - 2.95) / 0.69), 1.6)
        sc = lerp(0.9, 1.85, v)
        cx = lerp(540, GX2[7], v)
    cy = (GY2 - 125) + 60 / sc
    rot = lerp(-3.0, 0.0, u) + (1.4 * math.sin((t - 2.95) * 25) * math.exp(-(t - 2.95) * 3) if t > 2.95 else 0)
    for te, a in ((1.92, .04), (2.29, .06)):
        e = t - te
        if e > 0:
            kk = math.exp(-e * 10)
            sc *= 1 + a * kk
            cy += 12 * kk * math.sin(e * 40)
    return svg(f'<rect width="{W}" height="{H}" fill="#bfe0ea"/><g transform="{cam(cx, cy, sc, rot)}">{"".join(s)}</g>')


# ═════════════════════════ s06 ═════════════════════════
KG6 = 3.5
T6 = 8.5
HIT6_TREM = 9.41
HIT6_NO = 10.32
SH6 = [680.0, 1060.0]        # дно стаканов на полках
GX6 = [540 + (j - 1.5) * 238 for j in range(4)]


def bg_wall6():
    s = []
    g = lin_grad([(0, "#f6e8cc", 1), (1, "#ead2a6", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-1500" y="-1500" width="4200" height="3600" fill="url(#{g})"/>')
    for x in range(-1400, 2600, 160):
        s.append(f'<rect x="{x}" y="-1500" width="60" height="3600" fill="#e1c795" opacity=".5"/>')
    gl = rad_grad([(0, "#fff8dc", .6), (1, "#fff8dc", 0)], 540, 500, 800, 700)
    s.append(f'<rect x="-1500" y="-1500" width="4200" height="3200" fill="url(#{gl})" style="mix-blend-mode:screen"/>')
    return "".join(s)


def shelf6(y, sd):
    s = []
    g = lin_grad([(0, "#d6a263", 1), (1, "#a8703a", 1)], 0, 0, 0, 1)
    s.append(shape(rect_pts(-40, y, 1120, y + 44, 3), f"url(#{g})", "", w=5, seed=SEED + sd))
    s.append(line([(0, y + 14), (1080, y + 14)], 3, "#8a5a2e", taper=.05, wmin=.9, seed=SEED + sd + 1, op=.6))
    for bx in (150, 930):
        s.append(shape([(bx - 18, y + 44, 1), (bx + 18, y + 44, 1), (bx + 18, y + 150, 1), (bx - 60, y + 44 + 8, 1)], "#8a5a2e", "", w=4, seed=SEED + sd + int(bx)))
    return "".join(s)


def glass_motion6(j, row, t):
    """Положение стакана: дрожь на «правила», после «нет» — разъезжаются (вылетают в стороны с вращением)."""
    idx = row * 4 + j
    x, y = GX6[j], SH6[row]
    rot = 0.0
    trem = smooth(HIT6_TREM - 0.02, HIT6_TREM + 0.1, t) * (1 - smooth(HIT6_NO - 0.04, HIT6_NO, t))
    base = 0.5 * (1 - smooth(HIT6_TREM - 0.02, HIT6_TREM + 0.1, t))
    amp = (base + trem * (1.0 + 2.2 * clamp((t - HIT6_TREM) / (HIT6_NO - HIT6_TREM)))) * 1.0
    x += amp * 3.6 * math.sin(t * 61 + idx * 2.1)
    y += -abs(amp) * 3.0 * abs(math.sin(t * 47 + idx))
    rot = amp * 3.0 * math.sin(t * 53 + idx * 1.3)
    e = t - HIT6_NO - 0.12
    if e > 0:
        sgx = -1 if j < 2 else 1
        sgy = -1 if row == 0 else 1
        v = 700 + 200 * rnd(idx)
        ang = math.radians(20 + 18 * rnd(idx + 5))
        x += sgx * v * math.cos(ang) * e * (1 + .4 * (j % 2))
        y += -sgy * v * 0.6 * math.sin(ang) * e + 1100 * e * e
        rot = sgx * (260 + 140 * rnd(idx + 9)) * e
    return x, y, rot, trem


def cross_stroke(p0, p1, u, w, sd):
    """Жирный красный штрих-кисть от p0 к p1: нарисован до доли u (0…1); контур — тёмная тушь."""
    if u <= 0.01:
        return ""
    q = (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u)
    mid = ((p0[0] + q[0]) / 2 + 14 * math.sin(sd), (p0[1] + q[1]) / 2 + 10 * math.cos(sd))
    pts = [p0, mid, q]
    o = line(pts, w + 16, INK, taper=.12, wmin=.5, seed=sd, peak=.45, var=.08) if False else ""
    o += lib.line(pts, w + 14, INK, taper=.1, wmin=.55, seed=sd, peak=.5)
    o += lib.line(pts, w, "#d8352b", taper=.1, wmin=.55, seed=sd + 1, peak=.5)
    o += lib.line([(p0[0] + 6, p0[1] - w * .18), mid, (q[0] - 4, q[1] - w * .1)], w * .22, "#f27a6a", taper=.4, wmin=.3, seed=sd + 2, peak=.4)
    return o


def s06_frame(t):
    s = [bg_wall6()]
    for r in range(2):
        s.append(shelf6(SH6[r] + 4, 10 + r * 5))
    order = []
    for r in range(2):
        for j in range(4):
            x, y, rot, trem = glass_motion6(j, r, t)
            order.append((y, r, j, x, rot, trem))
    for y, r, j, x, rot, trem in sorted(order):
        sl = 6 * trem * math.sin(t * 37 + j + r * 3)
        if r == 0 or True:
            s.append(fp.shadow(GX6[j] + 24, SH6[r] + 10, 80, 12, .28 * (1 - smooth(HIT6_NO + .1, HIT6_NO + .4, t)), 6))
        s.append(props.glass(x, y, KG6, .78, tilt=rot, slosh=sl, wet=True, seed=r * 4 + j))
    # крест: две жирные полосы, вторая через 0.1 с
    A, B = (60, 330), (1020, 1120)
    C, D = (1020, 330), (60, 1120)
    s.append(cross_stroke(A, B, ease_out(clamp((t - HIT6_NO) / 0.11), 2), 62, SEED + 300))
    s.append(cross_stroke(C, D, ease_out(clamp((t - HIT6_NO - 0.11) / 0.11), 2), 62, SEED + 310))
    e = t - HIT6_NO
    if 0 < e < 0.45:
        s.append(fp.burst(540, 760, e / .45, 14, 380, 760, 16, "#fff4c2", SEED + 320))
    # камера: наезд с разгоном под riser, удар на «нет», дальше отскок
    u = ease_in(clamp((t - T6) / (HIT6_NO - T6)), 2.2)
    sc = lerp(0.96, 1.32, u)
    cx, cy = lerp(540, 540, u), lerp(880, 840, u)
    rot = lerp(-1.8, 0.0, clamp((t - T6) / 0.4)) + 0.6 * math.sin(t * 2.5)
    # дрожь камеры на «правила»
    if HIT6_TREM <= t < HIT6_NO:
        a = 1 + 3 * clamp((t - HIT6_TREM) / (HIT6_NO - HIT6_TREM))
        cx += 4 * a * math.sin(t * 57)
        cy += 4 * a * math.sin(t * 71)
    if t >= HIT6_NO:
        e = t - HIT6_NO
        kk = math.exp(-e * 8)
        sc = lerp(1.32, 1.04, ease_out(clamp(e / .5), 2)) * (1 + 0.06 * kk)
        rot += 2.6 * kk * math.sin(e * 34)
        cy += 26 * kk * math.sin(e * 48)
    return svg(f'<rect width="{W}" height="{H}" fill="#ead2a6"/><g transform="{cam(cx, cy, sc, rot)}">{"".join(s)}</g>')


def frame(sid, t):
    lib.dyn_begin()
    return s02_frame(t) if sid == "s02" else s06_frame(t)
