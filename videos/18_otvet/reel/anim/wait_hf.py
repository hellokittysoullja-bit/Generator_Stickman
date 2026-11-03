"""Хук рилса 18 «Ответить другу секунда, а ты не отвечаешь неделю?» на HyperFrames — по базе рилса 13 и правилам 25–29.

Рисунок gen/a1_wait.png (исправлен владельцем 03.11) разобран на слои anim/kit_wait.py; композиция anim/wait_hf/index.html:
с кадра 0 телефон в лапах вибрирует и кот трясётся, пустое облачко сообщения пульсирует, листки календаря летят и
кружат; на ударном «нЕделю» кот вздрагивает, облачко раздувается, листки разлетаются. Время удара — из озвучки; камера
хука — anim.hook_cam(t, hit=…) (правило 29: влёт не слабее эталона рилса 17, свой у этого рилса) и тряска — здесь.
Кадры — кэш .cache/anim/wait_hf_<подпись>/ (не в git), пересобираются сами."""
import json
import math
import os
import re

import numpy as np
from PIL import Image

import anim
import anim_hf
import tail_rig

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = ["bg.png", "body.png", "tail.png", "tail_body.png", "tail_flame.png", "tail_mesh.json", "bubble.png", "page0.png",
       "page1.png", "page2.png", "page3.png", "kit.json"]
SOURCES = ["gen/a1_wait.png", "anim/kit_wait.py", "anim/wait_hf/index.html"] + [f"anim/kit/{k}" for k in KIT]
VERSION = 1
FPS, DUR = 30, 3.6
HIT_FRAC = 0.4                      # «нЕделю»: ударный второй слог
PLACE = {n: n for n in ("body", "bubble", "page0", "page1", "page2", "page3")}
TAIL_MARG = 180
REEL_DIR = None
_C = {}


def _kit():
    return json.load(open(os.path.join(HERE, "kit", "kit.json")))


def place_layers(proj):
    """Положение слоёв в композиции — из kit.json (как в рилсе 13): нарезка меняет рамки, руками числа не пишутся."""
    layers = json.load(open(os.path.join(proj, "assets", "kit.json")))["layers"]
    html = os.path.join(proj, "index.html"); s = open(html, encoding="utf-8").read()
    pos = {i: layers[n]["xy"] for i, n in PLACE.items()}
    tx, ty = layers["tail"]["xy"]; pos["tail"] = (tx - TAIL_MARG, ty - TAIL_MARG)
    for i, (x, y) in pos.items():
        s, n = re.subn(rf'(id="{i}"[^>]*?style=")left:-?\d+px;top:-?\d+px', rf"\g<1>left:{x}px;top:{y}px", s)
        if n != 1:
            raise RuntimeError(f"wait_hf/index.html: нет слоя id={i} с left/top")
    open(html, "w", encoding="utf-8").write(s)


def _prepare(proj, v):
    place_layers(proj)
    mesh = json.load(open(os.path.join(proj, "assets", "tail_mesh.json")))
    tx, ty = _kit()["layers"]["tail"]["xy"]
    motion = tail_rig.extract_motion(proj, "tail", DUR)
    ang = tail_rig.simulate(mesh, motion, (tx, ty), v["hit"], DUR)
    json.dump(ang, open(os.path.join(proj, "assets", "tail_angles.json"), "w"))


def _hit(ctx):
    w = ctx["words"]
    return round(w[-1][0] + HIT_FRAC * (w[-1][1] - w[-1][0]), 3)


def prepare(ctx):
    hit = _hit(ctx)
    if _C.get("hit") != hit:
        k = _kit(); ox, oy = k["origin"]
        pts = {n: k[n] for n in ("feet", "head")}
        b = k["layers"]["bubble"]; pts["bubble_c"] = [b["xy"][0] + b["wh"][0] / 2, b["xy"][1] + b["wh"][1]]
        hf = anim_hf.Scene(os.path.join(HERE, "wait_hf"), os.path.join(HERE, "kit"), fps=FPS, duration=DUR,
                           cache_dir=os.path.join(REEL_DIR, ".cache", "anim"), name="wait_hf", version=VERSION,
                           prepare=_prepare, extra=[tail_rig.__file__])
        hf.render({"hit": hit, "kit": pts})
        a = np.asarray(Image.open(os.path.join(REEL_DIR, ".cache", "anim", "a1_wait_x2.png")).convert("RGB")).astype(np.float32)
        _C.update(hit=hit, hf=hf, origin=(ox, oy), canvas=anim.paper_like(a))
    return _C


def frame(t, ctx):
    C = prepare(ctx)
    img = C["canvas"].copy()
    w = C["hf"].frame(t); x0, y0 = C["origin"]
    img[y0:y0 + w.shape[0], x0:x0 + w.shape[1]] = w
    cam = anim.hook_cam(t, hit=C["hit"])                # правило 29: влёт не слабее эталона, второй удар на «нЕделю»
    th = t - C["hit"]
    if th >= 2 / 30:                                       # кадр отвечает на удар: тряска шумом, гаснет за ~0,15 с
        kk = math.exp(-(th - 2 / 30) / 0.12)
        cam["dx"] += 2 * 10 * kk * (anim.vnoise(th * 15.0, 1) - 0.5)
        cam["dy"] += 2 * 12 * kk * (anim.vnoise(th * 13.0, 2) - 0.5)
        cam["rot"] += 2 * 0.3 * kk * (anim.vnoise(th * 10.0, 3) - 0.5)
    return img, cam
