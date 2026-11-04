"""Хук рилса 20 «Купил абонемент, а не ходишь?» на HyperFrames — по базе рилса 13 и правилам 25–29.

Рисунок gen/g1_hook.png разобран на слои anim/kit_sofa.py; композиция anim/sofa_hf/index.html: с кадра 0 карточка
абонемента качается на гвозде, кот ёрзает виноватой дрожью, над пыльными кроссовками клубится пыль; перед ударным
«хОдишь» карточка срывается и бьёт кота по макушке, из пакета — облако пыли. Время удара — из озвучки; камера хука —
anim.hook_cam(t, hit=…) (правило 29: влёт не слабее эталона рилса 17, свой у этого рилса) и тряска — здесь.
Кадры — кэш .cache/anim/sofa_hf_<подпись>/ (не в git), пересобираются сами."""
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
KIT = ["bg.png", "body.png", "tail.png", "tail_body.png", "tail_flame.png", "tail_mesh.json", "card.png", "bag.png", "kit.json"]
SOURCES = ["gen/g1_hook.png", "anim/kit_sofa.py", "anim/sofa_hf/index.html"] + [f"anim/kit/{k}" for k in KIT]
VERSION = 1
FPS, DUR = 30, 3.4
HIT_FRAC = 0.25                     # «хОдишь»: ударный первый слог
PLACE = {n: n for n in ("body", "card", "bag")}
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
            raise RuntimeError(f"sofa_hf/index.html: нет слоя id={i} с left/top")
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
        pts = {n: k[n] for n in ("feet", "head", "nail")}
        c = k["layers"]["card"]; pts["card_xy"] = c["xy"]
        pts["card_c"] = [1030, 710]                       # центр самой карточки (без верёвок), ×2
        pts["hit_dx"], pts["hit_dy"] = 120, 740           # карточка падает на макушку кота (≈ 1150, 1450)
        pts["dust_top"] = [450, 2300]                     # верх пыльных кроссовок
        hf = anim_hf.Scene(os.path.join(HERE, "sofa_hf"), os.path.join(HERE, "kit"), fps=FPS, duration=DUR,
                           cache_dir=os.path.join(REEL_DIR, ".cache", "anim"), name="sofa_hf", version=VERSION,
                           prepare=_prepare, extra=[tail_rig.__file__])
        hf.render({"hit": hit, "kit": pts})
        a = np.asarray(Image.open(os.path.join(REEL_DIR, ".cache", "anim", "g1_hook_x2.png")).convert("RGB")).astype(np.float32)
        _C.update(hit=hit, hf=hf, origin=(ox, oy), canvas=anim.paper_like(a))
    return _C


def frame(t, ctx):
    C = prepare(ctx)
    img = C["canvas"].copy()
    w = C["hf"].frame(t); x0, y0 = C["origin"]
    img[y0:y0 + w.shape[0], x0:x0 + w.shape[1]] = w
    cam = anim.hook_cam(t, hit=C["hit"])                # правило 29: влёт не слабее эталона, второй удар на «хОдишь»
    th = t - C["hit"]
    if th >= 2 / 30:                                       # кадр отвечает на удар: тряска шумом, гаснет за ~0,15 с
        kk = math.exp(-(th - 2 / 30) / 0.12)
        cam["dx"] += 2 * 10 * kk * (anim.vnoise(th * 15.0, 1) - 0.5)
        cam["dy"] += 2 * 12 * kk * (anim.vnoise(th * 13.0, 2) - 0.5)
        cam["rot"] += 2 * 0.3 * kk * (anim.vnoise(th * 10.0, 3) - 0.5)
    return img, cam
