"""Время сцены room рилса 28 (одни формулы для assemble.py и SVG-героев; JS-копия timing28.js, проверка:
python3 timing28.py --check). t — время ролика, с. Вечер: торшер слева за кадром, часы на полке 20:40.
s01: хук, карточки кружат вокруг головы, «английский» 1.6 — плотнее, ударный слог 1.78 — удар камерой.
s04: «почему» 8.0 — кот наклоняет голову. s14: «запоминаются» 30.72 — карточки влетают в голову, Дима улыбается.
В s01 кота в кадре нет (он справа за кадром) — свет огонька выключен."""
import math
import sys

FPS = 30
DENSE = 1.6
HIT = 1.78
WHY = 8.0
SMILE = 30.72


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


def flame(t, shot):
    if shot == 's01':
        return 0.0
    return 0.85 + 0.30 * vnoise(t, 7, 7)


def lamp(t, shot):
    return 1.0


def tv(t, shot):
    return 0.0


NAMES = ['flame', 'lamp']

if __name__ == '__main__':
    if '--check' in sys.argv:
        import json, os, subprocess
        js = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timing28.js')
        out = json.loads(subprocess.check_output(['node', js, '--dump']))
        worst = 0.0
        for s in out:
            for n in NAMES:
                for f, v in enumerate(out[s][n]):
                    worst = max(worst, abs(globals()[n](f / FPS, s) - v))
        print('max |py - js| =', worst)
        sys.exit(0 if worst < 1e-9 else 1)
