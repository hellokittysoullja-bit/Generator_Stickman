"""Рилс 83 «12 лет в телефоне»: возраст Димы параметром expr["age"] (0 — школьник, 1 — студент, 2 — борода, 3 — седина).
Голова та же (рилс 23: FACE, глаза, причёска), меняются только: цвет волос и бровей (седеет с 2 до 3), щетина → борода
(растёт с 1.2 до 2.1), мешки под глазами (с 0.6), морщины (с 2.2). Без age голова байт в байт прежняя.
Используется в common/people.py (dima_head) и ext_a/rdima.py (head)."""
import math

import lib

GREY = ("#cfccc6", "#9d9993", "#efede9")


def colors(age, hair, hair_sh, hair_hi):
    g = lib.smooth(2.05, 2.9, age)
    return lib.mix(hair, GREY[0], g), lib.mix(hair_sh, GREY[1], g), lib.mix(hair_hi, GREY[2], g)


def stubble(age):
    """Доля прежней щетины: школьник 0, студент 0.45, дальше 1."""
    return lib.smooth(0.35, 1.0, age) * 0.45 + lib.smooth(1.0, 1.5, age) * 0.55


def bags(age):
    return lib.smooth(0.5, 1.2, age)


JAW = [(-88, 46), (-60, 88), (-30, 112), (2, 124), (30, 126), (62, 116), (90, 96), (108, 64), (114, 40)]
BEARD = [(-96, 40), (-74, 100), (-40, 150), (2, 178), (40, 182), (78, 162), (104, 122), (118, 76), (118, 40)]
TOP = [(112, 52), (98, 66), (86, 80), (64, 80), (42, 82), (22, 86), (-4, 74), (-40, 52), (-70, 22), (-90, 14)]


def beard(age, hair, hair_sh, shape, line):
    """Борода поверх лица (до рта): край растёт от линии челюсти до BEARD; усы — штрихом над губой."""
    b = lib.smooth(1.2, 2.1, age)
    if b < 0.02:
        return ""
    low = [(j[0] + (q[0] - j[0]) * b, j[1] + (q[1] - j[1]) * b) for j, q in zip(JAW, BEARD)]
    pts = low + TOP
    inner = lib.blob([(-100, 30), (-40, 60), (0, 120), (20, 200), (-100, 200)], hair_sh, .75)
    for k in range(7):
        x = -60 + k * 24
        inner += line([(x, 96 + 6 * math.sin(k)), (x + 6, 120 + 30 * b)], 2.2, hair_sh, seed=2300 + k, op=.7)
    o = f'<g opacity="{min(1.0, b * 1.6):.3f}">' + shape(pts, hair, inner, w=4.6, seed=2290)
    o += line([(32, 84), (56, 78), (80, 80), (96, 88)], 9.0 * b, hair, seed=2310, taper=.3, wmin=.5)
    return o + "</g>"


def wrinkles(age, col, line):
    w = lib.smooth(2.2, 2.9, age)
    if w < 0.02:
        return ""
    o = ""
    for k, y in enumerate((-112, -100)):
        o += line([(-24, y), (14, y - 6), (52, y - 2)], 2.4, col, seed=2320 + k, op=.8 * w)
    o += line([(-46, -16), (-56, -4)], 2.2, col, seed=2330, op=.8 * w)
    o += line([(-48, -2), (-58, 8)], 2.2, col, seed=2331, op=.7 * w)
    o += line([(38, 30), (46, 44), (44, 58)], 2.2, col, seed=2332, op=.7 * w)
    return o
