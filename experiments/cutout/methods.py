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
