"""Общая таблица времени сцены room рилса 25 «ночные дела» (одни формулы для assemble.py и SVG-героев; JS-копия
timing25.js, проверка: python3 timing25.py --check). t — время ролика, с; shot — план.
Ночь (s02 s03 s04 s13 s14): ноутбука и телевизора нет, только луна и тусклый огонёк кота.
s13: на «кот тоже» (27.92) кот закрывает глаза, огонёк притухает; s14: глаза открываются (29.5), огонёк чуть ярче.
Вечер s10: торшер слева за кадром.
"""
import math
import sys

FPS = 30
WHY = 7.52          # «почему»: кот наклоняет голову
TOMORROW = 6.20     # «завтра»: листок календаря бьёт в центр
NOTSLEEP = 3.28     # «спит»: Дима резко моргает
CATTOO = 27.92      # «кот тоже»: кот закрывает глаза
EYES = 29.45        # s14: кот открывает глаза
SLOWBLINK = 30.55   # s14: медленное моргание
NIGHT_SHOTS = ('s02', 's03', 's04', 's13', 's14')


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


def flame(t, shot):
    """Огонёк кота: дрожь 0.85..1.15 × ночная тусклость плана."""
    base = 0.85 + 0.30 * vnoise(t, 7, 7)
    if shot == 's10':
        k = 1.0
    elif shot == 's13':
        k = 0.78 - 0.33 * smoothstep(CATTOO, CATTOO + 0.6, t)
    elif shot == 's14':
        k = 0.45 + 0.17 * smoothstep(EYES, EYES + 0.5, t)
    elif shot == 's04':
        k = 0.64
    else:
        k = 0.52
    return base * k


def lamp(t, shot):
    return 1.0 if shot == 's10' else 0.0


def tv(t, shot):
    return 0.0


NAMES = ['flame', 'lamp']

if __name__ == '__main__':
    if '--check' in sys.argv:
        import json, os, subprocess
        js = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timing25.js')
        out = json.loads(subprocess.check_output(['node', js, '--dump']))
        worst = 0.0
        for s in out:
            for n in NAMES:
                for f, v in enumerate(out[s][n]):
                    worst = max(worst, abs(globals()[n](f / FPS, s) - v))
        print('max |py - js| =', worst)
        sys.exit(0 if worst < 1e-9 else 1)
