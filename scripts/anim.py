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


# Влёт камеры в хук (владелец 26.10 после рилса 08: «закрепи навсегда на автомате, чтоб было такое начало, более
# динамичное, как в 8»): наезд 18 % за 0,25 с с перелётом 2,2 % и поворотом −1,1°, гаснущим за 0,4 с. В 07 было 12 % за
# 0,3 с без перелёта — владелец: «в самом начале чуть-чуть совсем динамичнее». Сцена хука берёт камеру отсюда
# (reel_rules.check_hook_start ищет вызов), удар и тряска на слове — поверх.
HOOK_ZOOM, HOOK_SNAP_SEC, HOOK_OVERSHOOT, HOOK_ROLL, HOOK_ROLL_SEC = 0.18, 0.25, 0.022, -1.1, 0.4


def hook_cam(t):
    """Камера первого плана хука в момент t: резкий влёт с маленьким перелётом и поворотом (как в рилсе 08)."""
    snap = 1 / (1 + HOOK_ZOOM * (1 - SNAP(t / HOOK_SNAP_SEC)))
    # перелёт начинается с нуля и гаснет: в рилсе 08 он включался ступенькой (+2,2 % за один кадр на 0,25 с) — здесь плавно
    u = t - HOOK_SNAP_SEC
    over = 1 + HOOK_OVERSHOOT * 2.2 * math.exp(-u / 0.16) * math.sin(2 * math.pi * 1.6 * u) if u > 0 else 1.0
    return dict(dx=0.0, dy=0.0, zoom=snap * over, rot=HOOK_ROLL * (1 - EASE_OUT(min(1.0, t / HOOK_ROLL_SEC))))


# Рисунок хука двигается сам с первого кадра (владелец 26.10, рилс 08: лента листается уже на первом кадре; в 06 швабра
# начинала дрожать только с 0,15 с). Мера — доля пикселей рисунка, изменившихся между 0 и 0,1 с без камеры.
FIRST_MOTION_DT, FIRST_MOTION_LEVEL = 0.1, 12


def first_frame_motion(frame_fn, ctx):
    """Доля пикселей сцены, которые изменились за первые FIRST_MOTION_DT с (камера не считается: сцена отдаёт её отдельно)."""
    a, _ = frame_fn(0.0, ctx)
    b, _ = frame_fn(FIRST_MOTION_DT, ctx)
    d = np.abs(np.asarray(a, np.float32) - np.asarray(b, np.float32)).max(axis=2)
    return float((d > FIRST_MOTION_LEVEL).mean())


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


_FOLLOW = {}
CONTACT_ZONE = 0.4


def _follow_geo(mask, base, focus):
    """Для захлёста: доля пути от точки удара (нет удара — от опоры) до самой дальней точки персонажа: 0 — там, куда
    пришлась сила, 1 — хвост, дальнее ухо; и вес удара. Сетка — одна на размер кадра (память четырёх процессов)."""
    h, w = mask.shape[:2]
    gk = ("grid", h, w)
    if gk not in _FOLLOW:
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        _FOLLOW[gk] = (xs, ys)
    xs, ys = _FOLLOW[gk]
    src = focus if focus is not None else base
    uk = ("u", id(mask), src)
    if uk not in _FOLLOW:
        d = np.hypot(xs - src[0], ys - src[1])
        r = float(d[mask > 0.5].max()) if (mask > 0.5).any() else 1.0
        wf = None
        if focus is not None:                         # там, куда пришёлся удар, сминается сильнее
            wf = (0.6 + 0.4 * np.exp(-(d / (0.5 * r)) ** 2 / 2)).astype(np.float32)
        # зона удара (до 40% пути) отвечает в тот же кадр; запаздывает только дальнее — хвост, дальнее ухо. Без зоны
        # макушка в трети пути от пальца отставала на 1–2 кадра и на ударе почти не сминалась (замер 25.10, «ленивый»)
        _FOLLOW[uk] = (np.clip((d / r - CONTACT_ZONE) / (1 - CONTACT_ZONE), 0, 1).astype(np.float32), wf)
    u, wf = _FOLLOW[uk]
    return dict(xs=xs, ys=ys, u=u, wf=wf)


def _centroid(m):
    k = ("c", id(m))
    if k not in _FOLLOW:
        ys, xs = np.nonzero(m > 0.5)
        _FOLLOW[k] = (int(xs.mean()), int(ys.mean())) if len(xs) else (0, 0)
    return _FOLLOW[k]


def squash_follow(img, mask, base, amount, t, lag=0.12, focus=None, rigid=(), levels=6):
    """Сжатие персонажа на ударе так, как его рисуют аниматоры (25.10, разбор репозиториев: animation-principles,
    HyperFrames character.md), а не одним полем, как squash_region:
      - объём держится: насколько сплющилось по высоте, настолько раздалось вширь (sx = 1/sy); squash_region со
        sx = 1 + 0.5·a терял 3–7% площади на пике — кот «худел» на ударе;
      - захлёст: часть, куда пришлась сила (focus), отвечает в тот же кадр, дальние (хвост, дальнее ухо) запаздывают до
        lag секунд (0.12 с ≈ 4 кадра) и доколебываются позже. Первая версия считала запаздывание от пола — голова под
        пальцем отвечала на 3–4 кадра позже удара, ухо вытягивалось (лист 25.10);
      - focus — там сминается полностью, на дальней стороне — на 60%;
      - rigid — маски твёрдых предметов внутри рисунка (телефон, конверт): сдвигаются целиком, не гнутся.
    amount(t) -> a: >0 — сплющено, <0 — вытянуто (обычно пружина anim.spring). base — (x, y) точки опоры.
    ОТКЛОНЕНО ВЛАДЕЛЬЦЕМ 25.10 на трёх сценах: «кот как желе, слишком растекается… было лучше» — в сценах squash_region;
    сюда — только с его слова."""
    g = _follow_geo(mask, base, focus)
    al = np.array([amount(t - lag * k / (levels - 1)) for k in range(levels)], np.float32)
    if float(np.abs(al).max()) < 0.002:
        return img
    x = g["u"] * (levels - 1); k0 = np.floor(x).astype(np.int32); k1 = np.minimum(k0 + 1, levels - 1); fr = x - k0
    a = al[k0] * (1 - fr) + al[k1] * fr
    if g["wf"] is not None: a = a * g["wf"]
    a = np.clip(a, -0.4, 0.4)
    sy = 1.0 - a                                      # высота; ширина 1/sy — площадь та же
    m = mask.astype(np.float32)
    dx = (g["xs"] - base[0]) * (sy - 1.0) * m         # обратное отображение: 1/sx - 1 = sy - 1
    dy = (g["ys"] - base[1]) * (1.0 / sy - 1.0) * m
    for r in rigid:                                   # твёрдое — одним сдвигом, как в его центре
        cx, cy = _centroid(r)
        ox, oy = float(dx[cy, cx]), float(dy[cy, cx])
        # маска твёрдого задана на исходном рисунке, а сдвиг берётся в кадре — там, куда предмет приехал
        rr = cv2.warpAffine(np.clip(r, 0, 1).astype(np.float32), np.float32([[1, 0, -ox], [0, 1, -oy]]),
                            (r.shape[1], r.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)
        dx = dx * (1 - rr) + ox * rr
        dy = dy * (1 - rr) + oy * rr
    return cv2.remap(img, (g["xs"] + dx).astype(np.float32), (g["ys"] + dy).astype(np.float32), cv2.INTER_CUBIC,
                     borderMode=cv2.BORDER_REFLECT)


# ----------------------------------------------------------------------------- подготовка слоёв (быстро, без ручной возни)
def grid(img, box, path, zoom=3, step=20):
    """Кроп рисунка с сеткой — снимать координаты глазом. Подписи сетки — в координатах РИСУНКА (не кропа):
    каждые 100 px яркая линия и число. Так угол предмета читается сразу, без пересчёта «зум, сдвиг»."""
    from PIL import Image, ImageDraw
    x0, y0, x1, y1 = box
    im = Image.fromarray(np.clip(img[y0:y1, x0:x1], 0, 255).astype(np.uint8)).resize(((x1 - x0) * zoom, (y1 - y0) * zoom), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    for x in range((x0 // step + 1) * step, x1, step):
        X = (x - x0) * zoom; major = x % 100 == 0
        d.line([(X, 0), (X, im.height)], fill=(255, 0, 0) if major else (255, 170, 170), width=2 if major else 1)
        if major: d.text((X + 3, 3), str(x), fill=(255, 0, 0))
    for y in range((y0 // step + 1) * step, y1, step):
        Y = (y - y0) * zoom; major = y % 100 == 0
        d.line([(0, Y), (im.width, Y)], fill=(255, 0, 0) if major else (255, 170, 170), width=2 if major else 1)
        if major: d.text((3, Y + 3), str(y), fill=(255, 0, 0))
    im.save(path)
    return path


def ink_objects(img, box=None, min_area=4000, paper_l=225, close=9):
    """Нарисованное на бумаге — отдельными масками (связные куски не бумаги, внутри залиты): руки, предметы.
    Для рисунка на бумаге это вырезание без ручной разметки. Возвращает список масок uint8 по убыванию площади."""
    L = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB)[..., 0]
    # фон — самый большой связный кусок бумаги; всё остальное — предметы. Порог «светлее paper_l» сам по себе
    # не годится: блики на руках светлее бумаги по порогу и выходят к краю листа (первая версия — маски с дырами)
    paper = (L >= paper_l).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(paper, connectivity=4)
    bg = lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]) if n > 1 else np.zeros_like(paper, bool)
    m = (~bg).astype(np.uint8)
    if box is not None:
        keep = np.zeros_like(m); x0, y0, x1, y1 = box; keep[y0:y1, x0:x1] = 1; m &= keep
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((close, close), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in sorted(cs, key=cv2.contourArea, reverse=True):
        if cv2.contourArea(c) < min_area: break
        k = np.zeros_like(m); cv2.drawContours(k, [c], -1, 1, -1); out.append(k)
    return out


def cut_polygon(img, poly, grow=25, sure=13, iters=6):
    """Предмет по грубому многоугольнику (снятому по grid): GrabCut уточняет край, контур тушью остаётся предмету.
    Возвращает маску uint8 во весь рисунок (один связный кусок)."""
    poly = np.float32(poly)
    H, W = img.shape[:2]
    x0, y0 = max(0, int(poly[:, 0].min()) - 3 * grow), max(0, int(poly[:, 1].min()) - 3 * grow)
    x1, y1 = min(W, int(poly[:, 0].max()) + 3 * grow), min(H, int(poly[:, 1].max()) + 3 * grow)
    crop = np.clip(img[y0:y1, x0:x1], 0, 255).astype(np.uint8)
    m = np.zeros(crop.shape[:2], np.uint8); cv2.fillPoly(m, [np.int32(poly - [x0, y0])], 1)
    gc = np.full(m.shape, cv2.GC_BGD, np.uint8)
    gc[cv2.dilate(m, np.ones((grow, grow), np.uint8)) > 0] = cv2.GC_PR_BGD
    gc[m > 0] = cv2.GC_PR_FGD
    gc[cv2.erode(m, np.ones((sure, sure), np.uint8)) > 0] = cv2.GC_FGD
    cv2.grabCut(cv2.cvtColor(crop, cv2.COLOR_RGB2BGR), gc, None, np.zeros((1, 65)), np.zeros((1, 65)), iters, cv2.GC_INIT_WITH_MASK)
    ph = np.isin(gc, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(ph)
    if n > 1: ph = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    out = np.zeros((H, W), np.uint8); out[y0:y1, x0:x1] = ph
    return out


def _nfill(img, valid, sig):
    v = valid.astype(np.float32)
    num = cv2.GaussianBlur(img * v[..., None], (0, 0), sig); den = cv2.GaussianBlur(v, (0, 0), sig)[..., None]
    return num / np.maximum(den, 1e-6), den[..., 0]


def fill_hole(img, hole, valid=None, sigs=(10, 25, 60), grain_from=None, feather=5):
    """Фон на месте вырезанного предмета: гладкое продолжение соседнего фона (нормированная свёртка по `valid` —
    только свой фон, без контуров и соседних предметов) + зерно рисунка с чистого места `grain_from` (dy, dx:
    сдвиг, откуда брать зерно; по умолчанию — выше дыры на её высоту; "noise" — шумом силы соседнего фона, когда
    чистого места рядом нет; (0, 0) НЕЛЬЗЯ — дыра возьмёт своё же зерно и в ней проступят контуры предмета-призрака,
    замер 25.10 на руках хука 1). На бумаге и на гладкой стене этого хватает;
    LaMa на тёмной стене давала пятна и полосы (замер 25.10). Возвращает новую картинку float32."""
    img = img.astype(np.float32)
    hole = hole.astype(bool)
    if valid is None:
        L = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB)[..., 0]
        valid = (L > np.percentile(L[~hole], 30)) & ~hole            # светлое — фон, тёмное — контуры и предметы
    valid = valid & ~hole
    out, _ = _nfill(img, valid, sigs[-1])
    for s_ in reversed(sigs[:-1]):
        f, d = _nfill(img, valid, s_); out = np.where((d > 0.15)[..., None], f, out)
    hf = img - cv2.GaussianBlur(img, (0, 0), 2.5)
    if grain_from == "noise":                         # зерно шумом той же силы, что у чистого фона рядом
        sd = float(hf[valid].std()) if valid.any() else 2.0
        rng = np.random.default_rng(7)
        nz = cv2.GaussianBlur(rng.normal(0, 1, img.shape[:2]).astype(np.float32), (0, 0), 0.8)
        out = out + (nz / (nz.std() + 1e-6) * sd)[..., None]
    else:                                             # зерно с чистого места: (dy, dx) — строка y берёт y - dy
        if grain_from is None:
            grain_from = (int(cv2.boundingRect(hole.astype(np.uint8))[3] * 1.3), 0)
        out = out + np.roll(hf, grain_from, axis=(0, 1))
    a = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), feather)[..., None] if feather else hole[..., None].astype(np.float32)
    return img * (1 - a) + out * a


def paper_like(img):
    """Бумага рисунка -> крем рилса тем же способом, что prepare_src в reel.py (иначе сцена на другой бумаге)."""
    import canvas
    col, share = canvas.paper_color(img)
    return canvas.retint(img, col) if canvas.is_paper(col, share) else img


def sheet(frame_fn, ctx, ts, crop, path, width=480):
    """Проверочный лист сцены: кадры в моменты ts (кроп рисунка x0, y0, x1, y1), подписи времени. Смотреть его
    ДО рендера рилса — рендер дороже в 20 раз."""
    from PIL import Image
    x0, y0, x1, y1 = crop
    tiles = []
    for t in ts:
        img, cam = frame_fn(t, ctx)
        c = np.clip(img[y0:y1, x0:x1], 0, 255).astype(np.uint8)
        c = cv2.resize(c, (width, int(width * (y1 - y0) / (x1 - x0))))
        cv2.putText(c, f"{t:.2f}", (8, 28), 0, 0.8, (220, 0, 0), 2)
        tiles.append(c)
    cols = 4
    while len(tiles) % cols: tiles.append(np.full_like(tiles[0], 255))
    rows = [np.concatenate(tiles[i:i + cols], 1) for i in range(0, len(tiles), cols)]
    Image.fromarray(np.concatenate(rows, 0)).save(path)
    return path


# ----------------------------------------------------------------------------- детали на рисунке (усталость, страх)
def eye_bags(img, eyes, k, color=(118, 92, 138), line=(28, 22, 34)):
    """Мешки под глазами: акварельный полумесяц под глазом и тонкая дуга тушью по его низу; проявляются с k (0..1).
    eyes — [(cx, y_низа_глаза, полуширина_глаза)] в координатах картинки (снять по anim.grid). Кот чёрный, поэтому
    полумесяц — светлее шерсти (лиловый, обычным смешиванием): тёмный мешок умножением на чёрной шерсти не виден."""
    if k <= 0.01:
        return img
    h, w = img.shape[:2]
    m = np.zeros((h, w), np.float32); ln = np.zeros((h, w), np.float32)
    for cx, yb, hw in eyes:
        outer = np.zeros((h, w), np.float32); inner = np.zeros((h, w), np.float32)
        cv2.ellipse(outer, (int(cx), int(yb - 0.05 * hw)), (int(hw * 0.80), int(hw * 0.42)), 0, 0, 180, 1.0, -1, cv2.LINE_AA)
        cv2.ellipse(inner, (int(cx), int(yb - 0.22 * hw)), (int(hw * 0.92), int(hw * 0.36)), 0, 0, 180, 1.0, -1, cv2.LINE_AA)
        m = np.maximum(m, np.clip(outer - inner, 0, 1))
        cv2.ellipse(ln, (int(cx), int(yb - 0.05 * hw)), (int(hw * 0.74), int(hw * 0.40)), 0, 25, 155, 1.0,
                    max(2, int(hw * 0.045)), cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), max(2.0, eyes[0][2] * 0.05)) * 0.6 * k
    ln = cv2.GaussianBlur(ln, (0, 0), 1.0) * k
    out = img * (1 - m[..., None]) + np.float32(color) * m[..., None]
    return out * (1 - ln[..., None]) + np.float32(line) * ln[..., None]


def sweat_drop(img, p, t, size=40, fall=120, life=0.9, color=(140, 190, 235)):
    """Капля пота: появляется у виска, набухает и стекает вниз с ускорением; t — от появления."""
    if not 0 <= t < life:
        return img
    u = t / life
    x, y = p[0], p[1] + fall * gravity(clamp01((u - 0.3) / 0.7))
    r = size * (0.5 + 0.5 * EASE_OUT(clamp01(u / 0.3)))
    img = img.copy()
    pts = np.int32([(x, y - r * 1.6), (x + r * 0.8, y), (x, y + r), (x - r * 0.8, y)])
    cv2.ellipse(img, (int(x), int(y)), (int(r * 0.8), int(r)), 0, 0, 360, color, -1, cv2.LINE_AA)
    cv2.fillPoly(img, [pts[[0, 1, 3]]], color, cv2.LINE_AA)
    cv2.ellipse(img, (int(x), int(y)), (int(r * 0.8), int(r)), 0, -20, 200, (30, 30, 34), max(2, int(r * 0.12)), cv2.LINE_AA)
    cv2.line(img, tuple(pts[0]), tuple(pts[1]), (30, 30, 34), max(2, int(r * 0.12)), cv2.LINE_AA)
    cv2.line(img, tuple(pts[0]), tuple(pts[3]), (30, 30, 34), max(2, int(r * 0.12)), cv2.LINE_AA)
    cv2.circle(img, (int(x - r * 0.3), int(y - r * 0.2)), max(2, int(r * 0.15)), (250, 250, 255), -1, cv2.LINE_AA)
    return img


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
