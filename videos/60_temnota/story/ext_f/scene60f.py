"""Рилс 60 «темнота», группа F: s15 (подоконник), s16 (кот крупно), s17 (призыв, рукописное «кот»).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Слова — voice/words.json."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
for d in (os.path.join(STORY, "common"), os.path.join(STORY, "..", "..", "59_podarok", "story", "common")):
    if os.path.isdir(d):
        sys.path.insert(0, d)
import cat as Cat  # noqa: E402
import catf  # noqa: E402
import lib  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, rrect, shape  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
WI = {}
for i_, w_ in enumerate(WORDS):
    WI.setdefault(w_["word"].strip(".,!?").lower(), []).append(i_)


def wt(word, k=0):
    return WORDS[WI[word][k]]["start"]


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if (u <= 0 or u >= 1) else math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


# ═══════════════════════════════ s16: кот крупно ═══════════════════════════════
T_HOTYA, T_NE, T_NUZH = wt("хотя"), wt("не", 1), wt("нужно")


def lazy_blink(t, a, dur=.42):
    """Ленивое моргание: веки опускаются медленно, на секунду замирают и поднимаются."""
    u = (t - a) / dur
    if not 0 < u < 1:
        return 0.0
    return math.sin(math.pi * u) ** .6 if u < .5 else math.sin(math.pi * u) ** 1.4


def wall_window(t, z):
    """Тёплая стена вечера, слева окно с синим вечерним светом, внизу доска подоконника (кот сидит на ней)."""
    o = []
    g = lib.lin_grad([(0, "#e3d6bb", 1), (1, "#d6c4a2", 1)])
    o.append(f'<rect x="-900" y="-900" width="3200" height="3600" fill="url(#{g})"/>')
    # окно: синий вечер, перекрестье рамы
    wx0, wy0, wx1, wy1 = -330, 330, 300, 1300
    gg = lib.lin_grad([(0, "#6f88b5", 1), (.55, "#a9bddb", 1), (1, "#d9cfc0", 1)])
    o.append(shape(rrect(wx0 - 34, wy0 - 34, wx1 + 34, wy1 + 34, 8), "#f1eadb", w=5, seed=601))
    o.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="url(#{gg})"/>')
    for (x, y, r) in [(-200, 420, 4), (-60, 380, 3), (140, 500, 4), (-240, 600, 3)]:
        o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff6d8" opacity=".85"/>')
    o.append(blob(ellipse_pts(110, 560, 64, 64, 14), "#fff3cf", .95))
    o.append(blob(ellipse_pts(136, 552, 56, 60, 14), "#a9bddb", 1))
    o.append(f'<rect x="{wx0}" y="{(wy0 + wy1) // 2 - 7}" width="{wx1 - wx0}" height="14" fill="#f1eadb"/>')
    o.append(f'<rect x="-14" y="{wy0}" width="28" height="{wy1 - wy0}" fill="#f1eadb"/>')
    o.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="none" stroke="{INK}" stroke-width="4"/>')
    # свет окна на стене
    o.append(blob([(330, 300), (900, 360), (1000, 1200), (330, 1180)], "#aebfdc", .22))
    # подоконник — доска, на ней сидит кот
    top = [(-900, 1306), (1900, 1306), (1900, 1380), (-900, 1380)]
    o.append(shape(top, "#b98a5c", blob([(-900, 1344), (1900, 1344), (1900, 1380), (-900, 1380)], "#8d6440"), w=5, seed=605))
    o.append(blob([(-900, 1306), (1900, 1306), (1900, 1318), (-900, 1318)], "#d6a878"))
    o.append(blob([(-900, 1380), (1900, 1380), (1900, 1700), (-900, 1700)], "#cdbd9c"))
    return "".join(o)


def frame16(t):
    # кот крупно: поворот от окна к зрителю, ленивое моргание, зевок, довольный прищур
    turn_u = sm(t, 26.55, 27.15)
    turn = -1.0 * (1 - turn_u)
    look = (-1.0 * (1 - turn_u) + .0 * turn_u, -.25 * (1 - turn_u))
    blink = lazy_blink(t, T_HOTYA - .05, .46)
    yawn = sm(t, T_NE - .02, T_NE + .2) * (1 - sm(t, T_NE + .36, T_NE + .58))
    happy = sm(t, T_NE + .4, T_NE + .62)
    if yawn > .02:
        happy = max(happy, 0.0)
    if t < T_NUZH + .6:
        eyes_happy = happy * (1 - 0)
    else:
        eyes_happy = happy
    st = dict(turn=turn, look=look, blink=blink, yawn=yawn, happy=eyes_happy if yawn < .3 else 0.0,
              ear=2.5 * math.sin(t * 17) * bump(t, T_NE - .1, .5) + 4 * bump(t, T_HOTYA + .2, .3), perk=.35 * (1 - turn_u),
              tilt=-5 * (1 - turn_u) + 3 * math.sin(t * 1.4) + 5 * bump(t, T_NUZH, .5), drop=-.12 * yawn + .03 * bump(t, T_NUZH, .4),
              tail=10 * math.sin(t * 2.2) + 5 * bump(t, 27.4, .5), flame_e=1.1 + .5 * bump(t, T_NUZH, .5), smile=happy)
    z = 1.0 + .26 * sm(t, 26.7, 28.6)
    set_ink(z * 2.9)
    body = wall_window(t, z)
    ck = 2.9
    cxs, cys = 395 + 8 * math.sin(t * 1.1), 1480
    sq = 1 + .02 * bump(t, T_NE, .5)
    body += catf.draw2(cxs, cys, ck * sq, st, t)
    fx, fy = 395 + (180 + 28) * 0, 0
    cam_cx = 560 + 30 * sm(t, 26.7, 28.6) + (-60) * 0
    cam_cy = 960 + (-40) * sm(t, 26.7, 28.6)
    cam = lib.cam(cam_cx, cam_cy, z, 1.2 * math.sin(t * 1.3) - 2.0 * bump(t, T_NE, .5) + 1.4 * bump(t, T_NUZH, .3))
    return f'<g transform="{cam}">{body}</g>'


FRAMES = {"s16": frame16}


def frame(sid, t):
    lib.dyn_begin()
    body = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#d9c9a8"/>{body}')
