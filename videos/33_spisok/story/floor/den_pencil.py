"""Карандаш из den.py рилса 32."""
import numpy as np

from lib import blob, shape


def pencil(a, b, w=11.0, seed=3910):
    """Карандаш от a (тупой конец с ластиком) к b (острие)."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0]])
    h = w / 2
    P = lambda s_, v: tuple(a + u * s_ + n * v)  # noqa: E731
    er = L * .1
    tip = L * .82
    body = [P(er, -h) + (1,), P(tip, -h) + (1,), P(tip, h) + (1,), P(er, h) + (1,)]
    out = [shape([P(0, -h) + (1,), P(er, -h) + (1,), P(er, h) + (1,), P(0, h) + (1,)], "#e8a0a8", "", w=2.6, seed=seed)]
    out.append(shape([P(er - 3, -h - 1) + (1,), P(er + 6, -h - 1) + (1,), P(er + 6, h + 1) + (1,), P(er - 3, h + 1) + (1,)], "#c9c2b0", "", w=2.2, seed=seed + 1))
    out.append(shape(body, "#f2b33a", blob([P(er + 6, 0), P(tip, 0), P(tip, h), P(er + 6, h)], "#d4902a"), w=2.6, seed=seed + 2))
    out.append(shape([P(tip, -h) + (1,), P(L, 0) + (1,), P(tip, h) + (1,)], "#efd2a6", blob([P(L * .94, -h * .3), P(L, 0), P(L * .94, h * .3)], "#3a3036"),
                     w=2.4, seed=seed + 3))
    return "".join(out)
