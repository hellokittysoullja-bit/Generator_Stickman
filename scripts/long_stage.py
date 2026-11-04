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
VERSION = 4              # смена вида — смена подписи клипа (3: вырезка SAM + край по туши; 4: стикеры, 04.11)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BG = None


def ease_io(u):
    u = min(1.0, max(0.0, u))
    return u*u*(3 - 2*u)


def ease_out(u):
    u = min(1.0, max(0.0, u))
    return 1 - (1 - u)**3


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


# --- вырезка предмета: SAM по рамке + край по туши (владелец 04.11: «обрезается без каких-либо других объектов») -----
# Замер на пяти трудных местах L03 (песочные часы с лапой кота сверху, ноутбук рядом с котом, аквариум на табурете,
# кружка на столе, кот с телефоном рядом с конвертом): BiRefNet по рамке брал соседей — лапу, шерсть, линию стола, дым —
# и пробивал дыры в стекле; SAM, которому указан предмет, соседей не берёт, но рвёт контур и захватывает просветы
# бумаги. Край по туши чинит это правилами рисунка на бумаге (refine). Остаток: тонкие детали, которые SAM срезал
# сильнее 2 px (верх ручки кружки), не возвращаются.
SAM_BAND = 2          # тушь у края маски SAM, которая возвращается предмету: SAM срезает контур на 1–2 px
PAPER_TONE_TOL = 4    # область внутри предмета может быть фоном, только если её тон — тон бумаги снаружи (±4)…
SOLID_BRIDGE = 7      # "solid": щели до 14 px в контуре сплошного предмета закрываются (правая страница книги L03)
COLOUR_SAT = 90       # цветное — насыщенность выше этого (огонёк ~200, серая тушь и бумага < 40)
ATTACH_MAX = 0.15     # присоединяется цветная часть меньше 15 % предмета
HOLE_SAM_MAX = 0.08   # …и SAM покрыл её меньше чем на 8 % (просвет ручки 0,0; страница книги 0,14)
SEAL = 4              # разрыв линии до 2·SEAL px считается закрытым (замер: страницы книги L03, фраза 7)
SAM_TIMEOUT = 300     # на картинку: загрузка модели ~12 с и ~5 с на маску на четырёх ядрах


def _sam_job(path, box, point):
    """Две маски — по рамке и по рамке с точкой (SAM из rembg, ~4 ГБ памяти)."""
    from rembg import new_session, remove
    sess = new_session("sam")
    img = Image.open(path).convert("RGB")
    out = []
    for prompt in ([{"type": "rectangle", "data": list(box), "label": 1}],
                   [{"type": "rectangle", "data": list(box), "label": 1},
                    {"type": "point", "data": list(point), "label": 1}]):
        out.append((np.asarray(remove(img, session=sess, only_mask=True, sam_prompt=prompt)) > 127).astype(np.uint8))
    return out


def _sam_masks(path, box, point):
    """SAM в отдельном процессе обычным запуском этого файла: память отпускается сразу, и нет multiprocessing,
    который зависает, когда главный скрипт не файл (тест, stdin)."""
    import subprocess
    import sys
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "m.npz")
        subprocess.run([sys.executable, os.path.abspath(__file__), "--sam", path, json.dumps(list(box)),
                        json.dumps(list(point)), out], check=True, timeout=SAM_TIMEOUT, capture_output=True)
        z = np.load(out)
        return [z["a"], z["b"]]


def sam_close():
    """Совместимость: SAM живёт в своём подпроцессе и уходит вместе с ним."""
    return None


def _bbox_iou(m, box):
    ys, xs = np.nonzero(m)
    if not len(ys):
        return 0.0
    b = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    ix = max(0, min(b[2], box[2]) - max(b[0], box[0]))
    iy = max(0, min(b[3], box[3]) - max(b[1], box[1]))
    inter = ix*iy
    return inter/((b[2] - b[0])*(b[3] - b[1]) + (box[2] - box[0])*(box[3] - box[1]) - inter)


def pick_mask(masks, box):
    """Из масок SAM — та, что лучше заполняет рамку; при равных рамках — сплошная (по одной рамке SAM терял стекло
    песочных часов: 45 тыс. пикселей против 60 тыс.)."""
    scored = [(round(_bbox_iou(m, box), 2), int(m.sum()), k) for k, m in enumerate(masks)]
    return masks[max(scored)[2]]


def _fill_holes(m):
    h, w = m.shape
    ff = m.copy()
    cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 1)
    return m | (1 - ff)


def ink_map(img):
    """Что нарисовано на бумаге: тушь (тёмное) и цветная заливка."""
    img = np.clip(img, 0, 255).astype(np.uint8)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return ((g < 205) | (hsv[..., 1] > 60)).astype(np.uint8)


def refine(img, sam, band=SAM_BAND, solid=False):
    """Маска SAM -> предмет рисунка на бумаге (float 0..1).
    1. Маска SAM и тушь в узкой полосе у её края (контур, который SAM срезал).
    2. Бумага, до которой можно дойти от края картинки, не переступая туши (щели в линии до 2·SEAL px закрыты), — фон, даже
       если SAM её захватил (просвет между хвостом и телом), и кайма бумаги у контура тоже.
    3. Закрытая линиями область внутри предмета — его поверхность (страница, экран, стекло, заливка ручки). Фоном,
       видным сквозь предмет (просвет ручки), она считается, только если и тон — бумага снаружи, и SAM её не покрыл;
       такой просвет уходит вместе с тонкими линиями фона в нём (стол за ручкой).
    solid=True (элемент сцены "solid") — предмет сплошной по смыслу: закрытые контуром области заливаются целиком
       (страница книги, которую SAM не покрыл, а контур открыт шире SEAL).
    Цветная часть, касающаяся предмета и меньше его (огонёк на хвосте), присоединяется к нему.
    4. Остаётся одна связная часть, пересекающая ядро SAM."""
    m = (sam > 0).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*band + 1, 2*band + 1))
    zone, core = cv2.dilate(m, k), cv2.erode(m, k)
    ink = ink_map(img)
    obj = ((m > 0) | ((zone - core > 0) & (ink > 0))).astype(np.uint8)
    # разрывы в линии рисунка (контур книги, кружки) до SEAL px закрываются только для поиска внешней бумаги: иначе
    # бумага снаружи затекала на страницы книги; широкий просвет (между хвостом и телом) остаётся открытым
    seal = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*SEAL + 1, 2*SEAL + 1))
    paper = (1 - cv2.dilate(ink, seal)).astype(np.uint8)
    _, lab = cv2.connectedComponents(paper, 4)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    outside = np.isin(lab, border[border > 0]).astype(np.uint8)
    obj &= 1 - (cv2.dilate(outside, seal) & (1 - ink))
    g = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    tone = float(np.median(g[outside > 0])) if outside.any() else 245.0
    inner = paper & (1 - outside) & _fill_holes(zone)        # и большие дыры SAM посреди предмета (страницы книги)
    ni, il, ist, _ = cv2.connectedComponentsWithStats(inner, 4)
    area = max(1, int(obj.sum()))
    for j in range(1, ni):
        hole = il == j
        # фон, видный сквозь предмет (просвет ручки), уходит, только когда об этом говорят оба признака: тон той же
        # бумаги, что снаружи, и SAM его почти не покрыл. Замер L03: просвет ручки — тон 253 при 253, SAM 0,0;
        # страница книги — тон 245 при бумаге 246 (тоном не отличить), SAM 0,14; поверхность предмета остаётся
        background = abs(g[hole].mean() - tone) <= PAPER_TONE_TOL and m[hole].mean() < HOLE_SAM_MAX
        if not background or ist[j, cv2.CC_STAT_AREA] < 0.004*area:
            obj[hole] = 1
            continue
        gone = cv2.morphologyEx(hole.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
        obj[gone > 0] = 0
    if solid:          # предмет сплошной по смыслу (открытая книга, экран): всё, что внутри его контура, — его
        close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*SOLID_BRIDGE + 1, 2*SOLID_BRIDGE + 1))
        near = cv2.dilate(zone, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))   # контур, который SAM недобрал
        edge = ink & near & (1 - obj)
        closed = cv2.morphologyEx(obj | edge, cv2.MORPH_CLOSE, close)
        full = _fill_holes(closed)
        filled = cv2.dilate(full & (1 - closed), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
        ne, el = cv2.connectedComponents(edge, 8)                   # линия у края, которая ничего не замкнула
        stray = edge & ~np.isin(el, np.unique(el[(filled > 0) & (edge > 0)]))   # (спинка стула), — соседу
        deep = cv2.erode(full, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*SOLID_BRIDGE + 3, 2*SOLID_BRIDGE + 3)))
        obj = obj | (full & (1 - closed)) | (closed & deep) | (edge & (1 - stray.astype(np.uint8)))
        # закрытие разрывов у внешнего края не берётся: там оно ловит бумагу между прядями шерсти (крупинки у головы)
    # цветная часть, которая касается предмета и меньше его, — его (огонёк на хвосте: SAM считает его отдельным);
    # серые линии соседей так не присоединяются
    hsv = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    colour = ((hsv[..., 1] > COLOUR_SAT) & (hsv[..., 2] > 60)).astype(np.uint8) & (1 - obj)
    nc, cl, cst, _ = cv2.connectedComponentsWithStats(colour, 8)
    touch = np.unique(cl[(cv2.dilate(obj, np.ones((7, 7), np.uint8)) > 0) & (colour > 0)])
    area = max(1, int(obj.sum()))
    for j in touch[touch > 0]:
        if cst[j, cv2.CC_STAT_AREA] < ATTACH_MAX*area:
            piece = (cl == j).astype(np.uint8)
            obj |= cv2.morphologyEx(piece | (ink & cv2.dilate(piece, np.ones((7, 7), np.uint8))), cv2.MORPH_CLOSE,
                                    np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(obj, 8)
    keep = np.unique(lab[(core > 0) & (obj > 0)])
    keep = keep[keep > 0]
    if len(keep):
        obj = (lab == keep[np.argmax(st[keep, cv2.CC_STAT_AREA])]).astype(np.uint8)
    return cv2.GaussianBlur(obj.astype(np.float32), (0, 0), 0.7)


def _sam_object(path, img, box, point=None, solid=False):
    """Маска предмета в рамке: SAM (в своём процессе) + край по туши; без SAM — None (вызывающий берёт BiRefNet)."""
    point = point or ((box[0] + box[2])//2, (box[1] + box[3])//2)
    try:
        masks = _sam_masks(path, box, point)
    except Exception as e:                           # нет модели, нет памяти — прежний способ, не падение сборки
        print(f"  вырезка {os.path.basename(path)}: SAM не сработал ({e}) — BiRefNet по рамке")
        return None
    m = pick_mask(masks, box)
    if not m.any():
        return None
    return refine(img, m, solid=solid)


def cutout(path, box=None, poly=None, cache_dir=None, point=None, solid=False):
    """RGBA-вырезка предмета (uint8). poly — многоугольник по сетке рисунка; иначе box (+ по желанию point — точка на
    предмете): SAM по рамке и край по туши (refine), запасной путь — BiRefNet по рамке и самый большой кусок.
    Кэш — по файлу, рамке, точке и версии."""
    key = hashlib.sha256(json.dumps([os.path.basename(path), os.path.getsize(path), box, poly, point, solid,
                                     VERSION]).encode()).hexdigest()[:16]
    cp = os.path.join(cache_dir, f"cut_{key}.png") if cache_dir else None
    if cp and os.path.exists(cp):
        return np.asarray(Image.open(cp).convert("RGBA"))
    img = _paper_like(np.asarray(Image.open(path).convert("RGB"), np.float32))
    if poly:
        m = np.zeros(img.shape[:2], np.uint8)
        cv2.fillPoly(m, [np.int32(poly)], 1)
        m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.0)
    elif box and (sm := _sam_object(path, np.asarray(Image.open(path).convert("RGB")), box, point, solid)) is not None:
        m = sm
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


# --- стикеры (владелец 04.11, пробник 1: «первое берём… уже нормально») ----------------------------------------------
STICKER_BORDER = 0.055    # белая обводка — доля высоты вырезки
SLAP_SEC = 0.20           # стикер шлёпается на бумагу: сверху и крупнее (1.25 → 1 с перелётом), тень растёт
BOIL_FPS = 12             # «живая» бумага: после посадки стикер чуть дрожит 12 раз в секунду, как рисованная анимация
BOIL_PX, BOIL_DEG = 1.6, 0.45
STICKER_ROT = (-4.0, 3.0, -2.5)   # стикеры наклеены не по линейке


def sticker(rgba):
    """Вырезка -> стикер: белая скруглённая обводка по контуру."""
    rgba = np.asarray(rgba, np.float32)
    r = max(6, int(rgba.shape[0]*STICKER_BORDER))
    pad = r + 4
    a = np.pad(rgba[..., 3], pad)/255.0
    rgb = np.pad(rgba[..., :3], ((pad, pad), (pad, pad), (0, 0)), constant_values=255)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r + 1, 2*r + 1))
    border = cv2.GaussianBlur(cv2.dilate((a > 0.5).astype(np.uint8), k).astype(np.float32), (0, 0), 1.2)
    out = rgb*a[..., None] + np.array([255, 254, 250], np.float32)*(1 - a[..., None])
    return np.dstack([out, np.maximum(a, border)*255]).astype(np.float32)


def boil(t, k):
    """Дрожь стикера k: новое смещение и поворот каждые 1/BOIL_FPS с, у каждого своё."""
    rng = np.random.default_rng(1000*k + int(t*BOIL_FPS))
    return rng.uniform(-BOIL_PX, BOIL_PX), rng.uniform(-BOIL_PX, BOIL_PX), rng.uniform(-BOIL_DEG, BOIL_DEG)


class Stage:
    """Сцена плана: assets — RGBA элементов, времена — от начала плана (с)."""

    def __init__(self, spec, assets, dur):
        import long_fx
        self.spec, self.dur = spec, dur
        self.assets = [sticker(a) for a in assets] if spec["type"] == "items" else assets
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
                u = t - it["t"]
                land = min(1.0, u/SLAP_SEC)                       # шлепок: сверху и крупнее, с перелётом
                sc = 1.25 - 0.25*back_out(land, 2.2)
                bx, by, br = boil(t, k) if land >= 1 else (0.0, 0.0, 0.0)
                h = H*it.get("h", ITEM_H if n > 2 else 0.58)
                f = place(f, self.assets[k], self.xs[k] + dx + bx,
                          H*(0.50 if n > 2 else 0.56) - 30*(1 - ease_out(land)) + by, h*sc,
                          alpha=min(1.0, u/0.06), rot=STICKER_ROT[k % len(STICKER_ROT)] + br, shadow=land > 0.5)
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


if __name__ == "__main__" and len(__import__("sys").argv) == 6 and __import__("sys").argv[1] == "--sam":
    import sys
    _a, _b = _sam_job(sys.argv[2], json.loads(sys.argv[3]), json.loads(sys.argv[4]))
    np.savez_compressed(sys.argv[5], a=_a, b=_b)
