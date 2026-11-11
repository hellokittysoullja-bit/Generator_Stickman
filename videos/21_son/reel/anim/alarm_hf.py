"""Хук рилса 21 «Ты спал 8 часов, а утром разбит?» на HyperFrames — по базе рилса 13 (стандарт 24), правилам 25–29,
образец — хук рилса 20 (scroll_hf.py).

Рисунок gen/s1_alarm.png разобран на слои anim/kit_alarm.py (anim.save_layer, фон — бумага этого рисунка и узкие швы
anim.inpaint_bg, хвост — сеткой tail_rig); композиция anim/alarm_hf/index.html: с кадра 0 будильник трезвонит —
дребезжит, подпрыгивает, мигают дуги звона и штрихи вибрации; кот под одеялом мотает головой, жмурится, тянет одеяло,
ухо дёргается, хвост лениво болтается; на ударном «разБИТ» будильник подскакивает выше всего, кот вздрагивает,
вокруг — штрихи удара. Время удара — из озвучки; камера хука — anim.hook_cam(t, hit=…) (правила 28–29: сильный влёт,
размытие, второй удар на слоге) и тряска — здесь. Кадры — кэш .cache/anim/alarm_hf_<подпись>/ (не в git)."""
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
KIT = ["bg.png", "head.png", "ear.png", "blanket.png", "clock.png", "buzz.png", "tail.png", "tail_body.png",
       "tail_flame.png", "tail_mesh.json", "eye_l.png", "eye_r.png", "lid_l.png", "lid_r.png", "kit.json"]
SOURCES = ["gen/s1_alarm.png", "anim/kit_alarm.py", "anim/alarm_hf/index.html"] + [f"anim/kit/{k}" for k in KIT]
X2 = "s1_alarm_x2.png"
VERSION = 1
FPS, DUR = 30, 3.0
HIT_FRAC = 0.5                      # «разБИТ»: ударный слог во второй половине слова
PLACE = {"head": "head", "ear": "ear", "blanket": "blanket", "clock": "clock", "buzz": "buzz"}
TAIL_MARG = 280
CLOCK_CENTER = (1796, 1543)         # центр циферблата в ×2 (веер удара, дуги звона)
HEAD = (820, 1250)                  # центр головы в ×2 (веер удара вокруг головы)
# хвост висит с края кровати и болтается лениво, на ударе — хлёст (физика tail_rig, свои числа сцены)
TAIL_PHYS = dict(tail_rig.PHYS, wag_deg=6.0, wag_period=1.1, whip_deg=11.0)
REEL_DIR = None
_C = {}


def _kit():
    return json.load(open(os.path.join(HERE, "kit", "kit.json")))


def place_layers(proj):
    """Положение слоёв в композиции — из kit.json (как в рилсах 13, 17, 20): руками числа не пишутся."""
    k = json.load(open(os.path.join(proj, "assets", "kit.json")))
    layers = k["layers"]
    html = os.path.join(proj, "index.html"); s = open(html, encoding="utf-8").read()
    pos = {i: layers[n]["xy"] for i, n in PLACE.items()}
    tx, ty = layers["tail"]["xy"]; pos["tail"] = (tx - TAIL_MARG, ty - TAIL_MARG)
    for i, (x, y) in pos.items():
        s, n = re.subn(rf'(id="{i}"[^>]*?style=")left:-?\d+px;top:-?\d+px', rf"\g<1>left:{x}px;top:{y}px", s)
        if n != 1:
            raise RuntimeError(f"alarm_hf/index.html: нет слоя id={i} с left/top")
    tw, th = layers["tail"]["wh"]
    s, n = re.subn(r'(id="tail"[^>]*?)width="\d+" height="\d+"', rf'\g<1>width="{tw + 2 * TAIL_MARG}" height="{th + 2 * TAIL_MARG}"', s)
    if n != 1:
        raise RuntimeError("alarm_hf/index.html: у холста хвоста нет width/height")
    for e, i in (("l", "eyeL"), ("r", "eyeR")):
        (x, y), (w, h), fur = k["eyes"][e]["xy"], k["eyes"][e]["wh"], k["eyes"][e]["fur"]
        st = (f"left:{x}px;top:{y}px;width:{w}px;height:{h}px;-webkit-mask-image:url(assets/eye_{e}.png);"
              f"mask-image:url(assets/eye_{e}.png)")
        s, n = re.subn(rf'id="{i}" class="eye" style="[^"]*"', f'id="{i}" class="eye" style="{st}"', s)
        s, m = re.subn(rf'id="lid{e.upper()}" class="lid"( style="[^"]*")?', f'id="lid{e.upper()}" class="lid" style="background:{fur} url(assets/lid_{e}.png) 0 0 / 100% 100% no-repeat"', s)
        if n != 1 or m != 1:
            raise RuntimeError(f"alarm_hf/index.html: нет глаза {i}")
    open(html, "w", encoding="utf-8").write(s)


def _prepare(proj, v):
    place_layers(proj)
    mesh = json.load(open(os.path.join(proj, "assets", "tail_mesh.json")))
    tx, ty = _kit()["layers"]["tail"]["xy"]
    motion = tail_rig.extract_motion(proj, "tail", DUR)
    ang = tail_rig.simulate(mesh, motion, (tx, ty), v["hit"], DUR, p=TAIL_PHYS)
    json.dump(ang, open(os.path.join(proj, "assets", "tail_angles.json"), "w"))


def _hit(ctx):
    w = ctx["words"]
    return round(w[-1][0] + HIT_FRAC * (w[-1][1] - w[-1][0]), 3)


def prepare(ctx):
    hit = _hit(ctx)
    if _C.get("hit") != hit:
        k = _kit(); ox, oy = k["origin"]
        pts = {n: k[n] for n in ("seat", "ear_pivot", "clock_pivot", "tail_pivot", "blanket_base")}
        pts["clock_center"] = [CLOCK_CENTER[0] - ox, CLOCK_CENTER[1] - oy]
        pts["head"] = [HEAD[0] - ox, HEAD[1] - oy]
        hf = anim_hf.Scene(os.path.join(HERE, "alarm_hf"), os.path.join(HERE, "kit"), fps=FPS, duration=DUR,
                           cache_dir=os.path.join(REEL_DIR, ".cache", "anim"), name="alarm_hf", version=VERSION,
                           prepare=_prepare, extra=[tail_rig.__file__, __file__])
        hf.render({"hit": hit, "kit": pts})
        x2 = os.path.join(REEL_DIR, ".cache", "anim", X2)
        if not os.path.exists(x2):                         # тот же рисунок ×2, что режет kit_alarm.py
            import upscale
            a = np.asarray(Image.open(os.path.join(REEL_DIR, SOURCES[0])).convert("RGB"))
            os.makedirs(os.path.dirname(x2), exist_ok=True)
            Image.fromarray(upscale.upscale(a, 2)).save(x2)
        a = np.asarray(Image.open(x2).convert("RGB")).astype(np.float32)
        _C.update(hit=hit, hf=hf, origin=(ox, oy), canvas=anim.paper_like(a))
    return _C


def frame(t, ctx):
    C = prepare(ctx)
    img = C["canvas"].copy()
    w = C["hf"].frame(t); x0, y0 = C["origin"]
    img[y0:y0 + w.shape[0], x0:x0 + w.shape[1]] = w
    cam = anim.hook_cam(t, hit=C["hit"])                # правило 28: сильный влёт и второй удар на «разБИТ»
    th = t - C["hit"]
    if th >= 2 / 30:                                       # кадр отвечает на удар: тряска шумом, гаснет за ~0,15 с
        kk = math.exp(-(th - 2 / 30) / 0.12)
        cam["dx"] += 2 * 12 * kk * (anim.vnoise(th * 15.0, 4) - 0.5)
        cam["dy"] += 2 * 14 * kk * (anim.vnoise(th * 13.0, 5) - 0.5)
        cam["rot"] += 2 * 0.35 * kk * (anim.vnoise(th * 10.0, 6) - 0.5)
    return img, cam
