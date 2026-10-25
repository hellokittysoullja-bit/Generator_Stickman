"""Вертикальный рилс 9:16 из уже оплаченных рисунков эпизода: сценарий-удержание, камера, субтитры, звук.

    python scripts/reel.py videos/02_sdvg_vremya/reel            # reel.json -> reel.mp4
    python scripts/reel.py videos/02_sdvg_vremya/reel --sheet    # лист кадрирований без рендера

Своё, а не сборщик длинного ролика: у рилса другая грамматика (замер и разбор 22.10 — Kallaway, Jenny Hoyos,
LISTOPADOV, Яковлева, vidIQ, Isaac):
  * тема и контраст в первые 1-2 с, обещание конца в первые 3 с; смена картинки каждые 1-2.5 с;
  * субтитры — это голос: 1-3 слова на экране, активное слово подсвечено, ключевые слова крупнее и цветом,
    поп-появление 160 мс; без звука ролик понятен целиком;
  * склейка — жёсткая, на начало слова за 2 кадра до него (J-cut картинки); звук перехода начинается раньше
    склейки (J-cut звука), звон таймера тянется через склейку (L-cut);
  * через склейку размер плана меняется на шаг и больше (общий -> крупный), иначе читается «скачок»;
  * камера внутри плана — постоянная скорость (правило 07.10: ease-in/out даёт «насос»), а намеренные
    движения (наезд на слово, хлёст) — с торможением;
  * конец = начало (тот же кадр и слово «пять минут») — ролик замыкается в петлю.
Тайминг слов: alignment.json (озвучка, [{word,start,end}]) или оценка по слогам — тогда это немой рилс.
"""
import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import reel_rules  # noqa: E402  (после пути к scripts)

W, H, FPS = 1080, 1920, 30
PAPER = np.array([250, 247, 240], np.float32)          # #FAF7F0, как у длинных роликов (canvas.py)
FONT = os.path.join(ROOT, "assets", "fonts", "ShantellSans-ExtraBold.ttf")     # надписи в кадре (плашки, часы)
HAND = os.path.join(ROOT, "assets", "fonts", "Caveat-Variable.ttf")
# Субтитры: Onest Black (OFL, шрифт под кириллицу, близок к Gilroy «дорогих» русских рилсов) — временно, до выбора
# владельца по листу 16 шрифтов (22.10). Регистр как в предложении; один кегль и одна базовая линия на весь ролик.
CAP_FONT = os.path.join(ROOT, "assets", "fonts", "reels", "Onest[wght].ttf")
CAP_AXES = {"Weight": 900}
CAP_FEATURES = None
CAP_UPPER = False
VIEW_K = 1.0           # view_scale после layout(): подсказки окон печатаются в координатах reel.json
PH = 1100              # картинка — PH px от PIC_TOP (reel.json: picture_h); ниже — полоса субтитров на той же бумаге
PIC_TOP = 0            # сверху над картинкой — полоса бумаги (reel.json: picture_top; по умолчанию 60, владелец 25.10)
CAP_CX, CAP_CY = 500, 1175   # центр полосы субтитров = PH + 75 (полоса 150 px, субтитр не ложится на рисунок)
BASE_PH = 1100         # под эту высоту написаны экранные координаты reel.json (cy кадров fit/doll, y пометок, часы)
CAP_SIZE = 76          # один кегль на весь ролик; 90 → 76 (24.10): при 90 в строку влезало ~15 знаков и треть групп была
                      # из одного слова, владелец: «удобнее по два-три слова» (замер на эп.01 v4: одиночных 21 → 4)
CAP_MAX_W = 860        # px: от 70 до 930 — правее колонка кнопок Reels (~150 px у правого края)
CAP_AHEAD_ALPHA = 0    # слово появляется, когда его сказали (владелец 25.10: «субтитры всегда динамичные… и в хуке»);
                       # место в строке у всех слов группы своё с начала — строка не прыгает, когда слова добавляются
CAP_RISE = 0           # въезда снизу нет (владелец 25.10: «зачем они поднимаются, пусть ровно»); было 18 px за 250 мс
CAP_STROKE = 6         # тонкая тёмная обводка + мягкая тень (обводка 12% кегля читалась наклейкой)
WHITE = (255, 255, 255); INK = (18, 18, 20)
ACTIVE = (255, 210, 63)        # активное слово (караоке) — тёплый жёлтый
KEY = (255, 138, 31)           # ключевое слово — цвет огонька героя, единственный тёплый цвет бренда
RED = (214, 52, 40)            # стрелки и пометки — как красные стрелки схем
CUT_LEAD = 2 / FPS             # склейка за 2 кадра до слова: картинка «тянет» глаз раньше звука


# ----------------------------------------------------------------------------- слова и время
VOWELS = set("аеёиоуыэюяaeiouy")

def syllables(w):
    return max(1, sum(ch in VOWELS for ch in w.lower()))

PAUSE = {",": .14, ":": .22, "—": .16, ".": .34, "?": .40, "!": .34, "…": .46}

def estimate_times(words, rate=1.0):
    """Немой рилс: время слова по слогам. 0.16 + 0.075 на слог — ~2.8 слова/с, темп бодрого диктора;
    пауза по знаку в конце слова. Это же темп чтения субтитров: 1-3 слова держатся 0.5-1 с."""
    t, out = 0.0, []
    for w in words:
        d = (0.16 + 0.075 * syllables(w)) / rate
        out.append(dict(word=w, start=round(t, 3), end=round(t + d, 3)))
        tail = w.rstrip("»*)")[-1:] if w.rstrip("»*)") else ""
        t += d + PAUSE.get(tail, 0.03) / rate
    return out

def clean(w):
    return w.replace("*", "").replace("|", "")

def tokens(beats):
    """Слова всех фраз подряд; у каждой фразы — индексы её слов."""
    allw, spans = [], []
    for b in beats:
        ws = []
        for w in b["text"].split():                  # одиночное тире — к предыдущему слову, не отдельной группой
            if w in ("—", "–") and ws: ws[-1] += " —"
            else: ws.append(w)
        spans.append((len(allw), len(allw) + len(ws)))
        allw += ws
    return allw, spans


# ----------------------------------------------------------------------------- субтитры
# служебные слова не заканчивают группу: «в / тетради», «не / открыл» читаются обрывком (StudioBinder: не рвать
# синтаксические пары; предлог, частица, союз уходят в следующую группу вместе со своим словом)
CLITICS = {"в", "во", "на", "с", "со", "к", "ко", "по", "о", "об", "от", "до", "из", "у", "за", "для", "при", "без",
           "и", "а", "но", "не", "ни", "что", "как", "это", "то", "же", "ли", "бы", "его", "её", "их", "мой", "твой", "твоей"}
CAP_CPS = 17.0         # знаков в секунду на группу — потолок чтения (StudioBinder: 17)
CAP_MIN_SEC = 0.5      # группа на экране не меньше полсекунды

def cap_text(w):
    """Слово для субтитра: без точек и запятых в конце (Pakalin: знаки препинания удешевляют субтитр);
    «?», «!», «…» и тире остаются — они несут смысл."""
    t = clean(w).rstrip(".,;:")
    if t.endswith("»") and t[:-1].endswith((".", ",")): t = t[:-1].rstrip(".,") + "»"
    return t.upper() if CAP_UPPER else t

def bare(w):
    return clean(w).strip("«»\"'.,:;!?…—- ").lower()

def cap_font():
    return font(CAP_FONT, CAP_SIZE, CAP_AXES, raqm=True)

def tracked(f, t):
    """Ширина слова с контекстными заменами шрифта (calt): трекинга нет, слово меряется целиком."""
    return f.getlength(t, features=CAP_FEATURES)

def cap_width(idx, words):
    f = cap_font()
    return tracked(f, " ".join(cap_text(words[j]) for j in idx)) + 2 * CAP_STROKE

CAP_SENT_END = r"[.?!…]»?\*?$"     # жёсткий обрыв группы — только конец предложения и «|»
CAP_SOFT_END = r"[,:;—]»?\*?$"     # запятая и двоеточие — желательное место границы, но не обрыв

def _split_segment(seg, words):
    """Отрезок предложения → группы по 2–3 слова (владелец 24.10: «по одному слову неудобно, по два-три»).
    Число групп — наименьшее, при котором каждая не длиннее 3 слов и влезает в CAP_MAX_W; длины ровные
    (4 → 2+2, 5 → 3+2, 7 → 3+2+2), одиночная группа остаётся только у отрезка из одного слова. Граница
    сдвигается на запятую рядом и никогда не стоит после служебного слова («в / тетради»)."""
    n = len(seg)
    if n <= 1: return [list(seg)]
    def fits(a, b): return b - a <= 3 and (b - a == 1 or cap_width(list(seg[a:b]), words) <= CAP_MAX_W)
    def cost(a, b):                                   # штраф одной группы seg[a:b]
        c = 0.0
        if b - a == 1: c += 10                          # одиночное слово — только если иначе не влезает
        if b < n and bare(words[seg[b - 1]]) in CLITICS: c += 6     # «в / тетради» — обрывок
        if b < n and not re.search(CAP_SOFT_END, clean(words[seg[b - 1]])): c += 0.5   # граница не на запятой
        return c
    best = [(0.0, 0)] + [(float("inf"), 0)] * n          # (штраф, число групп) до позиции i; меньше групп — лучше
    back = [0] * (n + 1)
    for b in range(1, n + 1):
        for a in range(max(0, b - 3), b):
            if best[a][0] == float("inf") or not fits(a, b): continue
            cand = (best[a][0] + cost(a, b) + 1.0, best[a][1] + 1)   # +1 за группу: длинные группы предпочтительнее
            if cand < best[b]: best[b] = cand; back[b] = a
    groups, b = [], n
    while b > 0:
        a = back[b]; groups.append(list(seg[a:b])); b = a
    return groups[::-1]

def chunks(words, times):
    """Группы по 2-3 слова, всегда ОДНОЙ строкой одного кегля. Обрыв — только конец предложения и «|»;
    внутри предложения группы ровные (см. `_split_segment`), группа не переносится и не уменьшается — делится."""
    out, seg = [], []
    def flush():                                   # хук (первое предложение) — одной группой, если влезает в строку:
        if not seg: return                         # текст хука стоит с первого кадра целиком (эп.01 v5 резался на два)
        if not out and len(seg) > 1 and cap_width(list(seg), words) <= CAP_MAX_W: out.append(list(seg))
        else: out.extend(_split_segment(seg, words))
        seg.clear()
    for i, w in enumerate(words):
        if w.startswith("|"): flush()
        seg.append(i)
        if re.search(CAP_SENT_END, clean(w) + ("*" if w.endswith("*") else "")): flush()
    flush()
    res = []
    for k, c in enumerate(out):
        t0 = max(0.0, times[c[0]]["start"] - CUT_LEAD)      # вместе со склейкой: группа не «переезжает» на чужой план
        t1 = times[out[k + 1][0]]["start"] - CUT_LEAD if k + 1 < len(out) else times[c[-1]]["end"] + 0.6
        res.append(dict(idx=c, t0=t0, t1=t1))
    return res

_FONTS = {}
def font(path, size, wght=None, raqm=False):
    k = (path, size, json.dumps(wght, sort_keys=True), raqm)
    if k not in _FONTS:
        f = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM if raqm else None)
        if wght:
            axes = wght if isinstance(wght, dict) else {"Weight": wght}
            try:
                f.set_variation_by_axes([axes.get(a["name"].decode() if isinstance(a["name"], bytes) else a["name"], a["default"])
                                         for a in f.get_variation_axes()])
            except Exception: pass                                      # шрифт без осей — как есть
        _FONTS[k] = f
    return _FONTS[k]

def render_chunk(words, idx, active, fade_ahead=True):
    """RGBA одной группы: одна строка, один кегль, базовая линия на одной высоте у всех групп (высота картинки
    от метрик шрифта, а не от букв: «у/д/щ» не сдвигают группу). Белые буквы, тонкая тёмная обводка, мягкая
    тень; активное слово — жёлтым (караоке), ключевое — оранжевым. Цвет — единственное отличие слов."""
    f = cap_font(); st = CAP_STROKE; space = f.getlength(" ")
    parts = [(cap_text(words[j]), (KEY if j <= active else WHITE) if "*" in words[j] else (ACTIVE if j == active else WHITE))
             for j in idx]                      # ключевое слово вспыхивает оранжевым, когда до него дошло чтение
    fade = [fade_ahead and j > active for j in idx]   # ещё не «произнесённые» слова: CAP_AHEAD_ALPHA (0 — их нет)
    tw = sum(tracked(f, t) for t, _ in parts) + space * (len(parts) - 1)
    asc, desc = f.getmetrics()
    bw, bh = int(tw + 2 * st + 60), int(asc + desc + 2 * st + 60)
    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); sh = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(sh)
    x, y = 30 + st, 30 + st
    for (t, col), fd in zip(parts, fade):
        a = CAP_AHEAD_ALPHA if fd else 255
        if not a:
            x += tracked(f, t) + space; continue
        ds.text((x, y + CAP_SIZE * 0.07), t, font=f, fill=(0, 0, 0, 80 * a // 255), stroke_width=st + 2,
                stroke_fill=(0, 0, 0, 80 * a // 255), features=CAP_FEATURES)
        d.text((x, y), t, font=f, fill=col + (a,), stroke_width=st, stroke_fill=INK + (a,), features=CAP_FEATURES)
        x += tracked(f, t) + space
    sh = sh.filter(ImageFilter.GaussianBlur(CAP_SIZE * 0.10))
    return Image.alpha_composite(sh, img)

def ease_out_back(u, s=2.2):
    u = min(max(u, 0.0), 1.0) - 1
    return 1 + (s + 1) * u ** 3 + s * u ** 2

def ease_out(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 3

def ease_io(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


# ----------------------------------------------------------------------------- картинка
_SRC = {}
def load_src(reel_dir, name):
    key = (os.path.abspath(reel_dir), name)          # не только имя: f3 двух рилсов в одном процессе — разные рисунки
    if key not in _SRC:
        p = os.path.join(reel_dir, "src", name + "_c.png")
        _SRC[key] = np.asarray(Image.open(p).convert("RGB"))
    return _SRC[key]

def paper_tex(seed=5):
    """Фактура бумаги ±2.5%: тот же крем, что у длинных роликов, но не мёртвая заливка."""
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    n = cv2.resize(cv2.GaussianBlur(n, (0, 0), 1.2), (W, H), interpolation=cv2.INTER_CUBIC)
    n = n / (np.abs(n).max() + 1e-6)
    return np.clip(PAPER[None, None] * (1 + 0.025 * n[..., None]), 0, 255).astype(np.uint8)

def sample(src, cx, cy, h, scale_src=2.0, shake=(0, 0), rot=0.0, boil_t=None, reflect=False):
    """Окно (cx, cy, высота h) в координатах ИСХОДНОГО кадра -> картинка 1080xPH. Края за картинкой — бумага.
    boil_t — «кипение» линии в том же проходе выборки: второй проход (remap поверх готового кадра) мылил рисунок —
    замер 22.10, v7: резкость готового рилса −11% к v6, сам второй проход на кадре f1 −46%."""
    s = h * scale_src / PH
    a = math.radians(rot)
    ca, sa = math.cos(a) * s, math.sin(a) * s
    X0, Y0 = cx * scale_src, cy * scale_src
    M = np.array([[ca, -sa, X0 - ca * (W / 2 + shake[0]) + sa * (PH / 2 + shake[1])],
                  [sa, ca, Y0 - sa * (W / 2 + shake[0]) - ca * (PH / 2 + shake[1])]], np.float32)
    paper = tuple(int(v) for v in PAPER)
    bm = cv2.BORDER_REFLECT_101 if reflect else cv2.BORDER_CONSTANT   # ночной рисунок: за краем — его же стена, не крем
    if boil_t is None:
        return cv2.warpAffine(src, M, (W, PH), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_CUBIC,
                              borderMode=bm, borderValue=paper)
    X, Y = boil_maps(boil_t, PH, W)
    return cv2.remap(src, M[0, 0] * X + M[0, 1] * Y + M[0, 2], M[1, 0] * X + M[1, 1] * Y + M[1, 2], cv2.INTER_CUBIC,
                     borderMode=bm, borderValue=paper)

# «дорогой» вид (разбор роликов о дорогом монтаже 22.10): мягкая S-кривая (тушь глубже, бумага на месте), лёгкая
# резкость картинки и живое зерно по всему кадру, сменяется 12 раз в секунду — как бумага рисованной анимации
_LUT = None
def grade(img):
    global _LUT
    if _LUT is None:
        x = np.arange(256, dtype=np.float32) / 255.0
        y = np.where(x < 0.5, 0.5 * (2 * x) ** 1.18, x)                   # тени глубже, светлое (бумага) не трогается
        _LUT = np.clip(y * 255 + 0.5, 0, 255).astype(np.uint8)
    return cv2.LUT(img, _LUT)

def sharpen(img, amount=0.35, sigma=1.2):
    bl = cv2.GaussianBlur(img, (0, 0), sigma)
    return cv2.addWeighted(img, 1 + amount, bl, -amount, 0)

_BOIL = {}
def boil_maps(t, h, w, amp=0.8):
    """«Кипение» линии рисунка: смещение до ~0.8 px по 4 картам шума, 12 раз в секунду — как рисованная анимация
    (разбор 22.10: Grubbe, Yum Yum — 8-12 рисунков в секунду). Только картинка, не субтитры."""
    k = int(t * GRAIN_FPS) % 4
    if (k, h, w, amp) not in _BOIL:
        rng = np.random.default_rng(300 + k)
        dx = cv2.resize(rng.normal(0, 1, (h // 60 + 2, w // 60 + 2)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
        dy = cv2.resize(rng.normal(0, 1, (h // 60 + 2, w // 60 + 2)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
        X, Y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        _BOIL[(k, h, w, amp)] = (X + amp * dx, Y + amp * dy)
    return _BOIL[(k, h, w, amp)]

def boil(img, t, amp=0.8):
    """То же кипение отдельным проходом — для кадров, собранных на бумаге (fit/stack), где выборка не одна."""
    mx, my = boil_maps(t, *img.shape[:2], amp=amp)
    return cv2.remap(img, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

GRAIN_FPS = 12
_GRAIN = {}
def grain(img, t, amp=0.012):
    k = int(t * GRAIN_FPS) % 6
    if k not in _GRAIN:
        rng = np.random.default_rng(100 + k)
        n = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
        _GRAIN[k] = cv2.resize(n, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    g = _GRAIN[k][:img.shape[0]]
    return np.clip(img.astype(np.float32) * (1 + amp * g), 0, 255).astype(np.uint8)

def fit_on_paper(base, src, region, cy, width_frac, scale=1.0, scale_src=2.0, dx=0.0):
    """Кусок рисунка во всю ширину на бумаге (широкая схема, сравнение двух половин)."""
    x0, y0, x1, y1 = [v * scale_src for v in region]
    piece = src[int(y0):int(y1), int(x0):int(x1)]
    tw = W * width_frac * scale
    th = tw * piece.shape[0] / piece.shape[1]
    piece = cv2.resize(piece, (max(1, int(tw)), max(1, int(th))), interpolation=cv2.INTER_AREA)
    px, py = int(W / 2 - tw / 2 + dx), int(cy - th / 2)
    # мягкий край: рисунок уходит в бумагу, без «вклеенного прямоугольника»
    h_, w_ = piece.shape[:2]
    m = np.ones((h_, w_), np.float32); f = max(4, int(min(h_, w_) * 0.06))
    ramp = np.linspace(0, 1, f, dtype=np.float32)
    m[:f] *= ramp[:, None]; m[-f:] *= ramp[::-1, None]; m[:, :f] *= ramp[None]; m[:, -f:] *= ramp[None, ::-1]
    X0, Y0 = max(0, px), max(0, py); X1, Y1 = min(W, px + w_), min(base.shape[0], py + h_)
    if X1 <= X0 or Y1 <= Y0: return base
    sub = piece[Y0 - py:Y1 - py, X0 - px:X1 - px].astype(np.float32)
    mm = m[Y0 - py:Y1 - py, X0 - px:X1 - px, None]
    base[Y0:Y1, X0:X1] = (sub * mm + base[Y0:Y1, X0:X1].astype(np.float32) * (1 - mm)).astype(np.uint8)
    return base


def prepare_src(reel_dir, sources):
    """src/fN.png — кадры эпизода, увеличенные вдвое (upscale.py: Real-ESRGAN + Lanczos), чтобы вертикальный
    кроп 9:16 из кадра 3:2 (в 3.4 раза уже) не мылился; erase_below — стереть впечатанную старым сборщиком
    печатную подпись схемы (строка пикселей исходного кадра, ниже — бумага)."""
    os.makedirs(os.path.join(reel_dir, "src"), exist_ok=True)
    for name, sp in sources.items():
        out = os.path.join(reel_dir, "src", name + ".png")
        if os.path.exists(out): continue
        import upscale
        a = np.asarray(Image.open(os.path.join(reel_dir, sp["frame"])).convert("RGB"))
        b = upscale.upscale(a, 2).copy()
        if sp.get("erase_below"):
            y = int(sp["erase_below"] * 2)
            b[y:] = np.median(b[y - 100:y].reshape(-1, 3), axis=0).astype(np.uint8)
        Image.fromarray(b).save(out)
        print(f"  исходник {name}: {a.shape[1]}x{a.shape[0]} -> {b.shape[1]}x{b.shape[0]}")
    for name in sources:                               # бумага кадра -> ровный крем, как у длинных роликов (canvas.retint):
        out = os.path.join(reel_dir, "src", name + "_c.png")   # иначе белая бумага схемы читалась швом с полосой субтитров
        if os.path.exists(out): continue
        import canvas
        a = np.asarray(Image.open(os.path.join(reel_dir, "src", name + ".png")).convert("RGB"), np.float32)
        col, share = canvas.paper_color(a)
        if canvas.is_paper(col, share): a = canvas.retint(a, col)   # тёмный фон ночи — не бумага
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out)
        print(f"  бумага {name}: {col.round().tolist()} -> крем (доля бумаги по краю {share:.2f})")


# ----------------------------------------------------------------------------- кукла героя
_DOLL = {}
DOLL_FPS = 12          # кукла рисуется 12 к/с, как рисованная анимация; камера остаётся 30 к/с (white minimal: Posterize Time 12)
DOLL_LIFE_PHASE = 400 / DOLL_FPS   # с какого места плана жизни (seed 11) кукла начинает: как в одобренном v12 (33.3 с)
def doll_frame(t, dur, actions):
    """Живой кот (риг из experiments/alive_cat/doll): RGBA премультиплицированный, координаты рига."""
    if "rig" not in _DOLL:
        sys.path.insert(0, os.path.join(ROOT, "experiments", "alive_cat", "doll"))
        import doll_rig
        _DOLL["mod"] = doll_rig
        _DOLL["rig"] = doll_rig.Rig(os.path.join(ROOT, "experiments", "alive_cat", "doll", "rig.json"))
    flames = sorted((a["t"], a["state"]) for a in actions if a.get("do") == "flame")
    acts = [a for a in actions if a.get("do") != "flame"]
    key = (dur, json.dumps(acts))
    if _DOLL.get("key") != key:
        _DOLL["st"] = _DOLL["mod"].plan(dur, acts, seed=11); _DOLL["key"] = key
    st = _DOLL["st"](t)
    fl = [s_ for t_, s_ in flames if t_ <= t]          # огонёк: «тлеет — застрял», «золотой — шаг сделан» (look/hero_states)
    if fl and fl[-1] in ("ember", "golden"): st = dict(st, flame=fl[-1])
    return _DOLL["rig"].frame_rgba(st, t)

def paste_doll(base, rgba, cx, cy, h):
    """Кот высотой h px с центром рамки рига в (cx, cy); тень под лапами — мягкое пятно."""
    R = _DOLL["rig"]
    x0, y0, x1, y1 = (int(v) for v in R.bb)
    y0 = 0                                      # над головой — звёздочки
    reg = rgba[y0:y1, x0:x1]
    s = h / (y1 - y0)
    reg = cv2.resize(reg, (int((x1 - x0) * s), int((y1 - y0) * s)), interpolation=cv2.INTER_AREA)
    rh, rw = reg.shape[:2]
    px, py = int(cx - rw / 2), int(cy - rh / 2)
    # тень
    BH = base.shape[0]; sh = np.zeros((BH, W), np.float32)
    cv2.ellipse(sh, (int(cx - rw * 0.02), int(py + rh * 0.985)), (int(rw * 0.30), int(rh * 0.035)), 0, 0, 360, 1.0, -1)
    sh = cv2.GaussianBlur(sh, (0, 0), 14) * 0.22
    b = base.astype(np.float32) * (1 - sh[..., None])
    X0, Y0 = max(0, px), max(0, py); X1, Y1 = min(W, px + rw), min(BH, py + rh)
    sub = reg[Y0 - py:Y1 - py, X0 - px:X1 - px]
    a = np.clip(sub[..., 3:4], 0, 1)
    b[Y0:Y1, X0:X1] = np.clip(sub[..., :3], 0, 255) + b[Y0:Y1, X0:X1] * (1 - a)
    return np.clip(b, 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------- накладки
_CLOCK = {}
def clock_img(txt, fill):
    """Часы хука: каждая цифра в ячейке ширины самой широкой цифры (по самому знаку, без полей картинки), по центру
    ячейки. В Shantell «1» — 89 px, «5» — 120, остальные — 133: строка «23:55 → 03:12» центрировалась заново и
    плясала до ±22 px (замер 23.10). Первая версия брала ячейку вместе с полями и разводила цифры («0 3 : 1 2»)."""
    f = font(FONT, 190)
    def glyph(ch, col):
        im = text_img(ch, f, col, stroke=16, stroke_fill=INK)
        return im.crop(im.getbbox() or (0, 0, im.width, im.height)), im.height
    if "cell" not in _CLOCK:
        _CLOCK["cell"] = max(glyph(d, WHITE)[0].width for d in "0123456789")
    cell, gap = _CLOCK["cell"], -6                     # обводки соседних цифр чуть сходятся, как в наборе
    parts = [glyph(ch, fill) for ch in txt]
    widths = [cell if ch.isdigit() else g.width for ch, (g, _h) in zip(txt, parts)]
    H_ = max(h for _g, h in parts)
    out = Image.new("RGBA", (sum(widths) + gap * (len(txt) - 1) + 40, H_), (0, 0, 0, 0)); x = 20
    for (g, _h), w in zip(parts, widths):
        out.alpha_composite(g, (x + (w - g.width) // 2, (H_ - g.height) // 2)); x += w + gap
    return out

def text_img(txt, f, fill, stroke=0, stroke_fill=None, pad=20):
    bb = f.getbbox(txt, stroke_width=stroke)
    im = Image.new("RGBA", (bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - bb[0], pad - bb[1]), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

def strike(base, im, cx, cy, sc, u):
    """Линия от руки поперёк надписи: идёт слева направо за ~0.28 с, чуть вверх и с дрожью пера, выходит за края слова."""
    if u <= 0: return
    gx0, gy0, gx1, gy1 = im.getchannel("A").getbbox()
    x0 = cx + (gx0 - im.width / 2) * sc; x1 = cx + (gx1 - im.width / 2) * sc
    ym = cy + ((gy0 + gy1) / 2 - im.height / 2) * sc
    ext = 0.08 * (x1 - x0); x0 -= ext; x1 += ext
    xe = x0 + (x1 - x0) * min(1.0, ease_out(u))
    xs = np.linspace(x0, xe, max(2, int((xe - x0) / 6)))
    ys = ym + 0.06 * (gy1 - gy0) * sc - (xs - x0) * 0.06 + 3 * np.sin((xs - x0) * 0.045)
    cv2.polylines(base, [np.stack([xs, ys], 1).astype(np.int32)], False, RED, max(6, int(0.11 * (gy1 - gy0) * sc)),
                  cv2.LINE_AA)

def over(base, im, cx, cy, alpha=1.0, scale=1.0, wipe=1.0):
    """RGBA PIL поверх кадра; wipe — доля ширины, открытая слева направо (письмо «от руки»)."""
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    al = a[..., 3:4] / 255 * alpha
    if wipe < 1.0:
        cut = int(a.shape[1] * max(0.0, wipe))
        al = al.copy(); al[:, cut:] = 0
        f = min(18, cut)
        if f > 0: al[:, cut - f:cut] *= np.linspace(1, 0, f, dtype=np.float32)[None, :, None]
    px, py = int(cx - a.shape[1] / 2), int(cy - a.shape[0] / 2)
    X0, Y0 = max(0, px), max(0, py); X1, Y1 = min(W, px + a.shape[1]), min(base.shape[0], py + a.shape[0])
    if X1 <= X0 or Y1 <= Y0: return base
    s = a[Y0 - py:Y1 - py, X0 - px:X1 - px]; m = al[Y0 - py:Y1 - py, X0 - px:X1 - px]
    base[Y0:Y1, X0:X1] = (s[..., :3] * m + base[Y0:Y1, X0:X1] * (1 - m)).astype(np.uint8)
    return base

def ring_lines(base, cx, cy, r, t, color=INK):
    """Пометки «звенит» — короткие штрихи вокруг предмета, дрожат."""
    for k in range(6):
        ang = math.radians(-150 + k * 24 + (k > 2) * 160) + 0.06 * math.sin(t * 60 + k)
        r0, r1 = r * 1.08, r * 1.30
        p0 = (int(cx + r0 * math.cos(ang)), int(cy + r0 * math.sin(ang)))
        p1 = (int(cx + r1 * math.cos(ang)), int(cy + r1 * math.sin(ang)))
        cv2.line(base, p0, p1, color, 9, cv2.LINE_AA)
    return base

def arrow(base, p0, p1, u, color=RED, th=12, dash_t=None, u_head=None):
    """Рисованная стрелка, растёт по u (0..1). dash_t — бегущий пунктир (сцена не замирает, п.1.22): фаза 120 px/с;
    u_head — головка дорисовывается своим временем (на 2–3 кадра позже древка, вторичное движение)."""
    u = ease_out(u)
    if u <= 0: return base
    x = p0[0] + (p1[0] - p0[0]) * u; y = p0[1] + (p1[1] - p0[1]) * u
    if dash_t is None:
        cv2.line(base, (int(p0[0]), int(p0[1])), (int(x), int(y)), color, th, cv2.LINE_AA)
    else:
        L = math.hypot(x - p0[0], y - p0[1]); dx, dy = (x - p0[0]) / max(L, 1e-6), (y - p0[1]) / max(L, 1e-6)
        d0 = -((dash_t * 120.0) % 56.0)
        while d0 < L:
            a0, a1 = max(0.0, d0), min(L, d0 + 34.0)
            if a1 > a0:
                cv2.line(base, (int(p0[0] + dx * a0), int(p0[1] + dy * a0)), (int(p0[0] + dx * a1), int(p0[1] + dy * a1)),
                         color, th, cv2.LINE_AA)
            d0 += 56.0
    if (u if u_head is None else ease_out(u_head)) > 0.85:
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        for s in (-1, 1):
            a2 = ang + math.pi + s * 0.5
            cv2.line(base, (int(x), int(y)), (int(x + 48 * math.cos(a2)), int(y + 48 * math.sin(a2))), color, th, cv2.LINE_AA)
    return base


def pen_tip(base, x, y, h):
    """Кончик карандаша у головы штриха: графитовый грифель и серый корпус под 35°, тень — ничего тёплого."""
    k = h / 200.0; ang = math.radians(-35)
    tip = np.array([x, y]); d = np.array([math.cos(ang), math.sin(ang)])
    n = np.array([-d[1], d[0]])
    cone = tip + d * 46 * k; end = tip + d * 260 * k
    body = np.array([cone + n * 15 * k, end + n * 15 * k, end - n * 15 * k, cone - n * 15 * k], np.int32)
    cv2.fillConvexPoly(base, body, (92, 92, 98), cv2.LINE_AA)
    cv2.fillConvexPoly(base, np.array([tip, cone + n * 15 * k, cone - n * 15 * k], np.int32), (200, 200, 200), cv2.LINE_AA)
    cv2.fillConvexPoly(base, np.array([tip, tip + d * 16 * k + n * 5 * k, tip + d * 16 * k - n * 5 * k], np.int32),
                       (40, 40, 44), cv2.LINE_AA)
    return base


# ----------------------------------------------------------------------------- звук
# Только звуки владельца (assets/sfx/reels, решение 22.10): синтезированные свисты, щелчки на субтитрах,
# тики и музыка-заглушка звучали дёшево. Пик звука — момент, который должен совпасть со склейкой.
SR = 48000
SFX_DIR = os.path.join(ROOT, "assets", "sfx", "reels")
# библиотека звуков владельца с описаниями «что значит и когда ставить» — assets/sfx/reels/library.json
SFX_LIB = {k: v for k, v in json.load(open(os.path.join(SFX_DIR, "library.json"), encoding="utf8")).items() if not k.startswith("_")}
SFX = {k: (v["file"], v["peak_sec"], v["level_db"]) for k, v in SFX_LIB.items()}   # файл, пик (с), громкость пика (dBFS)
# Громкость звука — по роли, от голоса (25.10, калибровка ghost-editor по 6 топ-рилсам, docs/reels_knowledge/tools_review_2510.md):
# пик звука = p95 пиков голоса (окна 50 мс) + ROLE_DB[роль] + gain_db события. До 25.10 стояли подобранные на глаз −2…−8 дБ
# и общие −7 дБ под голосом: замер рилсов v2 — «уф» на 7 дБ тише цели, свисты склеек −15…−21 дБ к голосу, у порога «не слышно».
ROLE_DB = {"ui": -14.0, "whoosh": -12.0, "impact": -8.0, "meme": -3.0}
VOICE_P95_NOMINAL = -5.0   # немой черновик: p95 пиков голоса Lumean −16 LUFS (замер трёх рилсов v2 — −5.0 dBFS)
SFX_LOUDER_MAX = 1.5       # пик звука выше голоса больше чем на 1.5 дБ — громче голоса (ошибка)
SFX_INAUDIBLE = -22.0      # ниже −22 дБ к голосу — не слышно (ошибка)
SFX_OFF_TARGET = 4.0       # дальше 4 дБ от цели роли — наложение звуков (предупреждение)
SOFT_DB = {"zoom": -5.0, "new_picture": -3.0, "same_picture": -6.0}   # переходные звуки — фактура, тише своей роли
_SFX = {}

def sfx(name):
    if name not in _SFX:
        f, _, peak_db = SFX[name]
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SFX_DIR, f), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                           capture_output=True, check=True)
        x = np.frombuffer(p.stdout, np.float32).reshape(-1, 2).copy()
        x = x * (10 ** (peak_db / 20) / max(1e-6, float(np.abs(x).max())))
        f = int(0.01 * SR)                          # края 10 мс: звук не начинается щелчком
        x[:f] *= np.linspace(0, 1, f)[:, None]; x[-f:] *= np.linspace(1, 0, f)[:, None]
        _SFX[name] = x
    return _SFX[name]


# ----------------------------------------------------------------------------- сборка
def layout(spec):
    """Высота картинки из reel.json. 22.10, владелец: «в рилсах столько воздуха не оставляют» — при PH 1100 нижние 35%
    были пустой бумагой. Разбор 31 ролика (Restream): интерфейс Shorts/TikTok закрывает нижние 350–400 px, поэтому
    картинка до 1380 (23.10: при 1420 низ букв ложился на край 400 px интерфейса), полоса субтитров 1380–1530,
    внизу 390 px. Окна кадров (h в пикселях исходника) растут на view_scale — по умолчанию 1.11: рисунок крупнее,
    бока целы, рисунка больше по высоте;
    экранные координаты фраз (cy, h куклы, y пометок) пересчитываются из 1100 в PH."""
    global PH, CAP_CY, VIEW_K, PIC_TOP
    # 25.10, владелец: «сместить картинку чуть вниз: сверху чуть свободного места, внизу чуть меньше» — правило навсегда.
    # Картинка с 60 px (полоса той же бумаги с мягким краем), 1440 по высоте (владелец дважды: «длиннее внизу на 40»,
    # «всегда»), субтитры под ней (центр 1575), внизу 270 px; граница интерфейса для надписей — 360 px снизу
    # (reel_rules.SAFE_BOTTOM 1560); субтитры ниже неё — решение владельца 25.10 («всё отлично»).
    # До этого: картинка 0–1380, субтитры 1455, внизу 390 (23.10: низ букв у края 400 px интерфейса).
    PIC_TOP = int(spec.get("picture_top", 60))
    PH = int(spec.get("picture_h", 1440)); CAP_CY = PIC_TOP + PH + 75
    k = PH / BASE_PH; vk = spec.get("view_scale", round(1.0 + (k - 1.0) * 0.42, 2))   # 1380 -> 1.11: рисунок крупнее, бока целы
    VIEW_K = vk
    if k == 1 and vk == 1: return
    for b in spec["beats"]:
        for s in b["shots"]:
            for key in ("from", "to"):
                if key in s: s[key] = [s[key][0], s[key][1], s[key][2] * vk]
            for key in ("cy", "h"):
                if key in s and s.get("kind") in ("fit", "doll"): s[key] = s[key] * k
        for e in b.get("fx", []):
            if e["kind"] in ("write", "mark", "badge") and "y" in e: e["y"] = e["y"] * k

def ink_rows(reel_dir, name):
    """Верх и низ рисунка исходника (в координатах исходного кадра): строки, где туши больше 0.5% ширины."""
    g = load_src(reel_dir, name).mean(axis=2)
    rows = np.where((g < 200).mean(axis=1) > 0.005)[0]
    return (rows[0] / 2.0, rows[-1] / 2.0) if len(rows) else (0.0, g.shape[0] / 2.0)

def fill_windows(reel_dir, spec):
    """Окно не уходит ниже рисунка: высокая картинка (PH 1380) с окнами старых пропорций показывала под столом пустую
    бумагу — тот же «воздух», что был в нижних 35% экрана, только внутри картинки. Окно поднимается, пока его низ не
    ляжет на нижнюю линию рисунка (+2% воздуха); выше верха рисунка не уходит — тогда окно сжимается (наезд)."""
    for b in spec["beats"]:
        for s in b["shots"]:
            if "src" not in s or s.get("kind") in ("fit", "stack", "doll"): continue
            if s.get("anim") or s.get("keep_window"): continue   # сцена с движением (предмет прилетает из-за рисунка)
                                                    # или план, где автор сознательно оставляет воздух (широкий низкий рисунок)
            top, bot = ink_rows(reel_dir, s["src"])
            hs = [s[k][2] for k in ("from", "to") if k in s]
            cap = (bot - top) * 1.04                    # окно выше рисунка: from и to сжимались к одной высоте и план стоял
            if max(hs) > cap:                           # (рилс эп.01: 710/666 -> 530/528, 9 % неподвижных кадров) — сжать
                for k in ("from", "to"):                # пару одним множителем, наезд сохраняется
                    if k in s: s[k] = [s[k][0], s[k][1], s[k][2] * cap / max(hs)]
            for key in ("from", "to"):
                if key not in s: continue
                cx, cy, h = s[key]; pad = 0.02 * h
                if cy + h / 2 > bot + pad:
                    cy = bot + pad - h / 2
                    if cy - h / 2 < top - pad:
                        h = (bot - top) + 2 * pad; cy = (top + bot) / 2
                s[key] = [cx, cy, h]

def overlay_boxes(events, shots=()):
    """Рамки рукописных надписей и маркера по туши, в пикселях картинки (на экран — + PIC_TOP): для безопасных зон.
    Надпись приклеена к бумаге и едет с наездом плана, поэтому рамка — объединение по всему времени, пока она видна."""
    out = []
    for e in events:
        if e["kind"] not in ("write", "mark"):
            continue
        im = text_img(e["text"], font(HAND, e.get("size", 120), 700), INK)
        gx0, gy0, gx1, gy1 = im.getchannel("A").getbbox()
        ox, oy = e["x"] - im.width / 2, e["y"] - im.height / 2
        box = [ox + gx0, oy + gy0, ox + gx1, oy + gy1]
        end = e["t"] + max(e.get("dur", 0.5), e.get("hold") or 0.0)
        for s in shots if e["kind"] == "write" else ():
            a0, a1 = max(e["t"], s["t0"]), min(end, s["t1"])
            started_here = s["t0"] - 0.01 <= e["t"] < s["t1"]
            if a1 <= a0 or "from" not in s or s.get("kind", "crop") != "crop" or \
                    not (started_here or e.get("kind_of_shot", "crop") == "crop"):   # удержание — только в планах того же рода
                continue
            vx0, vy0, vh0 = shot_view(s, a0)
            for tt in np.linspace(a0, a1 - 1e-3, 8):
                vx, vy, vh = shot_view(s, tt); k = vh0 / vh
                for px, py in ((box[0], box[1]), (box[2], box[3])):
                    qx, qy = (px - W / 2) * k + W / 2 + (vx0 - vx) * PH / vh, (py - PH / 2) * k + PH / 2 + (vy0 - vy) * PH / vh
                    box = [min(box[0], qx), min(box[1], qy), max(box[2], qx), max(box[3], qy)]
        out.append((e.get("beat"), e["text"], *box))
    return out

def after_sfx_source(beats, bi):
    """Звук, на пик которого встаёт фраза bi (after_sfx): ближайший такой звук в этой фразе или раньше. Раньше брался
    первый в ролике — второй riser (эп.01 v6, раскрытие «две строчки») вставал на пик riser хука, то есть никуда."""
    name = beats[bi]["after_sfx"]
    return next((j, e) for j in range(bi, -1, -1) for e in reversed(beats[j].get("fx", []))
                if e["kind"] == "sfx" and e["name"] == name)

def hook_split_errors(words, times, spans):
    """Хук — одна группа субтитров с первого кадра. Шире строки (CAP_MAX_W) chunks делит его молча, и первые полсекунды
    видно полхука (эп.01 v6: «„Тебе» отдельно, 984 px при 860) — это ошибка рилса, а не раскладки субтитров."""
    first = next(iter(chunks(words, times)), None)
    n = spans[0][1] - spans[0][0]
    if first is None or len(first["idx"]) >= n:
        return []
    return [f"хук «{' '.join(clean(w) for w in words[:n])}» не влезает в одну строку субтитров "
            f"({cap_width(list(range(n)), words)} px > {CAP_MAX_W}): короче или без лишнего слова"]

def build(reel_dir, sheet=False, preview=False, force=False):
    spec = json.load(open(os.path.join(reel_dir, "reel.json"), encoding="utf8"))
    import reel_rules                                  # правила рилса кодом: хук, riser с 0 с, звуки владельца, планы ≤ 3 с
    rule_errs = reel_rules.check_spec(spec, set(SFX))
    log_p = os.path.join(ROOT, "docs", "reels_log.json")           # против шаблона: паспорт против прошлых рилсов
    rule_errs += reel_rules.check_passport(spec, json.load(open(log_p, encoding="utf8")) if os.path.exists(log_p) else [],
                                           os.path.relpath(reel_dir, ROOT))
    rule_errs += reel_rules.check_hook(spec, json.load(open(log_p, encoding="utf8")) if os.path.exists(log_p) else [],
                                       os.path.relpath(reel_dir, ROOT))      # волна 9: паспорт хука (стандарт 9)
    rule_errs += reel_rules.check_call_to_comment(spec)    # призыв в комментарии — всегда
    rule_errs += reel_rules.check_brand_and_face(spec)     # имя бренда и эмоция куклы не теряются
    rule_errs += reel_rules.check_hook_steal(spec, json.load(open(log_p, encoding="utf8")) if os.path.exists(log_p) else [],
                                             os.path.relpath(reel_dir, ROOT))   # хук ворует внимание (стандарт 13)
    rule_errs += reel_rules.check_hook_layers(spec)    # хук: пять слоёв и 3C (правило владельца 24.10)
    rule_errs += reel_rules.check_hook_motion(spec, json.load(open(log_p, encoding="utf8")) if os.path.exists(log_p) else [],
                                              os.path.relpath(reel_dir, ROOT), reel_dir)   # движение в рисунке (стандарт 14)
    rule_errs += reel_rules.check_matrix(spec)          # матрица: каждый приём базы решён в этом рилсе (стандарт 10)
    rule_errs += reel_rules.check_coverage(spec, json.load(open(log_p, encoding="utf8")) if os.path.exists(log_p) else [],
                                           os.path.relpath(reel_dir, ROOT))  # стратегия: каждый пункт решён (стандарт 11)
    rule_errs += reel_rules.check_human(spec)           # человеческий текст: без тире и рваной парцелляции (стандарт 11)
    rule_errs += reel_rules.check_inventory(spec, json.load(open(log_p, encoding="utf8")) if os.path.exists(log_p) else [],
                                            os.path.relpath(reel_dir, ROOT))   # весь инвентарь базы (стандарт 12)
    layout(spec)
    beats = spec["beats"]
    prepare_src(reel_dir, spec.get("sources", {}))
    if spec.get("fill_ink", True): fill_windows(reel_dir, spec)
    words, spans = tokens(beats)
    al = os.path.join(reel_dir, "alignment.json")
    vw = os.path.join(reel_dir, "voice", "words.json")   # голос Lumean (reel_voice.py): фразы раскладываются здесь
    nat = None                                       # естественное время слов в дорожке голоса — откуда резать куски
    if os.path.exists(al):
        times = json.load(open(al, encoding="utf8")); voiced = True
        assert len(times) == len(words), f"alignment: {len(times)} слов, в сценарии {len(words)}"
    else:
        if os.path.exists(vw):
            nat = json.load(open(vw, encoding="utf8")); voiced = True
            assert len(nat) == len(words), f"голос: {len(nat)} слов, в сценарии {len(words)} — озвучить заново (reel_voice.py)"
            times = [dict(w) for w in nat]
        else:
            times = estimate_times([clean(w) for w in words], rate=spec.get("rate", 1.0)); voiced = False
        for b, (i0, _i1) in zip(beats, spans):        # немая пауза после слова (стоп-кадр с тишиной, Runia)
            for k, sec in b.get("gaps", []):
                times = times[:i0 + k + 1] + [dict(w, start=w["start"] + sec, end=w["end"] + sec) for w in times[i0 + k + 1:]]
    lead = spec.get("lead_in", 0.0)                  # перебивка до первого слова: сначала остановить, потом смысл (vidIQ)
    if lead:
        times = [dict(w, start=w["start"] + lead, end=w["end"] + lead) for w in times]
    if not voiced or nat:                             # фраза ждёт пика звука: «Психолог…» встаёт на пик riser, пауза — нарастание
        for bi, b in enumerate(beats):
            if not b.get("after_sfx"): continue
            src_bi, src_e = after_sfx_source(beats, bi)
            w = times[spans[src_bi][0] + src_e.get("at", 0)]
            t_sfx = (w["end"] if src_e.get("after") else w["start"]) + src_e.get("dt", 0.0)
            peak = t_sfx + (SFX[b["after_sfx"]][1] if src_e.get("align") == "start" else 0.0)
            shift = peak - times[spans[bi][0]]["start"] + CUT_LEAD
            k0 = spans[bi][0]                         # голос: фраза может и подтянуться к пику, если не налезает на прошлую
            if shift > 0 or (nat and k0 and times[k0 - 1]["end"] + 0.05 <= times[k0]["start"] + shift):
                times = times[:spans[bi][0]] + [dict(x, start=x["start"] + shift, end=x["end"] + shift) for x in times[spans[bi][0]:]]
    anchors = sorted(spans[bi][0] for bi, b in enumerate(beats) if b.get("after_sfx"))
    if not voiced:                                    # немой рилс: темп — скорость чтения, а не диктора
        for _ in range(3):
            for c in chunks(words, times):
                txt = " ".join(cap_text(words[j]) for j in c["idx"])
                need = max(CAP_MIN_SEC, len(txt) / CAP_CPS)
                k_next = c["idx"][-1] + 1
                if k_next >= len(times): continue
                have = times[k_next]["start"] - times[c["idx"][0]]["start"]
                if have < need:
                    d = need - have
                    # фраза на пике звука (after_sfx) уже стоит позже, чем нужно чтению, — сдвиг до неё уходит в этот
                    # запас и не уводит склейку с пика (эп.01 v3: хук в две группы уводил первую склейку на 1.88 с)
                    a = next((x for x in anchors if x > k_next), None)
                    if k_next not in anchors and a is not None and times[a - 1]["end"] + d <= times[a]["start"]:
                        times = times[:k_next] + [dict(x, start=x["start"] + d, end=x["end"] + d) for x in times[k_next:a]] + times[a:]
                    else:
                        times = times[:k_next] + [dict(x, start=x["start"] + d, end=x["end"] + d) for x in times[k_next:]]
    total = times[-1]["end"] + spec.get("tail", 0.5)

    # кадрирования: у фразы shots=[{at: номер слова во фразе, ...}]; начало плана = начало слова - CUT_LEAD
    shots = []
    for b, (i0, _i1) in zip(beats, spans):
        for s in b["shots"]:
            k = i0 + s.get("at", 0)
            shots.append(dict(s, t0=max(0.0, times[k]["start"] - (CUT_LEAD if k else 0)), beat=b, bi=beats.index(b)))
    shots.sort(key=lambda s: s["t0"])
    shots[0]["t0"] = 0.0                              # перебивка до первого слова идёт на первом плане, а не в пустоту
    # кукла живёт по общему времени ролика: смена плана с куклой не перезапускает моргание и лицо
    # и по своим часам, которые идут с первого появления: правка фраз до куклы не меняет её моргания и взгляды
    # (23.10: пауза 0.5 с во фразе 5 сдвинула куклу по фоновому плану жизни — другой отрезок, другие движения)
    doll_first = min([s["t0"] for s in shots if s.get("kind") == "doll"] or [0.0])
    doll_acts = [dict(a, t=a["t"] + s["t0"] - doll_first + DOLL_LIFE_PHASE)
                 for s in shots if s.get("kind") == "doll" for a in s.get("actions", [])]
    for s in shots:
        if s.get("kind") == "doll": s["doll_acts"] = doll_acts; s["doll_t0"] = doll_first
    for a, b in zip(shots, shots[1:]): a["t1"] = b["t0"]
    shots[-1]["t1"] = total
    for s in shots:                                   # сцене анимации — время слов её фразы (удар на слове)
        if s.get("anim"):
            i0, i1 = spans[s["bi"]]
            s["anim_ctx"] = dict(words=[(round(times[k]["start"], 4), round(times[k]["end"], 4)) for k in range(i0, i1)])
    # события внутри фраз: наезд, тряска, стрелка, надпись — привязаны к слову
    def wt(b_idx, k, after=False):
        w = times[spans[b_idx][0] + k]
        return w["end"] if after else w["start"]
    events = []
    for bi, b in enumerate(beats):
        for e in b.get("fx", []):                     # after: от конца слова (riser — сразу после фразы-хука)
            events.append(dict(e, t=wt(bi, e.get("at", 0), e.get("after", False)) + e.get("dt", 0.0), beat=bi))
            if "strike_at" in e:                      # зачёркивание: только если поле задано в reel.json
                events[-1]["strike_t"] = wt(bi, e["strike_at"]) + e.get("strike_dt", 0.0)
    for e in events:                                  # удержание накладки — только пока идут планы того же рода
        e["kind_of_shot"] = next((x.get("kind", "crop") for x in reversed(shots) if x["t0"] <= e["t"] + CUT_LEAD), "crop")
    caps_txt = [dict(t0=c["t0"], t1=c["t1"], text=" ".join(cap_text(words[j]) for j in c["idx"])) for c in chunks(words, times)]
    caps_txt[0]["t0"] = 0.0                            # хук стоит с первого кадра (still)
    rule_errs += hook_split_errors(words, times, spans)
    rule_errs += reel_rules.check_hook_gap(times, spans, beats)
    rule_errs += reel_rules.check_montage(spec, shots, events, total)
    rule_errs += reel_rules.check_timeline(shots, events, {k: v[1] for k, v in SFX.items()}, caps_txt, total)
    rule_errs += reel_rules.check_overlays([(i, tx, x0, y0 + PIC_TOP, x1, y1 + PIC_TOP)    # картинка — с PIC_TOP экрана
                                            for i, tx, x0, y0, x1, y1 in overlay_boxes(events, shots)], PIC_TOP + PH)
    rule_errs += reel_rules.check_cta(spec, [times[i0]["start"] for i0, _ in spans], total)
    rule_errs += reel_rules.rehook_timing(spec, [times[i0]["start"] for i0, _ in spans])
    import reel_geom                                  # до рендера: обрывки у краёв, кукла шире кадра, надпись на рисунке
    rule_errs += reel_geom.check(sys.modules[__name__], reel_dir, shots, events)
    rule_errs += reel_rules.check_knowledge(spec)                 # знания базы: маркетинг, воронка, бренд — у каждой фразы
    rule_errs += reel_rules.knowledge_timing(spec, [times[i0]["start"] for i0, _ in spans], total)
    rule_errs += reel_rules.check_sounds(sound_plan(shots, events))
    rule_errs += reel_rules.check_cut_sounds(sound_plan(shots, events), shots, CUT_SOUND_NEAR)
    rule_errs += reel_rules.check_whoosh_gap(sound_plan(shots, events))
    rule_errs += reel_rules.check_spots(spec, events)
    rule_errs += reel_rules.check_writing(events, shots)
    rule_errs += reel_rules.check_written_read(events, shots)  # дописанное слово не срезано склейкой
    for w in reel_rules.warnings(spec, shots, total, events) + reel_rules.sound_warnings(sound_plan(shots, events)):
        print("  ⚠ " + w)
    if rule_errs:
        print("ПРАВИЛА РИЛСА (docs/REELS_PLAYBOOK.md):\n" + "\n".join("  ✗ " + e for e in rule_errs))
        if not force:
            raise SystemExit("не рендерю: исправьте reel.json (или --force, если нарушение осознанное)")
    caps = chunks(words, times)
    # текст хука стоит с первого кадра целиком, без въезда и бледных слов (разбор 22.10: heyDominik, Jenny Hoyos —
    # пролистывание в первые 0.5 с — «не понял, о чём», поэтому хук читается сразу; подсветка слов идёт как обычно)
    caps[0]["t0"] = 0.0
    if spec.get("hook_still"): caps[0]["still"] = True   # старые рилсы: хук целиком с первого кадра (до 25.10)
    for c in caps:
        c["imgs"] = {j: render_chunk(words, c["idx"], j, fade_ahead=not c.get("still")) for j in c["idx"]}

    if sheet:
        return contact_sheet(reel_dir, shots)

    tex = paper_tex()
    hook_clock = spec.get("clock")
    if hook_clock:                                   # часы хука привязаны к словам: [фраза, слово]
        spec["clock"] = hook_clock = dict(hook_clock, t0=wt(*hook_clock["from_word"]), t1=wt(*hook_clock["to_word"]))
        hook_clock["t_end"] = hook_clock["t1"] + 0.9
        if hook_clock.get("hide_on_cut"):            # часы уходят вместе со своим планом, а не висят над следующим
            hook_clock["t_end"] = min([s["t0"] for s in shots if s["t0"] > hook_clock["t1"]] + [hook_clock["t_end"]])
    wav = os.path.join(reel_dir, "reel_audio.wav")      # звук до картинки: его проверка дешёвая, рендер — нет
    snd = mix_audio(wav, total, shots, events, spec, voiced, voice_segments(reel_dir, nat, times) if nat else None,
                    words=times if voiced else None)
    print(f"  звук: голос p95 {snd['voice_p95']} dBFS, звуков {len(snd['sounds'])}")
    for m in snd["warnings"]: print("  ⚠", m)
    for m in snd["errors"]: print("  ✗", m)
    if snd["errors"] and not force:
        raise SystemExit("звук: " + "; ".join(snd["errors"]) + " — рендер остановлен (--force — только с причиной)")
    vid = os.path.join(reel_dir, "reel_preview.mp4" if preview else "reel_video.mp4")
    fps = 15 if preview else FPS
    render_video(reel_dir, vid, fps, total, shots, events, caps, words, times, tex, hook_clock)

    out = os.path.join(reel_dir, "reel_preview_av.mp4" if preview else "reel.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    json.dump(dict(total=total, voiced=voiced, picture_h=PH, picture_top=PIC_TOP, words=times,
                   voice_p95=snd["voice_p95"], sounds=sorted(snd["sounds"], key=lambda r: r["peak"]),
                   events=[dict(kind=e["kind"], t=round(e["t"], 3), beat=e.get("beat"), **({"name": e["name"]} if e.get("name") else {}))
                           for e in sorted(events, key=lambda e: e["t"])],
                   shots=[dict(t0=round(s["t0"], 3), t1=round(s["t1"], 3), kind=s.get("kind", "crop"), src=s.get("src"),
                              **({"closeup": True} if s.get("closeup") else {})) for s in shots],
                   captions=[dict(t0=round(c["t0"], 3), t1=round(c["t1"], 3),
                                  text=" ".join(clean(words[j]) for j in c["idx"])) for c in caps]),
              open(os.path.join(reel_dir, "reel_report.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    write_srt(os.path.join(reel_dir, "reel.srt"), caps, words)
    if not preview:
        import reel_proof                              # лист проверки: один кадр-лист вместо десятка кадров
        print("  лист проверки:", reel_proof.proof(reel_dir))
        import reel_publish                            # комплект публикации: обложка, подпись, UTM, комментарий, варианты хука
        print("  комплект публикации:", reel_publish.publish(reel_dir))
    print(f"Готово. Файл: {out} ({total:.1f} с, планов {len(shots)}, групп субтитров {len(caps)})")
    return out

X264 = ["-c:v", "libx264", "-preset", "slow", "-crf", "19",
        "-maxrate", "9M", "-bufsize", "18M",        # зерно жмётся плохо: потолок ~9 Мбит/с, Reels всё равно пережмёт
        "-pix_fmt", "yuv420p",
        "-threads", "1"]   # VBV (maxrate) в несколько потоков x264 недетерминирован: тот же кадр через трубу давал разный
                           # поток от темпа подачи (замер 23.10: 3 подачи — 3 файла; без VBV или в 1 поток — один файл).
                           # Параллелим по планам (render_video), каждому кодеку — один поток: детерминизм без потерь.

def _code_sig():
    """Подпись кода картинки: правка reel.py, модуля движения, библиотеки звуков или рига куклы перерисовывает все планы."""
    h = hashlib.md5()
    for p in (os.path.abspath(__file__), os.path.join(SFX_DIR, "library.json"), os.path.join(ROOT, "scripts", "anim.py"),
              os.path.join(ROOT, "experiments", "alive_cat", "doll", "doll_rig.py"),
              os.path.join(ROOT, "experiments", "alive_cat", "doll", "rig.json")):
        if os.path.exists(p): h.update(open(p, "rb").read())
    return h.hexdigest()

_MD5 = {}
def _file_md5(p):
    """По содержимому, не по времени файла: копия папки или пересборка того же исходника кэш не сбрасывает."""
    st = os.stat(p); k = (p, st.st_size, st.st_mtime_ns)
    if k not in _MD5: _MD5[k] = hashlib.md5(open(p, "rb").read()).hexdigest()
    return _MD5[k]

def _plain(x):
    """Без служебных полей (`_anchor` меняется при рендере) и без ссылки плана на фразу."""
    if isinstance(x, dict): return {k: _plain(v) for k, v in sorted(x.items()) if not k.startswith("_") and k != "beat"}
    if isinstance(x, (list, tuple)): return [_plain(v) for v in x]
    return x

def segment_key(reel_dir, fps, n0, n1, i, shots, events, caps, words, times, hook_clock, total, code_sig):
    """Всё, от чего зависят кадры n0..n1 плана i: сам план и соседи (хлёст смазывает оба края склейки), события,
    которые могут быть видны (накладки держатся до 6 с), субтитры, часы хука, исходники, код. Совпал ключ — кадры
    те же, план берётся из кэша без рендера."""
    t0, t1 = n0 / fps, n1 / fps
    srcs = sorted({x["src"] for x in shots[max(0, i - 1):i + 2] if "src" in x})
    src_sig = [(s_, _file_md5(p_)) for s_ in srcs
               for p_ in [os.path.join(reel_dir, "src", s_ + "_c.png")] if os.path.exists(p_)]
    for x in shots[max(0, i - 1):i + 2]:            # сцена анимации: её код и рисунки — тоже исходник кадров
        if x.get("anim"):
            import anim
            src_sig += [(x["anim"], _file_md5(p_)) for p_ in anim.scene_files(reel_dir, x["anim"])]
    ev = [e for e in events if t0 - 7.0 <= e["t"] <= t1 + 0.5]
    cp = [dict(c0=c["t0"], c1=c["t1"], words=[words[j] for j in c["idx"]], still=c.get("still"),
               at=[round(times[j]["start"], 4) for j in c["idx"]])
          for c in caps if c["t0"] < t1 + 0.5 and c["t1"] > t0 - 0.5]
    hc = hook_clock if hook_clock and hook_clock["t0"] < t1 and hook_clock["t_end"] > t0 else None
    blob = json.dumps(_plain(dict(v=code_sig, fps=fps, n=[n0, n1], shots=shots[max(0, i - 1):i + 2], ev=ev, caps=cp,
                                  clock=hc, total=round(total, 4), src=src_sig, ph=PH)), sort_keys=True, default=str)
    return hashlib.md5(blob.encode()).hexdigest()[:16]

_JOB = None
def _init_job(job):
    """Состояние сборки для процесса-рисовальщика: планы, события, субтитры и раскладка (PH из reel.json)."""
    global _JOB, PH, CAP_CY, PIC_TOP
    _JOB = job[:10]; PH, CAP_CY, PIC_TOP = job[10], job[11], job[12]

def _render_segment(job):
    """Один план в свой файл. Кадр зависит только от времени и плана (кэши кипения, зерна, куклы — по времени), поэтому
    план, отрисованный в другом процессе, побайтно тот же, что в одном процессе (сверено 23.10, md5 кусков)."""
    i, n0, n1, path = job
    reel_dir, fps, shots, events, caps, words, times, tex, hook_clock, total = _JOB
    tmp = path + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(fps), "-i", "-", *X264, tmp], stdin=subprocess.PIPE)
    for fi in range(n0, n1):
        ff.stdin.write(render_frame(reel_dir, fi / fps, shots, events, caps, words, times, tex, hook_clock, total).tobytes())
    ff.stdin.close(); ff.wait(); os.replace(tmp, path)
    return f"  план {i + 1}/{len(shots)}: кадры {n0}–{n1 - 1}"

def render_video(reel_dir, vid, fps, total, shots, events, caps, words, times, tex, hook_clock):
    """Видео планами с кэшем (23.10, по решению владельца «ускорить без потери качества»): каждый план — свой файл
    x264 с теми же настройками, ключ — всё, от чего зависят его кадры (`segment_key`); поменяли одну фразу —
    перерисовываются только её планы и соседи, остальное склеивается из кэша без перекодирования (concat, -c copy).
    Каждый кусок начинается с ключевого кадра; качество задаёт тот же CRF, что и у цельного прохода."""
    cache = os.path.join(reel_dir, ".cache"); os.makedirs(cache, exist_ok=True)
    n = int(total * fps); code_sig = _code_sig()
    starts = [int(math.ceil(s["t0"] * fps - 1e-6)) for s in shots] + [n]
    segs, used, todo = [], set(), []
    for i in range(len(shots)):
        n0, n1 = max(0, starts[i]), min(n, starts[i + 1])
        if n1 <= n0: continue
        key = segment_key(reel_dir, fps, n0, n1, i, shots, events, caps, words, times, hook_clock, total, code_sig)
        path = os.path.join(cache, f"seg_{fps}_{key}.mp4"); used.add(os.path.basename(path)); segs.append(path)
        if not os.path.exists(path): todo.append((i, n0, n1, path))
    job = (reel_dir, fps, shots, events, caps, words, times, tex, hook_clock, total, PH, CAP_CY, PIC_TOP)
    jobs = max(1, min(int(os.environ.get("REEL_JOBS", os.cpu_count() or 1)), len(todo)))
    if jobs > 1:                                      # планы независимы: каждый — свой процесс и свой файл x264
        import multiprocessing as mp                  # spawn, не fork: fork при живых потоках OpenCV вешал процессы
        with mp.get_context("spawn").Pool(jobs, initializer=_init_job, initargs=(job,)) as pool:   # (замер 23.10)
            for msg in pool.imap_unordered(_render_segment, todo): print(msg, flush=True)
    else:
        _init_job(job)
        for t in todo: print(_render_segment(t), flush=True)
    print(f"  планов перерисовано {len(todo)}, из кэша {len(segs) - len(todo)}, процессов {jobs}")
    lst = os.path.join(cache, "concat.txt")
    open(lst, "w").write("".join(f"file '{os.path.basename(p)}'\n" for p in segs))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid], check=True)
    for f in os.listdir(cache):                       # кэш не растёт: держим только куски этой сборки
        if f.startswith(f"seg_{fps}_") and f not in used: os.remove(os.path.join(cache, f))

def lerp(a, b, u):
    return a + (b - a) * u

def shot_view(s, t):
    """Окно камеры плана в момент t: постоянная скорость от from к to, плюс наезды плана (punch)."""
    d = max(1e-3, s["t1"] - s["t0"]); u = (t - s["t0"]) / d
    if s.get("ease") == "out": u = ease_out(u)
    elif s.get("ease") == "io": u = ease_io(u)
    elif s.get("ease") == "in": u = min(max(u, 0.0), 1.0) ** 2.2   # разгон к склейке: картинка нарастает вместе с riser
    f, to = s["from"], s.get("to", s["from"])
    cx, cy, h = (lerp(f[i], to[i], u) for i in range(3))
    # хлёст в начале плана: окно прилетает из сдвига (whip), 0.18 с с торможением
    if s.get("whip"):
        k = 1 - ease_out((t - s["t0"]) / 0.18)
        dx, dy = s["whip"]
        cx += dx * k; cy += dy * k
    # быстрый наезд/отъезд в начале плана (zoom-in transition)
    if s.get("zoom_in"):
        k = 1 - ease_out((t - s["t0"]) / 0.30)       # 0.3 с с торможением (разбор: 11-15 кадров, ease-out)
        h *= 1 + s["zoom_in"] * k
    return cx, cy, h

def motion_blur(img, dx, dy):
    k = int(max(abs(dx), abs(dy)))
    if k < 3: return img
    k = min(k, 90)
    ker = np.zeros((k, k), np.float32)
    if abs(dx) >= abs(dy): ker[k // 2, :] = 1
    else: ker[:, k // 2] = 1
    return cv2.filter2D(img, -1, ker / k)

def punch_at(events, s, t):
    """Наезды плана в момент t. Обычный — 0.12 с с торможением и держится до конца плана; style "cut" — склейкой в
    один кадр, держится hold и склейкой назад: «сглаженный удар убит» (HyperFrames film.md; Tella add-zooms 1.18–1.30)."""
    punch = 1.0
    for e in events:
        if e["kind"] == "punch" and s["t0"] <= e["t"] <= t < s["t1"]:
            if e.get("style") == "cut":
                if t < e["t"] + e.get("hold", 1e9):
                    punch *= 1 + e.get("amt", 0.22)
            else:
                punch *= 1 + e.get("amt", 0.14) * ease_out((t - e["t"]) / 0.12)
    return punch

def punch_focus(events, s, t):
    """Центр окна удара-наезда склейкой (focus [x, y] в координатах окон reel.json): Tella add-zooms наезжает на лицо, а
    лицо говорящей головы и так вверху кадра; у нас кот часто внизу. Лист 25.10: наезд к центру окна срезал коту лапы."""
    for e in events:
        if (e["kind"] == "punch" and e.get("style") == "cut" and e.get("focus") and s["t0"] <= e["t"] <= t < s["t1"]
                and t < e["t"] + e.get("hold", 1e9)):
            return e["focus"]
    return None

def render_frame(reel_dir, t, shots, events, caps, words, times, tex, hook_clock, total):
    s = next(x for x in shots if x["t0"] <= t < x["t1"] or x is shots[-1])
    kind = s.get("kind", "crop")
    shake = (0.0, 0.0); rot = 0.0
    punch = punch_at(events, s, t)
    for e in events:
        if e["kind"] == "shake" and 0 <= t - e["t"] < e.get("dur", 0.45):
            k = 1 - (t - e["t"]) / e.get("dur", 0.45); A = e.get("amp", 22) * k
            shake = (A * math.sin(t * 93), A * 0.7 * math.cos(t * 71)); rot = 0.6 * k * math.sin(t * 57)
    if kind == "crop":
        src = load_src(reel_dir, s["src"])
        cx, cy, h = shot_view(s, t)
        pf = punch_focus(events, s, t)
        if pf:                                      # окно удара — по центру своей точки (лицо низко в кадре:
            cx, cy = pf[0], pf[1]                   # наезд «на месте» всё равно срезал бы лапы)
        if s.get("anim"):                           # движение внутри рисунка: картинку и реакцию камеры даёт сцена
            import anim
            img, cam = anim.scene(reel_dir, s["anim"]).frame(t, s["anim_ctx"])
            src = np.clip(img, 0, 255).astype(np.uint8)
            shake = (shake[0] + cam.get("dx", 0.0), shake[1] + cam.get("dy", 0.0))
            punch *= cam.get("zoom", 1.0); rot += cam.get("rot", 0.0)
        # второй слой камеры: медленный поворот до 0.5° поверх дрейфа, на соседних планах в разные стороны
        sign = 1 if s.get("bi", 0) % 2 else -1   # одно направление на фразу (мысль): Tim Runia; правило длинного ролика
        rot += s.get("rot_drift", 0.5) * sign * ((t - s["t0"]) / max(1e-3, s["t1"] - s["t0"]) - 0.5)
        base = grade(sharpen(sample(src, cx, cy, h / punch, shake=shake, rot=rot, boil_t=t, reflect=bool(s.get("anim")))))
        view = (cx, cy, h / punch)
        if s.get("whip"):
            k = 1 - ease_out((t - s["t0"]) / 0.18)
            if k > 0.05:
                sc = PH / (h / punch) / 2.0
                base = motion_blur(base, s["whip"][0] * k * sc * 0.25 * 2.0 * 0.5, s["whip"][1] * k * sc * 0.25)
        if s.get("zoom_in"):                       # вход наездом: размытие гаснет за 0.25 с (white minimal: blur 30->0)
            k = 1 - ease_out((t - s["t0"]) / 0.25)
            if k > 0.05: base = cv2.GaussianBlur(base, (0, 0), 1 + 7 * k)
        nxt = next((x for x in shots if x["t0"] >= s["t1"] - 1e-6 and x is not s), None)
        if nxt is not None and nxt.get("whip") and s["t1"] - t < 0.1:   # уходящий кадр смазывается в сторону хлёста
            k = ease_io(1 - (s["t1"] - t) / 0.1)
            base = motion_blur(np.roll(base, int(-nxt["whip"][0] * 0.08 * k), axis=1), -nxt["whip"][0] * 0.08 * k, 0)
    else:
        view = None
        base = tex[:PH].copy()
        d = max(1e-3, s["t1"] - s["t0"]); u = (t - s["t0"]) / d
        zs = lerp(s.get("zoom", (1.0, 1.06))[0], s.get("zoom", (1.0, 1.06))[1], u) * punch
        if kind == "fit":
            src = load_src(reel_dir, s["src"])
            base = fit_on_paper(base, src, s["region"], s.get("cy", PH * 0.5) + shake[1], s.get("width", 0.96), zs, dx=shake[0])
        elif kind == "stack":
            for part in s["parts"]:
                src = load_src(reel_dir, part["src"])
                base = fit_on_paper(base, src, part["region"], part["cy"], part.get("width", 0.94), zs)
        elif kind == "doll":
            td = math.floor((t - s["doll_t0"]) * DOLL_FPS) / DOLL_FPS + DOLL_LIFE_PHASE              # кукла «на двойках»
            rgba = doll_frame(td, total - s["doll_t0"] + DOLL_LIFE_PHASE + 0.5, s["doll_acts"])
            ey = 0.0
            if s.get("enter", {}).get("kind") == "drop":   # кукла падает на пол с отскоком (п.1.20), а не возникает
                eu = (t - s["t0"]) / s["enter"].get("dur", 0.5)
                ey = -(1.0 - ease_out_back(eu, s=1.7)) * PH * 0.22 if eu < 1.0 else 0.0
            base = paste_doll(base, rgba, s.get("cx", W / 2) + shake[0], s.get("cy", PH * 0.55) + shake[1] + ey, s.get("h", 900) * zs)
    base = np.ascontiguousarray(boil(base, t)) if kind in ("fit", "stack") else np.ascontiguousarray(base)
    for e in events:                                # прожектор: всё, кроме главного, темнеет до 25% (Golden «darken all but focus»)
        if e["kind"] == "spot" and s["t0"] <= e["t"] <= t < s["t1"]:
            u = ease_out((t - e["t"]) / 0.25)
            if view is not None:
                vx, vy, vh = view; k = PH / vh
                sx, sy, r = (e["x"] - vx) * k + W / 2, (e["y"] - vy) * k + PH / 2, e["r"] * k
            else:
                sx, sy, r = e["x"], e["y"], e["r"]
            Y, X = np.ogrid[:PH, :W]
            d = np.sqrt((X - sx) ** 2 + (Y - sy) ** 2)
            m = np.clip((d - r) / (r * 1.2), 0, 1).astype(np.float32)[..., None] * 0.25 * u
            base = (base.astype(np.float32) * (1 - m)).astype(np.uint8)

    # накладки фраз (в координатах картинки 1080xPH)
    arrows = []
    for e in events:
        held = e.get("hold") and e["t"] <= t < e["t"] + e["hold"] and kind == e.get("kind_of_shot", kind)
        if not (s["t0"] - 0.01 <= e["t"] <= t < s["t1"] + 0.01 or held):
            continue
        if e["kind"] == "write":                    # рукописная надпись на рисунке, пишется ~0.5 с
            im = text_img(e["text"], font(HAND, e.get("size", 120), 700), RED if e.get("red", True) else INK)
            u = (t - e["t"]) / e.get("dur", 0.5)
            x, y, sc = e["x"], e["y"], 1.0
            if view is not None:                    # приклеена к бумаге: едет и растёт вместе с рисунком (наезд, тряска)
                ev = e.setdefault("_anchor", {}).get(id(s))
                if ev is None:
                    vx, vy, vh = shot_view(s, max(e["t"], s["t0"]))
                    ev = e["_anchor"][id(s)] = ((e["x"] - W / 2) * vh / PH + vx, (e["y"] - PH / 2) * vh / PH + vy, vh)
                vx, vy, vh = view; k = PH / vh
                x, y, sc = (ev[0] - vx) * k + W / 2 + shake[0], (ev[1] - vy) * k + PH / 2 + shake[1], ev[2] / vh
            if e.get("pop"):                         # пружина появления 70 → 110 → 100 % за ~12 кадров (п.1.22)
                sc *= 0.7 + 0.3 * ease_out_back((t - e["t"]) / 0.4, s=4.0)
            over(base, im, x, y, wipe=min(1.0, u * 1.05), scale=sc)
            if e.get("pen") and 0.0 < u * 1.05 < 1.0:  # карандаш виден, пока пишет (п.1.21): графит, не тёплое дерево
                pen_tip(base, x - im.width * sc / 2 + im.width * sc * u * 1.05, y + im.height * sc * 0.18, im.height * sc)
            if e.get("strike_t") is not None and t >= e["strike_t"]:   # зачёркнуто от руки на слове (Aeovisuals,
                strike(base, im, x, y, sc, (t - e["strike_t"]) / 0.28)     # 07 §8.32): старый ярлык перечёркнут, не стёрт
        elif e["kind"] == "arrow":
            arrows.append(e)
        elif e["kind"] == "ring" and t - e["t"] < e.get("dur", 1.0) and view is not None:
            vx, vy, vh = view; k = PH / vh
            ring_lines(base, (e["x"] - vx) * k + W / 2 + shake[0], (e["y"] - vy) * k + PH / 2 + shake[1], e["r"] * k, t)
        elif e["kind"] == "hands" and view is not None:   # стрелки на пустом циферблате: «время снова видно»
            vx, vy, vh = view; k = PH / vh
            sx, sy = (e["x"] - vx) * k + W / 2, (e["y"] - vy) * k + PH / 2; r = e["r"] * k
            u = (t - e["t"]) / 0.35
            for ang, ln, th in ((-60, 0.48, 22), (55, 0.72, 15)):           # часовая на ~10, минутная на ~2
                a = math.radians(ang - 90); L = r * ln * ease_out(u)
                cv2.line(base, (int(sx), int(sy)), (int(sx + L * math.cos(a)), int(sy + L * math.sin(a))), INK, th, cv2.LINE_AA)
            if u > 0: cv2.circle(base, (int(sx), int(sy)), 16, RED, -1, cv2.LINE_AA)
            for q in range(12):                                             # деления — проявляются вслед за стрелками
                if u * 12 > q:
                    a = math.radians(q * 30); r0, r1 = r * (0.80 if q % 3 else 0.72), r * 0.90
                    cv2.line(base, (int(sx + r0 * math.cos(a)), int(sy + r0 * math.sin(a))),
                             (int(sx + r1 * math.cos(a)), int(sy + r1 * math.sin(a))), INK, 10 if q % 3 == 0 else 6, cv2.LINE_AA)
        elif e["kind"] == "mark":                   # VOX: слово от руки + жёлтый маркер, проведённый под ним слева направо
            f = font(HAND, e.get("size", 120), 700)
            im = text_img(e["text"], f, INK)
            sp = e.get("speed", 1.0)                  # якорь хука пишется вдвое быстрее (speed 2): готов к 0.3 с
            u = (t - e["t"]) / (0.35 / sp)
            if u > 0:
                mw, mh = int(im.width * 1.02 * min(1.0, ease_out(u))), int(im.height * 0.42)
                if mw > 4:
                    mk = Image.new("RGBA", (int(im.width * 1.04), im.height), (0, 0, 0, 0)); dm = ImageDraw.Draw(mk)
                    y0 = int(im.height * 0.48)
                    pts = [(0, y0 + 6)] + [(x_, y0 + int(3 * math.sin(x_ * 0.05))) for x_ in range(0, mw, 12)] + \
                          [(mw, y0 + 4), (mw, y0 + mh), (0, y0 + mh - 4)]
                    dm.polygon(pts, fill=(255, 205, 50, 200))
                    if e.get("soft"): mk = mk.filter(ImageFilter.GaussianBlur(6))   # мягкий край маркера ~15 px (п.1.22)
                    over(base, mk.rotate(-2, resample=Image.BICUBIC, expand=False), e["x"], e["y"])
            msc = 0.7 + 0.3 * ease_out_back((t - e["t"]) / 0.4, s=4.0) if e.get("pop") else 1.0
            over(base, im, e["x"], e["y"], wipe=min(1.0, max(0.0, (t - e["t"] - 0.15 / sp) / (0.45 / sp))), scale=msc)
        elif e["kind"] == "circle":                 # VOX: красный круг рисуется от руки по контуру, открытый на конце
            u = ease_out((t - e["t"]) / 0.45)
            if view is not None:
                vx, vy, vh = view; k = PH / vh
                cx_, cy_ = (e["x"] - vx) * k + W / 2 + shake[0], (e["y"] - vy) * k + PH / 2 + shake[1]
                rx, ry = e["rx"] * k, e.get("ry", e["rx"]) * k
            else:
                cx_, cy_, rx, ry = e["x"], e["y"], e["rx"], e.get("ry", e["rx"])
            n = max(2, int(64 * u * 1.08))
            pts = [(int(cx_ + rx * (1 + 0.04 * math.sin(3 * a_)) * math.cos(a_ - 2.2)),
                    int(cy_ + ry * (1 + 0.04 * math.cos(2 * a_)) * math.sin(a_ - 2.2) - 6 * a_ / (2 * math.pi)))
                   for a_ in np.linspace(0, 2 * math.pi * 1.08 * u, n)]
            cv2.polylines(base, [np.array(pts, np.int32)], False, RED, 10, cv2.LINE_AA)
        elif e["kind"] == "badge":                  # плашка-подпись в кадре (бесплатно, ссылка)
            im = text_img(e["text"], font(FONT, e.get("size", 64)), WHITE if e.get("dark") else INK, stroke=0, pad=6)
            pad = Image.new("RGBA", (im.width + 40, im.height + 10), (0, 0, 0, 0))
            ImageDraw.Draw(pad).rounded_rectangle((0, 0, pad.width - 1, pad.height - 1), radius=pad.height // 2,
                                                  fill=(18, 18, 20, 235) if e.get("dark") else (255, 210, 63, 255))
            pad.alpha_composite(im, (20, 5))
            u = (t - e["t"]) / 0.22                     # въезд снизу с торможением, без «прыжка»
            over(base, pad, e["x"], e["y"] + 16 * (1 - ease_out(u)), alpha=min(1.0, u * 2.5))

    # картинка уходит в полосу субтитров мягким краем: одна бумага, без «вклеенного» прямоугольника; сверху — так же
    # мягко из полосы бумаги PIC_TOP (ночной рисунок не встаёт резким краем под шапкой)
    pic = base; base = tex.copy(); f_ = 60; T0 = PIC_TOP
    base[T0:T0 + PH] = pic[:PH]
    a_ = np.linspace(1, 0, f_, dtype=np.float32)[:, None, None]
    base[T0 + PH - f_:T0 + PH] = (pic[PH - f_:PH].astype(np.float32) * a_
                                  + tex[T0 + PH - f_:T0 + PH].astype(np.float32) * (1 - a_)).astype(np.uint8)
    if T0:
        ft = min(f_, T0 + 1)
        a_ = np.linspace(0, 1, ft, dtype=np.float32)[:, None, None]
        base[T0:T0 + ft] = (pic[:ft].astype(np.float32) * a_ + tex[T0:T0 + ft].astype(np.float32) * (1 - a_)).astype(np.uint8)
    base = grain(base, t)
    for e in arrows:
        if e.get("dash"):
            arrow(base, (e["p0"][0], e["p0"][1] + PIC_TOP), (e["p1"][0], e["p1"][1] + PIC_TOP), (t - e["t"]) / 0.25,
                  dash_t=t - e["t"], u_head=(t - e["t"] - 0.08) / 0.25)
        else:
            arrow(base, (e["p0"][0], e["p0"][1] + PIC_TOP), (e["p1"][0], e["p1"][1] + PIC_TOP), (t - e["t"]) / 0.25)

    # часы хука: время «летит» 23:55 -> 03:12, на последнем слове встаёт с ударом
    if hook_clock and t < hook_clock["t_end"]:
        t0c, t1c = hook_clock["t0"], hook_clock["t1"]
        u = min(1.0, max(0.0, (t - t0c) / (t1c - t0c)))
        m0, m1 = hook_clock["from_min"], hook_clock["to_min"]
        if m1 < m0: m1 += 24 * 60                                    # через полночь — время идёт вперёд
        mins = int(m0 + (m1 - m0) * (u ** 2.2)) % (24 * 60)
        txt = f"{mins // 60:02d}:{mins % 60:02d}"
        landed = t >= t1c
        sc = 1.0 + (0.18 * (1 - ease_out((t - t1c) / 0.25)) if landed else 0.0)
        im = clock_img(txt, KEY if landed else WHITE)
        if t < 0.25: sc *= 1 + 0.6 * (1 - ease_out(t / 0.25))   # влёт с ударом; при 2.4x первый кадр резал цифры
        sc = min(sc, (W - 40) / im.width)             # влёт с увеличением не режет цифры краями кадра
        over(base, im, W / 2, PIC_TOP + PH * 0.27, scale=sc)   # ниже верхних 14% — там шапка Reels

    # субтитры: группа въезжает снизу, активное слово — по времени слова
    for c in caps:
        if c["t0"] - 0.0 <= t < c["t1"]:
            act = c["idx"][0]
            for j in c["idx"]:
                if times[j]["start"] - 0.03 <= t: act = j
            im = c["imgs"][act]
            u = 1.0 if c.get("still") else (t - c["t0"]) / 0.25
            dy = CAP_RISE * (1 - ease_out(u))             # ровная строка: без подъёма (CAP_RISE 0), слова — по речи
            over(base, im, CAP_CX, CAP_CY + dy, alpha=1.0 if not CAP_RISE else min(1.0, 0.3 + 0.7 * u * 2.0))
    return base

def contact_sheet(reel_dir, shots):
    """Лист: первый и последний кадр каждого плана (без субтитров) — проверить кадрирование глазами."""
    tex = paper_tex(); tiles = []; total = shots[-1]["t1"]
    for s in shots:
        for t in (s["t0"] + 0.2, max(s["t0"] + 0.2, s["t1"] - 0.02)):
            fr = render_frame(reel_dir, t, [s], [], [], [], [], tex, None, total)
            tiles.append(cv2.resize(fr, (216, 384), interpolation=cv2.INTER_AREA))
    cols = 10; rows = (len(tiles) + cols - 1) // cols
    sheet = np.full((rows * 394, cols * 222, 3), 60, np.uint8)
    for i, tl in enumerate(tiles):
        r, c = divmod(i, cols); sheet[r * 394:r * 394 + 384, c * 222:c * 222 + 216] = tl
    p = os.path.join(reel_dir, "shots_sheet.jpg"); Image.fromarray(sheet).save(p, quality=85)
    print(p); return p

def place(track, x, t, gain=1.0):
    i = int(t * SR)
    if i < 0: x = x[-i:]; i = 0
    m = min(len(x), len(track) - i)
    if m > 0: track[i:i + m] += x[:m] * gain

SWOOSH_RATES = (1.0, 0.95, 1.05, 0.97, 1.03)
CUT_SOUND_NEAR = 0.35      # склейка «озвучена», если пик звука ближе 0.35 с
WHOOSHES, WHOOSH_GAP = reel_rules.WHOOSHES, reel_rules.WHOOSH_GAP   # свист от свиста не ближе 1.5 с (владелец 26.10)

def sound_plan(shots, events):
    """Все звуки рилса по порядку: [{name, t, align, gain_db, pan, peak, soft, whip}] — одна правда для микшера и для
    правил (reel_rules.check_sounds): хлёсткие склейки — swoosh пиком на склейку (J-cut), звуки планов, события фраз,
    тихий свист на наезд. Громкость по смыслу — `gain_db` у события или плана в reel.json (по умолчанию 0)."""
    plan, placed, count = [], [], {}
    def add(name, t, align="peak", gain_db=0.0, pan=0.0, soft=False, whip=False):
        k = count.get(name, 0); count[name] = k + 1
        rate = SWOOSH_RATES[k % 5] if name in ("swoosh", "swoosh_deep", "fast_whoosh") else 1.0
        pk = SFX[name][1] / rate
        peak = t if align == "peak" else t + pk
        placed.append(peak)
        plan.append(dict(name=name, t=t, align=align, gain_db=gain_db, pan=pan, rate=rate, peak=peak, soft=soft, whip=whip,
                         role=SFX_LIB[name]["role"]))
    for k, sh in enumerate(shots):
        if k and sh.get("whip") and sh.get("sound", "swoosh"):        # кадр едет справа — звук справа налево
            add(sh.get("sound", "swoosh"), sh["t0"], gain_db=sh.get("gain_db", 0.0), pan=0.3 if sh["whip"][0] < 0 else -0.3, whip=True)
        elif k and sh.get("sound"):
            add(sh["sound"], sh["t0"], gain_db=sh.get("gain_db", 0.0))
    for e in events:
        if e["kind"] == "sfx": add(e["name"], e["t"], e.get("align", "peak"), gain_db=e.get("gain_db", 0.0))
    # тихий свист на наезд и вход наездом (на 7 дБ тише хлёста), если рядом (1 с) уже не звучит другой звук
    soft = [sh["t0"] for k, sh in enumerate(shots) if k and sh.get("zoom_in") and not sh.get("sound")] + \
           [e["t"] for e in events if e["kind"] == "punch"]
    soft_done = []
    def whoosh_free(t):                               # свист не ближе WHOOSH_GAP к другому свисту (владелец 26.10)
        return all(abs(t - p["peak"]) >= WHOOSH_GAP for p in plan if p["name"] in WHOOSHES)
    for tt in sorted(soft):                           # и не чаще раза в 3 с: эталон v11 — три тихих свиста через 1.5 с
        if all(abs(tt - p) > 1.0 for p in placed) and all(abs(tt - q) > 3.0 for q in soft_done) and whoosh_free(tt):
            add("swoosh", tt, gain_db=SOFT_DB["zoom"], soft=True); soft_done.append(tt)
    # звук перехода на каждой склейке (владелец 24.10: «на новой картинке свуш, там другой свуш» — склейка без звука
    # проваливается): новая картинка — свист, по очереди обычный и короткий, разной скорости; тот же рисунок ближе —
    # тихий короткий свист. Не ставится, если рядом (CUT_SOUND_NEAR) уже звучит смысловой звук.
    # Свисты не «тук-тук-тук» (владелец 26.10: «не супер часто свуши… не надо прям быстро»): между свистами не меньше
    # WHOOSH_GAP; сначала свист новой картинки, склейка того же рисунка ближе уступает, если рядом уже свистело.
    cuts = []
    for k, sh in enumerate(shots):
        prev = shots[k - 1] if k else None
        new_pic = prev is None or (sh.get("src") or sh.get("kind")) != (prev.get("src") or prev.get("kind"))
        cuts.append((not new_pic, sh["t0"]))
    alt = 0
    for same, t in sorted(cuts):
        if any(abs(t - p) <= CUT_SOUND_NEAR for p in placed) or not whoosh_free(t):
            continue
        if not same:
            name = ("swoosh", "fast_whoosh")[alt % 2]; alt += 1
            add(name, t, gain_db=SOFT_DB["new_picture"], soft=True, whip=True)
        else:
            add("fast_whoosh", t, gain_db=SOFT_DB["same_picture"], soft=True)
    plan.sort(key=lambda p: p["peak"])
    return plan

def voice_segments(reel_dir, nat, times):
    """Куски дорожки голоса и куда их ставить: слова с одинаковым сдвигом (раскладка фраз: пик riser, немые паузы,
    перебивка) идут одним куском; граница куска — середина тишины между словами в исходной дорожке."""
    path = os.path.join(reel_dir, "voice", "voice.wav")
    segs, a = [], 0
    for k in range(1, len(nat) + 1):
        d0 = times[a]["start"] - nat[a]["start"]
        if k < len(nat) and abs((times[k]["start"] - nat[k]["start"]) - d0) < 1e-6:
            continue
        s0 = 0.0 if a == 0 else (nat[a - 1]["end"] + nat[a]["start"]) / 2
        s1 = None if k == len(nat) else (nat[k - 1]["end"] + nat[k]["start"]) / 2
        segs.append(dict(src=path, s0=s0, s1=s1, dst=s0 + d0)); a = k
    return segs

def voice_p95(v):
    """p95 пиков голоса по окнам 50 мс там, где голос есть (окно громче −40 dBFS) — опора громкости звуков (ghost-editor)."""
    win = int(0.05 * SR); n = len(v) // win
    if n == 0: return VOICE_P95_NOMINAL
    pk = np.abs(v[:n * win]).reshape(n, win).max(1)
    pk = pk[pk > 10 ** (-40 / 20)]
    return float(20 * np.log10(np.percentile(pk, 95))) if len(pk) else VOICE_P95_NOMINAL

def sound_levels(plan, sfx_mono, vp, words=None):
    """Замер каждого звука на дорожке звуков (без голоса): пик против голоса и против цели роли. Ошибки — громче голоса и
    не слышно; предупреждения — далеко от цели (наложение) и мем-звук на слове (его место — пауза после слова)."""
    out, err, warn = [], [], []
    for p in plan:
        i0 = max(0, int(p["t0"] * SR)); dur = min(SFX_LIB[p["name"]]["duration_sec"] / p["rate"], 3.0) + 0.1
        seg = sfx_mono[i0:i0 + int(dur * SR)]
        mix_pk = float(20 * np.log10(max(float(np.abs(seg).max()) if len(seg) else 0.0, 1e-9)))
        own = p.get("own_db", mix_pk)                 # пик самого звука; mix_pk — вместе с наложенными соседями
        rel, rel_mix = own - vp, mix_pk - vp; tgt = ROLE_DB[p.get("level_role", p["role"])] + p["gain_db"]
        r = dict(name=p["name"], role=p.get("level_role", p["role"]), peak=round(p["peak"], 3), soft=p["soft"],
                 gain_db=p["gain_db"], vs_voice_db=round(rel, 1), with_overlap_db=round(rel_mix, 1), target_db=round(tgt, 1))
        where = f"«{p['name']}» на {p['peak']:.2f} с"
        if rel_mix > SFX_LOUDER_MAX:
            err.append(f"{where}: {rel_mix:+.1f} дБ к голосу вместе с соседями — громче голоса"); r["flag"] = "loud"
        elif rel < SFX_INAUDIBLE:
            err.append(f"{where}: {rel:+.1f} дБ к голосу — не слышно (порог {SFX_INAUDIBLE:.0f})"); r["flag"] = "inaudible"
        elif abs(rel - tgt) > SFX_OFF_TARGET:
            warn.append(f"{where}: {rel - tgt:+.1f} дБ от цели роли — что-то сбило уровень"); r["flag"] = "off_target"
        if p.get("level_role") == "impact" and p["role"] == "meme":
            warn.append(f"{where}: мем-звук на слове — громкость удара ({ROLE_DB['impact']:.0f}), а не мема "
                        f"({ROLE_DB['meme']:.0f}): мем громок, только когда стоит в паузе после слова (ghost-editor)")
        out.append(r)
    return out, err, warn

def on_word(t, words):
    return bool(words) and any(w["start"] <= t <= w["end"] for w in words)

def mix_audio(path, total, shots, events, spec, voiced=False, voice=None, words=None):
    """Звук рилса по sound_plan. Повтор одного звука — каждый чуть другой (разбор 23.10: Gaku Lange, Marketing
    Demons — одинаковый свист «15 раз» слышен): скорость/высота по кругу 1.00 / 0.95 / 1.05 / 0.97 / 1.03, это тот же
    звук владельца, не чужой; панорама — по направлению хлёста. Первое появление звука — как в файле.
    Громкость — по роли от голоса (ROLE_DB). Возвращает замер каждого звука (sound_levels)."""
    n = int((total + 0.2) * SR)
    vt = np.zeros((n, 2), np.float32)
    for seg in voice or ():                           # голос по кускам на свои места; края 10 мс без щелчков
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", seg["src"], "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                           capture_output=True, check=True)
        x = np.frombuffer(p.stdout, np.float32).reshape(-1, 2)
        x = x[int(seg["s0"] * SR):(int(seg["s1"] * SR) if seg["s1"] is not None else len(x))].copy()
        f = min(int(0.01 * SR), len(x) // 2)
        if f: x[:f] *= np.linspace(0, 1, f)[:, None]; x[-f:] *= np.linspace(1, 0, f)[:, None]
        i = int(seg["dst"] * SR)
        if i < 0: x = x[-i:]; i = 0
        m = min(len(x), n - i)
        if m > 0: vt[i:i + m] += x[:m]
    vp = voice_p95(np.abs(vt).max(1)) if voice else VOICE_P95_NOMINAL   # пик по громкому каналу — как нормирует sfx()
    st = np.zeros((n, 2), np.float32)
    plan = sound_plan(shots, events)
    for p in plan:
        if p["role"] == "meme" and on_word(p["peak"], words):
            p["level_role"] = "impact"                 # мем на слове заглушил бы слово — уровень удара
        lvl = SFX[p["name"]][2]                       # sfx() отдаёт пик на level_db — приводим к цели роли
        x = sfx(p["name"]) * (10 ** ((vp + ROLE_DB[p.get("level_role", p["role"])] + p["gain_db"] - lvl) / 20)); rate = p["rate"]
        if rate != 1.0:
            src_t = np.arange(int(len(x) / rate)) * rate
            x = np.stack([np.interp(src_t, np.arange(len(x)), x[:, ch]) for ch in (0, 1)], axis=1).astype(np.float32)
        if p["pan"]:
            pan = p["pan"]
            x = x * np.array([math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)], np.float32) * math.sqrt(2)
        pk = SFX[p["name"]][1] / rate
        t0 = p["t"] - (pk if p["align"] == "peak" else 0.0)
        p["t0"] = t0; p["own_db"] = float(20 * np.log10(max(float(np.abs(x).max()), 1e-9)))
        i = int(t0 * SR)
        if i < 0: x = x[-i:]; i = 0
        m = min(len(x), n - i)
        if m > 0: st[i:i + m] += x[:m]
    levels = sound_levels(plan, np.abs(st).max(1), vp, words)
    tr = vt + st
    peak = float(np.abs(tr).max())
    if peak > 0.89: tr *= 0.89 / peak                 # наложение двух звуков не клипует: пик не выше -1 dBFS
    pcm = (np.clip(tr, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    return dict(voice_p95=round(vp, 1), sounds=levels[0], errors=levels[1], warnings=levels[2])

def write_srt(path, caps, words):
    def ts(x):
        ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    with open(path, "w", encoding="utf8") as f:
        for k, c in enumerate(caps, 1):
            f.write(f"{k}\n{ts(c['t0'])} --> {ts(c['t1'])}\n{' '.join(clean(words[j]) for j in c['idx'])}\n\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("reel_dir")
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--preview", action="store_true", help="15 к/с — быстро посмотреть монтаж")
    ap.add_argument("--force", action="store_true", help="рендерить, даже если нарушены правила рилса")
    a = ap.parse_args()
    build(a.reel_dir, sheet=a.sheet, preview=a.preview, force=a.force)
