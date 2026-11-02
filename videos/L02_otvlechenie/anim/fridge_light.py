"""Хук L02, кадр 1 «Ты убираешь телефон, выключаешь уведомления, садишься за дело, а через пять минут почему-то стоишь
у холодильника?» — движение в HyperFrames (решение владельца 28.10: «гиперфреймс по КД везде используем»).

Композиция anim/fridge_hf/index.html рисует мир кадра целиком (холст 16:9 ×2, как у сборщика): стол — телефон уезжает,
колокольчик звенит и его перечёркивают, кот садится и пишет; хлёст-панорама на «через»; кухня — свет холодильника
мигает и дышит, кот тянется к дверце, на «холоди́льника» вздрагивает с «!». Слои — anim/kit_hook_hf.py (anim/hf/assets).
Источник времени один — озвучка: время каждого движения берётся из слов фразы и вписывается в композицию; камеру хука
(anim.hook_cam) и тряску на ударе даёт сборщик. Рендер, кэш и подстановку времени делает scripts/anim_hf.py;
кадры — media_plan/anim_cache/ (не в git)."""
import math
import os
import re

import anim
import anim_hf

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "fridge_hf")
ASSETS = os.path.join(HERE, "hf", "assets")
CACHE = os.path.join(HERE, "..", "media_plan", "anim_cache")
FPS, DUR = 24, 8.0
VERSION = 1
# слово (основа) -> событие; удар — на ударный слог «холоди́льника» (4-й из 6 слогов)
WORDS = dict(bell="выключа", strike="уведомл", sit="садишь", work="дело", whip="через", lean="почему", hit="холодильник")
HIT_FRAC = 0.36
SHAKE_SEC = 2 / FPS


def _stem(w):
    return re.sub(r"[^а-яё]", "", w.lower())


def times(words):
    T = anim_hf.default_vars(PROJ)
    for k, stem in WORDS.items():
        w = next((w for w in words if _stem(w["word"]).startswith(stem)), None)
        if w is None:
            continue
        s, e = w["start"], w["end"]
        T[k] = round(s + HIT_FRAC * (e - s) if k == "hit" else s - 0.04 if k == "whip" else s, 3)
    return T


class Scene:
    def __init__(self, fr, words, scale):
        self.T = times(words)
        self.hf = anim_hf.Scene(PROJ, ASSETS, fps=FPS, duration=DUR, cache_dir=CACHE, name="fridge_hf", version=VERSION)
        self.hf.render(self.T)
        self.shape = fr["world"].shape

    def frame(self, t, world):
        a = self.hf.frame(t)
        if a.shape != self.shape:
            raise RuntimeError(f"кадр HyperFrames {a.shape} не совпадает с миром кадра {self.shape}")
        return a.copy()

    def cam(self, t):
        c = anim.hook_cam(t)
        th = t - self.T["hit"]
        if th >= SHAKE_SEC:                               # кадр отвечает на «пойман»: тряска гаснет за ~0,15 с
            k = math.exp(-(th - SHAKE_SEC) / 0.12)
            c["dx"] += 9 * k * math.sin(th * 95); c["dy"] += 11 * k * math.cos(th * 77)
            c["rot"] += 0.3 * k * math.sin(th * 61)
        return c
