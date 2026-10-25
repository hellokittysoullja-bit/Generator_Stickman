"""Хук «Тебя звали ленивым.»: три руки влетают с краёв и по очереди тычут в кота на ударных слогах, кот вжимается.

Рисунок один — gen/g1_hands.png: руки на бумаге отделяются сами (anim.ink_objects: всё, что не фон-бумага), фон
под ними — бумага (anim.fill_hole). Хронометраж (от «Тебя», голос с 0 с):
  0 – 0.25   руки влетают из-за краёв кадра (на единицах), по очереди с шагом 0.05 с; резкий наезд камеры;
  дальше     руки покачиваются (на двойках);
  тычки      «звАли» — левая, «ленИвым» — правая, «-вым» — средняя: замах назад 0.10 с, тычок 0.06 с со смазом,
             задержка, возврат пружиной; кот на каждый тычок вжимается (сжатие от пола, пружина), у пальца штрихи
             тушью, камера вздрагивает (последний тычок — сильнее всех).
"""
import math
import os

import cv2
import numpy as np
from PIL import Image

import anim

SOURCES = ["gen/g1_hands.png"]
VERSION = 2
REEL_DIR = None

CAT = dict(center=(1520, 1400), axes=(620, 440), floor=1790)     # кот (×2): сжимается от пола
HANDS_BOX_Y = 960                                               # руки — выше этой строки (×2)
ENTER = 260                                                     # откуда влетают (×2, вдоль руки)

_L = None


def prepare():
    d = os.path.join(REEL_DIR, ".cache", "anim"); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"hands_poke_v{VERSION}.npz")
    if os.path.exists(p):
        z = np.load(p)
        return {k: z[k] for k in z.files}
    import upscale
    x2 = os.path.join(d, "g1_hands_x2.png")
    if not os.path.exists(x2):
        a = np.asarray(Image.open(os.path.join(REEL_DIR, SOURCES[0])).convert("RGB"))
        Image.fromarray(upscale.upscale(a, 2)).save(x2)
    A = np.asarray(Image.open(x2).convert("RGB")).astype(np.float32)
    hands = anim.ink_objects(A, box=(0, 0, A.shape[1], HANDS_BOX_Y), min_area=20000)
    hands.sort(key=lambda m: np.argwhere(m)[:, 1].mean())          # слева направо
    union = np.zeros(A.shape[:2], np.uint8)
    for m in hands: union |= m
    bg = anim.fill_hole(A, cv2.dilate(union, np.ones((9, 9), np.uint8)) > 0, grain_from="noise", feather=2)
    A, bg = anim.paper_like(A), anim.paper_like(bg)
    out = dict(A=np.clip(A, 0, 255).astype(np.uint8), bg=np.clip(bg, 0, 255).astype(np.uint8))
    for i, m in enumerate(hands):
        out[f"hand{i}"] = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.0)
    np.savez(p, **out)
    return out


def layers():
    global _L
    if _L is None:
        d = prepare()
        hands = []
        target = np.float32(CAT["center"]) - (0, 120)
        for k in sorted(x for x in d if x.startswith("hand")):
            a = d[k]
            lay = anim.Layer.cut(d["A"], a > 0.5, pad=6, feather=0)
            x0, y0 = lay.origin.astype(int); h, w = lay.a.shape
            lay.a = a[y0:y0 + h, x0:x0 + w]
            pts = np.argwhere(a > 0.5)[:, ::-1].astype(np.float32)
            tip = pts[np.argmin(((pts - target) ** 2).sum(1))]          # кончик пальца — ближайшая к коту точка
            c = pts.mean(0); dvec = (tip - c) / np.linalg.norm(tip - c)
            lay.pivot = tip - lay.origin
            hands.append(dict(lay=lay, tip=tip, dir=dvec))
        m = np.zeros(d["A"].shape[:2], np.float32)
        cv2.ellipse(m, CAT["center"], CAT["axes"], 0, 0, 360, 1.0, -1)
        _L = dict(d=d, hands=hands, cat=cv2.GaussianBlur(m, (0, 0), 50))
    return _L


def timing(ctx):
    w = ctx["words"]                                   # «Тебя», «звали», «ленивым.»
    jabs = [w[1][0] + 0.05, w[2][0] + 0.12, w[2][0] + 0.36]
    return dict(jabs=jabs, order=[0, 2, 1])            # левая, правая, средняя (средняя — главная, последней)


def hand_offset(t, i, T):
    """Сдвиг руки i вдоль её направления (px ×2, + к коту) и поворот в момент t."""
    enter = anim.SNAP((t - 0.05 * i) / 0.22)
    off = -ENTER * (1 - enter)
    ang = 0.0
    if t > 0.3:                                        # покачивание, на двойках
        tq = anim.on_twos(t)
        off += 6 * math.sin(2 * math.pi * 0.9 * tq + i * 2.1)
    for j, hi in zip(T["jabs"], T["order"]):
        if hi != i: continue
        if j - 0.10 <= t < j:                          # замах назад
            off -= 40 * anim.EASE_OUT((t - (j - 0.10)) / 0.10)
        elif j <= t < j + 0.06:                        # тычок — на единицах
            u = anim.EASE_IN((t - j) / 0.06)
            off += -40 + 150 * u; ang = 3 * u
        elif t >= j + 0.06:                            # задержка у кота и возврат пружиной
            s = anim.spring(max(0.0, t - j - 0.12), freq=3.2, damping=0.42)
            off += 110 * s; ang = 3 * s
    return off, ang


def frame(t, ctx):
    Lr = layers(); d = Lr["d"]; T = timing(ctx)
    cam = dict(dx=0.0, dy=0.0, zoom=1 / (1 + 0.12 * (1 - anim.SNAP(t / 0.30))), rot=0.0)
    # «храповик» (Tella add-zooms): три руки — перечисление, каждый тычок склейкой поднимает камеру на ступень,
    # последний — выше всех; без сглаживания, держится до конца плана
    n = sum(t >= j + 0.05 for j in T["jabs"])
    cam["zoom"] *= (1.0, 1.04, 1.08, 1.14)[n]
    img = d["bg"].astype(np.float32)
    # кот вжимается на каждый тычок одним полем: «желе» squash_follow владелец отклонил 25.10, было лучше
    sq = 0.0
    for k, j in enumerate(T["jabs"]):
        if t >= j + 0.04:
            sq += (0.07 + 0.03 * k) * anim.spring(t - j - 0.04, freq=4.2, damping=0.34)
    if abs(sq) > 0.002:
        img = anim.squash_region(img, Lr["cat"], CAT["floor"], CAT["center"][0], 1 - sq, 1 + 0.5 * sq)
    for i, h in enumerate(Lr["hands"]):
        off, ang = hand_offset(t, i, T)
        prev, _ = hand_offset(t - 1 / 30, i, T)
        v = h["dir"] * (off - prev)
        pos = h["tip"] + h["dir"] * off
        h["lay"].draw(img, pos, ang, smear=(float(v[0]), float(v[1])) if abs(off - prev) > 8 else None)
    for k, (j, hi) in enumerate(zip(T["jabs"], T["order"])):     # штрихи у пальца и вздрагивание камеры
        tj = t - j - 0.05
        if 0 <= tj < 0.4:
            h = Lr["hands"][hi]; tip = h["tip"] + h["dir"] * 110
            a0 = math.degrees(math.atan2(h["dir"][1], h["dir"][0]))
            anim.impact_strokes(img, tip, anim.on_twos(tj), r0=70, r1=170, n=3, spread=(a0 - 60, a0 + 60), width=12,
                                color=(24, 24, 26), seed=11 + k, life=0.25)
            amp = (6, 8, 14)[k] * math.exp(-tj / 0.1)
            cam["dx"] += amp * math.sin(tj * 90); cam["dy"] += amp * 0.7 * math.cos(tj * 70)
    return img, cam
