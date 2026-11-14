"""Общая таблица времени сцены room рилса 40 «66 дней» (одни формулы для assemble.py и SVG-героев; JS-копия
timing40.js, проверка: python3 timing40.py --check). t — время ролика, с (voice/words.json рилса 40).
s03: утро, Дима спит под пледом, Z; часы на полке 07:00 → 09:40 на «проспал» 3.04; кот смотрит на часы.
s05: вечер, лёжа; на «можно» 6.32 машет рукой «не продолжать» и обмякает на подушку; кот следит за рукой.
s06: крупно кот, «почему» 8.08 — наклон головы. s18: крупно кот у коробки с кроссовками, медленно моргает.
"""
import math
import sys

FPS = 30
OVERSLEPT = 3.04    # «проспал»: часы перещёлкиваются
WAVE = 6.32         # «можно»: рука вверх, отмахивается
GIVEUP = 6.64       # «продолжать»: рука падает, обмякает
WHY = 8.08          # «почему»: наклон головы кота
WRITE = 34.76       # «Напиши»
CAT_WORD = 35.28    # «кот»
SHOTS = ('s03', 's05', 's06', 's18')
# часы на полке s03: до «проспал» 07:00, затем за 0.36 с прощёлкивают до 09:40
CLOCK_STEPS = ['0700', '0712', '0731', '0749', '0808', '0826', '0845', '0903', '0921', '0940']


def clock_text(t, shot):
    if shot != 's03':
        return '2115'
    if t < OVERSLEPT:
        return CLOCK_STEPS[0]
    i = int((t - OVERSLEPT) / 0.04) + 1
    return CLOCK_STEPS[min(i, len(CLOCK_STEPS) - 1)]


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
    return 0.55 if shot == 's03' else 1.0


def tv(t, shot):
    return 0.0


NAMES = ['flame', 'lamp']

if __name__ == '__main__':
    if '--check' in sys.argv:
        import json, os, subprocess
        js = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timing40.js')
        out = json.loads(subprocess.check_output(['node', js, '--dump']))
        worst = 0.0
        for s in out:
            for n in NAMES:
                for f, v in enumerate(out[s][n]):
                    worst = max(worst, abs(globals()[n](f / FPS, s) - v))
        print('max |py - js| =', worst)
        sys.exit(0 if worst < 1e-9 else 1)
