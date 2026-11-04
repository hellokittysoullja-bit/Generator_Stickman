"""Эксперимент владельца 04.11: BiRefNet (вырезка фона нейросетью) против нынешней нарезки слоёв — на хуке рилса 22.

Шаг 1 (`mask`, отдельный процесс — BiRefNet на CPU берёт ~14 ГБ, 06.10 ронял контейнер): маска кота по кадру хука
p1_hook ×2 → experiments/birefnet/out/mask_birefnet.png, время и пик памяти — в out/stats.json.
Шаг 2 (`kit`): тот же kit_night.py, но тело и хвост режутся маской BiRefNet (внутри тех же многоугольников кота и хвоста),
фон — тем же inpaint → out/kit_bir/. Шаг 3 (`video`): одна и та же композиция night_hf с обоими наборами слоёв, без
камеры, бок о бок «сейчас | BiRefNet» → out/compare.mp4 и лист кадров out/compare_sheet.jpg."""
import json
import os
import resource
import shutil
import subprocess
import sys
import time

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REEL = os.path.join(ROOT, "videos", "22_minutka", "reel")
ANIM = os.path.join(REEL, "anim")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
X2 = os.path.join(REEL, ".cache", "anim", "p1_hook_x2.png")
sys.path.insert(0, os.path.join(ROOT, "scripts")); sys.path.insert(0, ANIM)


def mask():
    from rembg import new_session, remove
    os.makedirs(OUT, exist_ok=True)
    t = time.time()
    sess = new_session("birefnet-general")
    t_load = time.time() - t
    im = Image.open(X2).convert("RGB")
    x0, y0, x1, y1 = 250, 1300, 1700, 2850                     # рамка кота с хвостом, ×2 (как рамка судьи у опыта 06.10)
    t = time.time()
    a = remove(im.crop((x0, y0, x1, y1)), session=sess, only_mask=True)
    t_run = time.time() - t
    full = Image.new("L", im.size, 0); full.paste(a, (x0, y0))
    full.save(os.path.join(OUT, "mask_birefnet.png"))
    st = dict(load_sec=round(t_load, 1), run_sec=round(t_run, 1),
              peak_rss_gb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 / 1024, 2))
    json.dump(st, open(os.path.join(OUT, "stats.json"), "w"), indent=1); print(st)


def kit():
    import cv2
    import kit_night as K
    import anim
    import tail_rig
    A = np.asarray(Image.open(X2).convert("RGB")).astype(np.float32)
    m = np.asarray(Image.open(os.path.join(OUT, "mask_birefnet.png"))) > 127
    cat_reg, tail_reg = K.region(A.shape, K.CAT_POLY), K.region(A.shape, K.TAIL_POLY)
    phone = K.region(A.shape, K.PHONE_POLY)
    cat = anim.keep_attached(((m & (cat_reg > 0)) | (phone > 0)).astype(np.uint8))
    tail = (anim.keep_attached((m & (tail_reg > 0)).astype(np.uint8)) & (1 - cat)).astype(np.uint8)
    full = (cat | tail).astype(np.uint8)
    tail, body = anim.split_part(tail, cat)
    tail, body, tail_fill = anim.claim_strokes(A, tail, body)
    tail = anim.underlap(tail, body, full, around=(*K.TAIL_PIVOT, 200))
    hole = cv2.dilate(full, np.ones((15, 15), np.uint8)) > 0
    bg = anim.inpaint_bg(A, hole, cache_dir=os.path.join(REEL, ".cache", "anim"))
    out = os.path.join(OUT, "kit_bir"); shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    layers = {}
    for name, mm in [("tail", tail), ("body", body)]:
        anim.save_layer(out, name, A, mm.astype(np.uint8), layers, keep_attached_=True)
    Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).save(os.path.join(out, "bg.png"))
    tx, ty = layers["tail"]["xy"]
    tail_rig.prepare_part(os.path.join(out, "tail.png"), attach=(K.TAIL_PIVOT[0] - tx, K.TAIL_PIVOT[1] - ty), out_dir=out, name="tail")
    meta = json.load(open(os.path.join(ANIM, "kit", "kit.json"))); meta["layers"] = layers
    json.dump(meta, open(os.path.join(out, "kit.json"), "w"), indent=1)
    print("kit_bir", {k: (v["xy"], v["wh"]) for k, v in layers.items()})


def video():
    import anim_hf
    import night_hf as N
    words = json.load(open(os.path.join(REEL, "voice", "words.json")))[:6]
    hit = round(words[-1]["start"] + 0.3 + N.HIT_FRAC * (words[-1]["end"] - words[-1]["start"]), 3)   # пауза 0,3 перед «ночь»
    frames = {}
    for tag, kit_dir in [("now", os.path.join(ANIM, "kit")), ("bir", os.path.join(OUT, "kit_bir"))]:
        k = json.load(open(os.path.join(kit_dir, "kit.json")))

        def prep(p, v, kit_dir=kit_dir, k=k):
            N.place_layers(p)
            mesh = json.load(open(os.path.join(p, "assets", "tail_mesh.json")))
            motion = N.tail_rig.extract_motion(p, "tail", N.DUR)
            ang = N.tail_rig.simulate(mesh, motion, tuple(k["layers"]["tail"]["xy"]), v["hit"], N.DUR)
            json.dump(ang, open(os.path.join(p, "assets", "tail_angles.json"), "w"))
        sc = anim_hf.Scene(os.path.join(ANIM, "night_hf"), kit_dir, fps=30, duration=N.DUR, cache_dir=os.path.join(OUT, "cache"), name=f"cmp_{tag}",
                           version=1, prepare=prep, extra=[N.tail_rig.__file__])
        t = time.time()
        sc.render({"hit": hit, "kit": {n: k[n] for n in ("feet", "head", "pane")}})
        print(tag, "рендер", round(time.time() - t, 1), "с")
        frames[tag] = sc
    tmp = os.path.join(OUT, "cmp_frames"); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    n = int(N.DUR * 30); sheet = []
    for i in range(n):
        t = i / 30
        a, b = frames["now"].frame(t), frames["bir"].frame(t)
        crop = lambda x: x[1300:2900, 200:1800]                  # кот и хвост крупно — там и разница
        row = np.concatenate([crop(a), np.full((1600, 24, 3), 255, np.float32), crop(b)], 1)
        im = Image.fromarray(np.clip(row, 0, 255).astype(np.uint8)).resize((1608, 1000))
        im.save(os.path.join(tmp, f"{i:04d}.png"))
        if i in (0, 15, 30, int(hit * 30) + 2, int(hit * 30) + 8, 80):
            sheet.append(im.resize((804, 500)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", os.path.join(tmp, "%04d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "18", os.path.join(OUT, "compare.mp4")], check=True)
    S = Image.new("RGB", (804 * 2, 500 * 3), "white")
    for j, im in enumerate(sheet):
        S.paste(im, ((j % 2) * 804, (j // 2) * 500))
    S.save(os.path.join(OUT, "compare_sheet.jpg"), quality=88)
    print("ok", os.path.join(OUT, "compare.mp4"))


if __name__ == "__main__":
    {"mask": mask, "kit": kit, "video": video}[sys.argv[1]]()
