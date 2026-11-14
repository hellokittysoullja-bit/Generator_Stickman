"""Рилс 58 группа B: s10 (18.1–21.1) крупно таймер-круг без цифр: сектор закрашивается на «десять» (18.69); затем студент у парты
пишет штрихи-страхи на листе (без букв), на «страхах» (20.47) лист заполнен. Камера: наезд на таймер, затем перевод вниз на лист."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import bits  # noqa: E402
import dima  # noqa: E402
import fxprops as fp  # noqa: E402
import hand  # noqa: E402
import lib  # noqa: E402
import props  # noqa: E402
from lib import H, W, blob, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rect_pts, shape, smooth, spring, svg  # noqa: E402

SEED = 10000
T_TEN = 18.69
T_FILL1 = 19.62
T_PAN0, T_PAN1 = 19.5, 20.2
T_W0, T_W1 = 19.95, 20.47
TIMER = (540, 560)
TK = 6.6
HO = (540, 1215)
HS = 1.32
DESK_Y = 1500
SHEET = (560, 1720, 7.4, -3.0)       # x, y, k, rot
LINES = 6
PSEED = 4

STUDENT = dict(SKIN="#d9a984", SKIN_SH="#bd8a68", SKIN_SH2="#a87756", HAIR="#23232f", HAIR_SH="#14141c", HAIR_HI="#3f3f55",
               HOOD="#5b86b8", HOOD_SH="#456a96", HOOD_SH2="#36567c", FOLD="#243a54")


def lerp(a, b, u):
    return a + (b - a) * u


class Palette:
    """Временно перекрашивает героя в студента (кожа, волосы, свитер) — модули dima и hand берут цвета из своих глобалов."""
    def __enter__(self):
        self.old = {k: (getattr(dima, k, None), getattr(hand, k, None)) for k in STUDENT}
        for k, v in STUDENT.items():
            if hasattr(dima, k):
                setattr(dima, k, v)
            if hasattr(hand, k):
                setattr(hand, k, v)

    def __exit__(self, *a):
        for k, (d, h) in self.old.items():
            if d is not None:
                setattr(dima, k, d)
            if h is not None:
                setattr(hand, k, h)


def background():
    g = lin_grad([(0, "#d3e6e2", 1), (1, "#bcd6d1", 1)], 0, 0, 0, 1)
    s = [f'<rect x="-600" y="-900" width="2300" height="{DESK_Y + 900}" fill="url(#{g})"/>']
    for x in range(-500, 1600, 260):
        s.append(f'<rect x="{x}" y="-900" width="100" height="{DESK_Y + 900}" fill="#c9e0db"/>')
    return "".join(s)


def desk_top():
    s = []
    top = [(-300, DESK_Y, 1), (1380, DESK_Y, 1), (1380, 2400, 1), (-300, 2400, 1)]
    inner = ""
    for i, y in enumerate((1610, 1760, 1940, 2150)):
        inner += line([(-300, y), (1380, y + 5)], 3.4, mix(props.C_DESK, "#8a6538", .5), taper=0, wmin=1, seed=SEED + 30 + i, op=.9)
    inner += blob([(-300, DESK_Y), (1380, DESK_Y), (1380, DESK_Y + 26), (-300, DESK_Y + 26)], mix(props.C_DESK, "#8a6538", .35))
    s.append(shape(top, props.C_DESK, inner, w=6, seed=SEED + 40))
    return "".join(s)


def sheet_geo():
    x, y, k, rot = SHEET
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return x, y, k, c, sn


def line_end(i, part):
    """Мировая точка конца строки i (штрих растёт на part 0..1) — туда ведёт кончик ручки."""
    x, y, k, c, sn = sheet_geo()
    Wd, Hd = props.SHEET_W, props.SHEET_H
    top, bot = -Hd / 2 + 9, Hd / 2 - 7
    step = (bot - top) / (LINES - 1)
    y0 = top + i * step
    Lw = (Wd - 11) * (0.78 + 0.22 * math.sin(i * 2.3 + PSEED)) * part
    lx, ly = -Wd / 2 + 5 + Lw, y0
    return x + k * (lx * c - ly * sn), y + k * (lx * sn + ly * c)


def student(t, fillu):
    s = []
    done = smooth(T_W1 - .1, T_W1 + .25, t)
    look = (lerp(.35, .55, .5 + .5 * math.sin(t * 5)), .85 - .8 * done)
    expr = {"lid": lerp(.5, .6, done), "look": look, "brows": "det" if done < .5 else "calm", "mouth": "flat" if done < .5 else "relief", "hair": 1.5 * math.sin(t * 3)}
    dima.LWK = 0.82
    hd = dima.head(expr)
    cc = lib.clip_rect(-600, -600, 3000, 600 + DESK_Y + 10)
    s.append(f'<g clip-path="url(#{cc})"><g transform="translate({HO[0] - 10} {HO[1] + 12}) scale({HS})">{bits.hood_body(SEED + 100)}</g></g>')
    tilt = 11 - 7 * done + 1.2 * math.sin(t * 4.2)
    s.append(f'<g transform="translate({HO[0] + 40} {HO[1] + 46 - 22 * done}) rotate({tilt:.2f}) scale({HS})">{hd}</g>')
    return "".join(s)


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    s = [background()]
    # ── таймер на стене: сектор закрашивается на «десять»
    u = ease_io(clamp((t - T_TEN) / (T_FILL1 - T_TEN)))
    bump = 0.0
    if t > T_TEN:
        e = t - T_TEN
        bump = 0.09 * math.exp(-e * 7) * math.cos(e * 22)
    shake = 3.0 * math.sin(t * 60) * (1 if T_TEN < t < T_FILL1 else 0.25)
    tx, ty = TIMER
    s.append(f'<g transform="translate({tx} {ty}) scale({1 + bump:.4f}) translate({-tx} {-ty})">{props.timer_circle(tx, ty, TK, u, shake, 0)}</g>')
    if T_TEN < t < T_TEN + .5:
        s.append(fp.burst(tx, ty, (t - T_TEN) / .5, 12, 420, 560, 14, "#fff4c2", SEED + 50))
    if T_FILL1 - .05 < t < T_FILL1 + .4:   # щелчок: круг закрашен
        s.append(fp.burst(tx, ty, (t - T_FILL1 + .05) / .45, 10, 430, 520, 12, "#ffe3a0", SEED + 60))
    # ── студент и парта
    s.append('<g transform="translate(0 120)">')
    with Palette():
        fillu = smooth(T_W0, T_W1, t) if True else 0
        s.append(student(t, fillu))
        s.append(desk_top())
        sx, sy, sk, rot = SHEET[0], SHEET[1], SHEET[2], SHEET[3]
        s.append(lib.blob(ellipse_pts(sx + 16, sy + 22, 20 * sk * 1.05, 28 * sk * .62, 18), "#6b4524", .22, lib.blur(10)))
        s.append(props.paper_sheet(sx, sy, sk, fill=fillu, rot=rot, t=t, writing=True, lines=LINES, seed=PSEED))
        # левая рука придерживает лист слева
        s.append(bits.forearm((100, 1480), (300, 1715), 150, 108, SEED + 120))
        s.append(bits.hand_flat(338, 1722, 8, 1.55, SEED + 130))
        # правая рука с ручкой пишет: кончик ведёт по строкам
        n = fillu * LINES
        i = min(LINES - 1, int(n))
        part = clamp(n - i)
        if fillu >= .999:
            i, part = LINES - 1, 1.0
        tx_, ty_ = line_end(i, max(part, 0.02))
        tw = 3.0 * math.sin(t * 50)
        tip = (tx_ + 4, ty_ + 5 + tw)
        ang = -50 + 6 * math.sin(t * 24) * (1 if fillu < 1 else 0)
        lift = 0 if fillu < .999 else 26 * smooth(T_W1, T_W1 + .3, t)
        sc = 1.0
        s.append(hand.draw(tip[0] + lift * .4, tip[1] - lift, ang, sc, SEED + 140, 0.4, sleeve=True))
    s.append('</g>')
    # ── камера: наезд на таймер → перевод вниз на лист
    p = ease_io(clamp((t - T_PAN0) / (T_PAN1 - T_PAN0)))
    sc1 = lerp(1.3, 1.5, clamp((t - 17.9) / 1.7))
    sc_c = lerp(sc1, 1.18, p) + 0.12 * smooth(20.2, 21.3, t)
    cy_ = lerp(590, 1700, p) + 20 * smooth(20.2, 21.3, t)
    cx_ = lerp(540, 560, p)
    rot_ = lerp(1.2, -.8, clamp((t - 17.9) / 3.4)) + 0.5 * math.sin(t * 40) * (1 if T_TEN < t < T_FILL1 else 0)
    return svg(f'<rect width="{W}" height="{H}" fill="#d3e6e2"/><g transform="{cam(cx_, cy_, sc_c, rot_)}">{"".join(s)}</g>')
