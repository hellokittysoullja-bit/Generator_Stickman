"""Рилс 80 «Мама была права», группа B: Дима, кот, призыв. Время — только из shots.json и voice/words.json (слово по индексу wN).
s04: тёмная комната, Дима растёт в три рывка «лет» (w10), сам затягивает шнур бирки «сам» (w13), смирился «поверил» (w16).
s05: призыв «Телеграм» модулем scripts/story_cta_tg.py: PRESS = W[20].start + 0.12 («Телеграм»), T0 = PRESS − 1.10.
s07: комната вечером, кот на задних лапах поддевает бирку носом: «смотри» (w30) к зрителю, «что»–«было» (w31–w34) дымок из-под
     бирки, «самом» (w36) захлопнулась, бровь.
s08: стол днём, «Дима»–«садился» (w38–w39) садится и закатывает рукав, «дело» (w41) кладёт лист и папку.
s10: «уходил» (w51) отворачивается к телефону, «телефон» (w53) тёплый купол, облако снаружи.
s16: вечер, «да» (w85) кивает облачку, «неприятно» (w86) облачко-клубок на угол стола, берёт ручку.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(STORY)))
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import cat as CAT  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as P  # noqa: E402
import room as R  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, svg  # noqa: E402,F401

INK = lib.INK
W = json.load(open(os.path.join(STORY, "voice", "words.json")))
W = W if isinstance(W, list) else W["words"]
SH = {s["id"]: s for s in json.load(open(os.path.join(STORY, "shots.json")))["shots"]}


def ws(i):
    return W[i]["start"]


def we(i):
    return W[i]["end"]


def T0(sid):
    return SH[sid]["t0"]


def T1(sid):
    return SH[sid]["t1"]


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (lerp(a[0], b[0], u), lerp(a[1], b[1], u))


def bump(t, t0, dur):
    u = (t - t0) / dur
    return math.sin(math.pi * u) if 0 < u < 1 else 0.0


def kick(t, t0, dur=.35, freq=2.2, damp=5.0):
    """Затухающий удар после t0: 0 до t0, потом колебание к нулю (для тряски и наездов)."""
    if t < t0:
        return 0.0
    u = (t - t0) / dur
    return math.exp(-damp * u) * math.cos(2 * math.pi * freq * u) if u < 3 else 0.0


def frame_svg(body, cx, cy, s, rot, bg="#05070f", over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def soft(x, y, rx, ry, col, op):
    g = lib.rad_grad([(0, col, op), (.55, col, op * .45), (1, col, 0)], x, y, rx, ry)
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#{g})"/>'


# ═══════════════════════════════ s05: призыв «Телеграм» ═══════════════════════════════
def s05(t):
    import story_cta_tg as tg
    press = ws(20) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=COMMON)


def frame(sid, t):
    return globals()[sid](t)
