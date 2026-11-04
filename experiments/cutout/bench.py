"""Стенд вырезки (владелец 04.11: «ищи способ лучше — без пробелов, без артефактов, максимально точно»).

Три рисунка разного типа (×2, как режет сцена хука):
  sofa  — кот с телефоном лежит на диване, рядом подушка, хвост свисает с огоньком (рилс 22, p1_hook);
  clock — кот в шарфе с ботинком в лапе, капли пота, огонёк на хвосте (рилс 19, d1_clock);
  tips  — кот сидит под листками-советами, два листка на голове (рилс 21, k1_tips).
Метод = функция (img_rgb_uint8, box, points) -> альфа float 0..1 той же величины. Для каждого метода и рисунка:
лист «слой на синем» + крупные куски трудных мест (усы, огонёк, касание предмета) → out/<метод>_<рисунок>.jpg,
время и пик памяти — out/stats.json. Запуск: python bench.py <метод> (методы — в methods.py)."""
import json
import os
import resource
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
CASES = {
    "sofa": dict(img="videos/22_minutka/reel/.cache/anim/p1_hook_x2.png", box=(250, 1300, 1700, 2850),
                 pos=[(700, 1900), (1100, 2050), (1450, 2400), (1100, 1700)], neg=[(420, 2050), (900, 2500), (1000, 900)],
                 zooms={"усы и подушка": (250, 1650, 750, 2150), "телефон": (950, 1500, 1250, 1950),
                        "огонёк": (1150, 2500, 1650, 2850)}),
    "clock": dict(img="videos/19_opozdal/reel/.cache/anim/d1_clock_x2.png", box=(60, 1350, 1500, 2900),
                  pos=[(850, 1900), (850, 2400), (250, 2000), (1150, 2450)], neg=[(980, 760), (1800, 2000), (600, 2950)],
                  zooms={"усы и капли": (1050, 1450, 1500, 1950), "огонёк": (60, 1500, 560, 2100),
                         "ботинок": (1050, 2200, 1450, 2650)}),
    "tips": dict(img="videos/21_znayu/reel/.cache/anim/k1_tips_x2.png", box=(40, 1200, 1500, 2900),
                 pos=[(880, 1900), (880, 2500), (300, 2400)], neg=[(1700, 2000), (300, 1500), (900, 600)],
                 zooms={"листки на голове": (650, 1250, 1350, 1650), "усы": (1150, 1600, 1600, 2000),
                        "огонёк": (40, 2000, 560, 2500)}),
}


def sheet(rgb, alpha, case, title):
    a = alpha[..., None]
    blue = np.zeros_like(rgb, np.float32) + (40, 70, 160)
    comp = rgb.astype(np.float32) * a + blue * (1 - a)
    x0, y0, x1, y1 = case["box"]
    main = Image.fromarray(comp[y0:y1, x0:x1].astype(np.uint8))
    main = main.resize((int(main.width * 900 / main.height), 900))
    zs = []
    for name, (zx0, zy0, zx1, zy1) in case["zooms"].items():
        z = Image.fromarray(comp[zy0:zy1, zx0:zx1].astype(np.uint8)).resize((300, int(300 * (zy1 - zy0) / (zx1 - zx0))))
        ImageDraw.Draw(z).text((6, 4), name, fill=(255, 255, 255), font=FONT)
        zs.append(z)
    W = main.width + 310
    S = Image.new("RGB", (W, max(900, sum(z.height + 6 for z in zs)) + 30), (30, 30, 30))
    S.paste(main, (0, 30)); y = 30
    for z in zs:
        S.paste(z, (main.width + 10, y)); y += z.height + 6
    ImageDraw.Draw(S).text((8, 4), title, fill=(255, 255, 0), font=FONT)
    return S


def run(method):
    import methods
    fn = getattr(methods, method)
    os.makedirs(OUT, exist_ok=True)
    stats_p = os.path.join(OUT, "stats.json")
    stats = json.load(open(stats_p)) if os.path.exists(stats_p) else {}
    for key, case in CASES.items():
        rgb = np.asarray(Image.open(os.path.join(ROOT, case["img"])).convert("RGB"))
        t = time.time()
        alpha = np.clip(fn(rgb, case["box"], case["pos"], case["neg"]).astype(np.float32), 0, 1)
        dt = time.time() - t
        np.save(os.path.join(OUT, f"{method}_{key}.npy"), (alpha * 255).astype(np.uint8))
        sheet(rgb, alpha, case, f"{method} · {key} · {dt:.1f} с").save(os.path.join(OUT, f"{method}_{key}.jpg"), quality=88)
        stats.setdefault(method, {})[key] = round(dt, 1)
        print(method, key, round(dt, 1), "с", flush=True)
    stats.setdefault(method, {})["peak_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 / 1024, 2)
    json.dump(stats, open(stats_p, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    run(sys.argv[1])
