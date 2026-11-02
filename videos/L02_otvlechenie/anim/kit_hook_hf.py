"""Слои хука L02 для HyperFrames в размере мира сборщика: холст 16:9 × UPSCALE, как у кадра 1 (библиотека 103).

Сборщик кладёт кадр 1 на бумагу так: рисунок 1531×1027, бумага подведена к крему (`canvas.retint`), строки 120–981
(центр рисунка, 16:9), увеличение ×2 нейросетью (`upscale`), фактура бумаги. Фоны хука проходят тот же путь, чтобы
кадр сцены не отличался по бумаге и резкости от соседних: кухня (kit/kitchen.png, кот убран, зеркало) — те же строки,
стол (kit/desk.png, библиотека 10) — растянут на ширину 1531 и обрезан так, чтобы стол целиком был в кадре. Куски с
листа (коты, телефон) — тоже ×2 нейросетью по крему, альфа — Lanczos. Выход — anim/hf/assets/*.png + geom.json."""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import canvas  # noqa: E402
import upscale  # noqa: E402

KIT = os.path.join(HERE, "kit")
OUT = os.path.join(HERE, "hf", "assets")
CACHE = os.path.join(HERE, "..", "media_plan", "upscale")
S = 2                                   # frame_clip.UPSCALE
W, H = 1531, 861                        # холст кадра 1 (canvas.prepare рисунка 103: строки 120–981)
KITCHEN_TOP = 120
DESK_TOP = 166                          # стол 1264×848 ×1.211 → 1531×1027: лампа и ножки стола в кадре


def plate(a):
    col, share = canvas.paper_color(a)
    return canvas.retint(a, col) if canvas.is_paper(col, share) else a


def bg(name, a, top, seed):
    a = plate(a.astype(np.float32))[top:top + H]
    big = upscale.upscale(np.clip(a, 0, 255).round().astype(np.uint8), S, cache_dir=CACHE)
    big = canvas.bake_texture(big, canvas.paper_texture(), seed=seed)
    Image.fromarray(big).save(os.path.join(OUT, name + ".png"))


def piece(name):
    im = np.asarray(Image.open(os.path.join(KIT, name + ".png")).convert("RGBA")).astype(np.float32)
    a = im[..., 3:] / 255
    rgb = im[..., :3] * a + np.float32(canvas.CREAM) * (1 - a)          # край куска — на креме, не на чёрном
    big = upscale.upscale(np.clip(rgb, 0, 255).round().astype(np.uint8), S, cache_dir=CACHE)
    al = Image.fromarray(im[..., 3].astype(np.uint8)).resize(big.shape[1::-1], Image.LANCZOS)
    Image.fromarray(np.dstack([big, np.asarray(al)])).save(os.path.join(OUT, name + ".png"))
    return list(big.shape[1::-1])


def main():
    os.makedirs(OUT, exist_ok=True)
    k = np.asarray(Image.open(os.path.join(KIT, "kitchen.png")).convert("RGB"))
    bg("kitchen", k, KITCHEN_TOP, seed=1)
    d = Image.open(os.path.join(KIT, "desk.png")).convert("RGB").resize((W, 1027), Image.LANCZOS)
    bg("desk", np.asarray(d), DESK_TOP, seed=2)
    geom = dict(stage=[W * S, H * S], scale=S, pieces={n: piece(n) for n in ("cat_desk", "cat_fridge", "phone")})
    json.dump(geom, open(os.path.join(OUT, "geom.json"), "w"), indent=1)
    print(geom)


if __name__ == "__main__":
    main()
