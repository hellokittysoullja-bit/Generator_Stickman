"""Методы вырезки для стенда bench.py: f(rgb uint8 H×W×3, box (x0,y0,x1,y1), pos [(x,y)], neg [(x,y)]) -> альфа 0..1."""
import os

import cv2
import numpy as np
from PIL import Image


def _fill_holes(m):
    m = (m > 0).astype(np.uint8)
    ff = m.copy(); pad = np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 1)
    return (m | (1 - ff)).astype(np.uint8)


def ink(rgb, box, pos, neg):
    """Нынешний способ, обобщённый на рамку: шерсть и тушь (тёмное) + цветное (глаза, огонёк, подушечки) внутри рамки,
    дыры внутри контура — коту, оторванное — прочь (сцены режут так же, только по ручному многоугольнику)."""
    x0, y0, x1, y1 = box
    g = rgb.mean(2); sat = rgb.max(2).astype(int) - rgb.min(2)
    m = ((g < 125) | (sat > 70)).astype(np.uint8)
    reg = np.zeros(m.shape, np.uint8); reg[y0:y1, x0:x1] = 1
    m = cv2.morphologyEx(m & reg, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    keep = np.zeros_like(m)
    for (x, y) in pos:                                   # связные куски, где стоят точки «кот»
        if lab[y, x]:
            keep |= (lab == lab[y, x]).astype(np.uint8)
    return _fill_holes(keep).astype(np.float32)


_SESS = {}


def birefnet(rgb, box, pos, neg, model="birefnet-general"):
    from rembg import new_session, remove
    if model not in _SESS:
        _SESS[model] = new_session(model)
    x0, y0, x1, y1 = box
    a = remove(Image.fromarray(rgb[y0:y1, x0:x1]), session=_SESS[model], only_mask=True)
    out = np.zeros(rgb.shape[:2], np.float32); out[y0:y1, x0:x1] = np.asarray(a, np.float32) / 255
    return out


MODELS = "/home/user/models"
MEAN, STD = np.array([0.485, 0.456, 0.406], np.float32), np.array([0.229, 0.224, 0.225], np.float32)


def _sess(path):
    import onnxruntime as ort
    if path not in _SESS:
        o = ort.SessionOptions(); o.intra_op_num_threads = 4
        _SESS[path] = ort.InferenceSession(path, o, providers=["CPUExecutionProvider"])
    return _SESS[path]


def _prep(crop, size=1024):
    x = cv2.resize(crop, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return ((x - MEAN) / STD).transpose(2, 0, 1)[None].astype(np.float32)


def sam2(rgb, box, pos, neg):
    """SAM 2.1 Hiera-Small ONNX (Apache-2.0): рамка кота + точки «кот» и «не кот»; кадр — вырез рамки, растянутый в 1024."""
    x0, y0, x1, y1 = box; crop = rgb[y0:y1, x0:x1]; h, w = crop.shape[:2]
    enc = _sess(f"{MODELS}/sam21s/sam2.1_hiera_small.encoder.onnx")
    dec = _sess(f"{MODELS}/sam21s/sam2.1_hiera_small.decoder.onnx")
    f0, f1, emb = enc.run(None, {"image": _prep(crop)})
    pts = [((x - x0) * 1024 / w, (y - y0) * 1024 / h) for x, y in pos + neg]
    lab = [1] * len(pos) + [0] * len(neg)
    pts += [(0, 0), (1023, 1023)]; lab += [2, 3]                                   # рамка — углы
    masks, iou = dec.run(None, {"image_embed": emb, "high_res_feats_0": f0, "high_res_feats_1": f1,
                                "point_coords": np.array([pts], np.float32), "point_labels": np.array([lab], np.float32),
                                "mask_input": np.zeros((1, 1, 256, 256), np.float32), "has_mask_input": np.zeros(1, np.float32)})
    m = masks[0][int(np.argmax(iou[0]))]
    m = cv2.resize(m.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
    out = np.zeros(rgb.shape[:2], np.float32); out[y0:y1, x0:x1] = _fill_holes((m > 0).astype(np.uint8))   # экран, подушечки — внутри контура
    return out


def toonout(rgb, box, pos, neg):
    """ToonOut — BiRefNet, дообученный на аниме (MIT), ONNX fp32, вход 1024²; кадр — вырез рамки."""
    x0, y0, x1, y1 = box; crop = rgb[y0:y1, x0:x1]; h, w = crop.shape[:2]
    y = _sess(f"{MODELS}/birefnet-toonout.onnx").run(None, {"image": _prep(crop)})[0][0, 0]
    if y.min() < 0 or y.max() > 1:
        y = 1 / (1 + np.exp(-y))
    out = np.zeros(rgb.shape[:2], np.float32); out[y0:y1, x0:x1] = cv2.resize(y, (w, h), interpolation=cv2.INTER_CUBIC)
    return out


def _matte(rgb, hard, box, inner=8, outer=14, scale=0.5):
    """Тримап из жёсткой маски (сжатие — точно предмет, расширение — неизвестно; тонкие тёмные линии у края — тоже
    неизвестно: усы) → pymatting closed-form на половинном размере, назад к полному."""
    from pymatting import estimate_alpha_cf
    x0, y0, x1, y1 = box
    m = (hard[y0:y1, x0:x1] > 0.5).astype(np.uint8); crop = rgb[y0:y1, x0:x1]
    fg = cv2.erode(m, np.ones((inner, inner), np.uint8)); grow = cv2.dilate(m, np.ones((outer, outer), np.uint8))
    dark = (crop.mean(2) < 110).astype(np.uint8)
    whisk = cv2.dilate(m, np.ones((61, 61), np.uint8)) & dark & (1 - grow)        # усы, торчащие за край маски
    tri = np.where(fg > 0, 1.0, 0.0); tri[(grow > 0) & (fg == 0)] = 0.5; tri[whisk > 0] = 0.5
    sm = cv2.resize(crop, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA).astype(np.float64) / 255
    ts = cv2.resize(tri, (sm.shape[1], sm.shape[0]), interpolation=cv2.INTER_NEAREST)
    a = estimate_alpha_cf(sm, ts)
    a = cv2.resize(a.astype(np.float32), (crop.shape[1], crop.shape[0]), interpolation=cv2.INTER_LINEAR)
    a[tri == 1] = 1; a[tri == 0] = 0
    out = np.zeros(rgb.shape[:2], np.float32); out[y0:y1, x0:x1] = np.clip(a, 0, 1)
    return out


def sam2_matte(rgb, box, pos, neg):
    return _matte(rgb, sam2(rgb, box, pos, neg), box)


def toonout_sam2(rgb, box, pos, neg):
    """ToonOut ∩ SAM 2 (расширенный): ToonOut даёт край, SAM — что считать котом (без подушки и мебели)."""
    t = toonout(rgb, box, pos, neg); s = sam2(rgb, box, pos, neg)
    s = cv2.dilate((s > 0.5).astype(np.uint8), np.ones((25, 25), np.uint8)).astype(np.float32)
    return t * s


def _sam2_points(rgb, box, pts_lab):
    x0, y0, x1, y1 = box; crop = rgb[y0:y1, x0:x1]; h, w = crop.shape[:2]
    pts_lab = [((x, y), l) for (x, y), l in pts_lab if x0 <= x < x1 and y0 <= y < y1]   # точка за рамкой сбивала SAM
    g = crop.mean(2); sat = crop.max(2).astype(int) - crop.min(2)                      # + бумага у края рамки — «не кот»
    for fx, fy in [(0.04, 0.04), (0.5, 0.03), (0.96, 0.04), (0.03, 0.5), (0.97, 0.5), (0.04, 0.96), (0.5, 0.97), (0.96, 0.96)]:
        px, py = int(fx * (w - 1)), int(fy * (h - 1))
        if g[py, px] > 225 and sat[py, px] < 30:
            pts_lab.append(((px + x0, py + y0), 0))
    key = ("sam2emb", id(rgb), box)
    if key not in _SESS:
        _SESS.clear() if len(_SESS) > 20 else None
        _SESS[key] = _sess(f"{MODELS}/sam21s/sam2.1_hiera_small.encoder.onnx").run(None, {"image": _prep(crop)})
    f0, f1, emb = _SESS[key]
    dec = _sess(f"{MODELS}/sam21s/sam2.1_hiera_small.decoder.onnx")
    pts = [((x - x0) * 1024 / w, (y - y0) * 1024 / h) for (x, y), _ in pts_lab] + [(0, 0), (1023, 1023)]
    lab = [l for _, l in pts_lab] + [2, 3]
    masks, iou = dec.run(None, {"image_embed": emb, "high_res_feats_0": f0, "high_res_feats_1": f1,
                                "point_coords": np.array([pts], np.float32), "point_labels": np.array([lab], np.float32),
                                "mask_input": np.zeros((1, 1, 256, 256), np.float32), "has_mask_input": np.zeros(1, np.float32)})
    best, score = None, -1e9
    for k in range(masks.shape[1]):                      # из трёх ответов SAM — тот, что согласен с точками, а не тот,
        m = cv2.resize(masks[0][k].astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR) > 0   # кому SAM верит
        hit = sum(m[int(y - y0), int(x - x0)] == (l == 1) for (x, y), l in pts_lab)
        border = np.concatenate([m[0], m[-1], m[:, 0], m[:, -1]]).mean()
        sc = hit * 10 - border * 20 + float(iou[0][k])
        if sc > score:
            best, score = m, sc
    out = np.zeros(rgb.shape[:2], np.uint8); out[y0:y1, x0:x1] = best
    return out


def sam2u(rgb, box, pos, neg):
    """SAM 2.1: все точки разом ∪ каждая «кот»-точка отдельно (со всеми «не кот») — держатся мелкие части: телефон в
    лапах, огонёк, ботинок; дыры внутри контура — заливкой."""
    negl = [(p, 0) for p in neg]
    m = _sam2_points(rgb, box, [(p, 1) for p in pos] + negl)
    x0, y0, x1, y1 = box; area = (x1 - x0) * (y1 - y0)
    for p in pos:
        one = _sam2_points(rgb, box, [(p, 1)] + negl)
        sub = one[y0:y1, x0:x1]
        border = np.concatenate([sub[0], sub[-1], sub[:, 0], sub[:, -1]]).mean()
        ok = (one[p[1], p[0]] and not any(one[q[1], q[0]] for q in neg) and one.sum() < 0.6 * area and border < 0.25)
        if ok:                                           # одна точка иногда выделяет фон вокруг кота — такой ответ не брать
            m |= one
    x0, y0, x1, y1 = box
    out = np.zeros_like(m); out[y0:y1, x0:x1] = _fill_small_holes(m[y0:y1, x0:x1])
    return out.astype(np.float32)


def sam2u_matte(rgb, box, pos, neg):
    return _matte(rgb, sam2u(rgb, box, pos, neg), box)


def _fill_small_holes(m, max_share=0.02):
    """Дыры внутри маски (экран телефона, подушечки) — заливкой, но только маленькие: большая «дыра» — это фон между
    котом и краем рамки, его не трогать."""
    m = (m > 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(1 - m, connectivity=4)
    lim = max_share * m.size
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a < lim and x > 0 and y > 0 and x + w < m.shape[1] and y + h < m.shape[0]:
            m[lab == i] = 1
    return m


def sam2b(rgb, box, pos, neg):
    """SAM 2.1 одной маской по всем точкам (+ бумага у края рамки — «не кот»), мелкие дыры внутри — заливкой."""
    m = _sam2_points(rgb, box, [(p, 1) for p in pos] + [(p, 0) for p in neg])
    x0, y0, x1, y1 = box
    out = np.zeros_like(m); out[y0:y1, x0:x1] = _fill_small_holes(m[y0:y1, x0:x1])
    return out.astype(np.float32)


def sam2b_matte(rgb, box, pos, neg):
    return _matte(rgb, sam2b(rgb, box, pos, neg), box)


def anim_cut(rgb, box, pos, neg):
    """Боевой вариант из scripts/anim.py: SAM 2.1 + матирование + усы."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
    import anim
    return anim.cut_sam(rgb, box, pos, neg)
