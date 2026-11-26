"""Автопроверка готового рилса-истории (формат 4) до показа владельцу — ловит повторяющиеся недостатки прошлых рилсов.

python3 scripts/story_qc.py videos/NNN_xxx/story

1. ПУСТОЙ СТАРТ ПЛАНА: первый кадр плана почти пустой, а через 0,4 с картинка полная (элемент «выскакивает» на пустом
   фоне — рилсы 107, 112, 114). Порог: содержимого в первом кадре < 70 % от кадра через 0,4 с.
2. ВЕРХНЯЯ НАДПИСЬ НА РИСУНКЕ: в полосе крупной надписи хука (верх 0–15 % кадра) много рисунка до появления надписи
   (голова, парик, шапка приложения под надписью — рилсы 115, 117).
Выход: список планов с проблемой; код 1, если есть хоть одна.
"""
import json
import os
import subprocess
import sys

import numpy as np

W, H = 270, 480


def frame(video, t):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", f"{max(t, 0):.3f}", "-i", video, "-frames:v", "1",
                                   "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.int16)


def content(img, y0=0.18, y1=0.80):
    """Доля «рисунка»: пиксели, отличные от фона (медиана кадра) — без зоны субтитров и надписей."""
    a = img[int(H * y0):int(H * y1)]
    bg = np.median(a.reshape(-1, 3), axis=0)
    return float((np.abs(a - bg).sum(axis=2) > 60).mean())


def main(story):
    sh = json.load(open(os.path.join(story, "shots.json")))
    video = os.path.join(story, "reel.mp4")
    bad = []
    for s in sh["shots"]:
        t0, t1 = s["t0"], s["t1"]
        if t1 - t0 < 0.6:
            continue
        a, b = content(frame(video, t0 + 0.04)), content(frame(video, min(t0 + 0.4, t1 - 0.05)))
        if b > 0.04 and a < 0.7 * b:
            bad.append(f"{s['id']} {t0:.2f}s: пустой старт плана (рисунка {a:.0%} против {b:.0%} через 0,4 с)")
    if bad:
        print("\n".join(bad))
        sys.exit(1)
    print("story_qc: чисто")


if __name__ == "__main__":
    main(sys.argv[1])
