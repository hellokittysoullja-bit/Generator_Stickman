"""Слои хука рилса 52 «Двоечник стал гением?» для HyperFrames — по базе рилса 13 (стандарт 24).

Рисунок gen/g1_dunce_genius.png ×2 (src/f1.png, upscale.py); координаты сняты по рисунку 1333×2000 и умножены на
2.5 (×1.25 до 1664×2496, ×2 до исходника рилса). Слои: кот целиком над партой (голова, лапы, лист с красной
каракулей, хвост с огоньком — одним куском, хвост не отдельный слой, поэтому без tail_rig), лампочка с лучами.
Парта, стул, доска — фон; фон под слоями — anim.inpaint_bg."""
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
K = 2.5                                   # рисунок 1333×2000 -> исходник рилса ×2
ORIGIN = (0, int(140 * K))                # левый верх композиции в ×2
SIZE = (3328, int(1180 * K))              # до низа парты (y 1320 на рисунке)


def P(pts):
    return [(int(x * K), int(y * K)) for x, y in pts]


CAT_REG = P([(50, 700), (250, 700), (380, 560), (470, 505), (600, 505), (622, 452), (860, 452), (885, 700),
             (965, 790), (1005, 990), (1005, 1100), (955, 1215), (250, 1215), (240, 1250), (50, 1250)])
CHAIR = P([(318, 1058), (448, 1058), (448, 1216), (318, 1216)])   # спинка стула — фон, не кот
MARKS = [P([(250, 530), (360, 680)]), P([(85, 720), (145, 785)])]  # штрихи испуга и искры огонька — с котом
SHEET = P([(637, 942), (947, 912), (950, 1215), (630, 1215)])
BULB_BOX = tuple(int(v * K) for v in (425, 180, 772, 505))
FEET = P([(700, 1220)])[0]               # ось качания кота: у края парты под листом
HEAD = P([(640, 760)])[0]
BULB_C = P([(600, 400)])[0]


def fill_holes(m):
    m = (m > 0).astype(np.uint8)
    h, w = m.shape
    ff = m.copy(); pad = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 1)
    return (m | (1 - ff)).astype(np.uint8)


def poly_mask(shape, poly):
    r = np.zeros(shape[:2], np.uint8); cv2.fillPoly(r, [np.int32(poly)], 1); return r


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.path.join(REEL, "src", "f1.png")).convert("RGB")).astype(np.float32)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    reg = poly_mask(A.shape, CAT_REG)
    ink = (((g < 120) | ((sat > 70) & (A[..., 0] > 150))) & (reg > 0)).astype(np.uint8)
    ink = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    for (x0, y0), (x1, y1) in MARKS:
        sub = np.zeros_like(reg); sub[y0:y1, x0:x1] = 1
        ink |= (((g < 150) | (sat > 60)) & (sub > 0)).astype(np.uint8)
        reg |= sub
    chair = poly_mask(A.shape, CHAIR)
    fur = (g < 95).astype(np.uint8)                       # мех кота поверх стула остаётся коту
    ink &= ~((chair > 0) & (fur == 0))
    sheet = poly_mask(A.shape, SHEET)
    core = anim.keep_attached((ink | sheet).astype(np.uint8))
    core = (fill_holes(core) & (reg | sheet) & ~((chair > 0) & (fur == 0))).astype(np.uint8)
    cat = core | (ink & ~cv2.dilate(core, np.ones((3, 3), np.uint8)))   # штрихи испуга — отдельные мазки, тоже коту
    bx0, by0, bx1, by1 = BULB_BOX
    breg = np.zeros_like(cat); breg[by0:by1, bx0:bx1] = 1
    cat[:int(497 * K), int(560 * K):int(637 * K)] = 0      # патрон лампочки — лампочке; кончик уха (x ≥ 640) — коту
    # лампочка и лучи — тушь и насыщенный жёлтый; бледный ореол вокруг — фону (иначе слой несёт белый квадрат)
    bulb = (((g < 170) | (sat > 70)) & (breg > 0)).astype(np.uint8)
    bulb = cv2.morphologyEx(bulb, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    bulb = fill_holes(bulb) & breg
    bulb &= ~cv2.dilate(cat, np.ones((5, 5), np.uint8)).astype(bool)   # ухо кота заходит в рамку лампочки — оно коту
    bulb = anim.keep_attached(bulb.astype(np.uint8))
    bg = A.copy()
    for m in (cat, bulb):
        hole = cv2.dilate(m, np.ones((17, 17), np.uint8)) > 0
        bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
    Ap, bg = anim.paper_like(A), anim.paper_like(bg)
    layers = {}
    anim.save_layer(OUT, "cat", Ap, cat, layers, keep_attached_=False)
    anim.save_layer(OUT, "bulb", Ap, bulb, layers, keep_attached_=False)
    ox, oy = ORIGIN; w, h = SIZE
    Image.fromarray(np.clip(bg[oy:oy + h, ox:ox + w], 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    for v in layers.values():
        v["xy"] = (v["xy"][0] - ox, v["xy"][1] - oy)
    rel = lambda p: (p[0] - ox, p[1] - oy)      # noqa: E731
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, feet=rel(FEET), head=rel(HEAD), bulb_c=rel(BULB_C), fps=30)
    # композиция HyperFrames — в половинном размере (диск и время рендера; кот в кадре 9:16 уже меньше половины ×2):
    # genius_hf.py увеличивает кадр обратно вдвое
    for f in ["bg.png"] + [n + ".png" for n in layers]:
        im = Image.open(os.path.join(OUT, f)); im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(os.path.join(OUT, f))
    for v in layers.values():
        v["xy"] = (v["xy"][0] // 2, v["xy"][1] // 2); v["wh"] = (v["wh"][0] // 2, v["wh"][1] // 2)
    meta.update(size=(w // 2, h // 2), feet=(meta["feet"][0] // 2, meta["feet"][1] // 2),
                head=(meta["head"][0] // 2, meta["head"][1] // 2), bulb_c=(meta["bulb_c"][0] // 2, meta["bulb_c"][1] // 2),
                scale=0.5)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
