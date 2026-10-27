"""Хук L01, кадр 1 «Сколько лет ты уже ждёшь, когда начнётся жизнь?»: листки календаря срываются со стены и падают
в кучу у стула — время уходит у зрителя на глазах, пока кот ждёт.

Рисунок один (frames/001.png): кот на стуле, у стула куча оторванных листков, на стене календарь с надорванным листом.
Листки рисуются кодом в цвет бумаги и туши самого рисунка (берутся с календаря), с дырочками от спирали, как в куче.

Хронометраж (от начала фразы, голос с 0 с):
  0       первый листок уже рвётся (рисунок движется с первого кадра) — под влёт камеры hook_cam;
  слова   «понедельника», «праздников», «силы»: на ударную гласную срывается следующий листок;
  полёт   ~0,95 с: рывок вверх 0,08 с, падение ∝ t², листок кружит и качается (флаттер затухает), на единицах;
  куча    упавший листок остаётся лежать на куче до конца плана.
Координаты — в пикселях рисунка 1531×1027 (сетка anim.grid, 27.10)."""
import math
import re

import cv2
import numpy as np

import anim

CAL = (880.0, 215.0)               # центр надорванного листа календаря
CAL_BOX = (805, 150, 975, 285)     # откуда брать цвет листа
PAGE = (165.0, 125.0)              # размер листка в пикселях рисунка (как лист календаря)
LAND = [(735, 905), (250, 900), (840, 840), (470, 945)]   # куда ложится: перед кучей, на виду
LAND_ROT = [-14.0, 11.0, 7.0, -6.0]
FALL_SEC, RIP_SEC = 0.95, 0.08
WORDS = ("понедельник", "праздник", "сил")
FALLBACK = (1.9, 3.4, 5.0)


def _times(words):
    out = [-0.12]                       # первый листок уже рвётся на первом кадре: рисунок движется с 0 с
    for stem, fb in zip(WORDS, FALLBACK):
        w = next((w for w in words if re.sub(r"[^а-яё]", "", w["word"].lower()).startswith(stem)), None)
        out.append(w["start"] + 0.08 if w else fb)
    return out


def _page(w, h, paper, ink, seed):
    """Листок RGBA: бумага, контур тушью, рваный верх с дырочками спирали, лёгкая серая заливка снизу."""
    rng = np.random.default_rng(seed)
    pad = 8
    W, H = int(w) + 2 * pad, int(h) + 2 * pad
    top = [(pad + x, pad + 6 + rng.uniform(-3, 3) * (1 if k % 2 else -1)) for k, x in enumerate(np.linspace(0, w, 14))]
    poly = np.int32(top + [(pad + w, pad + h), (pad, pad + h)])
    a = np.zeros((H, W), np.float32)
    cv2.fillPoly(a, [poly], 1.0, cv2.LINE_AA)
    rgb = np.ones((H, W, 3), np.float32) * np.float32(paper)
    shade = np.clip((np.arange(H) - H * 0.55) / (H * 0.45), 0, 1)[:, None, None] * 0.07
    rgb = rgb * (1 - shade)
    line = np.zeros((H, W), np.float32)
    # контур от руки: ребро бьётся на короткие куски с дрожью и разной толщиной, как штрих рисунка
    pts = np.float32(poly)
    for p0, p1 in zip(pts, np.roll(pts, -1, axis=0)):
        n = max(2, int(np.hypot(*(p1 - p0)) / 18))
        seg = [p0 + (p1 - p0) * (i / n) + rng.normal(0, 0.8, 2) for i in range(n + 1)]
        for q0, q1 in zip(seg, seg[1:]):
            cv2.line(line, tuple(np.int32(q0)), tuple(np.int32(q1)), 1.0, int(rng.integers(3, 5)), cv2.LINE_AA)
    for x in np.linspace(pad + w * 0.12, pad + w * 0.88, 7):          # дырочки от спирали, как у листков в куче
        cv2.ellipse(line, (int(x), int(pad + 15)), (4, 5), 0, 0, 360, 1.0, 2, cv2.LINE_AA)
    line = cv2.GaussianBlur(line, (0, 0), 0.6)
    rgb = rgb * (1 - line[..., None]) + np.float32(ink) * line[..., None]
    return anim.Layer(rgb, np.clip(a + line, 0, 1), (W / 2, H / 2))


class Scene:
    def __init__(self, fr, words, scale):
        self.ox, self.oy = fr["off"]
        self.s = scale
        x0, y0, x1, y1 = CAL_BOX
        reg = fr["world"][int((y0 + self.oy) * scale):int((y1 + self.oy) * scale),
                          int((x0 + self.ox) * scale):int((x1 + self.ox) * scale)].reshape(-1, 3).astype(np.float32)
        lum = reg.mean(1)
        paper = np.median(reg[lum >= np.percentile(lum, 70)], axis=0)
        ink = np.median(reg[lum <= np.percentile(lum, 2)], axis=0)
        self.times = _times(words)
        self.pages = [_page(PAGE[0] * scale, PAGE[1] * scale, paper, ink, seed=k) for k in range(len(self.times))]
        self.shadow = []
        for pg in self.pages:
            a = cv2.GaussianBlur(pg.a, (0, 0), 6 * scale)
            self.shadow.append(anim.Layer(np.zeros(pg.rgb.shape, np.float32) + 40, a, pg.pivot))

    def _w(self, x, y):
        return ((x + self.ox) * self.s, (y + self.oy) * self.s)

    def _pose(self, k, t):
        """(позиция в мире, угол, масштаб) листка k в момент t; None — ещё не сорван."""
        u = t - self.times[k]
        if u < 0:
            return None
        sx, sy = CAL
        ex, ey = LAND[k % len(LAND)]
        if u < RIP_SEC:                                   # рывок: лист отрывается вверх и вбок
            r = anim.EASE_OUT(u / RIP_SEC)
            return self._w(sx - 6 * r, sy - 14 * r), -7 * r, 1.0
        v = min(1.0, (u - RIP_SEC) / FALL_SEC)
        y = sy - 14 + (ey - sy + 14) * anim.gravity(v)
        x = sx - 6 + (ex - sx + 6) * anim.EASE_IO(v) + 40 * math.sin(2 * math.pi * 1.7 * v) * (1 - v)
        ang = -7 + (LAND_ROT[k % len(LAND_ROT)] + 7) * v + 26 * math.sin(2 * math.pi * 1.5 * v + 0.6) * (1 - v)
        return self._w(x, y), ang, 1.0 - 0.15 * v

    def frame(self, t, world):
        base = world.astype(np.float32)
        for k, pg in enumerate(self.pages):
            pose = self._pose(k, t)
            if pose is None:
                continue
            pos, ang, sc = pose
            falling = self.times[k] + RIP_SEC < t < self.times[k] + RIP_SEC + FALL_SEC
            smear = None
            if falling:
                p2 = self._pose(k, t + 1 / 24)
                smear = (0.0, (p2[0][1] - pos[1]) * 0.5) if p2 else None
            flip = 1.0
            if falling:                                    # лист кувыркается: то ребром, то плашмя (затухает к земле)
                v = (t - self.times[k] - RIP_SEC) / FALL_SEC
                flip = 1 - 0.55 * abs(math.sin(2 * math.pi * 1.2 * v)) * (1 - v)
                sh = (pos[0] + 14 * self.s, pos[1] + 18 * self.s)   # мягкая тень на стене и полу
                self.shadow[k].draw(base, sh, angle=ang, sx=sc, sy=sc * flip, opacity=0.18)
            pg.draw(base, pos, angle=ang, sx=sc, sy=sc * flip, smear=smear)
        return np.clip(base, 0, 255).astype(np.uint8)

    def cam(self, t):
        c = anim.hook_cam(t)
        for t0 in self.times[1:]:          # лёгкое вздрагивание на каждом сорванном листке
            u = t - t0
            if 0 <= u < 0.25:
                c["dy"] += 3.0 * math.sin(2 * math.pi * 9 * u) * (1 - u / 0.25)
        return c
