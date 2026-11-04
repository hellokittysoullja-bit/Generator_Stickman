"""Хук L03, кадр 1 «Ты не досмотришь это видео. И дело не в твоей лени.» — движение внутри рисунка (библиотека:
кот на полу весь в телефоне, r1_phone).

С кадра 0 из телефона в лапах вылетают карточки роликов, одна за другой в ритме смахивания (раз в ~0,4 с): разгон
вверх-влево, поворот, рост, смаз позади. На ударный слог «ле́ни» лента замирает: карточки встают в воздухе, вздрагивают
и чуть оседают, вокруг головы вспыхивают штрихи удара, новые карточки больше не летят. Камера — anim.hook_cam(t, hit=…)
(влёт правил 28–29) и тряска на ударе. Карточки рисуются кодом поверх мира кадра (рисунок тот же, что у сборщика:
бумага, увеличение, фактура), поэтому кадр сцены не отличается от соседних ни бумагой, ни резкостью.
Координаты — холст кадра (canvas.prepare рисунка 1531×1027 → 1826×1027, сдвиг 147 px) ×2, сняты сеткой anim.grid."""
import math
import re

import cv2
import numpy as np
from PIL import Image, ImageDraw

import anim

S = 2                                   # frame_clip.UPSCALE
PHONE = (372 * S, 575 * S)              # левый край телефона в лапах — отсюда вылетают карточки (мимо морды)
HEAD = (600 * S, 430 * S)               # центр головы — штрихи удара
SPAWN = 0.40                            # смахивание раз в 0,4 с
FLIGHT = 0.62                           # полёт карточки до края кадра
HIT_FRAC = 0.25                         # ударный слог «ле́ни» — начало слова
SHAKE_SEC = 2 / 30
INK = (24, 24, 26)


def _stem(w):
    return re.sub(r"[^а-яё]", "", w.lower())


def _card():
    """Карточка ролика: светлый лист с «экраном» и треугольником воспроизведения, обводка тушью."""
    w, h = 230, 290
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 10 + w, 10 + h), 26, fill=(246, 243, 236, 255), outline=INK + (255,), width=8)
    d.rounded_rectangle((32, 34, w - 12, 196), 14, fill=(214, 226, 236, 255), outline=INK + (255,), width=5)
    cx, cy = (w + 20) / 2, 115
    d.polygon([(cx - 22, cy - 30), (cx - 22, cy + 30), (cx + 30, cy)], fill=INK + (255,))
    for k, ln in enumerate((0.8, 0.55)):
        y = 224 + k * 30
        d.line((34, y, 34 + (w - 46) * ln, y), fill=(120, 118, 114, 255), width=9)
    return np.asarray(im).astype(np.float32)


def _paste(base, card, cx, cy, scale, rot, alpha):
    if alpha <= 0.01 or scale <= 0.05:
        return
    h, w = card.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, scale)
    M[0, 2] += cx - w / 2
    M[1, 2] += cy - h / 2
    H, W = base.shape[:2]
    out = cv2.warpAffine(card, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    a = out[..., 3:] / 255.0 * alpha
    base[:] = base * (1 - a) + out[..., :3] * a


class Scene:
    def __init__(self, fr, words, scale):
        w = next((w for w in words if _stem(w["word"]).startswith("лени")), None)
        self.hit = (w["start"] + HIT_FRAC * (w["end"] - w["start"])) if w else 3.0
        self.card = _card()
        self.cards = []                                  # (момент вылета, разброс)
        rng = np.random.default_rng(7)
        t0 = -0.32                                       # к кадру 0 одна карточка уже в полёте
        while t0 < self.hit:
            self.cards.append((t0, rng.uniform(-1, 1), rng.uniform(-1, 1)))
            t0 += SPAWN * rng.uniform(0.85, 1.12)

    def _pos(self, u, j1, j2):
        """Путь карточки: из телефона вверх-влево с разгоном (смахивание), поворот и рост."""
        x0, y0 = PHONE
        dx, dy = -(320 + 110 * j1) * S, -(900 + 80 * j2) * S
        cx = x0 + dx * u ** 0.45                         # сначала резко влево, мимо морды и уха, потом вверх с разгоном
        cy = y0 + dy * u ** 1.7
        return cx, cy, (0.45 + 0.85 * min(1.0, u * 1.6)) * S * 0.75, -8 - (24 + 10 * j2) * u

    def frame(self, t, world):
        base = world.astype(np.float32).copy()
        frozen = t >= self.hit
        if frozen:                                       # штрихи удара — под карточками, не поверх них
            base = anim.impact_strokes(base, HEAD, t - self.hit, 300 * S, 420 * S, n=7, spread=(195, 345),
                                       width=12 * S, color=INK, life=0.4)
        tt = min(t, self.hit)
        for (t0, j1, j2) in self.cards:
            u = (tt - t0) / FLIGHT
            if not 0 <= u < 1:
                continue
            cx, cy, sc, rot = self._pos(u, j1, j2)
            if frozen:                                   # лента замерла: карточки вздрагивают и чуть оседают
                th = t - self.hit
                k = math.exp(-th / 0.18)
                cx += 14 * k * math.sin(th * 70 + j1 * 3)
                cy += 26 * anim.EASE_OUT(min(1.0, th / 0.5)) + 10 * k * math.cos(th * 60)
                rot += 4 * k * math.sin(th * 50)
            else:                                        # смаз позади — два следа по пути
                for back, al in ((0.10, 0.18), (0.05, 0.32)):
                    ub = u - back
                    if ub > 0:
                        bx, by, bs, br = self._pos(ub, j1, j2)
                        _paste(base, self.card, bx, by, bs, br, al)
            _paste(base, self.card, cx, cy, sc, rot, 1.0)
        return np.clip(base, 0, 255).astype(world.dtype)

    def cam(self, t):
        c = anim.hook_cam(t, hit=self.hit)
        th = t - self.hit
        if th >= SHAKE_SEC:                              # кадр отвечает на «ле́ни»: тряска гаснет за ~0,15 с
            k = math.exp(-(th - SHAKE_SEC) / 0.12)
            c["dx"] += 10 * k * math.sin(th * 95)
            c["dy"] += 12 * k * math.cos(th * 77)
            c["rot"] += 0.3 * k * math.sin(th * 61)
        return c
