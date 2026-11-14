"""Слои хука рилса 69 «Всем ответил, кроме одного?» для HyperFrames — по образцу рилса 68 (kit_wipe.py).

Рисунок gen/g1_one_unread.png (1664×2496) ×2 = src/f1.png (3328×4992); координаты сняты по сетке исходника и умножены
на K=2. Слои: кот (голова, тело, лапы с телефоном — одним куском; под каплей пота мех, под красной точкой экран),
хвост с огоньком — в слое кота (дрожит с телом; отдельный слой хвоста требует сетки tail_rig), капля пота, красная точка непрочитанного. Фон — бумага (anim.inpaint_bg под
всеми слоями, потом ровная бумага везде, кроме тени на полу). Композиция — весь рисунок в половинном размере, её
координаты = координаты исходника. F1=путь — подмена исходника для проб."""
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


def P(pts):
    return [(int(x * K), int(y * K)) for x, y in pts]


TAIL = P([(1340, 990), (1664, 990), (1664, 2010), (1175, 2010), (1160, 1940), (1185, 1800), (1250, 1700),
          (1240, 1560), (1262, 1430), (1345, 1330)])
DROP = ((1072, 958), 52)                 # капля пота на лбу
DOT = ((873, 1430), 27)                  # красная точка на экране телефона
TAIL_PIV = P([(1190, 1900)])[0]          # основание хвоста у тела
CAT_PIV = P([(830, 1980)])[0]            # кот сидит: ось дрожи — у пола под ним
FLOOR_Y = 2035                           # ниже — тень на полу (остаётся фоном)
PAW_Y = 1945                             # от сюда до пола у кота — только тёмная тушь лап (без светлой тени)


def fill_holes(m):
    m = (m > 0).astype(np.uint8)
    h, w = m.shape
    big = np.zeros((h + 2, w + 2), np.uint8); big[1:-1, 1:-1] = m
    ff = big.copy(); pad = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 2)
    return (big[1:-1, 1:-1] | (ff[1:-1, 1:-1] != 2)).astype(np.uint8)


def poly_mask(shape, poly):
    r = np.zeros(shape[:2], np.uint8); cv2.fillPoly(r, [np.int32(poly)], 1); return r


def disc(shape, c, r):
    m = np.zeros(shape[:2], np.uint8); cv2.circle(m, (int(c[0] * K), int(c[1] * K)), int(r * K), 1, -1); return m


def ring_color(A, c, r, w=14):
    outer = disc(A.shape, c, r + w); inner = disc(A.shape, c, r)
    return np.median(A[(outer > 0) & (inner == 0)].reshape(-1, 3), axis=0)


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.environ.get("F1") or os.path.join(REEL, "src", "f1.png")).convert("RGB")).astype(np.float32)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    H, Wd = g.shape
    floor = np.zeros((H, Wd), bool); floor[int(FLOOR_Y * K):] = True
    tailp = poly_mask(A.shape, TAIL)
    non = ((g < 200) | (sat > 50)) & ~floor
    low = np.zeros((H, Wd), bool); low[int(PAW_Y * K):] = True
    non &= ~(low & (g >= 140))
    ink = cv2.morphologyEx(non.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    # хвост: всё нарисованное в его многоугольнике (с огоньком), главный кусок
    tail = fill_holes(anim.keep_attached(ink & tailp)) & tailp
    # кот: остальное, главный кусок с усами
    cat = anim.keep_attached(ink & (1 - tailp), reach=6)
    cat = fill_holes(cat) & (1 - tailp)
    cat |= ((g < 160) & ~floor & ~low & (tailp == 0) & ~cv2.dilate(cat, np.ones((3, 3), np.uint8)).astype(bool)).astype(np.uint8)
    cat = anim.keep_attached(cat, reach=4)
    drop_d, dot_d = disc(A.shape, *DROP), disc(A.shape, *DOT)
    drop = ((g < 235) & (drop_d > 0)).astype(np.uint8)        # капля: голубая с контуром, без меха вокруг
    drop = fill_holes(cv2.morphologyEx(drop, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))) & drop_d
    redd = ((A[..., 0] - A[..., 2] > 50) & (dot_d > 0)).astype(np.uint8)
    redd = fill_holes(cv2.dilate(redd, np.ones((9, 9), np.uint8))) & dot_d   # точка с тёмным ободком
    # под каплей — мех, под точкой — экран: слой кота без дыр (капля уползает, точка пульсирует)
    Ap = anim.paper_like(A)
    Acat = Ap.copy()
    for m, (c, r) in ((drop, DROP), (redd, DOT)):
        hole = cv2.dilate(m.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
        col = ring_color(Ap, c, r)
        a = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 3)[..., None]
        Acat = Acat * (1 - a) + col * a
    bg = A.copy()
    for part in (cat | tail | ink,):
        hole = cv2.dilate(part.astype(np.uint8), np.ones((17, 17), np.uint8)) > 0
        bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
    bg = anim.paper_like(bg)
    # всё выше пола — ровная бумага (LaMa оставляла призраки меха и хвоста; кот дрожит, края открываются)
    paper = np.median(bg[int(100 * K):int(350 * K), int(100 * K):int(1500 * K)].reshape(-1, 3), axis=0)
    wipe = np.zeros((H, Wd), np.float32); wipe[:int((PAW_Y - 20) * K)] = 1
    wipe = cv2.GaussianBlur(wipe, (0, 0), 10)[..., None]
    bg = bg * (1 - wipe) + paper * wipe
    layers = {}
    # хвост — в слое кота (без отдельной сетки tail_rig): дрожит вместе с телом
    anim.save_layer(OUT, "cat", Acat, (cat | tail).astype(np.uint8), layers, keep_attached_=False)
    anim.save_layer(OUT, "drop", Ap, drop, layers, keep_attached_=False)
    anim.save_layer(OUT, "dot", Ap, redd, layers, keep_attached_=False)
    Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    for f in ["bg.png"] + [n + ".png" for n in layers]:
        im = Image.open(os.path.join(OUT, f)); im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(os.path.join(OUT, f))
    for v in layers.values():
        v["xy"] = (v["xy"][0] // 2, v["xy"][1] // 2); v["wh"] = (v["wh"][0] // 2, v["wh"][1] // 2)
    h2 = lambda p: (p[0] // 2, p[1] // 2)     # noqa: E731
    meta = dict(origin=(0, 0), size=(Wd // 2, H // 2), layers=layers, cat=h2(CAT_PIV),
                drop=list(DROP[0]), dot=list(DOT[0]), fps=30, scale=0.5)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
