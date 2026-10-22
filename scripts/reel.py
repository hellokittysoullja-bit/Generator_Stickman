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
FONT = os.path.join(ROOT, "assets", "fonts", "ShantellSans-ExtraBold.ttf")     # надписи в кадре (плашки, часы)
HAND = os.path.join(ROOT, "assets", "fonts", "Caveat-Variable.ttf")
# Субтитры (разбор 11 роликов о субтитрах, 22.10): Inter Display ExtraBold — бесплатная замена Helvetica/SF Pro,
# самый частый шрифт субтитров в разборах, полная кириллица; регистр как в предложении (капслок кириллицы —
# широкие кирпичи Ш/Щ/Ж/Ы, капс оставляют для 1-3 акцентов); один кегль и одна базовая линия на весь ролик.
CAP_FONT = os.path.join(ROOT, "assets", "fonts", "reels", "Inter[opsz,wght].ttf")
CAP_AXES = {"Weight": 800, "Optical size": 32}
CAP_UPPER = False
CAP_TRACK = 0.0       # без трекинга: при обводке -2% сливал буквы (замер на превью 22.10)
PH = 1100              # картинка — верхние 1100 px; ниже — полоса субтитров на той же бумаге (субтитр не ложится на рисунок)
CAP_CX, CAP_CY = 500, 1175   # центр полосы субтитров 1100-1250: ниже 1250 (нижние 35%) Reels закрывает подписью и кнопками (Meta 9:16)
CAP_SIZE = 90          # один кегль на весь ролик: группы не прыгают по размеру
CAP_MAX_W = 820        # px: от 90 до 910 — правее колонка кнопок Reels
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
def cap_text(w):
    return clean(w).upper() if CAP_UPPER else clean(w)

def cap_font():
    return font(CAP_FONT, CAP_SIZE, CAP_AXES)

def tracked(f, t):
    """Ширина строки с трекингом: PIL трекинга не знает, буквы ставятся по одной."""
    return sum(f.getlength(ch) for ch in t) + CAP_TRACK * CAP_SIZE * max(0, len(t) - 1)

def cap_width(idx, words):
    f = cap_font()
    return tracked(f, " ".join(cap_text(words[j]) for j in idx)) + 2 * CAP_STROKE

def chunks(words, times):
    """Группы по 1-3 слова, всегда ОДНОЙ строкой одного кегля: обрыв на знаке препинания, на «|», перед
    словом, которое не влезает в CAP_MAX_W (группа не переносится и не уменьшается — делится)."""
    out, cur = [], []
    def flush():
        if cur: out.append(list(cur)); cur.clear()
    for i, w in enumerate(words):
        if w.startswith("|"): flush()
        if cur and cap_width(cur + [i], words) > CAP_MAX_W: flush()
        cur.append(i)
        end_punct = re.search(r"[.,:?!…—]»?\*?$", clean(w) + ("*" if w.endswith("*") else ""))
        if len(cur) >= 3 or end_punct:
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
    k = (path, size, json.dumps(wght, sort_keys=True))
    if k not in _FONTS:
        f = ImageFont.truetype(path, size)
        if wght:
            axes = wght if isinstance(wght, dict) else {"Weight": wght}
            try:
                f.set_variation_by_axes([axes.get(a["name"].decode() if isinstance(a["name"], bytes) else a["name"], a["default"])
                                         for a in f.get_variation_axes()])
            except Exception: pass                                      # шрифт без осей — как есть
        _FONTS[k] = f
    return _FONTS[k]

def render_chunk(words, idx, active):
    """RGBA одной группы: одна строка, один кегль, базовая линия на одной высоте у всех групп (высота картинки
    от метрик шрифта, а не от букв: «у/д/щ» не сдвигают группу). Белые буквы, тонкая тёмная обводка, мягкая
    тень; активное слово — жёлтым (караоке), ключевое — оранжевым. Цвет — единственное отличие слов."""
    f = cap_font(); st = CAP_STROKE; space = f.getlength(" ") + CAP_TRACK * CAP_SIZE
    parts = [(cap_text(words[j]), KEY if "*" in words[j] else (ACTIVE if j == active else WHITE)) for j in idx]
    tw = sum(tracked(f, t) for t, _ in parts) + space * (len(parts) - 1)
    asc, desc = f.getmetrics()
    bw, bh = int(tw + 2 * st + 60), int(asc + desc + 2 * st + 60)
    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); sh = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(sh)
    x, y = 30 + st, 30 + st
    for t, col in parts:
        for ch in t:
            ds.text((x, y + CAP_SIZE * 0.07), ch, font=f, fill=(0, 0, 0, 110), stroke_width=st + 2, stroke_fill=(0, 0, 0, 110))
            d.text((x, y), ch, font=f, fill=col, stroke_width=st, stroke_fill=INK)
            x += f.getlength(ch) + CAP_TRACK * CAP_SIZE
        x += space - CAP_TRACK * CAP_SIZE
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
    if name not in _SRC:
        p = os.path.join(reel_dir, "src", name + "_c.png")
        _SRC[name] = np.asarray(Image.open(p).convert("RGB"))
    return _SRC[name]

def paper_tex(seed=5):
    """Фактура бумаги ±2.5%: тот же крем, что у длинных роликов, но не мёртвая заливка."""
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    n = cv2.resize(cv2.GaussianBlur(n, (0, 0), 1.2), (W, H), interpolation=cv2.INTER_CUBIC)
    n = n / (np.abs(n).max() + 1e-6)
    return np.clip(PAPER[None, None] * (1 + 0.025 * n[..., None]), 0, 255).astype(np.uint8)

def sample(src, cx, cy, h, scale_src=2.0, shake=(0, 0), rot=0.0):
    """Окно (cx, cy, высота h) в координатах ИСХОДНОГО кадра -> картинка 1080xPH. Края за картинкой — бумага."""
    s = h * scale_src / PH
    a = math.radians(rot)
    ca, sa = math.cos(a) * s, math.sin(a) * s
    X0, Y0 = cx * scale_src, cy * scale_src
    M = np.array([[ca, -sa, X0 - ca * (W / 2 + shake[0]) + sa * (PH / 2 + shake[1])],
                  [sa, ca, Y0 - sa * (W / 2 + shake[0]) - ca * (PH / 2 + shake[1])]], np.float32)
    return cv2.warpAffine(src, M, (W, PH), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR,
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
        if share >= canvas.PAPER_MIN_SHARE: a = canvas.retint(a, col)
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out)
        print(f"  бумага {name}: {col.round().tolist()} -> крем (доля бумаги по краю {share:.2f})")


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
# Только звуки владельца (assets/sfx/reels, решение 22.10): синтезированные свисты, щелчки на субтитрах,
# тики и музыка-заглушка звучали дёшево. Пик звука — момент, который должен совпасть со склейкой.
SR = 48000
SFX_DIR = os.path.join(ROOT, "assets", "sfx", "reels")
SFX = {   # файл, где пик (с), громкость пика (dBFS) — без голоса звук не нормализуется, громкость задана тут
    "riser": ("riser_metallic.mp3", 1.65, -7.0),       # интрига: стартует сразу после фразы-хука
    "swoosh": ("swoosh.mp3", 0.35, -10.0),             # хлёсткий переход
    "swoosh_deep": ("swoosh_deep_low.wav", 0.70, -8.0),  # большой переход, смена части ролика
    "oof": ("oof.mp3", 0.10, -9.0),                    # «провал» — смешная неудача героя
}
_SFX = {}

def sfx(name):
    if name not in _SFX:
        f, _, peak_db = SFX[name]
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SFX_DIR, f), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                           capture_output=True, check=True)
        x = np.frombuffer(p.stdout, np.float32).reshape(-1, 2).copy()
        _SFX[name] = x * (10 ** (peak_db / 20) / max(1e-6, float(np.abs(x).max())))
    return _SFX[name]


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
    def wt(b_idx, k, after=False):
        w = times[spans[b_idx][0] + k]
        return w["end"] if after else w["start"]
    events = []
    for bi, b in enumerate(beats):
        for e in b.get("fx", []):                     # after: от конца слова (riser — сразу после фразы-хука)
            events.append(dict(e, t=wt(bi, e.get("at", 0), e.get("after", False)) + e.get("dt", 0.0), beat=bi))
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
    mix_audio(wav, total, shots, events, spec)
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
                sc = PH / (h / punch) / 2.0
                base = motion_blur(base, s["whip"][0] * k * sc * 0.25 * 2.0 * 0.5, s["whip"][1] * k * sc * 0.25)
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
            rgba = doll_frame(t, total + 0.5, s["doll_acts"])
            base = paste_doll(base, rgba, W / 2 + shake[0], s.get("cy", PH * 0.55) + shake[1], s.get("h", 900) * zs)
    base = np.ascontiguousarray(base)

    # накладки фраз (в координатах картинки 1080xPH)
    arrows = []
    for e in events:
        held = e.get("hold") and e["t"] <= t < e["t"] + e["hold"] and kind == e.get("kind_of_shot", kind)
        if not (s["t0"] - 0.01 <= e["t"] <= t < s["t1"] + 0.01 or held):
            continue
        if e["kind"] == "write":                    # рукописная надпись на рисунке, пишется ~0.5 с
            im = text_img(e["text"], font(HAND, e.get("size", 120), 700), RED if e.get("red", True) else INK)
            u = (t - e["t"]) / e.get("dur", 0.5)
            over(base, im, e["x"], e["y"], wipe=min(1.0, u * 1.05), scale=1.0)
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
        elif e["kind"] == "badge":                  # плашка-подпись в кадре (бесплатно, ссылка)
            im = text_img(e["text"], font(FONT, e.get("size", 64)), WHITE if e.get("dark") else INK, stroke=0, pad=6)
            pad = Image.new("RGBA", (im.width + 40, im.height + 10), (0, 0, 0, 0))
            ImageDraw.Draw(pad).rounded_rectangle((0, 0, pad.width - 1, pad.height - 1), radius=pad.height // 2,
                                                  fill=(18, 18, 20, 235) if e.get("dark") else (255, 210, 63, 255))
            pad.alpha_composite(im, (20, 5))
            sc = ease_out_back((t - e["t"]) / 0.22)
            over(base, pad, e["x"], e["y"], scale=max(0.01, sc))

    # картинка уходит в полосу субтитров мягким краем: одна бумага, без «вклеенного» прямоугольника
    pic = base; base = tex.copy(); f_ = 60
    base[:PH - f_] = pic[:PH - f_]
    a_ = np.linspace(1, 0, f_, dtype=np.float32)[:, None, None]
    base[PH - f_:PH] = (pic[PH - f_:].astype(np.float32) * a_ + base[PH - f_:PH].astype(np.float32) * (1 - a_)).astype(np.uint8)
    for e in arrows:
        arrow(base, e["p0"], e["p1"], (t - e["t"]) / 0.25)

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
        over(base, im, W / 2, PH * 0.20, scale=sc)

    # субтитры: группа въезжает снизу, активное слово — по времени слова
    for c in caps:
        if c["t0"] - 0.0 <= t < c["t1"]:
            act = c["idx"][0]
            for j in c["idx"]:
                if times[j]["start"] - 0.03 <= t: act = j
            im = c["imgs"][act]
            u = (t - c["t0"]) / 0.20                  # подъём на 18 px за 200 мс с торможением + проявление за 100 мс;
            dy = 18 * (1 - ease_out(u))                   # без «прыжка» с перелётом и без смены размера
            over(base, im, CAP_CX, CAP_CY + dy, alpha=min(1.0, u * 2.0))
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

def mix_audio(path, total, shots, events, spec):
    """Звук рилса: хлёсткие склейки — swoosh пиком на склейку (J-cut звука: звук приходит раньше картинки),
    события фраз (sfx) — пиком на слово, riser — началом сразу после фразы-хука. Больше ничего."""
    n = int((total + 0.2) * SR); tr = np.zeros((n, 2), np.float32)
    def put(name, t, align="peak"):
        x = sfx(name); t0 = t - (SFX[name][1] if align == "peak" else 0.0)
        i = int(t0 * SR)
        if i < 0: x = x[-i:]; i = 0
        m = min(len(x), n - i)
        if m > 0: tr[i:i + m] += x[:m]
    for k, sh in enumerate(shots):
        if k and sh.get("whip") and sh.get("sound", "swoosh"):
            put(sh.get("sound", "swoosh"), sh["t0"])
        elif k and sh.get("sound"):
            put(sh["sound"], sh["t0"])
    for e in events:
        if e["kind"] == "sfx": put(e["name"], e["t"], e.get("align", "peak"))
    peak = float(np.abs(tr).max())
    if peak > 0.89: tr *= 0.89 / peak                 # наложение двух звуков не клипует: пик не выше -1 dBFS
    pcm = (np.clip(tr, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

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
