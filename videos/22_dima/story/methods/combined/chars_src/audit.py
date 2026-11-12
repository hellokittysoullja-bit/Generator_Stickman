"""Проверка слоёв без артефактов: (1) альфа внутри силуэта (дальше 2 px от края) — только 255;
(2) вырезки ×3 частей на кадрах 0, 17, 39, 69, 81 поверх фона комнаты — для глаз.
python3 audit.py room.png out_dir"""
import sys
import numpy as np
from PIL import Image, ImageFilter

BG, OUT = sys.argv[1], sys.argv[2]
L = ("L_dima", "L_plaid", "L_cat")
here = __file__.rsplit("/", 1)[0] + "/../chars"
worst = {}
for f in range(90):
    for l in L:
        a = np.array(Image.open(f"{here}/{l}/{f:04d}.png"))[..., 3]
        sil = Image.fromarray(((a > 0) * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5))   # эрозия на 2 px
        inside = np.array(sil) > 0
        bad = inside & (a < 255)
        worst[l] = max(worst.get(l, (0, 0, 0))[0], bad.sum()), f if bad.sum() >= worst.get(l, (0, 0, 0))[0] else worst[l][1], inside.sum()
for l, (n, f, tot) in worst.items():
    print(f"{l}: пикселей с альфой <255 глубже 2 px от края — максимум {n} из {tot} (кадр {f})")
parts = {"face": (150, 660, 470, 1010), "hand_phone": (550, 650, 760, 960), "cat_head": (740, 880, 980, 1100),
         "tail_flame": (960, 840, 1080, 1250), "plaid": (300, 1150, 700, 1500)}
bg = Image.open(BG).convert("RGBA")
for f in (0, 17, 39, 69, 81):
    im = bg.copy()
    for l in L:
        im.alpha_composite(Image.open(f"{here}/{l}/{f:04d}.png"))
    row = [im.crop(b).resize(((b[2] - b[0]) * 3 // 2, (b[3] - b[1]) * 3 // 2), Image.LANCZOS) for b in parts.values()]
    for (name, b), r in zip(parts.items(), row):
        im.crop(b).resize(((b[2] - b[0]) * 3, (b[3] - b[1]) * 3), Image.LANCZOS).convert("RGB").save(f"{OUT}/a_{f:02d}_{name}.png")
    W_ = sum(r.width for r in row) + 10 * len(row)
    sheet = Image.new("RGB", (W_, max(r.height for r in row)), (20, 20, 20))
    x = 0
    for r in row:
        sheet.paste(r.convert("RGB"), (x, 0)); x += r.width + 10
    sheet.save(f"{OUT}/sheet_{f:02d}.png")
