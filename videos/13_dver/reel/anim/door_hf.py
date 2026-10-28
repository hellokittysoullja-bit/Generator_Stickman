"""Хук рилса 13 «Ты шёл и всё забыл?», движение — в HyperFrames (HTML + GSAP, рендер кадр за кадром в Chrome).

Почему не numpy, как прежние сцены (владелец 28.10: «движение с нулевой секунды… динамичней, аккуратней, несколько
движений»; сравнение HyperFrames и Remotion — videos/13_dver/reel/anim/ENGINES.md): движок двигает разобранные слои
(kit_doorway.py), а не куски плоской картинки, и даёт настоящее размытие движения.
Источник времени один — наш сборщик: время удара берётся из озвучки (ударный слог «забы́л») и вписывается в
композицию перед рендером; камера хука (anim.hook_cam), тряска, субтитры и звук — тоже наши.

Кадры движка — PNG без потерь в .cache/anim/door_hf_<подпись>/ (не в git), пересобираются сами, если поменялись
слои, композиция или время удара. Нужны Node 22 и `npx hyperframes` (скачивается при первом запуске)."""
import glob
import hashlib
import json
import math
import os
import shutil
import subprocess

import numpy as np
from PIL import Image

import anim

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = ["bg.png", "body.png", "tail.png", "cloud.png", "pencil.png", "bubble1.png", "bubble2.png", "kit.json"]
SOURCES = ["gen/d1_doorway.png", "anim/kit_doorway.py", "anim/door_hf/index.html"] + [f"anim/kit/{k}" for k in KIT]
VERSION = 1
HF = "hyperframes@0.8.214"
FPS = 30
HIT_FRAC = 0.55                    # «за-бы́л»: ударный второй слог
REEL_DIR = None
_C = {}


def _hit(ctx):
    w = ctx["words"]
    return round(w[-1][0] + HIT_FRAC * (w[-1][1] - w[-1][0]), 3)


def _render(hit):
    """Рендер композиции с этим временем удара; возвращает папку кадров."""
    sig = hashlib.md5()
    for p in [os.path.join(HERE, "door_hf", "index.html")] + [os.path.join(HERE, "kit", k) for k in KIT]:
        sig.update(open(p, "rb").read())
    sig.update(f"{hit}|{VERSION}|{HF}".encode())
    out = os.path.join(REEL_DIR, ".cache", "anim", f"door_hf_{sig.hexdigest()[:12]}")
    if len(glob.glob(os.path.join(out, "frames", "*.png"))) >= 45:
        return out
    proj = os.path.join(out, "proj"); shutil.rmtree(out, ignore_errors=True)
    shutil.copytree(os.path.join(HERE, "door_hf"), proj)
    os.makedirs(os.path.join(proj, "assets"), exist_ok=True)
    for k in KIT:
        shutil.copy(os.path.join(HERE, "kit", k), os.path.join(proj, "assets", k))
    html = os.path.join(proj, "index.html"); s = open(html, encoding="utf-8").read()
    assert 'data-hit="0.94"' in s, "в композиции нет data-hit по умолчанию"
    open(html, "w", encoding="utf-8").write(s.replace('data-hit="0.94"', f'data-hit="{hit}"'))
    env = dict(os.environ, HYPERFRAMES_TELEMETRY="0", DO_NOT_TRACK="1")
    subprocess.run(["npx", "--yes", HF, "render", "--format", "png-sequence", "-o", "frames", "--quiet"],
                   cwd=proj, env=env, check=True, stdout=subprocess.DEVNULL)
    shutil.move(os.path.join(proj, "frames"), os.path.join(out, "frames"))   # путь вывода — относительный: абсолютный CLI не принял
    shutil.rmtree(proj)
    n = len(glob.glob(os.path.join(out, "frames", "*.png")))
    if n < 45:
        raise RuntimeError(f"HyperFrames отдал {n} кадров из 45: {out}")
    return out


def prepare(ctx):
    hit = _hit(ctx)
    if _C.get("hit") != hit:
        d = _render(hit)
        meta = json.load(open(os.path.join(HERE, "kit", "kit.json")))
        a = np.asarray(Image.open(os.path.join(REEL_DIR, ".cache", "anim", "d1_doorway_x2.png")).convert("RGB")).astype(np.float32)
        _C.update(hit=hit, frames=sorted(glob.glob(os.path.join(d, "frames", "*.png"))),
                  origin=(meta["origin"][0], meta["origin"][1] - meta.get("bg_top", 0)),
                  canvas=anim.paper_like(a), cache={})
    return _C


def _world(i):
    c = _C["cache"]
    if i not in c:
        if len(c) > 2:                                     # по памяти: клипы рендерятся в 4 процессах
            c.clear()
        c[i] = np.asarray(Image.open(_C["frames"][i]).convert("RGB"))
    return c[i]


def frame(t, ctx):
    C = prepare(ctx)
    i = min(len(C["frames"]) - 1, max(0, int(round(t * FPS))))
    img = C["canvas"].copy()
    w = _world(i); x0, y0 = C["origin"]
    img[y0:y0 + w.shape[0], x0:x0 + w.shape[1]] = w
    cam = anim.hook_cam(t)
    th = t - C["hit"]
    if th >= 2 / 30:                                       # кадр отвечает на удар: тряска гаснет за ~0,15 с
        kk = math.exp(-(th - 2 / 30) / 0.12)
        cam["dx"] += 10 * kk * math.sin(th * 95); cam["dy"] += 12 * kk * math.cos(th * 77)
        cam["rot"] += 0.3 * kk * math.sin(th * 61)
    return img, cam
