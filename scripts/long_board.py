"""Доска расследования (владелец 04.11 о пробнике v2: «доска мне очень понравилась… навсегда принимаю»).

Пробковая доска под тёплым светом лампы в деревянной рамке; на ней фото-карточки (картинки ролика) на красных кнопках с
подписью от руки, стикеры с почерком и красным маркером, карточка-заголовок, вырванный лист блокнота, скотч; витая
красная нить с тенью идёт от карточки к карточке, ветки — к стикерам. Камера приходит на карточку на её слове, на
переезде чуть отъезжает (видна нить) и наклоняется, у кадра малая глубина резкости и живая дрожь; на слове overview_at —
общий план всей доски. Ставится по смыслу: цепочка исследований или улик, которые вместе дают вывод.

edit.json, план:
    {"stage": {"type": "board", "title": ["ВНИМАНИЕ", "куда оно уходит?"], "page": ["а у тебя", "так же?"],
               "cards": [{"src": "phrase:4", "caption": "8 секунд? миф", "at": "слово",
                          "note": {"lines": ["рыбка", "тут ни при чём"], "color": "yellow", "circle": 1}}, ...],
               "overview_at": "слово"}}
Время и звуки — long_stage.times/sounds (переезд — звук движения в его середине). Отрисовка — Board.frame(t)."""
import functools
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from easing import ease_io

W, H = 1920, 1080
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAVEAT = os.path.join(ROOT, "assets", "fonts", "Caveat-Variable.ttf")
INK = (24, 22, 26)
MARKER = (196, 30, 32)
NOTE_COLORS = {"yellow": (252, 224, 92), "pink": (250, 170, 180), "blue": (160, 214, 236), "green": (196, 230, 160)}
PIN_COLORS = {"red": (205, 36, 36), "blue": (40, 92, 190), "green": (50, 150, 70), "yellow": (230, 186, 30)}
NOTE_PINS = ("blue", "yellow", "green", "blue", "yellow")

CARD_W = 860              # ширина фото на доске (px доски)
CARD_FILL = 0.70          # карточка на остановке — 70 % высоты кадра
TRAVEL = 0.95             # переезд камеры от карточки к карточке, с
TRAVEL_LIFT = 0.35        # на переезде камера отъезжает на треть: видна нить
TILT = 2.0                # наклон камеры на остановке, °, чередуется
SHAKE_PX, SHAKE_DEG = (6, 4), 0.25   # живая рука оператора
DOF_SHARP = 0.45          # центр кадра резкий, к краям размытие (малая глубина резкости)
DOF_SIGMA, DOF_SIGMA_TRAVEL = 3.2, 4.5
BRANCH_DELAY, BRANCH_SEC = 0.35, 0.5   # ветка к стикеру тянется после прихода на карточку
YS = (0.39, 0.28, 0.42, 0.71, 0.60)    # змейка по высоте доски; пятая почти вровень с четвёртой — нить к ней не идёт снизу через подпись
VERSION = 1


def board_size(n):
    bw = max(3600, 1250*n + 200)
    return bw, int(bw*9/16)


def _font(size, wght=700):
    f = ImageFont.truetype(CAVEAT, size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


# --- материалы ------------------------------------------------------------------------------------------------------
@functools.lru_cache(maxsize=4)
def cork(bw, bh, seed=11):
    """Пробка с крошками, тёплый свет лампы сверху слева и деревянная рамка с тенью."""
    rng = np.random.default_rng(seed)

    def noise(sigma, amp):
        n = cv2.GaussianBlur(rng.normal(0, 1, (bh//2, bw//2)).astype(np.float32), (0, 0), sigma)
        return amp*cv2.resize(n/n.std(), (bw, bh), interpolation=cv2.INTER_LINEAR)
    t = noise(1.0, 0.05) + noise(4, 0.06) + noise(25, 0.05)
    img = np.array([176, 128, 82], np.float32)[None, None]*(1 + t)[..., None]
    for col, k in (((95, 62, 38), 26000), ((214, 172, 120), 18000), ((70, 45, 28), 6000)):   # крошки пробки
        ys, xs = rng.integers(1, bh - 2, k), rng.integers(1, bw - 2, k)
        tone = np.array(col, np.float32)[None]*rng.uniform(0.85, 1.1, (k, 1))
        for dy in (0, 1):
            for dx in (0, 1):
                img[ys + dy, xs + dx] = tone
    img = cv2.GaussianBlur(img, (0, 0), 0.8)
    yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
    lamp = np.exp(-(((xx - bw*0.38)/(bw*0.55))**2 + ((yy - bh*0.30)/(bh*0.75))**2))
    img = img*(0.62 + 0.48*lamp)[..., None]*np.array([1.04, 1.0, 0.92], np.float32)
    fr = 70
    frame = np.zeros((bh, bw), np.float32)
    frame[:fr], frame[-fr:], frame[:, :fr], frame[:, -fr:] = 1, 1, 1, 1
    wood = np.array([96, 62, 36], np.float32)*(1 + 0.12*np.sin(xx/9 + 3*np.sin(yy/140)))[..., None]
    img = img*(1 - frame[..., None]) + wood*(0.8 + 0.3*lamp[..., None])*frame[..., None]
    shade = cv2.GaussianBlur(frame, (0, 0), 18)*(1 - frame)                  # тень рамки на пробке
    return np.clip(img*(1 - 0.45*shade[..., None]), 0, 255).astype(np.uint8)


def polaroid(picture, caption, rng):
    """Картинка ролика в белой рамке с полем снизу и подписью от руки."""
    img = Image.fromarray(np.clip(picture, 0, 255).astype(np.uint8)).convert("RGB")
    img = img.resize((CARD_W, int(CARD_W*img.height/img.width)), Image.LANCZOS)
    m, bottom = 30, 140
    card = Image.new("RGB", (img.width + 2*m, img.height + m + bottom), (250, 248, 240))
    card.paste(img, (m, m))
    d = ImageDraw.Draw(card)
    size = 84
    f = _font(size)
    while d.textlength(caption, font=f) > card.width - 60 and size > 40:
        size -= 6
        f = _font(size)
    d.text(((card.width - d.textlength(caption, font=f))/2, img.height + m + 16), caption, font=f, fill=INK)
    arr = np.asarray(card, np.float32)*(1 + 0.025*rng.normal(0, 1, (card.height, card.width)))[..., None]
    return np.dstack([arr, np.full(arr.shape[:2], 255, np.float32)]), img.height + m          # и где начинается поле


def note(lines, color, rng, w=430, h=400, size=78, circle=None, under=False):
    """Стикер или карточка с почерком; circle — номер строки, обведённой красным маркером; under — подчёркнуто."""
    card = Image.new("RGB", (w, h), color)
    d = ImageDraw.Draw(card)
    f = _font(size)
    y = h*0.5 - len(lines)*size*0.55
    boxes = []
    for ln in lines:
        tw = d.textlength(ln, font=f)
        d.text(((w - tw)/2, y), ln, font=f, fill=INK)
        boxes.append(((w - tw)/2, y, tw))
        y += size*1.1
    arr = np.asarray(card, np.float32).copy()
    if under:
        x, y0, tw = boxes[0]
        pts = np.array([[x - 10 + t*(tw + 20), y0 + size*1.08 + 6*np.sin(t*7)] for t in np.linspace(0, 1, 40)], np.int32)
        cv2.polylines(arr, [pts], False, MARKER, 7, cv2.LINE_AA)
    if circle is not None and 0 <= circle < len(boxes):
        x, y0, tw = boxes[circle]
        t = np.linspace(-0.2, 2*np.pi + 0.5, 90)
        pts = np.stack([x + tw/2 + (tw/2 + 30)*np.cos(t)*(1 + 0.04*np.sin(3*t)), y0 + size*0.62 + size*0.75*np.sin(t)], 1)
        cv2.polylines(arr, [pts.astype(np.int32)], False, MARKER, 7, cv2.LINE_AA)
    g = np.linspace(0, 1, h)[:, None]
    arr *= (1 - 0.10*np.clip((g - 0.82)/0.18, 0, 1))[..., None]                    # низ стикера чуть загнут
    arr *= (1 + 0.02*rng.normal(0, 1, (h, w)))[..., None]
    return np.dstack([arr, np.full((h, w), 255, np.float32)])


def torn_page(lines, rng, w=700, h=520):
    """Вырванный лист блокнота: линейки, поле, дырки от пружины, рваный верх, почерк."""
    arr = np.full((h, w, 3), (248, 246, 238), np.float32)
    for y in range(90, h, 46):
        arr[y:y + 2] = (170, 196, 222)
    arr[:, 70:72] = (222, 150, 150)
    a = np.full((h, w), 255, np.float32)
    edge = (14 + 8*np.abs(np.convolve(rng.normal(0, 1, w + 20), np.ones(5)/5, "same")[10:w + 10])).astype(int)
    for x in range(w):
        a[:edge[x], x] = 0
    for y in range(40, h, 70):
        cv2.circle(a, (34, y), 9, 0, -1)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    for k, ln in enumerate(lines):
        d.text((120, 120 + k*120), ln, font=_font(90), fill=INK)
    return np.dstack([np.asarray(img, np.float32), a])


def tape(rng, w=230, h=70):
    a = np.full((h, w), 0.72, np.float32)
    a[:, :6] = np.linspace(0, 0.72, 6)[None]
    for x in (0, w - 1):
        for y in range(h):
            if rng.random() < 0.5:
                a[y, max(0, x - 4):x + 4] = 0
    return np.dstack([np.full((h, w, 3), (232, 222, 196), np.float32), a*255])


def put(dst, rgba, cx, cy, rot, shadow=0.42, lift=1.0):
    """Наклеить на доску с тенью; вернуть матрицу (координаты элемента -> доска)."""
    bh, bw = dst.shape[:2]
    h, w = rgba.shape[:2]
    M = cv2.getRotationMatrix2D((w/2, h/2), rot, 1.0)
    M[0, 2] += cx - w/2
    M[1, 2] += cy - h/2
    x0, y0 = int(max(0, cx - w)), int(max(0, cy - h))
    x1, y1 = int(min(bw, cx + w)), int(min(bh, cy + h))
    M2 = M.copy()
    M2[0, 2] -= x0
    M2[1, 2] -= y0
    lay = cv2.warpAffine(rgba, M2, (x1 - x0, y1 - y0), flags=cv2.INTER_CUBIC)
    a = lay[..., 3:]/255.0
    reg = dst[y0:y1, x0:x1]
    if shadow:
        sh = cv2.GaussianBlur(np.roll(np.roll(a[..., 0], int(18*lift), 0), int(12*lift), 1), (0, 0), 16*lift)
        reg = reg*(1 - shadow*sh[..., None])
    dst[y0:y1, x0:x1] = reg*(1 - a) + lay[..., :3]*a
    return M


@functools.lru_cache(maxsize=8)
def pin_sprite(color, r=30):
    """Канцелярская кнопка: шляпка с объёмом и бликом, тень на доске."""
    s = r*4
    yy, xx = np.mgrid[-s//2:s//2, -s//2:s//2].astype(np.float32)
    sh = np.exp(-(((xx - 14)**2 + (yy - 18)**2)/(2*(r*0.85)**2)))
    d = np.sqrt(xx**2 + yy**2)
    head = np.clip(r - d, 0, 1)
    rgb = np.array(PIN_COLORS[color], np.float32)*np.clip(1 - 0.55*(xx + yy)/(1.6*r), 0.45, 1.25)[..., None]
    hl = np.clip(1 - np.sqrt((xx + r*0.38)**2 + (yy + r*0.42)**2)/(r*0.32), 0, 1)
    rgb = rgb*(1 - 0.9*hl[..., None]) + 255*0.9*hl[..., None]
    rgb *= (1 - 0.35*np.clip(1 - np.abs(d - r*0.98)/2.0, 0, 1)*head)[..., None]
    return rgb, head, sh


def draw_pin(img, x, y, color, ox=0, oy=0):
    rgb, a, sh = pin_sprite(color)
    s = a.shape[0]
    x0, y0 = int(x - ox) - s//2, int(y - oy) - s//2
    if x0 < 0 or y0 < 0 or x0 + s > img.shape[1] or y0 + s > img.shape[0]:
        return
    reg = img[y0:y0 + s, x0:x0 + s]
    reg[:] = reg*(1 - 0.5*sh[..., None])
    reg[:] = reg*(1 - a[..., None]) + rgb*a[..., None]


def sag(a, b, k=0.07, n=160):
    """Нить провисает между кнопками."""
    (x0, y0), (x1, y1) = a, b
    L = np.hypot(x1 - x0, y1 - y0)
    t = np.linspace(0, 1, n)[:, None]
    mid = np.array([(x0 + x1)/2, (y0 + y1)/2 + k*L])
    return (1 - t)**2*np.array([x0, y0]) + 2*(1 - t)*t*mid + t**2*np.array([x1, y1])


def yarn(img, pts, ox, oy, u=1.0):
    """Витая красная нить: тень на доске, тёмная основа, светлые косые витки через 9 px."""
    k = max(2, int(len(pts)*u))
    p = pts[:k] - np.array([ox, oy])
    lay = np.zeros(img.shape[:2], np.float32)
    cv2.polylines(lay, [np.round((p + np.array([10, 14]))*4).astype(np.int32)], False, 1.0, 36, cv2.LINE_AA, shift=2)
    img *= (1 - 0.35*cv2.GaussianBlur(lay, (0, 0), 6)[..., None])
    q = np.round(p*4).astype(np.int32)
    cv2.polylines(img, [q], False, (120, 14, 18), 36, cv2.LINE_AA, shift=2)
    cv2.polylines(img, [q], False, (190, 32, 34), 24, cv2.LINE_AA, shift=2)
    d = np.diff(p, axis=0)
    seg = np.hypot(d[:, 0], d[:, 1])
    acc = np.concatenate([[0], np.cumsum(seg)])
    for s in np.arange(4, acc[-1], 9):
        i = int(np.searchsorted(acc, s)) - 1
        if 0 <= i < len(d) and seg[i] > 1e-6:
            x, y = p[i] + d[i]*(s - acc[i])/seg[i]
            tx, ty = d[i]/seg[i]
            a = ((x - 2.5*ty - 2*tx)*4, (y + 2.5*tx - 2*ty)*4)
            b = ((x + 2.5*ty + 2*tx)*4, (y - 2.5*tx + 2*ty)*4)
            cv2.line(img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), (232, 92, 88), 4, cv2.LINE_AA, shift=2)


# --- раскладка ------------------------------------------------------------------------------------------------------
def layout(n, bw, bh):
    """Центры карточек змейкой слева направо и места стикеров: над карточкой и в сторону от неё (у первой — влево,
    у остальных — вправо), чтобы нить шла над фото, а не по нему и не по подписи."""
    margin = 0.08*bw
    cards = [(margin + (k + 0.5)*(bw - 2*margin)/n, YS[k % len(YS)]*bh) for k in range(n)]
    notes = []
    for k, (x, y) in enumerate(cards):
        dx = -0.135*bw if k == 0 else 0.135*bw
        notes.append((float(np.clip(x + dx, 260, bw - 260)), float(np.clip(y - 0.19*bh, 230, bh - 230))))
    return cards, notes


class Board:
    """Доска одного плана: собирается один раз, кадр — Board.frame(t) в секундах от начала плана."""

    def __init__(self, spec, pictures, dur, seed=11):
        rng = np.random.default_rng(seed)
        self.spec, self.dur = spec, dur
        cards = spec["cards"]
        n = len(cards)
        self.bw, self.bh = board_size(n)
        board = cork(self.bw, self.bh, seed).astype(np.float32)
        pos, note_pos = layout(n, self.bw, self.bh)
        if spec.get("title"):
            put(board, note(spec["title"], (246, 243, 232), rng, w=760, h=330, size=96, under=True),
                0.135*self.bw, 0.11*self.bh, -2.0)
        if spec.get("page"):
            put(board, torn_page(spec["page"], rng), 0.41*self.bw, 0.78*self.bh, -4)
        self.cards, self.notes, self.pins = [], [], []
        rots = (-3.5, 2.5, -2.0, 3.0, -2.5)
        for k, (c, pic) in enumerate(zip(cards, pictures)):
            img, _ = polaroid(pic, c.get("caption", ""), rng)
            M = put(board, img, pos[k][0], pos[k][1], rots[k % len(rots)], lift=1.3)
            pin = tuple((M @ np.array([img.shape[1]/2, 30, 1.0])).tolist())
            self.cards.append(dict(at=pos[k], h=img.shape[0], pin=pin))
            self.pins.append((pin, "red"))
        for k, c in enumerate(cards):
            nt = c.get("note")
            if not nt:
                self.notes.append(None)
                continue
            img = note(nt["lines"], NOTE_COLORS.get(nt.get("color", "yellow"), NOTE_COLORS["yellow"]), rng,
                       circle=nt.get("circle"))
            M = put(board, img, note_pos[k][0], note_pos[k][1], (5, -6, 4, -5, 3)[k % 5])
            pin = tuple((M @ np.array([img.shape[1]/2, 34, 1.0])).tolist())
            self.notes.append(pin)
            self.pins.append((pin, NOTE_PINS[k % len(NOTE_PINS)]))
        if spec.get("page"):
            self.pins.append(((0.41*self.bw, 0.78*self.bh - 220), "green"))
        for k in range(1, min(3, n)):                                          # скотч на углах двух карточек
            corner = (0.05, 0.03) if k == 1 else (0.95, 0.02)
            x, y = self.cards[k]["at"]
            put(board, tape(rng), x + (corner[0] - 0.5)*CARD_W, y - self.cards[k]["h"]/2 + 12, 38 if k == 1 else -38,
                shadow=0.12, lift=0.3)
        self.board = np.clip(board, 0, 255).astype(np.uint8)
        self.chain = [sag(self.cards[k]["pin"], self.cards[k + 1]["pin"]) for k in range(n - 1)]
        self.branches = [None if p is None else sag(self.cards[k]["pin"], p, 0.03) for k, p in enumerate(self.notes)]
        # время: на карточку k камера приходит на её слове (t), переезд — TRAVEL до него, ужатый, если слова близко
        self.arrive = [float(c.get("t", 0.0 if k == 0 else k*2.2)) for k, c in enumerate(cards)]
        self.arrive[0] = 0.0
        ov = spec.get("overview_t")
        self.overview = float(ov) if ov is not None else min(dur - 0.5, self.arrive[-1] + 1.4)
        self.dof = _dof()

    def travel(self, k):
        """(начало, длина) переезда к карточке k (k = len(cards) — общий план)."""
        if k >= len(self.cards):
            return self.overview, min(TRAVEL, max(0.3, self.dur - self.overview))
        gap = self.arrive[k] - self.arrive[k - 1]
        d = min(TRAVEL, 0.6*gap)
        return self.arrive[k] - d, d

    def camera(self, t):
        stops = [(c["at"][0], c["at"][1] + 20, c["h"]/CARD_FILL) for c in self.cards]
        full = (self.bw/2, self.bh/2, float(self.bh))
        n = len(stops)
        for k in range(1, n + 1):
            t0, d = self.travel(k)
            if t < t0:
                return (*stops[k - 1], TILT if (k - 1) % 2 else -TILT, k - 1, None)
            if t < t0 + d:
                u = ease_io((t - t0)/d)
                a, b = stops[k - 1], (stops[k] if k < n else full)
                r0 = TILT if (k - 1) % 2 else -TILT
                r1 = 0.0 if k >= n else (TILT if k % 2 else -TILT)
                h = (a[2] + (b[2] - a[2])*u)*(1 + TRAVEL_LIFT*np.sin(np.pi*u))
                return a[0] + (b[0] - a[0])*u, a[1] + (b[1] - a[1])*u, h, r0 + (r1 - r0)*u, k - 1, (t - t0)/d
        return (*full, 0.0, n, None)

    def frame(self, t):
        cx, cy, h, rot, k, travel = self.camera(t)
        cx += SHAKE_PX[0]*_smooth(t, 1)
        cy += SHAKE_PX[1]*_smooth(t, 2)
        rot += SHAKE_DEG*_smooth(t, 3)
        m = 0.75*max(h*W/H, h)
        x0, y0 = int(max(0, cx - m)), int(max(0, cy - m))
        x1, y1 = int(min(self.bw, cx + m)), int(min(self.bh, cy + m))
        img = self.board[y0:y1, x0:x1].astype(np.float32)
        for j in range(min(k, len(self.chain))):
            yarn(img, self.chain[j], x0, y0)
        if travel is not None and k < len(self.chain):
            yarn(img, self.chain[k], x0, y0, min(1.0, ease_io(travel)*1.2))        # нить чуть обгоняет камеру
        for j, br in enumerate(self.branches):
            if br is None:
                continue
            since = t - self.arrive[j] - BRANCH_DELAY
            if k > j or since > 0:
                yarn(img, br, x0, y0, ease_io(1.0 if k > j and since > BRANCH_SEC else min(1.0, max(0.0, since)/BRANCH_SEC)))
        for (px, py), col in self.pins:
            draw_pin(img, px, py, col, x0, y0)
        s = H/h
        M = cv2.getRotationMatrix2D((cx - x0, cy - y0), rot, s)
        M[0, 2] += W/2 - (cx - x0)
        M[1, 2] += H/2 - (cy - y0)
        out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REFLECT)
        blur = cv2.GaussianBlur(out, (0, 0), DOF_SIGMA if travel is None else DOF_SIGMA_TRAVEL)
        return out*(1 - self.dof[..., None]) + blur*self.dof[..., None]


def _smooth(t, seed, f=0.6):
    ph = np.random.default_rng(seed).uniform(0, 6.28, 3)
    return sum(np.sin(2*np.pi*f*m*t + ph[i])/m for i, m in enumerate((1, 2.3, 4.1)))


@functools.lru_cache(maxsize=1)
def _dof():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W/2)/(W*0.62))**2 + ((yy - H/2)/(H*0.62))**2)
    return (np.clip((r - DOF_SHARP)/(1 - DOF_SHARP), 0, 1)**1.4).astype(np.float32)


def times(spec, word_time, t0):
    """Карточка k: камера приходит на её слове (поле t, от начала плана); общий план — overview_t."""
    for k, c in enumerate(spec["cards"]):
        c["t"] = 0.0 if k == 0 or not c.get("at") else max(0.0, word_time(c["at"]) - t0)
    if spec.get("overview_at"):
        spec["overview_t"] = max(0.0, word_time(spec["overview_at"]) - t0)
    return spec


def beats(spec):
    """Моменты на экране: приход на каждую карточку и начало общего плана."""
    out = [c["t"] for c in spec["cards"] if "t" in c]
    if spec.get("overview_t") is not None:
        out.append(spec["overview_t"])
    return sorted(out)


def sounds(spec):
    """Звук движения — в середине каждого переезда (к карточке и на общий план)."""
    out = []
    cards = spec["cards"]
    for k in range(1, len(cards)):
        if "t" in cards[k] and "t" in cards[k - 1]:
            d = min(TRAVEL, 0.6*(cards[k]["t"] - cards[k - 1]["t"]))
            out.append((cards[k]["t"] - d/2, cards[k].get("sound", "fast_whoosh"), f"нить к карточке «{cards[k].get('caption', '')}»"))
    if spec.get("overview_t") is not None:
        out.append((spec["overview_t"] + TRAVEL/2, spec.get("overview_sound", "swoosh_deep"), "вся доска"))
    return out
