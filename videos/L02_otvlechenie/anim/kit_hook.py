"""Слои хука L02 для HyperFrames: «Ты убираешь телефон, выключаешь уведомления, садишься за дело, а через пять минут
почему-то стоишь у холодильника?».

Две сцены одного хука: стол (library 10, без кота) и кухня (library 103 «кот у открытого холодильника», кот убран), и
три куска с листа слоёв gen/hook_sheet.png (+1 рисунок, владелец 28.10): кот на стуле с карандашом, кот у холодильника
оглядывается пойманным, телефон экраном вниз. Всё отражено по горизонтали: на листе загнутое ухо у кота справа, а по
приметам героя (look/hero_marks.txt) оно слева от зрителя — зеркалим кусок, а вместе с ним и фоны, чтобы кот у
холодильника тянулся к дверце, а не от неё.

Кот из 103 убирается по рецепту рилса 13 (kit_doorway.py): маска тушью в многоугольнике, дыра стены и пола
заливается медианой своей строки из чистых столбцов слева, у дверцы холодильника — по столбцам (вертикальная кромка),
шов мягкий. Координаты сняты сеткой anim.grid 28.10 (рисунок 103 — 1531×1027)."""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import anim  # noqa: E402

LIB = os.path.join(ROOT, "library", "cat", "originals")
KITCHEN = "2026-10-27_gen_cx_gpt-image-2_eb2640c6.png"     # 103
DESK = "2026-10-07_look_style_1_desk_1c1c5a17.jpg"           # 10
OUT = os.path.join(HERE, "kit")
CAT_POLY = [(215, 430), (290, 420), (300, 500), (420, 330), (700, 270), (760, 330), (800, 470), (840, 540), (845, 640),
            (760, 700), (700, 850), (450, 850), (450, 790), (300, 800), (215, 740)]
SMOKE = (255, 420, 330, 560)       # дымок над огоньком хвоста
CLEAN_X = (0, 90)                  # чистые столбцы стены и пола слева от хвоста (бумажный комок ниже — не в них)
EDGE_X = (790, 845)                # кромка дверцы холодильника за лапой: заливка по столбцам
FLAME = (296, 540)                 # огонёк хвоста кота 103


def rgba(img, m):
    ys, xs = np.where(m > 0.02)
    x0, y0, x1, y1 = xs.min() - 4, ys.min() - 4, xs.max() + 5, ys.max() + 5
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8)
    return np.dstack([img[y0:y1, x0:x1], 255 * a[y0:y1, x0:x1]]).clip(0, 255).astype(np.uint8), (int(x0), int(y0))


def kitchen():
    A = np.asarray(Image.open(os.path.join(LIB, KITCHEN)).convert("RGB")).astype(np.float32)
    reg = np.zeros(A.shape[:2], np.uint8); cv2.fillPoly(reg, [np.int32(CAT_POLY)], 1)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    m = (((g < 175) | (sat > 45)) & (reg > 0)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    m = np.zeros_like(m); cv2.drawContours(m, cs, -1, 1, -1)
    x0, y0, x1, y1 = SMOKE; m[y0:y1, x0:x1] |= (g[y0:y1, x0:x1] < 215).astype(np.uint8)   # дымок светлее туши
    cv2.circle(m, FLAME, 42, 1, -1)                     # свечение огонька вокруг кончика хвоста
    hole = cv2.dilate(m, np.ones((13, 13), np.uint8)) > 0
    bg = A.copy()
    # каждая строка дыры — от её левого края к правому: стена здесь с плавным переходом тона, и цвет строки с края
    # картинки оставлял светлый силуэт кота (замер 28.10); край берётся медианой 6 px за краем дыры, не одним пикселем
    for y in range(A.shape[0]):
        row = hole[y]
        if not row.any():
            continue
        xs = np.where(row)[0]
        runs = np.split(xs, np.where(np.diff(xs) > 1)[0] + 1)
        for r in runs:
            lft, rr = r[0] - 1, r[-1] + 1
            cl = np.median(A[y, max(0, lft - 6):lft + 1], axis=0) if lft >= 0 else None
            cr = np.median(A[y, rr:rr + 7], axis=0) if rr < A.shape[1] else None
            cl = cr if cl is None else cl; cr = cl if cr is None else cr
            if rr >= EDGE_X[0] - 8:                     # правый край — дверца холодильника: её серый не тянуть через стену
                cr = cl
            u = np.linspace(0, 1, len(r))[:, None]
            bg[y, r] = cl * (1 - u) + cr * u
    # зерно бумаги: ровная заливка гладкая — добавить шум с соседней чистой стены той же яркости
    noise = A[:, CLEAN_X[0]:CLEAN_X[1]] - cv2.GaussianBlur(A[:, CLEAN_X[0]:CLEAN_X[1]], (0, 0), 3)
    tile = np.tile(noise, (1, A.shape[1] // noise.shape[1] + 1, 1))[:, :A.shape[1]]
    bg[hole] += tile[hole]
    for x in range(*EDGE_X):
        col = hole[:, x]
        if col.any():
            ys = np.where(~col)[0]
            for c in range(3):
                bg[col, x, c] = np.interp(np.where(col)[0], ys, A[ys, x, c])
    soft = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 2)[..., None]
    return np.clip(A * (1 - soft) + bg * soft, 0, 255).astype(np.uint8)


def main():
    os.makedirs(OUT, exist_ok=True)
    k = kitchen()[:, ::-1]
    Image.fromarray(k).save(os.path.join(OUT, "kitchen.png"))
    d = np.asarray(Image.open(os.path.join(LIB, DESK)).convert("RGB"))[:, ::-1]
    Image.fromarray(d).save(os.path.join(OUT, "desk.png"))
    sheet = np.asarray(Image.open(os.path.join(HERE, "gen", "hook_sheet.png")).convert("RGB")).astype(np.float32)
    sheet = anim.paper_like(sheet)[:, ::-1]
    obs = anim.ink_objects(sheet, min_area=4000)
    obs.sort(key=lambda m: -np.where(m)[1].mean())       # после зеркала: справа налево -> кот на стуле, у холодильника, телефон
    meta = dict(kitchen=list(k.shape[1::-1]), desk=list(d.shape[1::-1]), pieces={})
    for name, m in zip(("cat_desk", "cat_fridge", "phone"), obs):
        im, xy = rgba(sheet, m)
        Image.fromarray(im).save(os.path.join(OUT, name + ".png")); meta["pieces"][name] = dict(wh=im.shape[1::-1], at=xy)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
