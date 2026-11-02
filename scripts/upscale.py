#!/usr/bin/env python3
"""Увеличение рисунка для крупных планов.

С 02.11 по выбору владельца — waifu2x swin_unet/art (nagadomi/nunif, MIT): по листу «исходник / наше / waifu2x» на
кадре L02 выбрана правая — линия как у художника. Замер агента 02.11 на 7 рисунках: верность исходнику PSNR
40,5–47,8 дБ против 31,7–39,7 у прежней смеси (она «обводила маркером»: линии темнее на 12–42 %, серые штрихи
чернели), цветных пятен, блоков и сдвига нет; швы кусков убраны запасом контекста 16 px (отличия > 20 уровней у
границ 448 → 6). Пустые куски (бумага) берутся из Lanczos. В ~1,7 раза медленнее, но считается один раз на рисунок
и лежит в кэше. UPSCALE_METHOD=esrgan — прежняя смесь ниже (байт в байт как раньше).

Прежнее (до 02.11): Real-ESRGAN (аниме, лёгкая версия) + смешивание с Lanczos.

Почему смесь, а не чистый ESRGAN: нейросеть на рисованной линии чуть
«пластилинит» штриховку и зерно бумаги. Низкие частоты берутся у Lanczos
(геометрия и цвет ровно исходные), высокие — у ESRGAN (чистая линия) и
частично у Lanczos (родное зерно). Замер на кадрах демо (04.10): без ореолов
и без мыла на 2.5x; критики подтвердили.

Модель: xiongjie/lightweight-real-ESRGAN-anime, RealESRGAN_x4plus_anime_4B32F.onnx
(MIT, 5 МБ), качается при первом вызове и сверяется по sha256. Нет сети/
onnxruntime — чистый Lanczos с громким предупреждением (кадр не пропадает).
Обработка кусками 256 px с перекрытием 24 — без стыков и без роста памяти
(целиком 2528x1696 съедало всю память контейнера)."""
import hashlib
import os
import sys
import urllib.request

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_URL = ("https://huggingface.co/xiongjie/lightweight-real-ESRGAN-anime/resolve/main/"
             "RealESRGAN_x4plus_anime_4B32F.onnx")
MODEL_SHA = "2208c7ae8db793330abf1248fbce15585ad317e921c456265572836b92926c9a"
MODEL_PATH = os.path.join(ROOT, "models", "esrgan", "RealESRGAN_x4plus_anime_4B32F.onnx")
TILE, PAD = 256, 24
FLAT_DEV = 12            # кусок, где 99.5% пикселей отличаются от его медианы меньше — бумага или ровная
                         # заливка: линий нет, нейросеть там не нужна (замер 04.10: ~45% кусков кадра)
LOW_SIGMA, HI_ESR, HI_LANCZOS = 1.4, 0.85, 0.6
VERSION = 3                # 3: waifu2x по умолчанию (02.11)
W2X_URL = "https://unlimited.waifu2x.net/models/swin_unet/art/scale2x.onnx"
W2X_SHA = "f5de9edfbc4ef273c962502ccd949e6d4e3b2a93db2c2f9cba5c795d19554342"
W2X_PATH = os.path.join(ROOT, "models", "waifu2x", "swin_unet_art_scale2x.onnx")
W2X_TILE, W2X_CROP, W2X_MARGIN = 256, 8, 8      # модель сама срезает 8 px с каждой стороны; ещё 8 — запас против швов


def method():
    return os.environ.get("UPSCALE_METHOD", "waifu2x")

_SESSION = None
WARNED = []


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def ensure_model(path=MODEL_PATH, url=MODEL_URL, sha=MODEL_SHA):
    if os.path.exists(path) and _sha(path) == sha:
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".part"
    urllib.request.urlretrieve(url, tmp)
    if _sha(tmp) != sha:
        os.remove(tmp)
        raise RuntimeError(f"{os.path.basename(path)}: скачанный файл не совпал по sha256 — не используем")
    os.replace(tmp, path)
    return path


def session():
    """Сессия onnxruntime или None (с предупреждением один раз)."""
    global _SESSION
    if os.environ.get("UPSCALE_NEURAL", "1") == "0":     # явное «без нейросети» (тесты, слабая машина)
        return None
    if _SESSION is None:
        try:
            import onnxruntime as ort
            so = ort.SessionOptions()
            so.intra_op_num_threads = int(os.environ.get("UPSCALE_THREADS", "1"))
            model = ensure_model(W2X_PATH, W2X_URL, W2X_SHA) if method() == "waifu2x" else ensure_model()
            _SESSION = ort.InferenceSession(model, so, providers=["CPUExecutionProvider"])
        except Exception as e:  # noqa: BLE001
            _SESSION = False
            if not WARNED:
                WARNED.append(str(e))
                print(f"  ВНИМАНИЕ: увеличение без нейросети (Lanczos) — {type(e).__name__}: {e}"[:300],
                      file=sys.stderr)
    return _SESSION or None


def _esrgan(a, scale, sess, L):
    """a — HxWx3 uint8 -> (H*scale)x(W*scale)x3 float32, кусками с перекрытием.
    Пустые куски (бумага) берутся из Lanczos L — у рисунка на бумаге это
    большая часть кадра, а результат там тот же."""
    h, w = a.shape[:2]
    out = np.zeros((h*scale, w*scale, 3), np.float32)
    name = sess.get_inputs()[0].name
    src = a.astype(np.float32)/255
    for ty in range(0, h, TILE):
        for tx in range(0, w, TILE):
            a0, b0 = max(0, ty - PAD), max(0, tx - PAD)
            a1, b1 = min(h, ty + TILE + PAD), min(w, tx + TILE + PAD)
            ey, ex = min(ty + TILE, h), min(tx + TILE, w)
            t_ = a[a0:a1, b0:b1].astype(np.int16)
            dev = np.abs(t_ - np.median(t_.reshape(-1, 3), axis=0).astype(np.int16)).max(2)
            if float(np.percentile(dev, 99.5)) < FLAT_DEV:
                out[ty*scale:ey*scale, tx*scale:ex*scale] = L[ty*scale:ey*scale, tx*scale:ex*scale]
                continue
            y = sess.run(None, {name: src[a0:a1, b0:b1].transpose(2, 0, 1)[None]})[0][0].transpose(1, 2, 0)
            y = np.clip(y, 0, 1)*255
            if scale != 4:
                y = np.asarray(Image.fromarray(y.round().astype(np.uint8)).resize(
                    ((b1 - b0)*scale, (a1 - a0)*scale), Image.LANCZOS), np.float32)
            out[ty*scale:ey*scale, tx*scale:ex*scale] = \
                y[(ty - a0)*scale:(ey - a0)*scale, (tx - b0)*scale:(ex - b0)*scale]
    return out


def _flat(t):
    dev = np.abs(t.astype(np.int16) - np.median(t.reshape(-1, 3), axis=0).astype(np.int16)).max(2)
    return float(np.percentile(dev, 99.5)) < FLAT_DEV


def _waifu2x(a, sess, L):
    """a — HxWx3 uint8 -> (2H)x(2W)x3 float32 кусками; пустые куски — из Lanczos L (там результат тот же)."""
    name = sess.get_inputs()[0].name
    x = a.astype(np.float32) / 255
    H, W = a.shape[:2]
    off = W2X_CROP + W2X_MARGIN; step = W2X_TILE - 2 * off; m = 2 * W2X_MARGIN
    xp = np.pad(x, ((off, off + step), (off, off + step), (0, 0)), mode="edge")
    out = np.zeros((2 * H, 2 * W, 3), np.float32)
    for i in range(0, H, step):
        for j in range(0, W, step):
            ey, ex = min(i + step, H), min(j + step, W)
            if _flat(a[max(0, i - off):ey + off, max(0, j - off):ex + off]):
                out[2 * i:2 * ey, 2 * j:2 * ex] = L[2 * i:2 * ey, 2 * j:2 * ex]
                continue
            t = np.ascontiguousarray(xp[i:i + W2X_TILE, j:j + W2X_TILE].transpose(2, 0, 1)[None])
            y = sess.run(None, {name: t})[0][0].transpose(1, 2, 0)
            out[2 * i:2 * ey, 2 * j:2 * ex] = np.clip(y[m:m + 2 * (ey - i), m:m + 2 * (ex - j)], 0, 1) * 255
    return out


def upscale(a, scale=2, cache_dir=None):
    """Рисунок в scale (2 или 4) раза: смесь ESRGAN и Lanczos. uint8 -> uint8.
    cache_dir — дисковый кэш по содержимому (повторный рендер не платит временем)."""
    a = np.ascontiguousarray(a, dtype=np.uint8)
    key = None
    if cache_dir:
        neural = os.environ.get("UPSCALE_NEURAL", "1") != "0"
        tag = f"|{VERSION}|w2x" if method() == "waifu2x" else f"|2|{LOW_SIGMA}|{HI_ESR}|{HI_LANCZOS}"
        key = hashlib.sha256(a.tobytes() + f"{a.shape}|{scale}{tag}|{neural}|{FLAT_DEV}"
                             .encode()).hexdigest()[:24]
        p = os.path.join(cache_dir, f"up_{key}.png")
        if os.path.exists(p):
            try:
                return np.asarray(Image.open(p).convert("RGB"))
            except OSError:
                pass
    h, w = a.shape[:2]
    L = np.asarray(Image.fromarray(a).resize((w*scale, h*scale), Image.LANCZOS), np.float32)
    sess = session()
    if sess is None:
        out = L
    elif method() == "waifu2x":
        L2 = L if scale == 2 else np.asarray(Image.fromarray(a).resize((w * 2, h * 2), Image.LANCZOS), np.float32)
        out = _waifu2x(a, sess, L2)
        if scale == 4:                                   # 4x — дважды по 2x
            b = np.clip(out, 0, 255).round().astype(np.uint8)
            L4 = np.asarray(Image.fromarray(b).resize((w * 4, h * 4), Image.LANCZOS), np.float32)
            out = _waifu2x(b, sess, L4)
    else:
        U = _esrgan(a, scale, sess, L)

        def lo(x):
            return ndimage.gaussian_filter(x, (LOW_SIGMA, LOW_SIGMA, 0))
        lL = lo(L)
        out = lL + (U - lo(U))*HI_ESR + (L - lL)*HI_LANCZOS
    out = np.clip(out, 0, 255).round().astype(np.uint8)
    if key:
        os.makedirs(cache_dir, exist_ok=True)
        tmp = os.path.join(cache_dir, f"up_{key}.{os.getpid()}.png")
        Image.fromarray(out).save(tmp)
        os.replace(tmp, os.path.join(cache_dir, f"up_{key}.png"))
    return out
