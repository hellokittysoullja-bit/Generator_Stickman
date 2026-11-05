"""Слои хука рилса 24 «Купишь блокнот и жалко писать?» для HyperFrames — по правилу 30 (образцы — рилсы 22, 23).

Рисунок gen/p1_hook.png ×2 (.cache/anim/p1_hook_x2.png); координаты ×2, сняты сеткой anim.grid 05.11.
Слои (anim.cut_sam: SAM 2.1 + матирование края + усы): кот над столом с пером в лапе (тело), хвост с огоньком
(сеткой с физикой, tail_rig). Стол, стул, лапы под столом и блокнот — фон. Две пустые страницы блокнота — мир: в них
пишет и стирает композиция (PAGES). Фон под котом — anim.plate_bg (тот же рисунок без кота: спинка стула, край стола
и блокнота под лапами дорисованы)."""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); REEL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REEL, "..", "..", "..", "scripts"))
import anim  # noqa: E402
import tail_rig  # noqa: E402

OUT = os.path.join(HERE, "kit")
CACHE = os.path.join(REEL, ".cache", "anim")
ORIGIN = (0, 0)
SIZE = (2048, 3072)
# страницы: левая и правая, углы по часовой от левого верхнего — композиция пишет строчки внутри них
PAGES = [[(465, 1668), (1015, 1668), (1015, 1995), (310, 2018)],
         [(1025, 1668), (1568, 1663), (1722, 2018), (1025, 1995)]]
CAT_BOX = (300, 400, 1990, 1760)
CAT_POS = [(1027, 1028), (1040, 1496), (689, 1548), (728, 1444), (1274, 1574), (1820, 1535), (1690, 1080), (611, 729),
           (1261, 625)]
CAT_NEG = [(546, 1470), (1469, 1470), (910, 1880), (1300, 1880), (390, 690), (1800, 600)]
TAIL_POLY = [(1500, 840), (1990, 840), (1990, 1730), (1470, 1730), (1470, 1600), (1560, 1500), (1560, 1240), (1500, 1200)]
TAIL_PIVOT = (1508, 1630)         # основание хвоста у бока кота
FEET = (1027, 1690)               # ось наклона кота — край стола посередине
HEAD = (1027, 1000)
PEN = (832, 1736)                 # кончик пера на рисунке
WIPE = [(380, 1120, 600, 1360), (1480, 1090, 1580, 1240)]


def region(shape, poly):
    r = np.zeros(shape[:2], np.uint8); cv2.fillPoly(r, [np.int32(poly)], 1); return r


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.path.join(CACHE, "p1_hook_x2.png")).convert("RGB"))
    cat_a = anim.cut_sam(A, CAT_BOX, CAT_POS, CAT_NEG)
    cat = (cat_a > 0.5).astype(np.uint8)
    tail_reg = region(A.shape, TAIL_POLY)
    tail, body = anim.split_part(cat & tail_reg, cat & (1 - tail_reg))
    tail, body, tail_fill = anim.claim_strokes(A.astype(np.float32), tail, body)
    tail = anim.underlap(tail, body, cat, around=(*TAIL_PIVOT, 200))
    hole = cv2.dilate((cat_a > 0.05).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
    # выше стола дыра шире: кончики усов за маской SAM висели бы на месте, пока кот наклоняется (рилс 23, лист 05.11)
    wide = cv2.dilate((cat_a > 0.05).astype(np.uint8), np.ones((61, 61), np.uint8)) > 0
    wide[1640:] = False
    hole |= wide
    bg = anim.plate_bg(A, hole, CACHE, what="the black cat (keep the chair, the desk and the open notebook exactly as they are)")
    Ap = A.astype(np.float32)
    Ap_tail = Ap
    if tail_fill.any():
        Ap_tail = cv2.inpaint(A, cv2.dilate(tail_fill, np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA).astype(np.float32)
    layers = {}
    anim.save_layer(OUT, "tail", Ap_tail, tail.astype(np.uint8), layers, keep_attached_=True, alpha=cat_a)
    anim.save_layer(OUT, "body", Ap, body.astype(np.uint8), layers, keep_attached_=True, alpha=cat_a)
    for x0, y0, x1, y1 in WIPE:                                           # кончики усов дальше дыры (лист 05.11)
        sub = bg[y0:y1, x0:x1]; dark = (sub.mean(2) < 238)[..., None]
        bg[y0:y1, x0:x1] = np.where(dark, np.median(sub.reshape(-1, 3), 0), sub)
    pm = np.zeros(A.shape[:2], np.uint8)
    for q in PAGES:
        cv2.fillPoly(pm, [np.int32(q)], 1)
    page_rgb = [int(v) for v in np.median(A[cv2.erode(pm, np.ones((41, 41), np.uint8)) > 0].reshape(-1, 3), 0)]
    Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    tx, ty = layers["tail"]["xy"]
    tail_rig.prepare_part(os.path.join(OUT, "tail.png"), attach=(TAIL_PIVOT[0] - tx, TAIL_PIVOT[1] - ty), out_dir=OUT,
                          name="tail")
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, tail_pivot=TAIL_PIVOT, feet=FEET, head=HEAD, pages=PAGES, page_rgb=page_rgb, pen=PEN,
                fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    S = np.zeros_like(Ap) + (40, 70, 160)                                    # лист слоёв на синем — глазами
    for name in ("tail", "body"):
        L = np.asarray(Image.open(os.path.join(OUT, name + ".png")).convert("RGBA")).astype(np.float32)
        x, y = layers[name]["xy"]; a = L[..., 3:] / 255
        S[y:y + L.shape[0], x:x + L.shape[1]] = L[..., :3] * a + S[y:y + L.shape[0], x:x + L.shape[1]] * (1 - a)
    both = np.concatenate([np.clip(bg, 0, 255), S], 1)[350:2500]
    Image.fromarray(both.astype(np.uint8)).resize((1600, 840)).save(os.path.join(CACHE, "note_layers.jpg"))
    print(json.dumps({k: v for k, v in meta.items() if k not in ("layers", "pages")}), {k: (v["xy"], v["wh"]) for k, v in layers.items()})


if __name__ == "__main__":
    main()
