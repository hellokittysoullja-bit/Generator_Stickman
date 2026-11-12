"""Общая таблица времени сцены «Дима, 01:47» (combine_spec.md). Одни формулы для Blender и SVG-героев.

JS-копия — timing.js (window.Timing / require). Проверка совпадения: python3 timing.py --check
Кадр f → t = f / 30.

(Файл восстановлен по timing.js 12.11: SVG-агент по ошибке перезаписал исходный timing.py Blender-агента;
формулы перенесены из timing.js один в один и сверены --check.)
"""
import json
import math
import os
import subprocess
import sys

FPS, DURATION = 30, 3.0
SWIPES = [0.55, 1.45, 2.35]
SWIPE_UP, SWIPE_BACK = 0.18, 0.25
FLASH_DELAY, FLASH_ATTACK, FLASH_DECAY, FLASH_GAIN, JITTER = 0.12, 0.04, 0.35, 0.6, 0.06
DIMA_BLINKS = [1.15, 2.70]
CAT_BLINK, CAT_BLINK_DUR = 2.30, 0.35
TAIL_DEG, TAIL_PERIOD, PUSH = 4.0, 2.2, 0.06


def frac(x):
    return x - math.floor(x)


def hash01(i, seed):
    return frac(math.sin(i * 127.1 + seed * 311.7) * 43758.5453123)


def vnoise(t, hz, seed):
    x = t * hz
    i = math.floor(x)
    f = x - i
    u = f * f * (3 - 2 * f)
    a, b = hash01(i, seed), hash01(i + 1, seed)
    return a + (b - a) * u


def smoothstep(e0, e1, x):
    u = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return u * u * (3 - 2 * u)


def flash(t):
    best = 0.0
    for s in SWIPES:
        dt = t - (s + FLASH_DELAY)
        if dt < 0:
            continue
        if dt < FLASH_ATTACK:
            v = dt / FLASH_ATTACK
        elif dt < FLASH_ATTACK + FLASH_DECAY:
            u = 1 - (dt - FLASH_ATTACK) / FLASH_DECAY
            v = u * u
        else:
            v = 0.0
        best = max(best, v)
    return best


def screen(t):
    return (1 + JITTER * (2 * vnoise(t, 7, 3) - 1)) * (1 + FLASH_GAIN * flash(t))


def flame(t):
    return 0.85 + 0.30 * vnoise(t, 9, 7)


def thumb(t):
    best = 0.0
    for s in SWIPES:
        dt = t - s
        v = 0.0
        if 0 <= dt < SWIPE_UP:
            v = smoothstep(0, SWIPE_UP, dt)
        elif SWIPE_UP <= dt < SWIPE_UP + SWIPE_BACK:
            v = 1 - smoothstep(SWIPE_UP, SWIPE_UP + SWIPE_BACK, dt)
        best = max(best, v)
    return best


def dima_blink(t):
    best = 0.0
    for b in DIMA_BLINKS:
        dt = t - b
        v = 0.0
        if 0 <= dt < 0.08:
            v = smoothstep(0, 0.08, dt)
        elif 0.08 <= dt < 0.17:
            v = 1 - smoothstep(0.08, 0.17, dt)
        best = max(best, v)
    return best


def cat_blink(t):
    dt, h = t - CAT_BLINK, CAT_BLINK_DUR / 2
    if 0 <= dt < h:
        return smoothstep(0, h, dt)
    if h <= dt < CAT_BLINK_DUR:
        return 1 - smoothstep(h, CAT_BLINK_DUR, dt)
    return 0.0


def tail(t):
    return TAIL_DEG * math.sin(2 * math.pi * t / TAIL_PERIOD)


def pupils(t):
    marks = [0.0, *SWIPES, DURATION + 0.6]
    for k in range(len(marks) - 1):
        a, b = marks[k], marks[k + 1]
        if a <= t < b:
            p = (t - a) / (b - a)
            y = -1 + 2 * p
            if k > 0 and t - a < 0.1:
                prev = 1.0
                y = prev + (y - prev) * smoothstep(0, 0.1, t - a)
            return y
    return 1.0


def push(t):
    return PUSH * smoothstep(0, DURATION, t)


NAMES = ['screen', 'flame', 'thumb', 'dima_blink', 'cat_blink', 'tail', 'pupils', 'push', 'flash']

if __name__ == '__main__' and '--check' in sys.argv:
    here = os.path.dirname(os.path.abspath(__file__))
    js = json.loads(subprocess.run(['node', os.path.join(here, 'timing.js'), '--dump'], capture_output=True, text=True,
                                   check=True).stdout)
    worst = max(abs(globals()[n](f / FPS) - js[n][f]) for n in NAMES for f in range(91))
    print('max |py - js| =', worst)
    sys.exit(0 if worst < 1e-9 else 1)
