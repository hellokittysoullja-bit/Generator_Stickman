"""Рилс 55 s05 (10.2–13.2, клип 10.0–13.4): Дима в профиль, от ноутбука тянется светящаяся нить и ведёт его руку к клавишам
(10.2–11.2); потом камера въезжает в голову, в ней раскрывается круглое окно «внутри головы»: клочок бумаги летит и застревает
в крючке на «застревает» (12.36), дёргается и висит («не даёт забыть»)."""
import math

import dima
import lib
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg)

_ST = {}
K = 2.6
HIPX, HIPY = 230.0, 1385.0
HX, HY = 292.0, 755.0          # центр черепа (мир)
WR = 150.0                     # радиус окна «внутри головы»
OPEN0 = 11.25                  # окно начинает раскрываться
CATCH = 12.36                  # «застревает»
KEYS = (185.0, -72.0)          # цель кисти у клавиш (L мира относительно таза)
LAP = (745.0, 1000.0)          # экран ноутбука
THREAD0, THREAD1 = 10.05, 10.55


def background():
    s = []
    g = lin_grad([(0, "#1d2346", 1), (1, "#3a3560", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-900" y="-900" width="3000" height="{1230 + 900}" fill="url(#{g})"/>')
    for x in range(-900, 2000, 140):
        s.append(f'<rect x="{x}" y="-900" width="50" height="{1230 + 900}" fill="#262a52" opacity=".7"/>')
    tp = [(-900, 1230, 1), (2000, 1230, 1), (2000, 2800, 1), (-900, 2800, 1)]
    inner = "".join(line([(-900, 1270 + k * 60), (2000, 1274 + k * 60)], 2.4, "#7a5238", taper=.1, wmin=.7, seed=610 + k, op=.8) for k in range(8))
    s.append(shape(tp, "#9a6a46", inner, w=5, seed=608))
    s.append(blob(rect_pts(-900, 1230, 2000, 1256), "#7e5336", .8))
    s.append(line([(-900, 1230), (2000, 1230)], 5, INK, taper=.05, wmin=.9, seed=611))
    return "".join(s)


def laptop(t):
    glow = 0.8 + 0.2 * math.sin(t * 6)
    s = [blob([(620, 1250), (1040, 1250), (1060, 1270), (600, 1270)], "#1a0e05", .35, blur(8))]
    s.append(shape([(640, 1196), (1010, 1196), (1020, 1236), (630, 1236)], "#9aa0b4", blob([(630, 1222), (1020, 1222), (1020, 1236), (630, 1236)], "#6f7488"), w=5, seed=620))
    for k in range(7):    # клавиши-штрихи
        s.append(line([(668 + k * 46, 1190), (698 + k * 46, 1190)], 8, "#5c6174", taper=.1, wmin=.8, seed=621 + k))
    lid = [(990, 1198), (1030, 1198), (1068, 800), (1030, 796)]
    s.append(shape(lid, "#b8bdd0", blob([(1030, 1198), (1068, 800), (1030, 796)], "#8d92a8"), w=5, seed=630))
    s.append(line([(988, 1190), (1024, 806)], 7, "#fff2b8", taper=.1, wmin=.9, seed=631, op=glow))
    g = rad_grad([(0, "#ffe9a0", .5 * glow), (1, "#ffe9a0", 0)], 960, 1000, 520, 420)
    s.append(f'<rect x="300" y="500" width="1000" height="1000" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    return '<g transform="translate(-250 0)">' + "".join(s) + "</g>"


def hand_target(t):
    """Кисть: висит → нить тянет → у клавиш и печатает."""
    u = ease_io(clamp((t - 10.3) / 0.85))
    x = 70 + (KEYS[0] - 70) * u
    y = -20 + (KEYS[1] + 20) * u - 34 * math.sin(math.pi * u)
    if t > 11.2:
        x += 2 * math.sin(t * 22)
        y += 3 * abs(math.sin(t * 17))
    return x, y


def hand_world(t):
    x, y = hand_target(t)
    return HIPX + x * K, HIPY + y * K


def thread(t):
    """Светящаяся нить от экрана к кисти: растёт к руке (THREAD0–THREAD1), по ней бегут искры; после 11.3 гаснет."""
    g = ease_out(clamp((t - THREAD0) / (THREAD1 - THREAD0)), 2)
    fade = 1 - smooth(11.2, 11.55, t)
    if g <= 0 or fade <= 0:
        return ""
    hx, hy = hand_world(t)
    hx += 22
    hy -= 24
    sx, sy = LAP
    pts = []
    n = 26
    for i in range(n + 1):
        u = i / n * g
        # кривая с провисом и волной
        x = sx + (hx - sx) * u
        y = sy + (hy - sy) * u + 150 * math.sin(math.pi * u) * (1 - 0.4 * u) + 14 * math.sin(u * 9 - t * 8) * u
        pts.append((x, y))
    s = [line(pts, 26 * fade, "#ffcf5a", taper=.2, wmin=.3, seed=640, extra=blur(6)),
         line(pts, 11 * fade, "#ffe58a", taper=.15, wmin=.5, seed=641),
         line(pts, 4.5 * fade, "#fffbe6", taper=.1, wmin=.6, seed=642)]
    for j in range(4):    # бегущие светлячки
        u = ((t * 1.3 + j / 4) % 1.0) * g
        x = sx + (hx - sx) * u
        y = sy + (hy - sy) * u + 150 * math.sin(math.pi * u) * (1 - 0.4 * u) + 14 * math.sin(u * 9 - t * 8) * u
        s.append(blob(ellipse_pts(x, y, 11, 11, 10), "#fffbe6"))
    return "".join(s)


def dima_fig(t):
    work = smooth(10.3, 11.1, t)
    lx, ly = 0.15 + 0.85 * smooth(10.1, 10.6, t), 0.2 - 0.15 * work
    hx, hy = hand_target(t)
    pose = {"hip": (0.0, 0.0), "lean": math.radians(8 + 5 * work + 1.2 * math.sin(t * 1.9)),
            "head_ang": math.radians(4 + 4 * work + 2 * math.sin(t * 2.2)),
            "feet": {"n": ((40, 260), 0.0), "f": ((-20, 260), 0.0)},
            "arms": {"n": ("ik", (hx, hy), 1), "f": ("ik", (hx - 20, hy + 40), 1)},
            "hands": {"n": ("open", 0.35 + 0.3 * (1 - work)), "f": "none"},
            "expr": {"lid": 0.35 + 0.35 * work, "look": (lx, ly), "brows": "up" if work > .4 else "worry",
                     "mouth": "tired" if work < .6 else "gape", "hair": 2 * math.sin(t * 4)},
            "hood": 0.0, "strings": (3 * math.sin(t * 3.1), 0)}
    g, _ = dima.draw(pose)
    cid = lib.clip_rect(-400, -400, 2800, 400 + 1236)
    br = 1 + 0.008 * math.sin(t * 2.4)
    return f'<g clip-path="url(#{cid})"><g transform="translate({HIPX} {HIPY}) scale({K} {K * br:.4f})">{g}</g></g>'


# ───────────────────────── внутри головы
def window(t):
    e = t - OPEN0
    if e < 0:
        return ""
    r = WR * back_out(clamp(e / 0.4), 2.0)
    if r < 4:
        return ""
    cid = lib.uid("w")
    lib.DEFS.append(f'<clipPath id="{cid}"><circle cx="{HX}" cy="{HY}" r="{f(r)}"/></clipPath>')
    gr = lin_grad([(0, "#2a2f6e", 1), (1, "#161a44", 1)], 0, 0, 0, 1)
    s = [f'<circle cx="{HX}" cy="{HY}" r="{f(r + 12)}" fill="#fff2c4"/>', f'<circle cx="{HX}" cy="{HY}" r="{f(r)}" fill="url(#{gr})"/>']
    inner = []
    # извилины-штрихи фона
    for k in range(5):
        y0 = HY - 110 + k * 55
        pts = [(HX - 170 + i * 30, y0 + 16 * math.sin(i * 1.1 + k * 1.7 + t * .6)) for i in range(12)]
        inner.append(line(pts, 7, "#3b4690", taper=.3, wmin=.5, seed=650 + k))
    inner.append(hook_and_paper(t))
    s.append(f'<g clip-path="url(#{cid})">{"".join(inner)}</g>')
    s.append(f'<circle cx="{HX}" cy="{HY}" r="{f(r)}" fill="none" stroke="{INK}" stroke-width="7"/>')
    return "".join(s)


def hook_path(pull):
    """Крючок: верёвка сверху → J-изгиб, кончик вверх. pull — оттяжка вниз при рывке."""
    top = (HX + 10, HY - 190)
    pts = [top, (HX + 10, HY - 100), (HX + 12, HY - 40 + pull * .5), (HX + 4, HY + 4 + pull), (HX - 22, HY + 24 + pull),
           (HX - 54, HY + 8 + pull), (HX - 62, HY - 24 + pull * .9), (HX - 50, HY - 44 + pull * .9)]
    return pts


def hook_and_paper(t):
    e = t - CATCH
    pull = 0.0
    if e > 0:
        pull = 26 * math.exp(-e * 5) * math.sin(e * 16 + .3) + 10 * (1 - math.exp(-e * 4))
    # шатание от «даёт» после 13.0
    if t > 12.95:
        pull += 5 * math.sin((t - 12.95) * 14)
    hp = hook_path(pull)
    # бумага
    if t < CATCH:
        u = clamp((t - 11.7) / (CATCH - 11.7))
        x = HX - 330 + 300 * ease_in(u, 1.3) + 6 * math.sin(u * 9)
        y = HY - 40 + 22 * math.sin(u * 8) - 10 * u
        rot = 18 * math.sin(u * 7)
        sc = 1.0
    else:
        a = hp[-1]
        sway = 16 * math.exp(-e * 2.2) * math.sin(e * 11) + (8 * math.sin((t - 12.95) * 9) if t > 12.95 else 0)
        x, y = a[0] + 8, a[1] + 34 + pull * .3
        rot = sway
        sc = 1.0
    P = [(-52, -30), (-18, -40, 1), (14, -34), (50, -38), (56, -6, 1), (48, 34), (54, 62, 1), (14, 56), (-22, 66, 1), (-46, 44), (-56, 6)]
    pap = shape(P, "#f7f1de", blob([(-56, 30), (54, 40), (54, 62), (-46, 66)], "#e2d9bd") +
                "".join(line([(-36, -16 + k * 22), (30 - 8 * (k % 2), -14 + k * 22)], 5, "#8e8a7c", taper=.2, wmin=.6, seed=660 + k) for k in range(3)),
                w=4.2, seed=661)
    out = [f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({sc})">{pap}</g>']
    # крючок поверх бумаги (кончик ловит её)
    out.append(line(hp, 17, INK, taper=0, wmin=1, seed=670))
    out.append(line(hp, 11, "#f0b43c", taper=0, wmin=1, seed=671))
    out.append(line(hp[2:6], 3.5, "#fff0b0", taper=.1, wmin=.5, seed=672))
    # искры в момент зацепа
    if 0 < e < 0.4:
        kk = e / 0.4
        for j in range(8):
            a = math.radians(j * 45 + 10)
            tp = hp[-1]
            out.append(line([(tp[0] + (40 + 40 * kk) * math.cos(a), tp[1] + (40 + 40 * kk) * math.sin(a)),
                             (tp[0] + (70 + 90 * kk) * math.cos(a), tp[1] + (70 + 90 * kk) * math.sin(a))], 8 * (1 - kk) + 1.5, "#ffe58a", taper=.6, seed=680 + j))
    return "".join(out)


def camera(t):
    # широкий → к голове (11.0–12.0), толчок на «застревает»
    u = ease_io(clamp((t - 10.9) / 1.2))
    v = clamp((t - 10.0) / 3.4)
    ccx = 520 + (HX + 90 - 520) * u - 30 * v * (1 - u)
    ccy = 1040 + (HY + 20 - 1040) * u
    sc = 1.22 + (2.2 - 1.22) * u
    sc *= 1 + 0.05 * (1 - ease_out(clamp((t - 10.0) / 0.5)))
    e = t - CATCH
    rot = 1.2 * math.sin(t * 1.5) * (1 - u)
    if e > 0:
        k = math.exp(-e * 7)
        sc *= 1 + 0.07 * k
        ccy += 14 * k * math.sin(e * 40)
        rot += 3.0 * k * math.sin(e * 25)
    return cam(ccx, ccy, sc, rot)


def frame(sid, t):
    if not _ST:
        _ST["bg"] = background()
        dima.LWK = 1.0
        lib.static_done()
    lib.dyn_begin()
    s = [_ST["bg"], laptop(t), dima_fig(t), thread(t), window(t)]
    return svg(f'<rect width="{W}" height="{H}" fill="#1d2346"/><g transform="{camera(t)}">{"".join(s)}</g>')
