"""Слои хука рилса 53 «Восемь пауков за ночь?» для HyperFrames — по базе рилса 13 (стандарт 24).

Рисунок gen/g1_mouth_guard.png (1664×2496) режется на слои прямо в его координатах (композиция HyperFrames идёт в
размере рисунка, сцена увеличивает кадр вдвое до исходника рилса). Слои: кот (голова, лапы, усы), хвост без огонька
(качается), огонёк (мерцает), паук (качается и спускается), нить паука рисует сама композиция; фон под ними —
anim.inpaint_bg. Композиция — от верха рисунка до y=1800 (кровать ниже остаётся рисунком)."""
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
SIZE = (1664, 1800)
CAT_RECTS = [(380, 760, 1240, 1600), (290, 1180, 1360, 1420)]       # голова, лапы и усы
TAIL_RECT = (0, 1380, 330, 1800)                                      # хвост без огонька
FLAME_RECT = (40, 1150, 260, 1470)                                    # огонёк
SPIDER_RECT = (660, 250, 940, 440)
THREAD_RECT = (790, 0, 816, 330)
THREAD_X = 803                                                         # нить: середина по рисунку (замер ниже)
BASE = dict(cat=(800, 1580), tail=(60, 1740), flame=(150, 1405), spider=(800, 360))   # оси качания (px рисунка)


def rects(shape, rr):
    m = np.zeros(shape[:2], np.uint8)
    for x0, y0, x1, y1 in rr:
        m[y0:y1, x0:x1] = 1
    return m


def fill_holes(m):
    m = (m > 0).astype(np.uint8)
    ff = m.copy(); pad = np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 1)
    return (m | (1 - ff)).astype(np.uint8)


def smooth_fill(img, hole, sigma=28):
    """Под хвостом и огоньком LaMa рисует чужие пятна (тёплый блик, серый бугор): здесь сплошная подушка, поэтому
    дыра заливается гладким тоном кольца вокруг неё (нормированная свёртка) и зерном бумаги этого же рисунка."""
    g, sat = img.mean(2), img.max(2) - img.min(2)
    m = ((~hole) & (g > 205) & (sat < 45)).astype(np.float32)      # только светлая бумага и подушка, без туши и огня
    fill = np.zeros_like(img); done = np.zeros(hole.shape, bool)
    for sg in (sigma, 2.5 * sigma, 6 * sigma, 14 * sigma):                # мелкий масштаб, где хватает бумаги вокруг; иначе крупнее
        num = cv2.GaussianBlur(img * m[..., None], (0, 0), sg); den = cv2.GaussianBlur(m, (0, 0), sg)
        ok = (den > 0.03) & ~done
        fill[ok] = num[ok] / den[ok][:, None]; done |= ok
    out = img.copy(); soft = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 4)[..., None]
    rng = np.random.RandomState(7)
    grain = cv2.GaussianBlur(rng.normal(0, 1.4, hole.shape).astype(np.float32), (0, 0), 0.8)[..., None]
    return img * (1 - soft) + (fill + grain) * soft


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.path.join(REEL, "gen", "g1_mouth_guard.png")).convert("RGB")).astype(np.float32)
    A = anim.paper_like(A)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    inkish = ((g < 112) | (sat > 70)).astype(np.uint8)
    flame_c = ((sat > 90) & (A[..., 0] > 200) & (A[..., 2] < 140)).astype(np.uint8)
    # огонёк: насыщенное оранжевое и тушь его контура в своей рамке
    fr = rects(A.shape, [FLAME_RECT])
    fsat = ((sat > 55) & (A[..., 0] > 180)).astype(np.uint8) & fr
    fsat = cv2.morphologyEx(fsat, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8))
    flame = fill_holes(fsat | ((g < 125).astype(np.uint8) & cv2.dilate(fsat, np.ones((9, 9), np.uint8))))
    flame = (cv2.dilate(flame, np.ones((5, 5), np.uint8)) & fr).astype(np.uint8)
    # хвост: толстое тело (раскрытие 9 px) и тушь вплотную к нему; тонкие линии кровати остаются фоном
    tr = rects(A.shape, [TAIL_RECT])
    body = cv2.morphologyEx((inkish & tr & (1 - flame)).astype(np.uint8), cv2.MORPH_OPEN, np.ones((11, 11), np.uint8))
    tail = fill_holes(cv2.morphologyEx(body, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)))
    tail |= (inkish & tr & cv2.dilate(tail, np.ones((9, 9), np.uint8)) & (1 - flame)).astype(np.uint8)
    tail &= (1 - flame).astype(np.uint8)
    # кот
    cr = rects(A.shape, CAT_RECTS)
    ink = (inkish & cr).astype(np.uint8)
    core = anim.keep_attached(ink)
    cat = (fill_holes(core) & cr).astype(np.uint8)
    cat &= (1 - cv2.dilate(tail | flame, np.ones((3, 3), np.uint8))).astype(np.uint8)
    # паук и нить
    sr = rects(A.shape, [SPIDER_RECT]); thr = rects(A.shape, [THREAD_RECT])
    spider = fill_holes(cv2.morphologyEx((((g < 150) | (sat > 60)).astype(np.uint8) & sr), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)))
    thread = ((g < 170).astype(np.uint8) & thr)
    ys, xs = np.where(thread > 0)
    print("нить x", xs.min(), xs.max(), "y", ys.min(), ys.max())
    bg = A.copy()
    for m in (cat, spider, thread):
        hole = cv2.dilate(m, np.ones((15, 15), np.uint8)) > 0
        bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
    hole = cv2.dilate((tail | flame).astype(np.uint8), np.ones((61, 61), np.uint8)) > 0      # хвост и огонёк — одной дырой
    bg = smooth_fill(bg, hole)
    layers = {}
    for n, m in (("cat", cat), ("tail", tail), ("flame", flame), ("spider", spider)):
        anim.save_layer(OUT, n, A, m, layers, keep_attached_=False)
    p = os.path.join(OUT, "cat.png"); im = np.asarray(Image.open(p).convert("RGBA")).copy()
    fade = np.clip((im.shape[0] - np.arange(im.shape[0]) - 4) / 34.0, 0, 1)[:, None]
    im[..., 3] = (im[..., 3] * fade).astype(np.uint8); Image.fromarray(im).save(p)
    w, h = SIZE
    Image.fromarray(np.clip(bg[:h, :w], 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    spx = np.where(spider > 0)
    meta = dict(size=SIZE, layers=layers, base=BASE, thread_x=int((xs.min() + xs.max()) / 2) if len(xs) else THREAD_X,
                spider_top=int(spx[0].min()), spider_c=[int(spx[1].mean()), int(spx[0].mean())], fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))
    # лист проверки: слои на сером, чтобы видеть оторванные куски
    sheet = np.full((h, w, 3), 128, np.uint8)
    for n, v in layers.items():
        im = np.asarray(Image.open(os.path.join(OUT, n + ".png")).convert("RGBA")).astype(np.float32)
        x, y = v["xy"]; a = im[..., 3:] / 255
        reg = sheet[y:y + im.shape[0], x:x + im.shape[1]].astype(np.float32)
        sheet[y:y + im.shape[0], x:x + im.shape[1]] = (im[..., :3] * a + reg * (1 - a)).astype(np.uint8)
    Image.fromarray(sheet).resize((w // 2, h // 2)).save(os.path.join(OUT, "_layers.jpg"))


if __name__ == "__main__":
    main()
