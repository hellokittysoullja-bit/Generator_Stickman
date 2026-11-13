"""Сцена room рилса 28 «телефон в другой комнате» (s01 s04 s14): вечер, торшер, Дима сидит на диване с раскрытым
учебником на коленях (поза B: обе кисти придерживают страницы), вокруг головы летают карточки с английскими словами.
Герои и кот — рилса 24/26 (heroes24 + правки ушей и пледа из heroes26e). Карточки — две копии каждой: в слое L_fxb
(за головой, под Димой) и в L_fx (перед лицом); JS показывает ту, что ближе к зрителю.
Запуск: python3 heroes28e.py → heroes28e.html (анимация — template28e.html)."""
import base64
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import heroes26e  # noqa: E402,F401  (правки ушей кота и пледа рилса 26 — ставятся при импорте)
import heroes24 as H  # noqa: E402
from heroes24 import shape, blob, line, rect_pts, blur, HOOD_SH, SKIN, SKIN_SH  # noqa: E402
from heroes26e import arm_parts, cat_shadow  # noqa: E402
from ink import fill_d  # noqa: E402

_front24 = heroes26e._front24

# ─── учебник на коленях: твёрдая обложка (синяя) выступает из-под разворота, страницы с текстом-полосками
BK_BL, BK_BR, BK_FR, BK_FL = np.array([206.0, 1150.0]), np.array([432.0, 1158.0]), np.array([448.0, 1232.0]), np.array([186.0, 1222.0])


def bkp(x, y, d=(0.0, 0.0)):
    top = BK_BL + (BK_BR - BK_BL) * x
    bot = BK_FL + (BK_FR - BK_FL) * x
    return tuple(top + (bot - top) * y + np.array(d))


def text_lines(x0, x1, seed, pic=False):
    rs = np.random.RandomState(seed)
    g = []
    rows = [.13, .23, .33, .43, .53, .63, .73, .83]
    for k, y in enumerate(rows):
        if pic and k in (2, 3, 4):
            continue
        a = x0 + (.04 if k == 0 else 0)
        b = x1 - rs.uniform(0, .12) if k % 3 == 2 else x1
        u = a
        while u < b - .02:
            v = min(b, u + rs.uniform(.06, .16))
            g.append(line([bkp(u, y), bkp(v, y + .004)], 2.2, "#8f8a9e", seed=seed + k * 13 + int(u * 100), taper=.1, wmin=.8, op=.95))
            u = v + .025
    if pic:   # маленькая картинка на левой странице (яблоко в рамке)
        fr = [bkp(x0, .27) + (1,), bkp(x0 + .17, .27) + (1,), bkp(x0 + .17, .57) + (1,), bkp(x0, .57) + (1,)]
        cx, cy = np.array(bkp(x0 + .085, .43))
        ap = [(cx - 9, cy - 4), (cx - 2, cy - 9), (cx + 8, cy - 6), (cx + 10, cy + 4), (cx + 2, cy + 10), (cx - 8, cy + 6)]
        g.append(shape(fr, "#e7f0f4", shape(ap, "#e0504a", "", w=2.0, seed=seed + 300), w=2.4, seed=seed + 301))
        g.append(line([bkp(x0 + .2, .33), bkp(x0 + .3, .33)], 2.2, "#8f8a9e", seed=seed + 302, taper=.1, wmin=.8))
        g.append(line([bkp(x0 + .2, .43), bkp(x0 + .27, .43)], 2.2, "#8f8a9e", seed=seed + 303, taper=.1, wmin=.8))
    return "".join(g)


def textbook():
    s = []
    pc = H.clip_of(H.REG["plaid"])
    s.append(f'<g clip-path="url(#{pc})">' + blob([bkp(-.04, -.06, (4, 6)), bkp(1.04, -.06, (4, 6)), bkp(1.05, 1.1, (4, 8)),
                                                     bkp(-.05, 1.1, (4, 8))], "#0d160f", .5, blur(6)) + "</g>")
    # обложка выступает на 6 px со всех сторон, корешок посередине
    cov = [bkp(-.03, -.07) + (1,), bkp(.5, -.05) + (1,), bkp(1.03, -.07) + (1,), bkp(1.035, 1.12) + (1,), bkp(.5, 1.1) + (1,),
           bkp(-.035, 1.12) + (1,)]
    s.append(shape(cov, "#2f6aa8", blob([bkp(-.04, .95), bkp(1.04, .95), bkp(1.04, 1.13), bkp(-.04, 1.13)], "#1f4c7e", .9), w=4.2, seed=1501))
    # торцы страниц снизу
    for side, sd in ((0, 1502), (1, 1503)):
        a, b = (0, .5) if side == 0 else (.5, 1)
        s.append(shape([bkp(a, 1) + (1,), bkp(b, 1) + (1,), bkp(b, 1, (0, 7)) + (1,), bkp(a, 1, (0, 7)) + (1,)], "#e6dfcf",
                       line([bkp(a + .03, 1, (0, 3.5)), bkp(b - .03, 1, (0, 3.5))], 1.2, "#bfb6a2", seed=sd + 10, taper=.05, wmin=.9),
                       w=3.0, seed=sd))
    # левая и правая страницы, у корешка — тень изгиба
    s.append(shape([bkp(0, 0) + (1,), bkp(.25, -.025), bkp(.5, .02) + (1,), bkp(.5, 1) + (1,), bkp(.25, .985), bkp(0, 1) + (1,)], "#f7f2e6",
                   text_lines(.05, .44, 1510, pic=True) + blob([bkp(.4, 0), bkp(.5, 0), bkp(.5, 1), bkp(.4, 1)], "#d8cfba", .55), w=3.8, seed=1504))
    s.append(shape([bkp(.5, .02) + (1,), bkp(.75, -.025), bkp(1, 0) + (1,), bkp(1, 1) + (1,), bkp(.75, .985), bkp(.5, 1) + (1,)], "#f7f2e6",
                   text_lines(.56, .95, 1530) + blob([bkp(.5, 0), bkp(.58, 0), bkp(.58, 1), bkp(.5, 1)], "#d8cfba", .5), w=3.8, seed=1505))
    s.append(line([bkp(.5, .02), bkp(.5, 1)], 2.4, "#6a6170", seed=1506, taper=.2, wmin=.6, op=.9))
    return "".join(s)


def right_flat_hand(cx, cy, ang, seed):
    """Правая кисть ладонью вниз: зеркало flat_hand (большой палец к зрителю-сверху), пальцы смотрят влево."""
    return f'<g transform="translate({cx} {cy}) scale(-1 1) translate({-cx} {-cy})">' + H.flat_hand(cx, cy, ang, seed=seed) + "</g>"


def front28():
    s = [cat_shadow(), _front24()]
    s.append('<g id="pose_B" style="display:none">')
    s.append(textbook())
    up, fore = arm_parts(H.L_S, (150, 1196), (214, 1206), seed=940)
    s.append(up + fore)
    s.append(H.hand_s(H.flat_hand, 240, 1200, 4, 950, 1.0))
    up, fore = arm_parts(H.R_S, (528, 1218), (452, 1204), seed=960)
    s.append(up + fore)
    s.append(right_flat_hand(426, 1200, 4, 990))
    s.append("</g>")
    return "".join(s)


H.front_dima = front28

# ─── карточки слов
WORDS = ["apple", "window", "tired", "river", "honest", "borrow", "quiet", "remember", "bridge", "always", "cloud", "answer"]
CARD_COLS = ["#fbf6ea", "#fff3c4", "#e6f1fb", "#fde4e0", "#e7f6e3", "#fbf6ea"]
NCARD = len(WORDS)


def card(i):
    w, h = 132, 74
    pts = rect_pts(-w / 2, -h / 2, w / 2, h / 2, 9)
    col = CARD_COLS[i % len(CARD_COLS)]
    inner = blob(rect_pts(-w / 2, h / 2 - 12, w / 2, h / 2), "#000000", .10)
    inner += blob(rect_pts(-w / 2, -h / 2, w / 2, -h / 2 + 9), "#d9524a" if i % 3 == 0 else ("#3a86c8" if i % 3 == 1 else "#4aa65a"), .9)
    word = WORDS[i]
    fs = 30 if len(word) <= 6 else 25
    txt = (f'<text x="0" y="{fs * .36 + 3:.1f}" text-anchor="middle" font-family="SH" font-size="{fs}" fill="#22202c">{word}</text>')
    return shape(pts, col, inner, w=3.4, seed=1600 + i) + txt


def cards(prefix):
    return "".join(f'<g id="{prefix}{i}" style="display:none">{card(i)}</g>' for i in range(NCARD))


def glints():
    return "".join(f'<g id="gl{i}" style="display:none">{H.spark(40 + i, r=22, col="#ffe27a")}</g>' for i in range(NCARD))


FILT = ('<filter id="fCard" x="-500" y="-500" width="2080" height="2920" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">'
        '<feColorMatrix type="matrix" values=".93 .03 0 0 0  .02 .84 .02 0 0  0 .02 .74 0 0  0 0 0 1 0"/></filter>')


def build():
    H.light_defs()
    H.DEFS.append(FILT)
    a_dima = '<g id="dima_all"><g id="dima_lean">' + H.dima_back() + f'<g id="dima_head_pose">{H.dima_head()}</g></g></g>'
    a_plaid = H.plaid() + H.front_dima()
    a_cat = H.cat_art()
    layers = [f'<g id="L_fxb" style="isolation:isolate"><g filter="url(#fCard)">{cards("cb")}</g></g>']
    for name, art, lit, top in [("dima", a_dima, H.lights_dima(), ""),
                                ("plaid", a_plaid, H.lights_plaid(), ""),
                                ("cat", a_cat, H.lights_cat(), H.cat_eyes() + H.cat_flame()),
                                ("fx", "", "", f'<g filter="url(#fCard)">{cards("cf")}</g>{glints()}')]:
        if art:
            m = H.mask_of(f"A_{name}")
            body = (f'<g id="A_{name}" filter="url(#fNight)">{art}</g>'
                    f'<g style="mix-blend-mode:screen" mask="url(#{m})">{lit}</g>')
        else:
            body = ""
        inner = body + top
        if name == "cat":
            inner = f'<g id="cat_jump">{inner}</g>'
        layers.append(f'<g id="L_{name}" style="isolation:isolate">{inner}</g>')
    return (f'<svg id="scene" xmlns="http://www.w3.org/2000/svg" width="{H.W}" height="{H.H}" viewBox="0 0 {H.W} {H.H}">'
            f'<defs>{"".join(H.DEFS)}</defs>{"".join(layers)}</svg>')


if __name__ == "__main__":
    font = os.path.join(HERE, "..", "..", "..", "..", "..", "assets", "fonts", "ShantellSans-ExtraBold.ttf")
    b64 = base64.b64encode(open(font, "rb").read()).decode()
    svg = build()
    html = open(f"{HERE}/template28e.html").read().replace("<!--SVG-->", svg).replace("/*FONT*/", b64)
    open(f"{HERE}/heroes28e.html", "w").write(html)
    print("heroes28e.html", len(html) // 1024, "KB")
