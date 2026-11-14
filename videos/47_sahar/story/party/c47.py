"""Общие помощники сцен party рилса 47: время слов, удары камеры, тряска, рукописный текст (Caveat «CAV» в base.html)."""
import json
import math
import os

from lib import clamp, f

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["word"].strip(".,?!").lower() == word.lower() and w["start"] >= after - 1e-6:
            return w["start"]
    raise KeyError(word)


def kick(t, times, amp=0.03, dec=16):
    """Толчок масштаба и поворота на моменты times."""
    s, rot = 1.0, 0.0
    for tt in times:
        q = t - tt
        if q >= 0:
            s *= 1 + amp * math.exp(-q * dec) * math.cos(q * 30)
            rot += amp * 18 * math.exp(-q * dec) * math.sin(q * 34)
    return s, rot


def shake(t, t0, amp, dec=9, fr=55):
    q = t - t0
    if q < 0:
        return 0.0, 0.0
    a = amp * math.exp(-q * dec)
    return a * math.sin(q * fr), a * math.cos(q * fr * 1.3)


def pop(t, t0, dur=0.1, over=0.18, k0=0.0):
    """Масштаб «вылет с перелётом»: k0 → 1 за dur, потом затухающий перелёт."""
    e = t - t0
    if e <= 0:
        return k0
    if e < dur:
        u = e / dur
        return k0 + (1 + over - k0) * (1 - (1 - u) ** 2)
    q = e - dur
    return 1 + over * math.exp(-q * 9) * math.cos(q * 22)


def hand_text(x, y, txt, size, fill, stroke=None, sw=0.0, weight=700, anchor="middle", rot=0.0, extra=""):
    """Рукописная надпись Caveat; stroke — обводка-подложка (paint-order: stroke под заливкой)."""
    st = (f' stroke="{stroke}" stroke-width="{f(sw)}" stroke-linejoin="round" paint-order="stroke"' if stroke else "")
    return (f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" font-family="CAV" font-weight="{weight}" font-size="{f(size)}" '
            f'fill="{fill}"{st} transform="rotate({f(rot)} {f(x)} {f(y)})" {extra}>{txt}</text>')


_ = clamp
