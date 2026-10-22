"""Замеры готового рилса по пикселям и звуку — сравнить версии одним прибором, а не на глаз (22.10).

    python scripts/reel_metrics.py old.mp4 new.mp4

frozen_share — доля кадров, где картинка почти не меняется (без склеек); motion_median — средняя смена пикселей
кадр к кадру; sharpness — дисперсия вторых разностей (кипение линий вторым проходом снижало её на 11%);
silence_share / longest_silence_s — тишина звука (<-50 dB по 100 мс); sound_events — отдельные звуки (>-30 dB)."""
import json
import subprocess
import sys

import numpy as np


def frames(p, ph=1420):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-vf', f'crop=1080:{ph}:0:0,scale=270:{ph // 4},format=gray',
                        '-f', 'rawvideo', '-'], capture_output=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, ph // 4, 270).astype(np.float32)


def audio(p, sr=16000):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-vn', '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True)
    return np.frombuffer(r.stdout, np.float32)


def measure(p):
    a = frames(p); d = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))
    moving = d[d <= 6]
    lap = [np.var(np.diff(f, 2, axis=0)) + np.var(np.diff(f, 2, axis=1)) for f in a[::15]]
    x = audio(p); w = 1600
    db = 20 * np.log10(np.array([np.sqrt(np.mean(x[i:i + w] ** 2)) for i in range(0, len(x) - w, w)]) + 1e-9)
    run = best = 0
    for v in db < -50: run = run + 1 if v else 0; best = max(best, run)
    ev = int(np.sum((db[1:] > -30) & (db[:-1] <= -30)))
    return dict(frozen_share=round(float((moving < 0.15).mean()), 3), motion_median=round(float(np.median(moving)), 3),
                sharpness=round(float(np.median(lap)), 1), silence_share=round(float((db < -50).mean()), 2),
                longest_silence_s=round(best * 0.1, 1), sound_events=ev)


if __name__ == "__main__":
    print(json.dumps({p: measure(p) for p in sys.argv[1:]}, ensure_ascii=False, indent=1))
