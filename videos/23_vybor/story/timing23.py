"""Общая таблица времени рилса 23 «выбор»: свет телевизора и огонька. Одни формулы для Blender-сборки комнаты
и SVG-героев. JS-копия — timing23.js; проверка: python3 timing23.py --check.
t — время ролика, с (общее для всех клипов; кадр k клипа = t0 - pad + k/30).
"""
import math
import sys

FPS, END = 30, 34.10
FLASH_ATTACK, FLASH_DECAY, FLASH_GAIN, JITTER = 0.03, 0.25, 0.7, 0.05
PLAY_AT = 25.72          # «включает»: дальше идёт фильм, свет ровный, мягко дышит


def _panic_switches():
    """18.53..22.64: карточки переключаются всё чаще (шаг 0.34 -> 0.10 с), на «вообще» замирают."""
    out, t, k = [], 18.62, 0
    while t < 22.60:
        out.append(round(t, 4))
        u = (t - 18.62) / (22.60 - 18.62)
        t += 0.34 - 0.24 * u
        k += 1
    return out


SWITCHES = [0.42, 0.98, 1.50, 1.82, 2.12, 2.42, 4.92, 5.40, 5.90, 6.30] + _panic_switches() + [23.20, 23.95, 24.62]


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


def switch_flash(t):
    """0..1: вспышка экрана после переключения карточки."""
    best = 0.0
    for s in SWITCHES:
        dt = t - s
        if dt < 0 or dt > FLASH_ATTACK + FLASH_DECAY:
            continue
        v = dt / FLASH_ATTACK if dt < FLASH_ATTACK else (1 - (dt - FLASH_ATTACK) / FLASH_DECAY) ** 2
        best = max(best, v)
    return best


def tv(t):
    """Яркость света телевизора (множитель): ~0.95..1.05 дрожь, x1.7 на переключениях; после PLAY_AT — фильм:
    ровнее и чуть ярче, медленно дышит (сцены фильма)."""
    base = 1 + JITTER * (2 * vnoise(t, 7, 11) - 1)
    film = smoothstep(PLAY_AT, PLAY_AT + 0.4, t)
    base = base * (1 - film) + film * (1.08 + 0.10 * (2 * vnoise(t, 1.3, 5) - 1))
    return base * (1 + FLASH_GAIN * switch_flash(t))


def flame(t):
    """Огонёк кота 0.85..1.15 (как в 22-м); в s17 (28.56+) ярче — кот доволен."""
    happy = smoothstep(28.9, 29.6, t)
    return (0.85 + 0.30 * vnoise(t, 9, 7)) * (1 + 0.35 * happy)


NAMES = ['tv', 'flame', 'switch_flash']

if __name__ == '__main__':
    if '--check' in sys.argv:
        import json, os, subprocess
        js = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timing23.js')
        out = json.loads(subprocess.check_output(['node', js, '--dump']))
        worst = max(abs(globals()[n](f / FPS) - out[n][f]) for n in NAMES for f in range(int(END * FPS) + 1))
        print('max |py - js| =', worst)
        sys.exit(0 if worst < 1e-9 else 1)
    print('SWITCHES', SWITCHES)
