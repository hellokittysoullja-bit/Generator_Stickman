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

W, H, FPS = 1080, 1920, 30
PAPER = np.array([250, 247, 240], np.float32)          # #FAF7F0, как у длинных роликов (canvas.py)
FONT = os.path.join(ROOT, "assets", "fonts", "ShantellSans-ExtraBold.ttf")
HAND = os.path.join(ROOT, "assets", "fonts", "Caveat-Variable.ttf")
CAP_Y = 0.665          # центр субтитра: над нижними 20% (кнопки и подпись Reels), в средних 60% экрана
CAP_SIZE = 100         # px на ширине 1080: ~8.5% ширины, читается с телефона на вытянутой руке
CAP_MAX_W = 0.80       # правые 12% — колонка кнопок Reels
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
def chunks(words, times):
    """Группы по 1-3 слова: обрыв на знаке препинания, на «|», на ключевом слове (оно идёт одно или
    со служебным словом перед ним), не длиннее ~16 знаков — одна строка крупного кегля."""
    out, cur = [], []
    def flush():
        if cur: out.append(list(cur)); cur.clear()
    for i, w in enumerate(words):
        raw = w
        if raw.startswith("|"): flush()
        key = "*" in raw
        if key and len(cur) >= 2 and "*" not in words[cur[-1]]: flush()
        cur.append(i)
        text = " ".join(clean(words[j]) for j in cur)
        end_punct = re.search(r"[.,:?!…—]»?\*?$", clean(raw) + ("*" if raw.endswith("*") else ""))
        nxt_key = i + 1 < len(words) and "*" in words[i + 1] and not end_punct
        if len(cur) >= 3 or len(text) >= 14 or end_punct or (key and len(cur) >= 2 and not nxt_key):
            flush()
    flush()
    res = []
    for k, c in enumerate(out):
        t0 = max(0.0, times[c[0]]["start"] - CUT_LEAD)      # вместе со склейкой: группа не «переезжает» на чужой план
        t1 = times[out[k + 1][0]]["start"] - CUT_LEAD if k + 1 < len(out) else times[c[-1]]["end"] + 0.6
        res.append(dict(idx=c, t0=t0, t1=t1))
    return res

_FONTS = {}
def font(path, size, wght=None):
    k = (path, size, wght)
    if k not in _FONTS:
        f = ImageFont.truetype(path, size)
        if wght:
            try: f.set_variation_by_axes([wght])
            except Exception: pass                                      # шрифт без осей — как есть
        _FONTS[k] = f
    return _FONTS[k]

def render_chunk(words, idx, active, size=CAP_SIZE):
    """RGBA одной группы: белые буквы с толстой тёмной обводкой и мягкой тенью (читается на любом
    рисунке), активное слово — жёлтым, ключевое — оранжевым и на 18% крупнее. Перенос на 2 строки,
    если шире CAP_MAX_W."""
    parts = []
    for j in idx:
        w = words[j]; key = "*" in w
        s = int(size * (1.18 if key else 1.0))
        col = KEY if key else (ACTIVE if j == active else WHITE)
        parts.append((clean(w).upper() if key else clean(w), font(FONT, s), col, j == active))
    stroke = int(size * 0.11)
    space = int(size * 0.28)
    widths = [p[1].getbbox(p[0], stroke_width=stroke)[2] - p[1].getbbox(p[0], stroke_width=stroke)[0] for p in parts]
    lines, cur, cw = [], [], 0
    for p, w in zip(parts, widths):
        if cur and cw + space + w > W * CAP_MAX_W: lines.append(cur); cur, cw = [], 0
        cur.append((p, w)); cw += (space if len(cur) > 1 else 0) + w
    lines.append(cur)
    lh = int(size * 1.22)
    bw = int(max(sum(w for _, w in L) + space * (len(L) - 1) for L in lines)) + 2 * stroke + 40
    bh = lh * len(lines) + 2 * stroke + 60
    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    sh = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(sh)
    y = 30 + stroke
    for L in lines:
        lw = sum(w for _, w in L) + space * (len(L) - 1)
        x = (bw - lw) / 2
        for (txt, f, col, _act), w in L:
            asc = f.getbbox(txt, stroke_width=stroke)
            yy = y + (lh - (asc[3] - asc[1])) / 2 - asc[1] - lh * 0.05
            ds.text((x - asc[0], yy + size * 0.07), txt, font=f, fill=(0, 0, 0, 120), stroke_width=stroke, stroke_fill=(0, 0, 0, 120))
            d.text((x - asc[0], yy), txt, font=f, fill=col, stroke_width=stroke, stroke_fill=INK)
            x += w + space
        y += lh
    sh = sh.filter(ImageFilter.GaussianBlur(size * 0.09))
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
    if name not in _SRC:
        p = os.path.join(reel_dir, "src", name + ".png")
        _SRC[name] = np.asarray(Image.open(p).convert("RGB"))
    return _SRC[name]

def paper_tex(seed=5):
    """Фактура бумаги ±2.5%: тот же крем, что у длинных роликов, но не мёртвая заливка."""
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    n = cv2.resize(cv2.GaussianBlur(n, (0, 0), 1.2), (W, H), interpolation=cv2.INTER_CUBIC)
    n = n / (np.abs(n).max() + 1e-6)
    return np.clip(PAPER[None, None] * (1 + 0.025 * n[..., None]), 0, 255).astype(np.uint8)

def crop_box(cx, cy, h, aspect=W / H):
    return cx - h * aspect / 2, cy - h / 2, h

def sample(src, cx, cy, h, scale_src=2.0, shake=(0, 0), rot=0.0):
    """Окно (cx, cy, высота h) в координатах ИСХОДНОГО кадра -> 1080x1920. Края за картинкой — бумага."""
    s = h * scale_src / H
    a = math.radians(rot)
    ca, sa = math.cos(a) * s, math.sin(a) * s
    X0, Y0 = cx * scale_src, cy * scale_src
    M = np.array([[ca, -sa, X0 - ca * (W / 2 + shake[0]) + sa * (H / 2 + shake[1])],
                  [sa, ca, Y0 - sa * (W / 2 + shake[0]) - ca * (H / 2 + shake[1])]], np.float32)
    return cv2.warpAffine(src, M, (W, H), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=tuple(int(v) for v in PAPER))

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
    X0, Y0 = max(0, px), max(0, py); X1, Y1 = min(W, px + w_), min(H, py + h_)
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


# ----------------------------------------------------------------------------- кукла героя
_DOLL = {}
def doll_frame(t, dur, actions):
    """Живой кот (риг из experiments/alive_cat/doll): RGBA премультиплицированный, координаты рига."""
    if "rig" not in _DOLL:
        sys.path.insert(0, os.path.join(ROOT, "experiments", "alive_cat", "doll"))
        import doll_rig
        _DOLL["mod"] = doll_rig
        _DOLL["rig"] = doll_rig.Rig(os.path.join(ROOT, "experiments", "alive_cat", "doll", "rig.json"))
    key = (dur, json.dumps(actions))
    if _DOLL.get("key") != key:
        _DOLL["st"] = _DOLL["mod"].plan(dur, actions, seed=11); _DOLL["key"] = key
    st = _DOLL["st"](t)
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
    sh = np.zeros((H, W), np.float32)
    cv2.ellipse(sh, (int(cx - rw * 0.02), int(py + rh * 0.985)), (int(rw * 0.30), int(rh * 0.035)), 0, 0, 360, 1.0, -1)
    sh = cv2.GaussianBlur(sh, (0, 0), 14) * 0.22
    b = base.astype(np.float32) * (1 - sh[..., None])
    X0, Y0 = max(0, px), max(0, py); X1, Y1 = min(W, px + rw), min(H, py + rh)
    sub = reg[Y0 - py:Y1 - py, X0 - px:X1 - px]
    a = np.clip(sub[..., 3:4], 0, 1)
    b[Y0:Y1, X0:X1] = np.clip(sub[..., :3], 0, 255) + b[Y0:Y1, X0:X1] * (1 - a)
    return np.clip(b, 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------- накладки
def text_img(txt, f, fill, stroke=0, stroke_fill=None, pad=20):
    bb = f.getbbox(txt, stroke_width=stroke)
    im = Image.new("RGBA", (bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - bb[0], pad - bb[1]), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

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
    X0, Y0 = max(0, px), max(0, py); X1, Y1 = min(W, px + a.shape[1]), min(H, py + a.shape[0])
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

def arrow(base, p0, p1, u, color=RED, th=12):
    """Рисованная стрелка, растёт по u (0..1)."""
    u = ease_out(u)
    if u <= 0: return base
    x = p0[0] + (p1[0] - p0[0]) * u; y = p0[1] + (p1[1] - p0[1]) * u
    cv2.line(base, (int(p0[0]), int(p0[1])), (int(x), int(y)), color, th, cv2.LINE_AA)
    if u > 0.85:
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        for s in (-1, 1):
            a2 = ang + math.pi + s * 0.5
            cv2.line(base, (int(x), int(y)), (int(x + 48 * math.cos(a2)), int(y + 48 * math.sin(a2))), color, th, cv2.LINE_AA)
    return base


# ----------------------------------------------------------------------------- звук
SR = 48000

def _env(n, a, r):
    e = np.ones(n, np.float32)
    na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e

def sfx_whoosh(dur=0.32, seed=1):
    from scipy.signal import butter, sosfilt
    rng = np.random.default_rng(seed); n = int(dur * SR)
    x = rng.normal(0, 1, n).astype(np.float32); out = np.zeros(n, np.float32)
    blk = 512
    for i in range(0, n, blk):
        u = i / n; fc = 400 + 3200 * math.sin(math.pi * u) ** 1.5
        sos = butter(2, [fc * 0.6, fc * 1.4], btype="band", fs=SR, output="sos")
        out[i:i + blk] = sosfilt(sos, x[max(0, i - 2048):i + blk])[-len(out[i:i + blk]):]
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return (out * e / (np.abs(out).max() + 1e-6) * 0.55).astype(np.float32)

def sfx_pop(f0=760, f1=320, dur=0.07):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 60)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 55) * 0.42).astype(np.float32)

def sfx_tick(f=2300, dur=0.04, amp=0.28, seed=2):
    n = int(dur * SR); t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 180) + rng.normal(0, 1, n) * np.exp(-t * 700) * 0.4
    return (x * amp).astype(np.float32)

def sfx_ring(dur=1.1):
    n = int(dur * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((2350, 1.0), (3140, .5), (4710, .3), (1180, .25)))
    trem = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 17 * t))          # молоточек будильника
    return (x * trem * _env(n, 0.005, 0.25) * 0.16).astype(np.float32)

def sfx_boom(dur=0.6):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 42 + 70 * np.exp(-t * 14)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    return (np.tanh(x * 1.6) * 0.55).astype(np.float32)

def sfx_riser(dur):
    """Нарастание под гонку часов: шум с поднимающейся полосой и громкостью, обрывается в удар."""
    from scipy.signal import butter, sosfilt
    rng = np.random.default_rng(9); n = int(dur * SR)
    x = rng.normal(0, 1, n).astype(np.float32); out = np.zeros(n, np.float32); blk = 1024
    for i in range(0, n, blk):
        u = i / n; fc = 500 + 4500 * u ** 1.6
        sos = butter(2, [fc * 0.7, fc * 1.3], btype="band", fs=SR, output="sos")
        out[i:i + blk] = sosfilt(sos, x[max(0, i - 4096):i + blk])[-len(out[i:i + blk]):]
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * np.cumsum(220 + 660 * (t / dur) ** 2) / SR) * 0.25
    return ((out / (np.abs(out).max() + 1e-6) * 0.6 + tone) * (t / dur) ** 2 * 0.5).astype(np.float32)

def sfx_chime():
    n = int(1.8 * SR); t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    for k, f in enumerate((1046.5, 1568.0)):                     # до и соль второй октавы
        d = int(k * 0.11 * SR); tt = t[: n - d]
        v = sum(np.sin(2 * np.pi * f * m * tt) * a for m, a in ((1, 1), (2.76, .3), (5.4, .12))) * np.exp(-tt * 3.2)
        out[d:] += v
    return (out * 0.18).astype(np.float32)

def sfx_scribble(dur=0.5, seed=4):
    from scipy.signal import butter, sosfilt
    rng = np.random.default_rng(seed); n = int(dur * SR)
    x = rng.normal(0, 1, n).astype(np.float32)
    x = sosfilt(butter(2, [1800, 6500], btype="band", fs=SR, output="sos"), x)
    strokes = 0.35 + 0.65 * np.abs(np.sin(2 * np.pi * 7.5 * np.arange(n) / SR + rng.uniform(0, 3)))
    return (x / (np.abs(x).max() + 1e-6) * strokes * _env(n, .02, .08) * 0.20).astype(np.float32)

def music_bed(total, bpm=96):
    """Подложка-заглушка до выбора трека (в Reels трек кладут из библиотеки приложения — трендовый звук
    даёт охват): тёплые аккорды Am-F-C-G мягкими синусами и тихий тик часов на каждую долю — тема ролика."""
    n = int(total * SR)
    out = np.zeros(n, np.float32)
    beat = 60 / bpm; bar = beat * 4
    chords = [(220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (130.8, 164.8, 196.0), (196.0, 246.9, 293.7)]
    for k in range(int(total / bar) + 1):
        a = int(k * bar * SR); b = min(n, int((k + 1) * bar * SR) + int(0.4 * SR))
        if a >= n: break
        tt = np.arange(b - a) / SR
        env = (1 - np.exp(-tt * 6)) * np.exp(-tt * 0.35)
        for f in chords[k % 4]:
            out[a:b] += (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)) * env * 0.035
        bass = chords[k % 4][0] / 2
        for q in range(4):
            qa = a + int(q * beat * SR)
            if qa >= n: break
            m = min(n - qa, int(0.35 * SR)); tq = np.arange(m) / SR
            out[qa:qa + m] += np.sin(2 * np.pi * bass * tq) * np.exp(-tq * 7) * 0.09
    tick = sfx_tick(amp=0.05)
    k = 0
    while k * beat < total:
        i = int(k * beat * SR); m = min(len(tick), n - i)
        out[i:i + m] += tick[:m] * (1.0 if k % 2 == 0 else 0.6)
        k += 1
    return out


# ----------------------------------------------------------------------------- сборка
def build(reel_dir, sheet=False, preview=False):
    spec = json.load(open(os.path.join(reel_dir, "reel.json"), encoding="utf8"))
    beats = spec["beats"]
    prepare_src(reel_dir, spec.get("sources", {}))
    words, spans = tokens(beats)
    al = os.path.join(reel_dir, "alignment.json")
    if os.path.exists(al):
        times = json.load(open(al, encoding="utf8")); voiced = True
        assert len(times) == len(words), f"alignment: {len(times)} слов, в сценарии {len(words)}"
    else:
        times = estimate_times([clean(w) for w in words], rate=spec.get("rate", 1.0)); voiced = False
        for b, (i0, _i1) in zip(beats, spans):        # немая пауза после слова (стоп-кадр с тишиной, Runia)
            for k, sec in b.get("gaps", []):
                times = times[:i0 + k + 1] + [dict(w, start=w["start"] + sec, end=w["end"] + sec) for w in times[i0 + k + 1:]]
    lead = spec.get("lead_in", 0.0)                  # перебивка до первого слова: сначала остановить, потом смысл (vidIQ)
    if lead:
        times = [dict(w, start=w["start"] + lead, end=w["end"] + lead) for w in times]
    total = times[-1]["end"] + spec.get("tail", 0.5)

    # кадрирования: у фразы shots=[{at: номер слова во фразе, ...}]; начало плана = начало слова - CUT_LEAD
    shots = []
    for b, (i0, _i1) in zip(beats, spans):
        for s in b["shots"]:
            k = i0 + s.get("at", 0)
            shots.append(dict(s, t0=max(0.0, times[k]["start"] - (CUT_LEAD if k else 0)), beat=b))
    shots.sort(key=lambda s: s["t0"])
    shots[0]["t0"] = 0.0                              # перебивка до первого слова идёт на первом плане, а не в пустоту
    # кукла живёт по общему времени ролика: смена плана с куклой не перезапускает моргание и лицо
    doll_acts = [dict(a, t=a["t"] + s["t0"]) for s in shots if s.get("kind") == "doll" for a in s.get("actions", [])]
    for s in shots:
        if s.get("kind") == "doll": s["doll_acts"] = doll_acts
    for a, b in zip(shots, shots[1:]): a["t1"] = b["t0"]
    shots[-1]["t1"] = total
    # события внутри фраз: наезд, тряска, стрелка, надпись — привязаны к слову
    def wt(b_idx, k):
        return times[spans[b_idx][0] + k]["start"]
    events = []
    for bi, b in enumerate(beats):
        for e in b.get("fx", []):
            events.append(dict(e, t=wt(bi, e.get("at", 0)) + e.get("dt", 0.0), beat=bi))
    for e in events:                                  # окна музыки: тишина после слова, приглушение на фразе
        if e["kind"] == "silence_after":
            k = spans[e["beat"]][0] + e.get("at", 0)
            e["t"], e["t1"] = times[k]["end"], times[k + 1]["start"] + 0.05
        if e["kind"] == "duck":
            e["t1"] = times[spans[e["beat"]][1] - 1]["end"]
    for e in events:                                  # удержание накладки — только пока идут планы того же рода
        e["kind_of_shot"] = next((x.get("kind", "crop") for x in reversed(shots) if x["t0"] <= e["t"] + CUT_LEAD), "crop")
    caps = chunks(words, times)
    for c in caps:
        c["imgs"] = {j: render_chunk(words, c["idx"], j) for j in c["idx"]}

    if sheet:
        return contact_sheet(reel_dir, shots)

    tex = paper_tex()
    hook_clock = spec.get("clock")
    if hook_clock:                                   # часы хука привязаны к словам: [фраза, слово]
        spec["clock"] = hook_clock = dict(hook_clock, t0=wt(*hook_clock["from_word"]), t1=wt(*hook_clock["to_word"]))
    vid = os.path.join(reel_dir, "reel_preview.mp4" if preview else "reel_video.mp4")
    fps = 15 if preview else FPS
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                           "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    n = int(total * fps)
    for fi in range(n):
        t = fi / fps
        frame = render_frame(reel_dir, t, shots, events, caps, words, times, tex, hook_clock, total)
        ff.stdin.write(frame.tobytes())
        if fi % 60 == 0: print(f"  кадр {fi}/{n}", flush=True)
    ff.stdin.close(); ff.wait()

    wav = os.path.join(reel_dir, "reel_audio.wav")
    mix_audio(wav, total, shots, events, caps, spec, voiced)
    out = os.path.join(reel_dir, "reel_preview_av.mp4" if preview else "reel.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    json.dump(dict(total=total, voiced=voiced, words=times,
                   shots=[dict(t0=round(s["t0"], 3), t1=round(s["t1"], 3), kind=s.get("kind", "crop"), src=s.get("src")) for s in shots],
                   captions=[dict(t0=round(c["t0"], 3), t1=round(c["t1"], 3),
                                  text=" ".join(clean(words[j]) for j in c["idx"])) for c in caps]),
              open(os.path.join(reel_dir, "reel_report.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    write_srt(os.path.join(reel_dir, "reel.srt"), caps, words)
    print(f"Готово. Файл: {out} ({total:.1f} с, планов {len(shots)}, групп субтитров {len(caps)})")
    return out

def lerp(a, b, u):
    return a + (b - a) * u

def shot_view(s, t):
    """Окно камеры плана в момент t: постоянная скорость от from к to, плюс наезды плана (punch)."""
    d = max(1e-3, s["t1"] - s["t0"]); u = (t - s["t0"]) / d
    if s.get("ease") == "out": u = ease_out(u)
    elif s.get("ease") == "io": u = ease_io(u)
    f, to = s["from"], s.get("to", s["from"])
    cx, cy, h = (lerp(f[i], to[i], u) for i in range(3))
    # хлёст в начале плана: окно прилетает из сдвига (whip), 0.18 с с торможением
    if s.get("whip"):
        k = 1 - ease_out((t - s["t0"]) / 0.18)
        dx, dy = s["whip"]
        cx += dx * k; cy += dy * k
    # быстрый наезд/отъезд в начале плана (zoom-in transition)
    if s.get("zoom_in"):
        k = 1 - ease_out((t - s["t0"]) / 0.22)
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

def render_frame(reel_dir, t, shots, events, caps, words, times, tex, hook_clock, total):
    s = next(x for x in shots if x["t0"] <= t < x["t1"] or x is shots[-1])
    kind = s.get("kind", "crop")
    shake = (0.0, 0.0); punch = 1.0; rot = 0.0
    for e in events:
        if e["kind"] == "punch" and s["t0"] <= e["t"] <= t < s["t1"]:
            punch *= 1 + e.get("amt", 0.14) * ease_out((t - e["t"]) / 0.12)     # наезд держится до конца плана
        if e["kind"] == "shake" and 0 <= t - e["t"] < e.get("dur", 0.45):
            k = 1 - (t - e["t"]) / e.get("dur", 0.45); A = e.get("amp", 22) * k
            shake = (A * math.sin(t * 93), A * 0.7 * math.cos(t * 71)); rot = 0.6 * k * math.sin(t * 57)
    if kind == "crop":
        src = load_src(reel_dir, s["src"])
        cx, cy, h = shot_view(s, t)
        base = sample(src, cx, cy, h / punch, shake=shake, rot=rot)
        view = (cx, cy, h / punch)
        if s.get("whip"):
            k = 1 - ease_out((t - s["t0"]) / 0.18)
            if k > 0.05:
                sc = H / (h / punch) / 2.0
                base = motion_blur(base, s["whip"][0] * k * sc * 0.25 * 2.0 * 0.5, s["whip"][1] * k * sc * 0.25)
    else:
        view = None
        base = tex.copy()
        d = max(1e-3, s["t1"] - s["t0"]); u = (t - s["t0"]) / d
        zs = lerp(s.get("zoom", (1.0, 1.06))[0], s.get("zoom", (1.0, 1.06))[1], u) * punch
        if kind == "fit":
            src = load_src(reel_dir, s["src"])
            base = fit_on_paper(base, src, s["region"], s.get("cy", H * 0.42) + shake[1], s.get("width", 0.96), zs, dx=shake[0])
        elif kind == "stack":
            for part in s["parts"]:
                src = load_src(reel_dir, part["src"])
                base = fit_on_paper(base, src, part["region"], part["cy"], part.get("width", 0.94), zs)
        elif kind == "doll":
            rgba = doll_frame(t, total + 0.5, s["doll_acts"])
            base = paste_doll(base, rgba, W / 2 + shake[0], s.get("cy", H * 0.43) + shake[1], s.get("h", 900) * zs)
    base = np.ascontiguousarray(base)

    # накладки фраз
    for e in events:
        held = e.get("hold") and e["t"] <= t < e["t"] + e["hold"] and kind == e.get("kind_of_shot", kind)
        if not (s["t0"] - 0.01 <= e["t"] <= t < s["t1"] + 0.01 or held):
            continue
        if e["kind"] == "write":                    # рукописная надпись на рисунке, пишется ~0.5 с
            im = text_img(e["text"], font(HAND, e.get("size", 120), 700), RED if e.get("red", True) else INK)
            u = (t - e["t"]) / e.get("dur", 0.5)
            over(base, im, e["x"], e["y"], wipe=min(1.0, u * 1.05), scale=1.0)
        elif e["kind"] == "arrow":
            arrow(base, e["p0"], e["p1"], (t - e["t"]) / 0.25)
        elif e["kind"] == "ring" and t - e["t"] < e.get("dur", 1.0) and view is not None:
            vx, vy, vh = view; k = H / vh
            ring_lines(base, (e["x"] - vx) * k + W / 2 + shake[0], (e["y"] - vy) * k + H / 2 + shake[1], e["r"] * k, t)
        elif e["kind"] == "hands" and view is not None:   # стрелки на пустом циферблате: «время снова видно»
            vx, vy, vh = view; k = H / vh
            sx, sy = (e["x"] - vx) * k + W / 2, (e["y"] - vy) * k + H / 2; r = e["r"] * k
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
        elif e["kind"] == "badge":                  # плашка-подпись в кадре (бесплатно, ссылка)
            im = text_img(e["text"], font(FONT, e.get("size", 64)), WHITE if e.get("dark") else INK, stroke=0)
            pad = Image.new("RGBA", (im.width + 40, im.height + 10), (0, 0, 0, 0))
            ImageDraw.Draw(pad).rounded_rectangle((0, 0, pad.width - 1, pad.height - 1), radius=pad.height // 2,
                                                  fill=(18, 18, 20, 235) if e.get("dark") else (255, 210, 63, 255))
            pad.alpha_composite(im, (20, 5))
            sc = ease_out_back((t - e["t"]) / 0.22)
            over(base, pad, e["x"], e["y"], scale=max(0.01, sc))

    # часы хука: время «летит» 23:55 -> 03:12, на последнем слове встаёт с ударом
    if hook_clock and t < hook_clock["t1"] + 0.9:
        t0c, t1c = hook_clock["t0"], hook_clock["t1"]
        u = min(1.0, max(0.0, (t - t0c) / (t1c - t0c)))
        m0, m1 = hook_clock["from_min"], hook_clock["to_min"]
        if m1 < m0: m1 += 24 * 60                                    # через полночь — время идёт вперёд
        mins = int(m0 + (m1 - m0) * (u ** 2.2)) % (24 * 60)
        txt = f"{mins // 60:02d}:{mins % 60:02d}"
        landed = t >= t1c
        sc = 1.0 + (0.18 * (1 - ease_out((t - t1c) / 0.25)) if landed else 0.0)
        im = text_img(txt, font(FONT, 190), KEY if landed else WHITE, stroke=16, stroke_fill=INK)
        if t < 0.25: sc *= 1 + 1.4 * (1 - ease_out(t / 0.25))          # влетает в кадр с ударом — перебивка ленты
        over(base, im, W / 2, H * 0.17, scale=sc)

    # субтитры: группа выскакивает (0.85 -> 1.06 -> 1.0 за 160 мс), активное слово — по времени слова
    for c in caps:
        if c["t0"] - 0.0 <= t < c["t1"]:
            act = c["idx"][0]
            for j in c["idx"]:
                if times[j]["start"] - 0.03 <= t: act = j
            im = c["imgs"][act]
            u = (t - c["t0"]) / 0.20
            sc = 0.70 + 0.30 * ease_out_back(u, 3.2)                       # 70% -> ~110% -> 100% за 200 мс
            over(base, im, W / 2 - W * 0.03, H * CAP_Y, alpha=min(1.0, u * 3.0), scale=sc)
    if t > total - 0.35:                            # последние кадры — без затемнения: петля в начало
        pass
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

def mix_audio(path, total, shots, events, caps, spec, voiced):
    n = int((total + 0.2) * SR); tr = np.zeros(n, np.float32)
    if spec.get("music", True):
        mus = music_bed(total + 0.2)
        env = np.ones(n, np.float32)
        for e in events:                            # тишина — контраст громкое/тихое; приглушение — «тихий момент»
            if e["kind"] in ("silence_after", "duck"):
                a, b = int(e["t"] * SR), int(e["t1"] * SR); r = int(0.06 * SR)
                g = 0.0 if e["kind"] == "silence_after" else e.get("gain", 0.35)
                env[a:b] = np.minimum(env[a:b], g)
                env[max(0, a - r):a] = np.minimum(env[max(0, a - r):a], np.linspace(1, g, len(env[max(0, a - r):a])))
                env[b:b + r] = np.minimum(env[b:b + r], np.linspace(g, 1, len(env[b:b + r])))
        tr += mus[:n] * env
    # J-cut звука: свист перехода начинается за 0.12 с до склейки и пиком попадает на неё
    for k, s in enumerate(shots):
        if k == 0: continue
        if s.get("whip") or s.get("zoom_in"):
            place(tr, sfx_whoosh(0.32, seed=k), s["t0"] - 0.16, 0.9)
    for e in events:
        if e["kind"] == "punch": place(tr, sfx_pop(f0=600, f1=240), e["t"], 0.7)
        if e["kind"] == "shake": place(tr, sfx_boom(), e["t"], 0.9)
        if e["kind"] == "ring": place(tr, sfx_ring(e.get("dur", 1.0) + 0.3), e["t"], 1.0)   # L-cut: звон тянется через склейку
        if e["kind"] == "write": place(tr, sfx_scribble(e.get("dur", 0.5)), e["t"], 1.0)
        if e["kind"] == "chime": place(tr, sfx_chime(), e["t"], 1.0)
        if e["kind"] == "badge": place(tr, sfx_pop(1200, 700, 0.05), e["t"], 0.6)
        if e["kind"] == "ticks":
            k = 0
            while k * e.get("every", 0.25) < e.get("dur", 2.0):
                place(tr, sfx_tick(2300 if k % 2 == 0 else 1700), e["t"] + k * e.get("every", 0.25), e.get("gain", 1.0)); k += 1
    clk = spec.get("clock")
    if clk:                                         # удар на влёте часов в 0 с, нарастание до остановки на 03:12
        place(tr, sfx_boom(0.5), 0.0, 0.8)
        place(tr, sfx_riser(max(0.3, clk["t1"] - 0.15)), 0.15, 0.7)
    if not voiced:                                  # немой рилс: тихий щелчок на каждую новую группу субтитров
        for c in caps: place(tr, sfx_pop(1500, 900, 0.025), c["t0"], 0.18)
    tr *= 0.89 / max(1e-6, float(np.abs(tr).max()))           # пик -1 dBFS; громкость по LUFS — у мастера ниже
    pcm = (np.clip(tr, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    tmp = path.replace(".wav", "_ln.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), tmp], check=True)
    os.replace(tmp, path)

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
    a = ap.parse_args()
    build(a.reel_dir, sheet=a.sheet, preview=a.preview)
