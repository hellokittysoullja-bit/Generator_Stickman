"""Хук рилса 12 (версия друга) «Все успели, а ты?» на HyperFrames — по базе рилса 13 (стандарт 24).

Рисунок gen/k1_finish.png разобран на слои anim/kit_finish.py (anim.save_layer, фон — anim.inpaint_bg, хвост —
сеткой tail_rig); композиция anim/finish_hf/index.html: шарик уплывает, трое уходят, рваная лента треплется,
падает запоздалое конфетти, на ударном «ты́» кот сникает, вырывается вздох, хвост гнётся по физике.
Время удара — из озвучки; камера хука (anim.hook_cam) и тряска шумом — здесь, у сборщика. Кадры — кэш
.cache/anim/finish_hf_<подпись>/ (не в git), пересобираются сами."""
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
KIT = ["bg.png", "body.png", "tail.png", "tail_body.png", "tail_flame.png", "tail_mesh.json", "tape_l.png", "tape_r.png",
       "people.png", "balloon.png", "puff.png", "kit.json"]
SOURCES = ["gen/k1_finish.png", "anim/kit_finish.py", "anim/finish_hf/index.html"] + [f"anim/kit/{k}" for k in KIT]
VERSION = 1
FPS, DUR = 30, 1.7
HIT_FRAC = 0.45                     # «ты́»: удар на гласную
HEAD = (1130, 2000)                 # центр головы: штрихи удара вокруг макушки (×2 рисунка)
PLACE = {"body": "body", "balloon": "balloon", "people": "people", "tape_l": "tape_l", "tape_r": "tape_r", "puff": "puff"}
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
            raise RuntimeError(f"finish_hf/index.html: нет слоя id={i} с left/top")
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
        pts = dict(cat_foot=k["cat_foot"], tape_l_pivot=k["tape_l_pivot"], tape_r_pivot=k["tape_r_pivot"],
                   head=(HEAD[0] - ox, HEAD[1] - oy))
        hf = anim_hf.Scene(os.path.join(HERE, "finish_hf"), os.path.join(HERE, "kit"), fps=FPS, duration=DUR,
                           cache_dir=os.path.join(REEL_DIR, ".cache", "anim"), name="finish_hf", version=VERSION,
                           prepare=_prepare, extra=[tail_rig.__file__])
        hf.render({"hit": hit, "kit": pts})
        a = np.asarray(Image.open(os.path.join(REEL_DIR, ".cache", "anim", "k1_finish_x2.png")).convert("RGB")).astype(np.float32)
        _C.update(hit=hit, hf=hf, origin=(ox, oy), canvas=anim.paper_like(a))
    return _C


def frame(t, ctx):
    C = prepare(ctx)
    img = C["canvas"].copy()
    w = C["hf"].frame(t); x0, y0 = C["origin"]
    img[y0:y0 + w.shape[0], x0:x0 + w.shape[1]] = w
    cam = anim.hook_cam(t)
    th = t - C["hit"]
    if th >= 2 / 30:                                       # кадр отвечает на удар: тряска шумом, гаснет за ~0,15 с
        kk = math.exp(-(th - 2 / 30) / 0.12)
        cam["dx"] += 2 * 10 * kk * (anim.vnoise(th * 15.0, 1) - 0.5)
        cam["dy"] += 2 * 12 * kk * (anim.vnoise(th * 13.0, 2) - 0.5)
        cam["rot"] += 2 * 0.3 * kk * (anim.vnoise(th * 10.0, 3) - 0.5)
    return img, cam
