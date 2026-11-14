"""Предметы и фоны сцены dima рилса 31: золотая рыбка, круглый аквариум, облачко-реплика, облако-мысль, комната Димы
(обои, окно, полка, постер), стол с блокнотом и ручкой, прихожая (вешалка, ключница, дверь), ключи, телефон.

Всё — SVG в мировых координатах (мир = кадр 1080×1920 при камере (540, 960, 1)); манера — как у 26–28: живая линия
туши (ink.py), плоский цвет с одной тенью. Букв нигде нет.
"""
import math

import numpy as np

import lib
from lib import INK, blob, ellipse_pts, line, rect_pts, shape


def rsd(*k):
    h = 2166136261
    for v in k:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return np.random.RandomState(h % (2 ** 31))


def tf_pts(pts, x, y, k, rot=0.0, flip=1):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for p in pts:
        px, py = p[0] * k * flip, p[1] * k
        out.append((x + px * c - py * s, y + px * s + py * c) + ((1,) if len(p) > 2 and p[2] else ()))
    return out


# ═════════════════════════ золотая рыбка (вуалехвост) ═════════════════════════
# Для единообразия с планами fish / lab берётся рыбка агента сцены fish (../fish/fish.py, только чтение); её модуль
# берёт помощники из уже загруженного lib (общий DEFS). Нет файла — своя рыбка ниже (fish()).
def _load_fish31():
    import importlib.util
    import os
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fish", "fish.py")
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location("fish31_shared", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


FISH31 = _load_fish31()


def gold_fish(x, y, k, t, flip=1, rot=0.0, seed=0, **kw):
    """Рыбка длиной ~300·k носом вправо (flip=-1 — влево): общая рыбка ролика, если есть, иначе своя."""
    if FISH31 is None:
        return fish(x, y, k, t, flip=flip, rot=rot, seed=seed)
    s = k * 300 / 380
    return FISH31.draw(x + 40 * s * flip, y, s, t, face=flip, rot=rot, lw=3.4 / s, ph=t * 1.6 * 2 * math.pi + seed, **kw)


FISH, FISH_SH, FISH_HI, FISH_FIN, FISH_FIN_SH = "#f08a24", "#c8631a", "#ffc24a", "#f9b04a", "#e48a2a"


def fish(x, y, k, t, flip=1, rot=0.0, eye="open", seed=0, look=(0.2, 0.0)):
    """Рыбка носом вправо (flip=-1 — влево), длина ~300·k. eye: open | blank (пустые глаза)."""
    wv = math.sin(t * 7.0 + seed)
    wv2 = math.sin(t * 7.0 + seed - 1.1)

    def T(pts):
        return tf_pts(pts, x, y, k, rot, flip)

    o = []
    # вуалевый хвост: два длинных лепестка с волной по краю
    tail_u = [(-58, -10), (-96, -40 + 6 * wv), (-150, -78 + 12 * wv), (-196, -70 + 16 * wv2), (-178, -40 + 10 * wv2),
              (-150, -20 + 8 * wv), (-182, 2 + 12 * wv2), (-150, 30 + 8 * wv), (-188, 58 + 16 * wv2), (-196, 86 + 14 * wv),
              (-150, 82 + 10 * wv), (-100, 48 + 6 * wv), (-58, 12)]
    inner = ""
    for i, (a, b) in enumerate([((-70, -4), (-170, -60 + 14 * wv)), ((-70, 0), (-170, 6 + 10 * wv2)), ((-70, 4), (-172, 70 + 14 * wv))]):
        inner += line(T([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 6 * wv), b]), 2.0 * k, FISH_FIN_SH, seed=seed + 40 + i, op=.85)
    inner += blob(T([(-60, 10), (-150, 40 + 8 * wv), (-190, 84 + 14 * wv), (-150, 82 + 10 * wv), (-100, 48 + 6 * wv)]), FISH_FIN_SH, .55)
    o.append(shape(T(tail_u), FISH_FIN, inner, w=3.4 * k, seed=seed + 1))
    # дальний грудной плавник
    o.append(shape(T([(24, 30), (6, 66 + 6 * wv), (-10, 70 + 6 * wv), (6, 36)]), FISH_FIN_SH, w=2.6 * k, seed=seed + 2))
    # спинной плавник
    o.append(shape(T([(32, -50), (10, -96 + 5 * wv2), (-30, -92 + 6 * wv), (-52, -66 + 4 * wv), (-40, -38)]), FISH_FIN,
                   line(T([(14, -54), (-6, -86 + 5 * wv2)]), 1.8 * k, FISH_FIN_SH, seed=seed + 41, op=.8) +
                   line(T([(-14, -48), (-34, -82 + 5 * wv)]), 1.8 * k, FISH_FIN_SH, seed=seed + 42, op=.8), w=3.0 * k, seed=seed + 3))
    # тело
    body = [(108, -2), (96, -32), (66, -54), (24, -62), (-20, -52), (-56, -24), (-66, 0), (-56, 22), (-20, 50), (24, 60), (70, 50),
            (98, 26)]
    bi = blob(T([(110, 6), (60, 18), (10, 24), (-60, 8), (-60, 70), (110, 70)]), FISH_HI, .95)
    bi += blob(T([(-70, -70), (10, -70), (-10, -40), (-70, -10)]), FISH_SH, .7)
    # чешуйки дугами
    for j, (sx, sy) in enumerate([(30, -26), (6, -18), (-18, -10), (18, -2), (-6, 6), (40, -6)]):
        bi += line(T([(sx - 8, sy - 8), (sx, sy), (sx - 8, sy + 8)]), 1.6 * k, FISH_SH, seed=seed + 50 + j, op=.75)
    # жабра
    bi += line(T([(58, -36), (48, -10), (54, 22)]), 2.4 * k, FISH_SH, seed=seed + 59)
    bi += blob(T([(70, -40), (96, -30), (100, -16), (76, -24)]), "#ffe2a0", .9)
    o.append(shape(T(body), FISH, bi, w=3.8 * k, seed=seed + 4))
    # ближний грудной плавник
    o.append(shape(T([(40, 20), (20, 50 + 8 * wv2), (2, 52 + 8 * wv2), (14, 28)]), FISH_FIN,
                   line(T([(32, 24), (12, 46 + 8 * wv2)]), 1.6 * k, FISH_FIN_SH, seed=seed + 60, op=.8), w=2.8 * k, seed=seed + 5))
    # рот
    o.append(line(T([(102, 10), (110, 6), (106, 16)]), 2.6 * k, seed=seed + 61))
    # глаз: большой белый, маленький зрачок
    ex, ey = 70, -16
    ep = T(ellipse_pts(ex, ey, 19, 20, 12))
    if eye == "blank":
        o.append(shape(ep, "#fbf8f0", "", w=3.2 * k, seed=seed + 6))
        cx_, cy_ = T([(ex, ey)])[0]
        o.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{2.6 * k:.2f}" fill="{INK}"/>')
    else:
        lx, ly = look
        cx_, cy_ = T([(ex + 7 * lx + 4, ey + 7 * ly)])[0]
        inner = f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{6.5 * k:.2f}" fill="{INK}"/>'
        hx, hy = T([(ex + 7 * lx + 2, ey + 7 * ly - 3)])[0]
        inner += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{2.2 * k:.2f}" fill="#ffffff"/>'
        o.append(shape(ep, "#fbf8f0", inner, w=3.2 * k, seed=seed + 6))
    return "".join(o)


# ═════════════════════════ круглый аквариум ═════════════════════════
def bowl(cx, cy, R, t, fish_fn=None, seed=900):
    """Аквариум-шар: центр, радиус. fish_fn(clip_id) -> svg рыбки внутри воды (рисуется под стеклом)."""
    o = []
    top = cy - R * .78
    glass = []
    for i in range(48):
        a = math.radians(-90 + 39 + (360 - 78) * i / 47)        # от верхнего правого края по часовой через низ к левому
        glass.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    glass[0] = glass[0] + (1,)
    glass[-1] = glass[-1] + (1,)
    gclip = lib.clip_of(glass)
    water_y = cy - R * .48 + 3 * math.sin(t * 2.2)
    inner = f'<rect x="{cx - R - 10:.1f}" y="{cy - R - 10:.1f}" width="{2 * R + 20:.1f}" height="{2 * R + 20:.1f}" fill="#e9f3f2"/>'
    wpts = [(cx - R - 10, water_y + 4 * math.sin(t * 3)), (cx, water_y - 3 * math.sin(t * 3)), (cx + R + 10, water_y + 4 * math.sin(t * 3 + 1)),
            (cx + R + 10, cy + R + 10, 1), (cx - R - 10, cy + R + 10, 1)]
    inner += blob(wpts, "#8fcde0")
    inner += blob([(cx - R - 10, cy + R * .2), (cx + R + 10, cy + R * .1), (cx + R + 10, cy + R + 10), (cx - R - 10, cy + R + 10)], "#76bcd3", .9)
    # камушки
    rs = rsd(seed)
    for j in range(16):
        gx = cx + rs.uniform(-.75, .75) * R
        gy = cy + R * (.80 - .12 * (1 - abs(gx - cx) / R)) + rs.uniform(-6, 6)
        inner += shape(ellipse_pts(gx, gy, R * rs.uniform(.06, .1), R * rs.uniform(.04, .07), 8), ["#e7b46a", "#c9876a", "#f2e2c4", "#8fb07a"][j % 4],
                       w=2.0, seed=seed + 10 + j)
    # водоросль
    sw = 8 * math.sin(t * 1.6)
    inner += line([(cx - R * .45, cy + R * .78), (cx - R * .5 + sw * .3, cy + R * .4), (cx - R * .42 + sw, cy + R * .05)], 8, "#5b944c",
                  seed=seed + 40, taper=.2, wmin=.4)
    inner += line([(cx - R * .36, cy + R * .78), (cx - R * .3 + sw * .4, cy + R * .48), (cx - R * .36 + sw * .8, cy + R * .25)], 7, "#6aa457",
                  seed=seed + 41, taper=.2, wmin=.4)
    if fish_fn:
        inner += fish_fn()
    # пузырьки
    for j in range(4):
        u = ((t * .55 + j * .27) % 1.0)
        bx = cx + R * (.25 + .12 * j) + 6 * math.sin(t * 3 + j)
        by = cy + R * .5 - u * R * .9
        if by > water_y + 8:
            inner += shape(ellipse_pts(bx, by, 6 + j, 6 + j, 8), "#d9f1f8", w=1.8, seed=seed + 60 + j)
    # блик стекла
    inner += line([(cx - R * .78, cy - R * .1), (cx - R * .72, cy + R * .3), (cx - R * .55, cy + R * .58)], R * .07, "#ffffff", seed=seed + 70,
                  op=.85, taper=.4)
    inner += line([(cx + R * .55, cy - R * .5), (cx + R * .66, cy - R * .34)], R * .045, "#ffffff", seed=seed + 71, op=.8)
    o.append(f'<path d="{lib.fill_d(glass)}" fill="#e9f3f2"/><g clip-path="url(#{gclip})">{inner}</g>')
    o.append(f'<path d="{lib.ink_closed(glass, 5.0 * lib.INK_K[0] * max(.6, R / 160), seed=seed + 1)}" fill="{INK}"/>')
    # горлышко (кольцо сверху)
    rim = ellipse_pts(cx, top, R * .64, R * .1, 16)
    o.append(shape(rim, "#d5ecee", blob(ellipse_pts(cx, top + R * .02, R * .56, R * .06, 14), "#b9dde3"), w=3.6 * max(.6, R / 160),
                   seed=seed + 2))
    return "".join(o)


# ═════════════════════════ облачко-реплика и облако-мысль ═════════════════════════
PAPER = "#fffdf6"


def speech_bubble(cx, cy, rx, ry, tip, s=1.0, seed=950):
    """Овальное облачко с хвостиком к точке tip (мир). s — масштаб «выскока» (0..1+)."""
    tx, ty = tip
    ang_t = math.atan2((ty - cy) / ry, (tx - cx) / rx)
    pts = []
    n = 40
    for i in range(n):
        a = ang_t + .26 + (2 * math.pi - .52) * i / (n - 1)
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    pts = [pts[0]] + pts[1:-1] + [pts[-1], (tx, ty, 1)]
    pts = [((p[0] - cx) * s + cx, (p[1] - cy) * s + cy) + tuple(p[2:]) for p in pts]
    inner = f'<rect x="{cx - rx * 2:.1f}" y="{cy - ry * 2:.1f}" width="{rx * 4:.1f}" height="{ry * 4:.1f}" fill="#efe7d4"/>'
    inner += blob(ellipse_pts(cx - rx * .06 * s, cy - ry * .1 * s, rx * .97 * s, ry * .93 * s, 24), PAPER)
    return shape(pts, PAPER, inner, w=5.0, seed=seed)


def cloud_pts(cx, cy, rx, ry, n_bumps=9, s=1.0, phase=0.0):
    pts = []
    N = n_bumps * 10
    for i in range(N):
        a = 2 * math.pi * i / N + phase
        bump = abs(math.sin(n_bumps * (a - phase) / 2))
        r = 1.0 + .13 * bump
        pts.append((cx + rx * s * r * math.cos(a), cy + ry * s * r * math.sin(a)))
    # острые «впадины» между буграми — углы
    out = []
    for i, p in enumerate(pts):
        out.append(p + ((1,) if i % 10 == 0 else ()))
    return out


def thought_cloud(cx, cy, rx, ry, src, s=1.0, trail=1.0, seed=970, t=0.0):
    """Облако-мысль и три кружка-следа к голове (src). trail 0..1 — сколько кружков уже видно."""
    o = []
    dx, dy = src[0] - cx, src[1] - cy
    for j, (u, r) in enumerate([(.86, 14), (.74, 22), (.6, 32)]):
        if trail < (j + 1) / 3 - .01:
            continue
        x, y = cx + dx * u, cy + dy * u
        o.append(shape(ellipse_pts(x, y, r, r * .86, 12), PAPER, "", w=4.0, seed=seed + j))
    if s > 0.02:
        pts = cloud_pts(cx, cy, rx, ry, 9, s, phase=.3 + .03 * math.sin(t * 2))
        inner = f'<rect x="{cx - rx * 2:.1f}" y="{cy - ry * 2:.1f}" width="{rx * 4:.1f}" height="{ry * 4:.1f}" fill="#efe7d4"/>'
        inner += blob(ellipse_pts(cx - rx * .06 * s, cy - ry * .12 * s, rx * 1.0 * s, ry * .95 * s, 24), PAPER)
        o.append(shape(pts, PAPER, inner, w=5.0, seed=seed + 5))
    return "".join(o)


def burst(cx, cy, k, u, seed=990, color=INK, n=6, r0=60, r1=110):
    """Штрихи-лучики «удара» вокруг точки: u 0..1 — разлёт."""
    if u <= 0 or u >= 1:
        return ""
    o = []
    for i in range(n):
        a = 2 * math.pi * i / n + .4
        ra = r0 + (r1 - r0) * u
        rb = ra + 46 * (1 - .5 * u)
        o.append(line([(cx + math.cos(a) * ra * k, cy + math.sin(a) * ra * k), (cx + math.cos(a) * rb * k, cy + math.sin(a) * rb * k)],
                      5 * k * (1 - .5 * u), color, seed=seed + i, taper=.5, wmin=.3))
    return "".join(o)


# ═════════════════════════ комната Димы ═════════════════════════
WALL, WALL_SH, WALL_ST = "#cfdcc4", "#b6c6a8", "#bfcfb3"
WOOD, WOOD_SH, WOOD_HI, WOOD_DK = "#a8693f", "#7f4b2b", "#c88a58", "#5e3720"


def room_wall(t, x0=-500, x1=1600, y0=-500, y1=2400):
    o = []
    g = lib.lin_grad([(0, "#b9c9ac", 1), (.4, WALL, 1), (1, "#dfe6cf", 1)], 0, 0, 0, 1500, units="userSpaceOnUse")
    o.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>')
    # обои: тонкие вертикальные полоски с ромбиками
    for k in range(-6, 20):
        x = k * 96
        o.append(line([(x, y0), (x, y1)], 3.0, WALL_ST, seed=2000 + k, taper=.02, wmin=.9, op=.9))
        for j in range(-4, 26):
            y = j * 110 + (k % 2) * 55
            o.append(blob([(x + 48, y - 9), (x + 55, y), (x + 48, y + 9), (x + 41, y)], WALL_ST, .9))
    # тёплое пятно света от лампы
    gl = lib.rad_grad([(0, "#fff3d2", .55), (.5, "#ffe2a8", .22), (1, "#ffd890", 0)], 860, 560, 620)
    o.append(f'<rect x="240" y="-60" width="1240" height="1240" fill="url(#{gl})"/>')
    return "".join(o)


def window(x0, y0, x1, y1, t, seed=2100):
    """Окно днём: небо, облака, крыши; рама, подоконник, занавеска слева."""
    o = []
    clip = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    g = lib.lin_grad([(0, "#8fc4e6", 1), (1, "#d6ecf4", 1)], 0, y0, 0, y1, units="userSpaceOnUse")
    sky = f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>'
    for j, (cx, cy, s) in enumerate([(x0 + 90 + 14 * math.sin(t * .2), y0 + 110, 1.0), (x1 - 80 - 10 * math.sin(t * .17), y0 + 200, .8)]):
        sky += shape(cloud_pts(cx, cy, 70 * s, 26 * s, 7), "#ffffff", "", w=2.6, seed=seed + j)
    # дома напротив
    for j, (hx, hw, hh, col) in enumerate([(x0 - 20, 150, 260, "#c97e5c"), (x0 + 140, 170, 330, "#d9b27a"), (x0 + 320, 190, 230, "#b8705a")]):
        top = y1 - hh
        b = shape([(hx, top, 1), (hx + hw, top, 1), (hx + hw, y1 + 20, 1), (hx, y1 + 20, 1)], col,
                  blob([(hx + hw * .7, top), (hx + hw, top), (hx + hw, y1 + 20), (hx + hw * .7, y1 + 20)], lib.mul(col, (.82, .8, .8)), .9), w=3,
                  seed=seed + 10 + j)
        for r in range(4):
            for c in range(2):
                wx, wy = hx + 26 + c * (hw - 70) / 1.0 * .55 + c * 20, top + 34 + r * 70
                if wy + 40 < y1:
                    b += shape(rect_pts(wx, wy, wx + 34, wy + 44, 3), "#8fb6cf", "", w=2.2, seed=seed + 20 + j * 10 + r * 2 + c)
        sky += b
    o.append(f'<g clip-path="url(#{clip})">{sky}</g>')
    # рама
    fr = "#f4efe4"
    m = 22
    o.append(shape([(x0 - m, y0 - m, 1), (x1 + m, y0 - m, 1), (x1 + m, y1 + m, 1), (x0 - m, y1 + m, 1), (x0 - m, y0 - m, 1),
                    (x0, y0, 1), (x0, y1, 1), (x1, y1, 1), (x1, y0, 1), (x0, y0, 1)], fr, w=3.8, seed=seed + 40))
    xm = (x0 + x1) / 2
    o.append(shape(rect_pts(xm - 9, y0, xm + 9, y1), fr, "", w=3.2, seed=seed + 41))
    ym = y0 + (y1 - y0) * .42
    o.append(shape(rect_pts(x0, ym - 8, x1, ym + 8), fr, "", w=3.2, seed=seed + 42))
    # подоконник
    o.append(shape(rect_pts(x0 - 50, y1 + m, x1 + 50, y1 + m + 30, 4), "#ece4d4", blob([(x0 - 50, y1 + m + 18), (x1 + 50, y1 + m + 18),
                                                                                          (x1 + 50, y1 + m + 30), (x0 - 50, y1 + m + 30)], "#cfc4ae"),
                   w=3.6, seed=seed + 43))
    return "".join(o)


def curtain(x, y0, y1, w, t, col="#d9725a", seed=2200, side=1):
    sway = 6 * math.sin(t * 1.1)
    pts = [(x, y0, 1), (x + w * side, y0, 1), (x + w * .7 * side + sway, (y0 + y1) / 2), (x + w * .9 * side + sway * 1.4, y1, 1), (x, y1, 1)]
    inner = ""
    for k in range(3):
        xx = x + w * side * (.25 + .25 * k)
        inner += line([(xx, y0 + 10), (xx + sway * .4, (y0 + y1) / 2), (xx + sway * .9, y1 - 10)], 2.6, lib.mul(col, (.75, .7, .7)), seed=seed + 1 + k,
                      op=.85)
    inner += blob([(x, y0), (x + w * .3 * side, y0), (x + w * .3 * side, y1), (x, y1)], lib.mul(col, (.85, .8, .8)), .9)
    return shape(pts, col, inner, w=3.8, seed=seed)


def pot(x, y, k, seed, leaves=7, col="#c96b4a", t=0.0):
    o = []
    rs = np.random.RandomState(seed)
    for i in range(leaves):
        a = math.radians(-90 + (i - leaves / 2 + .5) * 24 + rs.uniform(-6, 6) + 3 * math.sin(t * 1.3 + i))
        L = (60 + rs.uniform(-8, 14)) * k
        bx, by = x, y - 46 * k
        tip = (bx + math.cos(a) * L, by + math.sin(a) * L)
        nrm = (-math.sin(a), math.cos(a))
        mid = (bx + math.cos(a) * L * .5, by + math.sin(a) * L * .5)
        lf = [(bx, by), (mid[0] + nrm[0] * 13 * k, mid[1] + nrm[1] * 13 * k), (tip[0], tip[1], 1), (mid[0] - nrm[0] * 13 * k, mid[1] - nrm[1] * 13 * k)]
        o.append(shape(lf, "#6aa457" if i % 2 else "#5b944c", line([(bx, by), tip], 1.6, "#3f6f36", seed=seed + 30 + i, op=.8), w=3.0,
                       seed=seed + i))
    pt = [(x - 34 * k, y - 50 * k, 1), (x + 34 * k, y - 50 * k, 1), (x + 26 * k, y, 1), (x - 26 * k, y, 1)]
    o.append(shape(pt, col, blob([(x + 10 * k, y - 50 * k), (x + 34 * k, y - 50 * k), (x + 26 * k, y), (x + 6 * k, y)], lib.mul(col, (.78, .75, .75)), .9) +
                   blob([(x - 36 * k, y - 50 * k), (x + 36 * k, y - 50 * k), (x + 36 * k, y - 40 * k), (x - 36 * k, y - 40 * k)], lib.mul(col, (.85, .8, .8))),
                   w=3.4, seed=seed + 20))
    return "".join(o)


def shelf_books(x0, y, x1, t, seed=2300):
    o = []
    o.append(shape(rect_pts(x0, y, x1, y + 22), WOOD_HI, blob([(x0, y + 12), (x1, y + 12), (x1, y + 22), (x0, y + 22)], WOOD_SH, .9), w=3.6, seed=seed))
    for k, x in enumerate((x0 + 40, x1 - 40)):
        o.append(shape([(x - 8, y + 22, 1), (x + 8, y + 22, 1), (x + 8, y + 60, 1), (x - 30, y + 22, 1)], WOOD_DK, w=3, seed=seed + 1 + k))
    x = x0 + 30
    cols = ["#3f7a72", "#d8483c", "#e8c35a", "#4f6fa0", "#8a5a9a", "#e2874a", "#5b944c"]
    rs = rsd(seed)
    for j in range(7):
        h = rs.uniform(90, 128)
        wdt = rs.uniform(26, 38)
        col = cols[j % len(cols)]
        if j == 5:       # наклонённая книга
            pts = [(x, y, 1), (x + 18, y - h * .95, 1), (x + 18 + wdt, y - h * .9, 1), (x + wdt, y, 1)]
        else:
            pts = rect_pts(x, y - h, x + wdt, y)
        o.append(shape(pts, col, blob([(x + wdt * .62, y - h - 10), (x + wdt + 20, y - h - 10), (x + wdt + 20, y), (x + wdt * .62, y)],
                                      lib.mul(col, (.78, .75, .78)), .8) +
                       line([(x + 6, y - h * .78), (x + wdt - 6, y - h * .78)], 2.0, lib.mul(col, (1.3, 1.3, 1.3)), seed=seed + 20 + j, op=.8),
                       w=3.0, seed=seed + 10 + j))
        x += wdt + (22 if j == 5 else 3)
    o.append(pot(x1 - 80, y, .8, seed + 40, leaves=6, col="#e3d3b2", t=t))
    return "".join(o)


def poster(x0, y0, x1, y1, seed=2400):
    """Постер в рамке: горы и солнце (без букв)."""
    o = []
    o.append(shape(rect_pts(x0, y0, x1, y1), "#2f2a33", w=3.6, seed=seed))
    ix0, iy0, ix1, iy1 = x0 + 14, y0 + 14, x1 - 14, y1 - 14
    inner = f'<rect x="{ix0}" y="{iy0}" width="{ix1 - ix0}" height="{iy1 - iy0}" fill="#f6d9a6"/>'
    w, h = ix1 - ix0, iy1 - iy0
    inner += blob(ellipse_pts(ix0 + w * .68, iy0 + h * .34, w * .14, w * .14, 14), "#e9774a")
    inner += blob([(ix0 - 10, iy1 + 10), (ix0 + w * .32, iy0 + h * .45), (ix0 + w * .58, iy0 + h * .78), (ix0 + w * .8, iy0 + h * .5),
                   (ix1 + 10, iy0 + h * .8), (ix1 + 10, iy1 + 10)], "#3f7a72")
    inner += blob([(ix0 - 10, iy1 + 10), (ix0 + w * .2, iy0 + h * .72), (ix0 + w * .5, iy1 - h * .08), (ix1 + 10, iy0 + h * .86), (ix1 + 10, iy1 + 10)],
                  "#2f5d57")
    o.append(shape(rect_pts(ix0, iy0, ix1, iy1), "#f6d9a6", inner, w=2.6, seed=seed + 1))
    return "".join(o)


def lamp(x, y, t, seed=2500):
    """Настенный светильник-бра."""
    o = []
    o.append(shape(rect_pts(x - 12, y - 60, x + 12, y - 26), "#b08a4a", w=3, seed=seed))
    sh = [(x - 46, y - 26), (x + 46, y - 26), (x + 30, y + 36, 1), (x - 30, y + 36, 1)]
    o.append(shape(sh, "#f6e3b5", blob([(x - 46, y - 26), (x + 46, y - 26), (x + 42, y - 12), (x - 42, y - 12)], "#ffffff", .5), w=3.4, seed=seed + 1))
    o.append(blob(ellipse_pts(x, y + 38, 28, 7, 10), "#fff4d2"))
    return "".join(o)


# ═════════════════════════ стол, блокнот, ручка ═════════════════════════
def desk(x0, y0, x1, depth=90, thick=30, seed=2600):
    """Столешница в лёгкой перспективе: верх (x0..x1, y0..y0+depth), кромка, ножка-тумба уходит вниз за кадр."""
    o = []
    top = [(x0 + 40, y0, 1), (x1 + 60, y0, 1), (x1 + 40, y0 + depth, 1), (x0, y0 + depth, 1)]
    o.append(shape([(x0 + 30, y0 + depth + thick - 4, 1), (x1 + 30, y0 + depth + thick - 4, 1), (x1 + 30, y0 + 900, 1), (x0 + 30, y0 + 900, 1)],
                   "#8a5534", blob([(x0 + 30, y0 + depth), (x1 + 30, y0 + depth), (x1 + 30, y0 + depth + 60), (x0 + 30, y0 + depth + 60)], "#5e3720", .8),
                   w=4, seed=seed + 3))
    o.append(shape([(x0, y0 + depth, 1), (x1 + 40, y0 + depth, 1), (x1 + 40, y0 + depth + thick, 1), (x0, y0 + depth + thick, 1)], WOOD_SH,
                   line([(x0 + 10, y0 + depth + thick * .5), (x1 + 20, y0 + depth + thick * .5)], 1.6, WOOD_DK, seed=seed + 4, op=.6), w=4,
                   seed=seed + 1))
    # ящик стола с ручкой
    dy0 = y0 + depth + thick + 26
    o.append(shape(rect_pts(x0 + 70, dy0, x1 - 20, dy0 + 150, 6), "#9a6845", blob([(x0 + 70, dy0 + 120), (x1 - 20, dy0 + 120), (x1 - 20, dy0 + 150),
                                                                                    (x0 + 70, dy0 + 150)], "#6f4428", .8), w=3.4, seed=seed + 5))
    hx = (x0 + x1) / 2 + 20
    o.append(shape(rect_pts(hx - 50, dy0 + 60, hx + 50, dy0 + 78, 8), "#e2c46a", "", w=3, seed=seed + 6))
    inner = ""
    rs = rsd(seed)
    for j in range(7):
        yy = y0 + 10 + j * depth / 7
        xa = x0 + rs.uniform(20, 120)
        inner += line([(xa, yy), (xa + rs.uniform(120, 300), yy + 2)], 1.8, WOOD_SH, seed=seed + 10 + j, op=.55)
    o.append(shape(top, WOOD_HI, inner, w=4, seed=seed))
    return "".join(o)


def notebook(cx, cy, k, seed=2700, flutter=0.0):
    """Раскрытый пустой блокнот на столе (сверху, в перспективе), пружина посередине."""
    o = []
    sx, sy = 150 * k, 62 * k
    sk = 26 * k
    o.append(blob([(cx - sx - 8 * k + sk, cy - sy + 10 * k), (cx + sx + 8 * k + sk, cy - sy + 10 * k), (cx + sx + 8 * k, cy + sy + 12 * k),
                   (cx - sx - 8 * k, cy + sy + 12 * k)], "#5e3720", .35))
    for side in (-1, 1):
        xa, xb = (cx - sx, cx - 4 * k) if side < 0 else (cx + 4 * k, cx + sx)
        lift = flutter * 10 * k if side > 0 else 0
        pts = [(xa + sk, cy - sy - (lift if side > 0 else 0), 1), (xb + sk, cy - sy - (lift * .3 if side < 0 else lift), 1), (xb, cy + sy, 1),
               (xa, cy + sy, 1)]
        inner = ""
        for j in range(5):
            u = (j + 1) / 6
            y = cy - sy + 2 * sy * u
            off = sk * (1 - u)
            inner += line([(xa + off + 14 * k, y), (xb + off - 14 * k, y)], 1.6, "#9fc0d9", seed=seed + 10 + j + (side > 0) * 10, op=.9)
        o.append(shape(pts, "#fbf8ef", inner, w=3.2, seed=seed + (1 if side > 0 else 2)))
    # пружина
    for j in range(8):
        u = (j + .5) / 8
        y = cy - sy + 2 * sy * u
        x = cx + sk * (1 - u)
        o.append(shape(ellipse_pts(x, y, 8 * k, 5 * k, 8), "#b9b6b0", "", w=2.2, seed=seed + 40 + j))
    return "".join(o)


def pen(x, y, ang, k=1.0, seed=2800):
    """Ручка: центр, угол (град). Синий корпус, колпачок с клипом."""
    L = 130 * k
    r = 9 * k

    def T(pts):
        return tf_pts(pts, x, y, 1.0, ang)

    body = T([(-L / 2, -r, 1), (L / 2 - 24 * k, -r, 1), (L / 2, 0, 1), (L / 2 - 24 * k, r, 1), (-L / 2, r, 1)])
    inner = blob(T([(-L / 2, 2 * k), (L / 2, 2 * k), (L / 2, r + 2), (-L / 2, r + 2)]), "#2c4d85", .9)
    inner += blob(T([(L / 2 - 26 * k, -r - 2), (L / 2 + 2, -r - 2), (L / 2 + 2, r + 2), (L / 2 - 26 * k, r + 2)]), "#e8e2d4")
    inner += blob(T([(L / 2 - 10 * k, -4 * k), (L / 2 + 2, -4 * k), (L / 2 + 2, 4 * k), (L / 2 - 10 * k, 4 * k)]), "#2b2733")
    o = shape(body, "#3d68b0", inner, w=2.8, seed=seed)
    o += shape(T([(-L / 2 - 4 * k, -r - 1, 1), (-L / 2 + 34 * k, -r - 1, 1), (-L / 2 + 34 * k, r + 1, 1), (-L / 2 - 4 * k, r + 1, 1)]), "#2c4d85", "",
               w=2.8, seed=seed + 1)
    o += shape(T([(-L / 2 + 2 * k, -r - 4 * k, 1), (-L / 2 + 40 * k, -r - 4 * k, 1), (-L / 2 + 40 * k, -r + 1, 1), (-L / 2 + 2 * k, -r + 1, 1)]),
               "#c9c4ba", "", w=2.2, seed=seed + 2)
    return o


def mug(x, y, k=1.0, col="#e85f4f", seed=2850):
    o = []
    o.append(shape(ellipse_pts(x + 46 * k, y - 40 * k, 20 * k, 24 * k, 10), "none", w=3.6, seed=seed + 1))
    body = [(x - 40 * k, y - 80 * k, 1), (x + 40 * k, y - 80 * k, 1), (x + 36 * k, y, 1), (x - 36 * k, y, 1)]
    o.append(shape(body, col, blob([(x + 10 * k, y - 80 * k), (x + 40 * k, y - 80 * k), (x + 36 * k, y), (x + 12 * k, y)], lib.mul(col, (.8, .75, .75)), .9),
                   w=3.6, seed=seed))
    o.append(shape(ellipse_pts(x, y - 80 * k, 40 * k, 9 * k, 14), "#5a3a24", "", w=3.0, seed=seed + 2))
    return "".join(o)


# ═════════════════════════ прихожая ═════════════════════════
HALL, HALL_SH = "#e6d4b8", "#cdb895"


def hall_wall(t, x0=-500, x1=1600, y0=-500, y1=2400):
    o = []
    g = lib.lin_grad([(0, "#d2bd9b", 1), (.45, HALL, 1), (1, "#efe1c8", 1)], 0, 0, 0, 1500, units="userSpaceOnUse")
    o.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>')
    # обои мелким узором: веточки
    rs = rsd(31)
    for j in range(140):
        x, y = rs.uniform(x0 + 300, x1 - 300), rs.uniform(y0 + 300, y1 - 400)
        o.append(line([(x, y), (x + 8, y - 14)], 2.0, HALL_SH, seed=3000 + j, op=.7))
        o.append(blob(ellipse_pts(x + 9, y - 16, 5, 3, 6, rot=-60), HALL_SH, .7))
    # панель снизу
    o.append(shape(rect_pts(x0, 1330, x1, y1), "#6f8f8a", blob([(x0, 1330), (x1, 1330), (x1, 1356), (x0, 1356)], "#557570", .9), w=4, seed=3200))
    o.append(shape(rect_pts(x0, 1312, x1, 1338), "#f2ebe0", "", w=3.4, seed=3201))
    gl = lib.rad_grad([(0, "#fff3d2", .6), (.5, "#ffe2a8", .25), (1, "#ffd890", 0)], 620, 260, 700)
    o.append(f'<rect x="-100" y="-460" width="1440" height="1440" fill="url(#{gl})"/>')
    return "".join(o)


def door(x0, y0, x1, y1, seed=3300):
    o = []
    o.append(shape(rect_pts(x0 - 26, y0 - 26, x1 + 26, y1 + 400), "#f2ebe0", "", w=4, seed=seed))
    inner = ""
    for (a, b, c, d) in [(x0 + 40, y0 + 50, x1 - 40, y0 + 420), (x0 + 40, y0 + 480, x1 - 40, y1 - 40)]:
        inner += shape(rect_pts(a, b, c, d, 6), "#8c5a3a", blob([(c - 22, b), (c, b), (c, d), (c - 22, d)], "#6f4428", .8), w=3, seed=seed + 3)
    inner += blob([(x1 - 60, y0), (x1, y0), (x1, y1 + 400), (x1 - 60, y1 + 400)], "#6f4428", .6)
    o.append(shape(rect_pts(x0, y0, x1, y1 + 400), "#9a6845", inner, w=4, seed=seed + 1))
    # ручка
    hx, hy = x1 - 50, y0 + 470
    o.append(shape(ellipse_pts(hx, hy, 16, 16, 10), "#e2c46a", blob(ellipse_pts(hx - 4, hy - 4, 6, 6, 8), "#fff0b0"), w=3, seed=seed + 2))
    o.append(shape(rect_pts(hx - 50, hy - 8, hx + 4, hy + 8, 6), "#e2c46a", "", w=3, seed=seed + 4))
    return "".join(o)


def coat(x, y, t, seed=3400):
    """Куртка на крючке: висит, чуть качается."""
    sw = 1.5 * math.sin(t * 1.3 + 1)
    pts = [(x - 20, y + 10), (x + 20, y + 10), (x + 110, y + 90), (x + 130, y + 420), (x + 40, y + 440), (x, y + 380), (x - 40, y + 440),
           (x - 130, y + 420), (x - 110, y + 90)]
    inner = blob([(x + 20, y), (x + 140, y + 60), (x + 140, y + 460), (x + 40, y + 460)], "#2f5d57", .8)
    inner += line([(x, y + 40), (x, y + 380)], 2.4, "#24474a", seed=seed + 2)
    for j in range(4):
        inner += f'<circle cx="{x + 14}" cy="{y + 110 + j * 70}" r="7" fill="#c9c2b0"/>'
    inner += line([(x - 90, y + 300), (x - 40, y + 296)], 2.4, "#24474a", seed=seed + 3)
    peg = line([(x, y - 34), (x, y + 6), (x + 10, y + 18)], 7, "#9a9590", seed=seed + 9, taper=.2, wmin=.7)
    peg = shape(ellipse_pts(x, y - 34, 14, 14, 10), WOOD_HI, "", w=3, seed=seed + 8) + peg
    return peg + f'<g transform="rotate({sw:.2f} {x} {y})">{shape(pts, "#3f7a72", inner, w=4.2, seed=seed)}</g>'


def key_rack(x0, y, x1, seed=3500):
    """Доска-ключница с тремя крючками; возвращает (svg, координаты кончиков крючков)."""
    o = []
    o.append(shape(rect_pts(x0, y - 40, x1, y + 40, 8), WOOD_HI, blob([(x0, y + 18), (x1, y + 18), (x1, y + 40), (x0, y + 40)], WOOD_SH, .9) +
                   f'<circle cx="{x0 + 20}" cy="{y - 20}" r="5" fill="{WOOD_DK}"/><circle cx="{x1 - 20}" cy="{y - 20}" r="5" fill="{WOOD_DK}"/>',
                   w=3.8, seed=seed))
    hooks = []
    for j in range(3):
        hx = x0 + (x1 - x0) * (j + 1) / 4
        o.append(line([(hx, y + 6), (hx, y + 44), (hx + 6, y + 58), (hx + 18, y + 52)], 6.5, "#9a9590", seed=seed + 10 + j, taper=.2, wmin=.7))
        o.append(line([(hx - 2, y + 8), (hx - 2, y + 42)], 2.0, "#e6e2da", seed=seed + 20 + j, taper=.2, wmin=.7))
        hooks.append((hx + 6, y + 56))
    return "".join(o), hooks


def keys(rx, ry, ang, k=1.0, seed=3600):
    """Связка ключей: кольцо в (rx, ry), ключи висят под углом ang (град, 0 — вниз)."""
    o = []

    def T(pts):
        return tf_pts(pts, rx, ry, k, ang)

    # брелок-рыбка (маленькая, сбоку)
    fx, fy = T([(-22, 46)])[0]
    # ключ латунный
    kb = [(-6, 20), (6, 20), (8, 34), (22, 40), (22, 66), (6, 72), (6, 140, 1), (12, 146), (6, 152), (14, 158), (6, 166, 1), (-6, 172, 1), (-6, 72),
          (-22, 66), (-22, 40), (-8, 34)]
    o.append(shape(T(kb), "#e2bb54", blob(T([(0, 72), (8, 72), (8, 168), (0, 170)]), "#b88f2c", .9) +
                   f'<circle cx="{T([(0, 52)])[0][0]:.1f}" cy="{T([(0, 52)])[0][1]:.1f}" r="{6 * k:.2f}" fill="#7d5f1c"/>', w=2.8 * k, seed=seed))
    # ключ серебряный, чуть повернут
    def T2(pts):
        return tf_pts(pts, rx, ry, k, ang + 26)
    kb2 = [(-6, 20), (6, 20), (6, 34), (20, 44), (16, 70), (6, 74), (6, 130, 1), (14, 134), (6, 142), (6, 150, 1), (-6, 156, 1), (-6, 74), (-16, 70),
           (-20, 44), (-6, 34)]
    o.insert(0, shape(T2(kb2), "#c7cdd4", blob(T2([(0, 74), (6, 74), (6, 150), (0, 154)]), "#9aa3ad", .9), w=2.8 * k, seed=seed + 1))
    # брелок-рыбка на цепочке
    def T3(pts):
        return tf_pts(pts, rx, ry, k, ang - 30)
    o.insert(0, line(T3([(0, 10), (0, 40)]), 2.4 * k, "#9a9590", seed=seed + 7))
    fxy = T3([(0, 78)])[0]
    o.insert(0, fish(fxy[0], fxy[1], .22 * k, 0.0, flip=1, rot=ang - 30 + 90, seed=seed + 8))
    # кольцо
    o.append(f'<path d="{lib.ink_closed(ellipse_pts(rx, ry, 16 * k, 16 * k, 14), 4.2 * k, seed=seed + 3)}" fill="#8c8780"/>')
    o.append(f'<path d="{lib.ink_open([(rx - 10 * k, ry - 10 * k), (rx - 2 * k, ry - 15 * k)], 2 * k, seed=seed + 4)}" fill="#e6e2da"/>')
    return "".join(o)


def phone(x, y, ang, k=1.0, glow=0.0, seed=3700):
    """Телефон экраном к зрителю: центр, угол (град)."""
    def T(pts):
        return tf_pts(pts, x, y, k, ang)
    o = shape(T(rect_pts(-46, -88, 46, 88, 14)), "#26232b", blob(T([(18, -92), (50, -92), (50, 92), (18, 92)]), "#1a181e", .8), w=3.2 * k, seed=seed)
    scr = "#8fc6e6" if glow > 0 else "#3a4a5e"
    o += shape(T(rect_pts(-38, -76, 38, 76, 8)), scr, blob(T([(-38, -76), (10, -76), (-38, 10)]), "#ffffff", .25) +
               "".join(blob(T(rect_pts(-28 + 22 * (j % 3), -60 + 24 * (j // 3), -12 + 22 * (j % 3), -44 + 24 * (j // 3), 3)),
                            ["#f2a23a", "#5b944c", "#e85f4f", "#ffffff"][j % 4], .9) for j in range(9)), w=2.0 * k, seed=seed + 1)
    return o
