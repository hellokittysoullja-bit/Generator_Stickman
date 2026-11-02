"""Заливка дыры под вырезанным предметом на акварельном рисунке — основная для новых сцен (владелец 02.11, лист
«было/стало»: «вообще идеально стало»; прежняя anim.fill_hole оставляла силуэт предмета рельефом и рвала плинтус).

inpaint(img, hole) -> img (float32 RGB 0..255, тот же размер); cached(img, hole, cache_dir) — то же с кэшем на диске
(LaMa ~3 с на свободной машине, считается один раз на рисунок). Сцены зовут anim.inpaint_bg.

Шаги (каждый — против конкретного брака прежней заливки, разбор 02.11):
1. halo(): маска растёт на «ореол» предмета — свечение огонька, дым, мягкую дымку у края: мягкие (без резкого края)
   пятна темнее или теплее бумаги, связанные с дырой и не уходящие далеко. Пятно, которое тянется дальше reach, —
   часть сцены (пол, дверца, тень пола), его не трогаем. Тушь (резкий край) рост не пропускает.
2. LaMa 512 на квадратном кропе вокруг дыры: структура — продолжение линий пола, плинтуса, рамок; цвет соседнего
   предмета в дыру не тянется (гладкое продолжение нормированной свёрткой тянуло).
3. tone_fix(): у LaMa свой тон и уровень (уменьшение-увеличение кропа): разность «исходник - LaMa» на спокойном
   кольце у края дыры плавно вносится внутрь — тон на границе совпадает с соседним.
   flatten(): собственная «фактура» сети (нарисована на сжатом кропе, после увеличения — крупные пятна) гасится
   билатеральным фильтром; линии сети остаются, чуть подтягиваются по резкости и теряют бурый оттенок.
4. grain(): зерно — кусками чистой бумаги этого же рисунка (только бумага своего цвета), смешанными окнами Ханна
   с сохранением дисперсии (Heitz & Neyret 2018): без швов плиток и без отражений; сила — по трём полосам частот,
   до МЕСТНОЙ силы бумаги вокруг (стена, пол, косяк зернятся по-разному).
5. Дыра больше 2×512 (кадры ×2): всё на копии, уменьшенной в k раз, обратно — увеличением, зерно — в полном размере.
Модель: Carve/LaMa-ONNX lama_fp32.onnx (208 МБ, вход 512×512 фиксирован), путь — переменная LAMA_ONNX.
"""
import os
import numpy as np
import cv2

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LAMA_ONNX = os.environ.get("LAMA_ONNX", os.path.join(ROOT, "models", "lama_fp32.onnx"))     # models/ — не в git
LAMA_URL = "https://huggingface.co/Carve/LaMa-ONNX/resolve/main/lama_fp32.onnx"              # Apache-2.0
LAMA_SHA256 = "1faef5301d78"                                                                 # начало sha256
LAMA_SIZE = 512                 # вход модели Carve/LaMa-ONNX фиксирован
CROP_MARGIN = 1.5               # сторона кропа = 1.5 × большая сторона дыры: контекст для линий
SHARPEN = 0.6                   # нерезкая маска линий сети (синтетика: 0 — линии 0.90–0.98, 0.6 — 0.91–0.99, 1.2 — ΔE хуже)
BANDS = (1.2, 3.0, 7.0)         # полосы зерна: σ разностей гауссиан (мелкое зерно, фактура, акварельные пятна)
_SESS = {}


def _lab(img):
    return cv2.cvtColor(np.clip(img, 0, 255).astype(np.float32) / 255, cv2.COLOR_RGB2LAB)


def _nfill(x, valid, sig):
    """Нормированная свёртка: среднее x по valid с гауссовым весом σ=sig. Большая σ — на уменьшенной копии
    (результат гладкий, а размытие с ядром в сотни пикселей на полном кадре стоило секунды)."""
    if sig > 8:
        f = sig / 4.0; H, W = valid.shape; h, w = max(1, int(round(H / f))), max(1, int(round(W / f)))
        xs = cv2.resize(x * (valid[..., None] if x.ndim == 3 else valid), (w, h), interpolation=cv2.INTER_AREA)
        vs = cv2.resize(valid.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
        num = cv2.GaussianBlur(xs, (0, 0), 4.0); den = cv2.GaussianBlur(vs, (0, 0), 4.0)
        num = cv2.resize(num, (W, H), interpolation=cv2.INTER_LINEAR); den = cv2.resize(den, (W, H), interpolation=cv2.INTER_LINEAR)
        return num / np.maximum(den if x.ndim == 2 else den[..., None], 1e-6), den
    v = valid.astype(np.float32)
    if x.ndim == 3: num = cv2.GaussianBlur(x * v[..., None], (0, 0), sig)
    else: num = cv2.GaussianBlur(x * v, (0, 0), sig)
    den = cv2.GaussianBlur(v, (0, 0), sig)
    return num / np.maximum(den if x.ndim == 2 else den[..., None], 1e-6), den


def _calm(L, win=7, thr=1.2):
    """Спокойная бумага: малый локальный разброс светлоты (L в 0..100)."""
    m = cv2.blur(L, (win, win)); v = cv2.blur(L * L, (win, win)) - m * m
    return np.sqrt(np.clip(v, 0, None)) < thr


def halo(img, hole, reach=None, t_dark=2.5, t_warm=3.0, t_edge=2.2):
    """Ореол предмета вокруг дыры: свечение, дым, дымка. Возвращает расширенную дыру (bool)."""
    hole = hole.astype(bool); H, W = hole.shape
    if reach is None:
        reach = int(np.clip(0.25 * np.sqrt(hole.sum()), 20, 160))
    lab = cv2.GaussianBlur(_lab(img), (0, 0), 1.5); L = lab[..., 0]
    dist = cv2.distanceTransform((~hole).astype(np.uint8), cv2.DIST_L2, 5)
    # опора — бумага дальше reach (там ореола нет), вносится внутрь гладко
    ref_ok = (dist > reach) & _calm(L, 9, 2.0)
    ref, den = _nfill(lab, ref_ok, reach * 0.75)
    if (den[dist <= reach] < 1e-3).mean() > 0.5:
        return hole
    gy, gx = np.gradient(L); grad = np.hypot(gx, gy)
    # тушь соседних предметов (резкий край или сильно темнее бумаги) — рост через неё и рядом с ней запрещён:
    # мягкая тень у края дверцы или плинтуса — их, а не ореол (первая версия съедала полосу плинтуса и край двери)
    ink_core = ((ref[..., 0] - L) > 25) | (grad > 6 * t_edge)
    ink = cv2.dilate(ink_core.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    warm = (lab[..., 2] - ref[..., 2] > t_warm) | (lab[..., 1] - ref[..., 1] > t_warm)
    # дым и дымка — тонкие тёмные пятна (уже ~2·k): «чёрная шляпа» по светлоте; широкая полоса (плинтус, пол,
    # тень на полу) ей не видна — это сцена
    k = 2 * max(7, reach // 8) + 1
    bh = cv2.morphologyEx(L, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))) - L
    dark = bh > t_dark
    cand = ((warm & ~cv2.dilate(ink_core.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)) | (dark & (grad < t_edge) & ~ink)) \
        & (dist <= reach) & ~hole
    n, lab_c, st, _ = cv2.connectedComponentsWithStats(cand.astype(np.uint8), connectivity=8)
    touch = np.zeros(n, bool)
    ring = (dist > 0) & (dist <= 3)
    touch[np.unique(lab_c[ring & cand])] = True
    far = np.bincount(lab_c[cand & (dist > 0.8 * reach)].ravel(), minlength=n)
    area = np.bincount(lab_c[cand].ravel(), minlength=n)
    keep = touch & (far <= 0.02 * np.maximum(area, 1)) & (area >= 30)
    # штрих сцены (линия пола, край двери, плинтус), даже бледный и короткий (кусок плинтуса между дырой и краем
    # кадра — синтетика 02.11): вытянутый кусок, продолжение которого по его оси за дырой или дальше — такая же
    # тёмная линия. У дыма и свечения продолжения нет.
    dkd = cv2.dilate((bh > t_dark).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0   # линия «дрожит» на 1–2 px
    _, _, bw, bh_ = cv2.boundingRect(hole.astype(np.uint8)); diag = float(np.hypot(bw, bh_))
    for i in np.nonzero(keep)[0]:
        x, y, w, h = st[i, :4]
        ys, xs = np.nonzero(lab_c[y:y + h, x:x + w] == i)
        if len(ys) < 3: continue
        P = np.stack([xs + x, ys + y]).astype(np.float64)
        ev, evec = np.linalg.eigh(np.cov(P))
        if ev[1] <= 0: continue
        if np.sqrt(ev[1]) > 12 and np.sqrt(max(ev[0], 0) / ev[1]) < 0.15:     # длинный прямой — сразу сцена
            keep[i] = False; continue
        if np.sqrt(max(ev[0], 0) / ev[1]) > 0.35: continue
        u = evec[:, 1]; c0 = P.mean(1); half = 2 * np.sqrt(ev[1])
        span = half + 3 * reach + diag                   # за дырой: линия продолжается на другой её стороне
        tt = np.concatenate([np.arange(half + 4, span, 2.0), -np.arange(half + 4, span, 2.0)])
        sx = np.round(c0[0] + tt * u[0]).astype(int); sy = np.round(c0[1] + tt * u[1]).astype(int)
        ok = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
        sx, sy = sx[ok], sy[ok]
        ok = ~hole[sy, sx]
        if ok.sum() < 10: continue
        cont = dkd[sy[ok], sx[ok]].mean()             # замер 02.11: линии сцены 0.44–0.82, дым и дымка 0.03–0.29
        if cont > 0.5 or (cont > 0.3 and np.sqrt(max(ev[0], 0) / ev[1]) < 0.15):
            keep[i] = False
    aura = keep[lab_c] & cand
    aura = cv2.morphologyEx(aura.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    aura = cv2.dilate(aura, np.ones((5, 5), np.uint8)) > 0       # мягкий край ореола — тоже его
    grown = hole | (aura & ~ink_core)
    # мелкие острова бумаги, окружённые дырой, — тоже в дыру (иначе останется «пятнышко» старого)
    inv = (~grown).astype(np.uint8)
    n, lb, st, _ = cv2.connectedComponentsWithStats(inv, connectivity=4)
    small = np.zeros(n, bool); small[1:] = st[1:, cv2.CC_STAT_AREA] < 400
    # кусок у края кадра — не остров (полоса плинтуса между дырой и краем, синтетика 02.11)
    edge = np.unique(np.concatenate([lb[0], lb[-1], lb[:, 0], lb[:, -1]])); small[edge] = False
    return grown | small[lb]


def _model():
    """Модель на диске: нет — скачать один раз и сверить sha256."""
    if not os.path.exists(LAMA_ONNX):
        import hashlib
        import urllib.request
        os.makedirs(os.path.dirname(LAMA_ONNX), exist_ok=True)
        urllib.request.urlretrieve(LAMA_URL, LAMA_ONNX + ".part")
        h = hashlib.sha256(open(LAMA_ONNX + ".part", "rb").read()).hexdigest()
        if not h.startswith(LAMA_SHA256):
            os.remove(LAMA_ONNX + ".part")
            raise RuntimeError(f"LaMa: sha256 {h[:12]} не совпал с {LAMA_SHA256}")
        os.replace(LAMA_ONNX + ".part", LAMA_ONNX)
    return LAMA_ONNX


def _session():
    if "lama" not in _SESS:
        import onnxruntime as ort
        so = ort.SessionOptions(); so.intra_op_num_threads = os.cpu_count() or 4
        _SESS["lama"] = ort.InferenceSession(_model(), so, providers=["CPUExecutionProvider"])
    return _SESS["lama"]


def lama_crop(img, hole, margin=CROP_MARGIN):
    """LaMa на квадратном кропе вокруг дыры. Возвращает (кроп-результат в полном разрешении, x0, y0, side)."""
    H, W = hole.shape; R = LAMA_SIZE
    x, y, w, h = cv2.boundingRect(hole.astype(np.uint8))
    side = int(min(max(max(w, h) * margin, R), min(W, H)))
    cx, cy = x + w / 2, y + h / 2
    x0 = int(min(max(cx - side / 2, 0), W - side)); y0 = int(min(max(cy - side / 2, 0), H - side))
    c = img[y0:y0 + side, x0:x0 + side]
    ci = cv2.resize(c, (R, R), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    cm = (cv2.resize(hole[y0:y0 + side, x0:x0 + side].astype(np.float32), (R, R), interpolation=cv2.INTER_AREA) > 0.01).astype(np.float32)
    ci *= 1 - cm[..., None]
    o = _session().run(None, {"image": ci.transpose(2, 0, 1)[None], "mask": cm[None, None]})[0][0].transpose(1, 2, 0)
    if o.max() <= 1.5: o = o * 255
    return cv2.resize(o, (side, side), interpolation=cv2.INTER_CUBIC), x0, y0, side


def tone_fix(orig, net, hole, width=12, sig=10):
    """Сдвиг тона заливки к соседней бумаге: разность «исходник − сеть» на спокойном кольце снаружи дыры вносится
    внутрь; у края — местная (σ=sig), к середине — всё более общая (3σ, 9σ). Не гаснет к середине: у LaMa сдвиг
    общий (замер на двери: середина на 5 уровней светлее стены), первая версия с затуханием оставляла светлое пятно."""
    L = _lab(orig)[..., 0]
    ring = (cv2.dilate(hole.astype(np.uint8), np.ones((2 * width + 1,) * 2, np.uint8)) > 0) & ~hole & _calm(L, 7, 1.5)
    d = orig - net
    off = np.zeros_like(orig)
    left = hole.copy()
    for s in (sig, 3 * sig, 9 * sig, 27 * sig):
        f, den = _nfill(d, ring, s)
        ok = left & (den > 0.05)
        off[ok] = f[ok]; left &= ~ok
    off = cv2.GaussianBlur(off, (0, 0), sig / 2)      # без ступенек между масштабами
    return net + off


def flatten(net, scale):
    """Убрать собственную «фактуру» сети: она нарисована на кропе, сжатом в scale раз, и после увеличения выходит
    крупными пятнами (дверь: средние частоты ×1.6–2 к бумаге). Билатеральный фильтр гасит колебания до ~8 уровней,
    линии туши (перепад 20+) остаются."""
    net = net.astype(np.float32)
    out = net
    for _ in range(2):
        out = cv2.bilateralFilter(out, 0, 8.0, max(2.0, 1.5 * scale))
    # линии сети — как есть: бледная линия плинтуса (перепад ~10–15) билатеральным фильтром тоже съедалась
    # (синтетика «плинтус»: сохранность линии 0.99 → 0.76)
    # и вернуть им резкость: после увеличения кропа в scale раз линия шире и бледнее, чем та же линия рядом
    # (дверь ×1: линия пола в дыре бледнее, ×2 — размыта). Нерезкая маска только по линиям; пересвет по бокам
    # срезается по бумаге вокруг (закрытие), чтобы у линии не было светлого ореола
    r = int(np.ceil(scale))
    sig = max(0.7, 0.6 * scale)
    sharp = net + SHARPEN * (net - cv2.GaussianBlur(net, (0, 0), sig))
    paper = cv2.morphologyEx(net, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4 * r + 1, 4 * r + 1)))
    sharp = np.clip(np.minimum(sharp, paper), 0, 255)
    ln = cv2.dilate(_lines(net.mean(2)).astype(np.uint8), np.ones((2 * r + 1,) * 2, np.uint8))
    # цвет линии — оттенок бумаги вокруг, как у туши рисунка: сеть подкрашивает тонкие линии в бурый
    # (только тонкие тёмные штрихи; край заливки другого цвета — бок холодильника — свой цвет держит)
    gn = net.mean(2)
    thin = cv2.morphologyEx(gn, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4 * r + 3,) * 2)) > 8
    thin = cv2.GaussianBlur(cv2.dilate(thin.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 1.0)[..., None]
    lab = _lab(sharp); ab, _ = _nfill(lab[..., 1:], ln == 0, 4.0)
    neutral = np.clip(cv2.cvtColor(np.dstack([lab[..., :1], ab]).astype(np.float32), cv2.COLOR_LAB2RGB) * 255, 0, 255)
    sharp = neutral * thin + sharp * (1 - thin)
    keep = cv2.GaussianBlur(ln.astype(np.float32), (0, 0), 1.5)[..., None]
    return sharp * keep + out * (1 - keep)


def _bands(x):
    out, prev = [], x
    for s in BANDS:
        b = cv2.GaussianBlur(x, (0, 0), s); out.append(prev - b); prev = b
    return out


def _mad(v):
    return 1.4826 * float(np.median(np.abs(v - np.median(v)))) if v.size else 0.0


def stationary_grain(src, clean, box, T=48, seed=7):
    """Зерно в рамке box=(x0,y0,x1,y1): случайные куски src с чистой бумаги, окна Ханна с перекрытием 50 %,
    сумма делится на sqrt(Σw²) — дисперсия ровная, швов нет, отражений нет."""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0; H, W = clean.shape
    e = cv2.erode(clean.astype(np.uint8), np.ones((T, T), np.uint8), borderType=cv2.BORDER_CONSTANT, borderValue=0)
    e[:T // 2 + 1] = 0; e[H - T // 2 - 1:] = 0; e[:, :T // 2 + 1] = 0; e[:, W - T // 2 - 1:] = 0
    ys, xs = np.nonzero(e)
    if len(ys) == 0:
        return None
    rng = np.random.default_rng(seed)
    win1 = np.sin(np.pi * (np.arange(T) + 0.5) / T) ** 2
    win = np.outer(win1, win1)[..., None].astype(np.float32)
    acc = np.zeros((h + 2 * T, w + 2 * T, src.shape[2]), np.float32); w2 = np.zeros((h + 2 * T, w + 2 * T, 1), np.float32)
    for yy in range(0, h + T, T // 2):
        for xx in range(0, w + T, T // 2):
            k = int(rng.integers(len(ys))); cy, cx = ys[k] - T // 2, xs[k] - T // 2
            acc[yy:yy + T, xx:xx + T] += win * src[cy:cy + T, cx:cx + T]
            w2[yy:yy + T, xx:xx + T] += win * win
    g = acc / np.sqrt(np.maximum(w2, 1e-6))
    return g[T:T + h, T:T + w]


def _lines(g):
    """Линии и края рисунка (серый 0..255): тёмный тонкий штрих или резкий перепад, с запасом."""
    bh = cv2.morphologyEx(g, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    gy, gx = np.gradient(cv2.GaussianBlur(g, (0, 0), 1.5))
    return cv2.dilate(((bh > 8) | (np.hypot(gx, gy) > 6)).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0


def grain(orig, fill, hole, seed=7, sig_local=40):
    """Зерно бумаги в дыру: по каждой полосе частот до МЕСТНОЙ силы бумаги вокруг (стена, пол и косяк зернятся по-
    разному: общая цель по кольцу давала на стене двери зерно ×1.6–2)."""
    hole = hole.astype(bool)
    g = orig.mean(2).astype(np.float32)
    x, y, w, h = cv2.boundingRect(hole.astype(np.uint8))
    ln = _lines(g); hl = hole.astype(np.uint8)
    paper = ~ln & ~(cv2.dilate(hl, np.ones((15, 15), np.uint8)) > 0)
    # источник зерна — только бумага своего цвета: в кусок со свечением огонька зерно уносило тёплое пятнышко
    if paper.sum() < 2000:
        return fill
    ab = _lab(orig)[..., 1:]
    med = np.median(ab[paper], axis=0)
    src_ok = paper & (np.hypot(ab[..., 0] - med[0], ab[..., 1] - med[1]) < 4)
    src = orig - cv2.GaussianBlur(orig, (0, 0), BANDS[-1])
    gr = stationary_grain(src, src_ok, (x, y, x + w, y + h), seed=seed)
    if gr is None:
        return fill
    hs = hole[y:y + h, x:x + w]
    ob = _bands(g); fb = _bands(fill.mean(2)[y:y + h, x:x + w]); gall = _bands(gr); gb = _bands(gr.mean(2))
    lf = _lines(fill.mean(2).astype(np.float32)[y:y + h, x:x + w]).astype(np.uint8)
    add = np.zeros_like(gr)
    for i, sb in enumerate(BANDS):
        # полоса «размазывает» линию и край дыры на ~2.5σ: её сила считается только дальше от них
        r = int(2.5 * sb) + 3
        pb = ~(cv2.dilate((ln | hole).astype(np.uint8), np.ones((2 * r + 1,) * 2, np.uint8)) > 0)
        tgt2, _ = _nfill(ob[i] ** 2, pb, sig_local)                   # местная сила полосы у бумаги
        tgt2 = tgt2[y:y + h, x:x + w]
        K = np.ones((2 * r + 1,) * 2, np.uint8)          # своя сила заливки — тоже вдали от линий и края дыры
        inner = (cv2.erode(hs.astype(np.uint8), K) > 0) & ~(cv2.dilate(lf, K) > 0)
        if inner.sum() < 200: inner = hs
        have2 = float(np.mean(fb[i][inner] ** 2)); g2 = float(np.mean(gb[i][inner] ** 2))
        k = np.sqrt(np.clip(tgt2 - have2, 0, None) / max(g2, 1e-6))
        add += k[..., None] * gall[i]
    out = fill.copy()
    out[y:y + h, x:x + w] += add * hs[..., None]
    return out


def inpaint(img, hole, grow=True, seed=7):
    """Фон на месте вырезанного предмета. img — RGB 0..255 (любой тип), hole — маска (bool/0-1).
    Возвращает float32 RGB. grow=False — без расширения на ореол (если маска уже точная)."""
    img = np.asarray(img, np.float32)
    hole = np.asarray(hole).astype(bool)
    if not hole.any():
        return img.copy()
    # большая дыра (кроп больше 2×512): сеть рисовала бы линии в 3+ раза мельче и после увеличения они мыльные
    # (дверь ×2: линия пола в дыре — серая полоса). Тогда всё делается на копии, уменьшенной в k раз, и дыра
    # увеличивается обратно; зерно — уже в полном размере, с бумаги этого же рисунка
    x, y, w, h = cv2.boundingRect(hole.astype(np.uint8))
    k = int(np.ceil(max(w, h) * CROP_MARGIN / (2 * LAMA_SIZE)))
    if k > 1:
        H, W = hole.shape
        small = cv2.resize(img, (W // k, H // k), interpolation=cv2.INTER_AREA)
        hs = cv2.resize(hole.astype(np.float32), (W // k, H // k), interpolation=cv2.INTER_AREA) > 0.01
        if grow: hs = halo(small, hs)
        rs = inpaint(small, hs, grow=False, seed=seed)
        hb = (cv2.resize(hs.astype(np.uint8), (W, H), interpolation=cv2.INTER_NEAREST) > 0) | hole
        # у увеличенной копии зерно крупное (в k раз) — гасится тем же фильтром, что фактура сети, и кладётся своё
        up = flatten(cv2.resize(rs, (W, H), interpolation=cv2.INTER_CUBIC), k)
        full = grain(img, up, hb, seed=seed)
        a = np.maximum(hb, cv2.GaussianBlur(hb.astype(np.float32), (0, 0), 1.5))[..., None]
        return np.clip(img * (1 - a) + full * a, 0, 255)
    if grow:
        hole = halo(img, hole)
    net, x0, y0, side = lama_crop(img, hole)
    sl = (slice(y0, y0 + side), slice(x0, x0 + side))
    o, hh = img[sl], hole[sl]
    fixed = tone_fix(o, flatten(net, side / LAMA_SIZE), hh)
    full = img.copy(); full[sl] = np.where(hh[..., None], fixed, o)
    full = grain(img, full, hole, seed=seed)                 # зерно — с чистой бумаги всего рисунка, не только кропа
    a = np.maximum(hole, cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 1.5))[..., None]   # шов мягкий наружу на 2–3 px
    out = img * (1 - a) + full * a
    return np.clip(out, 0, 255)


VERSION = 1        # правка алгоритма — VERSION += 1: кэш заливок пересчитается


def cached(img, hole, cache_dir, grow=True, seed=7):
    """inpaint с кэшем на диске по содержимому рисунка и дыры: при повторной сборке — чтение, а не LaMa."""
    import hashlib
    img = np.asarray(img); hole = np.asarray(hole).astype(bool)
    h = hashlib.md5(img.tobytes()); h.update(np.packbits(hole).tobytes())
    h.update(f"{img.shape}|{grow}|{seed}|{VERSION}".encode())
    path = os.path.join(cache_dir, f"inpaint_{h.hexdigest()[:16]}.npy")
    if os.path.exists(path):
        return np.load(path).astype(np.float32)
    out = inpaint(img, hole, grow=grow, seed=seed)
    os.makedirs(cache_dir, exist_ok=True)
    np.save(path, np.clip(out, 0, 255).astype(np.uint8))   # uint8: заливка всё равно идёт в 8-битный кадр
    return np.load(path).astype(np.float32)


if __name__ == "__main__":
    import sys
    import time
    from PIL import Image
    im = np.asarray(Image.open(sys.argv[1]).convert("RGB"))
    hm = np.asarray(Image.open(sys.argv[2]).convert("L")) > 127
    t = time.time(); r = inpaint(im, hm); print("%.1f s" % (time.time() - t))
    Image.fromarray(r.astype(np.uint8)).save(sys.argv[3])
