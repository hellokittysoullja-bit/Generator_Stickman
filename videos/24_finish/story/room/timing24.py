"""Общая таблица времени сцены room рилса 24 «финиш»: свет ноутбука, торшера, огонька, прыжок кота.
Одни формулы для сборки комнаты (assemble.py) и SVG-героев (JS-копия timing24.js; проверка: python3 timing24.py --check).
t — время ролика, с (кадр k клипа = t0 - pad + k/30).
Ночь (s03, s04, s07): свет ноутбука на коленях Димы, вспышка экрана на «получил» 2.427.
Вечер (s14-s18): тёплый торшер слева за кадром; с «Радость» 29.56 свет теплее; на «празднует» 31.84 кот прыгает,
огонёк ярче.
"""
import math
import sys

FPS, END = 30, 37.30
GOT = 2.427          # «получил»: экран и галочка вспыхивают
ZERO = 4.08          # «ноль»: хлопушка выдыхает две конфетти
WHY = 8.24           # «почему»: кот наклоняет голову
EVENING = 24.0       # до — ночь с ноутбуком, после — вечер с торшером
JOY = 29.56          # «Радость»: свет теплее
CELEB = 31.84        # «празднует»: прыжок кота


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
    """0..1: вспышка экрана на «получил» — атака 0.04 с, спад 0.45 с."""
    dt = t - GOT
    if dt < 0 or dt > 0.49:
        return 0.0
    return dt / 0.04 if dt < 0.04 else (1 - (dt - 0.04) / 0.45) ** 2


def tv(t):
    """Свет ноутбука (множитель прохода tv и свечения экрана): ночью ~1 с лёгкой дрожью, x2.2 во вспышку; вечером 0."""
    if t >= EVENING:
        return 0.0
    return (1 + 0.04 * (2 * vnoise(t, 5, 11) - 1)) * (1 + 1.2 * flash(t))


def lamp(t):
    """Торшер (тёплый): вечером 1, с «Радость» плавно до 1.35."""
    if t < EVENING:
        return 0.0
    return 1.0 + 0.35 * smoothstep(JOY, JOY + 0.8, t)


def warm(t):
    """0..1: насколько вечер «теплее» (для фильтра героев и тона комнаты)."""
    return smoothstep(JOY, JOY + 0.8, t) if t >= EVENING else 0.0


def flame(t):
    """Огонёк кота 0.85..1.15; на «празднует» вспыхивает до x1.8 и держится ярче (x1.4)."""
    base = 0.85 + 0.30 * vnoise(t, 9, 7)
    up = smoothstep(CELEB - 0.06, CELEB + 0.12, t)
    calm = smoothstep(CELEB + 0.5, CELEB + 1.6, t)
    return base * (1 + up * (0.8 - 0.4 * calm))


def _hop(t, t0, dur, h):
    if t < t0 or t > t0 + dur:
        return 0.0
    u = (t - t0) / dur
    return -4 * h * u * (1 - u)


def cat_jump(t):
    """Прыжок кота на «празднует»: подсед, большой прыжок, приземление, маленький подскок.
    Возвращает dy (px кадра 0, вверх отрицательно); sx, sy — сжатие/растяжение от точки опоры (лапы)."""
    t1, d1, t2, d2 = CELEB, 0.5, CELEB + 0.66, 0.3
    dy = _hop(t, t1, d1, 170) + _hop(t, t2, d2, 38)
    sq = 0.0
    sq += 0.10 * smoothstep(t1 - 0.2, t1 - 0.04, t) * (1 - smoothstep(t1 - 0.04, t1 + 0.04, t))       # подсед
    sq -= 0.07 * smoothstep(t1, t1 + 0.06, t) * (1 - smoothstep(t1 + 0.16, t1 + 0.32, t))            # вытянулся в полёте
    for land, k in ((t1 + d1, 0.11), (t2 + d2, 0.06)):                                                # приземления
        if land - 0.01 <= t <= land + 0.22:
            sq += k * math.sin(math.pi * (t - land + 0.01) / 0.23)
    return dy, 1 + 0.6 * sq, 1 - sq


NAMES = ['tv', 'flame', 'lamp', 'warm', 'flash']

if __name__ == '__main__':
    if '--check' in sys.argv:
        import json, os, subprocess
        js = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timing24.js')
        out = json.loads(subprocess.check_output(['node', js, '--dump']))
        worst = max(abs(globals()[n](f / FPS) - out[n][f]) for n in NAMES for f in range(int(END * FPS) + 1))
        for f in range(int(END * FPS) + 1):
            for a, b in zip(cat_jump(f / FPS), out['cat_jump'][f]):
                worst = max(worst, abs(a - b))
        print('max |py - js| =', worst)
        sys.exit(0 if worst < 1e-9 else 1)
