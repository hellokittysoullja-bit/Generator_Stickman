"""Рилс 58 группа B: s14 (29.1–31.56) крупно лист и рука Димы с ручкой (хват пальцами): в начале заводится таймер-круг без цифр
в углу, на «пишет» (29.81) рука выводит штрихи-страхи по листу, на «боится» (30.72) лист заполнен. Камера: наезд на лист."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import bits  # noqa: E402
import fxprops as fp  # noqa: E402
import hand  # noqa: E402
import lib  # noqa: E402
import props  # noqa: E402
from lib import H, W, blob, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, mix, rect_pts, shape, smooth, svg  # noqa: E402

SEED = 14000
T_WRITE0, T_WRITE1 = 29.81, 30.72
T_WIND0, T_WIND1 = 28.95, 29.7
SHEET = (560, 1110, 12.0, 2.5)
LINES = 7
PSEED = 9
TIMER = (230, 420, 2.4)


def lerp(a, b, u):
    return a + (b - a) * u


def desk_bg():
    s = [f'<rect x="-600" y="-600" width="2300" height="3200" fill="{props.C_DESK}"/>']
    for i, y in enumerate(range(-500, 2700, 260)):
        s.append(line([(-600, y), (1700, y + 5)], 4, props.C_DESK_END, taper=0, wmin=1, seed=SEED + i, op=.85))
        x = -200 + ((i * 411) % 1500)
        s.append(line([(x, y), (x, y + 260)], 3, props.C_DESK_END, taper=0, wmin=1, seed=SEED + 40 + i, op=.7))
    return "".join(s)


def line_end(i, part):
    x, y, k, rot = SHEET
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    Wd, Hd = props.SHEET_W, props.SHEET_H
    top, bot = -Hd / 2 + 9, Hd / 2 - 7
    step = (bot - top) / (LINES - 1)
    Lw = (Wd - 11) * (0.78 + 0.22 * math.sin(i * 2.3 + PSEED)) * part
    lx, ly = -Wd / 2 + 5 + Lw, top + i * step
    return x + k * (lx * c - ly * sn), y + k * (lx * sn + ly * c)


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    s = [desk_bg()]
    sx, sy, sk, rot = SHEET
    fillu = ease_io(clamp((t - T_WRITE0) / (T_WRITE1 - T_WRITE0)))
    s.append(lib.blob(ellipse_pts(sx + 26, sy + 40, 20 * sk * 1.05, 28 * sk * .62, 18), "#6b4524", .22, lib.blur(12)))
    s.append(props.paper_sheet(sx, sy, sk, fill=fillu, rot=rot, t=t, writing=True, lines=LINES, seed=PSEED))
    # левая рука придерживает лист слева, чуть дрожит
    tr = 1.6 * math.sin(t * 31)
    s.append(bits.forearm((-260, 1560 + tr), (205, 1290 + tr), 220, 160, SEED + 100))
    s.append(bits.hand_flat(240, 1290 + tr, -14, 2.4, SEED + 110))
    # правая рука с ручкой: кончик ведёт по строкам; до письма ручка у верха листа, после — отходит вверх
    n = fillu * LINES
    i = min(LINES - 1, int(n))
    part = clamp(n - i)
    if fillu >= .999:
        i, part = LINES - 1, 1.0
    wx, wy = line_end(i, max(part, 0.02))
    pre = smooth(28.9, T_WRITE0, t)
    start = (sx - 60, sy - 470)
    tipx = lerp(start[0] + 150 * (1 - pre), wx, pre) + 3
    tipy = lerp(start[1] - 120 * (1 - pre), wy, pre) + 6 + 2.5 * math.sin(t * 46) * pre
    lift = 90 * smooth(T_WRITE1 + .05, T_WRITE1 + .45, t)
    ang = -52 + 5 * math.sin(t * 26) * pre
    s.append(hand.draw(tipx + lift * .35, tipy - lift, ang, 1.6, SEED + 140, 0.45, sleeve=True))
    # таймер в углу: заводится рывками, потом тикает
    tx, ty, tk = TIMER
    u = ease_io(clamp((t - T_WIND0) / (T_WIND1 - T_WIND0)))
    u = u * (1 - 0.1 * smooth(T_WIND1, 31.6, t))
    bump = 0.08 * math.exp(-max(0, t - T_WIND1) * 8) * math.cos(max(0, t - T_WIND1) * 24) if t > T_WIND1 else 0.0
    sh = 2.0 * math.sin(t * 55) * (1 if t < T_WIND1 else 0)
    s.append(f'<g transform="translate({tx} {ty}) scale({1 + bump:.4f}) translate({-tx} {-ty})">{props.timer_circle(tx, ty, tk, u, sh, 1)}</g>')
    if T_WIND1 - .03 < t < T_WIND1 + .4:
        s.append(fp.burst(tx, ty, (t - T_WIND1 + .03) / .43, 10, 150, 250, 9, "#fff4c2", SEED + 50))
    # камера: наезд на лист
    u2 = clamp((t - 28.9) / 2.85)
    sc = lerp(0.92, 1.12, ease_io(u2))
    cx_, cy_ = lerp(500, 560, u2), lerp(980, 1060, u2)
    rot_c = lerp(-1.4, 1.0, u2) + 0.3 * math.sin(t * 36)
    return svg(f'<rect width="{W}" height="{H}" fill="{props.C_DESK}"/><g transform="{cam(cx_, cy_, sc, rot_c)}">{"".join(s)}</g>')
