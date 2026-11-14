"""Хук рилса 53 «Восемь пауков за ночь?» на HyperFrames — по базе рилса 13 (стандарт 24) и правилам 25–29.

Рисунок gen/g1_mouth_guard.png разобран на слои anim/kit_spider.py (anim.save_layer, фон — anim.inpaint_bg);
композиция anim/spider_hf/index.html (размер рисунка, до y=1800): с кадра 0 кот дрожит под одеялом, паук качается на
нити и ползёт вниз, хвост качается, огонёк мерцает; на ударном «ночь» паук срывается к пасти, кот подпрыгивает,
огонёк вспыхивает. Время удара — из озвучки; камера хука — anim.hook_cam(t, hit=…) (правила 28–29) и тряска — здесь.
Кадр композиции увеличивается вдвое до исходника рилса. Кадры — кэш .cache/anim/spider_hf_<подпись>/ (не в git)."""
import json
import math
import os

import cv2
import numpy as np
from PIL import Image

import anim
import anim_hf

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = ["bg.png", "cat.png", "tail.png", "flame.png", "spider.png", "kit.json"]
SOURCES = ["gen/g1_mouth_guard.png", "anim/kit_spider.py", "anim/spider_hf/index.html"] + [f"anim/kit/{k}" for k in KIT]
VERSION = 1
FPS, DUR = 30, 2.0
HIT_FRAC = 0.2                      # «ночь»: ударный слог в начале слова
REEL_DIR = None
_C = {}


def _kit():
    return json.load(open(os.path.join(HERE, "kit", "kit.json")))


def _hit(ctx):
    w = ctx["words"]
    return round(w[-1][0] + HIT_FRAC * (w[-1][1] - w[-1][0]), 3)


def prepare(ctx):
    hit = _hit(ctx)
    if _C.get("hit") != hit:
        k = _kit()
        kit = {n: k[n] for n in ("layers", "base", "thread_x", "spider_top")}
        kit["layers"] = {n: {"xy": v["xy"]} for n, v in kit["layers"].items()}
        hf = anim_hf.Scene(os.path.join(HERE, "spider_hf"), os.path.join(HERE, "kit"), fps=FPS, duration=DUR,
                           cache_dir=os.path.join(REEL_DIR, ".cache", "anim"), name="spider_hf", version=VERSION)
        hf.render({"hit": hit, "kit": kit})
        a = np.asarray(Image.open(os.path.join(REEL_DIR, "src", "f1.png")).convert("RGB")).astype(np.float32)
        _C.update(hit=hit, hf=hf, canvas=anim.paper_like(a))
    return _C


def frame(t, ctx):
    C = prepare(ctx)
    img = C["canvas"].copy()
    w = C["hf"].frame(t)
    w = cv2.resize(w, (w.shape[1] * 2, w.shape[0] * 2), interpolation=cv2.INTER_CUBIC)
    h = min(w.shape[0], img.shape[0]); ww = min(w.shape[1], img.shape[1])
    img[:h, :ww] = w[:h, :ww]
    cam = anim.hook_cam(t, hit=C["hit"])                # правила 28–29: сильный влёт и второй удар на «ночь»
    th = t - C["hit"]
    if th >= 2 / 30:                                       # кадр отвечает на срыв паука: тряска шумом, гаснет за ~0,15 с
        kk = math.exp(-(th - 2 / 30) / 0.12)
        cam["dx"] += 2 * 10 * kk * (anim.vnoise(th * 15.0, 1) - 0.5)
        cam["dy"] += 2 * 12 * kk * (anim.vnoise(th * 13.0, 2) - 0.5)
        cam["rot"] += 2 * 0.3 * kk * (anim.vnoise(th * 10.0, 3) - 0.5)
    return img, cam
