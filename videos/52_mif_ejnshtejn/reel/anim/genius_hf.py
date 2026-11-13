"""Хук рилса 52 «Двоечник стал гением?» на HyperFrames — по базе рилса 13 (стандарт 24) и правилам 25–29.

Рисунок gen/g1_dunce_genius.png разобран на слои anim/kit_genius.py (anim.save_layer, фон — anim.inpaint_bg);
композиция anim/genius_hf/index.html: с кадра 0 кот вздрагивает за партой с листом-«двойкой», лампочка над головой
качается и мигает; на ударном «гЕнием» лампочка вспыхивает с лучами, кот подпрыгивает. Время удара — из озвучки;
камера хука — anim.hook_cam(t, hit=…) (правила 28–29) и тряска — здесь. Композиция в половинном размере, кадр
увеличивается вдвое. Кадры — кэш .cache/anim/genius_hf_<подпись>/ (не в git), пересобираются сами."""
import json
import math
import os
import re

import cv2
import numpy as np
from PIL import Image

import anim
import anim_hf

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = ["bg.png", "cat.png", "bulb.png", "kit.json"]
SOURCES = ["gen/g1_dunce_genius.png", "anim/kit_genius.py", "anim/genius_hf/index.html"] + [f"anim/kit/{k}" for k in KIT]
VERSION = 1
FPS, DUR = 30, 2.0
HIT_FRAC = 0.2                      # «гЕнием»: ударный слог в начале слова
PLACE = {"cat": "cat", "bulb": "bulb"}
REEL_DIR = None
_C = {}


def _kit():
    return json.load(open(os.path.join(HERE, "kit", "kit.json")))


def place_layers(proj):
    layers = json.load(open(os.path.join(proj, "assets", "kit.json")))["layers"]
    html = os.path.join(proj, "index.html"); s = open(html, encoding="utf-8").read()
    for i, n in PLACE.items():
        x, y = layers[n]["xy"]
        s, k = re.subn(rf'(id="{i}"[^>]*?style=")left:-?\d+px;top:-?\d+px', rf"\g<1>left:{x}px;top:{y}px", s)
        if k != 1:
            raise RuntimeError(f"genius_hf/index.html: нет слоя id={i} с left/top")
    open(html, "w", encoding="utf-8").write(s)


def _prepare(proj, v):
    place_layers(proj)


def _hit(ctx):
    w = ctx["words"]
    return round(w[-1][0] + HIT_FRAC * (w[-1][1] - w[-1][0]), 3)


def prepare(ctx):
    hit = _hit(ctx)
    if _C.get("hit") != hit:
        k = _kit()
        pts = {n: k[n] for n in ("feet", "head", "bulb_c")}
        hf = anim_hf.Scene(os.path.join(HERE, "genius_hf"), os.path.join(HERE, "kit"), fps=FPS, duration=DUR,
                           cache_dir=os.path.join(REEL_DIR, ".cache", "anim"), name="genius_hf", version=VERSION,
                           prepare=_prepare)
        hf.render({"hit": hit, "kit": pts})
        a = np.asarray(Image.open(os.path.join(REEL_DIR, "src", "f1.png")).convert("RGB")).astype(np.float32)
        _C.update(hit=hit, hf=hf, origin=tuple(k["origin"]), canvas=anim.paper_like(a), bulb=k["bulb_c"])
    return _C


def frame(t, ctx):
    C = prepare(ctx)
    img = C["canvas"].copy()
    w = C["hf"].frame(t)
    w = cv2.resize(w, (w.shape[1] * 2, w.shape[0] * 2), interpolation=cv2.INTER_CUBIC)
    x0, y0 = C["origin"]
    h = min(w.shape[0], img.shape[0] - y0); ww = min(w.shape[1], img.shape[1] - x0)
    img[y0:y0 + h, x0:x0 + ww] = w[:h, :ww]
    cam = anim.hook_cam(t, hit=C["hit"])                # правила 28–29: сильный влёт и второй удар на «гЕнием»
    th = t - C["hit"]
    if th >= 2 / 30:                                       # кадр отвечает на вспышку: тряска шумом, гаснет за ~0,15 с
        kk = math.exp(-(th - 2 / 30) / 0.12)
        cam["dx"] += 2 * 10 * kk * (anim.vnoise(th * 15.0, 1) - 0.5)
        cam["dy"] += 2 * 12 * kk * (anim.vnoise(th * 13.0, 2) - 0.5)
        cam["rot"] += 2 * 0.3 * kk * (anim.vnoise(th * 10.0, 3) - 0.5)
    return img, cam
