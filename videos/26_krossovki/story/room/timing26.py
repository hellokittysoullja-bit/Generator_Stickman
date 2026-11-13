"""Общая таблица времени сцены room рилса 26 «кроссовки» (одни формулы для assemble.py и SVG-героев; JS-копия
timing26.js, проверка: python3 timing26.py --check). t — время ролика, с. Все планы — вечер: торшер слева за кадром,
часы на полке 21:15, огонёк кота горит ровно.
s02: «обещает» 1.44 — Дима вскидывает кулак, «бегать» 2.56 — обмякает на подушку; кот смотрит с сомнением.
s05: «почему» 6.48 — кот наклоняет голову. s13: Дима пишет на стикере. s17: кот у пустой коробки медленно моргает.
"""
import math
import sys

FPS = 30
PROMISE = 1.44      # «обещает»: кулак вверх
RUN = 2.56          # «бегать»: обмякает
WHY = 6.48          # «почему»: наклон головы кота
SHOTS = ('s02', 's05', 's13', 's17')


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
    """Огонёк кота: дрожь 0.85..1.15, вечером в полную силу."""
    return 0.85 + 0.30 * vnoise(t, 7, 7)


def lamp(t, shot):
    return 1.0


def tv(t, shot):
    return 0.0


NAMES = ['flame', 'lamp']

if __name__ == '__main__':
    if '--check' in sys.argv:
        import json, os, subprocess
        js = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timing26.js')
        out = json.loads(subprocess.check_output(['node', js, '--dump']))
        worst = 0.0
        for s in out:
            for n in NAMES:
                for f, v in enumerate(out[s][n]):
                    worst = max(worst, abs(globals()[n](f / FPS, s) - v))
        print('max |py - js| =', worst)
        sys.exit(0 if worst < 1e-9 else 1)
