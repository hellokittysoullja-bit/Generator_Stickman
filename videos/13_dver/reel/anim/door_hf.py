"""Хук рилса 13 «Ты шёл и всё забыл?», движение — в HyperFrames (HTML + GSAP, рендер кадр за кадром в Chrome).

Почему не numpy, как прежние сцены (владелец 28.10: «движение с нулевой секунды… динамичней, аккуратней, несколько
движений»; сравнение HyperFrames и Remotion — videos/13_dver/reel/anim/ENGINES.md): движок двигает разобранные слои
(kit_doorway.py), а не куски плоской картинки, и даёт настоящее размытие движения.
Источник времени один — наш сборщик: время удара берётся из озвучки (ударный слог «забы́л») и вписывается в
композицию перед рендером; камера хука (anim.hook_cam), тряска, субтитры и звук — тоже наши.

Рендер, кэш и подстановку времени делает общий модуль scripts/anim_hf.py (с 02.11 — для всех сцен на HyperFrames):
кадры — PNG без потерь в .cache/anim/door_hf_<подпись>/ (не в git), пересобираются сами, если поменялись слои,
композиция или время удара. Нужны Node 22 и `npx hyperframes` (скачивается при первом запуске)."""
import json
import math
import os

import numpy as np
from PIL import Image

import anim
import anim_hf
import tail_rig

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = ["bg.png", "body.png", "tail.png", "tail_body.png", "tail_flame.png", "tail_mesh.json", "cloud.png", "pencil.png",
       "bubble1.png", "bubble2.png", "kit.json"]
SOURCES = ["gen/d1_doorway.png", "anim/kit_doorway.py", "anim/door_hf/index.html"] + [f"anim/kit/{k}" for k in KIT]
VERSION = 1
FPS = 30
HIT_FRAC = 0.55                    # «за-бы́л»: ударный второй слог
REEL_DIR = None
_C = {}


def _hit(ctx):
    w = ctx["words"]
    return round(w[-1][0] + HIT_FRAC * (w[-1][1] - w[-1][0]), 3)


def _tail_physics(proj, v):
    """Хвост по физике (владелец 02.11): как тело несёт хвост по таймлайну композиции → углы суставов на 240 Гц
    с ударом в момент v["hit"] → assets/tail_angles.json проекта перед рендером."""
    mesh = json.load(open(os.path.join(proj, "assets", "tail_mesh.json")))
    tx, ty = json.load(open(os.path.join(HERE, "kit", "kit.json")))["layers"]["tail"]["xy"]
    motion = tail_rig.extract_motion(proj, "tail", 1.6)
    ang = tail_rig.simulate(mesh, motion, (tx, ty), v["hit"], 1.6)
    json.dump(ang, open(os.path.join(proj, "assets", "tail_angles.json"), "w"))


def prepare(ctx):
    hit = _hit(ctx)
    if _C.get("hit") != hit:
        hf = anim_hf.Scene(os.path.join(HERE, "door_hf"), os.path.join(HERE, "kit"), fps=FPS, duration=1.5,
                           cache_dir=os.path.join(REEL_DIR, ".cache", "anim"), name="door_hf", version=VERSION,
                           prepare=_tail_physics, extra=[tail_rig.__file__])
        hf.render({"hit": hit})
        meta = json.load(open(os.path.join(HERE, "kit", "kit.json")))
        a = np.asarray(Image.open(os.path.join(REEL_DIR, ".cache", "anim", "d1_doorway_x2.png")).convert("RGB")).astype(np.float32)
        _C.update(hit=hit, hf=hf, origin=(meta["origin"][0], meta["origin"][1] - meta.get("bg_top", 0)),
                  canvas=anim.paper_like(a))
    return _C


def frame(t, ctx):
    C = prepare(ctx)
    img = C["canvas"].copy()
    w = C["hf"].frame(t); x0, y0 = C["origin"]
    img[y0:y0 + w.shape[0], x0:x0 + w.shape[1]] = w
    cam = anim.hook_cam(t)
    th = t - C["hit"]
    if th >= 2 / 30:                                       # кадр отвечает на удар: тряска гаснет за ~0,15 с
        # тряска — шумом значений (как блок camera-shake HyperFrames: свой сид на каждую ось, без синусов) — неровная,
        # «снятая с руки», а не ровное качание; сила и затухание прежние (владелец 02.11: было/стало — «стало лучше»)
        kk = math.exp(-(th - 2 / 30) / 0.12)
        cam["dx"] += 2 * 10 * kk * (anim.vnoise(th * 15.0, 1) - 0.5)
        cam["dy"] += 2 * 12 * kk * (anim.vnoise(th * 13.0, 2) - 0.5)
        cam["rot"] += 2 * 0.3 * kk * (anim.vnoise(th * 10.0, 3) - 0.5)
    return img, cam
