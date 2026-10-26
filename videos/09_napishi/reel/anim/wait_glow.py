"""Хук «Ждёшь, кто напишет?»: кот лежит перед телефоном, экран вспыхивает, будто сейчас придёт сообщение, — и на
«напи́шет» гаснет; кот сникает.

Рисунок один — gen/m1_wait.png (1024×1536, координаты ниже ×2, сняты по сетке). Ничего не вырезается: экран лежит на
полу экраном вверх, и его свет — это яркость самого экрана плюс мягкое пятно на полу вокруг телефона; кот сникает
полем смещений (squash_region) — голова чуть опускается и пружинит. Камера — anim.hook_cam (начало как в рилсе 08,
стандарт 20); экран мерцает уже на первом кадре: надежда «вот-вот» — с первой доли секунды.
"""
import math
import os

import cv2
import numpy as np
from PIL import Image

import anim

SOURCES = ["gen/m1_wait.png"]
VERSION = 2
REEL_DIR = None

SCREEN = np.int32([(720, 2220), (1215, 2220), (1310, 2470), (610, 2470)])    # экран телефона (×2), по сетке
GLOW_CENTER, GLOW_AXES = (962, 2345), (560, 300)                             # пятно света на полу вокруг телефона
CAT = dict(center=(600, 1640), axes=(560, 480), floor=2100)                  # голова и плечи кота
ON, DIM, DARK = np.float32([255, 238, 176]), np.float32([150, 156, 168]), np.float32([66, 70, 80])
HALO = np.float32([255, 222, 140])
_L = None


def prepare():
    d = os.path.join(REEL_DIR, ".cache", "anim"); os.makedirs(d, exist_ok=True)
    x2 = os.path.join(d, "m1_wait_x2.png")
    if not os.path.exists(x2):
        import upscale
        a = np.asarray(Image.open(os.path.join(REEL_DIR, SOURCES[0])).convert("RGB"))
        Image.fromarray(upscale.upscale(a, 2)).save(x2)
    A = anim.paper_like(np.asarray(Image.open(x2).convert("RGB")).astype(np.float32))
    h, w = A.shape[:2]
    poly = np.zeros((h, w), np.uint8); cv2.fillPoly(poly, [SCREEN], 1)
    light = A.mean(axis=2) > 196                                             # светлое поле экрана, без рамки
    screen = cv2.GaussianBlur(((poly > 0) & light).astype(np.float32), (0, 0), 1.5)
    halo = np.zeros((h, w), np.float32); cv2.ellipse(halo, GLOW_CENTER, GLOW_AXES, 0, 0, 360, 1.0, -1)
    halo = cv2.GaussianBlur(halo, (0, 0), 90) * (1 - screen)
    cat = np.zeros((h, w), np.float32); cv2.ellipse(cat, CAT["center"], CAT["axes"], 0, 0, 360, 1.0, -1)
    return dict(A=A, screen=screen, halo=halo, cat=cv2.GaussianBlur(cat, (0, 0), 50))


def layers():
    global _L
    if _L is None:
        _L = prepare()
    return _L


def timing(ctx):
    w = ctx["words"]                                     # «Ждёшь, кто напишет?» — «напишет» последнее слово
    return dict(hit=w[-1][0] + 0.4 * (w[-1][1] - w[-1][0]))   # ударное «и» второго слога «напи́шет»


def glow_at(t, T):
    """Сила свечения экрана 0..1: мерцает «вот-вот придёт» с первого кадра, на ударе гаснет за 0.12 с."""
    if t < T["hit"]:
        tq = anim.on_twos(t)
        return 0.5 + 0.5 * math.sin(2 * math.pi * 1.9 * tq - 0.6)
    return 0.0


def frame(t, ctx):
    L = layers(); T = timing(ctx); A = L["A"]
    cam = anim.hook_cam(t)
    th = t - T["hit"]
    g = glow_at(t, T)
    img = A.copy()
    s = L["screen"][..., None]
    if th < 0:
        lit = DIM + (ON - DIM) * g                                           # экран просыпается и гаснет: «вот-вот»
        img = img * (1 - s) + lit * s
        img = img + (HALO - img) * (0.38 * g) * L["halo"][..., None]          # тёплый свет на полу вокруг
    else:
        k = min(1.0, th / 0.12)                                              # гаснет
        dark = (DIM + (ON - DIM) * glow_at(T["hit"] - 1e-3, T)) * (1 - k) + DARK * k
        img = img * (1 - s) + dark * s
        sq = 0.035 * (1 - math.exp(-th / 0.12)) + 0.03 * anim.spring(th, freq=3.6, damping=0.35)
        img = anim.squash_region(img, L["cat"], CAT["floor"], CAT["center"][0], 1 - sq, 1 + 0.3 * sq)
        if th >= 2 / 30:
            kk = math.exp(-(th - 2 / 30) / 0.12)
            cam["dx"] += 8 * kk * math.sin(th * 95); cam["dy"] += 10 * kk * math.cos(th * 77)
    return img, cam
