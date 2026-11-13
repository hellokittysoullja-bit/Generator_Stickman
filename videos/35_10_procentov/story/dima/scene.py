"""Сцена dima рилса 35: планы s05, s06, s16 (комната Димы за ноутбуком: ночь, крупно, день) и s14 (кухня, каша).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Удары — на словах по voice/words.json.

Основа — сцена desk рилса 32 (den.py — комната, people.py — Дима сидит слева лицом вправо, таз (230, 1262)), кухня —
kitchen.py (кухня рилса 29) отодвинута вглубь. Своё: ноутбук с экраном (контент в плоскости экрана, аффинно),
кнопки «КУПИТЬ»/«ВЕРНУТЬ», шкала «90 %» с замком, кошелёк и монетки, обруч с проводами и лампочкой, коробка, каша.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import den  # noqa: E402
import kitchen  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import room  # noqa: E402
from lib import INK, T, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, mix, rect_pts, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["word"].strip(".,?!").lower() == word and w["start"] >= after:
            return w["start"]
    raise KeyError(word)


T_KUPIL = wt("купил")              # 7.60
T_KURS = wt("курс", 7)             # 7.92
T_DEVYANOSTO = wt("девяносто")    # 9.24
T_POEST = wt("поесть")             # 24.72
T_GOLOVA = wt("голова", 24)        # 25.24
T_VERNUL = wt("вернул")            # 27.76
T_DENGI = wt("деньги")             # 28.12

BS = 0.6
HIP = np.array([230.0, 1262.0])
FONT = 'font-family="IDB" font-weight="900"'


# ═════════════════════════ время и движение ═════════════════════════
def osc(t, f, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


def punch(t, t0, amp=.08, up=.06, down=.35):
    """Удар камерой: +amp за up с, возврат за down с."""
    if t < t0:
        return 0.0
    if t < t0 + up:
        return amp * ease_out((t - t0) / up, 2)
    return amp * (1 - ease_io(clamp((t - t0 - up) / down)))


def whip_in(t, t0, dur=0.22):
    return 1 - ease_out(clamp((t - t0) / dur), 3)


def sweat(x, y, k, u, seed=3001):
    """Капля пота: u 0..1 — набухает и стекает."""
    if u <= 0:
        return ""
    yy = y + 70 * k * ease_in(u)
    r = 15 * k * min(1, u * 3)
    drop = [(x, yy - r * 2.2), (x + r, yy - r * .1), (x + r * .8, yy + r * .7), (x, yy + r), (x - r * .8, yy + r * .7), (x - r, yy - r * .1)]
    return shape(drop, "#bfe6fa", blob([(x - r * .4, yy - r * .6), (x - r * .1, yy - r * .9), (x - r * .1, yy - r * .2)], "#ffffff"), w=3, seed=seed)


def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([v[0] * c - v[1] * s, v[0] * s + v[1] * c])


# ═════════════════════════ Дима ═════════════════════════
def dima(t, arms, hands=None, expr=None, hip=None, lean=0.12, head_ang=0.0, feet=None):
    hip = HIP if hip is None else np.array(hip, float)
    if feet is None:
        feet = {"n": ((450, 1468), 0.0), "f": ((425, 1462), 0.0)}
    p = dict(hip=tuple(hip), scale=BS, lean=lean, feet=feet, arms=arms, hands=hands or {}, expr=expr or {}, head_ang=head_ang,
             hood=0.0, strings=(2 * osc(t, 1.3), 1.5 * osc(t, 1.1, 1)))
    d = people.draw(p, "dima")
    d["hang"] = lean * .5 + head_ang
    return d


def head_tf(d):
    """transform головы (единицы головы → мир)."""
    hx, hy = d["head"]
    return f"translate({hx:.2f} {hy:.2f}) scale({BS}) rotate({math.degrees(d['hang']):.3f})"


def head_pt(d, local):
    return d["head"] + rot(np.array(local, float), d["hang"]) * BS


FIST = dict(kind="open", curl=(.85, .9, .92, .95), spread=.02, thumb=.85, bend=.05)
POINT = dict(kind="open", curl=(0.0, .9, .95, .95), spread=.02, thumb=.85, bend=.03)
REST = dict(kind="open", curl=(.25, .3, .35, .4), spread=.08, thumb=.35, bend=.1)


def hnd(base, d, **kw):
    h = dict(base)
    h["dir"] = d
    h.update(kw)
    return h


# ═════════════════════════ ноутбук ═════════════════════════
class Laptop:
    """Ноутбук на столе, экран повёрнут к Диме и к зрителю. (x, y) — левый низ экрана (петля), k — масштаб.
    Экран — параллелограмм; контент рисуется в его плоскости в своих координатах 0..SW × 0..SH."""
    SW, SH = 300.0, 220.0

    def __init__(self, x, y, k=1.0):
        self.x, self.y, self.k = x, y, k
        W, H = 300 * k, 232 * k
        self.BL = np.array([x, y])
        self.BR = np.array([x + W, y - 16 * k])
        self.TL = np.array([x + 14 * k, y - H])
        self.TR = np.array([x + W + 14 * k, y - 16 * k - H])
        dk = np.array([-78 * k, 40 * k])          # передний край клавиатуры
        self.FL, self.FR = self.BL + dk, self.BR + dk
        # внутренний экран (рамка 12k)
        u = (self.TR - self.TL) / np.linalg.norm(self.TR - self.TL)
        v = (self.BL - self.TL) / np.linalg.norm(self.BL - self.TL)
        o = self.TL + u * 12 * k + v * 12 * k
        uu = (self.TR - self.TL - u * 24 * k) / self.SW
        vv = (self.BL - self.TL - v * 30 * k) / self.SH
        self.M = (uu, vv, o)

    def P(self, a, b):
        """Точка экрана (a, b) в мир."""
        uu, vv, o = self.M
        return o + uu * a + vv * b

    def key(self, fa, fb):
        """Точка клавиатуры: fa 0..1 вдоль, fb 0..1 от петли к переднему краю."""
        a = self.BL + (self.BR - self.BL) * fa
        return a + (self.FL - self.BL) * fb

    def screen_tf(self):
        uu, vv, o = self.M
        return f"matrix({uu[0]:.5f} {uu[1]:.5f} {vv[0]:.5f} {vv[1]:.5f} {o[0]:.3f} {o[1]:.3f})"

    def draw(self, content, bg=("#1b2a55", "#2f4f8f"), press=None):
        k = self.k
        o = []
        # тень на столе
        o.append(blob([tuple(self.FL + (0, 6 * k)), tuple(self.FR + (14 * k, 6 * k)), tuple(self.BR + (30 * k, 4 * k)), tuple(self.BL + (10 * k, 4 * k))],
                      "#1a100a", .3, lib.blur(5)))
        # крышка
        lid = [tuple(self.BL) + (1,), tuple(self.TL) + (1,), tuple(self.TR) + (1,), tuple(self.BR) + (1,)]
        o.append(shape(lid, "#30343f", blob([tuple(self.TR), tuple(self.BR), tuple(self.BR - (10 * k, 0)), tuple(self.TR - (10 * k, 0))], "#1e2129", .9),
                       w=4.2, seed=5000))
        g = lib.lin_grad([(0, bg[0], 1), (1, bg[1], 1)], 0, 0, 0, 1)
        cid = lib.clip_rect(0, 0, self.SW, self.SH, 6)
        o.append(f'<g transform="{self.screen_tf()}"><rect x="0" y="0" width="{self.SW}" height="{self.SH}" rx="6" fill="url(#{g})"/>'
                 f'<g clip-path="url(#{cid})">{content}</g>'
                 f'<path d="M14 {self.SH - 20} L{self.SW * .55} 12" stroke="#ffffff" stroke-opacity=".07" stroke-width="22" stroke-linecap="round"/></g>')
        # камера-точка
        c = self.TL + (self.TR - self.TL) * .5 + (self.BL - self.TL) * .025
        o.append(blob(ellipse_pts(c[0], c[1], 3 * k, 3 * k, 8), "#0d0f14"))
        # корпус-клавиатура
        deck = [tuple(self.BL) + (1,), tuple(self.BR) + (1,), tuple(self.FR) + (1,), tuple(self.FL) + (1,)]
        inner = ""
        for r in range(4):
            for c_ in range(10):
                a0, a1 = .08 + c_ * .084, .08 + c_ * .084 + .066
                b0, b1 = .1 + r * .17, .1 + r * .17 + .12
                kp = [tuple(self.key(a0, b0)), tuple(self.key(a1, b0)), tuple(self.key(a1, b1)), tuple(self.key(a0, b1))]
                col = "#3a3f4b"
                if press and press[0] == (r, c_):
                    col = mix("#3a3f4b", "#ffe9a0", press[1])
                inner += blob(kp, col)
        tp = [tuple(self.key(.36, .8)), tuple(self.key(.64, .8)), tuple(self.key(.64, .97)), tuple(self.key(.36, .97))]
        inner += blob(tp, "#aab1bd", .9)
        o.append(shape(deck, "#c9ced8", inner, w=3.8, seed=5001))
        o.append(shape([tuple(self.FL) + (1,), tuple(self.FR) + (1,), tuple(self.FR + (0, 8 * k)) + (1,), tuple(self.FL + (0, 8 * k)) + (1,)],
                       "#9aa1ae", "", w=3, seed=5002))
        return "".join(o)

    def glow(self, col="#9cc8ff", a=.55):
        c = (self.TL + self.BR) / 2
        g = lib.rad_grad([(0, col, a), (.45, col, a * .35), (1, col, 0)], c[0] - 60, c[1] + 20, 620, 520)
        return f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def text(x, y, s, size, fill="#ffffff", stroke=None, sw=0, extra=""):
    st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" paint-order="stroke"' if stroke else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" {FONT} font-size="{size}" fill="{fill}"{st} {extra}>{s}</text>'


def brain_icon(cx, cy, r, t, glow=1.0):
    """Сияющий мозг на экране (вид сбоку): лучи вращаются, мозг пульсирует."""
    o = []
    for j in range(12):
        a = t * .9 + j * math.pi / 6
        r0, r1 = r * 1.18, r * (1.55 + .12 * math.sin(t * 6 + j))
        w = 10 if j % 2 else 6
        o.append(line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], w, "#ffe27a", taper=.5,
                      wmin=.3, seed=5100 + j, op=.9 * glow))
    o.append(blob(ellipse_pts(cx, cy, r * 1.25, r * 1.1, 18), "#ffe9a8", .35 * glow))
    sc = 1 + .04 * math.sin(t * 8)
    P = lambda pts: T(pts, cx, cy, r / 60 * sc)  # noqa: E731
    body = [(-58, 6), (-56, -22), (-38, -44), (-10, -54), (20, -52), (46, -38), (60, -12), (58, 14), (40, 30), (14, 34), (-6, 30), (-26, 36),
            (-46, 28)]
    inner = blob(P([(-58, 10), (58, 14), (40, 30), (14, 34), (-6, 30), (-26, 36), (-46, 28)]), "#e27a95", .8)
    for j, st in enumerate([[(-40, -30), (-26, -16), (-34, 2)], [(-14, -46), (-6, -26), (-18, -8), (-8, 10)], [(14, -44), (6, -24), (20, -10)],
                            [(36, -30), (30, -12), (44, 2)], [(-30, 18), (-10, 12), (8, 20)], [(22, 8), (40, 16)]]):
        inner += line(P(st), 4.2, "#a8435f", seed=5130 + j, taper=.4, wmin=.4)
    o.append(shape(P(body), "#f4a3b8", inner, w=4.4, seed=5120))
    return "".join(o)


def button(cx, cy, w, h, label, col, press=0.0, size=40, flash=0.0):
    """Кнопка на экране: press 0..1 — вдавлена (сдвиг вниз, тень меньше)."""
    dy = 7 * press
    o = [blob(rect_pts(cx - w / 2, cy - h / 2 + 8, cx + w / 2, cy + h / 2 + 8, h / 2), "#000000", .35)]
    face = mix(col, "#000000", .18 * press)
    inner = blob(rect_pts(cx - w / 2, cy + h * .12 + dy, cx + w / 2, cy + h / 2 + dy, h / 2), mix(col, "#000000", .22), .9)
    inner += blob(rect_pts(cx - w / 2 + 12, cy - h / 2 + 6 + dy, cx + w / 2 - 12, cy - h / 2 + 14 + dy, 4), "#ffffff", .35)
    o.append(shape(rect_pts(cx - w / 2, cy - h / 2 + dy, cx + w / 2, cy + h / 2 + dy, h / 2), face, inner, w=3.6, seed=5200))
    o.append(text(cx, cy + size * .36 + dy, label, size, "#ffffff", INK, 5))
    if flash > 0:
        o.append(f'<rect x="{cx - w / 2 - 14 * flash:.1f}" y="{cy - h / 2 - 14 * flash + dy:.1f}" width="{w + 28 * flash:.1f}" '
                 f'height="{h + 28 * flash:.1f}" rx="{h / 2 + 14 * flash:.1f}" fill="none" stroke="#fff6c8" stroke-width="{6 * (1 - flash) + 1:.1f}" '
                 f'opacity="{1 - flash:.2f}"/>')
    return "".join(o)


def padlock(cx, cy, k, shake=0.0, red=0.0):
    P = lambda pts: T(pts, cx + shake, cy, k)  # noqa: E731
    o = [line(P([(-22, 0), (-22, -30), (-12, -46), (12, -46), (22, -30), (22, 0)]), 11, INK, taper=.02, wmin=.95, seed=5300)]
    o.append(line(P([(-22, 0), (-22, -30), (-12, -46), (12, -46), (22, -30), (22, 0)]), 5, "#c9ced8", taper=.02, wmin=.95, seed=5300))
    col = mix("#f2b33a", "#e2443a", red)
    o.append(shape(P(rect_pts(-34, -4, 34, 44, 8)), col, blob(P(rect_pts(10, -4, 34, 44, 8)), "#000000", .18) +
                   shape(P(ellipse_pts(0, 14, 7, 7, 10)), INK, "", w=1, seed=5302) + blob(P([(-3, 16), (3, 16), (5, 32), (-5, 32)]), INK), w=3.6,
                   seed=5301))
    return "".join(o)


def progress(t, x0, y0, w, h, fill, lock_shake=0.0, red=0.0):
    """Шкала: заполнено fill (доля), остальное — заперто, на нём «90 %» и замок."""
    o = [shape(rect_pts(x0, y0, x0 + w, y0 + h, h / 2), "#141b33", "", w=3.6, seed=5400)]
    fx = x0 + w * fill
    o.append(blob(rect_pts(x0 + 4, y0 + 4, fx, y0 + h - 4, h / 2 - 4), "#5fd17a"))
    # запертая часть: штриховка
    cid = lib.clip_rect(fx + 2, y0 + 4, x0 + w - 4 - fx - 2, h - 8, h / 2 - 4)
    hatch = "".join(f'<path d="M{x0 + j * 22 - 40:.1f} {y0 + h} L{x0 + j * 22:.1f} {y0}" stroke="#4a5470" stroke-width="7"/>' for j in range(int(w / 22) + 4))
    o.append(f'<g clip-path="url(#{cid})"><rect x="{fx:.1f}" y="{y0}" width="{x0 + w - fx:.1f}" height="{h}" fill="{mix("#2c3550", "#7a2430", red)}"/>{hatch}</g>')
    o.append(text(x0 + w * .58 + lock_shake, y0 - 18, "90 %", 64, mix("#ffffff", "#ff8a80", red), INK, 7))
    o.append(padlock(x0 + w * .58, y0 + h / 2 - 4, 1.0, lock_shake, red))
    return "".join(o)


# ═════════════════════════ кошелёк и монетки ═════════════════════════
def wallet(x, y, k=1.0, open_=1.0, puff=0.0, gape=0.0):
    """Кошелёк-«поцелуйчик» (с металлическим замком и двумя шариками), стоит на столе раскрытым. (x, y) — низ середины.
    puff 0..1 — полный (пухлый, в горле монетки) / пустой (опал, складки); gape — челюсти дрожат."""
    P = lambda pts: T(pts, x, y, k)  # noqa: E731
    o = [blob(P(ellipse_pts(4, 2, 84, 10, 12)), "#1a100a", .3)]
    wb = 66 + 10 * puff             # полуширина у пуза
    hb = 70 + 8 * puff              # высота до замка
    wt_ = 50.0                      # полуширина замка
    jaw = 40 + 22 * open_ + 8 * gape    # подъём задней челюсти
    # задняя створка (за горлом)
    back = [(-wt_, -hb), (-wt_ * .6, -hb - jaw * .95), (wt_ * .6, -hb - jaw * .95), (wt_, -hb)]
    o.append(shape(P(back + [(wt_, -hb + 6), (-wt_, -hb + 6)]), "#8f3530", "", w=3.6, seed=5501))
    # горло: тёмное, монетки
    mouth = [(-wt_ + 6, -hb + 2), (-wt_ * .55, -hb - jaw * .78), (wt_ * .55, -hb - jaw * .78), (wt_ - 6, -hb + 2)]
    minner = ""
    if puff > .05:
        for j, (cx_, cy_) in enumerate(((-24, -6), (2, -12), (26, -4), (-8, 2))):
            minner += shape(P(ellipse_pts(cx_, -hb + cy_ - jaw * .2 * puff, 15, 9, 10)), "#f2b33a", blob(P(ellipse_pts(cx_ + 4, -hb + cy_ - jaw * .2 * puff + 2, 8, 4, 8)),
                                                                                                          "#d4902a"), w=2.4, seed=5510 + j)
    o.append(blob(P(mouth), "#2a1010") + minner)
    # задняя дуга замка
    arc_b = [(-wt_ - 4, -hb), (-wt_ * .62, -hb - jaw), (wt_ * .62, -hb - jaw), (wt_ + 4, -hb)]
    o.append(line(P(arc_b), 12, INK, taper=.02, wmin=.95, seed=5520) + line(P(arc_b), 6, "#c9a860", taper=.02, wmin=.95, seed=5520))
    o.append(shape(P(ellipse_pts(7, -hb - jaw - 7, 8, 8, 10)), "#e8d29a", "", w=2.8, seed=5541))
    # тело-мешочек
    body = [(-wt_, -hb), (-wb, -hb * .62), (-wb - 6, -hb * .25), (-wb + 6, -4), (-wb * .45, 2, 1), (wb * .45, 2, 1), (wb - 6, -4), (wb + 6, -hb * .25),
            (wb, -hb * .62), (wt_, -hb)]
    inner = blob(P([(wb * .25, -hb), (wb, -hb * .62), (wb + 6, -hb * .25), (wb - 6, -4), (wb * .3, 2)]), "#7a2e2e", .85)
    inner += line(P([(-wb + 16, -hb * .3), (-wb * .45, -hb * .7)]), 5, "#e07a6a", seed=5504, op=.7)
    if puff < .5:
        for j in range(3):
            xx = -28 + j * 28
            inner += line(P([(xx, -hb + 12), (xx + 6, -hb * .6), (xx - 4, -hb * .3)]), 2.6, "#6a2424", seed=5506 + j, op=.8 * (1 - 2 * puff))
    o.append(shape(P(body), "#b8473f", inner, w=4.2, seed=5500))
    # передняя дуга замка и шарик
    arc_f = [(-wt_ - 4, -hb), (-wt_ * .6, -hb - 8), (wt_ * .6, -hb - 8), (wt_ + 4, -hb)]
    o.append(line(P(arc_f), 13, INK, taper=.02, wmin=.95, seed=5530) + line(P(arc_f), 7, "#d9c08a", taper=.02, wmin=.95, seed=5530))
    o.append(shape(P(ellipse_pts(-7, -hb - 16, 8, 8, 10)), "#e8d29a", blob(P(ellipse_pts(-9, -hb - 18, 3, 3, 6)), "#ffffff", .9), w=2.8, seed=5540))
    return "".join(o)


def coin(x, y, r, spin=0.0, seed=5600):
    """Монетка: spin — фаза вращения (ширина = |cos|)."""
    sx = max(.12, abs(math.cos(spin)))
    o = [shape(ellipse_pts(x, y, r * sx, r, 16), "#f2b33a", blob(ellipse_pts(x + r * .25 * sx, y + r * .2, r * .7 * sx, r * .75, 14), "#d4902a", .9) +
               (line([(x - r * .3 * sx, y - r * .1), (x, y - r * .45), (x + r * .3 * sx, y - r * .1)], 3, "#fff1b0", seed=seed + 1, op=.9) if sx > .4 else ""),
               w=3.2, seed=seed)]
    return "".join(o)


def coin_flight(t, t0, src, dst, n=7, dur=.55, up=180, rev=False, r=17):
    """Монетки по дугам от src к dst (rev — влетают). Возвращает SVG."""
    o = []
    for j in range(n):
        tj = t0 + j * .045
        u = clamp((t - tj) / dur)
        if u <= 0 or u >= 1:
            continue
        uu = ease_out(u, 1.6) if not rev else ease_in(u, 1.4)
        sx, sy = src
        dx, dy = dst[0] + (j - n / 2) * 34, dst[1] + 40 * ((j * 7) % 3 - 1)
        if rev:
            sx, sy, dx, dy = dx, dy, src[0], src[1]
        x = sx + (dx - sx) * uu
        y = sy + (dy - sy) * uu - up * math.sin(math.pi * uu) * (1 + .2 * (j % 3))
        o.append(coin(x, y, r * (1 + .1 * (j % 2)), t * 14 + j, seed=5600 + j * 3))
    return "".join(o)


def zip_lines(x, y, dx, dy, u, seed=5700, n=3, col="#ffe27a"):
    if u <= 0 or u >= 1:
        return ""
    o = []
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    for j in range(n):
        off = (j - (n - 1) / 2) * 26
        px, py = x - uy * off, y + ux * off
        a = 20 + 50 * u
        o.append(line([(px + ux * a, py + uy * a), (px + ux * (a + 40), py + uy * (a + 40))], 6, col, taper=.3, wmin=.4, seed=seed + j, op=1 - u))
    return "".join(o)


# ═════════════════════════ обруч с проводами и лампочкой ═════════════════════════
BAND = [(-150, -100), (-112, -126), (-50, -148), (16, -156), (70, -148), (106, -126), (122, -98)]


def headband(bulb=1.0, t=0.0, smoke=0.0):
    """В единицах головы Димы (head_tf). bulb — накал 0..1."""
    o = []
    from lib import band as lband
    pts = lband([tuple(p) for p in BAND], 26, 22, step=4, cap=True)
    inner = line([(p[0], p[1] + 6) for p in BAND[1:-1]], 6, "#6c7486", seed=5801, taper=.2, wmin=.8, op=.9)
    inner += line([(p[0], p[1] - 6) for p in BAND[1:-1]], 3, "#e6ebf2", seed=5802, taper=.3, wmin=.6, op=.9)
    o.append(shape(pts, "#a8b0bf", inner, w=4.2, seed=5800))
    # датчики-присоски на обруче
    for j, (x, y) in enumerate([(-96, -128), (-20, -150), (88, -130)]):
        o.append(shape(ellipse_pts(x, y, 13, 13, 12), "#4f8ea0", blob(ellipse_pts(x - 3, y - 3, 5, 5, 8), "#a8dde8"), w=3, seed=5810 + j))
    # патрон и колба
    bx, by = 40, -156
    o.append(shape([(bx - 18, by + 4), (bx + 18, by + 4), (bx + 16, by - 24), (bx - 16, by - 24)], "#8a909c",
                   line([(bx - 15, by - 8), (bx + 15, by - 8)], 2.6, INK, seed=5821) + line([(bx - 15, by - 16), (bx + 15, by - 16)], 2.6, INK, seed=5822),
                   w=3.4, seed=5820))
    gx, gy = bx + 2, by - 62
    glass = [(bx - 14, by - 22), (bx - 30, by - 44), (bx - 38, by - 70), (bx - 30, by - 94), (bx, by - 106), (bx + 32, by - 94), (bx + 40, by - 70),
             (bx + 32, by - 44), (bx + 14, by - 22)]
    col = mix("#e8edf2", "#fff07a", bulb)
    inner = blob(ellipse_pts(gx + 14, gy + 10, 18, 26, 12), mix("#c9d1d9", "#ffd23a", bulb), .8)
    inner += line([(gx - 10, gy + 30), (gx - 8, gy + 4), (gx - 2, gy - 4), (gx + 4, gy + 4), (gx + 8, gy - 4), (gx + 12, gy + 30)], 3.2,
                  mix("#5a5f6a", "#c45a00", bulb), seed=5831, taper=.1, wmin=.8)
    inner += line([(gx - 22, gy - 8), (gx - 14, gy - 28)], 5, "#ffffff", seed=5832, op=.8)
    o.append(shape(glass, col, inner, w=4, seed=5830))
    if bulb > .05:
        g = lib.rad_grad([(0, "#fff4a0", .75 * bulb), (.5, "#ffd23a", .3 * bulb), (1, "#ffd23a", 0)], gx, gy, 140, 140)
        o.append(f'<circle cx="{gx}" cy="{gy}" r="140" fill="url(#{g})" style="mix-blend-mode:screen"/>')
        for j in range(8):
            a = j * math.pi / 4 + .3
            r0, r1 = 60 + 6 * math.sin(t * 20 + j), 84 + 10 * bulb
            o.append(line([(gx + r0 * math.cos(a), gy + r0 * math.sin(a)), (gx + r1 * math.cos(a), gy + r1 * math.sin(a))], 6, "#ffd23a", seed=5840 + j,
                          taper=.4, wmin=.4, op=bulb))
    if smoke > 0:
        for j in range(3):
            v = clamp(smoke - j * .15)
            if v <= 0:
                continue
            sx, sy = gx + 10 * math.sin(j * 2 + smoke * 5), gy - 50 - 90 * v - j * 26
            rr = (14 + 8 * j) * (.6 + .6 * v)
            o.append(shape(ellipse_pts(sx, sy, rr, rr * .85, 12), mix("#b8bcc6", "#e3e6ec", v), "", w=3, seed=5850 + j))
    return "".join(o)


def wires(a, b, t, sag=120, seed=5900, cols=("#d8483c", "#3f7aa8"), wob=0.0):
    """Два провода от a к b с провисом и мелкими витками."""
    o = []
    a, b = np.array(a, float), np.array(b, float)
    for j, col in enumerate(cols):
        pts = []
        for i in range(29):
            u = i / 28
            p = a + (b - a) * u + np.array([0, sag * math.sin(math.pi * u)]) + np.array([j * 10, j * 6])
            p += np.array([0, 7 * math.sin(u * 40 + j) + wob * math.sin(u * 9 + t * 20)]) * (u * (1 - u) * 4)
            pts.append(tuple(p))
        o.append(line(pts, 9, INK, taper=.02, wmin=.95, seed=seed + j))
        o.append(line(pts, 4.6, col, taper=.02, wmin=.95, seed=seed + j))
    return "".join(o)


# ═════════════════════════ комната ═════════════════════════
def room_back(t, day):
    return "".join([den.wall(t, day), den.window(t, day), den.board(t), den.shelf(t), den.clock(*clock_at(t, day)), den.floor()])


def clock_at(t, day):
    if day:
        return (300.0 + t * .5, (t * 6) % 360, 0.0, 0.0)          # десять утра
    return (60.0 + t * .5, (t * 6) % 360, 0.0, 0.0)             # два часа ночи


def desk_world(t, d, day, *, on_desk="", mid="", front="", back_extra=""):
    w = [room_back(t, day), back_extra]
    w.append(room.chair(HIP[0], HIP[1] + 4, 1, 2300))
    w.append(den.desk_back())
    w.append(d.get("legs", ""))
    w.append(den.desk_top())
    w.append(on_desk)
    w.append(d["arm_f"])
    w.append(d["body"])
    w.append(mid)
    w.append(d["arm_n"])
    w.append(front)
    return "".join(w)


def vignette(col="#0a0c1e", a=.5):
    g = lib.rad_grad([(0, col, 0), (.6, col, 0), (1, col, a)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def compose(world, cam, day, light=""):
    cx, cy, s, r = cam
    set_ink(s)
    if day:
        g = lib.rad_grad([(0, "#fff4d0", .35), (1, "#fff4d0", 0)], 200, 500, 1100, 1000)
        tint = f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{g})" style="mix-blend-mode:screen"/>'
        o = ['<rect width="1080" height="1920" fill="#cfe0d6"/>', f'<g transform="{lib.cam(cx, cy, s, r)}">{world}{tint}{light}</g>',
             vignette("#3a2a1a", .28)]
    else:
        dark = lib.rad_grad([(0, "#000000", 0), (.45, "#000000", 0), (1, "#0a0c1e", .5)], 640, 1000, 1100, 1100)
        o = ['<rect width="1080" height="1920" fill="#2a3346"/>',
             f'<g transform="{lib.cam(cx, cy, s, r)}">{world}<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{dark})"/>{light}</g>',
             vignette()]
    return lib.svg("".join(o))


# ═════════════════════════ s05: ночь, «КУПИТЬ», жмёт на «купил», монетки улетают на «курс» ═════════════════════════
LAP5 = Laptop(440.0, 1098.0, 1.0)
WAL5 = (766.0, 1158.0)


def screen_buy(t, press, flash):
    c = brain_icon(150, 62, 40, t)
    c += button(150, 156, 236, 70, "КУПИТЬ", "#e2443a", press, 44, flash)
    return c


def s05(t):
    tk, tc = T_KUPIL, T_KURS
    k = ease_io(clamp((t - 6.75) / 1.8))
    wh = whip_in(t, 6.75, .24)
    hit = punch(t, tk, .05, .05, .3) + punch(t, tc, .06, .05, .35)
    s = (1.56 + .12 * k) * (1 + hit)
    cam = (530 + 14 * k + 380 * wh, 985 - 20 * k + 10 * bump(t, tc, .3) * osc(t, 11), s, -2.6 * wh + .5 * k + .8 * bump(t, tc, .3) * osc(t, 9))
    L = LAP5
    # нажатие: указательный палец поднят (замах) и бьёт клавишу Enter на «купил»
    key_pt = L.key(.45, .5)
    wind = smooth(tk - .38, tk - .12, t)
    strike = smooth(tk - .1, tk, t)
    after = smooth(tk + .15, tk + .4, t)
    tip = key_pt + np.array([-6, -4]) + np.array([-14, -48]) * wind * (1 - strike) + np.array([0, -14]) * after
    hd = np.array([.55, .83])
    hd = hd / np.linalg.norm(hd)
    wr = tip - hd * 92 * BS
    wr = wr + np.array([0, 4 * osc(t, 2.1)]) * (1 - wind)
    far_t = L.key(.28, .55) + np.array([0, -6 + 3 * osc(t, 1.7)])
    arms = {"n": ("ik", tuple(wr), -1), "f": ("ik", tuple(far_t), -1)}
    hands = {"n": hnd(POINT, tuple(hd)), "f": hnd(REST, (1, .25))}
    pressed = bump(t, tk - .02, .3)
    key_rc = (2, 4)
    look_coins = smooth(tc + .05, tc + .3, t)
    expr = dict(lid=.75 + .2 * wind + .1 * look_coins, look=(.75 - .3 * look_coins, .35 - .1 * wind - .85 * look_coins), brows="det" if t < tc + .1 else "up",
                mouth="grin" if t < tc + .1 else "talk", open=.55, smile=1.0, closed=blink_at(t, 7.05, .14), hair=5 * bump(t, tk, .3) + 4 * bump(t, tc, .3))
    d = dima(t, arms, hands, expr, lean=.26 + .04 * wind - .06 * look_coins, head_ang=.06 * wind - .1 * look_coins + .02 * osc(t, 1.3))
    flash = clamp((t - tk) / .35) if t > tk else 0.0
    press_k = ((4, 0), 0.0)
    scr = screen_buy(t, pressed, flash if 0 < flash < 1 else 0.0)
    lap = L.draw(scr, press=(key_rc, pressed))
    del press_k
    gape = bump(t, tc - .02, .3) * osc(t, 12)
    wal = wallet(*WAL5, 1.0, 1.0, puff=1.0 - smooth(tc, tc + .35, t), gape=gape)
    coins = coin_flight(t, tc, (WAL5[0], WAL5[1] - 90), (690, 250), n=7, dur=.75, up=200, r=22)
    zl = zip_lines(WAL5[0] - 10, WAL5[1] - 150, -.3, -1, clamp((t - tc) / .4), seed=5710)
    w = desk_world(t, d, False, on_desk=lap + wal, front=coins + zl)
    return compose(w, cam, False, L.glow("#9cc8ff", .55 + .25 * pressed))


# ═════════════════════════ s06: обруч, лампочка, тужится; «девяносто» — лампочка мигает и тухнет, пот ═════════════════════════
LAP6 = Laptop(470.0, 1094.0, 1.0)


def bulb_state(t):
    td = T_DEVYANOSTO
    if t < td:
        return .85 + .15 * osc(t, 7)
    v = t - td
    flick = [(0, .07, 0.0), (.07, .14, 1.0), (.14, .2, 0.0), (.2, .27, .8), (.27, .33, .0), (.33, .38, .45)]
    for a, b, val in flick:
        if a <= v < b:
            return val
    return 0.0


def s06(t):
    td = T_DEVYANOSTO
    k = ease_io(clamp((t - 8.15) / 2.35))
    hit = punch(t, td, .09, .05, .4)
    strain = smooth(8.15, 8.5, t) * (1 - smooth(td + .3, td + .55, t))
    shake = strain * osc(t, 15)
    s = (1.85 + .25 * k) * (1 + hit)
    cam = (392 + 12 * k + 2.5 * shake, 935 - 16 * k, s, .6 - .9 * k + 1.0 * bump(t, td, .3) * osc(t, 9))
    L = LAP6
    after = smooth(td + .35, td + .6, t)
    fist_n = np.array([452.0, 1062.0]) + np.array([3 * shake, -10 * strain])
    fist_f = L.key(.25, .5) + np.array([-10 + 2 * shake, -12])
    arms = {"n": ("ik", tuple(fist_n), -1), "f": ("ik", tuple(fist_f), -1)}
    hands = {"n": hnd(FIST, (.35, -1)), "f": hnd(FIST, (1, .1))}
    if after > .5:
        hands["n"] = hnd(REST, (.6, .8))
    expr = dict(lid=.2 + .55 * after, look=(.5, -.75 * after), brows="det" if after < .5 else "worry", mouth="flat",
                closed=strain if after < .5 else blink_at(t, 10.05, .14), blush=strain * .95, hair=2 * shake + 6 * bump(t, td, .3))
    d = dima(t, arms, hands, expr, lean=.2 + .02 * strain, head_ang=.02 * shake - .07 * after)
    bulb = bulb_state(t)
    smoke = clamp((t - td - .4) / .7)
    band = f'<g transform="{head_tf(d)}">{headband(bulb, t, smoke)}</g>'
    a = head_pt(d, (118, -98))
    b = L.BL + np.array([-4, -40])
    wr = wires(a, b, t, sag=70, wob=6 * strain)
    # экран: шкала тужится 10 → 12 %, на «девяносто» — замок краснеет и трясётся, шкала падает к 10
    fill = .1 + .03 * strain * (.5 + .5 * osc(t, 6)) if t < td else .1
    red = bump(t, td, .5)
    scr = text(150, 54, "МОЗГ", 34, "#9cc8ff") + progress(t, 22, 118, 256, 54, fill, 8 * red * osc(t, 14), red)
    lap = L.draw(scr, bg=("#141c38", "#25356a"))
    # капля пота у виска, вторая — позже
    sw = sweat(*head_pt(d, (-58, -52)), 1.0, clamp((t - td - .05) / .6), seed=3001)
    sw += sweat(*head_pt(d, (104, -40)), .8, clamp((t - td - .35) / .55), seed=3002)
    # штрихи натуги
    strain_l = ""
    if strain > .2:
        hx, hy = head_pt(d, (-10, -40))
        for j in range(4):
            aa = math.radians(-175 + j * 30)
            r0 = 165 + 7 * osc(t, 10, j)
            strain_l += line([(hx + r0 * math.cos(aa), hy + r0 * math.sin(aa)), (hx + (r0 + 34) * math.cos(aa), hy + (r0 + 34) * math.sin(aa))], 5.5, "#3a2a22",
                             seed=5950 + j, taper=.3, wmin=.4)
    w = desk_world(t, d, False, on_desk=lap, mid=band, front=wr + sw + strain_l)
    return compose(w, cam, False, L.glow("#9cc8ff", .45))


# ═════════════════════════ s16: день, «ВЕРНУТЬ», монетки обратно на «деньги», снимает обруч и бросает в коробку ═════════════════════════
LAP16 = Laptop(470.0, 1098.0, .92)
WAL16 = (790.0, 1138.0)
BOX = (930.0, 1146.0)


def box_back(x, y):
    o = [shape([(x - 80, y - 100), (x + 70, y - 100), (x + 96, y - 130), (x - 56, y - 130)], "#b98a52", "", w=3.4, seed=6001)]   # задняя стенка-клапан
    o.append(blob([(x - 78, y - 100), (x + 70, y - 100), (x + 62, y - 88), (x - 70, y - 88)], "#6e4d28", .9))
    return "".join(o)


def box_front(x, y):
    o = [blob(ellipse_pts(x + 6, y + 2, 100, 10, 12), "#1a100a", .3)]
    o.append(shape(rect_pts(x - 84, y - 100, x + 70, y), "#d4a464", blob(rect_pts(x + 40, y - 100, x + 70, y), "#b98a52", .9) +
                   line([(x - 84, y - 50), (x + 70, y - 50)], 6, "#e8c78e", seed=6012, op=.8), w=4, seed=6010))
    o.append(shape([(x - 84, y - 100), (x - 128, y - 70), (x - 120, y - 60), (x - 80, y - 88)], "#c99a5a", "", w=3.4, seed=6011))
    o.append(shape([(x + 70, y - 100), (x + 112, y - 76), (x + 104, y - 66), (x + 70, y - 88)], "#b98a52", "", w=3.4, seed=6013))
    return "".join(o)


def s16(t):
    tv, tdg = T_VERNUL, T_DENGI
    k = ease_io(clamp((t - 27.1) / 2.05))
    wh = whip_in(t, 27.1, .24)
    hit = punch(t, tv, .05, .05, .3) + punch(t, tdg + .38, .05, .05, .3)
    s = (1.22 + .12 * k) * (1 + hit)
    cam = (575 + 15 * k - 380 * wh, 975 - 20 * k, s, 2.6 * wh - .4 * k)
    L = LAP16
    # 1) замах и нажатие «ВЕРНУТЬ» на «вернул»; 2) рука к обручу (28.32), снимает (28.55), бросок (28.72) → коробка (28.98)
    key_pt = L.key(.86, .42)
    wind = smooth(tv - .36, tv - .12, t)
    strike = smooth(tv - .1, tv, t)
    tip = key_pt + np.array([-6, -4]) + np.array([-18, -70]) * wind * (1 - strike)
    hd = np.array([.55, .83])
    hd = hd / np.linalg.norm(hd)
    wr_key = tip - hd * 92 * BS
    t_up, t_grab, t_lift, t_throw, t_land = 28.2, 28.42, 28.62, 28.76, 29.0
    pressed = bump(t, tv - .02, .3)
    relief = smooth(tdg + .3, tdg + .5, t)
    expr = dict(lid=.7 + .2 * pressed, look=(.75, .3), brows="det" if t < tv + .2 else "calm", mouth="smile", smile=.6 + .4 * relief,
                closed=blink_at(t, 27.35, .14), hair=4 * bump(t, tv, .3))
    lean0, hang0 = .17, 0.0
    probe = dima(t, {"n": ("ik", tuple(wr_key), -1), "f": ("ik", tuple(L.key(.25, .55)), -1)}, {}, expr, lean=lean0, head_ang=hang0)
    grab_local = np.array([16.0, -168.0])               # верх обруча над макушкой (ед. головы)
    grab_w = head_pt(probe, grab_local)
    hd_g = np.array([.35, .94])
    hd_g = hd_g / np.linalg.norm(hd_g)
    wr_grab = grab_w - hd_g * 70 * BS
    lift_off = np.array([40.0, -120.0])
    if t < t_up:
        wr = wr_key + np.array([0, 3 * osc(t, 2)])
        hn = hnd(POINT, tuple(hd))
        band_off = None
    elif t < t_grab:
        u = ease_io(clamp((t - t_up) / (t_grab - t_up)))
        wr = wr_key + (wr_grab - wr_key) * u
        hn = hnd(REST, tuple(hd + (hd_g - hd) * u))
        band_off = None
    else:
        lift = ease_io(clamp((t - t_grab - .05) / (t_lift - t_grab)))
        wr = wr_grab + lift_off * lift
        hn = hnd(FIST, tuple(hd_g))
        band_off = lift_off * lift
    look = (.75, .3)
    if t > t_up:
        look = (.6, -.6)
    if t > t_throw:
        look = (.85, .2)
    expr["look"] = look
    if t > t_lift:
        expr["mouth"] = "grin"
    if t >= t_throw:
        # рука после броска уходит вправо-вниз
        v = ease_out(clamp((t - t_throw) / .25), 2)
        wr = wr_grab + lift_off + np.array([140, 60]) * v
        hn = hnd(REST, (.8, .3))
    arms = {"n": ("ik", tuple(wr), -1), "f": ("ik", tuple(L.key(.25, .55) + np.array([0, 2 * osc(t, 1.6)])), -1)}
    hands = {"n": hn, "f": hnd(REST, (1, .25))}
    d = dima(t, arms, hands, expr, lean=lean0, head_ang=hang0 - .05 * bump(t, t_lift, .3) + .02 * osc(t, 1.2))
    # обруч: на голове → в руке → летит в коробку
    band_svg = ""
    band_fly = ""
    if band_off is None and t < t_throw:
        band_svg = f'<g transform="{head_tf(d)}">{headband(0.0, t)}</g>'
        band_at = head_pt(d, (118, -98))
    elif t < t_throw:
        # в руке: тот же рисунок, сдвинут вместе с кистью
        hx, hy = d["head"]
        band_svg = (f'<g transform="translate({band_off[0]:.2f} {band_off[1]:.2f})"><g transform="{head_tf(d)}">{headband(0.0, t)}</g></g>')
        band_at = head_pt(d, (118, -98)) + band_off
    else:
        u = clamp((t - t_throw) / (t_land - t_throw))
        p0 = head_pt(d, grab_local) + lift_off
        p1 = np.array([BOX[0] - 8, BOX[1] - 110])
        x = p0[0] + (p1[0] - p0[0]) * u
        y = p0[1] + (p1[1] - p0[1]) * u - 160 * math.sin(math.pi * u)
        ang = 220 * u
        sc = 1 - .25 * u
        if u < 1:
            band_fly = (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({BS * sc:.3f}) translate({-grab_local[0]:.1f} {-grab_local[1]:.1f})">'
                        f'{headband(0.0, t)}</g>')
            band_at = np.array([x, y]) + rot(np.array([118 - grab_local[0], -98 - grab_local[1]]), math.radians(ang)) * BS * sc
        else:
            band_at = None
    flash = clamp((t - tv) / .35) if t > tv else 0.0
    scr = (text(150, 58, "КУРС", 30, "#7d8796") + text(150, 96, "«РАСКРОЙ 90 %»", 26, "#7d8796") +
           button(150, 160, 230, 64, "ВЕРНУТЬ", "#3aa86b", pressed, 40, flash if 0 < flash < 1 else 0.0))
    if t > tv + .2:
        scr += text(150, 212, "деньги возвращены", 20, "#3aa86b")
    lap = L.draw(scr, bg=("#f4f7fb", "#dde7f2"), press=((1, 9), pressed))
    # монетки влетают в кошелёк
    landed = smooth(tdg + .3, tdg + .55, t)
    wal = wallet(*WAL16, .92, 1.0, puff=landed + .15 * bump(t, tdg + .45, .3), gape=bump(t, tdg + .3, .3) * osc(t, 12))
    coins = coin_flight(t, tdg, (WAL16[0], WAL16[1] - 28), (1180, 600), n=7, dur=.42, up=120, rev=True)
    spark = ""
    u = clamp((t - tdg - .45) / .35)
    if 0 < u < 1:
        for j in range(6):
            a = math.radians(-160 + j * 28)
            r0, r1 = 60 + 30 * u, 90 + 46 * u
            spark += line([(WAL16[0] + r0 * math.cos(a), WAL16[1] - 40 + r0 * math.sin(a)), (WAL16[0] + r1 * math.cos(a), WAL16[1] - 40 + r1 * math.sin(a))],
                          6, "#f2b33a", seed=6100 + j, taper=.3, wmin=.4, op=1 - u)
    # провода: от обруча к ноутбуку, пока обруч не в коробке
    wr_svg = ""
    if band_at is not None:
        wr_svg = wires(band_at, L.BL + np.array([-4, -40]), t, sag=60 + 30 * (t > t_throw))
    land = clamp((t - t_land) / .3)
    thud = ""
    if 0 < land < 1:
        for j in range(5):
            a = math.radians(-150 + j * 30)
            thud += line([(BOX[0] + 80 * math.cos(a), BOX[1] - 110 + 60 * math.sin(a)), (BOX[0] + (110 + 30 * land) * math.cos(a),
                                                                                        BOX[1] - 110 + (80 + 24 * land) * math.sin(a))],
                          5, INK, seed=6200 + j, taper=.3, wmin=.4, op=1 - land)
    on_desk = lap + wal + box_back(*BOX)
    front = wr_svg + band_fly + box_front(*BOX) + coins + spark + thud
    w = desk_world(t, d, True, on_desk=on_desk, mid=band_svg, front=front)
    return compose(w, cam, True)


# ═════════════════════════ s14: кухня днём, каша, ложка в рот на «поесть», пар ═════════════════════════
KHIP = np.array([250.0, 1262.0])
BOWL = (560.0, 1104.0)


def kitchen_back(t):
    k = .74
    g = (f'<g transform="translate(560 1330) scale({k}) translate(-560 -1590)">' + kitchen.wall("morning") + kitchen.window("morning", t) +
         kitchen.clock_wall(10, 5 + t * .2, "morning") + kitchen.shelf(dust=0.0, wiped=1.0) + kitchen.cupboard() + kitchen.counter() +
         kitchen.fridge(magnets=True) + kitchen.floor("morning") + kitchen.lamp("morning", t, .02 * osc(t, .4)) + "</g>")
    return g


def table_top():
    x0, x1 = 360.0, 1400.0
    yt, yf = 1080.0, 1150.0
    cloth = [(x0 + 10, yt, 1), (x1, yt, 1), (x1, yf + 50, 1), (x0 - 10, yf + 60, 1)]
    inner = blob([(x0 - 10, yf), (x1, yf - 4), (x1, yf + 50), (x0 - 10, yf + 60)], "#d8a38d", .7)
    for j in range(9):
        x = x0 + 30 + j * 110
        inner += line([(x, yt + 4), (x - 8, yf + 54)], 7, "#e98a86", seed=6300 + j, op=.55, taper=.05, wmin=.9)
    inner += line([(x0, yt + 36), (x1, yt + 34)], 7, "#e98a86", seed=6320, op=.55, taper=.05, wmin=.9)
    o = [shape(cloth, "#f6e3d6", inner, w=4.2, seed=6301)]
    o.append(shape(rect_pts(x0 + 40, yf + 50, x0 + 74, 1700), den.WOOD, blob(rect_pts(x0 + 58, yf + 50, x0 + 74, 1700), den.WOOD_SH, .9), w=3.6, seed=6302))
    return "".join(o)


def porridge_bowl(x, y, k, t, dip=0.0):
    P = lambda pts: T(pts, x, y, k)  # noqa: E731
    o = [blob(P(ellipse_pts(6, 4, 108, 14, 14)), "#1a100a", .3)]
    o.append(shape(P([(-100, -66), (100, -66), (88, -28), (56, -4), (-56, -4), (-88, -28)]), "#6aa0c8",
                   blob(P([(30, -66), (100, -66), (88, -28), (56, -4), (20, -4)]), "#4f80a8", .9) +
                   line(P([(-92, -46), (92, -46)]), 5, "#f6efe2", seed=6401, op=.9), w=4.2, seed=6400))
    o.append(shape(P(ellipse_pts(0, -66, 100, 18, 18)), "#f3e2b8", blob(P(ellipse_pts(10, -62, 80, 11, 14)), "#e6cd96", .9) +
                   blob(P(ellipse_pts(-24 - 8 * dip, -68, 18, 6, 10)), "#d9b46a", .8 * dip) +
                   shape(P(rect_pts(14, -76, 40, -64, 3)), "#ffe27a", "", w=2.4, seed=6403), w=3.6, seed=6402))
    o.append(den.steam(x - 10 * k, y - 82 * k, 1.5 * k, t))
    o.append(den.steam(x + 40 * k, y - 78 * k, 1.2 * k, t + .45))
    return "".join(o)


def spoon(a, b, w=10.0, seed=6500, food=0.0):
    """Ложка: a — черпак, b — конец ручки."""
    a, b = np.array(a, float), np.array(b, float)
    u = (b - a) / np.linalg.norm(b - a)
    n = np.array([-u[1], u[0]])
    o = [line([tuple(a + u * 22), tuple(b)], w + 5, INK, taper=.05, wmin=.9, seed=seed), line([tuple(a + u * 22), tuple(b)], w - 2, "#c9ced8", taper=.05, wmin=.9, seed=seed)]
    cup = [tuple(a + u * 26 + n * 4), tuple(a + u * 8 + n * 15), tuple(a - u * 16 + n * 11), tuple(a - u * 22), tuple(a - u * 16 - n * 11),
           tuple(a + u * 8 - n * 15), tuple(a + u * 26 - n * 4)]
    inner = blob([tuple(a + u * 4 + n * 8), tuple(a - u * 14 + n * 6), tuple(a - u * 14 - n * 6), tuple(a + u * 4 - n * 8)], "#f3e2b8", food) if food > 0 else ""
    o.append(shape(cup, "#d8dde6", inner, w=3.4, seed=seed + 1))
    return "".join(o)


def s14(t):
    tp = T_POEST
    k = ease_io(clamp((t - 24.25) / 1.9))
    wh = whip_in(t, 24.25, .24)
    hit = punch(t, tp, .05, .05, .32)
    s = (1.45 + .1 * k) * (1 + hit)
    cam = (480 + 20 * k + 380 * wh, 965 - 15 * k, s, -2.6 * wh + .5 * k)
    # ложка: зачерпнул (24.25–24.45) → ко рту, в рот на «поесть» (24.72) → жуёт, второй заход с 25.45
    t_dip2 = 25.42
    to_mouth = smooth(24.42, tp, t) * (1 - smooth(tp + .3, tp + .55, t))
    to_mouth2 = smooth(t_dip2 + .1, t_dip2 + .38, t)
    chew = smooth(tp + .25, tp + .4, t) * (1 - smooth(25.95, 26.1, t))
    lean = .14 + .03 * to_mouth + .02 * to_mouth2
    hang = -.04 * to_mouth + .03 * chew * osc(t, 3.2)
    probe = dima(t, {"n": ("ik", (440, 1060), -1), "f": ("ik", (470, 1110), -1)}, {}, {}, hip=KHIP, lean=lean, head_ang=hang)
    mouth = probe["head"] + rot(np.array([80.0, 94.0]) * BS, lean * .5 + hang)
    # положение черпака: в миске ↔ у рта
    in_bowl = np.array([BOWL[0] - 30, BOWL[1] - 70]) + np.array([0, 8 * math.sin(t * 7)]) * (1 - max(to_mouth, to_mouth2))
    m = max(to_mouth, to_mouth2)
    sp = in_bowl + (mouth - in_bowl) * ease_io(m)
    ang = math.radians(28 - 6 * m)
    u = np.array([math.cos(ang), math.sin(ang)])
    fist = sp + u * 78
    hdir = np.array([-.2, -1.0])
    hdir = hdir / np.linalg.norm(hdir)
    wr = fist - hdir * 26
    happy = smooth(tp + .05, tp + .25, t)
    expr = dict(lid=.75, look=(.45, .55 - .5 * m), brows="up", mouth="smile" if (m < .7) else "flat", smile=.4 + .6 * happy, laugh=happy * (1 - to_mouth2) * (.6 + .4 * chew),
                closed=blink_at(t, 24.35, .14), blush=.6 * happy, hair=3 * bump(t, tp, .3))
    hands = {"n": dict(kind="open", dir=tuple(hdir), curl=(.85, .9, .92, .95), spread=.02, thumb=.85, bend=.05),
             "f": dict(kind="open", dir=(1, .2), curl=(.2, .25, .3, .35), spread=.08, thumb=.4)}
    d = dima(t, {"n": ("ik", tuple(wr), -1), "f": ("ik", (500, 1112), -1)}, hands, expr, hip=KHIP, lean=lean, head_ang=hang)
    food = 1.0 - smooth(tp + .05, tp + .2, t)
    if t > t_dip2:
        food = 1.0
    sp_svg = spoon(tuple(sp), tuple(sp + u * 160), food=food)
    w = [kitchen_back(t), room.chair(KHIP[0], KHIP[1] + 4, 1, 2300), d.get("legs", ""), table_top(), porridge_bowl(*BOWL, .95, t, dip=1 - m),
         kitchen.mug(800, 1110, .62, 0, col="#3f7a72"), d["arm_f"], d["body"], sp_svg, d["arm_n"]]
    # «мм!» — сердечки-искры у головы после «поесть»
    hu = clamp((t - tp - .15) / .6)
    if 0 < hu < 1:
        hx, hy = head_pt(d, (150, -60))
        for j in range(3):
            v = clamp(hu * 1.3 - j * .15)
            if v <= 0:
                continue
            x, y = hx + 40 * j + 10 * math.sin(v * 6), hy - 30 - 120 * v - 30 * j
            r = 14 * (1 - .4 * v)
            heart = [(x, y + r * 1.2), (x - r * 1.3, y), (x - r * 1.1, y - r * .9), (x - r * .3, y - r), (x, y - r * .4), (x + r * .3, y - r),
                     (x + r * 1.1, y - r * .9), (x + r * 1.3, y)]
            w.append(shape(heart, "#e2443a", "", w=3, seed=6600 + j))
    world = "".join(w)
    cx, cy, s_, r = cam
    set_ink(s_)
    o = ['<rect width="1080" height="1920" fill="#f0dcb4"/>', f'<g transform="{lib.cam(cx, cy, s_, r)}">{world}{kitchen.lamp_glow("morning")}</g>',
         vignette("#3a2a1a", .26)]
    return lib.svg("".join(o))


SHOTS = {"s05": s05, "s06": s06, "s14": s14, "s16": s16}


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    return SHOTS[sid](t)
