"""Кухня Димы днём рилса 31 (сцена kitchen): невысокий пузатый холодильник «как у бабушки», рядом тумба со
столешницей, окно с дневным небом, чайник парит.
s13: рука Димы (горчичный рукав) шлёпает белый листок на дверцу холодильника на «холодильнике» (21.04) — под ладонью
магнит-рыбка; рука уходит, на «листок» (21.76) листок качается на магните и замирает. Камера — наезд к листку.
s14: крупно листок: рука с маркером пишет «хлеб», «оплатить свет», «маме позвонить» (буквы — контуры Caveat 600,
проявляются по ходу пера, glyphs.json); «пишет» (23.6) — внутри второй строки.
s16: кот вразвалку подходит к холодильнику, на «листку» (27.72) встаёт на задние лапы и касается листка; на «ужин»
(29.04) у строки «покормить кота» ставится галочка, кот довольно щурится.
s17: крупно кот сидит у холодильника, смотрит в камеру и медленно моргает, огонёк горит (до 32.7)."""
import json
import math
import os

import numpy as np

import cat
import cat2
import fishy
import hand
import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix,
                 rad_grad, rect_pts, shape, smooth, svg, T)
from parts import sausage

G = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "glyphs.json")))
_ST = {}
SKIN, SKIN_SH, SKIN_SH2, NAIL = hand.SKIN, hand.SKIN_SH, hand.SKIN_SH2, hand.NAIL
HOOD, HOOD_SH, FOLD = hand.HOOD, hand.HOOD_SH, hand.FOLD

FLOOR = 1500
FX0, FX1, FTOP = 250, 720, 330           # холодильник
CTOP = 1050                              # столешница тумбы
# листок на дверце
PX0, PX1, PY0, PY1 = 305, 635, 700, 1145
MAG = (470, 722)                         # магнит-рыбка (точка подвеса листка)
PROT = -1.5                              # наклон листка в покое
FS = 42
SC = FS / G["upm"]
TX0 = PX0 + 26
BASES = [PY0 + 122, PY0 + 202, PY0 + 282, PY0 + 372]
SLOTS = [(22.42, 22.86), (22.98, 23.80), (23.92, 24.78)]
INKC = "#1d2236"
SLAP = 21.04
SWING = 21.76
REACH = 27.72
CHECK = 29.04
CATX = 772


# ─────────────────────────────── письмо (как scene_note рилса 26)
def build_lines():
    out = []
    for li in range(4):
        gl = G["lines"][li]
        x = TX0
        base = BASES[li]
        path, gls = [], []
        for gi, g in enumerate(gl):
            gls.append(dict(g=g, x=x))
            for st in g.get("strokes", []):
                for k, (px, py) in enumerate(st):
                    path.append((x + px * SC, base - py * SC, gi, k > 0))
            x += g["adv"] * SC
        P = np.array([(p[0], p[1]) for p in path])
        seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
        down = np.array([p[3] for p in path[1:]])
        cum = np.concatenate([[0], np.cumsum(np.where(down, seg, seg * 0.4))])
        out.append(dict(path=path, P=P, cum=cum / cum[-1], gls=gls, base=base, x1=x))
    return out


L = build_lines()


def progress(li, t):
    a, b = SLOTS[li]
    u = clamp((t - a) / (b - a))
    return u * 0.85 + 0.15 * (u * u * (3 - 2 * u))


def tip_at(li, p):
    ln = L[li]
    i = int(np.searchsorted(ln["cum"], p, side="right")) - 1
    i = max(0, min(i, len(ln["P"]) - 2))
    c0, c1 = ln["cum"][i], ln["cum"][i + 1]
    q = 0 if c1 <= c0 else (p - c0) / (c1 - c0)
    x, y = ln["P"][i] + (ln["P"][i + 1] - ln["P"][i]) * q
    lift = 0.0 if ln["path"][i + 1][3] else math.sin(math.pi * q)
    return x, y, i, lift


def text_line(li, t, done=False):
    ln = L[li]
    if li < 3:
        a, b = SLOTS[li]
        if t <= a and not done:
            return ""
        p = 1.0 if done else progress(li, t)
    else:
        p = 1.0
    s = []
    if p >= 1:
        cur, i_now = len(ln["gls"]), len(ln["P"]) - 1
    else:
        _, _, i_now, _ = tip_at(li, p)
        cur = ln["path"][i_now][2]
    for gi, o in enumerate(ln["gls"]):
        g = o["g"]
        if not g["bounds"] or gi > cur:
            continue
        body = f'<path d="{g["d"]}" transform="translate({f(o["x"])} {ln["base"]}) scale({SC:.5f} {-SC:.5f})" fill="{INKC}"/>'
        if gi == cur and p < 1:
            pts = [(x, y, d) for (x, y, gg, d) in ln["path"][:i_now + 1] if gg == gi]
            tx, ty, _, _ = tip_at(li, p)
            pts.append((tx, ty, True))
            d = ""
            for k, (x, y, dn) in enumerate(pts):
                d += ("L" if (dn and k > 0) else "M") + f"{f(x)} {f(y)}"
            wpx = g["width"] * SC * 1.25
            mid = lib.uid("m")
            DEFS.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-600" y="-600" width="3400" height="3200">'
                        f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{f(wpx)}" stroke-linecap="round" stroke-linejoin="round"/></mask>')
            body = f'<g mask="url(#{mid})">{body}</g>'
        s.append(body)
    return "".join(s)


def pen_tip(t):
    """Кончик маркера в координатах листка и подъём руки."""
    a0 = SLOTS[0][0]
    if t < a0:
        u = ease_out(clamp((t - 22.2) / (a0 - 22.2)), 2.0)
        sx, sy = PX1 + 60, BASES[0] + 150
        ex, ey = tip_at(0, 0)[:2]
        return sx + (ex - sx) * u, sy + (ey - sy) * u - 40 * math.sin(math.pi * u), 1.0 + 0.08 * (1 - u)
    for li, (a, b) in enumerate(SLOTS):
        if a <= t <= b:
            x, y, _, lift = tip_at(li, progress(li, t))
            return x, y, 1.0 + 0.03 * lift
        if li + 1 < len(SLOTS) and b < t < SLOTS[li + 1][0]:
            u = ease_io((t - b) / (SLOTS[li + 1][0] - b))
            sx, sy = tip_at(li, 1.0)[:2]
            ex, ey = tip_at(li + 1, 0.0)[:2]
            return sx + (ex - sx) * u, sy + (ey - sy) * u - 30 * math.sin(math.pi * u), 1.0 + 0.06 * math.sin(math.pi * u)
    e = t - SLOTS[-1][1]
    u = ease_out(clamp(e / 0.25), 2)
    sx, sy = tip_at(2, 1.0)[:2]
    return sx + 40 * u, sy - 14 * u, 1.0 + 0.05 * u


def check_mark(t):
    e = t - CHECK
    if e < 0:
        return ""
    k = ease_out(clamp(e / 0.2), 2)
    x0 = L[3]["x1"] + 8
    y0 = BASES[3]
    chk = [(x0, y0 - 22), (x0 + 14, y0 - 4), (x0 + 44, y0 - 50)]
    n = 1 + k * 1.999
    i = int(n)
    pts = chk[:i] + ([tuple(chk[i - 1][j] + (chk[min(i, 2)][j] - chk[i - 1][j]) * (n - i) for j in (0, 1))] if i < 3 else [])
    s = [line(pts, 9, "#2e9e4f", taper=.15, wmin=.6, seed=880)]
    # искорки вокруг галочки
    if e < 0.6:
        a = 1 - e / 0.6
        for j in range(5):
            ang = math.radians(-150 + j * 40)
            r0 = 34 + 40 * ease_out(e / 0.6)
            cx, cy = x0 + 22, y0 - 26
            s.append(line([(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0), (cx + math.cos(ang) * (r0 + 16 * a), cy + math.sin(ang) * (r0 + 16 * a))],
                          5 * a + 1, "#2e9e4f", taper=.6, seed=890 + j))
    return "".join(s)


# ─────────────────────────────── листок и магнит
def paper(t, lines, rot, check=False, flap=0.0):
    """Листок в мировых координатах: висит на магните MAG, повёрнут на rot. lines — сколько строк видно (0..4),
    при 1..3 строки пишутся по времени t. flap — подлёт углом (крен по вертикали)."""
    mx, my = MAG
    s = []
    pts = [(PX0, PY0 + 6, 1), (PX1, PY0, 1), (PX1 + 2, PY1 - 30), (PX1 - 26, PY1 + 2, 1), (PX0 - 2, PY1 - 4, 1)]
    inner = blob([(PX0, PY0), (PX1, PY0), (PX1, PY0 + 18), (PX0, PY0 + 22)], "#ffffff", .9)
    inner += blob([(PX1 - 40, PY0), (PX1, PY0), (PX1, PY1), (PX1 - 30, PY1)], "#e7e6e1", .9)
    for k in range(4):
        y = BASES[k] + 10
        inner += line([(PX0 + 16, y), (PX1 - 16, y - 1)], 2, "#d6dbe6", taper=.05, wmin=.9, seed=850 + k)
    body = []
    body.append(blob([(p[0] + 7, p[1] + 9) + tuple(p[2:]) for p in pts], "#4a3a22", .2, blur(3)))
    body.append(shape(pts, "#fbfaf6", inner, w=4.2, seed=860))
    # загнутый уголок
    body.append(shape([(PX1 + 2, PY1 - 30, 1), (PX1 - 26, PY1 + 2, 1), (PX1 - 22, PY1 - 26, 1)], "#dedcd5", "", w=3, seed=861))
    if lines > 0 or check:
        txt = ""
        for li in range(min(lines, 4)):
            txt += text_line(li, t, done=(lines >= 4 or li < lines - 1 and False))
        body.append(txt)
    if check:
        body.append(check_mark(t))
    g = "".join(body)
    if flap:
        g = f'<g transform="translate({mx} {my}) scale(1 {1 - 0.25 * flap:.4f}) skewX({10 * flap:.2f}) translate({-mx} {-my})">{g}</g>'
    s.append(f'<g transform="rotate({rot:.3f} {mx} {my})">{g}</g>')
    return "".join(s)


def magnet(t, sc=0.33, wig=0.0):
    mx, my = MAG
    return (blob(ellipse_pts(mx + 6, my + 10, 40, 16, 12), "#4a3a22", .25, blur(5)) +
            fishy.fish(mx, my, sc, -6 + wig, False, 8 * math.sin(t * 1.3) + wig * 2, (0.3, 0.2), w=3.4, sd=900, mouth="smile"))


# ─────────────────────────────── кухня
def kitchen():
    s = []
    wall = "#f1e2c4"
    s.append(f'<rect x="-1500" y="-1500" width="5000" height="{FLOOR + 1500}" fill="{wall}"/>')
    DEFS.append('<pattern id="pTile31" width="104" height="78" patternUnits="userSpaceOnUse">'
                '<rect width="104" height="78" fill="#fbf1dc"/><rect x="0" y="74" width="104" height="4" fill="#dcc79f"/>'
                '<rect x="100" width="4" height="78" fill="#dcc79f"/></pattern>')
    s.append(f'<rect x="720" y="760" width="2800" height="{CTOP - 760}" fill="url(#pTile31)"/>')
    s.append(line([(720, 760), (3500, 760)], 4, INK, taper=.05, wmin=.9, seed=900))
    # дверной проём слева (тёмный коридор) и наличник
    s.append(shape(rect_pts(-700, 120, 120, FLOOR + 20), "#8d7a63", blob(rect_pts(-700, 120, 120, 300), "#776650", .9), w=5, seed=901))
    s.append(shape(rect_pts(120, 100, 170, FLOOR + 20), "#f6eedd", blob(rect_pts(150, 100, 170, FLOOR + 20), "#dcd0b6", .9), w=4.4, seed=902))
    # окно: день, облака плывут (в frame), рама
    s.append(shape(rect_pts(890, 290, 1350, 770, 10), "#f6f1e6", "", w=5, seed=903))
    # полка с банками над тумбой справа от окна
    s.append(shape(rect_pts(1400, 520, 2100, 548, 4), "#b98a5a", "", w=4.4, seed=911))
    for k, (x, hgt, col) in enumerate([(1470, 110, "#e9c46a"), (1580, 84, "#9fc5a8"), (1690, 130, "#e07a5f"), (1810, 96, "#8ab6d6")]):
        s.append(shape(rect_pts(x - 40, 520 - hgt, x + 40, 520, 14), col, blob(rect_pts(x - 40, 520 - hgt, x + 40, 520 - hgt + 22), "#c9c0b0"),
                       w=4, seed=912 + k))
    # тумба
    s.append(shape(rect_pts(720, CTOP, 3500, CTOP + 44, 4), "#c98f5a", blob(rect_pts(720, CTOP + 26, 3500, CTOP + 44), "#a8723f", .9),
                   w=4.6, seed=920))
    front = "#e9dcc4"
    inner = "".join(line([(x, CTOP + 50), (x, FLOOR - 40)], 4, mix(front, "#000000", .3), taper=.05, wmin=.9, seed=921 + k)
                    for k, x in enumerate(range(1180, 3500, 440)))
    inner += "".join(shape(rect_pts(x - 120, CTOP + 110, x - 60, CTOP + 128, 8), "#b8b0a2", "", w=3, seed=930 + k)
                     for k, x in enumerate(range(1180, 3500, 440)))
    inner += blob(rect_pts(720, FLOOR - 44, 3500, FLOOR), "#b9a98d", .9)
    s.append(shape(rect_pts(740, CTOP + 44, 3500, FLOOR), front, inner, w=5, seed=940))
    # растение в горшке и хлебница на столешнице
    s.append(shape([(980, CTOP, 1), (1060, CTOP, 1), (1074, CTOP - 90, 1), (966, CTOP - 90, 1)], "#c4673f",
                   blob([(1030, CTOP), (1060, CTOP), (1074, CTOP - 90), (1040, CTOP - 90)], "#a4512e", .9), w=4, seed=941))
    s.append(shape(rect_pts(1600, CTOP - 150, 1880, CTOP, 40), "#c48a52", blob(rect_pts(1600, CTOP - 150, 1880, CTOP - 120, 20), "#d9a46a", .9) +
                   blob(rect_pts(1600, CTOP - 40, 1880, CTOP), "#a06c3a", .9), w=4.6, seed=943))
    s.append(line([(1640, CTOP - 92), (1840, CTOP - 92)], 4, "#7a4f28", seed=944))
    # пол: линолеум клеткой
    DEFS.append('<pattern id="pFloor31" width="140" height="140" patternUnits="userSpaceOnUse">'
                '<rect width="140" height="140" fill="#d8c3a0"/><rect width="70" height="70" fill="#cdb48d"/>'
                '<rect x="70" y="70" width="70" height="70" fill="#cdb48d"/></pattern>')
    s.append(f'<rect x="-1500" y="{FLOOR}" width="5000" height="1400" fill="url(#pFloor31)"/>')
    s.append(line([(-1500, FLOOR), (3500, FLOOR)], 5, INK, taper=.05, wmin=.9, seed=950))
    return "".join(s)


def window(t):
    x0, y0, x1, y1 = 912, 312, 1328, 748
    sky = lin_grad([(0, "#8fd0f5", 1), (1, "#e2f4ff", 1)], 0, 0, 0, 1)
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    inner = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{sky})"/>']
    inner.append(blob(ellipse_pts(1010, 400, 46, 46, 16), "#fff4c6"))
    for k, (cx, cy, r) in enumerate([(1100, 450, 70), (1290, 380, 56)]):
        dx = ((t * 14 + k * 260) % 560) - 140
        p = [(cx + dx - r, cy + 20), (cx + dx - r * .6, cy - 20), (cx + dx - r * .1, cy - 40), (cx + dx + r * .5, cy - 26), (cx + dx + r, cy + 20)]
        inner.append(shape(p, "#ffffff", "", w=3, seed=960 + k))
    # дома напротив
    inner.append(blob([(x0, 640), (1000, 640), (1000, 590), (1150, 590), (1150, 660), (x1, 640), (x1, y1), (x0, y1)], "#c9a37a"))
    for k, (x, y) in enumerate([(1030, 610), (1080, 610), (1180, 680), (1250, 670)]):
        inner.append(blob(rect_pts(x, y, x + 24, y + 30), "#f6eedd"))
    s = [f'<g clip-path="url(#{c})">{"".join(inner)}</g>']
    s.append(shape(rect_pts(1110, 312, 1130, 748), "#f6f1e6", "", w=3.4, seed=965))
    s.append(shape(rect_pts(912, 520, 1328, 540), "#f6f1e6", "", w=3.4, seed=966))
    s.append(shape(rect_pts(870, 760, 1370, 790, 5), "#f6f1e6", "", w=4.4, seed=967))
    return "".join(s)


def kettle(t):
    x, y = 1350, CTOP
    s = [blob(ellipse_pts(x + 8, y + 2, 120, 14, 14), "#4a3a22", .3, blur(5))]
    body = [(x - 100, y), (x - 112, y - 70), (x - 90, y - 140), (x - 40, y - 170), (x + 40, y - 170), (x + 90, y - 140), (x + 112, y - 70), (x + 100, y)]
    inner = blob([(x + 40, y - 170), (x + 112, y - 70), (x + 100, y), (x + 50, y)], "#3f7f8f", .9)
    inner += blob([(x - 80, y - 130), (x - 60, y - 150), (x - 50, y - 60), (x - 76, y - 50)], "#a8e0e8", .9)
    s.append(shape([(x + 96, y - 110), (x + 170, y - 160, 1), (x + 186, y - 150, 1), (x + 108, y - 60)], "#5aa5b5", "", w=4, seed=970))
    s.append(shape(body, "#5aa5b5", inner, w=5, seed=971))
    s.append(f'<path d="M{x - 70} {y - 165} Q{x} {y - 270} {x + 70} {y - 165}" fill="none" stroke="{INK}" stroke-width="12" stroke-linecap="round"/>')
    s.append(f'<path d="M{x - 70} {y - 165} Q{x} {y - 270} {x + 70} {y - 165}" fill="none" stroke="#2b2730" stroke-width="6" stroke-linecap="round"/>')
    s.append(shape(ellipse_pts(x, y - 172, 46, 12, 14), "#4c95a6", "", w=3.6, seed=972))
    # пар: три завитка поднимаются от носика
    for k in range(3):
        ph = (t * 0.7 + k / 3) % 1.0
        a = math.sin(math.pi * ph)
        bx, by = x + 182, y - 170 - ph * 150
        pts = [(bx + 14 * math.sin(t * 3 + k + j * 0.9), by - j * 22) for j in range(5)]
        s.append(line(pts, 9 * a + 1, "#ffffff", taper=.7, wmin=.2, seed=975 + k))
    return "".join(s)


def fridge():
    s = []
    x0, x1, y0, y1 = FX0, FX1, FTOP, FLOOR - 40
    s.append(blob(rect_pts(x0 + 20, FLOOR - 20, x1 + 40, FLOOR + 14), "#1a0e05", .35, blur(10)))
    pts = [(x0 + 8, y1, 1), (x0, y0 + 130), (x0 + 30, y0 + 32), (x0 + 120, y0), (x1 - 120, y0), (x1 - 30, y0 + 32), (x1, y0 + 130), (x1 - 8, y1, 1)]
    inner = blob([(x1 - 80, y0), (x1 + 10, y0), (x1 + 10, y1), (x1 - 70, y1)], "#d9d3c4", .95)
    inner += blob([(x0, y0 + 60), (x0 + 50, y0 + 30), (x0 + 60, y1), (x0, y1)], "#fffdf6", .9)
    inner += blob([(x0, y0), (x1, y0), (x1, y0 + 40), (x0, y0 + 60)], "#fffdf6", .8)
    s.append(shape(pts, "#f2eee4", inner, w=5.6, seed=980))
    # шов дверцы морозилки и эмблема-полоска (без букв)
    s.append(line([(x0 + 14, 620), (x1 - 14, 620)], 4, mix("#f2eee4", "#000000", .35), taper=.05, wmin=.9, seed=981))
    s.append(shape(rect_pts(400, 400, 570, 426, 12), "#c9ced8", blob(rect_pts(400, 414, 570, 426), "#9aa0ab"), w=3.4, seed=982))
    # ручка-рычаг справа
    s.append(shape(rect_pts(668, 760, 698, 960, 14), "#c9ced8", blob(rect_pts(684, 760, 698, 960), "#9aa0ab") +
                   line([(676, 780), (676, 930)], 4, "#ffffff", seed=984, op=.9), w=4.2, seed=983))
    s.append(shape(rect_pts(660, 600, 700, 640, 8), "#c9ced8", "", w=3.4, seed=985))
    # цоколь с решёткой и ножки
    s.append(shape(rect_pts(x0 + 20, y1, x1 - 20, FLOOR - 6, 6), "#5e5a54",
                   "".join(line([(x, y1 + 8), (x, FLOOR - 14)], 3, "#3a3732", taper=.05, wmin=.9, seed=986 + k)
                           for k, x in enumerate(range(x0 + 50, x1 - 30, 28))), w=4, seed=987))
    # другие магниты и фото кота
    s.append(shape(ellipse_pts(650, 520, 22, 22, 14), "#e5383b", blob(ellipse_pts(644, 514, 8, 8, 8), "#ff8a80"), w=3.4, seed=990))
    s.append(shape(rect_pts(318, 1190, 470, 1360, 4), "#fbfaf6", blob(rect_pts(334, 1206, 454, 1316), "#a9d6e6") +
                   cat_photo(394, 1316), w=3.6, seed=991, attrs='transform="rotate(4 394 1270)"'))
    s.append(shape(ellipse_pts(394, 1196, 16, 16, 12), "#3a6fc0", blob(ellipse_pts(390, 1192, 6, 6, 8), "#8fb3ee"), w=3, seed=992))
    s.append(shape([(560, 1260, 1), (600, 1240, 1), (640, 1262, 1), (626, 1306, 1), (576, 1306, 1)], "#e9c46a", "", w=3.4, seed=993))
    return "".join(s)


def cat_photo(cx, by):
    """Маленькое фото: силуэт сидящего кота с зелёными глазами."""
    s = [blob([(cx - 34, by), (cx - 30, by - 50), (cx - 24, by - 74), (cx - 30, by - 98), (cx - 14, by - 86), (cx + 14, by - 86),
               (cx + 30, by - 100), (cx + 24, by - 72), (cx + 30, by - 50), (cx + 34, by)], "#2b2733")]
    s.append(blob(ellipse_pts(cx - 10, by - 70, 6, 7, 8), "#a9d84a"))
    s.append(blob(ellipse_pts(cx + 10, by - 70, 6, 7, 8), "#a9d84a"))
    s.append(blob(ellipse_pts(cx + 44, by - 60, 6, 9, 8), "#ff8a2a"))
    return "".join(s)


def light():
    g = rad_grad([(0, "#fff6d8", .5), (.6, "#fff0c0", .15), (1, "#fff0c0", 0)], 1120, 520, 1300, 1300)
    s = [f'<rect x="-1500" y="-1500" width="5000" height="4500" fill="url(#{g})" style="mix-blend-mode:screen"/>']
    g2 = rad_grad([(0, "#000000", 0), (.6, "#000000", 0), (1, "#2a1606", .3)], 800, 900, 1500, 1500)
    s.append(f'<rect x="-1500" y="-1500" width="5000" height="4500" fill="url(#{g2})"/>')
    return "".join(s)


def scene_bg(t):
    return _ST["kit"] + window(t) + kettle(t) + _ST["fridge"]


# ─────────────────────────────── рука, шлёпающая листок (тыл кисти к зрителю, пальцы вверх)
def flat_hand(x, y, sc, rot):
    """Ладонь прижата к дверце: тыл кисти к зрителю, пальцы вверх, большой палец слева, рукав уходит вниз-вправо.
    (x, y) — середина костяшек."""
    s = []

    def P(pts):
        return T(pts, x, y, sc, rot)
    sl = [(-118, 150, 1), (108, 140, 1), (420, 1300, 1), (-60, 1360, 1)]
    s.append(shape(P(sl), HOOD, blob(P([(40, 150), (108, 140), (420, 1300), (180, 1330)]), HOOD_SH, .9) +
                   line(P([(-40, 280), (30, 600), (60, 900)]), 4, FOLD, seed=1010, op=.7) +
                   line(P([(60, 320), (150, 560)]), 3.4, FOLD, seed=1013, op=.6), w=5.2, seed=1011))
    s.append(shape(P([(-126, 116, 1), (114, 106, 1), (122, 176, 1), (-120, 186, 1)]), HOOD_SH,
                   "".join(line(P([(-100 + k * 40, 122), (-100 + k * 40, 180)]), 2.6, FOLD, seed=1020 + k, op=.8) for k in range(6)),
                   w=4.6, seed=1012))
    th = sausage(P([(-80, 60), (-122, 20), (-150, -24)]), 50 * sc, 42 * sc)
    s.append(shape(th, SKIN, "", w=4.4, seed=1030))
    s.append(shape(ellipse_pts(*P([(-146, -14)])[0], 12 * sc, 10 * sc, 10, rot=rot - 40), NAIL, "", w=2, seed=1031))
    fingers = [(-62, 150, 42), (-20, 168, 44), (22, 160, 42), (60, 126, 36)]
    for k, (fx, L_, w_) in enumerate(fingers):
        tip = (fx + (k - 1.5) * 7, -L_)
        sp = sausage(P([(fx, 20), (fx + (k - 1.5) * 3.5, -L_ * 0.5), tip]), w_ * sc, w_ * 0.9 * sc)
        inner = line(P([(fx - w_ * .3, -L_ * 0.45), (fx + w_ * .3, -L_ * 0.45)]), 2.4, SKIN_SH2, seed=1040 + k, op=.8)
        s.append(shape(sp, SKIN, inner, w=4.2, seed=1060 + k))
        nx, ny = P([(tip[0], tip[1] + w_ * 0.45)])[0]
        s.append(shape(ellipse_pts(nx, ny, w_ * 0.3 * sc, w_ * 0.34 * sc, 10, rot=rot), NAIL, "", w=2, seed=1070 + k))
    back = [(-92, 6), (-40, -6), (20, -8), (86, 2), (100, 50), (88, 130), (0, 140), (-90, 136), (-104, 64)]
    inner = blob(P([(40, 0), (96, 56), (90, 130), (30, 136)]), SKIN_SH, .9)
    for k in range(4):
        fx = fingers[k][0]
        inner += line(P([(fx - 10, 6), (fx, -2), (fx + 10, 6)]), 2.6, SKIN_SH2, seed=1080 + k, op=.8)
    inner += line(P([(-30, 40), (-20, 110)]), 2.4, SKIN_SH2, seed=1090, op=.6)
    inner += line(P([(20, 40), (14, 110)]), 2.4, SKIN_SH2, seed=1091, op=.6)
    s.append(shape(P(back), SKIN, inner, w=5, seed=1092))
    return "".join(s)


# ─────────────────────────────── s13
def swing_rot(t):
    if t < SLAP:
        return PROT
    a = 0.0
    e = t - (SWING - 0.12)
    if e > 0:
        a = 7 * math.exp(-e * 3.2) * math.sin(e * 9)
    return PROT + a


def frame13(t):
    s = [scene_bg(t)]
    mx, my = MAG
    e = t - SLAP
    if e < 0:
        # рука с листком летит из-за кадра справа-снизу (ближе к камере — крупнее) и шлёпает на дверцу
        u = clamp((t - 20.3) / (SLAP - 20.3))
        k = ease_in(u, 1.6)
        p0, p1 = np.array([1250.0, 1700.0]), np.array([mx + 6.0, my + 150.0])
        q = p0 + (p1 - p0) * k
        q[1] -= 120 * math.sin(math.pi * k) * (1 - k)
        sc = 1.0 + 0.55 * (1 - k)
        rot = 22 * (1 - k) + 3 * math.sin(t * 9) * (1 - k)
        flap = 0.4 * (1 - k) * (0.6 + 0.4 * math.sin(t * 17))
        dx, dy = q[0] - (mx + 6), q[1] - (my + 150)
        ps = f'<g transform="translate({f(dx)} {f(dy)}) rotate({f(rot)} {mx} {my + 150}) translate({mx} {my + 150}) scale({sc:.4f}) translate({-mx} {-my - 150})">'
        s.append(ps + paper(t, 0, PROT, flap=flap) + "</g>")
        s.append(flat_hand(q[0], q[1] - 40 * sc, 0.92 * sc, rot - 4))
        if t > 20.6:
            s.append(_ST["light"])
            return "".join(s)
    else:
        rot = swing_rot(t)
        s.append(paper(t, 0, rot))
        s.append(magnet(t, wig=(rot - PROT) * 1.2))
        # рука прижата, потом уходит к зрителю (вниз-вправо, крупнее)
        if e < 0.75:
            k = ease_in(clamp((e - 0.12) / 0.55), 2)
            s.append(flat_hand(mx + 6 + 520 * k, my + 110 + 900 * k, 0.92 * (1 + 0.5 * k), -4 + 14 * k))
        if e < 0.32:
            a = 1 - e / 0.32
            for k in range(8):
                ang = math.radians(-180 + k * 45 + 10)
                r0 = 230 + 70 * ease_out(e / .32)
                cx, cy = (PX0 + PX1) / 2, (PY0 + PY1) / 2
                s.append(line([(cx + math.cos(ang) * r0 * .8, cy + math.sin(ang) * r0), (cx + math.cos(ang) * (r0 * .8 + 50 * a),
                                                                                         cy + math.sin(ang) * (r0 + 50 * a))],
                              9 * a + 1, INK, taper=.6, seed=1100 + k))
    s.append(_ST["light"])
    return "".join(s)


def cam13(t):
    u = clamp((t - 20.1) / 2.5)
    k = 0.3 * u + 0.7 * ease_io(u)
    cx = 860 + (480 - 860) * k
    cy = 1080 + (910 - 1080) * k
    sc = 0.78 + (1.42 - 0.78) * k
    rot = 1.5 - 2.0 * u
    e = t - SLAP
    if e >= 0:
        kk = math.exp(-e * 9)
        cy += 7 * kk * math.sin(e * 52)
        sc *= 1 + 0.035 * kk
    return cam(cx, cy, sc, rot)


# ─────────────────────────────── s14
def frame14(t):
    s = [scene_bg(t)]
    s.append(paper(t, 3, PROT))
    s.append(magnet(t))
    x, y, lft = pen_tip(t)
    # кончик в мир: листок повёрнут на PROT вокруг магнита
    mx, my = MAG
    a = math.radians(PROT)
    wx = mx + (x - mx) * math.cos(a) - (y - my) * math.sin(a)
    wy = my + (x - mx) * math.sin(a) + (y - my) * math.cos(a)
    ang = -36 + 3 * math.sin(t * 2.3) - 4 * (lft - 1)
    hs = 0.5
    s.append(f'<g transform="translate({f(wx + 12 * lft)} {f(wy + 16 * lft)}) scale({f(hs * 1.02)})" opacity=".22" {blur(6)}>'
             f'{hand.hand(ang, 7, tool="marker")}</g>')
    s.append(f'<g transform="translate({f(wx)} {f(wy)}) scale({f(hs * lft)})">{hand.hand(ang, 7, tool="marker")}</g>')
    s.append(_ST["light"])
    return "".join(s)


def cam14(t):
    u = clamp((t - 22.2) / 2.75)
    cx = 478 + 22 * ease_io(u)
    cy = 900 + 14 * ease_io(u)
    sc = 2.6 + 0.1 * u
    rot = -1.0 + 1.2 * u
    for t0 in (SLOTS[1][0], SLOTS[2][0]):
        e = t - t0
        if e > 0:
            sc *= 1 + 0.01 * math.exp(-e * 6) * math.sin(min(e * 10, math.pi))
    return cam(cx, cy, sc, rot)


# ─────────────────────────────── s16 / s17: кот
CATS = 1.32


def cat_pose(t, sid="s16"):
    """Поза кота по времени (s16 → s17)."""
    d = dict(up=0.0, look=(0.0, 0.0), blink=0.0, tilt=0.0, flick=0.0, paw_l=None, paw_r=None, press=0.0, lift_l=0.0, lift_r=0.0,
             happy=0.0, bob=0.0)
    x = CATX
    tail = 5 * math.sin(t * 1.9) + 2.5 * math.sin(t * 3.3 + 1)
    W0, W1 = 26.55, 27.28                # подходит вразвалку
    if sid == "s16":
        # ходьба
        u = clamp((t - W0) / (W1 - W0))
        x = 1180 + (CATX - 1180) * (0.2 * u + 0.8 * ease_out(u, 1.6))
        if t < W1:
            ph = (t - W0) * 2 * math.pi * 2.4
            d["lift_l"] = max(0.0, math.sin(ph))
            d["lift_r"] = max(0.0, -math.sin(ph))
            d["bob"] = -10 * abs(math.sin(ph))
            d["up"] = 0.22
            d["paw_l"] = (811 - 4, 1298 - 22 * max(0.0, -math.sin(ph)))
            d["paw_r"] = (861 + 4, 1298 - 22 * max(0.0, math.sin(ph)))
            tail += 9 * math.sin(ph)
        d["look"] = (-0.8, 0.1)
        d["tilt"] = -3
        # встаёт на задние лапы и тянется к листку
        R0, R1 = 27.32, 27.62
        up = smooth(R0, R1, t)
        if t >= W1:
            d["up"] = 0.22 + 0.78 * up
        tgt = cat.to_int((PX1 - 46, PY1 - 26), x, FLOOR, CATS)
        rest_l = (811, 1298)
        k = ease_io(clamp((t - R0) / (REACH - R0)))
        if t >= R0:
            px = rest_l[0] + (tgt[0] - rest_l[0]) * k
            py = rest_l[1] + (tgt[1] - rest_l[1]) * k - 30 * math.sin(math.pi * k)
            if t >= REACH:
                e = t - REACH
                d["press"] = math.exp(-e * 10) * abs(math.sin(e * 30))
                # похлопывает по листку ещё раз на «проверить» и на «ужин»
                for c in (28.1, CHECK - 0.12):
                    v = (t - c) / 0.3
                    if 0 < v < 1:
                        px += 10 * math.sin(math.pi * v)
                        py += 14 * math.sin(math.pi * v)
            d["paw_l"] = (px, py)
            d["paw_r"] = (876 + 10 * up, 1298 - (1298 - 1074) * up)
        lk = smooth(R0 - 0.1, R0 + 0.2, t)
        d["look"] = (-0.8 * (1 - lk) - 0.75 * lk, 0.1 * (1 - lk) - 0.85 * lk)
        d["tilt"] = -3 * (1 - lk) - 7 * lk + 2 * math.sin((t - R0) * 2) * lk
        if t >= CHECK + 0.1:
            d["happy"] = 1.0
            d["tilt"] = -4 + 3 * math.sin((t - CHECK) * 4)
        for c in (28.5,):
            e = t - c
            if 0 <= e < 0.5:
                d["flick"] = -14 * math.exp(-e * 9) * math.sin(e * 34)
        for c, half in ((27.02, 0.07),):
            if c - half <= t <= c + half:
                d["blink"] = 1 - abs(t - c) / half
    else:
        # s17: сидит у холодильника, смотрит в камеру, медленно моргает
        x = CATX + 40
        d["look"] = (-0.04, 0.0)
        d["tilt"] = 2.2 * math.sin((t - 29.4) * 0.9) + 1.0
        for c, half, hold in ((30.42, 0.4, 0.3), (31.95, 0.36, 0.22)):
            a = c - half
            if a <= t <= c + hold + half:
                if t < c:
                    d["blink"] = ease_io((t - a) / half)
                elif t < c + hold:
                    d["blink"] = 1.0
                else:
                    d["blink"] = 1 - ease_io((t - c - hold) / half)
        for c in (29.95, 31.3):
            e = t - c
            if 0 <= e < 0.5:
                d["flick"] = -14 * math.exp(-e * 9) * math.sin(e * 34)
    d["tail"] = tail
    return x, d


def frame_cat(sid, t):
    s = [scene_bg(t)]
    show_check = t >= CHECK
    s.append(paper(t, 4, PROT if sid == "s16" else PROT, check=show_check))
    s.append(magnet(t))
    x, d = cat_pose(t, sid)
    s.append(_ST["light"])
    fx, fy = cat2.flame_world(x, FLOOR, CATS, d["tail"], d["up"], d["bob"])
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    g = rad_grad([(0, "#ffb050", .3 * fl), (1, "#ffb050", 0)], fx, fy, 280, 280)
    s.append(f'<rect x="{f(fx - 300)}" y="{f(fy - 300)}" width="600" height="600" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    s.append(cat2.draw(x, FLOOR, CATS, t, **d))
    return "".join(s)


def cam_cat(sid, t):
    if sid == "s16":
        u = clamp((t - 26.65) / 3.1)
        cx = 760 - 70 * ease_io(u)
        cy = 1210 - 30 * ease_io(u)
        sc = 1.12 + 0.12 * (0.3 * u + 0.7 * ease_io(u))
        rot = 1.0 - 1.6 * u
        for t0, amp in ((REACH, .03), (CHECK, .035)):
            e = t - t0
            if e > 0:
                kk = math.exp(-e * 8)
                sc *= 1 + amp * kk * math.sin(min(e * 12, math.pi))
                cy += 4 * kk * math.sin(e * 45)
    else:
        u = clamp((t - 29.35) / (32.7 - 29.35))
        hc = cat.to_world((836, 1090), CATX + 40, FLOOR, CATS)
        cx = hc[0] + 50 + 10 * u
        cy = hc[1] + 70 - 15 * u
        sc = 2.3 + 0.22 * (0.4 * u + 0.6 * ease_io(u))
        rot = -0.8 + 1.4 * u
    return cam(cx, cy, sc, rot)


def frame(sid, t):
    if not _ST:
        _ST["kit"] = kitchen()
        _ST["fridge"] = fridge()
        _ST["light"] = light()
        cat.static_parts()
        lib.static_done()
    lib.dyn_begin()
    if sid == "s13":
        art, cm = frame13(t), cam13(t)
    elif sid == "s14":
        art, cm = frame14(t), cam14(t)
    else:
        art, cm = frame_cat(sid, t), cam_cat(sid, t)
    return svg(f'<rect width="{W}" height="{H}" fill="#f1e2c4"/><g transform="{cm}">{art}</g>')
