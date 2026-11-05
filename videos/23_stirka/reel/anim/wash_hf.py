"""Хук рилса 23 «Стирка час, а достаёшь неделю?» на HyperFrames — по правилу 30 (образец — рилс 22) и правилам 25–29.

Рисунок gen/p1_hook.png разобран на слои anim/kit_wash.py; композиция anim/wash_hf/index.html: с кадра 0 в стекле
машинки крутится барабан с бельём и пеной, машинка трясётся на отжиме, кот ёрзает с телефоном; на ударном «нЕделю»
барабан встаёт, вода уходит, за стеклом мелькают дни, поднимается вонь, кот подлетает. Камера — anim.hook_cam(t, hit=…).

Композиция рендерится ОДИН раз — по удару хука. Другие планы рилса с этой сценой берут из неё свой отрезок по смыслу
(сборщик даёт сцене время ролика и слова своей фразы):
  • фраза хука — как есть;
  • план, который начинается на последнем слове фразы (петля в конце), — с начала: кадр хука ровно как в 0 с;
  • стекло крупно в истории кота («постирал в понедельник») — отрезок после удара: дни мелькают, вонь, по кругу.
Кадры — кэш .cache/anim/wash_hf_<подпись>/ (не в git)."""
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
KIT = ["bg.png", "machine.png", "body.png", "tail.png", "tail_body.png", "tail_flame.png", "tail_mesh.json", "kit.json"]
SOURCES = ["gen/p1_hook.png", "anim/kit_wash.py", "anim/wash_hf/index.html"] + [f"anim/kit/{k}" for k in KIT]
VERSION = 2
FPS, DUR = 30, 4.4
HIT_FRAC = 0.3                      # «нЕделю»: ударный слог
PLACE = {"body": "body", "machine": "machine"}
TAIL_MARG = 180
DAYS = (0.3, 0.3 + 7 * 0.24)        # после удара: дни мелькают (как в index.html)
REEL_DIR = None
_C = {}


def _kit():
    return json.load(open(os.path.join(HERE, "kit", "kit.json")))


def place_layers(proj):
    """Положение слоёв в композиции — из kit.json (как в рилсах 13 и 22): нарезка меняет рамки, руками числа не пишутся."""
    layers = json.load(open(os.path.join(proj, "assets", "kit.json")))["layers"]
    html = os.path.join(proj, "index.html"); s = open(html, encoding="utf-8").read()
    pos = {i: layers[n]["xy"] for i, n in PLACE.items()}
    tx, ty = layers["tail"]["xy"]; pos["tail"] = (tx - TAIL_MARG, ty - TAIL_MARG)
    for i, (x, y) in pos.items():
        s, n = re.subn(rf'(id="{i}"[^>]*?style=")left:-?\d+px;top:-?\d+px', rf"\g<1>left:{x}px;top:{y}px", s)
        if n != 1:
            raise RuntimeError(f"wash_hf/index.html: нет слоя id={i} с left/top")
    open(html, "w", encoding="utf-8").write(s)


def _prepare(proj, v):
    place_layers(proj)
    mesh = json.load(open(os.path.join(proj, "assets", "tail_mesh.json")))
    tx, ty = _kit()["layers"]["tail"]["xy"]
    motion = tail_rig.extract_motion(proj, "tail", DUR)
    ang = tail_rig.simulate(mesh, motion, (tx, ty), v["hit"], DUR)
    json.dump(ang, open(os.path.join(proj, "assets", "tail_angles.json"), "w"))


def _hit_file():
    return os.path.join(REEL_DIR, ".cache", "anim", "wash_hit.json")


def _hook_hit(ctx):
    """Удар хука: из слов фразы хука (она начинается с 0 с); для других фраз — записанный при подготовке хука."""
    w = ctx["words"]
    if w[0][0] < 0.5:
        hit = round(w[-1][0] + HIT_FRAC * (w[-1][1] - w[-1][0]), 3)
        os.makedirs(os.path.dirname(_hit_file()), exist_ok=True)
        tmp = f"{_hit_file()}.{os.getpid()}"            # процессы рендера пишут и читают одновременно: только атомарно
        json.dump({"hit": hit}, open(tmp, "w"))
        os.replace(tmp, _hit_file())
        return hit
    if not os.path.exists(_hit_file()):
        raise RuntimeError("wash_hf: удар хука ещё не посчитан — сцену сначала зовут со словами фразы хука")
    return json.load(open(_hit_file()))["hit"]


def prepare(ctx):
    hit = _hook_hit(ctx)
    if _C.get("hit") != hit:
        k = _kit(); ox, oy = k["origin"]
        pts = {n: k[n] for n in ("feet", "head", "glass", "mach_feet")}
        hf = anim_hf.Scene(os.path.join(HERE, "wash_hf"), os.path.join(HERE, "kit"), fps=FPS, duration=DUR,
                           cache_dir=os.path.join(REEL_DIR, ".cache", "anim"), name="wash_hf", version=VERSION,
                           prepare=_prepare, extra=[tail_rig.__file__])
        hf.render({"hit": hit, "kit": pts})
        a = np.asarray(Image.open(os.path.join(REEL_DIR, ".cache", "anim", "p1_hook_x2.png")).convert("RGB")).astype(np.float32)
        _C.update(hit=hit, hf=hf, origin=(ox, oy), canvas=anim.paper_like(a))
    return _C


def scene_time(t, ctx, hit):
    """Время композиции для момента t ролика (см. докстринг модуля)."""
    w = ctx["words"]
    if w[0][0] < 0.5:                                      # фраза хука
        return t, t
    if t >= w[-1][0] - 0.05:                               # петля: план на последнем слове — кадр хука с начала
        return t - w[-1][0], t - w[-1][0]
    a, b = hit + DAYS[0], hit + DAYS[1]                     # история кота: стекло, дни мелькают по кругу
    return a + (t - w[0][0]) % (b - a), hit + 1.5          # камера уже стоит


def frame(t, ctx):
    C = prepare(ctx)
    ts, tc = scene_time(t, ctx, C["hit"])
    img = C["canvas"].copy()
    w = C["hf"].frame(ts); x0, y0 = C["origin"]
    img[y0:y0 + w.shape[0], x0:x0 + w.shape[1]] = w
    cam = anim.hook_cam(tc, hit=C["hit"])                # правило 29: влёт не слабее эталона, второй удар на «нЕделю»
    th = tc - C["hit"]
    if th >= 2 / 30:                                       # кадр отвечает на удар: тряска шумом, гаснет за ~0,15 с
        kk = math.exp(-(th - 2 / 30) / 0.12)
        cam["dx"] += 2 * 10 * kk * (anim.vnoise(th * 15.0, 1) - 0.5)
        cam["dy"] += 2 * 12 * kk * (anim.vnoise(th * 13.0, 2) - 0.5)
        cam["rot"] += 2 * 0.3 * kk * (anim.vnoise(th * 10.0, 3) - 0.5)
    return img, cam
