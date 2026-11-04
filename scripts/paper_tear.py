"""Переход «рваная бумага» (владелец 04.11, пробник 1 одобрен: «первое берём… уже нормально»): кадр, который уходит,
рвётся по неровной линии с белыми волокнами по краю, половинки разлетаются, под ними — новый план. Сначала надрыв
(узкая тёмная щель, в ней тень под листом), потом лист расходится. Ставится по смыслу — поворот, обрыв старой мысли,
не украшение: план в edit.json с "tear": true (внутри картинки, не на первом плане — уходящий кадр нужен в том же
клипе). Звук — у плана ("sound"), на кадре разрыва."""
import functools

import cv2
import numpy as np

from easing import ease_io

VERSION = 1               # правка вида разрыва — смена ключа клипа (long_edit кладёт её в план)
TEAR_SEC = 0.6            # весь разрыв: надрыв 0.22 доли, дальше половинки улетают
PULL = 0.22               # доля времени на надрыв: щель в несколько пикселей, лист дёргается
FLY_PX = 1.3              # на сколько ширин кадра улетают половинки к концу
PAPER_CORE = np.array([253, 251, 245], np.float32)   # белая сердцевина бумаги на рваном краю


@functools.lru_cache(maxsize=8)
def _masks(w, h, seed):
    rng = np.random.default_rng(seed)
    y = np.arange(h, dtype=np.float32)
    x = w*0.52 + 0*y
    for amp, per in ((70, 900), (28, 260), (10, 70), (4, 18)):          # крупная волна и мелкие зубцы
        x += amp*h/1080*np.sin(2*np.pi*y/(per*h/1080) + rng.uniform(0, 6.28))
    x += np.cumsum(rng.normal(0, 1.2, h)).astype(np.float32)*0.6
    xx = np.arange(w, dtype=np.float32)[None, :]
    left = (xx < x[:, None]).astype(np.float32)
    dl, dr = np.clip(x[:, None] - xx, 0, None), np.clip(xx - x[:, None], 0, None)
    rim = (5 + 7*np.abs(np.convolve(rng.normal(0, 1, h + 40), np.ones(9)/9, "same")[20:h + 20]))[:, None]*h/1080
    rims = []
    for m, d in ((left, dl), (1 - left, dr)):
        r = cv2.GaussianBlur(((d < rim) & (m > 0)).astype(np.float32), (0, 0), 0.7)
        rims.append(r)
    return left, rims[0], rims[1]


def compose(before, after, u, seed=7):
    """Кадр перехода: before рвётся и разлетается над after; u — доля перехода 0..1."""
    h, w = before.shape[:2]
    left, rim_l, rim_r = _masks(w, h, seed)
    pull = min(1.0, u/PULL)
    fly = ease_io(max(0.0, (u - PULL)/(1 - PULL)))**1.3
    f = np.asarray(after, np.float32)*(0.35 + 0.65*min(1.0, fly*3))      # в узкой щели — тень под листом
    for m, rim, sgn in ((left, rim_l, -1), (1 - left, rim_r, 1)):
        rgb = np.asarray(before, np.float32)*(1 - rim[..., None]) + PAPER_CORE*rim[..., None]
        piece = np.dstack([rgb, m*255])
        dx = sgn*(8*w/1920*pull + FLY_PX*w*fly)
        dy = (-40 if sgn < 0 else 50)*h/1080*fly + 3*np.sin(40*u)*(1 - fly)*pull
        M = cv2.getRotationMatrix2D((w/2 + sgn*w/4, h/2), sgn*7*fly, 1.0)
        M[0, 2] += dx
        M[1, 2] += dy
        lay = cv2.warpAffine(piece, M, (w, h), flags=cv2.INTER_LINEAR)
        a = lay[..., 3:]/255.0
        sh = cv2.GaussianBlur(np.roll(np.roll(a[..., 0], int(14*h/1080), 0), int(10*h/1080)*sgn, 1), (0, 0), 14*h/1080)
        f = f*(1 - 0.35*sh[..., None])
        f = f*(1 - a) + lay[..., :3]*a
    return f
