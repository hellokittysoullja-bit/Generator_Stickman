"""s14: тетрадный лист, рукописная строка «я злюсь, потому что меня не услышали» пишется пером по словам (26.80–28.9);
красное облако в углу давит сверху и на «услышали» (28.32) сжимается в маленький шарик, падает на лист и отскакивает."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hw  # noqa: E402
import lib  # noqa: E402
import scene_c as C  # noqa: E402
from lib import (DEFS, INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts, shape,  # noqa: E402
                 smooth, spring)

_ST = {}
SIZE = 150
BASES = (620, 870, 1120)
# слова: я 26.80, злюсь, 26.96, потому 27.47, что 27.76, меня 27.92, не 28.16, услышали 28.32
WT = [[(26.80, 26.93), (26.96, 27.36), (27.47, 27.70)],
      [(27.76, 27.88), (27.92, 28.12), (28.16, 28.28)],
      [(28.32, 28.95)]]
INKC = "#1f3a8a"
_LN = {}


def lines():
    if not _LN:
        for i, tx in enumerate(("я злюсь, потому", "что меня не", "услышали")):
            _LN[i] = hw.Line(tx, SIZE, 540, BASES[i], INKC, word_t=WT[i], center=True)
    return _LN


def build_static():
    if _ST:
        return
    pg = lin_grad([(0, "#fbf6e8", 1), (1, "#f1e8d0", 1)], 0, 0, 0, 1)
    s = [f'<rect x="-1500" y="-1500" width="{W + 3000}" height="{H + 3000}" fill="#8a6a4a"/>',
         f'<rect x="-1500" y="-200" width="{W + 3000}" height="{H + 400}" fill="url(#{pg})"/>']
    for k in range(18):
        y = 250 + k * 100
        s.append(f'<rect x="-1500" y="{y}" width="{W + 3000}" height="3" fill="#8fb4d8" opacity=".75"/>')
    s.append(f'<rect x="132" y="-200" width="4" height="{H + 400}" fill="#e2605a" opacity=".7"/>')
    s.append(f'<rect x="140" y="-200" width="3" height="{H + 400}" fill="#e2605a" opacity=".45"/>')
    for k in range(10):
        y = 140 + k * 190
        s.append(f'<ellipse cx="48" cy="{y}" rx="19" ry="19" fill="#8a6a4a"/><ellipse cx="50" cy="{y + 3}" rx="16" ry="14" fill="#6a4c30"/>')
    _ST["page"] = "".join(s)
    lib.static_done()


def cloud_state(t):
    """(cx, cy, R, squash, calm) облака: сверху справа давит, на «услышали» (28.32) сжимается в шарик и падает."""
    R = 290 + 14 * math.sin(t * 3.0) + 30 * smooth(27.9, 28.25, t)
    cx, cy = 850 + 14 * math.sin(t * 1.7), 170 + 10 * math.sin(t * 2.3)
    sq = 1.0 + .05 * math.sin(t * 2.0)
    calm = 0.0
    u = clamp((t - 28.32) / 0.52)
    if t >= 28.32:
        e = ease_io(u)
        R = (290 + 30) * (1 - e) + 62 * e
        calm = e
        # полёт к листу: падает по дуге
        tx, ty = 935, 1195
        fx = ease_in(u, 1.4)
        cx = 850 + (tx - 850) * ease_io(u)
        cy = 170 + (ty - 170) * (ease_in(u, 2.0) * .75 + .25 * ease_io(u))
        sq = 1.0 - .16 * math.sin(math.pi * u)
        if t >= 28.84:
            tt = t - 28.84
            cx = 935 + 4 * (1 - math.exp(-tt * 3))
            cy = 1195 - 120 * abs(math.sin(math.pi * tt * 2.0)) * math.exp(-tt * 3.2)
            sq = 1.0 - 0.22 * max(0.0, math.cos(math.pi * tt * 2.0)) * math.exp(-tt * 4) * (1 if tt < .25 else 0)
            R = 62 + 4 * math.sin(tt * 5) * math.exp(-tt * 2)
    return cx, cy, R, sq, calm


def s14(t):
    build_static()
    lns = lines()
    out = [_ST["page"]]
    cx, cy, R, sq, calm = cloud_state(t)
    out.append(C.angry_cloud(cx, cy, R, t, seed=0.7, squash=sq, calm=calm, streaks=(calm < .5)))
    if calm < .1:
        out.append(C.sparks(cx, cy, R, t, n=8))
    # тень шарика / облака на листе
    if t >= 28.5:
        out.append(blob(ellipse_pts(cx + 6, 1263, R * .95, R * .2, 18), "#6a4c30", .30 * max(0.0, 1 - (1195 - cy) / 400), blur(5)))
    # строки: сначала письмо, потом облако сверху, если оно ещё большое
    for i in (0, 1, 2):
        out.append(lns[i].svg(t))
    # перо
    tipx = tipy = None
    for i in (0, 1, 2):
        ln = lns[i]
        if ln.t_start - 0.14 <= t <= ln.t_end + 0.25:
            if t < ln.t_start:
                prev = lns[i - 1].tip(lns[i - 1].t_end) if i else (900, 330, 0, 0)
                u = ease_io(clamp((t - (ln.t_start - 0.14)) / 0.14))
                nx, ny = ln.tip(ln.t_start)[:2]
                tipx, tipy = prev[0] + (nx - prev[0]) * u, prev[1] + (ny - prev[1]) * u - 30 * math.sin(math.pi * u)
            elif t > ln.t_end:
                if i == 2:
                    u = clamp((t - ln.t_end) / .25)
                    x0_, y0_ = ln.tip(ln.t_end)[:2]
                    tipx, tipy = x0_ + 40 * u, y0_ - 110 * u
            else:
                tipx, tipy = ln.tip(t)[:2]
    if tipx is not None:
        out.append(f'<g opacity=".25" transform="translate(16 18)">{hw.pencil(tipx, tipy, -52, 1.0, 5)}</g>')
        out.append(hw.pencil(tipx, tipy, -52, 1.0, 5))
    # облако поверх листа, пока давит; шарик — тоже
    a = ease_io(clamp((t - 26.6) / 2.7))
    cm = cam(540, 800 + 100 * a, 1.0 + 0.1 * a, -0.7 + 1.2 * a)
    return f'<g transform="{cm}">{"".join(out)}</g>'
