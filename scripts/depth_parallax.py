"""Объёмный параллакс по карте глубины — редкий эффект ручного плана длинного ролика.

Владелец 02.11 (было/стало на пяти рисунках L02: «стало лучше»): не везде, а как один из эффектов наряду с наездом,
тряской и хлёстом — на очень малом числе планов, где кот на чистой бумаге или перед столом; где за краем кота плотная
фактура (мозг), не ставить: там видны дыры заливки. В edit.json у плана — "parallax": true (или {"dx": px, "dz": доля}).

Глубина — Depth Anything V2 Small (ONNX, Apache-2.0 — только Small; Base/Large под некоммерческой лицензией), считается
один раз на рисунок и кэшируется. Поверх обычной камеры плана добавляется сдвиг по глубине: ближнее уезжает и
приближается сильнее дальнего, ближний предмет закрывает дальний (марш по слоям глубины), а не тянется резиной;
тонкие штрихи (усы) получают глубину своего хозяина; дыры за ближним краем заливаются только с дальней стороны."""
import hashlib
import os
import urllib.request

import cv2
import numpy as np

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MODEL_URL = "https://huggingface.co/onnx-community/depth-anything-v2-small/resolve/main/onnx/model.onnx"
MODEL = os.path.join(ROOT, "models", "depth_anything_v2_small.onnx")
DX, DZ = 24.0, 0.03          # px на экране и доля масштаба на всю глубину за план — замер 02.11: объём читается без дыр
STEPS = 22


def _session():
    import onnxruntime as ort
    if not os.path.exists(MODEL):
        os.makedirs(os.path.dirname(MODEL), exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, MODEL + ".part")
        os.replace(MODEL + ".part", MODEL)
    so = ort.SessionOptions(); so.intra_op_num_threads = 4
    return ort.InferenceSession(MODEL, so, providers=["CPUExecutionProvider"])


def depth_map(img, cache_dir=None):
    """Глубина рисунка 0..1 (1 — ближе) в размере img; кэш по содержимому рисунка."""
    img = np.asarray(img)
    key = hashlib.md5(img.tobytes()).hexdigest()[:16]
    path = os.path.join(cache_dir, f"depth_{key}.npy") if cache_dir else None
    if path and os.path.exists(path):
        return np.load(path)
    H, W = img.shape[:2]
    sc = 518 / min(H, W); h = int(round(H * sc / 14)) * 14; w = int(round(W * sc / 14)) * 14
    x = cv2.resize(img[..., :3], (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    s = _session()
    d = s.run(None, {s.get_inputs()[0].name: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
    lo, hi = np.percentile(d, 1), np.percentile(d, 99.5)
    d = cv2.resize(np.clip((d - lo) / (hi - lo + 1e-6), 0, 1).astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    if path:
        os.makedirs(cache_dir, exist_ok=True); np.save(path, d)
    return d


def _thin_to_owner(img, D):
    """Усы и тонкие штрихи: модель даёт им глубину «наполовину» — отдать глубину их хозяина (иначе усы рвутся)."""
    raised = (D - cv2.erode(D, np.ones((21, 21), np.uint8))) > 0.06
    big = cv2.morphologyEx(raised.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))) > 0
    T = raised & ~big
    ink = img.mean(2) < 170
    Dp = D.copy(); k3 = np.ones((3, 3), np.uint8)
    for _ in range(110):
        Dp = np.where(T, np.maximum(Dp, cv2.dilate(Dp, k3)), Dp)
    reach = T.copy()
    for _ in range(30):
        m = ink & cv2.dilate(reach.astype(np.uint8), k3).astype(bool)
        reach |= m
        Dp = np.where(m, np.maximum(Dp, cv2.dilate(Dp, k3)), Dp)
    return Dp


def prepare(screen_img, screen_depth, dil=4):
    """Глубина экрана, готовая к маршу: усы — хозяину, контур едет с ближним предметом, без шума."""
    D = _thin_to_owner(np.asarray(screen_img, np.float32), np.asarray(screen_depth, np.float32))
    D = cv2.dilate(D, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * dil + 1, 2 * dil + 1)))
    return cv2.GaussianBlur(D, (0, 0), 1.0)


def apply(screen, D, tau, dx=DX, dz=DZ, steps=STEPS):
    """Кадр экрана с параллаксом: tau 0..1 — ход плана. При tau = 0 — кадр без изменений."""
    if tau <= 0:
        return screen
    H, W = D.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = (W - 1) / 2, (H - 1) / 2
    dref = float(np.percentile(D, 50))
    lo, hi = float(D.min()) - 1e-3, float(D.max()) + 1e-3

    def inv(h):
        e = h - dref
        z = 1 + tau * dz * e
        return (cx + (xx - cx) / z + tau * dx * e).astype(np.float32), (cy + (yy - cy) / z).astype(np.float32)

    hs = np.linspace(hi, lo, steps)
    hit = np.zeros((H, W), bool); hstar = np.full((H, W), lo, np.float32); fprev = hprev = None
    for h in hs:
        qx, qy = inv(h)
        f = cv2.remap(D, qx, qy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE) - h
        new = (~hit) & (f >= 0)
        if fprev is None:
            hstar[new] = h
        else:
            hr = hprev + (h - hprev) * (fprev / (fprev - f + 1e-9))
            hstar[new] = np.clip(hr[new], h, hprev)
        hit |= f >= 0; fprev, hprev = f, h
    qx, qy = inv(hstar)
    A = cv2.remap(np.asarray(screen, np.float32), qx, qy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    J = np.gradient(qx, axis=1) * np.gradient(qy, axis=0) - np.gradient(qx, axis=0) * np.gradient(qy, axis=1)
    a = cv2.GaussianBlur(np.clip((cv2.erode(J, np.ones((3, 3), np.uint8)) - 0.35) / 0.35, 0, 1).astype(np.float32), (0, 0), 0.8)
    S = cv2.dilate((a < 0.5).astype(np.uint8), np.ones((3, 3), np.uint8))
    if not S.any():
        return np.clip(A, 0, 255)
    E = cv2.dilate(S, np.ones((81, 81), np.uint8)).astype(bool) & ~S.astype(bool) & \
        (hstar > cv2.erode(hstar, np.ones((121, 121), np.uint8)) + 0.08)
    mask = (S.astype(bool) | E).astype(np.uint8)
    ys, xs = np.nonzero(mask)
    y0, y1 = max(ys.min() - 60, 0), min(ys.max() + 61, H); x0, x1 = max(xs.min() - 60, 0), min(xs.max() + 61, W)
    B = A.copy()
    B[y0:y1, x0:x1] = cv2.inpaint(np.clip(A[y0:y1, x0:x1], 0, 255).astype(np.uint8), mask[y0:y1, x0:x1], 5,
                                  cv2.INPAINT_TELEA).astype(np.float32)
    return np.clip(A * a[..., None] + B * (1 - a[..., None]), 0, 255)
