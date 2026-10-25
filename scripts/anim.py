"""Движение внутри рисунка рилса (25.10, слово владельца: «сильное движение, а не только эффект камеры… профессионально,
не на коленке»). Сцена рилса — модуль videos/NN/reel/anim/<имя>.py со своими слоями и ключами; этот модуль — общее:

- кривые и пружины: cubic-bezier как в After Effects (`bezier`), падение под тяжестью (`gravity`), затухающая пружина
  (`spring`) для отскока и успокоения — числа движения берутся из физики, а не подбором;
- ключи (`Track`): значение по ключевым кадрам, у каждого отрезка своя кривая;
- рисунок на двойках (`on_twos`): рисованное меняется 12 раз в секунду, камера рилса идёт 30 — главный признак
  рисованной анимации (так уже живёт кукла, DOLL_FPS);
- слой (`Layer`): RGBA-вырезка с точкой опоры; ставится поворотом, сдвигом и сжатием вдоль своей оси — фон под ним не
  растягивается (пробник v3 тянул кусок картинки вокруг предмета: «резина»);
- смаз (`smear`): только у движущегося слоя, вдоль скорости, с чётким передним краем — как смаз-кадр аниматора,
  а не среднее нескольких кадров всей картинки (v3: мутное двойное пятно);
- штрихи удара тушью (`impact_strokes`): сужаются к концам, как линия пера, у каждого рисунка чуть свои.

Сцена отдаёт `frame(t, ctx) -> (картинка исходника ×2, камера)`; камера — поправка к окну плана reel.py
(сдвиг, наезд, поворот), её считает сцена: удар, задержка на ударе, тряска — это реакция на событие рисунка.
"""
import math
import importlib.util
import os

import cv2
import numpy as np

DRAW_FPS = 12


def on_twos(t, fps=DRAW_FPS):
    return math.floor(t * fps + 1e-6) / fps


def clamp01(u):
    return 0.0 if u < 0 else 1.0 if u > 1 else u


def bezier(p1x, p1y, p2x, p2y):
    """cubic-bezier(p1x, p1y, p2x, p2y) — та же кривая, что в CSS и After Effects. Возвращает u -> значение."""
    def f(u):
        u = clamp01(u)
        lo, hi = 0.0, 1.0
        for _ in range(40):                          # x(s) монотонна — ищем s делением пополам
            s = (lo + hi) / 2
            x = 3 * (1 - s) ** 2 * s * p1x + 3 * (1 - s) * s ** 2 * p2x + s ** 3
            lo, hi = (s, hi) if x < u else (lo, s)
        s = (lo + hi) / 2
        return 3 * (1 - s) ** 2 * s * p1y + 3 * (1 - s) * s ** 2 * p2y + s ** 3
    return f


LINEAR = lambda u: clamp01(u)                       # noqa: E731
EASE_OUT = bezier(0.22, 1.0, 0.36, 1.0)              # быстрый вход, долгое торможение (ease-out-quint)
EASE_IN = bezier(0.55, 0.0, 1.0, 0.45)               # разгон
EASE_IO = bezier(0.65, 0.0, 0.35, 1.0)
SNAP = bezier(0.16, 1.0, 0.3, 1.0)                    # резкий наезд камеры: 80% пути за первую треть


def gravity(u):
    """Свободное падение: путь растёт как квадрат времени (скорость растёт линейно)."""
    u = clamp01(u)
    return u * u


def spring(t, freq=4.0, damping=0.28):
    """Отклонение затухающей пружины от покоя после толчка в t=0: 1 в момент толчка, дальше колебания к 0.
    freq — колебаний в секунду, damping — доля критического затухания (0.2–0.4 — мультяшный отскок)."""
    if t < 0:
        return 0.0
    w = 2 * math.pi * freq
    wd = w * math.sqrt(max(1e-6, 1 - damping ** 2))
    return math.exp(-damping * w * t) * (math.cos(wd * t) + damping * w / wd * math.sin(wd * t))


class Track:
    """Значение по ключам: [(t, значение, кривая отрезка до следующего ключа)]. Значение — число или кортеж."""

    def __init__(self, keys):
        self.keys = sorted(keys, key=lambda k: k[0])

    def __call__(self, t):
        ks = self.keys
        if t <= ks[0][0]:
            return ks[0][1]
        for (t0, v0, *e), (t1, v1, *_) in zip(ks, ks[1:]):
            if t < t1:
                u = (e[0] if e else LINEAR)((t - t0) / max(1e-9, t1 - t0))
                if isinstance(v0, (tuple, list)):
                    return tuple(a + (b - a) * u for a, b in zip(v0, v1))
                return v0 + (v1 - v0) * u
        return ks[-1][1]


class Layer:
    """Вырезка RGBA (float32, альфа 0..1) с точкой опоры в своих координатах."""

    def __init__(self, rgb, alpha, pivot):
        self.rgb = rgb.astype(np.float32)
        self.a = alpha.astype(np.float32)
        self.pivot = np.float32(pivot)

    @classmethod
    def cut(cls, img, mask, pad=24, feather=1.0):
        """Вырезать из рисунка по маске: слой обрезан по рамке маски, опора — центр рамки (в координатах рисунка)."""
        x, y, w, h = cv2.boundingRect(mask.astype(np.uint8))
        x0, y0 = max(0, x - pad), max(0, y - pad)
        x1, y1 = min(img.shape[1], x + w + pad), min(img.shape[0], y + h + pad)
        a = mask[y0:y1, x0:x1].astype(np.float32)
        if feather:
            a = cv2.GaussianBlur(a, (0, 0), feather)
        lay = cls(img[y0:y1, x0:x1], a, ((x1 - x0) / 2, (y1 - y0) / 2))
        lay.origin = np.float32((x0, y0))              # где слой лежит на рисунке в покое
        return lay

    def home(self):
        """Точка опоры слоя на рисунке в покое."""
        return self.origin + self.pivot

    def matrix(self, pos, angle=0.0, sx=1.0, sy=1.0, axis=0.0):
        """Аффинная матрица: опора -> pos; сжатие (sx вдоль оси axis, sy поперёк), затем поворот angle (градусы)."""
        a = math.radians(axis)
        R = np.float32([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        S = R @ np.diag([sx, sy]).astype(np.float32) @ R.T
        b = math.radians(angle)
        Q = np.float32([[math.cos(b), -math.sin(b)], [math.sin(b), math.cos(b)]])
        M2 = Q @ S
        off = np.float32(pos) - M2 @ self.pivot
        return np.hstack([M2, off[:, None]]).astype(np.float32)

    def draw(self, base, pos, angle=0.0, sx=1.0, sy=1.0, axis=0.0, opacity=1.0, smear=None):
        """Положить слой на base (float32 RGB, на месте). smear=(vx, vy) — скорость в px за кадр рисунка."""
        M = self.matrix(pos, angle, sx, sy, axis)
        h, w = self.a.shape
        corners = np.float32([[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]]) @ M.T
        pad = 4 + (int(abs(smear[0]) + abs(smear[1])) if smear else 0)
        x0 = int(max(0, math.floor(corners[:, 0].min()) - pad)); x1 = int(min(base.shape[1], math.ceil(corners[:, 0].max()) + pad))
        y0 = int(max(0, math.floor(corners[:, 1].min()) - pad)); y1 = int(min(base.shape[0], math.ceil(corners[:, 1].max()) + pad))
        if x1 <= x0 or y1 <= y0:
            return base
        Ml = M.copy(); Ml[0, 2] -= x0; Ml[1, 2] -= y0
        size = (x1 - x0, y1 - y0)
        rgb = cv2.warpAffine(self.rgb * self.a[..., None], Ml, size, flags=cv2.INTER_CUBIC, borderValue=0)
        a = np.clip(cv2.warpAffine(self.a, Ml, size, flags=cv2.INTER_CUBIC, borderValue=0), 0, 1)
        if smear and math.hypot(*smear) > 2:
            rgb, a = _smear(rgb, a, smear)
        a = a * opacity
        reg = base[y0:y1, x0:x1]
        np.multiply(reg, 1 - a[..., None], out=reg)
        reg += rgb * opacity
        return base


def _smear(rgb_pm, a, v):
    """Смаз движущегося слоя вдоль скорости v: след позади, передний край чёткий (премультиплицированные цвета)."""
    vx, vy = v
    n = int(min(60, math.hypot(vx, vy)))
    if n < 3:
        return rgb_pm, a
    k = np.zeros((2 * n + 1, 2 * n + 1), np.float32)
    # filter2D — корреляция: точка берёт пиксели со стороны ядра, поэтому ядро смотрит ВПЕРЁД по скорости, а след
    # ложится позади (тест test_smear_trails_behind_motion: первая версия рисовала след впереди предмета)
    ux, uy = vx / math.hypot(vx, vy), vy / math.hypot(vx, vy)
    for i in range(n + 1):
        k[int(round(n + uy * i)), int(round(n + ux * i))] += 1.0 - 0.7 * i / n
    k /= k.sum()
    trail_rgb = cv2.filter2D(rgb_pm, -1, k, borderType=cv2.BORDER_CONSTANT)
    trail_a = cv2.filter2D(a, -1, k, borderType=cv2.BORDER_CONSTANT)
    # передний край: сам предмет поверх следа
    out_a = a + trail_a * (1 - a)
    out_rgb = rgb_pm + trail_rgb * (1 - a)[..., None]
    return out_rgb, out_a


def stroke(base, p0, p1, width, color, alpha=1.0, taper=(0.15, 0.25)):
    """Штрих пером: толщина растёт от начала к середине и сходит на нет к концу (как линия туши), край мягкий."""
    p0, p1 = np.float32(p0), np.float32(p1)
    d = p1 - p0; L = float(np.hypot(*d))
    if L < 1:
        return base
    nrm = np.float32([-d[1], d[0]]) / L
    n = max(8, int(L / 3))
    s = np.linspace(0, 1, n)
    prof = np.minimum(np.clip(s / taper[0], 0, 1), np.clip((1 - s) / taper[1], 0, 1)) ** 0.7
    pts = p0[None] + d[None] * s[:, None]
    left = pts + nrm[None] * (width / 2 * prof)[:, None]
    right = pts - nrm[None] * (width / 2 * prof)[:, None]
    poly = np.concatenate([left, right[::-1]])
    x0, y0 = np.floor(poly.min(0) - 4).astype(int); x1, y1 = np.ceil(poly.max(0) + 4).astype(int)
    x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, base.shape[1]), min(y1, base.shape[0])
    if x1 <= x0 or y1 <= y0:
        return base
    m = np.zeros((y1 - y0, x1 - x0), np.float32)
    cv2.fillPoly(m, [np.int32((poly - [x0, y0]) * 4)], 1.0, cv2.LINE_AA, shift=2)
    m = cv2.GaussianBlur(m, (0, 0), 0.8)[..., None] * alpha
    reg = base[y0:y1, x0:x1]
    reg[:] = reg * (1 - m) + np.float32(color) * m
    return base


def impact_strokes(base, center, t, r0, r1, n=7, spread=(200, 340), width=14, color=(235, 242, 255), seed=3, life=0.33):
    """Штрихи удара вокруг точки: вылетают наружу и тают за life секунд. t — от удара, уже на двойках.
    Направления и длины чуть свои у каждого рисунка (кипение), но веер — один."""
    if not 0 <= t < life:
        return base
    u = t / life
    rng = np.random.default_rng(seed)
    angs = np.linspace(spread[0], spread[1], n) + rng.uniform(-8, 8, n)
    lens = rng.uniform(0.75, 1.15, n)
    jit = np.random.default_rng(seed * 100 + int(round(t * DRAW_FPS)))
    out = EASE_OUT(u)
    for a, ln in zip(angs, lens):
        a2 = math.radians(a + jit.uniform(-2.5, 2.5))
        ra = r0 + (r1 - r0) * 0.55 * out
        rb = ra + (r1 - r0) * ln * (1 - 0.6 * u)
        c, s_ = math.cos(a2), math.sin(a2)
        stroke(base, (center[0] + ra * c, center[1] + ra * s_), (center[0] + rb * c, center[1] + rb * s_),
               width * (1 - 0.55 * u), color, alpha=1 - u ** 2)
    return base


def squash_region(img, mask, base_y, cx, sy, sx):
    """Сжатие и расширение части рисунка (персонаж на ударе) от линии опоры base_y. Деформация — плавным полем
    смещений (маска задаёт силу), а не смесью двух картинок: смесь по мягкой маске давала двойной контур."""
    h, w = img.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    m = mask.astype(np.float32)
    ky = 1.0 / sy - 1.0; kx = 1.0 / sx - 1.0
    mx = xs + (xs - cx) * kx * m
    my = ys + (ys - base_y) * ky * m
    return cv2.remap(img, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


_SCENES = {}


def scene(reel_dir, name):
    """Сцена videos/NN/reel/anim/<name>.py: модуль с frame(t, ctx). Загружается один раз на процесс."""
    key = (os.path.abspath(reel_dir), name)
    if key not in _SCENES:
        p = os.path.join(reel_dir, "anim", name + ".py")
        spec = importlib.util.spec_from_file_location(f"reel_anim_{name}", p)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        mod.REEL_DIR = reel_dir
        _SCENES[key] = mod
    return _SCENES[key]


def scene_files(reel_dir, name):
    """Файлы сцены для подписи кэша клипов: код сцены и исходные рисунки."""
    mod = scene(reel_dir, name)
    return [os.path.join(reel_dir, "anim", name + ".py")] + [os.path.join(reel_dir, p) for p in getattr(mod, "SOURCES", [])]
