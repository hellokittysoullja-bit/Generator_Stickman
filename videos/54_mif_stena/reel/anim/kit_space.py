"""Слои хука рилса 54 «Видишь стену из космоса?» для HyperFrames — по образцу рилса 52 (kit_genius.py).

Рисунок gen/g1_space_look.png (1664×2496) ×2 = src/f1.png (3328×4992); координаты сняты по уменьшенному виду 832×1248
и умножены на K=4. Слои: кот целиком (шлем, скафандр, бинокль, хвост с огоньком, капля пота — одним куском), знак «?»
(отдельно — на ударе выскакивает крупнее), иллюминатор с планетой (кольцо и Земля — один слой; под котом он
дорисован LaMa, чтобы при отшатывании кота не оставалась дыра). Фон — бумага (anim.inpaint_bg под обоими).
F1=путь — подмена исходника для проб."""
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
K = 4.0                                   # вид 832×1248 -> исходник рилса ×2 (3328×4992)
ORIGIN = (0, 800)                         # левый верх композиции в ×2
SIZE = (3328, 4192)                       # до низа рисунка


def P(pts):
    return [(int(x * K), int(y * K)) for x, y in pts]


CAT_REG = P([(0, 340), (195, 340), (205, 212), (672, 212), (672, 480), (640, 520), (606, 572), (574, 620), (570, 748),
             (530, 776), (440, 815), (400, 840), (400, 892), (0, 892)])
Q_BOX = tuple(int(v * K) for v in (668, 352, 740, 440))
PORT = P([(424, 1248), (424, 1000), (436, 880), (466, 790), (516, 700), (576, 628), (656, 568), (740, 532), (832, 500),
          (832, 1248)])
PIVOT = P([(330, 700)])[0]               # ось качания кота: центр скафандра
HEAD = P([(430, 450)])[0]
Q_C = P([(704, 396)])[0]
PORT_C = P([(700, 900)])[0]


def fill_holes(m):
    m = (m > 0).astype(np.uint8)
    h, w = m.shape
    big = np.ones((h + 2, w + 2), np.uint8); big[1:-1, 1:-1] = m; big[0, :] = 0; big[:, 0] = 0   # правый и нижний край — «стена»
    ff = big.copy(); pad = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 2)
    return (big[1:-1, 1:-1] | (ff[1:-1, 1:-1] != 2)).astype(np.uint8)


def poly_mask(shape, poly):
    r = np.zeros(shape[:2], np.uint8); cv2.fillPoly(r, [np.int32(poly)], 1); return r


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.environ.get("F1") or os.path.join(REEL, "src", "f1.png")).convert("RGB")).astype(np.float32)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    non = ((g < 232) | (sat > 38)).astype(np.uint8)
    reg = poly_mask(A.shape, CAT_REG)
    ink = cv2.morphologyEx(non & reg, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8)) & reg
    core = anim.keep_attached(ink)
    cat = (fill_holes(core) & reg).astype(np.uint8)
    cat |= (ink & ~cv2.dilate(cat, np.ones((3, 3), np.uint8))).astype(np.uint8)       # капля, усы — мазки рядом с котом
    qx0, qy0, qx1, qy1 = Q_BOX
    qreg = np.zeros_like(cat); qreg[qy0:qy1, qx0:qx1] = 1
    q = cv2.morphologyEx(((g < 200) & (qreg > 0)).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    q = anim.keep_attached(q)
    preg = poly_mask(A.shape, PORT)
    pn = cv2.morphologyEx(non & preg, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8)) & preg
    port = (fill_holes(pn) & preg).astype(np.uint8)
    port = anim.keep_attached(port, reach=40)
    port &= ~cv2.dilate(cat, np.ones((3, 3), np.uint8))           # там, где кот закрывает иллюминатор, слой не нужен — его дорисует LaMa
    # под котом иллюминатор дорисован целиком: для слоя планеты — без кота; для фона — без обоих
    cat_hole = cv2.dilate(cat, np.ones((9, 9), np.uint8)) > 0
    port_full = anim.inpaint_bg(A, cat_hole & (preg > 0), cache_dir=CACHE) if (cat_hole & (preg > 0)).any() else A
    port_full = np.where((preg > 0)[..., None], port_full, A)
    port_mask = (fill_holes(pn | (cv2.dilate(cat, np.ones((9, 9), np.uint8)) & preg)) & preg).astype(np.uint8)
    port_mask = anim.keep_attached(port_mask, reach=40)
    bg = A.copy()
    for m in (cat, q, port_mask):
        hole = cv2.dilate(m, np.ones((17, 17), np.uint8)) > 0
        bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
    Ap, bg, port_img = anim.paper_like(A), anim.paper_like(bg), anim.paper_like(port_full)
    layers = {}
    anim.save_layer(OUT, "cat", Ap, cat, layers, keep_attached_=False)
    anim.save_layer(OUT, "q", Ap, q, layers, keep_attached_=False)
    anim.save_layer(OUT, "planet", port_img, port_mask, layers, keep_attached_=False)
    ox, oy = ORIGIN; w, h = SIZE
    Image.fromarray(np.clip(bg[oy:oy + h, ox:ox + w], 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    for v in layers.values():
        v["xy"] = (v["xy"][0] - ox, v["xy"][1] - oy)
    rel = lambda p: (p[0] - ox, p[1] - oy)      # noqa: E731
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, pivot=rel(PIVOT), head=rel(HEAD), q_c=rel(Q_C), port_c=rel(PORT_C), fps=30)
    for f in ["bg.png"] + [n + ".png" for n in layers]:
        im = Image.open(os.path.join(OUT, f)); im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(os.path.join(OUT, f))
    for v in layers.values():
        v["xy"] = (v["xy"][0] // 2, v["xy"][1] // 2); v["wh"] = (v["wh"][0] // 2, v["wh"][1] // 2)
    h2 = lambda p: (p[0] // 2, p[1] // 2)     # noqa: E731
    meta.update(size=(w // 2, h // 2), pivot=h2(meta["pivot"]), head=h2(meta["head"]), q_c=h2(meta["q_c"]),
                port_c=h2(meta["port_c"]), scale=0.5)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
