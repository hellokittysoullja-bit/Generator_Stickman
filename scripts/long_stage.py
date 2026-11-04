#!/usr/bin/env python3
"""Сцены на кремовой бумаге в длинном ролике — приём канала Дани (владелец 04.11, по кадрам образца и пробнику
`montage_proto`): «вырезанные предметы на нашей бумаге… фотка отдаляется, какая-то другая… разнообразней, заполняет
скучные места, и картинок нужно меньше — одна вырезанная из другой… всё по смыслу, когда надо, а не просто так».

План ручного монтажа (`edit.json`) вместо окна своего рисунка показывает сцену `stage`:
  {"at": "слово", "why": "зачем по смыслу", "sound": "swoosh_deep",
   "stage": {"type": "items",                 # 1–3 вырезки в ряд (перечисление, «было → стало»)
             "items": [{"src": "lib:<файл>" | "phrase:<N>" | путь, "box": [x0, y0, x1, y1] | "poly": [[x, y], …],
                        "label": "ДО 10", "at": "слово", "sound": "swoosh", "h": 0.40}]}}
  {"stage": {"type": "cards",                 # две карточки рядом, на слове focus_at одна уезжает, другая на весь экран
             "cards": [{"src": …, "label": "8 СЕКУНД?", "at": "слово", "sound": …}, {…}],
             "focus": 1, "focus_at": "слово", "focus_sound": "swoosh_deep"}}
Вырезка — по контуру нейросетью (rembg, BiRefNet) в рамке `box` или по многоугольнику `poly` (если нейросеть цепляет
соседа: пробник — усы кота у ноутбука); остаётся самый большой предмет. Бумага рисунка приводится к крему, у предмета
мягкая тень, фон — крем со слабой виньеткой (владелец 04.11: «очень слабая виньетка, чтобы не казалось, что пусто»).
Время появления каждого элемента — его слово (как склейка монтажа), звук — на том же кадре (assemble_frames)."""
import hashlib
import json
import os

import cv2
import numpy as np
from PIL import Image

import canvas

W, H = 1920, 1080
VIGNETTE = 0.07          # края на 7 % темнее центра: бумага не пустая, но и не «сцена в луче» образца
GRAIN = 0.012
POP_SEC = 0.35           # выскакивание вырезки с перелётом
SLIDE_SEC = 0.5          # карточка уезжает за край / встаёт в центр
GROUP_SEC = 0.45          # группа раздвигается под новый элемент
ZOOM_SEC = 0.6           # карточка на весь экран
CARD_H = 470             # высота карточки в паре
CARD_RADIUS = 34
ITEM_H = 0.40            # высота вырезки по умолчанию — доля кадра
LABEL_SIZE = 96
VERSION = 2              # смена вида — смена подписи клипа

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BG = None


def ease_io(u):
    u = min(1.0, max(0.0, u))
    return u*u*(3 - 2*u)


def back_out(u, s=1.7):
    u = min(1.0, max(0.0, u)) - 1
    return 1 + (s + 1)*u**3 + s*u**2


def background():
    """Крем с живым зерном и слабой виньеткой."""
    global _BG
    if _BG is None:
        rng = np.random.default_rng(3)
        g = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.2)
        g = 1 + GRAIN*g/g.std()
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W/2)/(W/2))**2 + ((yy - H/2)/(H/2))**2)/np.sqrt(2)
        v = 1 - VIGNETTE*np.clip((r - 0.35)/0.65, 0, 1)**1.6
        _BG = np.clip(canvas.CREAM[None, None]*(g*v)[..., None], 0, 255).astype(np.float32)
    return _BG


def resolve_src(src, video_dir, phrase_src=None):
    """«lib:<файл>» — оригинал библиотеки, «phrase:<N>» — картинка фразы N этого ролика, иначе путь."""
    if src.startswith("lib:"):
        return os.path.join(ROOT, "library", "cat", "originals", src[4:])
    if src.startswith("phrase:"):
        if phrase_src is None:
            raise ValueError(f"{src}: картинка фразы недоступна")
        return phrase_src(int(src[7:]))
    return src if os.path.isabs(src) else os.path.join(video_dir, src)


_SESSION = None


def _paper_like(img):
    col, share = canvas.paper_color(img)
    return canvas.retint(img, col) if canvas.is_paper(col, share) else img


def cutout(path, box=None, poly=None, cache_dir=None):
    """RGBA-вырезка предмета (uint8). poly — многоугольник по сетке рисунка; иначе box и нейросеть по контуру,
    из маски — самый большой предмет (соседи у края рамки прочь). Кэш — по файлу и рамке."""
    key = hashlib.sha256(json.dumps([os.path.basename(path), os.path.getsize(path), box, poly, VERSION]).encode()).hexdigest()[:16]
    cp = os.path.join(cache_dir, f"cut_{key}.png") if cache_dir else None
    if cp and os.path.exists(cp):
        return np.asarray(Image.open(cp).convert("RGBA"))
    img = _paper_like(np.asarray(Image.open(path).convert("RGB"), np.float32))
    if poly:
        m = np.zeros(img.shape[:2], np.uint8)
        cv2.fillPoly(m, [np.int32(poly)], 1)
        m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.0)
    else:
        global _SESSION
        from rembg import new_session, remove
        if _SESSION is None:
            _SESSION = new_session("birefnet-general-lite")
        x0, y0, x1, y1 = box or (0, 0, img.shape[1], img.shape[0])
        crop = Image.fromarray(np.clip(img[y0:y1, x0:x1], 0, 255).astype(np.uint8))
        mc = np.asarray(remove(crop, session=_SESSION, only_mask=True), np.float32)/255
        n, lab, st, _ = cv2.connectedComponentsWithStats((mc > 0.5).astype(np.uint8), connectivity=8)
        if n > 2:
            keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
            mc = mc*cv2.dilate((lab == keep).astype(np.uint8), np.ones((5, 5), np.uint8))
        m = np.zeros(img.shape[:2], np.float32)
        m[y0:y1, x0:x1] = mc
    ys, xs = np.nonzero(m > 0.5)
    if not len(ys):
        raise ValueError(f"вырезка {os.path.basename(path)} {box or poly}: предмета не нашлось")
    a, b, c, d = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([np.clip(img[a:b, c:d], 0, 255), m[a:b, c:d, None]*255]).astype(np.uint8)
    if cp:
        os.makedirs(cache_dir, exist_ok=True)
        Image.fromarray(rgba).save(cp)
    return rgba


def card(path, cache_dir=None):
    """Картинка карточкой: скруглённые углы, тонкий край; бумага рисунка — крем."""
    key = hashlib.sha256(json.dumps([os.path.basename(path), os.path.getsize(path), "card", VERSION]).encode()).hexdigest()[:16]
    cp = os.path.join(cache_dir, f"card_{key}.png") if cache_dir else None
    if cp and os.path.exists(cp):
        return np.asarray(Image.open(cp).convert("RGBA"))
    img = _paper_like(np.asarray(Image.open(path).convert("RGB"), np.float32))
    h, w = img.shape[:2]
    r = int(CARD_RADIUS*w/900)
    m = np.zeros((h, w), np.uint8)
    cv2.rectangle(m, (r, 0), (w - r, h), 1, -1)
    cv2.rectangle(m, (0, r), (w, h - r), 1, -1)
    for cx, cy in ((r, r), (w - r, r), (r, h - r), (w - r, h - r)):
        cv2.circle(m, (cx, cy), r, 1, -1)
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8)
    rgba = np.dstack([np.clip(img, 0, 255), a*255]).astype(np.uint8)
    if cp:
        os.makedirs(cache_dir, exist_ok=True)
        Image.fromarray(rgba).save(cp)
    return rgba


def place(f, rgba, cx, cy, h_px, alpha=1.0, rot=0.0, shadow=True):
    """Наложить вырезку высотой h_px с центром (cx, cy) и мягкой тенью."""
    if alpha <= 0.01 or h_px < 4:
        return f
    src = rgba.astype(np.float32)
    s = h_px/src.shape[0]
    M = cv2.getRotationMatrix2D((src.shape[1]/2, src.shape[0]/2), rot, s)
    M[0, 2] += cx - src.shape[1]/2
    M[1, 2] += cy - src.shape[0]/2
    out = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_CUBIC, borderValue=0)
    a = np.clip(out[..., 3:]/255.0*alpha, 0, 1)
    if shadow:
        sh = cv2.GaussianBlur(np.roll(np.roll(a[..., 0], int(0.025*h_px) + 6, 0), int(0.012*h_px) + 3, 1), (0, 0), 10)
        f = f*(1 - 0.32*sh[..., None])
    return f*(1 - a) + out[..., :3]*a


class Stage:
    """Сцена плана: assets — RGBA элементов, времена — от начала плана (с)."""

    def __init__(self, spec, assets, dur):
        import long_fx
        self.spec, self.assets, self.dur = spec, assets, dur
        self.labels, self.label_x = [], []
        if spec["type"] == "items":
            n = len(spec["items"])
            xs = [W/2] if n == 1 else [W*(0.27 + 0.46*k/(n - 1)) for k in range(n)] if n == 2 else \
                [W*(0.19 + 0.31*k) for k in range(n)]
            self.xs = xs
            for k, it in enumerate(spec["items"]):
                if it.get("label"):
                    y = 150 if it.get("label_top", n <= 2) else 880
                    self.label_x.append(xs[k])
                    self.labels.append((long_fx.BoldText(it["label"], xs[k], y, size=it.get("label_size", LABEL_SIZE),
                                                         t0=it["t"] + 0.25), None))
        else:
            self.xs = [W*0.25, W*0.75]
            for k, c in enumerate(spec["cards"]):
                if c.get("label"):
                    end = spec.get("focus_t")
                    self.label_x.append(self.xs[k])
                    self.labels.append((long_fx.BoldText(c["label"], self.xs[k], 150, size=c.get("label_size", LABEL_SIZE),
                                                         t0=c["t"] + 0.25), end))

    def shift(self, t):
        """Сдвиг группы по x: появившиеся элементы стоят по центру кадра, новый раздвигает их (а не один в углу)."""
        sp = self.spec
        el = sp["items"] if sp["type"] == "items" else sp["cards"]
        if sp["type"] == "cards" and sp.get("focus_t") is not None and t >= sp["focus_t"]:
            t = sp["focus_t"]                      # на фокусе группа уже стоит по местам, дальше — выезд и наезд
        def centre(m):
            return W/2 - sum(self.xs[:m])/m
        out = centre(1)
        for k in range(1, len(el)):
            u = ease_io((t - el[k]["t"])/GROUP_SEC)
            out += (centre(k + 1) - centre(k))*u
        return out

    def frame(self, t):
        f = background().copy()
        sp = self.spec
        dx = self.shift(t)
        if sp["type"] == "items":
            n = len(sp["items"])
            for k, it in enumerate(sp["items"]):
                if t < it["t"]:
                    continue
                u = (t - it["t"])/POP_SEC
                h = H*it.get("h", ITEM_H if n > 2 else 0.58)
                f = place(f, self.assets[k], self.xs[k] + dx, H*(0.50 if n > 2 else 0.56), h*max(0.05, back_out(u)),
                          alpha=min(1.0, u*3))
        else:
            ft = sp.get("focus_t")
            fk = sp.get("focus", 1)
            for k, c in enumerate(sp["cards"]):
                if t < c["t"]:
                    continue
                enter = back_out((t - c["t"])/0.4)
                x, y, h = self.xs[k] + dx, H*0.56 + (1 - enter)*700, CARD_H
                if ft is not None and t >= ft:
                    u = ease_io((t - ft)/SLIDE_SEC)
                    if k != fk:
                        x += (-1 if k < fk else 1)*u*1150
                    else:
                        x += (W/2 - x)*u
                        z = ease_io((t - ft - SLIDE_SEC*0.6)/ZOOM_SEC)
                        h = CARD_H + z*(H*1.06 - CARD_H)
                        y = H*0.56 + (H/2 - H*0.56)*max(u, z)
                f = place(f, self.assets[k], x, y, h, rot=(1.5 if k else -1.5)*(1 - enter), shadow=h < H)
        for (lb, end), x0 in zip(self.labels, self.label_x):
            lb.cx = x0 + dx                        # подпись едет со своим элементом
            f = lb.composite(f, t, t_end=end if end is not None else self.dur)
        return f


def times(spec, word_time, t0):
    """Слова элементов -> секунды от начала плана; spec меняется на месте (поля t, focus_t)."""
    key = "items" if spec["type"] == "items" else "cards"
    for k, it in enumerate(spec[key]):
        it["t"] = max(0.0, word_time(it["at"]) - t0) if it.get("at") else 0.0 + 0.15*k
    if spec["type"] == "cards" and spec.get("focus_at"):
        spec["focus_t"] = max(0.0, word_time(spec["focus_at"]) - t0)
    return spec


def beats(spec):
    """Секунды от начала плана всех событий сцены — появлений элементов и сдвига карточек, со звуком или без: это
    моменты на экране, к ним прилипает звук смысла на том же слове (long_sfx.snap)."""
    key = "items" if spec["type"] == "items" else "cards"
    out = [it["t"] for it in spec[key] if "t" in it]
    if spec.get("focus_t") is not None:
        out.append(spec["focus_t"])
    return sorted(out)


def sounds(spec):
    """[(секунды от начала плана, звук, why)] появлений и сдвигов сцены."""
    out = []
    key = "items" if spec["type"] == "items" else "cards"
    for it in spec[key]:
        if it.get("sound"):
            out.append((it["t"], it["sound"], f"появление: {it.get('label') or it.get('src')}"))
    if spec.get("focus_sound") and spec.get("focus_t") is not None:
        out.append((spec["focus_t"], spec["focus_sound"], "карточка на весь экран"))
    return out
