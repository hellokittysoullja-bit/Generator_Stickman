"""Рилс 59 группа C: s02 (1.4–2.9) крупно подарочная коробка пружинит; на «день» (1.71) рядом вырастает торт, на «рождения» (1.91)
на нём вспыхивает свеча; мама смеётся в облачке-мысли; наезд на торт, тряска на свече."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
import props_c as pc  # noqa: E402
from lib import INK, W, H, back_out, blob, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, mix, rect_pts, shape, spring, svg  # noqa: E402

T0 = 1.2
T_CAKE, T_FLAME = 1.712, 1.911
BOX = (300, 1190)
CAKE = (730, 1190)


def rnd(i):
    return abs(math.sin(i * 12.9898) * 43758.5453) % 1.0


def lerp(a, b, u):
    return a + (b - a) * u


def background(t):
    s = [f'<rect x="-600" y="-600" width="2400" height="3400" fill="#FCE6CB"/>']
    # широкие тёплые полосы, едут вбок — фон живой с первого кадра
    off = (t * 40) % 240
    for k in range(-4, 12):
        x = k * 240 - off
        s.append(blob([(x, -600), (x + 120, -600), (x + 120 - 600, 1500), (x - 600, 1500)], "#FBD9B2", 1.0))
    # конфетти
    for i in range(34):
        x = (rnd(i) * 1500 - 200) + 30 * math.sin(t * 1.3 + i)
        y = ((rnd(i + 50) * 1700 - 100 + t * (60 + 50 * rnd(i + 9))) % 1700) - 100
        col = ("#F26B6B", "#3BBDB6", "#F6C445", "#7A6BD0", "#F28AB0")[i % 5]
        r = 12 + 14 * rnd(i + 3)
        a = t * 90 * (1 if i % 2 else -1) + i * 37
        c, sn = math.cos(math.radians(a)), math.sin(math.radians(a))
        pts = [(x + c * r - sn * r * .5, y + sn * r + c * r * .5), (x - c * r - sn * r * .5, y - sn * r + c * r * .5),
               (x - c * r + sn * r * .5, y - sn * r - c * r * .5), (x + c * r + sn * r * .5, y + sn * r - c * r * .5)]
        s.append(blob(pts, col))
    # стол
    s.append(shape(rect_pts(-600, 1180, 1700, 2600), "#E3AC6E", blob(rect_pts(-600, 1180, 1700, 1230), "#F2C892") + blob(rect_pts(-600, 1330, 1700, 1345), "#C98F52", 1.0), w=7, seed=3))
    return "".join(s)


def shadow(x, y, rx, ry, op=.28):
    return "".join(blob(ellipse_pts(x, y, rx * m, ry * m, 18), "#5a3416", op / 3) for m in (1.0, .86, .72))


def mama_face(cx, cy, k, t):
    """Мама, хохочет: серебряная прядь, морщинки у глаз, бежевый кардиган. Плечи подпрыгивают в такт смеху."""
    jig = math.sin(t * 28) * 5 * k
    o = []
    sk, sh = "#EFC8A8", "#D9A383"
    o.append(shape([(-150, 150 + jig / k), (-120, 90), (-60, 70), (60, 70), (120, 90), (150, 150 + jig / k)], "#D8BC94", blob([(40, 70), (120, 90), (150, 150), (60, 150)], "#BFA077", .8), w=5, seed=301))
    o.append(shape([(-34, 66), (0, 110), (34, 66)], "#FFFFFF", w=4, seed=302))
    o.append(shape(ellipse_pts(0, 46, 36, 30, 10), sk, w=4, seed=303))
    hair_back = [(-112, -10), (-108, -92), (-60, -140), (0, -150), (60, -140), (108, -92), (112, -10), (96, 40), (-96, 40)]
    o.append(shape(hair_back, "#DCDCE4", blob([(20, -150), (108, -92), (112, -10), (96, 40), (40, 40)], "#B9BAC8", .8), w=5.4, seed=304))
    o.append(shape(ellipse_pts(0, -8 + jig * .3 / k, 88, 100, 22), sk, blob(ellipse_pts(32, 14, 68, 84, 16), sh, .55), w=5.4, seed=305))
    fringe = [(-92, -30), (-84, -86), (-40, -112), (20, -114), (70, -96), (90, -50), (50, -60), (20, -84), (-30, -80), (-70, -52)]
    o.append(shape(fringe, "#DCDCE4", "", w=5, seed=306))
    o.append(shape(ellipse_pts(0, -150, 46, 34, 14), "#DCDCE4", blob(ellipse_pts(14, -144, 30, 20, 10), "#B9BAC8", .8), w=5.4, seed=320))  # пучок
    o.append(line([(-6, -114), (-18, -84), (-44, -62)], 6, "#9A9BAE", seed=307, taper=.2, wmin=.9))
    for sx in (-1, 1):
        o.append(line([(sx * 62, -22), (sx * 42, -34), (sx * 26, -22)], 5, INK, seed=308 + sx, taper=.15, wmin=.9))
        for j in range(3):
            o.append(line([(sx * 70, -26 + 8 * j), (sx * 88, -30 + 12 * j)], 2.2, "#B58A70", seed=312 + j + sx * 5, op=.9))
        o.append(shape(ellipse_pts(sx * 54, 22, 20, 12, 8), "#F29E96", "", w=0, ink=False))
    o.append(line([(-52, -56), (-34, -64), (-16, -58)], 4, "#8C8DA0", seed=316, taper=.2))
    o.append(line([(16, -58), (34, -64), (52, -56)], 4, "#8C8DA0", seed=317, taper=.2))
    op = 22 + 12 * abs(math.sin(t * 17))
    o.append(shape([(-38, 34), (-30, 34 + op * .5, 1), (0, 36 + op * 1.5), (30, 34 + op * .5, 1), (38, 34), (0, 40)], "#6B2B33", blob(ellipse_pts(0, 34 + op * 1.2, 20, 11, 8), "#E26A72"), w=4.4, seed=318))
    o.append(shape([(-34, 38), (0, 44), (34, 38), (26, 46), (0, 52), (-26, 46)], "#FFFFFF", w=0, ink=False))
    o.append(shape(ellipse_pts(0, 10, 8, 10, 8, rot=0), sk, w=3.6, seed=319))
    return f'<g transform="translate({f(cx)} {f(cy)}) scale({k:.4f})">{"".join(o)}</g>'


def cloud(cx, cy, r, t, pop):
    """Облачко-мысль: кольцо кругов, внутри белое; три пузыря вниз к торту."""
    o = []
    bump = []
    n = 12
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (.34 + .03 * math.sin(i * 2.1))
        bump.append((cx + (r * .72) * math.cos(a) * 1.15, cy + (r * .62) * math.sin(a), rr))
    for (x, y, rr) in bump:
        o.append(shape(ellipse_pts(x, y, rr, rr, 14), "#FFFFFF", "", w=5, seed=int(x + y) % 997))
    o.append(shape(ellipse_pts(cx, cy, r * .78, r * .66, 24), "#FFFFFF", "", w=0, ink=False))
    for j, (dx, dy, rr) in enumerate(((-90, r * .9, 38), (-150, r * 1.2, 26), (-198, r * 1.45, 16))):
        o.append(shape(ellipse_pts(cx + dx, cy + dy, rr, rr, 12), "#FFFFFF", "", w=4.4, seed=330 + j))
    return f'<g transform="translate({f(cx)} {f(cy)}) scale({pop:.4f}) translate({f(-cx)} {f(-cy)})">{"".join(o)}</g>'


def s02_frame(t):
    s = [background(t)]
    # --- коробка: прыжки на пружине ---
    e = t - T0
    per = 0.52
    p = ((t - 0.95) / per) % 1.0
    hop = 150 * 4 * p * (1 - p) * math.exp(-0.2 * e)
    sq = 0.0
    if p < 0.14:
        sq = 0.2 * math.sin(math.pi * p / 0.14)
    elif p > 0.92:
        sq = 0.1 * math.sin(math.pi * (p - 0.92) / 0.08)
    sy = 1 - sq + (0.07 if 0.14 < p < 0.5 else 0)
    sx = 1 + sq * .8 - (0.04 if 0.14 < p < 0.5 else 0)
    wob = 9 * math.sin(t * 14) * (0.4 + 0.6 * math.exp(-e * 1.2))
    bx, by = BOX
    s.append(shadow(bx, by + 6, 210 - hop * .25, 30, .3 * (1 - hop / 260)))
    s.append(pc.gift_box(bx, by - hop, 0.92, sx, sy, rot=4 * math.sin(t * 9), wob=wob))
    # --- торт ---
    cx_, cy_ = CAKE
    u = clamp((t - T_CAKE) / 0.34)
    if t >= T_CAKE - 0.02:
        kc = 0.78 * back_out(u, 2.2) if u < 1 else 0.78
        e2 = t - T_CAKE - 0.34
        wob2 = 1 + (0.045 * math.exp(-e2 * 9) * math.sin(e2 * 38) if e2 > 0 else 0)
        fu = clamp((t - T_FLAME) / 0.16)
        s.append(shadow(cx_, cy_ + 6, 250 * kc / .78 * .9, 28 * kc / .78, .28))
        s.append(pc.cake(cx_, cy_, kc, 1 / wob2, wob2, rot=0, flame_u=fu, t=t))
        # вспышка свечи
        ef = t - T_FLAME
        fx, fy = cx_, cy_ - 434 * 0.78
        if 0 < ef < .5:
            g = ef / .5
            r = 30 + 340 * ease_out(g, 2)
            s.append(f'<circle cx="{fx:.1f}" cy="{fy - 30:.1f}" r="{r:.1f}" fill="none" stroke="#FFD25C" stroke-width="{max(1.0, 26 * (1 - g)):.1f}"/>')
            for j in range(12):
                a = math.radians(30 * j + 8 * math.sin(j * 2.3))
                r0 = 70 + 40 * g
                r1 = r0 + 170 * ease_out(g, 2) * (.7 + .3 * rnd(j))
                s.append(line([(fx + r0 * math.cos(a), fy - 30 + r0 * math.sin(a)), (fx + r1 * math.cos(a), fy - 30 + r1 * math.sin(a))], 11 * (1 - g) + 2, "#FFC93C", taper=.6, wmin=.2, seed=400 + j))
            s.append(lib_glint(fx + 80, fy - 90, ef / .45))
            s.append(lib_glint(fx - 90, fy - 40, clamp((ef - .08) / .45)))
    # --- мама в облачке ---
    cp = 0.78 + 0.22 * clamp(1)  # облачко уже стоит (после s01), чуть дышит
    br = 1 + 0.03 * math.sin(t * 6)
    s.append(cloud(760, 400, 230, t, br))
    s.append(mama_face(760, 410, 1.1, t))
    # --- камера ---
    u = clamp((t - 1.55) / 1.45)
    kk = ease_io(u) ** 1.2
    sc = lerp(1.0, 1.62, kk)
    cxc, cyc = lerp(500, 720, kk), lerp(900, 890, kk)
    rot = lerp(2.4, -1.2, kk)
    # лёгкий пульс на каждом прыжке коробки и тряска на свече
    ef = t - T_FLAME
    if ef > 0:
        a = math.exp(-ef * 7)
        sc *= 1 + 0.05 * a
        rot += 1.6 * a * math.sin(ef * 46)
        cxc += 18 * a * math.sin(ef * 61)
        cyc += 22 * a * math.sin(ef * 53 + 1)
    ec = t - T_CAKE
    if 0 < ec < .4:
        sc *= 1 + .035 * math.exp(-ec * 12)
    return svg(f'<rect width="{W}" height="{H}" fill="#FCE6CB"/><g transform="{cam(cxc, cyc, sc, rot)}">{"".join(s)}</g>')


def lib_glint(cx, cy, k, r=70):
    if not 0 < k < 1:
        return ""
    a = r * math.sin(math.pi * k) ** .7
    pts = [(cx, cy - a, 1), (cx + a * .16, cy - a * .16, 1), (cx + a, cy, 1), (cx + a * .16, cy + a * .16, 1), (cx, cy + a, 1),
           (cx - a * .16, cy + a * .16, 1), (cx - a, cy, 1), (cx - a * .16, cy - a * .16, 1)]
    return blob(pts, "#FFFFFF", 1.0) + blob([(p[0], p[1]) for p in pts], "#FFFFFF", 1.0)


def frame(sid, t):
    lib.dyn_begin()
    return s02_frame(t)
