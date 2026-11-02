"""Хук L02, кадр 1 «Ты убираешь телефон, выключаешь уведомления, садишься за дело, а через пять минут почему-то стоишь
у холодильника?» — движение в HyperFrames (решение владельца 28.10: «гиперфреймс по КД везде используем»).

Композиция anim/fridge_hf/index.html рисует мир кадра целиком (холст 16:9 ×2, как у сборщика): стол — телефон уезжает,
колокольчик звенит и его перечёркивают, кот садится и пишет; хлёст-панорама на «через»; кухня — свет холодильника
мигает и дышит, кот тянется к дверце, на «холоди́льника» вздрагивает с «!». Слои — anim/kit_hook_hf.py (anim/hf/assets).
Источник времени один — озвучка: время каждого движения берётся из слов фразы и вписывается в композицию; камеру хука
(anim.hook_cam) и тряску на ударе даёт сборщик. Кадры движка — media_plan/anim_cache/ (не в git), пересобираются,
если поменялись слои, композиция или время."""
import glob
import hashlib
import json
import math
import os
import re
import shutil
import subprocess

import numpy as np
from PIL import Image

import anim

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "fridge_hf")
ASSETS = os.path.join(HERE, "hf", "assets")
CACHE = os.path.join(HERE, "..", "media_plan", "anim_cache")
FILES = ["desk.png", "kitchen.png", "cat_desk.png", "cat_fridge.png", "phone.png"]
HF = "hyperframes@0.8.214"
FPS, DUR = 24, 8.0
VERSION = 1
DEFAULT = '{"phone":0.16,"bell":1.4,"strike":1.92,"sit":2.92,"work":3.52,"whip":4.12,"lean":5.12,"hit":6.3}'
# слово (основа) -> событие; удар — на ударный слог «холоди́льника» (4-й из 6 слогов)
WORDS = dict(bell="выключа", strike="уведомл", sit="садишь", work="дело", whip="через", lean="почему", hit="холодильник")
HIT_FRAC = 0.36
SHAKE_SEC = 2 / FPS


def _stem(w):
    return re.sub(r"[^а-яё]", "", w.lower())


def times(words):
    T = json.loads(DEFAULT)
    for k, stem in WORDS.items():
        w = next((w for w in words if _stem(w["word"]).startswith(stem)), None)
        if w is None:
            continue
        s, e = w["start"], w["end"]
        T[k] = round(s + HIT_FRAC * (e - s) if k == "hit" else s - 0.04 if k == "whip" else s, 3)
    return T


def render(T):
    """Кадры композиции с этим временем; возвращает список путей к PNG."""
    sig = hashlib.md5()
    for p in [os.path.join(PROJ, "index.html")] + [os.path.join(ASSETS, f) for f in FILES]:
        sig.update(open(p, "rb").read())
    sig.update(f"{json.dumps(T, sort_keys=True)}|{VERSION}|{HF}|{FPS}".encode())
    out = os.path.join(CACHE, f"fridge_hf_{sig.hexdigest()[:12]}")
    need = int(round(DUR * FPS))
    frames = sorted(glob.glob(os.path.join(out, "frames", "*.png")))
    if len(frames) >= need:
        return frames
    proj = os.path.join(out, "proj"); shutil.rmtree(out, ignore_errors=True)
    shutil.copytree(PROJ, proj)
    shutil.copytree(ASSETS, os.path.join(proj, "assets"))
    html = os.path.join(proj, "index.html"); s = open(html, encoding="utf-8").read()
    assert s.count(f"data-times='{DEFAULT}'") == 1, "в композиции нет data-times по умолчанию"
    open(html, "w", encoding="utf-8").write(s.replace(f"data-times='{DEFAULT}'", f"data-times='{json.dumps(T)}'"))
    env = dict(os.environ, HYPERFRAMES_TELEMETRY="0", DO_NOT_TRACK="1")
    subprocess.run(["npx", "--yes", HF, "render", "--format", "png-sequence", "--fps", str(FPS), "--workers", "2",
                    "-o", "frames", "--quiet"], cwd=proj, env=env, check=True, stdout=subprocess.DEVNULL)
    shutil.move(os.path.join(proj, "frames"), os.path.join(out, "frames"))   # путь вывода — относительный (CLI)
    shutil.rmtree(proj)
    frames = sorted(glob.glob(os.path.join(out, "frames", "*.png")))
    if len(frames) < need:
        raise RuntimeError(f"HyperFrames отдал {len(frames)} кадров из {need}: {out}")
    return frames


class Scene:
    def __init__(self, fr, words, scale):
        self.T = times(words)
        self.frames = render(self.T)
        self.shape = fr["world"].shape
        self.cache = {}

    def _img(self, i):
        if i not in self.cache:
            if len(self.cache) > 2:                       # по памяти: клипы рендерятся в нескольких процессах
                self.cache.clear()
            a = np.asarray(Image.open(self.frames[i]).convert("RGB"))
            if a.shape != self.shape:
                raise RuntimeError(f"кадр HyperFrames {a.shape} не совпадает с миром кадра {self.shape}")
            self.cache[i] = a
        return self.cache[i]

    def frame(self, t, world):
        return self._img(min(len(self.frames) - 1, max(0, int(round(t * FPS))))).copy()

    def cam(self, t):
        c = anim.hook_cam(t)
        th = t - self.T["hit"]
        if th >= SHAKE_SEC:                               # кадр отвечает на «пойман»: тряска гаснет за ~0,15 с
            k = math.exp(-(th - SHAKE_SEC) / 0.12)
            c["dx"] += 9 * k * math.sin(th * 95); c["dy"] += 11 * k * math.cos(th * 77)
            c["rot"] += 0.3 * k * math.sin(th * 61)
        return c
