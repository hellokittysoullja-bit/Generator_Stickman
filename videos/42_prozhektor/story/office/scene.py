"""Сцена office рилса 42 «все заметили»: Дима в офисе, горчичная футболка задом наперёд (бирка под подбородком).
Планы s01 s02 s05 s06 s08 s14 s15. frame(sid, t) -> SVG 1080×1920, t — общее время ролика; удары — по voice/words.json.

Основа — сцена desk рилса 39 (тот же Дима people.py, ноутбук, стол, кисти hand.py). Своё: стена офиса (окно с жалюзи на
город, белая доска со схемами и стикерами, полка с папками, перегородка с коллегой, растения), офисное кресло, футболка
(people.tee_parts / tee_arm), красный круг от руки, прожектор с глазами из темноты, пузырь мыслей, облако-вихрь.
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
        if w["word"].strip(".,?!:").lower() == word and w["start"] >= after:
            return w["start"]
    raise KeyError(word)



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
def dima(t, arms, hands=None, expr=None, lean=0.14, head_ang=0.0, hip=None, feet=None, tee="back", tag_ang=14.0, tag_k=1.0, head_off=(8, -64)):
    feet = feet or {"n": ((450, 1468), 0.0), "f": ((425, 1462), 0.0)}
    hp = HIP if hip is None else np.array(hip, float)
    p = dict(hip=tuple(hp), scale=BS, lean=lean, feet=feet, arms=arms, hands=hands or {}, expr=expr or {}, head_ang=head_ang,
             hood=0.0, tee=tee, tag_ang=tag_ang, tag_k=tag_k, head_off=head_off)
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


# ═════════════════════════ офис ═════════════════════════
import office_room as OR  # noqa: E402


def desk_world(t, d, *, on_desk="", mid="", front="", back_extra="", chair_sq=0.0, chair=True, coll_turn=0.0):
    w = [OR.office_back(t), back_extra, OR.tall_plant(t), OR.colleague(t, turn=coll_turn), OR.partition(t)]
    if chair:
        w.append(OR.office_chair(HIP[0], HIP[1] + 4, chair_sq))
    w.append(den.desk_back())
    w.append(d.get("legs", ""))
    w.append(den.desk_top())
    w.append(on_desk)
    w.append(d["arm_f"])
    w.append(d["body"])
    w.append(mid)
    w.append(d["arm_n"])
    w.append(d.get("tag", ""))
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




# ═════════════════════════ слова ═════════════════════════
T_DIMA = wt("дима")              # 0.16
T_FUTB = wt("футболке")          # 1.44
T_ZADOM = wt("задом")            # 2.16
T_NAPER = wt("наперёд")          # 2.53
T_KAZAL = wt("казалось")         # 7.52
T_VSE = wt("все", 8.0)           # 8.32
T_NEE = wt("неё")                # 9.60
T_DUMAESH = wt("думаешь")        # 13.84
T_SEBE = wt("себе")              # 14.24
T_SMEET = wt("смеётся")          # 26.56
T_PEREV = wt("переворачивает")   # 27.36
T_FUTB2 = wt("футболку")         # 28.05

RED = "#e2443a"


def calm_arms(t):
    """Руки спокойно на столе у ноутбука (дальняя на клавиатуре, ближняя у края)."""
    near = LAP.key(.3, .7) + np.array([-40, -10 + 2 * osc(t, .7)])
    far = LAP.key(.2, .42) + np.array([-24, -14])
    return {"n": ("ik", tuple(near), -1), "f": ("ik", tuple(far), -1)}, {"n": hnd(REST, (1, .3)), "f": hnd(REST, (1, .25))}


def red_circle(cx, cy, rx, ry, u, w=9.0, seed=9100, rot0=-2.4):
    """Красный круг от руки (дописывается u 0..1): чуть больше оборота, начало и конец не сходятся, белый ореол."""
    if u <= 0:
        return ""
    n = 40
    pts = []
    for j in range(n + 1):
        q = j / n
        a = rot0 + q * 2 * math.pi * 1.12
        r = 1 + .07 * math.sin(q * 5.3 + 1) + .05 * q
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a) - 4 * q))
    m = max(2, int(len(pts) * clamp(u)))
    pp = pts[:m]
    return (line(pp, w * 1.9, "#ffffff", taper=.25, wmin=.5, seed=seed, op=.9) + line(pp, w, RED, taper=.25, wmin=.5, seed=seed + 1))


def sweat(x, y, s, seed=9200):
    pts = [(x, y - 26 * s), (x + 12 * s, y), (x + 9 * s, y + 12 * s), (x, y + 16 * s), (x - 9 * s, y + 12 * s), (x - 12 * s, y)]
    return shape(pts, "#bfe6fa", blob([(x - 4 * s, y - 4 * s), (x + 1 * s, y - 2 * s), (x - 1 * s, y + 5 * s)], "#ffffff"), w=3, seed=seed)


# ═════════════════════════ s01: хук — Дима плюхается на кресло, влёт камеры ═════════════════════════
def s01(t):
    # влёт: 1/(1+0.42) → 1.05 за 0.2 с → 1.0; поворот −3° → 0
    u = clamp(t / .2)
    z = lerp(1 / 1.42, 1.05, ease_out(u, 3))
    if t > .2:
        z = 1.0 + .05 * math.exp(-(t - .2) * 9) * math.cos((t - .2) * 14)
    r = -3.0 * (1 - ease_out(clamp(t / .22), 2)) + .35 * osc(t, .7)
    k = clamp(t / 1.6)
    # плюх: таз падает в кресло (уже летит в кадре 0), касание 0.24 с, просадка и отскок
    tl = .24
    if t < tl:
        q = t / tl
        hip = HIP + np.array([-46 * (1 - q), -170 * (1 - q * q)])
        sq = 0.0
    else:
        e = t - tl
        b = math.exp(-e * 7) * math.cos(e * 22)
        hip = HIP + np.array([0, 22 * b])
        sq = clamp(b) if b > 0 else 0.0
        sq = max(sq, 0.0)
    land = smooth(tl - .05, tl + .25, t)
    s = 1.66 * z * (1 + .05 * k) * (1 + punch(t, tl, .03, .04, .3))
    cam = (420 + 10 * k, 880 - 10 * k, s, r)
    # руки: в полёте раскинуты, после посадки ложатся на стол (ближняя тянется к кружке)
    arms_t, hands_t = calm_arms(t)
    if land < 1:
        up_n = hip + np.array([200, -330])
        up_f = hip + np.array([120, -380])
        an = np.array(arms_t["n"][1])
        af = np.array(arms_t["f"][1])
        pn = up_n + (an - up_n) * ease_io(land)
        pf = up_f + (af - up_f) * ease_io(land)
        arms_t = {"n": ("ik", tuple(pn), -1), "f": ("ik", tuple(pf), -1)}
        hands_t = {"n": hnd(REST, (lerp(.3, 1, land), lerp(-1, .3, land)), spread=lerp(.25, .08, land)),
                   "f": hnd(REST, (lerp(.4, 1, land), lerp(-1, .25, land)), spread=lerp(.25, .08, land))}
    feet = {"n": (tuple(np.array((450, 1468)) + np.array([-40, -40]) * (1 - land)), -.3 * (1 - land)),
            "f": (tuple(np.array((425, 1462)) + np.array([-30, -60]) * (1 - land)), -.4 * (1 - land))}
    expr = dict(lid=.55, look=(.5, .1), brows="up", mouth="grin" if t < .9 else "smile", open=.25, smile=1.0, closed=blink_at(t, 1.22, .14),
                hair=8 * bump(t, tl, .35) + 2 * osc(t, 2.1))
    d = dima(t, arms_t, hands_t, expr, lean=.1 - .06 * (1 - land) + .02 * osc(t, .9), head_ang=-.05 + .05 * bump(t, tl + .02, .3) + .02 * osc(t, 1.4),
             hip=hip, feet=feet, tag_ang=14 + 18 * bump(t, tl, .35) * osc(t, 7))
    dust = ""
    if t > tl:
        e = clamp((t - tl) / .4)
        if e < 1:
            dust = burst(hip[0] - 10, hip[1] + 60, e, 90, 170, 7, INK, 5, seed=9010, rot0=math.pi * .9)
    lap = LAP.draw(report(14, 286, 3.0, t, caret=True))
    on_desk = lap + phone_flat(*PHONE_DESK, .9, 1.0, .4) + mug_tip(*MUG, 0)
    w = desk_world(t, d, on_desk=on_desk, chair_sq=sq, front=dust)
    return compose(w, cam, False, LAP.glow())



import hand as Hand  # noqa: E402


def hand_kw(far=False):
    kw = dict(shape_fn=people.shape, line_fn=people.line, skin=people.PAL["dima"]["SKIN"], skin_sh=people.PAL["dima"]["SKIN_SH"],
              skin_sh2=people.PAL["dima"]["SKIN_SH2"])
    return kw


def mug_in_hand(C, ang, k=.46, steam_t=None):
    """Кружка в ближней руке: C — центр кружки (мир), ang — наклон (отриц. — верх к лицу). Возвращает (svg, запястье)."""
    people.C = people.PAL["dima"]
    h = 128 * k
    R = 50 * k
    side = -1
    back, front = Hand.grip((0, 0), R, side, k=BS, seed=9300, **hand_kw())
    mug = kitchen.mug(0, h / 2, k, 0, col="#c44f3a")
    mug += blob(T(ellipse_pts(0, -126, 42, 6, 14), 0, h / 2, k), "#5a3220")
    g = f'<g transform="translate({C[0]:.2f} {C[1]:.2f}) rotate({ang:.2f})">{back}{mug}{front}</g>'
    wr = np.array(C) + rot(np.array([side * (R + 40 * BS), 6.0]), math.radians(ang))
    st = ""
    if steam_t is not None:
        top = np.array(C) + rot(np.array([0, -h / 2 - 10]), math.radians(ang))
        for j in range(2):
            u = (steam_t * .7 + j * .5) % 1
            x0 = top[0] + 10 * (j - .5)
            pts = [(x0 + 6 * math.sin(u * 6 + q * 1.2 + j), top[1] - 14 - q * 14 - 30 * u) for q in range(4)]
            st += line(pts, 4 * (1 - u) + 1, "#ffffff", taper=.5, wmin=.3, seed=9310 + j, op=.7 * math.sin(math.pi * u))
    return g + st, wr


# ═════════════════════════ s02: крупно ворот, кофе, красный круг на «задом», бирка подпрыгивает на «наперёд» ═════════════════════════
def s02(t):
    tz, tn = T_ZADOM, T_NAPER
    k = ease_io(clamp((t - 1.2) / 2.2))
    tag_pop = 0.0
    if t > tn:
        e = t - tn
        tag_pop = math.exp(-e * 6) * math.sin(e * 26)
    probe = dima(t, *calm_arms(t), {}, lean=.12)
    tagw = probe["tag_w"]
    # кружка: у рта, глоток (наклон), потом опускается к груди
    sip = smooth(1.25, 1.55, t) * (1 - smooth(2.35, 2.75, t))
    mouth = head_pt(probe, (70, 96))
    C_up = mouth + np.array([50, -4])
    C_dn = np.array([tagw[0] + 190, tagw[1] + 120])
    C = C_dn + (C_up - C_dn) * ease_io(sip)
    ang = -6 - 26 * sip + 2 * osc(t, 1.3)
    mug, wr = mug_in_hand(C, ang, steam_t=t if sip < .5 else None)
    arms = {"n": calm_arms(t)[0]["n"], "f": ("ik", tuple(wr), -1)}
    hands = {"n": hnd(REST, (1, .3)), "f": dict(kind="none")}
    expr = dict(lid=.35 + .1 * (1 - sip), look=(.8, -.2 + .3 * (1 - sip)), brows="calm", mouth="smile", smile=.6 * (1 - sip),
                closed=.85 * sip + blink_at(t, 3.05, .14), hair=1.5 * osc(t, 1.7) + 3 * bump(t, tz, .3))
    d = dima(t, arms, hands, expr, lean=.12, head_ang=-.07 * sip + .015 * osc(t, 1.1), tag_ang=14 + 22 * tag_pop + 2 * osc(t, 2.3),
             tag_k=1 + .25 * max(0.0, tag_pop) + .12 * bump(t, tz, .3))
    tagw = d["tag_w"]
    hit = punch(t, tz, .07, .05, .35) + punch(t, tn, .04, .05, .3)
    s = (3.5 + .5 * k) * (1 + hit)
    cx = lerp(tagw[0] + 40, tagw[0] + 15, k)
    cy = lerp(tagw[1] - 60, tagw[1] - 30, k)
    cam = (cx + 3 * bump(t, tz, .3) * osc(t, 12), cy, s, .8 - 1.2 * k + .8 * bump(t, tz, .3) * osc(t, 9))
    circ = red_circle(tagw[0] + 2, tagw[1] - 2, 44, 50, clamp((t - tz + .02) / .3), w=6.5, seed=9120)
    burst_ = burst(tagw[0], tagw[1] - 10, clamp((t - tn) / .35), 62, 92, 7, RED, 4.5, seed=9130, rot0=-1.4)
    lap = LAP.draw(report(14, 286, 3.0, t, caret=True))
    w = desk_world(t, d, on_desk=lap + phone_flat(*PHONE_DESK, .9, 1.0, .4), front=mug + circ + burst_)
    return compose(w, cam, False, LAP.glow())


# ═════════════════════════ s05: нащупал бирку — глаза распахиваются на «казалось», пот, румянец ═════════════════════════
def s05(t):
    tk = T_KAZAL
    k = ease_io(clamp((t - 6.3) / 2.1))
    shock = smooth(tk - .04, tk + .12, t)
    probe = dima(t, *calm_arms(t), {}, lean=.12)
    tagw = probe["tag_w"]
    reach = ease_out(clamp((t - 6.3) / .45), 2)
    # пальцы щупают бирку: запястье ниже-левее бирки, кисть вверх-вправо; мелкое теребление
    rub = 4 * osc(t, 3.2) * (1 - shock)
    tgt = tagw + np.array([-4 + rub, 96 - .5 * rub])
    p = tgt + np.array([10, 60]) * (1 - reach)
    arms = {"n": ("ik", tuple(p), -1), "f": calm_arms(t)[0]["f"]}
    hands = {"n": hnd(dict(kind="open", curl=(.12, .6, .75, .85), spread=.04, thumb=.15, bend=.08), (.12 + .1 * (1 - reach), -1)),
             "f": hnd(REST, (1, .25))}
    expr = dict(lid=lerp(.45, 1.0, shock), look=(lerp(.2, .1, shock), lerp(.5, -.05, shock)), brows="up" if shock > .5 else "calm",
                mouth="talk" if shock > .5 else "flat", open=.35 * shock, smile=0, blush=shock,
                closed=blink_at(t, 6.95, .14), hair=1.5 * osc(t, 1.9) + 7 * bump(t, tk, .3))
    d = dima(t, arms, hands, expr, lean=.12 - .04 * shock, head_ang=-.03 - .05 * shock + .01 * osc(t, 1.2), tag_ang=14 + 6 * osc(t, 3.2) * (1 - shock))
    hp = d["head"]
    hit = punch(t, tk, .06, .05, .35)
    s = (2.55 + .25 * k) * (1 + hit)
    cam = (hp[0] + 40 - 10 * k, hp[1] + 70 + 10 * k, s, -.5 + .9 * k + .7 * bump(t, tk, .3) * osc(t, 10))
    fx = ""
    if t > tk:
        e = clamp((t - tk) / .5)
        sp = head_pt(d, (-96, -20))
        fx += sweat(sp[0] - 6, sp[1] + 28 * ease_in(clamp((t - tk - .1) / .9), 2), 1.0 * lib.back_out(clamp(e * 1.6), 2), seed=9210)
        fx += burst(*head_pt(d, (40, -40)), clamp((t - tk) / .35), 120, 170, 8, INK, 4, seed=9220, rot0=-2.8)
    lap = LAP.draw(report(14, 286, 3.0, t, caret=False))
    w = desk_world(t, d, on_desk=lap + phone_flat(*PHONE_DESK, .9, 1.0, .4) + mug_tip(*MUG, 0), front=fx)
    return compose(w, cam, False, LAP.glow())


# ═════════════════════════ s06: прожектор и глаза из темноты; на «неё» луч сужается на бирку ═════════════════════════
EYES = [(-330, -250, 1.0, .0), (330, -330, .9, .12), (-420, 60, .8, .24), (420, 30, 1.0, .06), (-250, -520, .7, .3), (250, -560, .75, .18),
        (-80, -640, .65, .36), (120, 260, .85, .42), (-300, 330, .9, .5)]


def glow_eyes(cx, cy, t, t0, look_to, k=1.0):
    o = []
    for j, (dx, dy, sc, dl) in enumerate(EYES):
        u = clamp((t - t0 - dl) / .22)
        if u <= 0:
            continue
        x, y = cx + dx * k, cy + dy * k
        sc = sc * k * lib.back_out(u, 2.4)
        bl = blink_at(t, t0 + .9 + .37 * j % 1.1, .16)
        v = np.array(look_to) - np.array([x, y])
        v = v / (np.linalg.norm(v) + 1e-9)
        g = lib.rad_grad([(0, "#fff6c0", .55), (1, "#fff6c0", 0)], x, y, 120 * sc, 70 * sc)
        o.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{120 * sc:.1f}" ry="{70 * sc:.1f}" fill="url(#{g})"/>')
        for sx in (-1, 1):
            ex = x + sx * 34 * sc
            ry = 22 * sc * (1 - bl * .92)
            o.append(shape(ellipse_pts(ex, y, 26 * sc, max(1.5, ry), 14), "#fffbe6", "", w=2.6 * sc, seed=9400 + j * 2 + (sx > 0), ink_color="#0a0c14")
                     if hasattr(lib, "shape") else "")
            if ry > 6:
                o.append(f'<ellipse cx="{ex + v[0] * 12 * sc:.1f}" cy="{y + v[1] * 8 * sc:.1f}" rx="{6.5 * sc:.1f}" ry="{min(ry * .6, 9 * sc):.1f}" fill="#0a0c14"/>')
    return "".join(o)


def s06(t):
    tv, tn = T_VSE, T_NEE
    k = ease_io(clamp((t - 8.0) / 2.5))
    dark = smooth(tv - .06, tv + .06, t)
    narrow = smooth(tn - .05, tn + .25, t)
    shrink = smooth(tv, tv + .5, t)
    arms, hands = calm_arms(t)
    arms["n"] = ("ik", tuple(np.array(arms["n"][1]) + np.array([-30, -10]) * shrink), -1)
    dart = osc(t, 1.4)
    expr = dict(lid=lerp(.5, .95, shrink), look=(lerp(.5, .9 * dart, shrink), lerp(.2, -.1, shrink)), brows="worry" if shrink > .3 else "calm",
                mouth="flat" if shrink < .3 else "talk", open=.15 + .1 * narrow, smile=0, blush=.6 * shrink + .4 * narrow,
                closed=blink_at(t, 8.12, .14), hair=6 * bump(t, tv, .3) + 1.5 * osc(t, 2.3))
    d = dima(t, arms, hands, expr, lean=.12 + .14 * shrink, head_ang=.12 * shrink + .02 * osc(t, 1.6), head_off=(8 + 10 * shrink, -64 + 40 * shrink),
             tag_ang=14 + 4 * osc(t, 2.7))
    tagw = d["tag_w"]
    hp = d["head"]
    hit = punch(t, tv, .08, .05, .4) + punch(t, tn, .05, .05, .35)
    s = (1.75 + .55 * k + 1.1 * narrow) * (1 + hit)
    tgt = hp + np.array([20, 120])
    cx = lerp(tgt[0], tagw[0], narrow)
    cy = lerp(tgt[1], tagw[1] - 20, narrow)
    cam = (cx + 5 * bump(t, tv, .35) * osc(t, 13), cy + 4 * bump(t, tv, .35) * osc(t, 11), s, .4 - .6 * k + 1.2 * bump(t, tv, .4) * osc(t, 9))
    lap = LAP.draw(report(14, 286, 3.0, t, caret=False))
    w = desk_world(t, d, on_desk=lap + phone_flat(*PHONE_DESK, .9, 1.0, .4) + mug_tip(*MUG, 0))
    light = ""
    if dark > 0:
        # луч: от верха к пятну вокруг Димы → сужается на бирку
        top = np.array([lerp(hp[0] + 60, tagw[0] + 30, narrow), hp[1] - 900])
        c = np.array([lerp(hp[0] + 10, tagw[0], narrow), lerp(hp[1] + 230, tagw[1], narrow)])
        rx = lerp(330, 62, narrow)
        ry = lerp(110, 50, narrow)
        tw = lerp(60, 18, narrow)
        cone = [(top[0] - tw, top[1]), (top[0] + tw, top[1]), (c[0] + rx, c[1]), ] + [
            (c[0] + rx * math.cos(a), c[1] + ry * math.sin(a)) for a in np.linspace(0, math.pi, 16)] + [(c[0] - rx, c[1])]
        cone_d = lib.fill_d(cone) if hasattr(lib, "fill_d") else ""
        if narrow > 0:
            # пятно на бирке поверх: всё, кроме круга вокруг бирки, темнее
            pass
        mid_ = lib.uid("m")
        fb = lib.uid("f")
        lib.DEFS.append(f'<filter id="{fb}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{lerp(16, 6, narrow):.1f}"/></filter>')
        lib.DEFS.append(f'<mask id="{mid_}" maskUnits="userSpaceOnUse" x="-2000" y="-2000" width="6000" height="6000">'
                        f'<rect x="-2000" y="-2000" width="6000" height="6000" fill="#fff"/>'
                        f'<path d="{cone_d}" fill="#000" filter="url(#{fb})"/></mask>')
        light += f'<rect x="-2000" y="-2000" width="6000" height="6000" fill="#07091a" opacity="{.93 * dark:.3f}" mask="url(#{mid_})"/>'
        g = lib.lin_grad([(0, "#fff3c4", .5 * dark), (1, "#fff3c4", .12 * dark)], 0, 0, 0, 1)
        light += f'<path d="{cone_d}" fill="url(#{g})" style="mix-blend-mode:screen"/>'
        light += f'<ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#fff3c4" opacity="{.18 * dark:.3f}" style="mix-blend-mode:screen"/>'
        # пылинки в луче
        for j in range(10):
            uu = (t * .25 + j * .1) % 1
            px = top[0] + (c[0] - top[0]) * uu + (j % 5 - 2) * tw * .6 * (1 + uu * 2)
            py = top[1] + (c[1] - top[1]) * uu
            light += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{2.2:.1f}" fill="#fff8d8" opacity="{.6 * dark * math.sin(math.pi * uu):.2f}"/>'
        light += glow_eyes(hp[0] + 40, hp[1] + 150, t, tv + .02, tagw, k=lerp(1.0, .55, narrow) / (1 + .0 * narrow))
    return compose(w, cam, False, light if dark > 0 else LAP.glow())


# ═════════════════════════ s08: пузырь мыслей про себя ═════════════════════════
def cloud_pts(cx, cy, rx, ry, n=11, bump_k=.16, ph=0.0):
    pts = []
    for j in range(n):
        a0 = j / n * 2 * math.pi + ph
        a1 = (j + 1) / n * 2 * math.pi + ph
        for q in np.linspace(0, 1, 6)[:-1]:
            a = a0 + (a1 - a0) * q
            r = 1 + bump_k * math.sin(math.pi * q)
            pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)) + ((1,) if q == 0 else ()))
    return pts


def tag_icon(x, y, s, ang=0.0, seed=9500):
    """Ворот футболки крупно, из него торчит белая бирка."""
    o = []
    fab = T([(-70, 6, 1), (-46, -6), (0, -14), (46, -6), (70, 6, 1), (70, 52, 1), (-70, 52, 1)], x, y + 20 * s, s)
    rib = lib.band([tuple(p) for p in T([(-66, 4), (-30, -8), (30, -8), (66, 4)], x, y + 20 * s, s)], 14 * s, 14 * s, step=3, cap=False)
    o.append(shape(fab, "#d4a23e", blob(rib, "#a97b25", .9), w=4 * s, seed=seed + 20))
    loc = [(-22, 4, 1), (22, 4, 1), (26, -64, 1), (-18, -66, 1)]
    P_ = [tuple(p[:2]) + (1,) for p in T(loc, x, y + 14 * s, s, ang)]
    inn = "".join(line(T([(-12, -50 + 12 * j), (14, -50 + 12 * j)], x, y + 14 * s, s, ang), 3.4 * s, "#9aa1ae", seed=seed + j, taper=.1, wmin=.8)
                  for j in range(3))
    o.append(shape(P_, "#fbfaf5", inn, w=4 * s, seed=seed + 9))
    return "".join(o)


def tee_icon(x, y, s, seed=9520):
    pts = [(-30, -50, 1), (-12, -50), (0, -40), (12, -50), (30, -50, 1), (62, -24, 1), (46, -4, 1), (32, -14, 1), (32, 52, 1), (-32, 52, 1), (-32, -14, 1),
           (-46, -4, 1), (-62, -24, 1)]
    P_ = T(pts, x, y, s)
    inn = line(T([(-14, -48), (0, -38), (14, -48)], x, y, s), 3 * s, "#a97b25", seed=seed + 1)
    inn += shape(T([(-8, -44, 1), (8, -44, 1), (9, -20, 1), (-7, -21, 1)], x, y, s), "#fbfaf5", "", w=2.6 * s, seed=seed + 2)
    inn += blob(T([(10, -50), (32, -50), (32, 52), (14, 52)], x, y, s), "#a97b25", .5)
    return shape(P_, "#d4a23e", inn, w=4 * s, seed=seed)


def face_icon(x, y, s, t):
    people.C = people.PAL["dima"]
    lib.INK_K[0], k0 = lib.INK_K[0] * 1.3, lib.INK_K[0]
    o = (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
         + people.dima_head(dict(lid=.95, look=(.0, .0), brows="worry", mouth="talk", open=.3, blush=1.0, hair=2 * osc(t, 3)))
         + blob(ellipse_pts(20, 20, 120, 110, 16), "#ff5a4a", .28, 'style="mix-blend-mode:multiply"') + "</g>")
    lib.INK_K[0] = k0
    return o


def s08(t):
    td, ts = T_DUMAESH, T_SEBE
    k = ease_io(clamp((t - 12.9) / 2.5))
    arms, hands = calm_arms(t)
    expr = dict(lid=.9, look=(.35, -.85), brows="worry", mouth="flat", smile=0, blush=.4 * smooth(ts, ts + .3, t),
                closed=blink_at(t, 13.4, .14), hair=1.5 * osc(t, 1.9) + 3 * bump(t, td, .3))
    d = dima(t, arms, hands, expr, lean=.12, head_ang=-.06 + .02 * osc(t, .9))
    hp = d["head"]
    bc = hp + np.array([120, -330])
    grow = lib.back_out(clamp((t - 12.95) / .4), 1.8)
    bub = ""
    if grow > 0:
        # хвостик пузыря — кружки от головы
        for j, (u, r) in enumerate([(.25, 12), (.5, 19), (.75, 27)]):
            uu = clamp((t - 12.9 - j * .07) / .25)
            if uu > 0:
                p = hp + np.array([70, -130]) + (bc + np.array([-120, 170]) - hp - np.array([70, -130])) * u
                bub += shape(ellipse_pts(p[0], p[1], r * uu, r * uu * .9, 12), "#ffffff", "", w=3.4, seed=9600 + j)
        rx, ry = 250 * grow, 150 * grow
        cp = cloud_pts(bc[0], bc[1] + 3 * osc(t, 1.1), rx, ry, n=12, ph=.05 * t)
        inner = blob(ellipse_pts(bc[0] + 20, bc[1] + 30, rx * .9, ry * .7, 18), "#eef3fa", .9)
        # картинки по очереди: бирка, футболка, своё красное лицо
        pics = [(td, -150, tag_icon, 1.1), (td + .2, 0, tee_icon, 1.15), (ts, 160, None, .46)]
        for j, (tj, dx, fn, sc) in enumerate(pics):
            u = lib.back_out(clamp((t - tj + .04) / .25), 2.6)
            if u <= 0:
                continue
            x, y = bc[0] + dx * grow, bc[1] + 6 + 6 * osc(t, 1.6, j)
            if fn is tag_icon:
                inner += tag_icon(x, y, sc * u, ang=8 * osc(t, 1.3))
            elif fn is tee_icon:
                inner += tee_icon(x, y, sc * u)
            else:
                inner += face_icon(x - 12, y + 6, sc * u, t)
        bub += shape(cp, "#ffffff", inner, w=4.2, seed=9620)
        if t > ts:
            bub += burst(bc[0] + 150, bc[1], clamp((t - ts) / .35), 70, 110, 7, RED, 4, seed=9640)
    hit = punch(t, td, .04, .05, .3) + punch(t, ts, .04, .05, .3)
    s = (1.72 + .22 * k) * (1 + hit)
    cam = (hp[0] + 110, hp[1] - 110 + 10 * k, s, -.4 + .7 * k)
    lap = LAP.draw(report(14, 286, 3.0, t, caret=True))
    w = desk_world(t, d, on_desk=lap + phone_flat(*PHONE_DESK, .9, 1.0, .4) + mug_tip(*MUG, 0), front=bub)
    return compose(w, cam, False, LAP.glow())


# ═════════════════════════ s14: смеётся ═════════════════════════
def s14(t):
    tl = T_SMEET
    k = ease_io(clamp((t - 24.9) / 2.55))
    lg = smooth(tl - .08, tl + .12, t)
    bounce = lg * abs(osc(t, 4.2))
    arms, hands = calm_arms(t)
    arms["n"] = ("ik", tuple(np.array(arms["n"][1]) + np.array([0, -8 * bounce])), -1)
    sm = smooth(25.0, 25.8, t)
    expr = dict(lid=.55, look=(.3, .2), brows="up" if lg > .3 else "calm", mouth="laugh" if lg > .2 else "smile", open=.6 + .4 * bounce,
                smile=sm, laugh=lg, tears=.6 * smooth(tl + .2, tl + .7, t), closed=blink_at(t, 25.4, .14),
                hair=3 * bounce + 1.5 * osc(t, 1.9))
    d = dima(t, arms, hands, expr, lean=.1 - .06 * lg, head_ang=-.03 - .26 * lg - .05 * bounce, tag_ang=14 + 22 * lg * osc(t, 8.4) + 3 * osc(t, 2))
    hp = d["head"]
    sh = lg * (1 - smooth(tl + .9, tl + 1.3, t) * .6)
    s = (2.35 + .2 * k) * (1 + punch(t, tl, .06, .05, .35))
    cam = (hp[0] + 60 + 7 * sh * osc(t, 11), hp[1] + 110 + 6 * sh * osc(t, 13, 1), s, .5 - .8 * k + 1.4 * sh * osc(t, 7))
    fx = ""
    if lg > 0:
        for j in range(3):
            u = ((t - tl) * 1.6 + j / 3) % 1
            p = head_pt(d, (150, -60 + 40 * j))
            fx += line([(p[0] + 20 + 40 * u, p[1] - 10 * u), (p[0] + 50 + 60 * u, p[1] - 20 * u + 8 * (j - 1))], 6 * (1 - u) + 1, INK, taper=.4,
                       wmin=.3, seed=9700 + j, op=lg * (1 - u))
    lap = LAP.draw(report(14, 286, 3.0, t, caret=False))
    w = desk_world(t, d, on_desk=lap + phone_flat(*PHONE_DESK, .9, 1.0, .4) + mug_tip(*MUG, 0), front=fx)
    return compose(w, cam, False, LAP.glow())


# ═════════════════════════ s15: облако-вихрь — футболка правильно, большой палец ═════════════════════════
def fight_cloud(cx, cy, t, u, seed=9800):
    """Мультяшное облако-вихрь (как драка в мультфильмах): пухлые клубы крутятся, внутри завитки, по краю мелькают
    рука, нога, клочок футболки и звёздочки, вокруг — штрихи скорости."""
    if u <= 0:
        return ""
    o = []
    sc = lib.back_out(clamp(u * 3), 1.8) * (1 - ease_in(smooth(.76, .97, u), 2))
    if sc < .04:
        return ""
    rx, ry = 230 * sc, 250 * sc
    ph = t * 7
    # штрихи скорости по кругу
    for j in range(10):
        a = -ph * .6 + j * 2 * math.pi / 10
        r0, r1 = 1.08, 1.32
        arc = [(cx + rx * (r0 + (r1 - r0) * .5) * math.cos(a + q * .5), cy + ry * (r0 + (r1 - r0) * .5) * math.sin(a + q * .5)) for q in np.linspace(0, 1, 6)]
        o.append(line(arc, 6, INK, taper=.6, wmin=.2, seed=seed + 60 + j, op=.8))
    # клубы по краю (вращаются)
    for j in range(9):
        a = ph * .35 + j * 2 * math.pi / 9
        pr = (.34 + .06 * math.sin(t * 9 + j)) * (rx + ry) / 2
        px, py = cx + rx * .78 * math.cos(a), cy + ry * .78 * math.sin(a)
        o.append(shape(ellipse_pts(px, py, pr, pr * .9, 16), "#f4efe4", blob(ellipse_pts(px + pr * .25, py + pr * .3, pr * .7, pr * .55, 12), "#ddd5c6", .9),
                       w=4.4, seed=seed + 70 + j))
    inner = blob(ellipse_pts(cx + 30 * sc, cy + 50 * sc, rx * .8, ry * .6, 18), "#e2dacb", .85)
    for j in range(4):
        a = -ph * (1 + .15 * j) + j * 1.6
        sw = [(cx + rx * .62 * (1 - q * .75) * math.cos(a + q * 4.2), cy + ry * .62 * (1 - q * .75) * math.sin(a + q * 4.2)) for q in np.linspace(0, 1, 16)]
        inner += line(sw, 7, "#9a8f7e", taper=.5, wmin=.25, seed=seed + 10 + j, op=.95)
    o.append(shape(cloud_pts(cx, cy, rx * .82, ry * .82, n=11, bump_k=.22, ph=ph * .2), "#f6f2ea", inner, w=5, seed=seed))
    # мелькающее: кулак, кроссовок, клочок футболки, бирка
    for j in range(4):
        a = ph * .8 + j * 2 * math.pi / 4
        if math.sin(t * 22 + j * 1.9) < -.1:
            continue
        p = (cx + rx * .95 * math.cos(a), cy + ry * .95 * math.sin(a))
        if j == 0:
            o.append(shape(ellipse_pts(p[0], p[1], 26, 22, 12, rot=math.degrees(a)), "#ecc4a2", line([(p[0] - 8, p[1] - 6), (p[0] + 8, p[1] - 6)], 2, "#bf8a74", seed=seed + 41), w=3.6, seed=seed + 40))
        elif j == 1:
            o.append(shape(T(rect_pts(-34, -14, 34, 14, 10), p[0], p[1], 1, math.degrees(a)), "#4b505e", blob(T(rect_pts(-34, 6, 34, 14, 6), p[0], p[1], 1, math.degrees(a)), "#f2eee6"), w=3.6, seed=seed + 42))
        elif j == 2:
            o.append(shape(T([(-30, -20, 1), (30, -24, 1), (24, 22, 1), (-26, 18, 1)], p[0], p[1], 1, math.degrees(a)), "#d4a23e", "", w=3.6, seed=seed + 43))
        else:
            o.append(shape(T([(-12, -16, 1), (12, -16, 1), (12, 16, 1), (-12, 16, 1)], p[0], p[1], 1, math.degrees(a) + 30), "#fbfaf5", "", w=3, seed=seed + 44))
    for j in range(5):
        a = -ph * .5 + j * 1.3
        p = (cx + rx * 1.18 * math.cos(a), cy + ry * 1.15 * math.sin(a))
        r = 17 + 5 * math.sin(t * 15 + j)
        st = [(p[0] + r * (1 if q % 2 == 0 else .42) * math.cos(q * math.pi / 5 - math.pi / 2),
               p[1] + r * (1 if q % 2 == 0 else .42) * math.sin(q * math.pi / 5 - math.pi / 2)) + (1,) for q in range(10)]
        o.append(shape(st, "#ffd23a", "", w=3, seed=seed + 50 + j))
    return "".join(o)


def s15(t):
    tp, tf = T_PEREV, T_FUTB2
    k = ease_io(clamp((t - 27.05) / 2.0))
    cu = clamp((t - tp + .02) / (tf - tp + .12))
    swapped = t >= tf - .2
    thumb = smooth(tf - .05, tf + .2, t)
    arms, hands = calm_arms(t)
    if swapped:
        sp = dima(t, arms, hands, {}, lean=.1, tee="front")
        up = sp["head"] + np.array([150, 130])
        an = np.array(arms["n"][1])
        arms["n"] = ("ik", tuple(an + (up - an) * ease_out(thumb, 2) + np.array([0, -6 * bump(t, tf + .2, .3)])), -1)
        ang = math.radians(-50)
        hands["n"] = dict(kind="open", curl=(.98, .98, .98, .98), spread=0.0, thumb=0.0, bend=.0, dir=(math.cos(ang), math.sin(ang)), flip=1)
        expr = dict(lid=.55, look=(.0, .0), brows="up", mouth="grin", open=.3, smile=1.0, wink=smooth(tf + .25, tf + .35, t) * (1 - smooth(28.7, 28.8, t)),
                    closed=0, hair=4 * bump(t, tf, .3) + 1.5 * osc(t, 2))
        d = dima(t, arms, hands, expr, lean=.08, head_ang=-.05 + .02 * osc(t, 1.4), tee="front")
    else:
        expr = dict(lid=.6, look=(.4, .3), brows="up", mouth="smile", smile=.8, closed=blink_at(t, 27.15, .14), hair=1.5 * osc(t, 2) + 5 * bump(t, tp, .3))
        d = dima(t, arms, hands, expr, lean=.1, head_ang=-.03, tag_ang=14 + 10 * osc(t, 6))
    hp = d["head"]
    hit = punch(t, tp, .07, .05, .35) + punch(t, tf, .05, .05, .3)
    s = (1.9 + .15 * k) * (1 + hit)
    shk = bump(t, tp + .3, .7)
    cam = (hp[0] + 60 + 8 * shk * osc(t, 12), hp[1] + 160 + 6 * shk * osc(t, 10, 1), s, .4 - .6 * k + 1.2 * shk * osc(t, 8))
    cloud = fight_cloud(hp[0] + 20, hp[1] + 150, t, cu)
    spark = ""
    if swapped:
        e = clamp((t - tf) / .45)
        spark = burst(hp[0] + 150, hp[1] + 60, e, 70, 130, 8, "#ffd23a", 6, seed=9900)
    lap = LAP.draw(report(14, 286, 3.0, t, caret=False))
    w = desk_world(t, d, on_desk=lap + phone_flat(*PHONE_DESK, .9, 1.0, .4) + mug_tip(*MUG, 0), front=cloud + spark)
    return compose(w, cam, False, LAP.glow())


SHOTS = {"s01": s01, "s02": s02, "s05": s05, "s06": s06, "s08": s08, "s14": s14, "s15": s15}


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    return SHOTS[sid](t)
