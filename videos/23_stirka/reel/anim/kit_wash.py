"""Слои хука рилса 23 «Стирка час, а достаёшь неделю?» для HyperFrames — по правилу 30 (образец — рилс 22).

Рисунок gen/p1_hook.png ×2 (.cache/anim/p1_hook_x2.png); координаты ×2, сняты сеткой anim.grid 05.11.
Слои (anim.cut_sam: SAM 2.1 + матирование края + усы): кот с телефоном (тело), хвост с огоньком (сеткой с физикой,
tail_rig), стиральная машинка (трясётся на отжиме). Стекло дверцы в слое машинки прозрачное: под ним мир, который рисует
композиция (барабан с бельём и пеной, на ударе — дни). Фон под котом и машинкой — anim.plate_bg (чистая подложка)."""
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
GLASS = (1474, 1842, 316, 298)     # стекло дверцы: центр и полуоси внутри чёрного кольца — мир рисует композиция
CAT_BOX = (50, 1190, 1090, 2510)
CAT_POS = [(700, 1650), (560, 2000), (450, 2350), (640, 2350), (220, 2080), (190, 2330), (520, 1450), (800, 1480)]
CAT_NEG = [(1300, 1800), (1470, 1300), (1000, 2250)]
MACH_BOX = (860, 1030, 1990, 2500)
MACH_POS = [(1300, 1250), (1700, 1260), (1474, 1600), (1200, 2350), (1800, 2300), (1950 - 200, 1842)]
MACH_NEG = [(700, 1700), (520, 2300), (1474, 900)]
TAIL_POLY = [(60, 1950), (330, 1950), (345, 2260), (360, 2300), (360, 2430), (450, 2440), (450, 2510), (60, 2510)]
TAIL_PIVOT = (420, 2460)          # основание хвоста под лапой
FEET = (620, 2460)                # ось ёрзанья кота
HEAD = (650, 1700)
MACH_FEET = (1390, 2470)          # ось тряски машинки
WIPE = (240, 1770, 380, 1860)


def region(shape, poly):
    r = np.zeros(shape[:2], np.uint8); cv2.fillPoly(r, [np.int32(poly)], 1); return r


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.path.join(CACHE, "p1_hook_x2.png")).convert("RGB"))
    cat_a = anim.cut_sam(A, CAT_BOX, CAT_POS, CAT_NEG)
    mach_a = anim.cut_sam(A, MACH_BOX, MACH_POS, MACH_NEG, whiskers=False)
    cat = (cat_a > 0.5).astype(np.uint8)
    # машинка — твёрдый корпус: SAM оставлял дырки в светлой крышке (бумага того же тона) — внутри выпуклой оболочки
    # всё её, кроме стекла и кота
    cnt, _ = cv2.findContours((mach_a > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    hull = np.zeros(A.shape[:2], np.uint8)
    cv2.fillPoly(hull, [cv2.convexHull(max(cnt, key=cv2.contourArea))], 1)
    hull = cv2.erode(hull, np.ones((5, 5), np.uint8))
    mach_a = np.maximum(mach_a, hull.astype(np.float32))
    # за спиной кота машинка на рисунке закрыта — кот ёрзает и подлетает, и там светилась бы дыра (лист 05.11):
    # её цвет — из второй чистой подложки «тот же рисунок без кота» (машинка дорисована целиком), прозрачность — корпус
    cat_hole = cv2.dilate((cat_a > 0.05).astype(np.uint8), np.ones((61, 61), np.uint8)) > 0   # с кончиками усов на корпусе
    Am = anim.plate_bg(A, cat_hole, CACHE, what="the black cat and the phone in its paws (keep the washing machine whole)")
    mach_a = mach_a * (1 - np.clip(cat_a * 1.5, 0, 1) * (1 - hull))   # вне корпуса кот режет машинку, внутри — нет
    glass = np.zeros(A.shape[:2], np.uint8)
    cx, cy, rx, ry = GLASS
    cv2.ellipse(glass, (cx, cy), (rx, ry), 0, 0, 360, 1, -1)
    gsoft = cv2.GaussianBlur(glass.astype(np.float32), (0, 0), 2)
    mach_a = mach_a * (1 - gsoft)
    mach = (mach_a > 0.5).astype(np.uint8)
    tail_reg = region(A.shape, TAIL_POLY)
    tail, body = anim.split_part(cat & tail_reg, cat & (1 - tail_reg))
    tail, body, tail_fill = anim.claim_strokes(A.astype(np.float32), tail, body)
    tail = anim.underlap(tail, body, cat, around=(*TAIL_PIVOT, 200))
    hole = cv2.dilate(((cat_a > 0.05) | (mach_a > 0.05) | glass.astype(bool)).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
    # выше пола дыра шире: кончики усов и боковая тень машинки остаются за маской SAM и висели бы на месте, пока кот
    # ёрзает и машинка трясётся (лист 05.11); тень на полу не трогаем — она лежит, а не ездит
    wide = cv2.dilate(((cat_a > 0.05) | (mach_a > 0.05)).astype(np.uint8), np.ones((61, 61), np.uint8)) > 0
    wide[2430:] = False
    hole |= wide
    bg = anim.plate_bg(A, hole, CACHE, what="the black cat, its phone and the washing machine")
    Ap = A.astype(np.float32)
    Ap_tail = Ap
    if tail_fill.any():
        Ap_tail = cv2.inpaint(A, cv2.dilate(tail_fill, np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA).astype(np.float32)
    layers = {}
    anim.save_layer(OUT, "machine", Am, mach, layers, keep_attached_=False, alpha=mach_a)
    anim.save_layer(OUT, "tail", Ap_tail, tail.astype(np.uint8), layers, keep_attached_=True, alpha=cat_a)
    anim.save_layer(OUT, "body", Ap, body.astype(np.uint8), layers, keep_attached_=True, alpha=cat_a)
    x0, y0, x1, y1 = WIPE                                                  # кончик уса слева дальше дыры (лист 05.11)
    sub = bg[y0:y1, x0:x1]; dark = (sub.mean(2) < 238)[..., None]
    bg[y0:y1, x0:x1] = np.where(dark, np.median(sub.reshape(-1, 3), 0), sub)
    Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    tx, ty = layers["tail"]["xy"]
    tail_rig.prepare_part(os.path.join(OUT, "tail.png"), attach=(TAIL_PIVOT[0] - tx, TAIL_PIVOT[1] - ty), out_dir=OUT,
                          name="tail")
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, tail_pivot=TAIL_PIVOT, feet=FEET, head=HEAD, glass=GLASS,
                mach_feet=MACH_FEET, fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    S = np.zeros_like(Ap) + (40, 70, 160)                                    # лист слоёв на синем — глазами
    for name in ("machine", "tail", "body"):
        L = np.asarray(Image.open(os.path.join(OUT, name + ".png")).convert("RGBA")).astype(np.float32)
        x, y = layers[name]["xy"]; a = L[..., 3:] / 255
        S[y:y + L.shape[0], x:x + L.shape[1]] = L[..., :3] * a + S[y:y + L.shape[0], x:x + L.shape[1]] * (1 - a)
    both = np.concatenate([np.clip(bg, 0, 255), S], 1)[1000:2600]
    Image.fromarray(both.astype(np.uint8)).resize((1600, 625)).save(os.path.join(CACHE, "wash_layers.jpg"))
    print(json.dumps({k: v for k, v in meta.items() if k != "layers"}), {k: (v["xy"], v["wh"]) for k, v in layers.items()})


if __name__ == "__main__":
    main()
