"""Стол и ноутбук Димы рилса 30 «двадцать вкладок» (агент A): s01 s02 s03 s14 s15 s16.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика; удары — на словах voice/words.json.

Два вида одного стола:
• «ноутбук спереди» (s01, s03, s14, s16) — ноутбук крупно лицом к зрителю на деревянном столе, за ним стена с окном
  (небо по времени дня), лампа справа; экран — браузер: полоса вкладок со значками (почта, документ, чат, видео),
  адресная строка без букв, содержимое активной вкладки значками и линиями;
• «Дима за столом» (s02, s15) — Дима (people.py, как в рилсе 27: лохматый, щетина, мешки, горчичное худи) сидит слева
  лицом вправо, ноутбук на столе развёрнут к нему и к зрителю (экран виден в 3/4), окно на стене за столом.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat as Cat  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
from ink import band, ellipse_pts, fill_d  # noqa: E402
from lib import INK, back_out, blob, clamp, ease_in, ease_io, ease_out, f, line, mix, rect_pts, shape, smooth  # noqa: E402
from parts import sevenseg  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["word"].strip(".,?!").lower() == word.lower() and w["start"] >= after - 1e-6:
            return w["start"]
    raise KeyError(word)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def kick(t, t0, dur=.4, freq=2.2):
    """Удар: мгновенный подъём и затухающее колебание (0 до t0)."""
    u = t - t0
    if u <= 0 or u > dur:
        return 0.0
    return math.exp(-u * 9) * math.cos(2 * math.pi * freq * u)


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


# ═════════════════════════════════════ ЦВЕТА ═════════════════════════════════════
WALL, WALL_SH = "#e8cfa8", "#d4b48a"
WOOD, WOOD_SH, WOOD_GR, WOOD_EDGE = "#b98653", "#9a6a3e", "#a7764a", "#7d5430"
LID, LID_SH, LID_HI = "#3b4152", "#2a2f3d", "#545b70"
DECK, DECK_SH, DECK_SH2, KEY, KEY_SH = "#c9ccd6", "#a9adbb", "#8d92a3", "#454b5c", "#2f3442"
CHROME, CHROME_SH = "#6b7489", "#566075"
PAGE, PAGE_SH, BAR, GREYL = "#fbfaf6", "#ebe7dc", "#e4e0d5", "#c3c0b8"
ICON = {"mail": "#f0a02a", "doc": "#3f7fd6", "chat": "#36a35a", "video": "#e0443a"}
SKY = {   # верх, низ, солнце/луна, тон света в комнате
    "day": ("#7fc0ea", "#cfe9f6", "#ffe27a"),
    "noon": ("#5fb1ec", "#bfe4f8", "#fff1a0"),
    "eve": ("#3c3570", "#f08c5c", "#ff9a52"),
    "night": ("#1d2148", "#4b3f78", "#f4ecc8"),
}


def sky_mix(a, b, u):
    return tuple(mix(x, y, u) for x, y in zip(SKY[a], SKY[b]))


# ═════════════════════════════════════ ЗНАЧКИ ═════════════════════════════════════
def icon(kind, cx, cy, s, sd=0, sat=1.0):
    """Значок вкладки: цветной скруглённый квадрат стороной s с белым символом."""
    col = ICON[kind] if sat >= 1 else mix("#9aa0ad", ICON[kind], sat)
    w = max(1.0, s * .06)
    h = s / 2
    o = [shape(rect_pts(cx - h, cy - h, cx + h, cy + h, s * .22), col, blob(rect_pts(cx - h, cy + h * .35, cx + h, cy + h, s * .2), lib.mul(col, (.82, .82, .86)), .9),
               w=w, seed=sd + 1, var=.1)]
    wh = "#ffffff"
    if kind == "mail":
        ex, ey = s * .30, s * .21
        o.append(shape([(cx - ex, cy - ey, 1), (cx + ex, cy - ey, 1), (cx + ex, cy + ey, 1), (cx - ex, cy + ey, 1)], wh, "", w=w * .8, seed=sd + 2, var=.1))
        o.append(line([(cx - ex, cy - ey), (cx, cy + ey * .15), (cx + ex, cy - ey)], w * .9, seed=sd + 3, taper=.1, wmin=.7))
    elif kind == "doc":
        px, py = s * .24, s * .32
        o.append(shape([(cx - px, cy - py, 1), (cx + px * .4, cy - py, 1), (cx + px, cy - py * .5, 1), (cx + px, cy + py, 1), (cx - px, cy + py, 1)], wh, "",
                       w=w * .8, seed=sd + 2, var=.1))
        for k in range(3):
            yy = cy - py * .25 + k * py * .38
            o.append(f'<rect x="{f(cx - px * .6)}" y="{f(yy - w * .45)}" width="{f(px * (1.2 if k < 2 else .8))}" height="{f(w * .9)}" fill="{col}"/>')
    elif kind == "chat":
        bx, by = s * .30, s * .2
        pts = ellipse_pts(cx, cy - s * .04, bx, by, 14)
        o.append(shape(pts + [], wh, "", w=w * .8, seed=sd + 2, var=.1))
        o.append(shape([(cx - bx * .5, cy + by * .6), (cx - bx * .75, cy + by * 1.45, 1), (cx - bx * .05, cy + by * .85)], wh, "", w=w * .7, seed=sd + 4, var=.1))
        for k in (-1, 0, 1):
            o.append(f'<circle cx="{f(cx + k * bx * .45)}" cy="{f(cy - s * .04)}" r="{f(s * .045)}" fill="{col}"/>')
    elif kind == "video":
        tr = s * .22
        o.append(shape([(cx - tr * .7, cy - tr, 1), (cx + tr, cy, 1), (cx - tr * .7, cy + tr, 1)], wh, "", w=w * .8, seed=sd + 2, var=.1))
    return "".join(o)


def cursor(x, y, s=1.0, press=0.0):
    """Курсор-стрелка, кончик в (x, y)."""
    k = s * (1 - .12 * press)
    pts = [(0, 0, 1), (0, 38, 1), (10, 29, 1), (17, 44, 1), (24, 41, 1), (17, 26, 1), (29, 26, 1)]
    P = [(x + p[0] * k, y + p[1] * k, 1) for p in pts]
    return shape(P, "#ffffff", "", w=3.0 * s, seed=901, var=.1)


# ═════════════════════════════════════ ЭКРАН-БРАУЗЕР ═════════════════════════════════════
SW, SH = 780.0, 560.0
TAB_Y0, TAB_Y1 = 12.0, 58.0
TOOL_Y1 = 108.0
TAB_X0, TAB_X1 = 12.0, SW - 58.0


def tab_layout(tabs):
    """tabs — список dict(kind, pop 0..1, out 0..1 (закрывается), prog). Возвращает [(x, w, tab)]."""
    weights = [tb.get("pop", 1.0) * (1 - tb.get("out", 0.0)) * tb.get("grow", 1.0) for tb in tabs]
    tot = sum(weights) or 1.0
    w0 = min(176.0, (TAB_X1 - TAB_X0) / max(tot, 1e-6))
    x = TAB_X0
    out = []
    for tb, wt_ in zip(tabs, weights):
        out.append((x, w0 * wt_, tb))
        x += w0 * wt_
    return out, w0


def tab_svg(x, w, tb, w0, active, sd):
    if w < 1.5:
        return ""
    pop = tb.get("pop", 1.0)
    out = tb.get("out", 0.0)
    sc = clamp(min(back_out(clamp(pop), 2.2), 1 - out) if pop < 1 else 1 - ease_in(out, 2))
    sc = max(0.0, min(1.25, sc))
    h = TAB_Y1 - TAB_Y0
    ww = max(w, w0 * pop * (1 - out) * tb.get("grow", 1.0)) - 3
    if ww < 2 or sc <= 0.02:
        return ""
    cx = x + w / 2
    r = min(10.0, ww * .25)
    fill = PAGE if active else "#cfd3de"
    pts = [(x + 1.5, TAB_Y1, 1), (x + 1.5 + r * .5, TAB_Y0 + r * .6), (x + 1.5 + r, TAB_Y0, 1), (x + 1.5 + ww - r, TAB_Y0, 1),
           (x + 1.5 + ww - r * .5, TAB_Y0 + r * .6), (x + 1.5 + ww, TAB_Y1, 1)]
    o = [shape(pts, fill, "" if active else blob([(x, TAB_Y1 - 8), (x + ww + 3, TAB_Y1 - 8), (x + ww + 3, TAB_Y1), (x, TAB_Y1)], "#b9bfcd"),
               w=2.4, seed=sd, var=.12)]
    s_ic = min(26.0, ww * .62)
    icx = x + 1.5 + min(ww * .5, 8 + s_ic / 2) if ww > 60 else cx
    o.append(icon(tb["kind"], icx, (TAB_Y0 + TAB_Y1) / 2 + 1, s_ic, sd + 10, sat=1.0))
    if ww > 70:
        lx0, lx1 = icx + s_ic / 2 + 8, x + ww - 26
        if lx1 > lx0 + 6:
            o.append(f'<rect x="{f(lx0)}" y="{f((TAB_Y0 + TAB_Y1) / 2 - 3)}" width="{f(lx1 - lx0)}" height="6" rx="3" fill="{GREYL}"/>')
        xx, yy = x + ww - 12, (TAB_Y0 + TAB_Y1) / 2
        o.append(line([(xx - 5, yy - 5), (xx + 5, yy + 5)], 2.2, "#6c7080", seed=sd + 3, taper=.1, wmin=.7))
        o.append(line([(xx + 5, yy - 5), (xx - 5, yy + 5)], 2.2, "#6c7080", seed=sd + 4, taper=.1, wmin=.7))
    pr = tb.get("prog")
    if pr is not None:
        bx0, bx1, by = x + 5, x + ww - 3, TAB_Y1 - 6
        o.append(f'<rect x="{f(bx0)}" y="{f(by)}" width="{f(bx1 - bx0)}" height="5" rx="2" fill="#8f96a8"/>')
        o.append(f'<rect x="{f(bx0)}" y="{f(by)}" width="{f((bx1 - bx0) * pr)}" height="5" rx="2" fill="#f2b632"/>')
    g = "".join(o)
    if sc != 1.0:
        g = f'<g transform="translate({f(cx)} {f(TAB_Y1)}) scale({sc:.4f}) translate({f(-cx)} {f(-TAB_Y1)})">{g}</g>'
    return g


def chrome(tabs, active, sd=0):
    o = [f'<rect x="0" y="0" width="{SW}" height="{TAB_Y1}" fill="{CHROME}"/>',
         f'<rect x="0" y="{TAB_Y1 - 2}" width="{SW}" height="2" fill="{CHROME_SH}"/>']
    lay, w0 = tab_layout(tabs)
    for i, (x, w, tb) in enumerate(lay):
        if i != active:
            o.append(tab_svg(x, w, tb, w0, False, sd + 40 + i * 7))
    o.append(f'<rect x="0" y="{TAB_Y1}" width="{SW}" height="{TOOL_Y1 - TAB_Y1}" fill="{PAGE}"/>')
    if 0 <= active < len(lay):
        x, w, tb = lay[active]
        o.append(tab_svg(x, w, tb, w0, True, sd + 40 + active * 7))
    # «+», адресная строка: кружки-кнопки и пустая строка с замком
    px = lay[-1][0] + lay[-1][1] + 18 if lay else TAB_X0 + 20
    px = min(px, SW - 30)
    o.append(line([(px - 8, (TAB_Y0 + TAB_Y1) / 2), (px + 8, (TAB_Y0 + TAB_Y1) / 2)], 2.6, "#e8ebf2", seed=sd + 5, taper=.1, wmin=.8))
    o.append(line([(px, (TAB_Y0 + TAB_Y1) / 2 - 8), (px, (TAB_Y0 + TAB_Y1) / 2 + 8)], 2.6, "#e8ebf2", seed=sd + 6, taper=.1, wmin=.8))
    yb = (TAB_Y1 + TOOL_Y1) / 2
    for k in range(3):
        o.append(f'<circle cx="{26 + k * 30}" cy="{f(yb)}" r="9" fill="{BAR}"/>')
    o.append(shape(rect_pts(118, yb - 17, SW - 70, yb + 17, 17), BAR, "", w=1.8, seed=sd + 7, var=.08, ink_color="#b8b4aa"))
    o.append(shape(rect_pts(134, yb - 6, 146, yb + 6, 2), "#8c8f99", "", ink=False))
    o.append(f'<rect x="158" y="{f(yb - 4)}" width="190" height="8" rx="4" fill="{GREYL}"/>')
    for k in range(3):
        o.append(f'<circle cx="{SW - 40}" cy="{f(yb - 9 + k * 9)}" r="2.8" fill="#8c8f99"/>')
    o.append(f'<rect x="0" y="{TOOL_Y1 - 2}" width="{SW}" height="2" fill="{PAGE_SH}"/>')
    return "".join(o)


def tab_center(tabs, i):
    lay, _ = tab_layout(tabs)
    x, w, _ = lay[i]
    return x + w / 2, (TAB_Y0 + TAB_Y1) / 2


# ── содержимое вкладок: локально в прямоугольнике (0, TOOL_Y1)–(SW, SH)
CY0 = TOOL_Y1


def panel_mail(t, k=1.0, sd=0):
    o = [f'<rect x="0" y="{CY0}" width="200" height="{SH - CY0}" fill="#f1eee6"/>']
    for r in range(7):
        y = CY0 + 34 + r * 58
        o.append(f'<circle cx="34" cy="{y}" r="13" fill="{["#f0a02a", "#3f7fd6", "#36a35a", "#c86bc4", "#e0443a", "#5fb1ec", "#f2b632"][r]}"/>')
        o.append(f'<rect x="56" y="{y - 10}" width="{110 - r * 7 % 30}" height="8" rx="4" fill="#9a978f"/>')
        o.append(f'<rect x="56" y="{y + 4}" width="{124 - r * 11 % 40}" height="6" rx="3" fill="{GREYL}"/>')
    s = .5 + .5 * back_out(k, 2.0)
    cx, cy = 490, 330
    E = [(cx - 170, cy - 110, 1), (cx + 170, cy - 110, 1), (cx + 170, cy + 110, 1), (cx - 170, cy + 110, 1)]
    inner = blob([(cx - 170, cy + 40), (cx + 170, cy + 40), (cx + 170, cy + 110), (cx - 170, cy + 110)], "#ece4d2", .9)
    inner += line([(cx - 170, cy + 110), (cx - 40, cy + 10), (cx + 40, cy + 10), (cx + 170, cy + 110)], 3.2, "#c9bfa9", seed=sd + 5)
    env = shape(E, "#fff8ea", inner, w=5.0, seed=sd + 3)
    env += shape([(cx - 170, cy - 110, 1), (cx + 170, cy - 110, 1), (cx, cy + 20, 1)], "#f6ecd6", blob([(cx - 170, cy - 110), (cx + 170, cy - 110), (cx, cy - 60)], "#efe2c6"),
                 w=4.6, seed=sd + 4)
    env += shape(ellipse_pts(cx, cy + 4, 26, 26, 14), "#d8483c", blob(ellipse_pts(cx + 6, cy + 10, 18, 16, 10), "#b5352b", .9), w=3.4, seed=sd + 6)
    env += shape(ellipse_pts(cx + 160, cy - 104, 26, 26, 14), "#e0443a", "", w=3.4, seed=sd + 7)
    env += f'<circle cx="{cx + 160}" cy="{cy - 104}" r="7" fill="#ffffff"/>'
    o.append(f'<g transform="translate({cx} {cy}) scale({s:.4f}) rotate({-6 * (1 - k):.2f}) translate({-cx} {-cy})">{env}</g>')
    return "".join(o)


def panel_doc(t, k=1.0, lines_done=0.62, caret=True, sd=0, rows=9, done_col="#9a978f"):
    o = [f'<rect x="0" y="{CY0}" width="{SW}" height="{SH - CY0}" fill="#e9e6de"/>']
    s = .6 + .4 * back_out(k, 1.6)
    px0, px1, py0 = 170, 610, CY0 + 22
    pg = shape([(px0, py0, 1), (px1, py0, 1), (px1, SH + 40, 1), (px0, SH + 40, 1)], "#ffffff",
               blob([(px1 - 24, py0), (px1, py0), (px1, SH + 40), (px1 - 24, SH + 40)], "#f0eee8"), w=3.0, seed=sd + 1, var=.1)
    pg += f'<rect x="{px0 + 34}" y="{py0 + 30}" width="210" height="16" rx="8" fill="#3f7fd6"/>'
    total = rows * 1.0
    done = lines_done * total
    for r in range(rows):
        y = py0 + 76 + r * 40
        full = (px1 - px0 - 68) * (0.86 if r % 4 == 3 else 1.0)
        u = clamp(done - r)
        if u <= 0:
            pg += f'<rect x="{px0 + 34}" y="{y}" width="{f(full)}" height="11" rx="5.5" fill="#f1efe9"/>'
            continue
        pg += f'<rect x="{px0 + 34}" y="{y}" width="{f(full * u)}" height="11" rx="5.5" fill="{done_col}"/>'
        if u < 1 and caret and (t * 2.2) % 1 < .6:
            pg += f'<rect x="{f(px0 + 36 + full * u)}" y="{y - 6}" width="4" height="23" fill="{INK}"/>'
    o.append(f'<g transform="translate(390 {CY0}) scale({s:.4f}) translate(-390 {-CY0})">{pg}</g>')
    return "".join(o)


def panel_chat(t, k=1.0, sd=0):
    o = [f'<rect x="0" y="{CY0}" width="{SW}" height="{SH - CY0}" fill="#e7efe6"/>']
    bubbles = [(-1, 230, 160), (1, 300, 230), (-1, 200, 300), (1, 250, 370)]
    for i, (side, w, y) in enumerate(bubbles):
        u = back_out(clamp(k * 1.6 - i * .18), 2.0)
        if u <= 0.01:
            continue
        x0 = 60 if side < 0 else SW - 60 - w
        col = "#ffffff" if side < 0 else "#bfe8c3"
        cx, cy = (x0 + (0 if side < 0 else w), y + 22)
        b = shape(rect_pts(x0, y, x0 + w, y + 44, 22), col, "", w=3.0, seed=sd + 10 + i)
        b += f'<rect x="{x0 + 22}" y="{y + 18}" width="{w - 70}" height="9" rx="4.5" fill="{GREYL if side < 0 else "#83c48b"}"/>'
        o.append(f'<g transform="translate({cx} {cy}) scale({u:.4f}) translate({-cx} {-cy})">{b}</g>')
    # «печатает…» — три точки
    u = clamp(k * 1.6 - .8)
    if u > 0:
        x0, y = 60, 440
        b = shape(rect_pts(x0, y, x0 + 120, y + 48, 24), "#ffffff", "", w=3.0, seed=sd + 30)
        for j in range(3):
            hop = max(0.0, math.sin(t * 9 - j * .9)) * 7
            b += f'<circle cx="{x0 + 32 + j * 28}" cy="{f(y + 24 - hop)}" r="8" fill="#8c8f99"/>'
        o.append(f'<g transform="translate({x0} {y + 24}) scale({back_out(u, 2):.4f}) translate({-x0} {-(y + 24)})">{b}</g>')
    return "".join(o)


def panel_video(t, k=1.0, sd=0, prog=0.35):
    o = [f'<rect x="0" y="{CY0}" width="{SW}" height="{SH - CY0}" fill="#1f2230"/>']
    s = .6 + .4 * back_out(k, 2.0)
    cx, cy = SW / 2, CY0 + 190
    g = shape(rect_pts(cx - 100, cy - 68, cx + 100, cy + 68, 34), "#e0443a", blob(rect_pts(cx - 100, cy + 20, cx + 100, cy + 68, 30), "#b8342b", .9),
              w=4.6, seed=sd + 2)
    g += shape([(cx - 30, cy - 42, 1), (cx + 46, cy, 1), (cx - 30, cy + 42, 1)], "#ffffff", "", w=3.6, seed=sd + 3)
    o.append(f'<g transform="translate({cx} {cy}) scale({s:.4f}) translate({-cx} {-cy})">{g}</g>')
    y = SH - 70
    o.append(f'<rect x="40" y="{y}" width="{SW - 80}" height="8" rx="4" fill="#4a4f63"/>')
    o.append(f'<rect x="40" y="{y}" width="{f((SW - 80) * prog)}" height="8" rx="4" fill="#e0443a"/>')
    o.append(f'<circle cx="{f(40 + (SW - 80) * prog)}" cy="{y + 4}" r="11" fill="#ffffff"/>')
    return "".join(o)


def panel_loading(t, sd=0, stuck=0.5):
    """Список «делается»: значок, серая строка и полоска прогресса, застрявшая на половине; крутится ромашка."""
    o = [f'<rect x="0" y="{CY0}" width="{SW}" height="{SH - CY0}" fill="{PAGE}"/>']
    kinds = ["mail", "doc", "chat", "video", "doc", "mail"]
    for r, kd in enumerate(kinds):
        y = CY0 + 46 + r * 72
        o.append(icon(kd, 70, y, 44, sd + 50 + r * 5))
        o.append(f'<rect x="110" y="{y - 16}" width="{150 + (r * 37) % 90}" height="10" rx="5" fill="#9a978f"/>')
        bx0, bx1 = 110, SW - 120
        pr = stuck + .04 * math.sin(r * 1.7)
        o.append(f'<rect x="{bx0}" y="{y + 6}" width="{bx1 - bx0}" height="14" rx="7" fill="#dcd8cd"/>')
        o.append(f'<rect x="{bx0}" y="{y + 6}" width="{f((bx1 - bx0) * pr)}" height="14" rx="7" fill="#f2b632"/>')
        # ромашка-загрузка
        cx = SW - 70
        for j in range(8):
            a = j * math.pi / 4 + t * 5 + r
            c = mix("#c9c6bd", "#55596a", ((j + int(t * 10)) % 8) / 7)
            o.append(f'<circle cx="{f(cx + 14 * math.cos(a))}" cy="{f(y + 2 + 14 * math.sin(a))}" r="4.2" fill="{c}"/>')
    return "".join(o)


PANELS = {"mail": panel_mail, "doc": panel_doc, "chat": panel_chat, "video": panel_video}


def screen_svg(content, tabs=None, active=0, glare=True):
    """Содержимое экрана в локальных координатах SW×SH (обрезано)."""
    cid = lib.clip_rect(0, 0, SW, SH)
    o = [f'<g clip-path="url(#{cid})"><rect width="{SW}" height="{SH}" fill="{PAGE}"/>', content]
    if tabs is not None:
        o.append(chrome(tabs, active))
    o.append("</g>")
    return "".join(o)


# ═════════════════════════════════════ «НОУТБУК СПЕРЕДИ» ═════════════════════════════════════
SCR = (150.0, 360.0)        # левый верх экрана в мире
LID_R = (118.0, 326.0, 962.0, 952.0)


def window_front(sky, t, sun=(330, 150), sun_r=56, moon=False, lights=0.0):
    """Окно на стене за ноутбуком: x 20–600, y 30–640 (низ закрыт крышкой)."""
    x0, y0, x1, y1 = 20, 30, 600, 640
    top, bot, sc = sky
    g = lib.lin_grad([(0, top, 1), (1, bot, 1)])
    cid = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    o = [f'<g clip-path="url(#{cid})"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>']
    if sun is not None:
        sx, sy = sun
        o.append(blob(ellipse_pts(sx, sy, sun_r * 1.9, sun_r * 1.9, 18), sc, .25))
        o.append(shape(ellipse_pts(sx, sy, sun_r, sun_r, 18), sc, "", w=3.0, seed=30, ink=False))
    # облака
    for i, (cx, cy, k) in enumerate([(160, 200, 1.0), (470, 110, .8)]):
        cx += (t * 6) % 40
        c = "#ffffff" if not moon else "#5a5488"
        o.append(blob([(cx - 70 * k, cy + 18 * k), (cx - 50 * k, cy - 10 * k), (cx - 10 * k, cy - 30 * k), (cx + 30 * k, cy - 18 * k), (cx + 66 * k, cy + 4 * k),
                       (cx + 70 * k, cy + 18 * k)], c, .85))
    # дома на горизонте
    for i, (bx, bw, bh) in enumerate([(30, 120, 200), (150, 90, 150), (240, 140, 240), (380, 100, 170), (480, 130, 220)]):
        col = mix("#8c7a92", "#2e2a4a", clamp(lights)) if lights > 0 else "#9b8fa6"
        o.append(f'<rect x="{bx}" y="{y1 - bh}" width="{bw}" height="{bh}" fill="{col}"/>')
        if lights > 0:
            for r in range(int(bh / 40)):
                for c_ in range(int(bw / 34)):
                    if (r * 7 + c_ * 3 + i) % 3:
                        o.append(f'<rect x="{bx + 10 + c_ * 34}" y="{y1 - bh + 16 + r * 40}" width="14" height="18" fill="{mix(col, '#ffd27a', clamp(lights))}"/>')
    o.append("</g>")
    # рама
    fr = "#f3ead8"
    o.append(shape([(x0 - 18, y0 - 18, 1), (x1 + 18, y0 - 18, 1), (x1 + 18, y1, 1), (x0 - 18, y1, 1)], "none", "", w=0, ink=False))
    for (a, b, c, d) in [(x0 - 18, y0 - 18, x1 + 18, y0), (x0 - 18, y0 - 18, x0, y1), (x1, y0 - 18, x1 + 18, y1), ((x0 + x1) / 2 - 8, y0, (x0 + x1) / 2 + 8, y1),
                         (x0, (y0 + y1) / 2 - 8, x1, (y0 + y1) / 2 + 8)]:
        o.append(shape([(a, b, 1), (c, b, 1), (c, d, 1), (a, d, 1)], fr, "", w=3.6, seed=int(a + b)))
    return "".join(o)


def room_back(sky, t, lamp=1.0, sun=(330, 150), lights=0.0):
    o = [f'<rect x="-900" y="-900" width="2900" height="1820" fill="{WALL}"/>']
    o.append(blob([(-900, -900), (2000, -900), (2000, -500), (-900, -500)], WALL_SH, .35))
    o.append(window_front(sky, t, sun=sun, lights=lights))
    # полка справа с книгами и растением
    o.append(shape([(900, 250, 1), (1260, 250, 1), (1260, 274, 1), (900, 274, 1)], WOOD, blob([(900, 264), (1260, 264), (1260, 274), (900, 274)], WOOD_SH), w=3.6, seed=40))
    for i, (bx, bw, bh, c) in enumerate([(930, 30, 120, "#c4553f"), (962, 26, 104, "#3f7fd6"), (990, 34, 128, "#36a35a"), (1026, 28, 96, "#f0a02a")]):
        o.append(shape([(bx, 250 - bh, 1), (bx + bw, 250 - bh, 1), (bx + bw, 250, 1), (bx, 250, 1)], c, blob([(bx + bw * .6, 250 - bh), (bx + bw, 250 - bh), (bx + bw, 250), (bx + bw * .6, 250)], lib.mul(c, (.8, .8, .85))),
                       w=3.0, seed=41 + i))
    pot = [(1090, 190, 1), (1160, 190, 1), (1150, 250, 1), (1100, 250, 1)]
    o.append(shape(pot, "#c96f45", "", w=3.4, seed=48))
    for i, a in enumerate((-50, -20, 10, 40)):
        r = math.radians(a + 4 * osc(t, .4, i))
        tip = (1125 + 70 * math.sin(r), 190 - 70 * math.cos(r))
        o.append(shape([(1125, 190), ((1125 + tip[0]) / 2 - 14, (190 + tip[1]) / 2), tip, ((1125 + tip[0]) / 2 + 14, (190 + tip[1]) / 2)], "#5f9e4a", "", w=2.8, seed=50 + i))
    # стол
    o.append(f'<rect x="-900" y="880" width="2900" height="2000" fill="{WOOD}"/>')
    for k in range(9):
        y = 930 + k * 120 + 20 * math.sin(k * 1.3)
        o.append(line([(-900, y), (200, y + 10), (900, y - 8), (2000, y + 6)], 3.2, WOOD_GR, seed=60 + k, taper=.05, wmin=.6))
    o.append(f'<rect x="-900" y="870" width="2900" height="16" fill="{WOOD_EDGE}"/>')
    # тёплый свет лампы
    if lamp > 0:
        o.append(blob(ellipse_pts(980, 980, 520, 360, 20), "#ffd27a", .22 * lamp, lib.blur(40)))
    return "".join(o)


def lamp_front(t, on=1.0):
    """Настольная лампа справа за ноутбуком."""
    o = []
    o.append(shape(ellipse_pts(1060, 880, 90, 22, 16), "#2f6f6a", blob(ellipse_pts(1060, 888, 90, 14, 12), "#224f4b"), w=3.6, seed=70))
    o.append(line([(1060, 874), (1030, 640), (980, 520)], 16, "#2f6f6a", seed=71, taper=.05, wmin=.9))
    shade = [(900, 470), (1020, 450), (1060, 560, 1), (880, 600, 1)]
    o.append(shape(shade, "#3a8b84", blob([(980, 460), (1020, 450), (1060, 560), (980, 580)], "#2b6c66"), w=4.0, seed=72))
    if on > 0:
        o.append(blob([(884, 596), (1058, 562), (1000, 610), (930, 620)], "#fff2c0", on))
    return "".join(o)


def laptop_front(screen, glow=1.0, sd=0, deck_extra=""):
    """Ноутбук лицом к зрителю: крышка с экраном (screen — SVG в координатах экрана), клавиатура в перспективе."""
    x0, y0, x1, y1 = LID_R
    o = []
    # тень на столе
    o.append(blob([(70, 1250), (1010, 1250), (1060, 1300), (40, 1300)], "#5a3a1f", .35, lib.blur(10)))
    # корпус-основание
    deck = [(108, 950, 1), (972, 950, 1), (1042, 1252, 1), (38, 1252, 1)]
    inner = blob([(38, 1220), (1042, 1220), (1042, 1252), (38, 1252)], DECK_SH, .9)
    inner += blob([(108, 950), (972, 950), (980, 985), (100, 985)], DECK_SH, .7)
    o.append(shape(deck, DECK, inner, w=5.0, seed=sd + 1))
    o.append(shape([(38, 1252, 1), (1042, 1252, 1), (1036, 1274, 1), (44, 1274, 1)], DECK_SH2, "", w=4.4, seed=sd + 2))

    def L(u, v):  # u 0..1 по ширине, v 0..1 от петли к краю
        xl = 108 + (38 - 108) * v
        xr = 972 + (1042 - 972) * v
        return (xl + (xr - xl) * u, 950 + 302 * v)

    # клавиши: 5 рядов
    for r in range(5):
        v0, v1 = .10 + r * .1, .10 + r * .1 + .082
        n = 13 if r < 4 else 7
        for c in range(n):
            if r == 4:
                widths = [.08, .08, .1, .38, .1, .08, .08]
                ua = .08 + sum(widths[:c]) * 0.84 / .9
                ub = ua + widths[c] * .84 / .9 - .008
            else:
                ua = .08 + c * .84 / n
                ub = ua + .84 / n - .008
            pts = [L(ua, v0) + (1,), L(ub, v0) + (1,), L(ub, v1) + (1,), L(ua, v1) + (1,)]
            o.append(f'<path d="{fill_d(pts)}" fill="{KEY}"/>')
            o.append(f'<path d="{fill_d([L(ua, v1 - .014), L(ub, v1 - .014), L(ub, v1), L(ua, v1)])}" fill="{KEY_SH}"/>')
    # тачпад
    tp = [L(.36, .66) + (1,), L(.64, .66) + (1,), L(.65, .95) + (1,), L(.35, .95) + (1,)]
    o.append(shape(tp, "#bfc3ce", blob([L(.35, .9), L(.65, .9), L(.65, .95), L(.35, .95)], DECK_SH, .8), w=3.0, seed=sd + 3, var=.1))
    o.append(deck_extra)
    # крышка
    lid = rect_pts(x0, y0, x1, y1, 26)
    inner = blob([(x0, y1 - 26), (x1, y1 - 26), (x1, y1), (x0, y1)], LID_SH, .9)
    o.append(shape(lid, LID, inner, w=5.4, seed=sd + 4))
    o.append(f'<circle cx="540" cy="343" r="5" fill="#1b1e27"/><circle cx="539" cy="342" r="1.6" fill="#5c6a8a"/>')
    o.append(f'<g transform="translate({SCR[0]} {SCR[1]})">{screen}</g>')
    o.append(f'<rect x="{SCR[0]}" y="{SCR[1]}" width="{SW}" height="{SH}" fill="none" stroke="#15171f" stroke-width="3"/>')
    # блик стекла
    o.append(blob([(SCR[0] + 520, SCR[1]), (SCR[0] + 640, SCR[1]), (SCR[0] + 420, SCR[1] + SH), (SCR[0] + 300, SCR[1] + SH)], "#ffffff", .05))
    # свечение экрана на столе и клавишах
    if glow > 0:
        o.append(blob([(150, 960), (930, 960), (1000, 1200), (80, 1200)], "#dfe8ff", .08 * glow))
    return "".join(o)


def vignette(col="#2a1408", a=.4):
    g = lib.rad_grad([(0, col, 0), (.62, col, 0), (1, col, a)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def scr_to_world(p):
    return (SCR[0] + p[0], SCR[1] + p[1])


# ═════════════════════════════════════ s01 — хук: вкладки множатся ═════════════════════════════════════
KINDS = ["doc", "mail", "chat", "video", "doc", "mail", "video", "chat", "doc", "mail", "chat", "video", "doc", "doc", "mail", "video",
         "chat", "mail", "doc", "video"]


def s01_pop_times():
    ts = [-0.6, -0.1]
    for k in range(3, 21):
        ts.append(-0.1 + 1.5 * ((k - 2) / 18) ** 0.62)
    return ts


def s01_tabs(t):
    tabs = []
    for k, t0 in enumerate(s01_pop_times()):
        u = clamp((t - t0) / 0.16)
        if t < t0:
            break
        tabs.append(dict(kind=KINDS[k], pop=u))
    return tabs


def hook_cam(t, hit):
    """Влёт 1/(1+0.4) → 1 за 0.22 с с перелётом и поворотом; второй удар +8 % на hit."""
    T = 0.22
    if t < T:
        u = t / T
        z = 1 / 1.4 + (1.05 - 1 / 1.4) * ease_out(u, 3)
        rot = -3.4 * (1 - ease_out(u, 2))
    else:
        u = t - T
        z = 1 + .05 * math.exp(-u * 10) * math.cos(2 * math.pi * 2.4 * u)
        rot = 1.1 * math.exp(-u * 8) * math.sin(2 * math.pi * 2.0 * u)
    z *= 1 + .08 * max(0.0, kick(t, hit, .5, 1.6))
    z *= 1 + .02 * t            # дрейф внутрь
    return z, rot


def s01(t):
    hit = wt("двадцать")
    z, rot = hook_cam(t, hit)
    cx, cy = 540 + 8 * t, 650 - 12 * t
    z *= 1.3
    set_ink(z)
    tabs = s01_tabs(t)
    n = len(tabs)
    active = n - 1
    # содержимое меняется на каждой второй новой вкладке (не мигает на каждой)
    pts_ = s01_pop_times()
    sw = max(i for i in range(n) if i % 2 == 0 or i == 1)
    kd = tabs[sw]["kind"]
    k = clamp((t - pts_[sw]) / .2)
    active = sw
    k = clamp(.35 + k)
    content = PANELS[kd](t, k=k) if kd != "doc" else panel_doc(t, k=k, lines_done=.35)
    scr = screen_svg(content, tabs, active)
    # курсор щёлкает «+» на каждом новом
    lay, _ = tab_layout(tabs)
    px = min(lay[-1][0] + lay[-1][1] + 18, SW - 30)
    pr = max([bump(t, t0, .12) for t0 in s01_pop_times()[2:]] + [0])
    cur = cursor(SCR[0] + px + 2, SCR[1] + 38, 1.0, pr)
    sky = SKY["eve"]
    w = [room_back(sky, t, lamp=1.0, sun=(250, 560), lights=.8), lamp_front(t), laptop_front(scr), cur]
    # мелкие «вспышки» новых вкладок — штрихи у полосы
    for k_, t0 in enumerate(s01_pop_times()[2:], start=2):
        u = (t - t0) / .18
        if 0 < u < 1 and k_ < len(lay):
            x = SCR[0] + lay[k_][0] + lay[k_][1] / 2
            y = SCR[1] + TAB_Y0
            for j, a in enumerate((-60, -90, -120)):
                r = math.radians(a)
                r0, r1 = 14 + 30 * u, 30 + 40 * u
                w.append(line([(x + r0 * math.cos(r), y + r0 * math.sin(r)), (x + r1 * math.cos(r), y + r1 * math.sin(r))], 4 * (1 - u) + 1, "#fff4c8",
                              seed=300 + k_ * 3 + j, taper=.3, wmin=.4))
    body = f'<g transform="{lib.cam(cx, cy, z, rot)}">{"".join(w)}</g>' + vignette()
    return lib.svg(body)


def full_tabs(active=None, grow=2.4, prog=None):
    tabs = [dict(kind=k, pop=1.0) for k in KINDS]
    if prog is not None:
        for i, tb in enumerate(tabs):
            tb["prog"] = prog + .06 * math.sin(i * 2.3)
    if active is not None:
        for i, tb in enumerate(tabs):
            tb["grow"] = 1.0 + (grow - 1.0) * active.get(i, 0.0)
    return tabs


def front_world(t, scr, sky, lamp=1.0, sun=(250, 560), lights=.8, extra="", deck_extra=""):
    return room_back(sky, t, lamp=lamp, sun=sun, lights=lights) + lamp_front(t, lamp) + laptop_front(scr, deck_extra=deck_extra) + extra


# ═════════════════════════════════════ s03 — почта, отчёт, чат, видео ═════════════════════════════════════
S03_CLICKS = [(None, 15, "video"), (wt("почта"), 1, "mail"), (wt("отчёт"), 4, "doc"), (wt("чат"), 7, "chat"), (wt("видео"), 11, "video"),
              (wt("отчёт", 6.5), 4, "doc")]


def s03(t):
    clicks = [(c[0] if c[0] is not None else -10.0, c[1], c[2]) for c in S03_CLICKS]
    cur_i = max(i for i, c in enumerate(clicks) if c[0] <= t)
    tc, idx, kd = clicks[cur_i]
    prev_idx = clicks[cur_i - 1][1] if cur_i > 0 else idx
    # активная вкладка расширяется за 0.12 с
    ug = ease_out(clamp((t - tc) / .12))
    act = {idx: ug}
    if prev_idx != idx:
        act[prev_idx] = 1 - ug
    tabs = full_tabs(act)
    k = clamp((t - tc) / .28)
    if kd == "doc":
        content = panel_doc(t, k=k, lines_done=.45)
    elif kd == "video":
        content = panel_video(t, k=k, prog=.2 + .05 * (t - tc))
    else:
        content = PANELS[kd](t, k=k)
    # сдвиг содержимого при щелчке (хлёст вбок)
    sh = 60 * (1 - ease_out(clamp((t - tc) / .16), 3)) if tc > 0 else 0
    content = f'<g transform="translate({sh:.2f} 0)">{content}</g>'
    scr = screen_svg(content, tabs, idx)
    # курсор: летит к следующей вкладке перед щелчком
    nxt = clicks[cur_i + 1] if cur_i + 1 < len(clicks) else None
    p_now = tab_center(tabs, idx)
    if nxt is not None:
        tn = nxt[0]
        mv = ease_io(clamp((t - (tn - .26)) / .22))
        p_next = tab_center(tabs, nxt[1])
        px = p_now[0] + (p_next[0] - p_now[0]) * mv
        py = p_now[1] + (p_next[1] - p_now[1]) * mv - 40 * math.sin(math.pi * mv)
    else:
        px, py = p_now
    press = bump(t, tc, .14) if tc > 0 else 0
    cur = cursor(SCR[0] + px + 4, SCR[1] + py + 6, 1.15, press)
    # искорки щелчка
    sp = ""
    u = (t - tc) / .2
    if tc > 0 and 0 < u < 1:
        x, y = SCR[0] + p_now[0], SCR[1] + p_now[1] - 6
        for j, a in enumerate(range(0, 360, 60)):
            r = math.radians(a + 30)
            r0, r1 = 22 + 26 * u, 34 + 36 * u
            sp += line([(x + r0 * math.cos(r), y + r0 * math.sin(r)), (x + r1 * math.cos(r), y + r1 * math.sin(r))], 4 * (1 - u) + 1, "#ffe08a",
                       seed=500 + j, taper=.3, wmin=.4)
    z = 1.3 * (1 + .035 * max(0.0, max(kick(t, c[0], .35, 2.0) for c in clicks if c[0] > 0)))
    z *= 1 + .02 * (t - 4.1)
    cx, cy = 540 + 6 * math.sin(t * 1.3), 662
    rot = .25 * math.sin(t * 1.1)
    set_ink(z)
    w = front_world(t, scr, SKY["eve"], lamp=1.0, lights=.8, extra=sp + cur)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, z, rot)}">{w}</g>' + vignette())


# ═════════════════════════════════════ s14 — закрывает всё, остаётся одна ═════════════════════════════════════
KEEP = 4
T_ZAKR = wt("закрывает")       # 28.92


def s14_close_times():
    order = [i for i in range(20) if i != KEEP]
    singles = [27.62, 27.92, 28.18, 28.42, 28.66]
    rest_order = order[len(singles):]
    rest_order = rest_order[::-1]          # курсор идёт справа налево
    n = len(rest_order)
    t_end = 29.62
    times = {}
    for i, ti in zip(order[:len(singles)], singles):
        times[i] = ti
    for j, i in enumerate(rest_order):
        times[i] = T_ZAKR + .02 + (t_end - T_ZAKR) * (j / (n - 1)) ** 0.8
    return times


def sleeve_hand(tip, press=0.0, sd=0, k=2.0, d=(-0.22, -1.0)):
    """Правая рука Димы в горчичном рукаве снизу справа, указательный палец на тачпаде (кончик в tip)."""
    people.C = people.PAL["dima"]
    C = people.C
    d = np.array(d, float)
    d /= np.linalg.norm(d)
    n = np.array([-d[1], d[0]])
    # кончик указательного в системе кисти: корень (70-16, -25*.95), +16 и три фаланги 66 → ~(136, -24)
    tip_local = np.array([136.0, -23.0])
    Wr = np.array(tip, float) - (d * tip_local[0] + n * tip_local[1]) * k
    Wr = Wr + np.array([0, 5 * press])
    kw = dict(shape_fn=shape, line_fn=line, skin=C["SKIN"], skin_sh=C["SKIN_SH"], skin_sh2=C["SKIN_SH2"], nail=C["NAIL"])
    o = []
    # рукав: от манжеты вниз-вправо за кадр, расширяется
    P = lambda p: (float(p[0]), float(p[1]))
    c0 = Wr - d * 46          # нижний край манжеты
    hw0, hw1 = 96, 150
    far = c0 - d * 700 + np.array([260.0, 0])
    sl = [P(c0 + n * hw0), P(c0 - d * 300 + n * (hw0 + 20) + np.array([90, 0])), P(far + n * hw1), P(far - n * hw1),
          P(c0 - d * 300 - n * (hw0 + 20) + np.array([90, 0])), P(c0 - n * hw0)]
    inner = blob([P(c0 - n * 30), P(c0 - d * 300 - n * 40 + np.array([90, 0])), P(far - n * 60), P(far - n * hw1 - n * 10),
                  P(c0 - d * 300 - n * (hw0 + 30) + np.array([90, 0])), P(c0 - n * (hw0 + 10))], C["TOP_SH"], .9)
    for j, (u, w_) in enumerate(((.18, 60), (.42, 80))):
        p = c0 + (far - c0) * u
        inner += line([P(p + n * w_), P(p - d * 16), P(p - n * (w_ * .6))], 3.2, C["FOLD"], seed=sd + 10 + j, op=.8)
    o.append(shape(sl, C["TOP"], inner, w=5.2, seed=sd + 1))
    # манжета-резинка
    a0, a1 = Wr - d * 4, Wr - d * 50
    cf = [P(a0 + n * 90, ) + (1,), P(a0 - n * 90) + (1,), P(a1 - n * 98) + (1,), P(a1 + n * 98) + (1,)]
    rib = "".join(line([P(a0 - d * (6 + 8 * q) + n * 96), P(a0 - d * (6 + 8 * q) - n * 96)], 1.8, C["TOP_SH2"], seed=sd + 20 + q, op=.85)
                  for q in range(5))
    rib = "".join(line([P(a0 + n * (80 - 22 * q) - d * 2), P(a1 + n * (86 - 24 * q) + d * 2)], 1.8, C["TOP_SH2"], seed=sd + 20 + q, op=.85)
                  for q in range(8))
    o.append(shape(cf, C["TOP_SH"], rib, w=4.6, seed=sd + 2))
    # большой палец прижат сбоку под указательным (виден краем), рисуется под ладонью
    tf = lambda x, y: P(Wr + d * x * k + n * y * k)
    th = band([tf(8, -28), tf(44, -42), tf(74, -42), tf(90, -34)], 26 * k, 19 * k, step=2.5, cap=True)
    o.append(shape(th, C["SKIN"], blob([tf(30, -40), tf(80, -38), tf(92, -30), tf(40, -26)], C["SKIN_SH"], .8), w=3.0, seed=sd + 30))
    o.append(Hand.hand(P(Wr), P(d), flip=1, k=k, curl=(0.0, .86, .92, .95), spread=.04, bend=.05, seed=sd + 40, show_thumb=False, **kw))
    return "".join(o), Wr


def s14(t):
    times = s14_close_times()
    tabs = []
    for i, kd in enumerate(KINDS):
        tc = times.get(i)
        out = clamp((t - tc) / .16) if tc is not None else 0.0
        tabs.append(dict(kind=kd, pop=1.0, out=out, grow=1.0 + 1.4 * (i == KEEP)))
    # следующая закрываемая вкладка — курсор на её крестике
    future = sorted((tc, i) for i, tc in times.items() if tc > t - .05)
    lay, w0 = tab_layout(tabs)
    if future:
        tn, i_n = future[0]
        x, w, _ = lay[i_n]
        tx = x + max(w, 20) - 14 if w > 60 else x + w / 2
        past = [tc for tc in times.values() if tc <= t]
        tp = max(past) if past else 27.3
        mv = ease_io(clamp((t - tp) / max(.06, min(.2, tn - tp - .02))))
        cx_c = getattr(s14, "_lastx", tx)
        px = tx
        py = (TAB_Y0 + TAB_Y1) / 2
    else:
        x, w, _ = lay[KEEP]
        px, py = x + w * .5, TOOL_Y1 + 120
        settle = ease_io(clamp((t - 29.65) / .4))
        px = 650 + (px - 650) * 0 if False else 600 - 160 * settle
        py = (TAB_Y0 + TAB_Y1) / 2 + (260 - (TAB_Y0 + TAB_Y1) / 2) * settle
    press = max([bump(t, tc, .12) for tc in times.values()] + [0.0])
    # содержимое: документ (оставленная вкладка)
    content = panel_doc(t, k=1.0, lines_done=.5, caret=False)
    scr = screen_svg(content, tabs, KEEP)
    cur = cursor(SCR[0] + px, SCR[1] + py, 1.1, press)
    # хлопки закрытых вкладок — штрихи
    sp = ""
    for i, tc in times.items():
        u = (t - tc) / .22
        if 0 < u < 1:
            x, w, _ = lay[i]
            xx, yy = SCR[0] + x + w / 2, SCR[1] + TAB_Y0 + 6
            for j, a in enumerate((-30, -90, -150)):
                r = math.radians(a)
                r0, r1 = 10 + 22 * u, 22 + 30 * u
                sp += line([(xx + r0 * math.cos(r), yy + r0 * math.sin(r)), (xx + r1 * math.cos(r), yy + r1 * math.sin(r))], 3.6 * (1 - u) + 1,
                           "#fff4c8", seed=600 + i * 3 + j, taper=.3, wmin=.4)
    # палец на тачпаде: точка тачпада следует за курсором (маленький ход)
    tpx = 540 + (px - SW / 2) * .14
    tpy = 1180 + (py - 40) * .04
    hand_svg, _ = sleeve_hand((tpx, tpy), press, 700)
    z = 1.1 * (1 + .03 * max([max(0.0, kick(t, tc, .3, 2.0)) for tc in list(times.values())[:5]] + [0.0]))
    z *= 1 + .05 * ease_io(clamp((t - T_ZAKR) / 1.0)) + .01 * (t - 27.55)
    cx, cy = 540, 830 - 40 * ease_io(clamp((t - T_ZAKR) / 1.2))
    set_ink(z)
    w = front_world(t, scr, SKY["day"], lamp=0.0, sun=(330, 170), lights=0.0, extra=sp + cur + hand_svg)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, z, .2 * math.sin(t))}">{w}</g>' + vignette(a=.3))


# ═════════════════════════════════════ s16 — отчёт готов, штамп ═════════════════════════════════════
T_GOTOV = wt("готов")


def stamp(cx, cy, s, rot, sd=0):
    G, GS = "#2fa84f", "#1f7f3a"
    o = []
    ring = ellipse_pts(cx, cy, 120 * s, 120 * s, 28)
    o.append(shape(ring, G, blob(ellipse_pts(cx + 14 * s, cy + 16 * s, 110 * s, 108 * s, 24), GS, .9), w=5.6, seed=sd + 1))
    o.append(shape(ellipse_pts(cx, cy, 92 * s, 92 * s, 24), "#ffffff", "", w=4.0, seed=sd + 2))
    ck = [(cx - 52 * s, cy + 2 * s), (cx - 16 * s, cy + 38 * s), (cx + 56 * s, cy - 40 * s)]
    o.append(line(ck, 30 * s, G, seed=sd + 3, taper=.15, wmin=.7))
    return f'<g transform="rotate({rot:.2f} {cx:.1f} {cy:.1f})">{"".join(o)}</g>'


def s16(t):
    tab = [dict(kind="doc", pop=1.0, grow=1.0)]
    typed = .78 + .22 * ease_out(clamp((t - 32.17) / (T_GOTOV - .1 - 32.17)), 1.4)
    content = panel_doc(t, k=1.0, lines_done=typed, caret=t < T_GOTOV - .05, done_col="#7d7a73")
    u = clamp((t - (T_GOTOV - .12)) / .12)
    over = ""
    if t >= T_GOTOV - .12:
        if t < T_GOTOV:
            sc = 2.6 - 1.6 * ease_in(u, 2)
        else:
            v = t - T_GOTOV
            sc = 1 - .14 * math.exp(-v * 12) * math.cos(2 * math.pi * 3 * v)
        sx, sy = scr_to_world((430, 330))
        over += stamp(sx, sy, sc * .9, -12, 800)
        if t >= T_GOTOV:
            v = (t - T_GOTOV) / .3
            if v < 1:
                for j in range(8):
                    a = math.radians(j * 45 + 20)
                    r0, r1 = 130 + 60 * v, 160 + 90 * v
                    over += line([(sx + r0 * math.cos(a), sy + r0 * math.sin(a)), (sx + r1 * math.cos(a), sy + r1 * math.sin(a))],
                                 6 * (1 - v) + 1.5, "#2fa84f", seed=820 + j, taper=.3, wmin=.4)
    scr = screen_svg(content, tab, 0)
    hit = max(0.0, kick(t, T_GOTOV, .5, 1.8))
    z = (1.24 + .12 * ease_io(clamp((t - 32.17) / .55))) * (1 + .09 * hit) * (1 + .025 * (t - 32.17))
    cx, cy = 540, 560 + 40 * ease_io(clamp((t - 32.17) / .55))
    rot = 1.4 * math.exp(-max(0, t - T_GOTOV) * 7) * math.sin(2 * math.pi * 2 * max(0, t - T_GOTOV)) if t > T_GOTOV else -.4
    set_ink(z)
    w = front_world(t, scr, SKY["noon"], lamp=0.0, sun=(310, 120), lights=0.0, extra=over)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, z, rot)}">{w}</g>' + vignette(a=.25))


SCENES = {"s01": s01, "s03": s03, "s14": s14, "s16": s16}


def frame(sid, t):
    lib.DEFS.clear()
    return SCENES[sid](t)


# ═════════════════════════════════════ «ДИМА ЗА СТОЛОМ» (s02, s15) ═════════════════════════════════════
BS = 0.6
D_HIP = np.array([300.0, 1262.0])
FLOOR_Y = 1480
DESK_Y = 1150            # передний край столешницы
DESK_BACK = 1062
WIN2 = (640, 300, 1060, 740)
# экран ноутбука — параллелограмм: начало (левый верх), орты по ширине и высоте экрана
SO = np.array([505.0, 812.0])
SX = np.array([336.0, -26.0]) / SW
SY = np.array([8.0, 246.0]) / SH


def S2W(p):
    return SO + SX * p[0] + SY * p[1]


def chair(x, seat_y, sd=2300):
    col, sh = "#4a5468", "#343c4d"
    o = []
    bx = x - 150
    back = [(bx - 34, seat_y - 40, 1), (bx - 40, seat_y - 380), (bx - 10, seat_y - 420), (bx + 30, seat_y - 410), (bx + 34, seat_y - 40, 1)]
    o.append(shape(back, col, blob([(bx + 6, seat_y - 410), (bx + 34, seat_y - 410), (bx + 34, seat_y), (bx + 6, seat_y)], sh, .9), w=4.4, seed=sd))
    o.append(shape([(bx + 10, seat_y - 60, 1), (bx + 60, seat_y - 40, 1), (bx + 60, seat_y - 14, 1), (bx + 10, seat_y - 20, 1)], sh, "", w=3.4, seed=sd + 1))
    seat = [(x - 170, seat_y - 6, 1), (x + 120, seat_y - 6, 1), (x + 132, seat_y + 30, 1), (x - 170, seat_y + 30, 1)]
    o.append(shape(seat, col, blob([(x - 180, seat_y + 14), (x + 140, seat_y + 14), (x + 140, seat_y + 34), (x - 180, seat_y + 34)], sh, .9), w=4, seed=sd + 2))
    o.append(shape([(x - 22, seat_y + 30, 1), (x + 2, seat_y + 30, 1), (x + 2, FLOOR_Y - 40, 1), (x - 22, FLOOR_Y - 40, 1)], "#8d92a3", "", w=3.4, seed=sd + 3))
    for k, (a, b) in enumerate(((-150, -10), (130, -10))):
        o.append(shape([(x - 10, FLOOR_Y - 46, 1), (x + a, FLOOR_Y - 14, 1), (x + a, FLOOR_Y - 2, 1), (x - 10, FLOOR_Y - 30, 1)], "#3a3f4e", "", w=3.2, seed=sd + 5 + k))
        o.append(shape(ellipse_pts(x + a, FLOOR_Y + 4, 13, 11, 10), "#23262f", "", w=2.6, seed=sd + 8 + k))
    return "".join(o)


def wall_clock(cx, cy, r, hours, sd=1200):
    o = [shape(ellipse_pts(cx, cy, r, r, 24), "#f6f1e6", blob(ellipse_pts(cx + r * .12, cy + r * .14, r * .9, r * .9, 20), "#e4dccb", .8), w=5.4, seed=sd)]
    for k in range(12):
        a = k * math.pi / 6
        o.append(line([(cx + r * .74 * math.sin(a), cy - r * .74 * math.cos(a)), (cx + r * .86 * math.sin(a), cy - r * .86 * math.cos(a))], 3.6 if k % 3 == 0 else 2.2,
                      seed=sd + 1 + k, taper=.1, wmin=.8))
    ah = hours / 12 * 2 * math.pi
    am = (hours % 1 if hours < 13.001 + 1e-9 else (hours - 13) / 2) * 2 * math.pi
    o.append(line([(cx, cy), (cx + r * .45 * math.sin(ah), cy - r * .45 * math.cos(ah))], 7, seed=sd + 20, taper=.3, wmin=.5))
    o.append(line([(cx, cy), (cx + r * .68 * math.sin(am), cy - r * .68 * math.cos(am))], 5, seed=sd + 21, taper=.3, wmin=.5))
    o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="6" fill="{INK}"/>')
    return "".join(o)


def side_room(t, sky, sun, lights, clock_h, lamp=0.0):
    o = [f'<rect x="-900" y="-900" width="3000" height="2400" fill="{WALL}"/>']
    o.append(blob([(-900, -900), (2100, -900), (2100, 0), (-900, 0)], WALL_SH, .3))
    # окно
    x0, y0, x1, y1 = WIN2
    top, bot, sc = sky
    g = lib.lin_grad([(0, top, 1), (1, bot, 1)])
    cid = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    w = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>']
    if sun is not None:
        sx, sy, sr = sun
        w.append(blob(ellipse_pts(sx, sy, sr * 1.9, sr * 1.9, 18), sc, .25))
        w.append(blob(ellipse_pts(sx, sy, sr, sr, 18), sc))
    for i, (cx, cy, k) in enumerate([(760, 400, .9), (980, 360, .7)]):
        cx += (t * 8) % 30
        c = mix("#ffffff", "#8a7aa8", clamp(lights))
        w.append(blob([(cx - 70 * k, cy + 18 * k), (cx - 50 * k, cy - 10 * k), (cx - 10 * k, cy - 30 * k), (cx + 30 * k, cy - 18 * k), (cx + 66 * k, cy + 4 * k),
                       (cx + 70 * k, cy + 18 * k)], c))
    for i, (bx, bw, bh) in enumerate([(640, 110, 180), (750, 80, 130), (830, 120, 210), (950, 110, 160)]):
        col = mix("#9b8fa6", "#2e2a4a", clamp(lights))
        w.append(f'<rect x="{bx}" y="{y1 - bh}" width="{bw}" height="{bh}" fill="{col}"/>')
        for r in range(int(bh / 40)):
            for c_ in range(int(bw / 34)):
                if (r * 7 + c_ * 3 + i) % 3:
                    w.append(f'<rect x="{bx + 10 + c_ * 34}" y="{y1 - bh + 16 + r * 40}" width="14" height="18" fill="{mix(col, "#ffd27a", clamp(lights))}"/>')
    o.append(f'<g clip-path="url(#{cid})">{"".join(w)}</g>')
    fr = "#f3ead8"
    for (a, b, c, d) in [(x0 - 18, y0 - 18, x1 + 18, y0), (x0 - 18, y0 - 18, x0, y1 + 18), (x1, y0 - 18, x1 + 18, y1 + 18), ((x0 + x1) / 2 - 8, y0, (x0 + x1) / 2 + 8, y1),
                         (x0 - 30, y1, x1 + 30, y1 + 22)]:
        o.append(shape([(a, b, 1), (c, b, 1), (c, d, 1), (a, d, 1)], fr, "", w=3.6, seed=int(a + b)))
    # часы на стене
    o.append(wall_clock(470, 600, 58, clock_h))
    # плинтус и пол
    o.append(f'<rect x="-900" y="1330" width="3000" height="1000" fill="#9a6f48"/>')
    for k in range(6):
        y = 1360 + k * 70 + k * k * 6
        o.append(f'<rect x="-900" y="{y}" width="3000" height="3" fill="#835c3a"/>')
    o.append(shape([(-900, 1310, 1), (2100, 1310, 1), (2100, 1334, 1), (-900, 1334, 1)], "#efe6d4", "", w=3.4, seed=1290))
    return "".join(o)


def desk_back_part(t):
    """Задняя часть стола (ножки, тень под столом) — рисуется до ног героя."""
    o = [blob([(440, 1190), (1240, 1190), (1240, FLOOR_Y), (440, FLOOR_Y)], "#6e4d30", .35)]
    for k, x in enumerate((1170,)):
        o.append(shape([(x, 1120, 1), (x + 34, 1120, 1), (x + 34, FLOOR_Y, 1), (x, FLOOR_Y, 1)], WOOD_SH, "", w=3.6, seed=1400 + k))
    return "".join(o)


def desk_top_part():
    o = []
    top = [(430, DESK_Y, 1), (500, DESK_BACK, 1), (1300, DESK_BACK, 1), (1300, DESK_Y, 1)]
    inner = blob([(430, DESK_Y - 22), (1300, DESK_Y - 22), (1300, DESK_Y), (430, DESK_Y)], WOOD_SH, .5)
    for k in range(3):
        y = DESK_BACK + 22 + k * 26
        inner += line([(480 - k * 20, y), (900, y + 3), (1300, y - 2)], 2.4, WOOD_GR, seed=1410 + k, taper=.05, wmin=.6)
    o.append(shape(top, WOOD, inner, w=4.6, seed=1405))
    o.append(shape([(430, DESK_Y, 1), (1300, DESK_Y, 1), (1300, DESK_Y + 40, 1), (436, DESK_Y + 40, 1)], WOOD_EDGE, "", w=4.4, seed=1406))
    o.append(shape([(446, DESK_Y + 40, 1), (482, DESK_Y + 40, 1), (482, FLOOR_Y, 1), (446, FLOOR_Y, 1)], WOOD_SH,
                   blob([(468, DESK_Y + 40), (482, DESK_Y + 40), (482, FLOOR_Y), (468, FLOOR_Y)], WOOD_EDGE, .8), w=3.6, seed=1407))
    return "".join(o)


def laptop_side(scr, glow=1.0, sd=1500):
    """Ноутбук на столе, экран развёрнут к Диме и к зрителю (3/4)."""
    o = []
    A, B = S2W((0, SH)), S2W((SW, SH))         # петля
    fwd = np.array([-115.0, 48.0])
    # тень
    o.append(blob([tuple(A + fwd + [0, 10]), tuple(B + fwd + [0, 10]), tuple(B + [20, 14]), tuple(A + [0, 10])], "#5a3a1f", .3, lib.blur(6)))
    # основание (клавиатура к Диме)
    deck = [tuple(A) + (1,), tuple(B) + (1,), tuple(B + fwd) + (1,), tuple(A + fwd) + (1,)]
    keys = ""
    for r in range(4):
        for c in range(9):
            u0, u1 = .08 + c * .093, .08 + c * .093 + .08
            v0, v1 = .12 + r * .13, .12 + r * .13 + .1
            q = [A + (B - A) * u + fwd * v for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))]
            keys += f'<path d="{fill_d([tuple(p) + (1,) for p in q])}" fill="{KEY}"/>'
    o.append(shape(deck, DECK, keys, w=4.4, seed=sd + 1))
    o.append(shape([tuple(A + fwd) + (1,), tuple(B + fwd) + (1,), tuple(B + fwd + [0, 12]) + (1,), tuple(A + fwd + [0, 12]) + (1,)], DECK_SH2, "", w=3.6, seed=sd + 2))
    # крышка: рамка вокруг экрана
    m = 22
    TL, TR, BR, BL = S2W((-m, -m)), S2W((SW + m, -m)), S2W((SW + m, SH + m * .5)), S2W((-m, SH + m * .5))
    back = [tuple(TR) + (1,), tuple(TR + [16, 6]) + (1,), tuple(BR + [16, 6]) + (1,), tuple(BR) + (1,)]
    o.append(shape(back, LID_SH, "", w=3.6, seed=sd + 3))
    o.append(shape([tuple(TL) + (1,), tuple(TR) + (1,), tuple(BR) + (1,), tuple(BL) + (1,)], LID, "", w=4.6, seed=sd + 4))
    mtx = f"matrix({SX[0]:.5f} {SX[1]:.5f} {SY[0]:.5f} {SY[1]:.5f} {SO[0]:.3f} {SO[1]:.3f})"
    o.append(f'<g transform="{mtx}">{scr}<rect width="{SW}" height="{SH}" fill="none" stroke="#15171f" stroke-width="5"/></g>')
    if glow > 0:
        o.append(blob([tuple(S2W((0, 0))), tuple(S2W((SW, 0))), tuple(S2W((SW, SH))), tuple(S2W((0, SH)))], "#ffffff", .05))
    return "".join(o)


def dima(pose):
    p = dict(hip=tuple(D_HIP + np.array(pose.get("hip_off", (0, 0)))), scale=BS, lean=pose.get("lean", .12),
             feet={"n": ((560, 1468), 0.0), "f": ((535, 1462), 0.0)}, arms=pose["arms"], hands=pose.get("hands", {}),
             expr=pose.get("expr", {}), head_ang=pose.get("head_ang", 0.0), head_off=pose.get("head_off", (0, 0)), hood=0.0,
             strings=pose.get("strings", (0, 0)))
    return people.draw(p, "dima")


def type_targets(t, calm=True, amp=1.0):
    """Цели кистей на клавиатуре с «печатью»: кисти чуть прыгают по клавишам."""
    A, B = S2W((0, SH)), S2W((SW, SH))
    fwd = np.array([-115.0, 48.0])
    base_n = A + (B - A) * .26 + fwd * .92
    base_f = A + (B - A) * .46 + fwd * .7
    rn = .5 + .5 * math.sin(t * 11.0) * math.sin(t * 3.3 + 1)
    rf = .5 + .5 * math.sin(t * 9.4 + 2) * math.sin(t * 2.7)
    jn = np.array([8 * math.sin(t * 2.1), -10 * max(0, math.sin(t * 13.0)) * amp])
    jf = np.array([8 * math.sin(t * 1.7 + 1), -10 * max(0, math.sin(t * 12.0 + 1.3)) * amp])
    return base_n + jn, base_f + jf


def side_frame(t, cam, A):
    set_ink(cam[2])
    w = [side_room(t, A["sky"], A.get("sun"), A.get("lights", 0.0), A["clock_h"], A.get("lamp", 0.0))]
    w.append(A.get("on_wall", ""))
    w.append(desk_back_part(t))
    d = A["dima"]
    w.append(chair(D_HIP[0], D_HIP[1] + 4))
    w.append(d.get("legs", ""))
    w.append(desk_top_part())
    w.append(A.get("on_desk_back", ""))
    w.append(laptop_side(A["scr"]))
    w.append(A.get("on_desk", ""))
    w.append(d["arm_f"])
    w.append(d["body"])
    w.append(d["arm_n"])
    w.append(A.get("front", ""))
    body = f'<g transform="{lib.cam(*cam)}">{"".join(w)}</g>'
    if A.get("grade", 0) > 0:
        body += f'<rect width="1080" height="1920" fill="#2a2060" opacity="{A["grade"]:.3f}"/>'
    if A.get("lamp", 0) > 0:
        g = lib.rad_grad([(0, "#ffcf7a", .28 * A["lamp"]), (1, "#ffcf7a", 0)], 820, 900, 700)
        body += f'<rect width="1080" height="1920" fill="url(#{g})"/>'
    return lib.svg(body + vignette(a=.35))


def cloud(cx, cy, k, t, sd=1700):
    """Серое облачко над головой с моросью."""
    if k <= 0.01:
        return ""
    pts = [(-90, 20), (-100, -10), (-70, -40), (-30, -50), (0, -70), (40, -60), (70, -40), (100, -20), (96, 16), (60, 30), (0, 34), (-50, 30)]
    c = shape([(x, y) for x, y in pts], "#9ea3b2", blob([(-96, 6), (96, 6), (96, 34), (-96, 34)], "#868b9b", .9) +
              line([(-40, -20), (-10, -32), (20, -26)], 3, "#c3c7d2", seed=sd + 2, op=.9), w=4.4, seed=sd)
    rain = ""
    for j in range(5):
        x = -60 + j * 30
        ph = (t * 2.2 + j * .37) % 1
        y0 = 40 + ph * 70
        rain += line([(x + 4, y0), (x, y0 + 18)], 3.4, "#6f9fd8", seed=sd + 10 + j, taper=.2, wmin=.6)
    sc = back_out(k, 2.4) if k < 1 else 1.0
    return f'<g transform="translate({f(cx)} {f(cy)}) scale({sc:.4f})">{rain if k >= 1 else ""}{c}</g>'


# ═════════════════════════════════════ s02 — за день ни одной ═════════════════════════════════════
T_ZA = wt("за")              # 2.24
T_DEN = wt("день")           # 2.48
T_ODNOY = wt("одной")        # 3.44


def s02(t):
    ev = smooth(T_ZA - .05, T_DEN + .2, t)           # день → вечер
    sky = sky_mix("day", "eve", ev)
    sun = (720 + 160 * ev, 380 + 330 * ev, 46)
    clock_h = 13.0 + 6.0 * ev + .01 * t
    lamp = smooth(T_DEN + .2, T_DEN + .28, t)
    tabs = full_tabs(prog=.5)
    for i, tb in enumerate(tabs):
        tb["kind"] = KINDS[i]
    scr = screen_svg(panel_loading(t), tabs, 0)
    # руки: печатает → ближняя рука поднимается под щёку → голова падает
    tn, tf_ = type_targets(t, amp=1.0 - smooth(2.8, 3.1, t))
    u_up = ease_io(clamp((t - 3.02) / .34))
    drop = 0.0 if t < T_ODNOY else 1 - math.exp(-(t - T_ODNOY) * 14) * math.cos(2 * math.pi * 2.4 * (t - T_ODNOY))
    cheek = np.array([338.0, 1046.0]) + np.array([-4 * drop, 16 * drop])
    near = tn * (1 - u_up) + cheek * u_up
    hn = dict(kind="open", flip=1, dir=(.95, -.05), curl=(.35, .4, .45, .5), spread=.08, thumb=.5, bend=.15)
    if u_up > 0:
        d0 = np.array([.95, -.05])
        d1 = np.array([-.2, -1.0])
        dd = d0 * (1 - u_up) + d1 * u_up
        hn = dict(kind="open", flip=1 if u_up < .5 else -1, dir=tuple(dd), curl=(.15 + .2 * u_up, .2 + .2 * u_up, .3 + .2 * u_up, .35 + .2 * u_up), spread=.06, thumb=.3, bend=.15)
    hf = dict(kind="open", flip=1, dir=(.95, -.1), curl=(.35, .4, .45, .5), spread=.08, thumb=.5, bend=.15)
    head_ang = -.02 + .05 * math.sin(t * 1.3) - .34 * drop * (1 if t >= T_ODNOY else 0)
    blink = clamp(1 - abs(t - 1.9) / .08) if abs(t - 1.9) < .08 else 0.0
    if t < T_ODNOY:
        expr = dict(lid=.28, look=(.55, .2), closed=blink, brows="tired", mouth="tired")
    else:
        expr = dict(lid=.12, look=(.5, .45), closed=clamp(1 - abs(t - 4.05) / .1) if abs(t - 4.05) < .1 else 0.0, brows="worry", mouth="flat")
    pose = dict(arms={"n": ("ik", tuple(near), -1), "f": ("ik", tuple(tf_), -1)}, hands={"n": hn, "f": hf}, expr=expr, head_ang=head_ang,
                head_off=(-16 * drop, 30 * drop), lean=.12 - .03 * u_up, strings=(-60 * u_up, 0))
    d = dima(pose)
    hd = d["head"]
    if os.environ.get("DBG"):
        print("head", hd, "wr", d["wrist"])
    ck = clamp((t - T_ODNOY) / .3)
    front = cloud(hd[0] - 10, hd[1] - 175 - 8 * math.sin(t * 2), ck, t) if t >= T_ODNOY else ""
    k = ease_io(clamp((t - 1.3) / 3.4))
    cam = (520 - 10 * k, 990 - 20 * k, 1.75 + .14 * k, .3 * math.sin(t * .9))
    A = dict(sky=sky, sun=sun, lights=ev, clock_h=clock_h, lamp=lamp, scr=scr, dima=d, front=front, grade=.14 * ev)
    return side_frame(t, cam, A)


SCENES["s02"] = s02


# ═════════════════════════════════════ s15 — одна вкладка, полчаса ═════════════════════════════════════
T_POLCHASA = wt("полчаса")       # 31.56


def kitchen_timer(cx, by, t, t_start, sd=1800):
    """Кухонный таймер на столе: корпус-томат, экран 7-сегментный; с t_start тикает (цифры, качание, мигание «:»)."""
    if t < t_start:
        secs = 1800
    else:
        secs = 1800 - int((t - t_start) / 1.0 + .7)
    txt = f"{secs // 60:02d}{':' if (t < t_start or (t - t_start) % 1 < .6) else ' '}{secs % 60:02d}"
    ticks = [t_start + .3 + k for k in range(4)]
    wob = sum(kick(t, tk, .3, 3.0) for tk in [t_start] + ticks) if t >= t_start else 0.0
    ang = 3.5 * wob
    jump = -14 * bump(t, t_start, .26)
    w, h = 176, 112
    x0, y0 = cx - w / 2, by - h
    o = [blob(ellipse_pts(cx, by + 2, w * .55, 9, 14), "#5a3a1f", .3, lib.blur(3))]
    g = []
    g.append(shape([(x0 + 14, y0 - 12, 1), (x0 + 40, y0 - 12, 1), (x0 + 40, y0 + 2, 1), (x0 + 14, y0 + 2, 1)], "#f2e6c8", "", w=3, seed=sd + 1))
    g.append(shape([(x0 + w - 44, y0 - 12, 1), (x0 + w - 18, y0 - 12, 1), (x0 + w - 18, y0 + 2, 1), (x0 + w - 44, y0 + 2, 1)], "#f2e6c8", "", w=3, seed=sd + 2))
    g.append(shape(rect_pts(x0, y0, x0 + w, by, 26), "#e2553f", blob(rect_pts(x0, by - 30, x0 + w, by, 22), "#b93f2e", .9) +
                   blob([(x0 + 14, y0 + 10), (x0 + 50, y0 + 8), (x0 + 30, y0 + 30)], "#f39a85", .8), w=4.6, seed=sd + 3))
    g.append(shape(rect_pts(x0 + 12, y0 + 18, x0 + w - 12, y0 + 82, 10), "#1f2a24", "", w=3.4, seed=sd + 4))
    digits, ww = sevenseg(txt, 0, 0, 20, 42, 6, "#c4f58a", ghost="#27302a", glow=.3, glow_col="#9be05a")
    tx = cx - ww / 2
    g.append(f'<g transform="translate({tx:.1f} {y0 + 29})">{digits}</g>')
    body = "".join(g)
    o.append(f'<g transform="translate(0 {jump:.2f}) rotate({ang:.2f} {cx} {by})">{body}</g>')
    # «тик» — штрихи у корпуса
    for tk in ([t_start] + ticks):
        u = (t - tk) / .25
        if 0 < u < 1:
            for j, a in enumerate((-150, -120, -60, -30)):
                r = math.radians(a)
                rr0, rr1 = 90 + 20 * u, 110 + 30 * u
                o.append(line([(cx + rr0 * math.cos(r), by - 60 + rr0 * math.sin(r) * .8), (cx + rr1 * math.cos(r), by - 60 + rr1 * math.sin(r) * .8)],
                              4 * (1 - u) + 1, INK, seed=sd + 20 + j, taper=.3, wmin=.4))
    return "".join(o)


def s15(t):
    t0 = 29.76
    tabs = [dict(kind="doc", pop=1.0)]
    done = .25 + .3 * clamp((t - t0) / 2.8)
    scr = screen_svg(panel_doc(t, k=1.0, lines_done=done), tabs, 0)
    tn, tf_ = type_targets(t, amp=.8)
    hn = dict(kind="open", flip=1, dir=(.95, -.05), curl=(.35, .4, .45, .5), spread=.08, thumb=.5, bend=.15)
    hf = dict(kind="open", flip=1, dir=(.95, -.1), curl=(.35, .4, .45, .5), spread=.08, thumb=.5, bend=.15)
    bl = 0.0
    for tb in (30.5, 32.0):
        if abs(t - tb) < .08:
            bl = 1 - abs(t - tb) / .08
    expr = dict(lid=.55, look=(.6, .18), closed=bl, brows="calm", mouth="smile", smile=.35)
    pose = dict(arms={"n": ("ik", tuple(tn), -1), "f": ("ik", tuple(tf_), -1)}, hands={"n": hn, "f": hf}, expr=expr,
                head_ang=-.03 + .03 * math.sin(t * 1.7), lean=.14)
    d = dima(pose)
    cat_blink = 0.0
    for tb, du in ((30.9, .5), (32.2, .16)):
        if abs(t - tb) < du / 2:
            cat_blink = 1 - abs(t - tb) / (du / 2)
    catsvg = Cat.draw(800, 762, .37, t, look=(-.8, .5), blink=cat_blink, tilt=3 * math.sin(t * .8), tail=2 * math.sin(t * 1.3))
    timer = kitchen_timer(808, 1152, t, T_POLCHASA)
    k = ease_io(clamp((t - t0) / 2.8))
    cam = (612 + 6 * k, 975 + 5 * k, 1.5 + .12 * k + .03 * bump(t, T_POLCHASA, .4), .25 * math.sin(t * .8))
    A = dict(sky=sky_mix("day", "noon", .3), sun=(760, 400, 46), lights=0.0, clock_h=10.2 + .01 * (t - t0), lamp=0.0, scr=scr, dima=d,
             on_wall=catsvg, front=timer)
    return side_frame(t, cam, A)


SCENES["s15"] = s15
