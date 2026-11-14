"""Общие помощники групп E и F рилса 71 (время слов, кривые, хлёст, кисть). Только хореография — предметы, люди, кот и комната
берутся из common/ (props, people, cat, room)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
from lib import clamp, ease_io, ease_out  # noqa: E402

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


def we(i):
    return WORDS[i]["end"]


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if (u <= 0 or u >= 1) else math.sin(math.pi * u) ** 2


def decay(t, t0, k=9.0, fr=18.0):
    if t < t0:
        return 0.0
    u = t - t0
    return math.exp(-k * u) * math.sin(2 * math.pi * fr * u)


def blinks(t, times, dur=.16):
    v = 0.0
    for tb in times:
        u = (t - tb) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def whip(g, t, t_in, amp=280.0, blur=30.0, dur=.2, side=-1):
    """Хвост хлёста на входе плана: приезжает сбоку с размытием по x, гаснет за dur."""
    e = ease_out(clamp((t - t_in) / dur), 2)
    dx, b = side * amp * (1 - e), blur * (1 - e)
    g = f'<g transform="translate({dx:.1f} 0)">{g}</g>'
    if b > .5:
        fid = lib.uid("wb")
        lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-5%" width="140%" height="110%"><feGaussianBlur stdDeviation="{b:.1f} 0"/></filter>')
        g = f'<g filter="url(#{fid})">{g}</g>'
    return g


def shake(t, t0, amp, k=9.0, fr=19.0):
    return amp * decay(t, t0, k, fr), amp * .6 * decay(t, t0 + .03, k, fr * 1.13)


# ───────── ступни Димы без кроссовок: босая (people.sock) и в полосатом носке (props.sock_worn) ─────────
import contextlib  # noqa: E402

import people  # noqa: E402
import props as PR  # noqa: E402


@contextlib.contextmanager
def bare_feet(near="sock", far="sock", pull=1.0):
    """На время вызова people.dima(...) кроссовки заменяются ступнями: "bare" — босая, "sock" — в полосатом носке (pull 0…1 —
    насколько натянут). near — ближняя нога (far=False в people.leg), far — дальняя. Только общие рисунки people/props."""
    orig = people.shoe

    def foot(A, phi, is_far, seed, who):
        kind = far if is_far else near
        d = (math.cos(phi), math.sin(phi))
        Ab = (A[0] + 4, A[1] + 30)          # подошва босой ступни на линии подошвы кроссовка
        o = people.sock(Ab, d, is_far, seed + 1)
        if kind == "sock":
            o += PR.sock_worn(Ab[0] - 6, Ab[1] - 2, 1.0, d, pull=pull, seed=seed % 97)
        return o

    people.shoe = foot
    try:
        yield
    finally:
        people.shoe = orig


# ───────── ноутбук ЭКРАНОМ К ДИМЕ (Дима слева, лицом вправо): вид сбоку в три четверти ─────────
# В общем props.laptop экран смотрит на зрителя (промах 70) — здесь крышка шарниром у дальнего от Димы края, экран повёрнут к нему,
# зритель видит его под острым углом узкой полосой (свет и волнистые штрихи, без букв). TODO: перенести в props, когда появится общий.
def laptop_side(x, y, k=1.0, open_=1.0, on=0.0, lines=0.0, t=0.0, seed=0):
    """(x, y) — середина переднего (к Диме) края корпуса на столе. open_ 0…1 (0 — закрыт), on 0…1 — экран светится.
    Возвращает dict(svg, lid_top (ближний верхний угол крышки, мир), screen (центр экрана), keys)."""
    from lib import INK as _INK, blob as _blob, line as _line, shape as _shape
    D, Wz, L, TH = 250.0, 330.0, 270.0, 16.0
    zx, zy = .3 * Wz, -.16 * Wz           # смещение «вглубь» (дальний бок ноутбука)

    def P(px, py):
        return (x + px * k, y + py * k)

    def Z(p, u=1.0):
        return (p[0] + zx * k * u, p[1] + zy * k * u)
    o = []
    # корпус: верхняя грань (параллелограмм) и передний торец
    a, b = P(0, -TH), P(D, -TH)
    top = [a, b, Z(b), Z(a)]
    keys_in = ""
    for r_ in range(4):
        u0, u1 = .14 + r_ * .19, .14 + r_ * .19 + .13
        for c_ in range(6):
            v0, v1 = .12 + c_ * .13, .12 + c_ * .13 + .1
            q = [(a[0] + (b[0] - a[0]) * v0 + zx * k * u0, a[1] + zy * k * u0), (a[0] + (b[0] - a[0]) * v1 + zx * k * u0, a[1] + zy * k * u0),
                 (a[0] + (b[0] - a[0]) * v1 + zx * k * u1, a[1] + zy * k * u1), (a[0] + (b[0] - a[0]) * v0 + zx * k * u1, a[1] + zy * k * u1)]
            keys_in += _blob(q, "#3A3F49")
    o.append(_shape(top, "#C9CDD5", keys_in, w=3.8, seed=7600 + seed))
    o.append(_shape([P(0, -TH), P(D, -TH), P(D, 0), P(0, 0)], "#9FA4AE", "", w=3.6, seed=7601 + seed))
    # крышка: от шарнира (дальний край b) поворачивается на угол th; 0 — лежит на корпусе к Диме
    th = math.radians(108 * max(0.0, min(1.0, open_)))
    dv = (-math.cos(th), -math.sin(th))
    h0 = P(D, -TH)
    h1 = (h0[0] + dv[0] * L * k, h0[1] + dv[1] * L * k - TH * k * .6)
    lid = [h0, h1, Z(h1), Z(h0)]
    screen_c = ((h0[0] + h1[0]) / 2 + zx * k * .5, (h0[1] + h1[1]) / 2 + zy * k * .5)
    if th < math.radians(62):      # видна внешняя сторона крышки
        o.append(_shape(lid, "#AEB3BD", "", w=3.8, seed=7602 + seed))
    else:
        o.append(_shape(lid, "#2E323A", "", w=3.8, seed=7603 + seed))
        ins = .1

        def Lp(u, v):          # u — вдоль крышки (0 шарнир, 1 верх), v — поперёк (0 ближний, 1 дальний)
            px = h0[0] + (h1[0] - h0[0]) * u + zx * k * v
            py = h0[1] + (h1[1] - h0[1]) * u + zy * k * v
            return (px, py)
        scr = [Lp(.06, ins), Lp(.94, ins), Lp(.94, 1 - ins), Lp(.06, 1 - ins)]
        col = lib.mix("#141821", "#F4F7FF", max(0.0, min(1.0, on)))
        inner = ""
        if lines > 0 and on > .5:
            n = 6
            for j in range(n):
                q = max(0.0, min(1.0, lines * n - j))
                if q <= 0:
                    break
                u_ = .85 - j * .12
                pts = [Lp(u_, .2 + .6 * s_ * q) for s_ in (0, .25, .5, .75, 1)]
                pts = [(p[0] + 1.5 * math.sin(i * 2.1 + j), p[1]) for i, p in enumerate(pts)]
                inner += _line(pts, 2.6 * k, "#5B6170", taper=.2, wmin=.6, seed=7610 + seed + j)
        o.append(_shape(scr, col, inner, w=2.4, seed=7604 + seed))
    return dict(svg="".join(o), lid_top=h1, screen=screen_c, keys=((a[0] + b[0]) / 2 + zx * k * .4, a[1] + zy * k * .4), hinge=h0)
