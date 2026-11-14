"""Сцена desk рилса 39 «я многозадачный»: планы s01 s02 s05 s06 s10 (день, суета) и s14 s15 s16 s17 (спокойный тёплый свет).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Удары — на словах по voice/words.json.

Основа — сцена dima рилса 35 (scene35.py в этой же папке — только как образец): комната den.py, Дима people.py (сидит
слева лицом вправо, таз (230, 1262)), ноутбук с экраном в своей плоскости. Своё: пять карточек-дел с иконками
(отчёт, созвон, чат, почта, список), рукописная «5», гарнитура, телефон с пузырями чата, окно созвона с коллегами,
красные подчёркивания и «?», опрокинутая кружка, зелёная галочка, кот на столе (cat2.py рилса 35) и сердечки.
Один и тот же Дима и один стол во всех девяти планах.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat  # noqa: E402
import cat2  # noqa: E402
import den  # noqa: E402
import kitchen  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import room  # noqa: E402
from lib import INK, T, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, mix, rect_pts, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["word"].strip(".,?!:").lower() == word and w["start"] >= after:
            return w["start"]
    raise KeyError(word)


T_PYAT = wt("пять")            # 2.16
T_SRAZU = wt("сразу")          # 2.76
T_OTCHET = wt("отчёт")         # 7.32
T_SOZVON = wt("созвон")        # 8.36
T_PEREP = wt("переписывается")  # 9.12
T_CHAT = wt("чате")            # 9.92
T_OBE = wt("обе")              # 18.0
T_HUZHE = wt("хуже")           # 19.28
T_ODNO = wt("одно")            # 25.84
T_VYKL = wt("выключает")       # 26.8
T_OSTAL = wt("остальное")      # 27.6
T_OSHIBOK = wt("ошибок")       # 29.04
T_KOT = wt("кот")              # 29.84
T_VNIM = wt("внимание")        # 31.68

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
    if t < t0:
        return 0.0
    if t < t0 + up:
        return amp * ease_out((t - t0) / up, 2)
    return amp * (1 - ease_io(clamp((t - t0 - up) / down)))


def pop(t, t0, dur=.32):
    """0 → 1 с перелётом (back_out)."""
    return lib.back_out(clamp((t - t0) / dur), 2.2) if t > t0 else 0.0


def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([v[0] * c - v[1] * s, v[0] * s + v[1] * c])


def lerp(a, b, u):
    return a + (b - a) * u


# ═════════════════════════ Дима ═════════════════════════
def dima(t, arms, hands=None, expr=None, lean=0.14, head_ang=0.0):
    feet = {"n": ((450, 1468), 0.0), "f": ((425, 1462), 0.0)}
    p = dict(hip=tuple(HIP), scale=BS, lean=lean, feet=feet, arms=arms, hands=hands or {}, expr=expr or {}, head_ang=head_ang,
             hood=0.0, strings=(2 * osc(t, 1.3), 1.5 * osc(t, 1.1, 1)))
    d = people.draw(p, "dima")
    d["hang"] = lean * .5 + head_ang
    return d


def head_tf(d):
    hx, hy = d["head"]
    return f"translate({hx:.2f} {hy:.2f}) scale({BS}) rotate({math.degrees(d['hang']):.3f})"


def head_pt(d, local):
    return d["head"] + rot(np.array(local, float), d["hang"]) * BS


REST = dict(kind="open", curl=(.25, .3, .35, .4), spread=.08, thumb=.35, bend=.1)
TYPE = dict(kind="open", curl=(.45, .5, .55, .6), spread=.1, thumb=.45, bend=.15)
FIST = dict(kind="open", curl=(.85, .9, .92, .95), spread=.02, thumb=.85, bend=.05)
GRIP = dict(kind="open", curl=(.7, .75, .8, .85), spread=.04, thumb=.6, bend=.1)
CLAW = dict(kind="open", curl=(.4, .45, .5, .55), spread=.18, thumb=.3, bend=.2)


def hnd(base, d, **kw):
    h = dict(base)
    h["dir"] = d
    h.update(kw)
    return h


# ═════════════════════════ ноутбук ═════════════════════════
class Laptop:
    """Ноутбук на столе (как в рилсе 35). (x, y) — левый низ экрана (петля), k — масштаб. Контент экрана — 0..SW × 0..SH."""
    SW, SH = 300.0, 220.0

    def __init__(self, x, y, k=1.0):
        self.x, self.y, self.k = x, y, k
        W, H = 300 * k, 232 * k
        self.BL = np.array([x, y])
        self.BR = np.array([x + W, y - 16 * k])
        self.TL = np.array([x + 14 * k, y - H])
        self.TR = np.array([x + W + 14 * k, y - 16 * k - H])
        dk = np.array([-78 * k, 40 * k])
        self.FL, self.FR = self.BL + dk, self.BR + dk
        u = (self.TR - self.TL) / np.linalg.norm(self.TR - self.TL)
        v = (self.BL - self.TL) / np.linalg.norm(self.BL - self.TL)
        o = self.TL + u * 12 * k + v * 12 * k
        uu = (self.TR - self.TL - u * 24 * k) / self.SW
        vv = (self.BL - self.TL - v * 30 * k) / self.SH
        self.M = (uu, vv, o)

    def P(self, a, b):
        uu, vv, o = self.M
        return o + uu * a + vv * b

    def key(self, fa, fb):
        a = self.BL + (self.BR - self.BL) * fa
        return a + (self.FL - self.BL) * fb

    def screen_tf(self):
        uu, vv, o = self.M
        return f"matrix({uu[0]:.5f} {uu[1]:.5f} {vv[0]:.5f} {vv[1]:.5f} {o[0]:.3f} {o[1]:.3f})"

    def draw(self, content, bg=("#eef3f9", "#d9e3ee"), press=None, spill=0.0):
        k = self.k
        o = [blob([tuple(self.FL + (0, 6 * k)), tuple(self.FR + (14 * k, 6 * k)), tuple(self.BR + (30 * k, 4 * k)), tuple(self.BL + (10 * k, 4 * k))],
                  "#1a100a", .3, lib.blur(5))]
        lid = [tuple(self.BL) + (1,), tuple(self.TL) + (1,), tuple(self.TR) + (1,), tuple(self.BR) + (1,)]
        o.append(shape(lid, "#30343f", blob([tuple(self.TR), tuple(self.BR), tuple(self.BR - (10 * k, 0)), tuple(self.TR - (10 * k, 0))], "#1e2129", .9),
                       w=4.2, seed=5000))
        g = lib.lin_grad([(0, bg[0], 1), (1, bg[1], 1)], 0, 0, 0, 1)
        cid = lib.clip_rect(0, 0, self.SW, self.SH, 6)
        o.append(f'<g transform="{self.screen_tf()}"><rect x="0" y="0" width="{self.SW}" height="{self.SH}" rx="6" fill="url(#{g})"/>'
                 f'<g clip-path="url(#{cid})">{content}</g>'
                 f'<path d="M14 {self.SH - 20} L{self.SW * .55} 12" stroke="#ffffff" stroke-opacity=".07" stroke-width="22" stroke-linecap="round"/></g>')
        c = self.TL + (self.TR - self.TL) * .5 + (self.BL - self.TL) * .025
        o.append(blob(ellipse_pts(c[0], c[1], 3 * k, 3 * k, 8), "#0d0f14"))
        deck = [tuple(self.BL) + (1,), tuple(self.BR) + (1,), tuple(self.FR) + (1,), tuple(self.FL) + (1,)]
        inner = ""
        for r in range(4):
            for c_ in range(10):
                a0, a1 = .08 + c_ * .084, .08 + c_ * .084 + .066
                b0, b1 = .1 + r * .17, .1 + r * .17 + .12
                kp = [tuple(self.key(a0, b0)), tuple(self.key(a1, b0)), tuple(self.key(a1, b1)), tuple(self.key(a0, b1))]
                col = "#3a3f4b"
                if press and (r, c_) in press[0]:
                    col = mix("#3a3f4b", "#8fa6c8", press[1])
                inner += blob(kp, col)
        tp = [tuple(self.key(.36, .8)), tuple(self.key(.64, .8)), tuple(self.key(.64, .97)), tuple(self.key(.36, .97))]
        inner += blob(tp, "#aab1bd", .9)
        if spill > 0:
            # лужа кофе на клавиатуре: растекается от правого края
            pts = []
            for j in range(14):
                a = j / 14 * 2 * math.pi
                rr = 1 + .12 * math.sin(a * 3 + 1) + .08 * math.sin(a * 5)
                fa = .82 - .22 * spill + .3 * spill * rr * math.cos(a)
                fb = .5 + .42 * min(1, spill * 1.3) * rr * math.sin(a)
                pts.append(tuple(self.key(fa, fb)))
            inner += blob(pts, "#5a3220", .95)
            inner += blob([tuple(self.key(.78 - .1 * spill, .35)), tuple(self.key(.86 - .08 * spill, .3)), tuple(self.key(.84 - .08 * spill, .42))], "#9a6440", .9)
        o.append(shape(deck, "#c9ced8", inner, w=3.8, seed=5001))
        o.append(shape([tuple(self.FL) + (1,), tuple(self.FR) + (1,), tuple(self.FR + (0, 8 * k)) + (1,), tuple(self.FL + (0, 8 * k)) + (1,)],
                       "#9aa1ae", "", w=3, seed=5002))
        return "".join(o)

    def glow(self, col="#cfe4ff", a=.3):
        c = (self.TL + self.BR) / 2
        g = lib.rad_grad([(0, col, a), (.45, col, a * .35), (1, col, 0)], c[0] - 60, c[1] + 20, 620, 520)
        return f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{g})" style="mix-blend-mode:screen"/>'


LAP = Laptop(470.0, 1096.0, .8)
PHONE_DESK = (458.0, 1150.0)      # телефон лежит на столе слева от ноутбука
MUG = (754.0, 1104.0, .46)


def text(x, y, s, size, fill="#ffffff", stroke=None, sw=0, extra="", anchor="middle"):
    st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" paint-order="stroke"' if stroke else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" {FONT} font-size="{size}" fill="{fill}"{st} {extra}>{s}</text>'


# ═════════════════════════ экран: отчёт, окно созвона, значки ═════════════════════════
LINE_W = [.92, .78, .88, .64, .9, .72, .84, .5]


def report(x0, x1, n_lines, t, caret=True, errors=0.0, red=0.0, title_k=1.0, clean=False):
    """Страница отчёта в координатах экрана: x0..x1, строки серыми полосками. n_lines — сколько строк (дробное — растёт
    последняя). errors 0..1 — красные волнистые подчёркивания и «опечатки»; red — страница краснеет."""
    o = [shape(rect_pts(x0, 10, x1, 214, 4), mix("#ffffff", "#ffd9d4", red), blob(rect_pts(x0, 10, x1, 22, 4), "#4f7fd0"), w=2.6, seed=7000)]
    o.append(text(x0 + 12, 52, "ОТЧЁТ", 24 * title_k, "#1f3d7a", anchor="start"))
    wmax = x1 - x0 - 26
    full = int(n_lines)
    frac = n_lines - full
    y = 74.0
    cx_, cy_ = x0 + 13, y
    for i in range(min(8, full + 1)):
        w = wmax * LINE_W[i % 8] * (1 if i < full else frac)
        if w < 2:
            break
        o.append(blob(rect_pts(x0 + 13, y - 4, x0 + 13 + w, y + 4, 4), "#9aa6b8"))
        cx_, cy_ = x0 + 13 + w + 4, y
        if errors > 0 and i in (0, 2, 3, 5, 6):
            k = clamp(errors * 2.2 - (0, 2, 3, 5, 6).index(i) * .3)
            if k > 0:
                xs = x0 + 13 + w * (.15 + .1 * (i % 3))
                xe = xs + w * .5 * k
                pts = [(xs + j * 6, y + 9 + 3 * (1 if j % 2 else -1)) for j in range(int((xe - xs) / 6) + 1)]
                if len(pts) > 1:
                    o.append(line(pts, 3.2, "#e2443a", taper=.05, wmin=.9, seed=7100 + i))
                if k > .6 and i in (2, 5):
                    # «опечатка»: красный блок поверх строки
                    o.append(blob(rect_pts(xs + 10, y - 5, xs + 30, y + 5, 3), "#e2443a", .9))
        y += 18
    if caret and not clean and int(t * 2.5) % 2 == 0:
        o.append(blob(rect_pts(cx_, cy_ - 8, cx_ + 3, cy_ + 8), "#1f3d7a"))
    return "".join(o)


def face_tile(x, y, w, h, skin, hair, shirt, t, talk=0.0, confused=0.0, seed=7200):
    """Маленький коллега в окне созвона."""
    o = [blob(rect_pts(x, y, x + w, y + h, 4), "#3b4d73")]
    cx, cy = x + w / 2, y + h * .5
    o.append(shape([(cx - w * .36, y + h), (cx - w * .3, cy + h * .26), (cx + w * .3, cy + h * .26), (cx + w * .36, y + h)], shirt, "", w=2, seed=seed))
    o.append(shape(ellipse_pts(cx, cy, w * .2, h * .27, 12), skin, "", w=2, seed=seed + 1))
    o.append(blob([(cx - w * .22, cy - h * .06), (cx - w * .2, cy - h * .3), (cx, cy - h * .36), (cx + w * .22, cy - h * .28), (cx + w * .22, cy - h * .1),
                   (cx + w * .08, cy - h * .2), (cx - w * .1, cy - h * .18)], hair))
    ey = cy - h * .02
    for sx in (-1, 1):
        o.append(f'<circle cx="{cx + sx * w * .07:.1f}" cy="{ey:.1f}" r="{1.8 + .6 * confused:.1f}" fill="{INK}"/>')
    mo = talk * (.5 + .5 * abs(osc(t, 3.3)))
    if confused > .5:
        o.append(line([(cx - w * .06, cy + h * .14), (cx, cy + h * .11), (cx + w * .06, cy + h * .15)], 1.8, INK, seed=seed + 3))
    else:
        o.append(blob(ellipse_pts(cx, cy + h * .13, w * .05, h * .015 + h * .04 * mo, 8), "#5a2b33"))
    return "".join(o)


def call_panel(x0, y0, t, slide=1.0, talk=1.0, q=0.0, red=0.0):
    """Окно созвона справа на экране: два коллеги, зелёная точка «в эфире»; q — большой «?» поверх."""
    if slide <= 0:
        return ""
    dx = 140 * (1 - slide)
    x0 = x0 + dx
    o = [shape(rect_pts(x0, y0, x0 + 116, y0 + 196, 6), mix("#26324c", "#6a1f26", red), "", w=2.6, seed=7300)]
    o.append(blob(ellipse_pts(x0 + 12, y0 + 12, 4, 4, 8), "#4fd17a"))
    o.append(blob(rect_pts(x0 + 22, y0 + 9, x0 + 70, y0 + 15, 3), "#6f7f9f"))
    o.append(face_tile(x0 + 8, y0 + 24, 100, 76, "#f0c7a4", "#3a2a22", "#5f8fd0", t, talk, q, seed=7310))
    o.append(face_tile(x0 + 8, y0 + 106, 100, 76, "#b98262", "#1c1622", "#d0805f", t + .4, talk * .6, q, seed=7320))
    if red > 0:
        o.append(shape(rect_pts(x0, y0, x0 + 116, y0 + 196, 6), "none", "", w=2.6, seed=7300).replace('fill="none"', 'fill="none"'))
    if q > 0:
        k = lib.back_out(clamp(q), 2.4)
        o.append(f'<g transform="translate({x0 + 58:.1f} {y0 + 110:.1f}) scale({k:.3f}) rotate({8 * osc(t, 2.2):.1f})">'
                 + text(0, 34, "?", 110, "#ffd23a", INK, 8) + "</g>")
    return "".join(o)


def badge(x, y, n, k=1.0):
    if k <= 0:
        return ""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})">' + shape(ellipse_pts(0, 0, 15, 15, 14), "#e2443a", "", w=2.4, seed=7400 + n)
            + text(0, 7, str(n), 20, "#ffffff") + "</g>")


def check_mark(cx, cy, r, k, seed=7500):
    """Большая зелёная галочка в круге (k 0..1 — появление с перелётом, штрих дописывается)."""
    if k <= 0:
        return ""
    s = lib.back_out(clamp(k * 1.6), 2.0)
    o = [f'<g transform="translate({cx:.1f} {cy:.1f}) scale({s:.3f})">']
    o.append(shape(ellipse_pts(0, 0, r, r, 24), "#3aa86b", blob(ellipse_pts(r * .2, r * .22, r * .85, r * .8, 20), "#2f8f5a", .9), w=4, seed=seed))
    u = clamp((k - .1) / .45)
    pts = [(-r * .5, r * .02), (-r * .14, r * .38), (r * .55, -r * .36)]
    if u > 0:
        if u < .4:
            q = u / .4
            pp = [pts[0], tuple(np.array(pts[0]) + (np.array(pts[1]) - np.array(pts[0])) * q)]
        else:
            q = (u - .4) / .6
            pp = [pts[0], pts[1], tuple(np.array(pts[1]) + (np.array(pts[2]) - np.array(pts[1])) * q)]
        o.append(line(pp, r * .3, "#ffffff", taper=.02, wmin=.95, seed=seed + 1))
    o.append("</g>")
    return "".join(o)


# ═════════════════════════ карточки-дела ═════════════════════════
KINDS = ["report", "call", "chat", "mail", "list"]
CARD_COL = {"report": "#4f7fd0", "call": "#3aa86b", "chat": "#9a63c9", "mail": "#e8903a", "list": "#2f9fa8"}


def icon(kind, col):
    o = []
    if kind == "report":
        page = [(-22, -32, 1), (12, -32, 1), (24, -20, 1), (24, 32, 1), (-22, 32, 1)]
        inn = "".join(blob(rect_pts(-14, -16 + j * 11, -14 + (30 if j % 2 == 0 else 22), -12 + j * 11, 2), "#9aa6b8") for j in range(4))
        inn += blob([(12, -32), (24, -20), (12, -20)], "#c9d3e3")
        o.append(shape(page, "#ffffff", inn, w=3, seed=7600))
        o.append(blob(rect_pts(-14, -27, 4, -22, 2), col))
    elif kind == "call":
        arc = [(-24, 8), (-25, -10), (-16, -24), (0, -30), (16, -24), (25, -10), (24, 8)]
        o.append(line(arc, 9, INK, taper=.02, wmin=.95, seed=7610) + line(arc, 4.4, col, taper=.02, wmin=.95, seed=7610))
        for sx in (-1, 1):
            o.append(shape(rect_pts(sx * 24 - 9, 0, sx * 24 + 9, 28, 6), "#30343f", blob(rect_pts(sx * 24 - 4, 4, sx * 24 + 4, 24, 3), col), w=2.6,
                           seed=7611 + sx))
        o.append(line([(-24, 22), (-20, 34), (-6, 36)], 3, INK, seed=7614))
        o.append(shape(ellipse_pts(-3, 36, 5, 4, 8), INK, "", w=1, seed=7615))
    elif kind == "chat":
        b = []
        for i in range(19):
            a = math.radians(-60 + i * 300 / 18)          # без сектора 240..300° (низ-лево) — там хвостик
            b.append((31 * math.cos(a), -4 - 22 * math.sin(a)))
        # от a=240° (низ слева) к a=300° (низ справа): хвостик вниз-влево
        b = b + [(4, 15), (-14, 30, 1), (-10, 14)]
        inn = "".join(blob(ellipse_pts(-12 + j * 12, -4, 4, 4, 8), "#ffffff") for j in range(3))
        o.append(shape(b, col, inn, w=3, seed=7620))
    elif kind == "mail":
        o.append(shape(rect_pts(-30, -20, 30, 22, 3), "#fff6e6", line([(-30, -18), (0, 4), (30, -18)], 3, INK, seed=7631) +
                       line([(-30, 22), (-8, 2)], 2, "#c9b48a", seed=7632) + line([(30, 22), (8, 2)], 2, "#c9b48a", seed=7633), w=3, seed=7630))
        o.append(shape(ellipse_pts(0, 6, 6, 6, 10), col, "", w=2, seed=7634))
    elif kind == "list":
        o.append(shape(rect_pts(-24, -30, 24, 32, 4), "#ffffff", "", w=3, seed=7640))
        o.append(shape(rect_pts(-10, -36, 10, -26, 3), "#9aa1ae", "", w=2.4, seed=7641))
        for j in range(3):
            y = -14 + j * 15
            o.append(shape(rect_pts(-17, y - 5, -7, y + 5, 2), "#ffffff", "", w=2, seed=7642 + j))
            o.append(line([(-15, y), (-12, y + 4), (-5, y - 7)], 3, col, seed=7650 + j, taper=.2, wmin=.6))
            o.append(blob(rect_pts(-1, y - 2, 15, y + 2, 2), "#9aa6b8"))
    return "".join(o)


def card(x, y, s, kind, rot_=0.0, glow=0.0, grey=0.0, seed=0):
    """Карточка-дело 120×104 (центр x, y; масштаб s): белая, цветная кромка, иконка."""
    if s <= 0.01:
        return ""
    col = mix(CARD_COL[kind], "#9aa1ae", grey)
    o = [f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot_:.2f}) scale({s:.4f})">']
    if glow > 0:
        g = lib.rad_grad([(0, "#fff2a8", .9 * glow), (.5, "#ffd23a", .45 * glow), (1, "#ffd23a", 0)], 0, 0, 120, 110)
        o.append(f'<ellipse cx="0" cy="0" rx="120" ry="110" fill="url(#{g})"/>')
    o.append(blob(rect_pts(-56, -46, 64, 60, 14), "#1a100a", .22))
    face = mix("#fffaf0", "#e6e1d6", grey)
    inner = blob(rect_pts(-60, -52, 60, -40, 14), col) + blob(rect_pts(-60, 38, 60, 52, 14), mix(face, "#000000", .07))
    o.append(shape(rect_pts(-60, -52, 60, 52, 14), face, inner, w=4, seed=7700 + seed))
    o.append(f'<g transform="translate(0 4) scale(.95)">{icon(kind, col)}</g>')
    o.append("</g>")
    return "".join(o)


def five(x, y, s, u, seed=7800):
    """Рукописная «5» (дописывается: u 0..1), красный маркер с белым ореолом. (x, y) — центр, высота ~ 150·s."""
    P = [(36, -64, 1), (-26, -62, 1), (-32, -8, 1), (-6, -22), (22, -20), (40, -4), (46, 22), (36, 48), (12, 64), (-14, 64), (-36, 50)]
    P = [(x + p[0] * s, y + p[1] * s) + ((1,) if len(p) > 2 else ()) for p in P]
    S = lib.sample(P, False, 2.0) if hasattr(lib, "sample") else None
    pts = [tuple(p[:2]) for p in S] if S is not None else P
    n = max(2, int(len(pts) * clamp(u)))
    pp = pts[:n]
    if len(pp) < 2:
        return ""
    return (line(pp, 34 * s, "#ffffff", taper=.02, wmin=.95, seed=seed) + line(pp, 22 * s, INK, taper=.02, wmin=.95, seed=seed + 1)
            + line(pp, 14 * s, "#e2443a", taper=.02, wmin=.95, seed=seed + 2))


def speed_lines(cx, cy, r, t, k, n=10, col="#ffffff", seed=7900):
    if k <= 0:
        return ""
    o = []
    for j in range(n):
        a = j * 2 * math.pi / n + t * 3
        r0 = r * (1 + .1 * osc(t, 4, j))
        o.append(line([(cx + r0 * math.cos(a), cy + r0 * .32 * math.sin(a)), (cx + r0 * math.cos(a - .35), cy + r0 * .32 * math.sin(a - .35))], 5 * k,
                      col, taper=.6, wmin=.2, seed=seed + j, op=.85))
    return "".join(o)


def burst(x, y, u, r0=30, r1=70, n=7, col=INK, w=5, seed=8000, rot0=0.0):
    if u <= 0 or u >= 1:
        return ""
    o = []
    for j in range(n):
        a = rot0 + j * 2 * math.pi / n
        a0, a1 = r0 + (r1 - r0) * ease_out(u) * .5, r0 + (r1 - r0) * ease_out(u)
        o.append(line([(x + a0 * math.cos(a), y + a0 * math.sin(a)), (x + a1 * math.cos(a), y + a1 * math.sin(a))], w * (1 - u * .6), col, taper=.3,
                      wmin=.4, seed=seed + j))
    return "".join(o)


def heart(x, y, r, col="#e2443a", seed=6600):
    pts = [(x, y + r * 1.2), (x - r * 1.3, y), (x - r * 1.1, y - r * .9), (x - r * .3, y - r), (x, y - r * .4), (x + r * .3, y - r),
           (x + r * 1.1, y - r * .9), (x + r * 1.3, y)]
    return shape(pts, col, blob(ellipse_pts(x - r * .55, y - r * .45, r * .28, r * .2, 8), "#ffffff", .8), w=3, seed=seed)


# ═════════════════════════ гарнитура ═════════════════════════
def headset(t, mic=1.0, wave=0.0):
    """Гарнитура в единицах головы Димы (head_tf): дуга по макушке, чашка на ухе, микрофон к углу рта."""
    o = []
    band = [(-104, -22), (-110, -70), (-96, -122), (-62, -168), (-14, -192), (36, -186), (78, -160), (100, -122)]
    from lib import band as lband
    pts = lband(band, 26, 22, step=4, cap=True)
    inner = line([(p[0] + 2, p[1] + 7) for p in band[1:-1]], 5, "#1d2028", seed=8101, taper=.2, wmin=.8, op=.9)
    inner += line([(p[0] - 2, p[1] - 6) for p in band[2:-2]], 3, "#8a93a6", seed=8102, taper=.3, wmin=.6, op=.9)
    o.append(shape(pts, "#3c4150", inner, w=4.2, seed=8100))
    # микрофон: штанга от чашки к углу рта
    if mic > 0:
        boom = [(-92, 34), (-70, 82), (-30, 112), (10, 118), (30, 112)]
        o.append(line(boom, 11, INK, taper=.02, wmin=.95, seed=8110) + line(boom, 5.5, "#4a5060", taper=.02, wmin=.95, seed=8110))
        o.append(shape(ellipse_pts(34, 110, 12, 10, 12), "#2b2e38", blob(ellipse_pts(31, 106, 5, 4, 8), "#6a7286"), w=2.8, seed=8111))
    # чашка на ухе
    o.append(shape(ellipse_pts(-108, 10, 40, 50, 18), "#2b2e38", blob(ellipse_pts(-98, 14, 28, 38, 16), "#3c4150") +
                   blob(ellipse_pts(-110, -8, 10, 14, 10), "#6a7286", .8), w=4.4, seed=8120))
    o.append(shape(ellipse_pts(-108, 10, 18, 24, 14), "#4fd17a" if wave > 0 else "#4a5060", "", w=2.6, seed=8121))
    if wave > 0:
        for j in range(3):
            u = (t * 1.8 + j / 3) % 1
            r = 58 + 70 * u
            arc = [(-108 - r * math.cos(a), 10 + r * math.sin(a)) for a in np.linspace(-.7, .7, 9)]
            o.append(line(arc, 7 * (1 - u) + 1.5, "#3aa86b", taper=.4, wmin=.3, seed=8130 + j, op=wave * (1 - u ** 2)))
    return "".join(o)


def headset_flat(x, y, s=1.0, ang=0.0):
    """Гарнитура, лежащая на столе (вид сбоку): дуга и чашка."""
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})">']
    o.append(blob(ellipse_pts(10, 4, 90, 9, 12), "#1a100a", .3))
    arc = [(-70, 0), (-62, -40), (-30, -66), (10, -72), (50, -60), (74, -30), (78, 0)]
    from lib import band as lband
    o.append(shape(lband(arc, 20, 18, step=4, cap=True), "#3c4150", "", w=3.6, seed=8140))
    o.append(shape(rect_pts(-92, -34, -50, 2, 12), "#2b2e38", blob(rect_pts(-86, -28, -58, -4, 8), "#3c4150"), w=3.6, seed=8141))
    o.append(shape(rect_pts(60, -30, 96, 2, 12), "#2b2e38", "", w=3.6, seed=8142))
    o.append("</g>")
    return "".join(o)


# ═════════════════════════ телефон ═════════════════════════
BUB_COL = ["#9a63c9", "#ffffff", "#9a63c9", "#ffffff", "#9a63c9"]


def phone_screen(n, t, w=70, h=130):
    """Экран телефона с пузырями чата (n — сколько показано, дробное — последний выезжает)."""
    o = [blob(rect_pts(-w / 2, -h / 2, w / 2, h / 2, 8), "#e9eef6")]
    o.append(blob(rect_pts(-w / 2, -h / 2, w / 2, -h / 2 + 16, 8), "#9a63c9"))
    full = int(n)
    shown = list(range(min(5, full + 1)))
    # прокрутка: новые снизу, старые уезжают вверх
    yb = h / 2 - 12
    for j in reversed(shown):
        k = 1.0 if j < full else clamp(n - full)
        if k <= 0:
            continue
        left = j % 2 == 0
        bw = w * (.6 if left else .52)
        bh = 18
        x0 = -w / 2 + 6 if left else w / 2 - 6 - bw
        sc = lib.back_out(k, 2)
        cx, cy = x0 + (0 if left else bw), yb - bh / 2
        o.append(f'<g transform="translate({cx:.1f} {cy:.1f}) scale({sc:.3f}) translate({-cx:.1f} {-cy:.1f})">'
                 + blob(rect_pts(x0, yb - bh, x0 + bw, yb, 7), "#b48ae0" if left else "#ffffff")
                 + blob(rect_pts(x0 + 6, yb - bh * .62, x0 + bw * .7, yb - bh * .42, 2), "#ffffff" if left else "#9aa6b8") + "</g>")
        yb -= bh + 6
        if yb < -h / 2 + 22:
            break
    return "".join(o)


def phone_held(x, y, s, ang, n, t):
    """Телефон в руке, экраном к зрителю. (x, y) — центр."""
    w, h = 70, 130
    cid = lib.clip_rect(-w / 2, -h / 2, w, h, 8)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})">']
    o.append(shape(rect_pts(-w / 2 - 7, -h / 2 - 9, w / 2 + 7, h / 2 + 9, 13), "#2b2e38", "", w=3.6, seed=8200))
    o.append(f'<g clip-path="url(#{cid})">{phone_screen(n, t, w, h)}</g>')
    o.append("</g>")
    return "".join(o)


def phone_flat(x, y, k=1.0, face_up=1.0, glow=0.0, lift=0.0, buzz=0.0):
    """Телефон лежит на столе (вид сбоку — тонкая плашка). face_up 1 — экраном вверх (светится), −1 — экраном вниз;
    промежуточные — переворот (плашка встаёт на ребро)."""
    o = []
    bx = 2 * buzz
    o.append(blob(ellipse_pts(x + 4, y + 3, 48 * k, 6 * k, 10), "#1a100a", .3))
    th = 10 * k + 60 * k * (1 - abs(face_up))       # на ребре — видна высота
    yy = y - lift
    body = rect_pts(x - 44 * k + bx, yy - th, x + 44 * k + bx, yy, 4 * k)
    top_col = "#bfd4ff" if face_up > 0 else "#2b2e38"
    inner = blob(rect_pts(x - 44 * k + bx, yy - th, x + 44 * k + bx, yy - th + 4 * k), top_col)
    o.append(shape(body, "#2b2e38", inner, w=3.2, seed=8210))
    if face_up > .5 and glow > 0:
        g = lib.rad_grad([(0, "#cfe0ff", .6 * glow), (1, "#cfe0ff", 0)], x, yy - 14 * k, 70 * k, 40 * k)
        o.append(f'<ellipse cx="{x:.1f}" cy="{yy - 14 * k:.1f}" rx="{70 * k:.1f}" ry="{40 * k:.1f}" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    return "".join(o)


def chat_bubble(x, y, s, left=True, col="#9a63c9", seed=8300):
    if s <= .01:
        return ""
    sg = 1 if left else -1
    b = rect_pts(-34, -18, 34, 18, 14)
    tail = [(-20 * sg, 14), (-30 * sg, 30), (-6 * sg, 16)]
    o = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">']
    o.append(shape(b, col, "".join(blob(ellipse_pts(-14 + j * 14, 0, 4.5, 4.5, 8), "#ffffff" if col != "#ffffff" else "#9a63c9") for j in range(3)), w=3,
                   seed=seed))
    o.append(shape(tail, col, "", w=2.6, seed=seed + 1))
    o.append(blob([(-24 * sg, 12), (-4 * sg, 12), (-8 * sg, 17), (-22 * sg, 17)], col))
    o.append("</g>")
    return "".join(o)


# ═════════════════════════ кружка ═════════════════════════
def mug_tip(x, y, k, ang, fill=1.0, t=0.0):
    """Кружка с кофе, ang — наклон влево вокруг левого нижнего угла (0..90°)."""
    pv = (x - 40 * k, y)
    o = [blob(ellipse_pts(x + 8 * k, y + 2, 56 * k, 10 * k, 12), "#1a100a", .3 * (1 - ang / 90))]
    g = kitchen.mug(x, y, k, 0, col="#c44f3a")
    if ang < 30 and fill > 0:
        g += blob(T(ellipse_pts(0, -126, 44, 7, 14), x, y, k), "#5a3220")
    o.append(f'<g transform="rotate({-ang:.2f} {pv[0]:.2f} {pv[1]:.2f})">{g}</g>')
    return "".join(o)


# ═════════════════════════ комната и свет ═════════════════════════
def room_back(t, warm=False):
    return "".join([den.wall(t, True), den.window(t, True), den.board(t), den.shelf(t), den.clock(300.0 + t * .5, (t * 6) % 360, 0.0, 0.0),
                    den.floor()])


def desk_world(t, d, warm=False, *, on_desk="", mid="", front="", back_extra=""):
    w = [room_back(t, warm), back_extra]
    if warm:
        w.append(den.lamp(t, 1.0))
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


def vignette(col="#3a2a1a", a=.28):
    g = lib.rad_grad([(0, col, 0), (.6, col, 0), (1, col, a)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def compose(world, cam, warm=False, light="", over=""):
    cx, cy, s, r = cam
    set_ink(s)
    if not warm:
        g = lib.rad_grad([(0, "#fff4d0", .35), (1, "#fff4d0", 0)], 200, 500, 1100, 1000)
        tint = f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{g})" style="mix-blend-mode:screen"/>'
        o = ['<rect width="1080" height="1920" fill="#cfe0d6"/>', f'<g transform="{lib.cam(cx, cy, s, r)}">{world}{tint}{light}</g>',
             vignette("#3a2a1a", .26)]
    else:
        g = lib.rad_grad([(0, "#ffd59a", .28), (.55, "#ffc27a", .1), (1, "#ffc27a", 0)], 900, 800, 900, 800)
        warm_l = f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{g})" style="mix-blend-mode:screen"/>'
        mul = '<rect x="-600" y="-600" width="2400" height="3400" fill="#ffbf80" opacity=".42" style="mix-blend-mode:multiply"/>'
        o = ['<rect width="1080" height="1920" fill="#e8d2b0"/>',
             f'<g transform="{lib.cam(cx, cy, s, r)}">{world}{mul}{warm_l}{light}</g>', vignette("#4a2a14", .3)]
    o.append(over)
    return lib.svg("".join(o))


# ═════════════════════════ общая поза за ноутбуком ═════════════════════════
def typing_arms(t, speed=1.0, amp=1.0, far_on=True, near_on=True):
    """Обе руки на клавиатуре, пальцы стучат (запястья подпрыгивают попеременно)."""
    L = LAP
    f = 7.5 * speed
    near = L.key(.36, .62) + np.array([-30, -16]) + np.array([4 * osc(t, f * .23), -7 * amp * max(0, osc(t, f))])
    far = L.key(.2, .42) + np.array([-24, -14]) + np.array([3 * osc(t, f * .19, 1), -6 * amp * max(0, osc(t, f, 2.1))])
    arms = {"n": ("ik", tuple(near), -1), "f": ("ik", tuple(far), -1)}
    hands = {"n": hnd(TYPE, (1, .3)), "f": hnd(TYPE, (1, .25))}
    keys = {(int(1 + (t * f) % 3), int(2 + (t * f * 1.7) % 6)), (int((t * f * 1.3) % 4), int(3 + (t * f * .9) % 5))}
    return arms, hands, keys


# ═════════════════════════ s01: хук — пять карточек влетают, влёт камеры ═════════════════════════
def orbit(t, d, n=5, rx=250.0, ry=62.0, speed=.9, cy_off=-150.0, enter=None, spin=1.0):
    """Позиции пяти карточек на эллипсе вокруг головы: (kind, x, y, s, depth)."""
    hx, hy = d["head"] + np.array([60.0, cy_off])
    out = []
    for j, kind in enumerate(KINDS):
        a = speed * t * spin + j * 2 * math.pi / n + .4
        x = hx + rx * math.cos(a)
        y = hy + ry * math.sin(a)
        depth = math.sin(a)                 # >0 — перед головой
        s = 1.0 + .12 * depth
        out.append([kind, x, y, s, depth, a])
    return out


def cards_svg(cards, t, behind, glow=None, grey=None, scale=None):
    o = []
    order = sorted(range(len(cards)), key=lambda j: cards[j][4])
    for j in order:
        kind, x, y, s, dep, a = cards[j]
        if (dep < 0) != behind:
            continue
        sc = 1.2 * s * (scale[j] if scale else 1.0)
        o.append(card(x, y, sc, kind, rot_=6 * math.cos(a) + 3 * osc(t, 1.1, j), glow=glow[j] if glow else 0, grey=grey[j] if grey else 0, seed=j * 10))
    return "".join(o)


def s01(t):
    # влёт: 1/(1+0.42) → 1.05 за 0.2 с → 1.0; поворот −3° → 0
    u = clamp(t / .2)
    z = lerp(1 / 1.42, 1.05, ease_out(u, 3))
    if t > .2:
        z = 1.0 + .05 * math.exp(-(t - .2) * 9) * math.cos((t - .2) * 14)
    r = -3.0 * (1 - ease_out(clamp(t / .26), 2)) + .4 * osc(t, .7)
    k = clamp(t / 1.7)
    s = 1.68 * z * (1 + .04 * k)
    cam = (400 + 10 * k, 840 - 10 * k, s, r)
    expr = dict(lid=.52, look=(-.25, .05), brows="up", mouth="smile", smile=1.0, closed=blink_at(t, 1.05, .14),
                hair=3 * bump(t, .0, .3) + 2 * osc(t, 2.1))
    arms, hands, keys = typing_arms(t, .7, .6)
    # ухмыляется: откинулся, руки на клавиатуре, лёгкий кивок
    d = dima(t, arms, hands, expr, lean=.08 + .02 * osc(t, .9), head_ang=-.04 + .03 * osc(t, 1.4))
    cards = orbit(t, d, rx=225, ry=52, speed=.9, cy_off=-270)
    # влёт карточек с краёв кадра: у каждой своя задержка, первая уже летит в кадре 0
    src = [(-520, -260), (640, -420), (-560, 260), (620, 120), (40, -700)]
    for j, c in enumerate(cards):
        tj = -.08 + j * .12
        v = clamp((t - tj) / .42)
        e = ease_out(v, 3)
        c[1] = c[1] + src[j][0] * (1 - e)
        c[2] = c[2] + src[j][1] * (1 - e)
        c[3] = c[3] * (.55 + .45 * lib.back_out(v, 1.8)) if v < 1 else c[3]
        if v <= 0:
            c[3] = 0
    behind = cards_svg(cards, t, True)
    front = cards_svg(cards, t, False)
    # хвосты-штрихи за летящими карточками
    trails = ""
    for j, c in enumerate(cards):
        tj = -.08 + j * .12
        v = clamp((t - tj) / .42)
        if 0 < v < .85:
            dx, dy = src[j]
            L = math.hypot(dx, dy)
            for q in range(3):
                off = (q - 1) * 26
                px, py = c[1] - dy / L * off, c[2] + dx / L * off
                a0 = 70 + 40 * v
                trails += line([(px + dx / L * a0, py + dy / L * a0), (px + dx / L * (a0 + 90 * (1 - v)), py + dy / L * (a0 + 90 * (1 - v)))], 6, "#ffffff",
                               taper=.4, wmin=.3, seed=8400 + j * 3 + q, op=.9 * (1 - v))
    lap = LAP.draw(report(14, 286, 3.2 + 1.5 * clamp(t / 1.7), t), press=(keys, .8))
    on_desk = lap + phone_flat(*PHONE_DESK, .9, 1.0, .5) + mug_tip(*MUG, 0)
    w = desk_world(t, d, on_desk=on_desk, back_extra=behind, front=front + trails)
    return compose(w, cam, False, LAP.glow())


# ═════════════════════════ s02: крупнее, карточки кружат, «5», подмигнул ═════════════════════════
def s02(t):
    tp, ts = T_PYAT, T_SRAZU
    k = clamp((t - 1.3) / 2.34)
    hit = punch(t, tp, .07, .05, .35) + punch(t, ts, .04, .05, .3)
    s = (1.72 + .16 * ease_io(k)) * (1 + hit)
    cam = (370 + 10 * k, 760 + 8 * k + 10 * bump(t, tp, .3) * osc(t, 11), s, .8 - .8 * k + .9 * bump(t, tp, .3) * osc(t, 9))
    fast = smooth(ts - .05, ts + .25, t)
    # фаза орбиты: ускорение после «сразу» (интеграл скорости)
    ph = .9 * t + 2.4 * max(0.0, t - ts) * fast
    wink = smooth(ts + .05, ts + .14, t) * (1 - smooth(3.45, 3.55, t))
    expr = dict(lid=.55, look=(-.3, -.05 - .3 * bump(t, tp - .05, .4)), brows="up", mouth="smile", smile=1.0, wink=wink,
                closed=blink_at(t, 1.62, .14), hair=4 * bump(t, tp, .3) + 2 * osc(t, 2.1))
    if t > ts:
        expr["mouth"] = "grin"
        expr["open"] = .35
    arms, hands, keys = typing_arms(t, .8, .6)
    d = dima(t, arms, hands, expr, lean=.08 + .02 * osc(t, .9), head_ang=-.05 + .03 * osc(t, 1.4) - .05 * fast)
    cards = orbit(0, d, rx=215, ry=52, speed=1, cy_off=-265)
    hx, hy = d["head"] + np.array([60.0, -265.0])
    for j, c in enumerate(cards):
        a = ph + j * 2 * math.pi / 5 + .4 + .9 * 1.3      # продолжает орбиту s01
        c[1] = hx + 215 * math.cos(a)
        c[2] = hy + 52 * math.sin(a) + 4 * osc(t, 1.7, j)
        c[4] = math.sin(a)
        c[3] = (1.0 + .12 * c[4]) * (1 + .1 * bump(t, tp + j * .03, .3))
        c[5] = a
    behind = cards_svg(cards, t, True)
    front = cards_svg(cards, t, False)
    hd = d["head"]
    fx, fy = hd[0] + 60, hd[1] - 420
    f5 = ""
    if t > tp - .05:
        u = clamp((t - tp + .05) / .3)
        sc = .9 * lib.back_out(clamp((t - tp + .05) / .28), 2.6)
        f5 = five(fx, fy + 8 * osc(t, 1.6), max(.01, sc), u)
        f5 += burst(fx, fy, clamp((t - tp) / .4), 100, 150, 8, "#e2443a", 6, seed=8500)
    sl = speed_lines(hx, hy, 215, t, fast, n=12)
    lap = LAP.draw(report(14, 286, 4.7 + 1.0 * k, t), press=(keys, .8))
    on_desk = lap + phone_flat(*PHONE_DESK, .9, 1.0, .5) + mug_tip(*MUG, 0)
    w = desk_world(t, d, on_desk=on_desk, back_extra=behind, front=sl + front + f5)
    return compose(w, cam, False, LAP.glow())


# ═════════════════════════ s05: печатает отчёт, гарнитура ═════════════════════════
def s05(t):
    to = T_OTCHET
    k = ease_io(clamp((t - 6.52) / 2.04))
    hit = punch(t, to, .05, .05, .3)
    s = (1.84 + .1 * k) * (1 + hit)
    cam = (485 - 25 * k, 975 - 10 * k, s, -.6 + .9 * k)
    arms, hands, keys = typing_arms(t, 1.0, 1.0)
    expr = dict(lid=.6, look=(.75, .4), brows="det", mouth="flat", closed=blink_at(t, 7.9, .14), hair=2 * osc(t, 2.3) + 3 * bump(t, to, .3))
    d = dima(t, arms, hands, expr, lean=.2 + .01 * osc(t, 3), head_ang=.02 * osc(t, 1.1))
    # строки растут: на «отчёт» — рывок
    n = 2.2 + .6 * (t - 6.52) + 1.6 * smooth(to - .05, to + .25, t)
    scr = report(14, 286, n, t, title_k=1 + .25 * bump(t, to, .35))
    lap = LAP.draw(scr, press=(keys, .9))
    hs = f'<g transform="{head_tf(d)}">{headset(t, 1.0, 0.0)}</g>'
    # штрихи стука по клавишам
    tap = ""
    for j in range(2):
        u = ((t * 3.1 + j * .5) % 1)
        p = LAP.key(.3 + .3 * j, .3) + np.array([0, -30])
        tap += burst(p[0], p[1], u, 18, 40, 3, INK, 4, seed=8600 + j * 5, rot0=-2.4)
    on_desk = lap + phone_flat(*PHONE_DESK, .9, 1.0, .4) + mug_tip(*MUG, 0)
    w = desk_world(t, d, on_desk=on_desk, mid=hs)
    return compose(w, cam, False, LAP.glow())


# ═════════════════════════ s06: созвон (волны, окно с коллегами), телефон и пузыри, глаза бегают ═════════════════════════
def s06(t):
    tz, tp = T_SOZVON, T_PEREP
    k = ease_io(clamp((t - 8.16) / 2.68))
    shake = sum(bump(t, tp + .25 + j * .32, .22) for j in range(4))
    s = (1.78 + .3 * k) * (1 + punch(t, tz, .05, .05, .3) + punch(t, tp + .2, .03, .05, .25))
    cam = (470 - 40 * k + 5 * shake * osc(t, 13), 975 - 20 * k + 4 * shake * osc(t, 11, 1), s, .3 - .6 * k + .8 * shake * osc(t, 9))
    # руки: обе печатают; на «переписывается» ближняя хватает телефон и поднимает к лицу
    arms, hands, keys = typing_arms(t, 1.1, 1.0)
    grab = smooth(tp - .2, tp + .05, t)
    lift = smooth(tp + .05, tp + .35, t)
    ph_desk = np.array(PHONE_DESK) + np.array([0, -14])
    ph_up = np.array([462.0, 1022.0])
    ph = ph_desk + (ph_up - ph_desk) * ease_out(lift, 2)
    if grab > 0:
        near_t = arms["n"][1]
        tgt = ph + np.array([-6, 26]) + np.array([2, 46]) * lift
        p = np.array(near_t) + (tgt - np.array(near_t)) * grab if lift <= 0 else tgt
        arms["n"] = ("ik", tuple(p), -1)
        hands["n"] = hnd(GRIP, (lerp(1, .1, lift), lerp(.3, -1, lift)))
    # глаза бегают: экран ↔ телефон
    if t < tp:
        look = (.75, .35)
    else:
        sw = osc(t, 1.6)
        look = (lerp(.75, -.2, (sw + 1) / 2) if sw * sw > .5 else .3, lerp(.35, .6, (sw + 1) / 2))
    expr = dict(lid=.75 + .15 * bump(t, tz, .4), look=look, brows="up" if t > tz else "det", mouth="flat" if t < tp else "talk", open=.3, smile=.2,
                closed=blink_at(t, 8.6, .14), hair=2 * osc(t, 2.3) + 3 * bump(t, tz, .3) + 3 * bump(t, tp, .3))
    d = dima(t, arms, hands, expr, lean=.2, head_ang=.03 * osc(t, 1.6) * (t > tp) - .02 * lift)
    wave = smooth(tz - .05, tz + .15, t)
    hs = f'<g transform="{head_tf(d)}">{headset(t, 1.0, wave)}</g>'
    slide = ease_out(clamp((t - tz) / .35), 3)
    n_rep = 3.0 + .5 * (t - 8.16)
    scr = report(14, 170 if slide > 0 else 286, n_rep, t) + call_panel(178, 12, t, slide, 1.0)
    lap = LAP.draw(scr, press=(keys, .9))
    # телефон: лежит → в руке экраном к зрителю, пузыри вылезают один за другим
    n_b = clamp((t - tp - .2) / 1.5) * 5
    phone_on = ""
    phone_in_hand = ""
    if lift < .02:
        phone_on = phone_flat(*PHONE_DESK, .9, 1.0, .6, buzz=osc(t, 30) * smooth(tp - .4, tp - .2, t))
    else:
        ang = lerp(80, -8, lift)
        phone_in_hand = phone_held(ph[0], ph[1], lerp(.5, .95, lift), ang, n_b, t)
        # большой палец по краю телефона
        tp_ = ph + np.array([-36, 30]) * lerp(.5, .95, lift)
        phone_in_hand += shape(T(ellipse_pts(0, 0, 9, 17, 12), tp_[0], tp_[1], 1, 20 + 60 * (1 - lift)), people.PAL["dima"]["SKIN"],
                               blob(T(ellipse_pts(2, -8, 5, 6, 8), tp_[0], tp_[1], 1, 20), people.PAL["dima"]["NAIL"]), w=3, seed=8230)
    bubbles = ""
    for j in range(4):
        tj = tp + .3 + j * .32
        u = clamp((t - tj) / .9)
        if u <= 0:
            continue
        sc = lib.back_out(clamp(u * 3), 2.2) * (1 - smooth(.85, 1, u))
        bx = ph[0] + (-110 if j % 2 == 0 else 60) + 10 * j
        by = ph[1] - 120 - 150 * ease_out(u, 2) - 20 * j
        bubbles += chat_bubble(bx, by, sc * 1.05, left=j % 2 == 0, col="#9a63c9" if j % 2 == 0 else "#ffffff", seed=8700 + j * 3)
    on_desk = lap + phone_on + mug_tip(*MUG, 0)
    # телефон в руке: перед телом, под пальцами ближней руки
    w = desk_world(t, d, on_desk=on_desk, mid=hs, front=phone_in_hand + bubbles)
    return compose(w, cam, False, LAP.glow())


# ═════════════════════════ s10: всё сразу — ошибки, «?», кружка на «хуже», за голову ═════════════════════════
def s10(t):
    to, th = T_OBE, T_HUZHE
    k = ease_io(clamp((t - 16.8) / 3.36))
    sh = bump(t, th + .05, .5)
    s = (1.58 + .08 * k) * (1 + punch(t, to, .05, .05, .3) + punch(t, th, .07, .05, .4))
    cam = (500 - 20 * k + 9 * sh * osc(t, 13), 985 - 10 * k + 7 * sh * osc(t, 11, 1), s, .4 - .7 * k + 1.6 * sh * osc(t, 9))
    grab = smooth(th + .02, th + .22, t)
    arms, hands, keys = typing_arms(t, 1.5, 1.2)
    # за голову: обе руки к вискам
    probe = dima(t, arms, hands, {}, lean=.2)
    if grab > 0:
        # ближняя рука — на затылок (локоть вверх-назад, лицо открыто), дальняя — на макушку спереди
        hn = head_pt(probe, (-175, -150))
        hf = head_pt(probe, (60, -235))
        na = np.array(arms["n"][1])
        fa = np.array(arms["f"][1])
        arms = {"n": ("ik", tuple(na + (hn - na) * grab), 1 if grab > .3 else -1), "f": ("ik", tuple(fa + (hf - fa) * grab), -1)}
        hands = {"n": hnd(CLAW, tuple(np.array([1, .3]) + (np.array([.75, .55]) - np.array([1, .3])) * grab)),
                 "f": hnd(CLAW, tuple(np.array([1, .25]) + (np.array([-.5, .85]) - np.array([1, .25])) * grab))}
    sw = osc(t, 2.2)
    look = (lerp(.75, -.3, (sw + 1) / 2), .4) if t < th else (.0, -.2)
    expr = dict(lid=.85 if t < to else 1.0, look=look, brows="up" if t < to else "worry", mouth="flat" if t < to else "talk",
                open=.25 + .5 * grab, smile=0, closed=blink_at(t, 17.3, .14), hair=3 * osc(t, 2.7) + 6 * bump(t, th, .35), blush=.0)
    d = dima(t, arms, hands, expr, lean=.2 + .03 * grab, head_ang=.03 * sw * (1 - grab) - .06 * grab)
    hs = f'<g transform="{head_tf(d)}">{headset(t, 1.0, 1.0)}</g>'
    err = clamp((t - 17.1) / .9) + .0
    red = smooth(to - .02, to + .2, t)
    scr = report(14, 170, 5.5, t, errors=err, red=.35 * red) + call_panel(178, 12, t, 1.0, .4, q=clamp((t - 17.3) / .3), red=red)
    if red > 0:
        scr += f'<rect x="0" y="0" width="300" height="220" fill="none" stroke="#e2443a" stroke-width="{8 * red:.1f}"/>'
    # кружка: на «хуже» опрокидывается влево на клавиатуру
    tip = ease_in(clamp((th - .08 - t) * -1 / .28), 1.6) if t > th - .08 else 0.0
    if t > th + .2:
        tip = 1 + .05 * math.exp(-(t - th - .2) * 10) * math.sin((t - th - .2) * 40)
    spill = clamp((t - th - .05) / .45)
    lap = LAP.draw(scr, press=(keys if grab < .5 else set(), .9), spill=spill)
    mug = mug_tip(*MUG, 92 * tip, fill=1.0, t=t)
    splash = ""
    if t > th + .05:
        # капли кофе вылетают из горлышка кружки влево-вниз на клавиатуру, каждая по своей дуге
        mx, my = MUG[0] - 40 * MUG[2] - 110 * MUG[2], 1080
        for j in range(6):
            tj = th + .05 + j * .035
            u = clamp((t - tj) / .42)
            if u <= 0 or u >= 1:
                continue
            vx = -(120 + 45 * j)
            vy = -(160 - 25 * j)
            x = mx + vx * u * .42
            y = my + vy * u * .42 + 900 * (u * .42) ** 2
            rr = 7 + 3 * (j % 3)
            splash += shape([(x - rr * .9, y), (x, y - rr * 1.5), (x + rr * .9, y), (x, y + rr)], "#6a3a22",
                            blob(ellipse_pts(x - rr * .3, y - rr * .3, rr * .25, rr * .25, 6), "#b07a52"), w=2.2, seed=8800 + j)
        splash += burst(mx + 10, my + 10, clamp((t - th - .05) / .4), 40, 100, 7, INK, 5, seed=8820)
    phone = phone_flat(*PHONE_DESK, .9, 1.0, .8, buzz=osc(t, 30) * (bump(t, 17.4, .4) + bump(t, 18.5, .4)))
    bubbles = ""
    for j in range(3):
        tj = 17.0 + j * .6
        u = clamp((t - tj) / .8)
        if 0 < u < 1:
            sc = lib.back_out(clamp(u * 3), 2.2) * (1 - smooth(.8, 1, u))
            bubbles += chat_bubble(PHONE_DESK[0] - 40 + 50 * j, PHONE_DESK[1] - 90 - 120 * ease_out(u, 2), sc * .9, left=j % 2 == 0,
                                   col="#9a63c9" if j % 2 == 0 else "#ffffff", seed=8900 + j * 3)
    # пот
    swt = ""
    if t > to:
        x, y = head_pt(d, (112, -96))
        u = clamp((t - to - .1) / .7)
        yy = y + 50 * ease_in(u)
        r = 12 * min(1, u * 3)
        if r > 0:
            drop = [(x, yy - r * 2.2), (x + r, yy - r * .1), (x + r * .8, yy + r * .7), (x, yy + r), (x - r * .8, yy + r * .7), (x - r, yy - r * .1)]
            swt = shape(drop, "#bfe6fa", blob([(x - r * .4, yy - r * .6), (x - r * .1, yy - r * .9), (x - r * .1, yy - r * .2)], "#ffffff"), w=3, seed=8950)
    on_desk = lap + phone + mug + splash
    w = desk_world(t, d, on_desk=on_desk, mid=hs, front=bubbles + swt)
    return compose(w, cam, False, LAP.glow("#ffd0c8" if red > .5 else "#cfe4ff", .3))


# ═════════════════════════ s14: спокойный тёплый свет, одна карточка загорается ═════════════════════════
def s14(t):
    to = T_ODNO
    k = ease_io(clamp((t - 24.48) / 2.42))
    s = (1.62 + .14 * k) * (1 + punch(t, to, .04, .05, .35))
    cam = (420 + 10 * k, 860 + 20 * k, s, -.5 + .7 * k)
    arms, hands, keys = typing_arms(t, .55, .5)
    expr = dict(lid=.55, look=(.7, .35), brows="calm", mouth="smile", smile=.3, closed=blink_at(t, 25.3, .16) + blink_at(t, 26.55, .16),
                hair=1.5 * osc(t, 1.3))
    if t > to:
        expr["look"] = (.2, -.7 * (1 - smooth(to + .6, to + 1.0, t)) + .35 * smooth(to + .6, to + 1.0, t))
    d = dima(t, arms, hands, expr, lean=.16 + .01 * osc(t, .8), head_ang=.015 * osc(t, .7))
    hs = f'<g transform="{head_tf(d)}">{headset(t, 1.0, 0.0)}</g>'
    hx, hy = d["head"] + np.array([110.0, -240.0])
    # пять карточек полукругом над головой, тихо покачиваются; на «одно» отчёт загорается и растёт, остальные лопаются
    sel = smooth(to - .02, to + .2, t)
    cards, glow, scale = [], [], []
    for j, kind in enumerate(KINDS):
        a = math.radians(-160 + [2, 0, 1, 3, 4][j] * 35)
        x = hx + 230 * math.cos(a) + 6 * osc(t, .6, j)
        y = hy + 90 * math.sin(a) + 50 + 6 * osc(t, .5, j * 2)
        if kind == "report":
            x = lerp(x, hx - 40, ease_io(sel))
            y = lerp(y, hy - 20, ease_io(sel))
            sc = .85 + .35 * lib.back_out(sel, 2)
            glow.append(sel)
        else:
            u = clamp((t - to - .05 - .06 * j) / .18)
            sc = .85 * (1 + .25 * math.sin(math.pi * u)) * (1 - ease_in(u, 2)) if u < 1 else 0
            glow.append(0)
        cards.append([kind, x, y, 1.0, 1.0, a])
        scale.append(sc)
    grey = [0 if KINDS[j] == "report" else .5 for j in range(5)]
    cs = cards_svg(cards, t, False, glow=glow, grey=grey, scale=scale)
    for j, kind in enumerate(KINDS):
        if kind != "report":
            u = clamp((t - to - .05 - .06 * j) / .18)
            v = clamp((t - to - .05 - .06 * j - .15) / .35)
            if 0 < v < 1:
                cs += burst(cards[j][1], cards[j][2], v, 20, 60, 6, "#9aa1ae", 4, seed=9000 + j * 7)
    rays = ""
    if sel > 0:
        for j in range(10):
            a = j * math.pi / 5 + t * .4
            r0, r1 = 105, 135 + 20 * sel + 6 * osc(t, 3, j)
            rays += line([(hx + r0 * math.cos(a), hy - 20 + r0 * math.sin(a)), (hx + r1 * math.cos(a), hy - 20 + r1 * math.sin(a))], 7, "#ffd23a",
                         taper=.4, wmin=.4, seed=9100 + j, op=sel)
    scr = report(14, 286, 4.0 + .3 * (t - 24.48), t)
    lap = LAP.draw(scr, press=(keys, .6))
    ph = phone_flat(*PHONE_DESK, .9, 1.0, .7)
    bub = chat_bubble(PHONE_DESK[0] + 10, PHONE_DESK[1] - 70 - 6 * osc(t, 1.2), .7 * (1 - smooth(to, to + .2, t)), True, seed=9200)
    badges = badge(*LAP.P(282, 18), 3, 1 - smooth(to, to + .2, t)) if False else ""
    on_desk = lap + ph + mug_tip(*MUG_W, 0) + badges
    w = desk_world(t, d, True, on_desk=on_desk, mid=hs, front=rays + cs)
    return compose(w, cam, True, LAP.glow("#ffe2b8", .25))


# ═════════════════════════ s15: снимает гарнитуру, телефон экраном вниз, уведомления гаснут ═════════════════════════
HS_DESK = (792.0, 1116.0)
MUG_W = (884.0, 1104.0, .46)


def s15(t):
    tv, tr = T_VYKL, T_OSTAL
    k = ease_io(clamp((t - 26.5) / 2.22))
    s = (1.72 + .06 * k) * (1 + punch(t, tv, .04, .05, .3) + punch(t, tr, .05, .05, .35))
    cam = (480 + 10 * k, 955 - 8 * k, s, .4 - .6 * k)
    t_up, t_grab, t_lift, t_put = tv - .1, tv + .08, tv + .3, tv + .62
    # дальняя рука снимает гарнитуру и кладёт на стол; ближняя переворачивает телефон экраном вниз
    arms, hands, keys = typing_arms(t, .5, .4)
    probe = dima(t, arms, hands, {}, lean=.16)
    grab_local = np.array([-14.0, -196.0])
    grab_w = head_pt(probe, grab_local)
    hd_g = np.array([.15, .98])
    wr_grab = grab_w - hd_g / np.linalg.norm(hd_g) * 60 * BS
    lift_off = np.array([30.0, -60.0])
    far0 = np.array(arms["f"][1])
    hs_state = "head"
    if t < t_up:
        pass
    elif t < t_grab:
        u = ease_io(clamp((t - t_up) / (t_grab - t_up)))
        arms["f"] = ("ik", tuple(far0 + (wr_grab - far0) * u), -1)
        hands["f"] = hnd(REST, (lerp(1, .15, u), lerp(.25, .98, u)))
    elif t < t_lift:
        u = ease_io(clamp((t - t_grab) / (t_lift - t_grab)))
        arms["f"] = ("ik", tuple(wr_grab + lift_off * u), -1)
        hands["f"] = hnd(FIST, (.15, .98))
        hs_state = "lift"
    else:
        hs_state = "fly" if t < t_put else "desk"
        u = ease_io(clamp((t - t_lift) / .3))
        back = far0 + np.array([0, -6])
        arms["f"] = ("ik", tuple(wr_grab + lift_off + (back - wr_grab - lift_off) * u), -1)
        hands["f"] = hnd(REST, (lerp(.15, 1, u), lerp(.98, .25, u)))
    # ближняя рука к телефону: 26.95 → переворот 27.15–27.35 → назад к 27.6
    pa, pb, pc = tv + .12, tv + .32, tv + .58
    near0 = np.array(arms["n"][1])
    ph_hand = np.array(PHONE_DESK) + np.array([-20, -40])
    flip = 1.0
    lift_ph = 0.0
    if pa < t < pc + .3:
        go = smooth(pa - .15, pa + .05, t) * (1 - smooth(pc, pc + .3, t))
        arms["n"] = ("ik", tuple(near0 + (ph_hand - near0) * go), -1)
        hands["n"] = hnd(GRIP, (lerp(1, .5, go), lerp(.3, .9, go)))
        fu = smooth(pa + .05, pb, t)
        flip = math.cos(math.pi * fu)
        lift_ph = 22 * math.sin(math.pi * fu)
    elif t >= pc + .3:
        flip = -1.0
    expr = dict(lid=.6, look=(.5, .1) if t < tv else ((.6, -.6) if t < t_lift else (.2, .5)), brows="calm", mouth="smile", smile=.4 + .4 * smooth(tr, tr + .3, t),
                closed=blink_at(t, 26.62, .14) + blink_at(t, 28.1, .16), hair=2 * bump(t, t_lift, .35) + 1.5 * osc(t, 1.3))
    d = dima(t, arms, hands, expr, lean=.16, head_ang=-.04 * bump(t, t_lift, .35) + .015 * osc(t, .9))
    head_hs = ""
    fly_hs = ""
    desk_hs = ""
    wave = 1.0 - smooth(t_grab, t_grab + .1, t)
    if hs_state == "head":
        head_hs = f'<g transform="{head_tf(d)}">{headset(t, 1.0, wave * .8)}</g>'
    elif hs_state == "lift":
        u = ease_io(clamp((t - t_grab) / (t_lift - t_grab)))
        off = lift_off * u
        head_hs = f'<g transform="translate({off[0]:.2f} {off[1]:.2f})"><g transform="{head_tf(d)}">{headset(t, 1.0, 0)}</g></g>'
    elif hs_state == "fly":
        u = clamp((t - t_lift) / (t_put - t_lift))
        p0 = head_pt(d, grab_local) + lift_off
        p1 = np.array([HS_DESK[0], HS_DESK[1] - 60])
        x = lerp(p0[0], p1[0], ease_io(u))
        y = lerp(p0[1], p1[1], ease_in(u, 1.4)) - 110 * math.sin(math.pi * u)
        ang = math.degrees(d["hang"]) + 70 * ease_io(u)
        fly_hs = (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({BS:.3f}) translate({-grab_local[0]:.1f} {-grab_local[1]:.1f})">'
                  f'{headset(t, 1.0, 0)}</g>')
    else:
        e = t - t_put
        wob = 5 * math.exp(-8 * e) * math.sin(e * 34)
        desk_hs = headset_flat(HS_DESK[0], HS_DESK[1], .62, wob)
        desk_hs += burst(HS_DESK[0], HS_DESK[1] - 30, clamp(e / .3), 40, 80, 5, INK, 4, seed=9300, rot0=-2.6)
    # пузыри над телефоном лопаются при перевороте
    bub = ""
    pop_t = pa + .1
    for j in range(3):
        bx, by = PHONE_DESK[0] - 50 + 55 * j, PHONE_DESK[1] - 110 - 40 * (j % 2) + 6 * osc(t, 1.2, j)
        if t < pop_t + j * .05:
            bub += chat_bubble(bx, by, .75, j % 2 == 0, "#9a63c9" if j % 2 == 0 else "#ffffff", seed=9400 + j * 3)
        else:
            u = clamp((t - pop_t - j * .05) / .25)
            bub += burst(bx, by, u, 10, 50, 8, "#9a63c9", 4, seed=9420 + j * 9)
    # уведомления на экране: значки; на «остальное» щелчок — гаснут
    off_k = 1 - smooth(tr, tr + .08, t)
    scr = report(14, 286 if t > tr else 170, 5.0, t) + (call_panel(178, 12, t, 1.0 - smooth(tr - .02, tr + .18, t), .6) if t < tr + .2 else "")
    scr += badge(286, 196, 3, off_k * (1 + .15 * osc(t, 3))) + badge(150, 196, 5, off_k * (1 + .15 * osc(t, 3, 1)))
    if t > tr:
        u = clamp((t - tr) / .35)
        scr += burst(286, 196, u, 10, 50, 7, "#e2443a", 4, seed=9500) + burst(150, 196, u, 10, 50, 7, "#e2443a", 4, seed=9510)
    lap = LAP.draw(scr, press=(keys, .5))
    ph = phone_flat(PHONE_DESK[0], PHONE_DESK[1], .9, flip, .7 if flip > 0 else 0, lift=lift_ph)
    click = burst(*LAP.P(150, 110), clamp((t - tr) / .4), 160, 230, 10, "#ffd23a", 7, seed=9520) if t > tr else ""
    on_desk = lap + ph + mug_tip(*MUG_W, 0) + desk_hs
    w = desk_world(t, d, True, on_desk=on_desk, mid=head_hs, front=fly_hs + bub + click)
    return compose(w, cam, True, LAP.glow("#ffe2b8", .25))


# ═════════════════════════ s16: крупно экран, отчёт ровный, галочка на «ошибок» ═════════════════════════
def s16(t):
    te = T_OSHIBOK
    k = ease_io(clamp((t - 28.32) / 1.88))
    s = (2.4 + .12 * k) * (1 + punch(t, te, .06, .05, .35))
    back = smooth(te + .1, te + .6, t)
    pan = ease_io(clamp((t - te - .15) / .7))
    cam = (565 - 95 * pan, 985 - 25 * pan + 6 * bump(t, te, .3) * osc(t, 11), s, -.4 + .6 * k + .8 * bump(t, te, .3) * osc(t, 9))
    arms, hands, keys = typing_arms(t, .6, .4)
    if back > 0:
        n0, f0 = np.array(arms["n"][1]), np.array(arms["f"][1])
        arms = {"n": ("ik", tuple(n0 + (np.array([330.0, 1110.0]) - n0) * back), -1), "f": ("ik", tuple(f0 + (np.array([300.0, 1100.0]) - f0) * back), -1)}
        hands = {"n": hnd(REST, (1, .5)), "f": hnd(REST, (1, .5))}
    expr = dict(lid=.6, look=(.7, .35), brows="calm", mouth="smile", smile=.5 + .5 * back, closed=blink_at(t, 28.6, .14), hair=1.5 * osc(t, 1.2))
    d = dima(t, arms, hands, expr, lean=.16 - .2 * back, head_ang=.02 * osc(t, .8) - .04 * back)
    scr = report(14, 286, 7.0, t, caret=t < te, clean=True)
    ck = clamp((t - te + .04) / .45)
    scr += check_mark(214, 132, 62, ck)
    if t > te:
        scr += burst(214, 132, clamp((t - te) / .45), 70, 110, 9, "#3aa86b", 6, seed=9600)
    lap = LAP.draw(scr, press=(keys if back < .3 else set(), .5))
    on_desk = lap + phone_flat(*PHONE_DESK, .9, -1.0, 0) + mug_tip(*MUG_W, 0) + headset_flat(HS_DESK[0], HS_DESK[1], .62, 0)
    w = desk_world(t, d, True, on_desk=on_desk)
    return compose(w, cam, True, LAP.glow("#d8ffe0", .25 * ck))


# ═════════════════════════ s17: кот на столе, Дима гладит, сердечки на «внимание» ═════════════════════════
CAT_X, CAT_Y, CAT_S = 520.0, 1126.0, .66


def s17(t):
    tk, tv = T_KOT, T_VNIM
    k = ease_io(clamp((t - 29.8) / 2.92))
    t_land = 30.12
    land = punch(t, t_land, .035, .04, .3)
    s = (1.62 + .1 * k) * (1 + land + punch(t, tv, .03, .05, .35))
    cam = (470 + 10 * k, 985 - 10 * k, s, .3 - .5 * k)
    # кот: прыжок справа-снизу (уже в воздухе в кадре 0) → приземление на стол, присед, дальше сидит и жмурится
    u = clamp((t - 29.62) / (t_land - 29.62))
    up = 0.0
    sq = 0.0
    if u < 1:
        x = lerp(1010, CAT_X, ease_out(u, 1.4))
        y = lerp(1340, CAT_Y, u) - 230 * math.sin(math.pi * u) * (1 - u * .25)
        tilt_b = lerp(-26, 0, u)
        up = .3 * math.sin(math.pi * u)
    else:
        x, y, tilt_b = CAT_X, CAT_Y, 0.0
        e = t - t_land
        sq = .12 * math.exp(-e * 9) * math.cos(e * 22)
    happy = smooth(30.55, 30.75, t)
    stroke = smooth(30.35, 30.6, t)
    ph = (t - 30.35) * 1.25
    sw = (math.sin(ph * 2 * math.pi) + 1) / 2 * stroke          # 0 — у головы, 1 — на спине
    tilt = (-6 * stroke + 4 * sw) if u >= 1 else 0
    cat_svg = cat2.draw(x, y, CAT_S * (1 + .02 * osc(t, .4)), t, up=up, look=(-.5, -.2) if happy < .5 else (0, 0), blink=0.0, tilt=tilt + tilt_b,
                        tail=6 * osc(t, 1.1) + 10 * (1 - u), happy=happy)
    if u < 1:
        cat_svg = f'<g transform="rotate({-24 * math.sin(math.pi * u):.2f} {x:.1f} {y - 90:.1f})">{cat_svg}</g>'
    if sq:
        cat_svg = f'<g transform="translate({x:.1f} {y:.1f}) scale({1 + sq:.3f} {1 - sq:.3f}) translate({-x:.1f} {-y:.1f})">{cat_svg}</g>'
    # рука гладит: от затылка вдоль спины
    head_w = np.array(cat.to_world((836, 1040), x, y, CAT_S))
    back_w = np.array(cat.to_world((900, 1170), x, y, CAT_S))
    top_w = np.array(cat.to_world((836, 975), x, y, CAT_S))
    p_hand = top_w + np.array([-78 + 46 * sw, 8 + 6 * sw])
    arms, hands, keys = typing_arms(t, .4, .3)
    arms["f"] = ("ik", (340.0, 1150.0 + 2 * osc(t, .9)), -1)
    hands["f"] = hnd(REST, (1, .3))
    if stroke > 0:
        n0 = np.array(arms["n"][1])
        arms["n"] = ("ik", tuple(n0 + (p_hand - n0) * stroke + np.array([-30, -90]) * math.sin(math.pi * stroke)), -1)
        hands["n"] = hnd(REST, (lerp(1, .95, stroke), lerp(.3, .32 + .1 * sw, stroke)), curl=(.3, .35, .4, .45), spread=.05)
    look_cat = smooth(29.9, 30.1, t)
    expr = dict(lid=.55, look=(lerp(.6, .9, look_cat), lerp(.3, .55, look_cat)), brows="calm" if t < 30.2 else "up", mouth="smile", smile=.5 + .5 * happy,
                closed=blink_at(t, 31.1, .16), hair=1.5 * osc(t, 1.2) + 2 * bump(t, t_land, .3))
    if t > tv:
        expr["laugh"] = .7 * smooth(tv, tv + .2, t)
    d = dima(t, arms, hands, expr, lean=.2 + .03 * stroke, head_ang=.03 * osc(t, .8) + .04 * look_cat)
    hearts = ""
    for j in range(5):
        hu = clamp((t - tv + .02 - j * .1) / .75)
        if 0 < hu < 1:
            hx = head_w[0] + 30 + 46 * (j - 2) + 14 * math.sin(hu * 6 + j)
            hy = head_w[1] - 110 - 170 * ease_out(hu, 1.5) - 14 * (j % 2)
            r = (30 + 6 * (j % 2)) * math.sin(math.pi * min(1, hu * 1.25)) + 1
            hearts += heart(hx, hy, r, seed=9700 + j * 3)
    dust = ""
    if t > t_land:
        e = clamp((t - t_land) / .4)
        dust = burst(x, y - 10, e, 50, 110, 6, INK, 4, seed=9800, rot0=math.pi + .3) if e < 1 else ""
    scr = report(14, 286, 7.0, t, caret=False, clean=True) + check_mark(214, 132, 62, 1.0)
    lap = LAP.draw(scr)
    on_desk = lap + phone_flat(*PHONE_DESK, .9, -1.0, 0) + mug_tip(*MUG_W, 0) + headset_flat(HS_DESK[0] + 60, HS_DESK[1], .62, 0) + cat_svg
    w = desk_world(t, d, True, on_desk=on_desk, front=hearts + dust)
    return compose(w, cam, True, LAP.glow("#ffe2b8", .2))


SHOTS = {"s01": s01, "s02": s02, "s05": s05, "s06": s06, "s10": s10, "s14": s14, "s15": s15, "s16": s16, "s17": s17}


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    return SHOTS[sid](t)
