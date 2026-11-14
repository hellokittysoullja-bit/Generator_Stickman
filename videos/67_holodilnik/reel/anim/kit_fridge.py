"""Слои хука рилса 67 «Открыл холодильник и закрыл?» для HyperFrames — по образцу рилса 66 (kit_list.py).

Рисунок gen/g1_fridge_glow.png (1664×2496) ×2 = src/f1.png; координаты сняты по сетке исходника и умножены на K=2.
Слои: кот целиком (хвост с огоньком, лапа на полке, усы), открытая дверца (полоса справа от петли), закрытая дверца —
нарисована кодом тем же пером (тушь, светло-серая заливка, ручка) поверх передней стенки холодильника. Фон — кухня
(anim.inpaint_bg под котом и открытой дверцей). Композиция — весь рисунок в половинном размере."""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); REEL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REEL, "..", "..", "..", "scripts"))
import anim  # noqa: E402

OUT = os.path.join(HERE, "kit")
CACHE = os.path.join(REEL, ".cache", "anim")
K = 2.0
EDGE_X = 958                               # левый край холодильника: правее — у кота только тёмная лапа и усы


def P(pts):
    return [(int(x * K), int(y * K)) for x, y in pts]


CAT_REG = P([(8, 560), (1000, 560), (1000, 1040), (1160, 1040), (1160, 1500), (990, 1520), (960, 1700), (960, 2180),
             (8, 2180)])
DOOR_REG = P([(1446, 280), (1655, 280), (1655, 2330), (1446, 2330)])
FACE = P([(978, 538), (1452, 318), (1452, 2296), (956, 2118)])     # передняя стенка: закрытая дверца
FEET = P([(560, 2150)])[0]
HINGE = P([(1452, 1300)])[0]
HEAD = P([(720, 1060)])[0]


def fill_holes(m):
    m = (m > 0).astype(np.uint8)
    h, w = m.shape
    big = np.zeros((h + 2, w + 2), np.uint8); big[1:-1, 1:-1] = m
    ff = big.copy(); pad = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 2)
    return (big[1:-1, 1:-1] | (ff[1:-1, 1:-1] != 2)).astype(np.uint8)


def poly_mask(shape, poly):
    r = np.zeros(shape[:2], np.uint8); cv2.fillPoly(r, [np.int32(poly)], 1); return r


def door_face(A):
    """Закрытая дверца: заливка как у боковины, тушь по контуру, внутренний скос и ручка у левого края."""
    img = A.copy()
    m = poly_mask(A.shape, FACE)
    H, Wd = m.shape
    xs = np.arange(Wd, dtype=np.float32)[None, :]
    shade = np.clip((xs - FACE[0][0]) / (FACE[1][0] - FACE[0][0]), 0, 1)       # к петле светлее
    base = np.array([214, 214, 212], np.float32)[None, None] + 26 * shade[..., None]
    img = np.where(m[..., None] > 0, base, img)
    ink = (52, 50, 50)
    c = np.ascontiguousarray(img.astype(np.uint8))
    cv2.polylines(c, [np.int32(FACE)], True, ink, 14, cv2.LINE_AA)
    inner = P([(1000, 575), (1428, 378), (1428, 2262), (980, 2098)])
    cv2.polylines(c, [np.int32(inner)], True, (120, 118, 118), 6, cv2.LINE_AA)
    (hx0, hy0), (hx1, hy1) = P([(1020, 1080), (1048, 1560)])
    cv2.rectangle(c, (hx0, hy0), (hx1, hy1), (176, 176, 176), -1, cv2.LINE_AA)
    cv2.rectangle(c, (hx0, hy0), (hx1, hy1), ink, 10, cv2.LINE_AA)
    return c.astype(np.float32), cv2.dilate(m, np.ones((9, 9), np.uint8))


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.environ.get("F1") or os.path.join(REEL, "src", "f1.png")).convert("RGB")).astype(np.float32)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    H, Wd = g.shape
    left = np.zeros((H, Wd), np.uint8); left[:, :int(EDGE_X * K)] = 1
    reg = poly_mask(A.shape, CAT_REG)
    head = np.zeros_like(left); head[int(850 * K):int(1500 * K), int(EDGE_X * K):int(1160 * K)] = 1   # глаз, щека, усы, лапа над полкой
    non = (((g < 205) | (sat > 45)) & (left > 0)) | ((g < 110) & (left == 0)) | (((g < 160) | (sat > 80)) & (head > 0))
    ink = cv2.morphologyEx((non & (reg > 0)).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8)) & reg
    cat = (fill_holes(anim.keep_attached(ink)) & reg).astype(np.uint8)
    cat |= ((g < 150) & (reg > 0) & ~cv2.dilate(cat, np.ones((3, 3), np.uint8)).astype(bool)).astype(np.uint8)  # усы
    cat = anim.keep_attached(cat, reach=4)
    dreg = poly_mask(A.shape, DOOR_REG)
    dm = cv2.morphologyEx((((g < 238) | (sat > 30)) & (dreg > 0)).astype(np.uint8), cv2.MORPH_CLOSE,
                          np.ones((15, 15), np.uint8)) & dreg
    dm = anim.keep_attached(fill_holes(dm) & dreg)
    bg = A.copy()
    split = np.zeros_like(left); split[:int(1400 * K)] = 1
    for part in (cat & split, cat & (1 - split), dm & split, dm & (1 - split)):
        hole = cv2.dilate(part.astype(np.uint8), np.ones((17, 17), np.uint8)) > 0
        if hole.any():
            bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
    # LaMa на таком большом проёме оставляла тёмные пятна меха у края холодильника и обрывок огонька: у стены за
    # котом — ровная бумага, внутри холодильника (где лапа и усы) — Telea по самому рисунку, без LaMa
    hole = cv2.dilate(cat, np.ones((25, 25), np.uint8)) > 0
    xx = np.arange(Wd)[None, :]; yy = np.arange(H)[:, None]
    wall = (hole | ((xx < int(14 * K)) & (yy > int(1300 * K)))) & (xx < int(EDGE_X * K)) & (yy < int(2075 * K))
    paper = np.median(A[int(150 * K):int(450 * K), int(100 * K):int(600 * K)].reshape(-1, 3), axis=0)
    a = cv2.GaussianBlur(wall.astype(np.float32), (0, 0), 5)[..., None]
    bg = bg * (1 - a) + paper * a
    inside = (hole & (xx >= int(EDGE_X * K))).astype(np.uint8)
    y0, y1 = int(820 * K), int(1520 * K); x0, x1 = int(880 * K), int(1260 * K)
    tel = cv2.inpaint(np.ascontiguousarray(A[y0:y1, x0:x1].astype(np.uint8)), hole[y0:y1, x0:x1].astype(np.uint8), 12,
                      cv2.INPAINT_TELEA)                     # известны только пиксели вне кота: тянет из холодильника
    m = inside[y0:y1, x0:x1, None].astype(np.float32)
    bg[y0:y1, x0:x1] = bg[y0:y1, x0:x1] * (1 - m) + tel.astype(np.float32) * m
    Ap, bg = anim.paper_like(A), anim.paper_like(bg)
    face, fm = door_face(Ap)
    layers = {}
    anim.save_layer(OUT, "door", Ap, dm, layers)
    anim.save_layer(OUT, "cat", Ap, cat, layers, keep_attached_=False)
    anim.save_layer(OUT, "face", face, fm, layers, keep_attached_=False)
    Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    for f in ["bg.png"] + [n + ".png" for n in layers]:
        im = Image.open(os.path.join(OUT, f)); im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(os.path.join(OUT, f))
    for v in layers.values():
        v["xy"] = (v["xy"][0] // 2, v["xy"][1] // 2); v["wh"] = (v["wh"][0] // 2, v["wh"][1] // 2)
    h2 = lambda p: (p[0] // 2, p[1] // 2)     # noqa: E731
    meta = dict(origin=(0, 0), size=(Wd // 2, H // 2), layers=layers, feet=h2(FEET), hinge=h2(HINGE), head=h2(HEAD),
                fps=30, scale=0.5)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
