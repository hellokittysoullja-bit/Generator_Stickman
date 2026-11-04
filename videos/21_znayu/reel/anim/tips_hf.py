"""Хук рилса 21 «Знаешь как, а не делаешь?» на HyperFrames — по базе рилса 13 и правилам 25–29.

Рисунок gen/k1_tips.png разобран на слои anim/kit_tips.py; композиция anim/tips_hf/index.html: с кадра 0 на кота
сыплются листки-советы (каждый уже летит, качается и кружит), кот дрожит и вжимается на каждый пролетающий листок; на
ударном «дЕлаешь» обрушивается вся пачка, кот приседает и подскакивает, по бокам головы — штрихи испуга. Немытые кружки
на столике стоят (фон). Время удара — из озвучки; камера хука — anim.hook_cam(t, hit=…) (правило 29) и тряска — здесь.
Кадры — кэш .cache/anim/tips_hf_<подпись>/ (не в git), пересобираются сами."""
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
KIT = ["bg.png", "body.png", "tail.png", "tail_body.png", "tail_flame.png", "tail_mesh.json", "kit.json",
       "page0.png", "page1.png", "page2.png", "page3.png", "page4.png", "page5.png", "page6.png", "page7.png", "page8.png", "page9.png", "page10.png", "page11.png"]
SOURCES = ["gen/k1_tips.png", "anim/kit_tips.py", "anim/tips_hf/index.html"] + [f"anim/kit/{k}" for k in KIT]
VERSION = 1
FPS, DUR = 30, 2.6
HIT_FRAC = 0.12                     # «дЕлаешь»: ударный первый слог
PLACE = {n: n for n in ["body"] + [f"page{i}" for i in range(12)]}
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
            raise RuntimeError(f"tips_hf/index.html: нет слоя id={i} с left/top")
    open(html, "w", encoding="utf-8").write(s)


def _prepare(proj, v):
    place_layers(proj)
    mesh = json.load(open(os.path.join(proj, "assets", "tail_mesh.json")))
    tx, ty = _kit()["layers"]["tail"]["xy"]
    motion = tail_rig.extract_motion(proj, "tail", DUR)
    ang = tail_rig.simulate(mesh, motion, (tx, ty), v["hit"], DUR)
    json.dump(ang, open(os.path.join(proj, "assets", "tail_angles.json"), "w"))


def _hit(ctx):
    w = ctx["words"][-1]                      # «делаешь» — последнее слово хука
    return round(w[0] + HIT_FRAC * (w[1] - w[0]), 3)


def prepare(ctx):
    hit = _hit(ctx)
    if _C.get("hit") != hit:
        k = _kit(); ox, oy = k["origin"]
        pts = {n: k[n] for n in ("feet", "head")}
        hf = anim_hf.Scene(os.path.join(HERE, "tips_hf"), os.path.join(HERE, "kit"), fps=FPS, duration=DUR,
                           cache_dir=os.path.join(REEL_DIR, ".cache", "anim"), name="tips_hf", version=VERSION,
                           prepare=_prepare, extra=[tail_rig.__file__])
        hf.render({"hit": hit, "kit": pts})
        a = np.asarray(Image.open(os.path.join(REEL_DIR, ".cache", "anim", "k1_tips_x2.png")).convert("RGB")).astype(np.float32)
        _C.update(hit=hit, hf=hf, origin=(ox, oy), canvas=anim.paper_like(a))
    return _C


def frame(t, ctx):
    C = prepare(ctx)
    img = C["canvas"].copy()
    w = C["hf"].frame(t); x0, y0 = C["origin"]
    img[y0:y0 + w.shape[0], x0:x0 + w.shape[1]] = w
    cam = anim.hook_cam(t, hit=C["hit"])                # правило 29: влёт не слабее эталона, второй удар на «дЕлаешь»
    th = t - C["hit"]
    if th >= 2 / 30:                                       # кадр отвечает на удар: тряска шумом, гаснет за ~0,15 с
        kk = math.exp(-(th - 2 / 30) / 0.12)
        cam["dx"] += 2 * 10 * kk * (anim.vnoise(th * 15.0, 1) - 0.5)
        cam["dy"] += 2 * 12 * kk * (anim.vnoise(th * 13.0, 2) - 0.5)
        cam["rot"] += 2 * 0.3 * kk * (anim.vnoise(th * 10.0, 3) - 0.5)
    return img, cam
