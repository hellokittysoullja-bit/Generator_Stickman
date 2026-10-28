#!/usr/bin/env python3
"""Эффекты удержания длинного ролика поверх кадра (28.10, по образцу, который прислал владелец):
кот-ведущий выходит к зрителю перед размытой сценой и жирный текст, вылетающий под голос.

Решения владельца 28.10: размытие — только когда кот обращается к зрителю; рукописный карандаш остаётся как был, а
жирный текст — шрифт субтитров рилсов (Onest Black), белый со слабой чёрной обводкой, вылетает (по буквам и другими
эффектами). Как выглядит — на согласование владельцу до встраивания в ролик.

Встройка в сборку (28.10, L02): videos/NN/fx.json — {"phrases": {"<номер фразы с 1>": {"narrator": {"why": …},
"bold": [{"text": "строка", "word": "слово фразы", "style": "letters|slam|rise", "why": …}]}}}. Кот-ведущий стоит всю
фразу (выходит через ENTER_SEC после её начала, уходит склейкой или, если склейки нет, обратным ростом); жирная строка
встаёт на слове и стоит до следующей строки той же фразы или до конца фразы (без кота — не дольше BOLD_HOLD_SEC);
место строки — по самому кадру (free_spot), мимо кота. Без why событие не ставится: эффект со смыслом, а не украшение."""
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw

W, H = 1920, 1080
FONT_AXES = {"Weight": 900}
STROKE = 3                 # слабая обводка: тонкая и полупрозрачная, не наклейка
STROKE_ALPHA = 0.84          # владелец 28.10, дважды «чуть-чуть сильнее обводку»: 0.55 → 0.72 → 0.84
SHADOW = (0, 5, 9, 0.55)   # dx, dy, blur, alpha: мягкая тень под буквами
GLOW = (14, 0.38)          # размытие и сила тёмного ореола: белое на кремовой бумаге без него не читается (пробник 28.10)


def _font(size):
    import reel
    return reel.font(reel.CAP_FONT, size, FONT_AXES, raqm=True)


def back_out(u, s=1.7):
    """Перелёт к 1 с отскоком (как поп слов в субтитрах рилсов)."""
    u = min(max(u, 0.0), 1.0) - 1
    return 1 + u*u*((s + 1)*u + s)


def ease_out(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u)**3


# --------------------------------------------------------------------------- размытие под ведущим

def focus_blur(f, t, t0, t1, sigma=20, dark=0.05, ramp=0.5, out=None):
    """Сцена уходит в расфокус вместе с выходом кота (замер образца 28.10: за 0,1 с уже сильно, максимум к 0,5 с —
    ease-out), до конца плана; уход — склейкой, а не обратным размытием (out=None). out — секунды обратного размытия,
    если плана-склейки после нет."""
    k = ease_out((t - t0)/ramp)
    if out:
        k *= 1 - ease_out((t - (t1 - out))/out)
    if k <= 0.01:
        return f
    b = cv2.GaussianBlur(np.ascontiguousarray(f, np.float32), (0, 0), sigma*k + 0.1)
    return b*(1 - dark*k)


GROW_SEC, OVER, SETTLE_SEC = 0.4, 1.36, 0.55   # замер образца: 0,4 с рост до 136 %, 0,55 с плавная посадка к 100 %
ENTER_SEC = 0.2            # сцена сначала резкая (образец: ~0,15 с), потом выходит кот
EXIT_SEC = 0.3             # уход без склейки: обратный рост и сцена в фокус
BOLD_HOLD_SEC = 2.4        # строка без кота стоит не дольше: камера режет планы, а строка стоит на экране
SIZE_NARRATOR, SIZE_PLAIN = 150, 120


def narrator_scale(t):
    """Масштаб кота-ведущего: растёт от ног из маленького с большим мягким перелётом и плавно садится (без пружины)."""
    if t < GROW_SEC:
        return 0.04 + (OVER - 0.04)*ease_out(t/GROW_SEC)
    u = min(1.0, (t - GROW_SEC)/SETTLE_SEC)
    return OVER - (OVER - 1.0)*(0.5 - 0.5*math.cos(math.pi*u))


# Жизнь ведущего (владелец 28.10: «чтоб двигал хвостом, ушками, головой… чтоб живой был»). Фон куклы рассчитан на
# кадр 6–10 с: за 4 с ведущего хвост ходил на 3,6°, уши не дёргались ни разу (первое — через 3–6 с), голова наклонялась
# один раз, пока кот ещё рос. Ведущий на экране 3–5 с, поэтому жизнь плотнее и крупнее, но в тех же формах куклы.
TAIL_GAIN = 2.4            # хвост: ±4,3° куклы → до ±10°, плюс медленный мах
TAIL_SWING = (4.5, 1.7)    # градусы и период маха, с
EAR_FLICKS = (0.75, 2.3)   # секунды после выхода: дёрнуть ухом (второе — двойное), как живая кошка, слушающая
EAR_DEG = 14.0
HEAD_SWAY = (2.2, 2.9)     # покачивание головы при речи: градусы и период, с
NOD_DEG = 2.0              # кивок-акцент на начале слова (затухает за 0,35 с), знак чередуется
Q_TILT = 8.0               # наклон на «?» вместо 5° куклы: вопрос зрителю виден


def _flick(u, deg):
    """Флик уха: резкий ход за 0,1 с с лёгким перелётом и возвратом к 0,35 с."""
    if not 0 <= u < 0.35:
        return 0.0
    if u < 0.1:
        return -deg*math.sin(0.5*math.pi*u/0.1)
    return -deg*math.exp(-(u - 0.1)/0.07)*math.cos(2*math.pi*(u - 0.1)/0.3)


class Narrator:
    """Кукла кота перед сценой: вырастает от ног снизу, живёт (хвост, уши, голова, взгляд, моргание), смотрит на
    зрителя; уходит склейкой. words — слова от момента выхода кота (t=0 — начало роста)."""

    def __init__(self, dur, cx=0.66, height=0.70, seed=3, words=None, text="", glance=None):
        import mascot_live as M
        self.M, self.R = M, M.rig()
        words = words or []
        acts = M.plan_actions(dur, words, text, [0.0, 0.0], seed=seed)
        for a in acts:
            if a["do"] == "tilt" and a["deg"] > 0:
                a["deg"] = Q_TILT
                a["t"] = max(a["t"], GROW_SEC + 0.1)       # наклон, когда кот уже вырос, а не во время роста
        if glance is not None:                              # взгляд на текст, который вылетает рядом, и снова на зрителя
            acts.append(dict(t=GROW_SEC + 0.15, do="look", x=glance[0], y=glance[1], dur=0.75))
        self.state0 = M._mod().plan(dur, acts, seed=seed)
        self.nods = [(w["start"], 1 if k % 2 else -1) for k, w in enumerate(words) if len(w["word"]) > 3]
        self.dur, self.cx, self.height = dur, cx, height

    def screen_box(self):
        """Где кот на экране с перелётом роста (до OVER): [x0, y0, x1, y1] — чтобы текст его не накрыл даже на росте
        (пробник встройки 28.10: на 0,7 с ухо задевало «Знакомо?»)."""
        st = self.state0(GROW_SEC + SETTLE_SEC)
        x0, y0, x1, y1 = self.R.bb_for(st)
        k = self.height*H/(y1 - y0)*OVER
        w, h = (x1 - x0)*k, (y1 - y0)*k
        return [self.cx*W - w/2, H + 4 - h, self.cx*W + w/2, H]

    def state(self, t):
        st = dict(self.state0(t))
        st["tail"] = st["tail"]*TAIL_GAIN + TAIL_SWING[0]*math.sin(2*math.pi*t/TAIL_SWING[1] + 0.8)
        st["ear"] = st["ear"] + sum(_flick(t - e, EAR_DEG) + (_flick(t - e - 0.22, EAR_DEG*0.7) if k else 0.0)
                                    for k, e in enumerate(EAR_FLICKS))
        live = min(1.0, max(0.0, (t - GROW_SEC)/0.3))      # пока растёт — без покачивания (иначе рост «гуляет»)
        head = HEAD_SWAY[0]*math.sin(2*math.pi*t/HEAD_SWAY[1])
        for t0, sgn in self.nods:
            u = t - t0
            if 0 <= u < 0.35:
                head += sgn*NOD_DEG*math.sin(math.pi*u/0.35)
        st["head"] = st["head"] + live*head
        return st

    def composite(self, f, t, exit_at=None):
        """exit_at — когда кот должен исчезнуть, если склейки нет: уходит обратным ростом за EXIT_SEC."""
        st = self.state(t)
        rgba = self.R.frame_rgba(st, t)
        x0, y0, x1, y1 = self.R.bb_for(st)
        sub = np.ascontiguousarray(rgba[y0:y1, x0:x1])
        sc = narrator_scale(t)
        if exit_at is not None and t > exit_at - EXIT_SEC:
            sc *= max(0.0, 1 - ease_out((t - (exit_at - EXIT_SEC))/EXIT_SEC))
            if sc < 0.03:
                return f
        k = self.height*H/sub.shape[0]*sc
        nw, nh = max(1, int(sub.shape[1]*k)), max(1, int(sub.shape[0]*k))
        small = cv2.resize(sub, (nw, nh), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
        x, y = int(self.cx*W - nw/2), int(H + 4 - nh)       # ноги на нижнем крае, рост от ног
        out_ = f.copy()
        xa, ya, xb, yb = max(0, x), max(0, y), min(W, x + nw), min(H, y + nh)
        if xb <= xa or yb <= ya:
            return out_
        piece = small[ya - y:yb - y, xa - x:xb - x]
        a = np.clip(piece[..., 3:4], 0, 1)
        sh = cv2.GaussianBlur(a[..., 0], (0, 0), 22)[..., None]*0.22    # мягкая тень: кот перед сценой
        region = out_[ya:yb, xa:xb]
        region *= 1 - sh
        out_[ya:yb, xa:xb] = region*(1 - a) + np.clip(piece[..., :3], 0, 255)
        return out_


# --------------------------------------------------------------------------- жирный текст

def _glyphs(text, size):
    """[(символ, x, ширина)] строки и её габариты."""
    f = _font(size)
    xs, x = [], 0.0
    for ch in text:
        w = f.getlength(ch)
        xs.append((ch, x, w))
        x += w
    asc, desc = f.getmetrics()
    return f, xs, x, asc + desc


def _glyph_rgba(ch, f, size):
    pad = STROKE + 14
    w = int(f.getlength(ch)) + 2*pad
    h = size + 2*pad
    im = Image.new("L", (w, h), 0)
    st = Image.new("L", (w, h), 0)
    ImageDraw.Draw(st).text((pad, pad), ch, font=f, fill=255, stroke_width=STROKE, stroke_fill=255)
    ImageDraw.Draw(im).text((pad, pad), ch, font=f, fill=255)
    fill = np.asarray(im, np.float32)/255
    stroke = np.asarray(st, np.float32)/255
    a = np.maximum(fill, stroke*STROKE_ALPHA)
    rgb = np.repeat((fill/np.maximum(a, 1e-4))[..., None]*255, 3, axis=2)     # белое внутри, тёмная обводка
    return np.dstack([rgb*a[..., None], a]), pad


def _paste(f, rgba, cx, cy, scale=1.0, rot=0.0, alpha=1.0, blur_x=0):
    """Буква на кадр (на месте, f меняется): сдвиг, тень и ореол считаются только в окне вокруг буквы — по всему
    кадру 1920×1080 это стоило 0,7 с на кадр строки (замер 28.10)."""
    h, w = rgba.shape[:2]
    r = int(0.75*max(w, h)*max(scale, 0.05)) + 60 + int(blur_x)
    x0, y0 = max(0, int(cx) - r), max(0, int(cy) - r)
    x1, y1 = min(W, int(cx) + r), min(H, int(cy) + r)
    if x1 <= x0 or y1 <= y0:
        return f
    M = cv2.getRotationMatrix2D((w/2, h/2), rot, scale)
    M[0, 2] += cx - w/2 - x0
    M[1, 2] += cy - h/2 - y0
    warped = cv2.warpAffine(rgba, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderValue=0)
    if blur_x > 1:
        n = int(blur_x) | 1
        warped = cv2.filter2D(warped, -1, np.ones((1, n), np.float32)/n)
    a = warped[..., 3:4]*alpha
    if a.max() <= 0:
        return f
    dx, dy, sb, sa = SHADOW
    sh = cv2.GaussianBlur(np.roll(np.roll(a, dy, 0), dx, 1)[..., 0], (0, 0), sb)[..., None]*sa
    gb, ga = GLOW
    glow = cv2.GaussianBlur(cv2.dilate(a[..., 0], np.ones((9, 9), np.float32)), (0, 0), gb)[..., None]*ga
    reg = f[y0:y1, x0:x1]
    reg = reg*(1 - np.clip(sh + glow, 0, 0.8))
    f[y0:y1, x0:x1] = reg*(1 - a) + warped[..., :3]*alpha
    return f


def free_spot(f, text, size, prefer=None, margin=0.05, bottom=0.12, sizes=(1.0, 0.85, 0.72), avoid=None):
    """Где поставить жирную строку, чтобы она не легла на рисунок (пробник 28.10: «2 минуты» на ухе кота, потом на
    стопке бумаг и за краем кадра). Чернила — пиксели темнее бумаги кадра больше чем на 28; окно строки с запасом
    скользит по кадру внутри полей (снизу — место плеера). Лучшее — с наименьшей долей чернил, при равенстве ближе к
    prefer; не нашлось чистого (≤ 1,5 %) — кегль меньше. avoid — [x0, y0, x1, y1] экрана, куда нельзя (кот-ведущий).
    Возвращает (cx, cy, кегль, доля чернил)."""
    g = np.asarray(f, np.float32).mean(2)
    paper = np.percentile(g, 90)
    ink = (g < paper - 28).astype(np.float32)
    if avoid is not None:
        x0, y0, x1, y1 = (int(v) for v in avoid)
        ink[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = 1.0
    ii = cv2.integral(ink)
    px, py = prefer or (W/2, H*0.3)
    best = None
    for k in sizes:
        sz = int(size*k)
        _, _, tw, th = _glyphs(text, sz)
        bw, bh = int(tw + 0.12*sz), int(th*0.9 + 0.12*sz)
        xs = range(int(W*margin), int(W*(1 - margin)) - bw, 16)
        ys = range(int(H*margin), int(H*(1 - bottom)) - bh, 16)
        for y in ys:
            for x in xs:
                share = (ii[y + bh, x + bw] - ii[y, x + bw] - ii[y + bh, x] + ii[y, x])/(bw*bh)
                d = math.hypot(x + bw/2 - px, y + bh/2 - py)/W
                cand = (share + 0.02*d, x + bw/2, y + bh/2, sz, share)
                if best is None or cand < best:
                    best = cand
        if best is not None and best[4] <= 0.015:
            break
    _, cx, cy, sz, share = best
    return cx, cy, sz, share


class BoldText:
    """Жирная строка, вылетающая под голос. style: letters — по буквам с отскоком (как в образце); slam — слово
    целиком влетает крупным и встаёт с тряской; rise — слова поднимаются снизу по очереди."""

    def __init__(self, text, cx, cy, size=120, style="letters", t0=0.0, per=0.05, word_times=None):
        self.f, self.xs, self.width, self.h = _glyphs(text, size)
        self.text, self.cx, self.cy, self.size, self.style, self.t0, self.per = text, cx, cy, size, style, t0, per
        self.cache = {}
        self.word_times = word_times

    def _g(self, ch):
        if ch not in self.cache:
            self.cache[ch] = _glyph_rgba(ch, self.f, self.size)
        return self.cache[ch]

    def composite(self, f, t, t_end=None):
        if t < self.t0:
            return f
        fade = 1.0
        if t_end is not None and t > t_end - 0.18:
            fade = max(0.0, (t_end - t)/0.18)
        left = self.cx - self.width/2
        u0 = t - self.t0
        f = np.array(f, np.float32)                 # буквы кладутся на месте — на копию кадра
        if self.style == "slam":
            u = min(1.0, u0/0.22)
            sc = 1.9 - 0.9*ease_out(u)
            shake = 0.0 if u0 < 0.22 else 7*math.exp(-(u0 - 0.22)/0.08)*math.sin(2*math.pi*16*(u0 - 0.22))
            for ch, x, w in self.xs:
                if ch == " ":
                    continue
                g, pad = self._g(ch)
                gx = self.cx + (left + x + w/2 - self.cx)*sc
                f = _paste(f, g, gx + shake, self.cy, scale=sc, alpha=min(1.0, u*3)*fade, blur_x=(1 - u)*40)
            return f
        if self.style == "rise":
            wi = 0
            for ch, x, w in self.xs:
                if ch == " ":
                    wi += 1
                    continue
                d = u0 - wi*0.16
                if d <= 0:
                    continue
                u = min(1.0, d/0.28)
                g, pad = self._g(ch)
                f = _paste(f, g, left + x + w/2, self.cy + 70*(1 - ease_out(u)), alpha=ease_out(u)*fade)
            return f
        # letters: каждая буква выпрыгивает из маленькой с отскоком и лёгким поворотом (как в образце)
        for i, (ch, x, w) in enumerate(self.xs):
            if ch == " ":
                continue
            d = u0 - i*self.per
            if d <= 0:
                continue
            u = min(1.0, d/0.18)
            g, pad = self._g(ch)
            rot = (8 if i % 2 else -8)*(1 - u)
            f = _paste(f, g, left + x + w/2, self.cy + 18*(1 - u), scale=max(0.05, back_out(u)), rot=rot, alpha=fade)
        return f


# --------------------------------------------------------------------------- встройка в сборку

def load(video_dir):
    """fx.json ролика -> {номер фразы с 0: {"narrator": {...} | None, "bold": [...]}}. Без why — ошибка."""
    import json
    import os
    path = os.path.join(video_dir, "fx.json")
    if not os.path.exists(path):
        return {}
    out = {}
    for k, v in json.load(open(path, encoding="utf-8")).get("phrases", {}).items():
        nar, bold = v.get("narrator"), v.get("bold") or []
        if nar is not None and not (nar.get("why") or "").strip():
            raise ValueError(f"fx.json, фраза {k}: у кота-ведущего нет why")
        for b in bold:
            if not (b.get("why") or "").strip() or not (b.get("text") or "").strip():
                raise ValueError(f"fx.json, фраза {k}: у жирной строки нет text или why")
        out[int(k) - 1] = dict(narrator=nar, bold=bold)
    return out


def _stem(w):
    import re
    return re.sub(r"[^а-яёa-z0-9]", "", w.lower())


def events(spec, t0, t1, words, text, seed=0):
    """События одной фразы в секундах клипа. words — слова фразы (start/end от начала клипа)."""
    ev = []
    if spec.get("narrator") is not None:
        ev.append(dict(kind="narrator", t0=t0, t1=t1, text=text, seed=seed,
                       words=[dict(word=w["word"], start=w["start"] - t0 - ENTER_SEC, end=w["end"] - t0 - ENTER_SEC)
                              for w in words]))
    bold = []
    for b in spec.get("bold") or []:
        w = None
        if b.get("word"):
            st = _stem(b["word"])
            w = next((x for x in words if _stem(x["word"]) == st), None) or \
                next((x for x in words if _stem(x["word"]).startswith(st)), None)
        at = w["start"] - 0.05 if w else t0 + 0.3          # немое превью без alignment: в начале фразы
        bold.append(dict(kind="bold", text=b["text"], t0=max(t0, at), style=b.get("style", "letters")))
    bold.sort(key=lambda e: e["t0"])
    for i, e in enumerate(bold):
        end = bold[i + 1]["t0"] if i + 1 < len(bold) else t1
        if spec.get("narrator") is None:
            end = min(end, e["t0"] + BOLD_HOLD_SEC)
        e["t1"] = max(e["t0"] + 0.5, end)
        e["narrator"] = spec.get("narrator") is not None
    return ev + bold


class Track:
    """Все события клипа: размытие и кот-ведущий, жирные строки — поверх готового кадра экрана."""

    def __init__(self, evs, D):
        self.D = D
        self.nar = []
        for e in evs:
            if e["kind"] == "narrator":
                n = Narrator(max(0.5, e["t1"] - e["t0"] - ENTER_SEC), cx=0.79, height=0.70, seed=3 + e["seed"],
                             words=e["words"], text=e["text"], glance=(-0.6, -0.25))
                self.nar.append((e, n, n.screen_box()))
        self.bold = [dict(e, obj=None) for e in evs if e["kind"] == "bold"]

    def apply(self, f, t):
        box = None
        for e, n, b in self.nar:
            if not e["t0"] <= t < e["t1"]:
                continue
            exit_at = None if e["t1"] >= self.D - 1e-3 else e["t1"] - e["t0"] - ENTER_SEC   # склейки нет — уход сам
            if t >= e["t0"] + ENTER_SEC:
                f = focus_blur(f, t, e["t0"] + ENTER_SEC, e["t1"], out=EXIT_SEC if exit_at is not None else None)
                f = n.composite(f, t - e["t0"] - ENTER_SEC, exit_at=exit_at)
            box = b
        for e in self.bold:
            if not e["t0"] <= t < e["t1"]:
                continue
            if e["obj"] is None:
                if e["narrator"]:          # под котом сцена размыта: строке мешает только сам кот, кегль полный
                    cx, cy, sz, _ = free_spot(np.full_like(f, 245), e["text"], SIZE_NARRATOR, prefer=(W*0.33, H*0.3),
                                              avoid=box)
                else:
                    cx, cy, sz, _ = free_spot(f, e["text"], SIZE_PLAIN, prefer=(W/2, H*0.2), avoid=box)
                e["obj"] = BoldText(e["text"], cx, cy, size=sz, style=e["style"], t0=e["t0"])
            f = e["obj"].composite(f, t, t_end=e["t1"])
        return f
