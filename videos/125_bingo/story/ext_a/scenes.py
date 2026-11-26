"""Рилс 125 «СДВГ-бинго», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json. Карточка бинго 3×3: в каждой клетке рисунок пункта; кот лапой с маркером
ставит отметку в клетку на её слове (shots.json "cells": mark). Каждый план пункта — камера на свою клетку, рисунок клетки
живёт. «У меня бинго» — Дима крупно с карточкой, вспышка «БИНГО!». Призыв — число в комментариях (поле с цифрой).
NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402

HIT = stress(0, .3)
CX0, CY0, CELL = 540.0, 1000.0, 300.0
MARKS = [c["mark"] for c in SH["cells"]]
LIME = "#7bd65a"
CAT_FUR, PAD = CT.CAT, "#e8823a"


def cell_c(i):
    r, c = divmod(i, 3)
    return CX0 + (c - 1) * (CELL + 14), CY0 + (r - 1) * (CELL + 14)


# ─────────── рисунки клеток (центр 0,0, поле ±130) ───────────
def ic_tabs(t, u):
    n = 3 + int(37 * u)
    o = shape(lib.rrect(-120, -90, 120, 100, 14), "#ffffff", "", w=4, seed=8000)
    o += rect(-118, -88, 118, -50, "#dfe3ea")
    w = 236 / min(n, 40)
    for j in range(min(n, 40)):
        o += rect(-118 + w * j + 1, -88, -118 + w * (j + 1) - 1, -60, ("#7fb2ff", "#ffb3c7", "#b9e8a0", "#ffe08a")[j % 4])
    o += text(str(min(40, n)), 0, 60, 110, fill="#e2453a", stroke="#111", sw=8)
    return o


def ic_kettle(t, u):
    o = shape([(-90, 90, 1), (90, 90, 1), (70, -40), (0, -70), (-70, -40)], "#c9cdd5", "", w=5, seed=8010)
    o += line([(80, 10), (130, -40)], 16, "#9aa0aa", taper=0, wmin=1, seed=8011)
    o += shape(ellipse_pts(0, -78, 26, 12, 10), "#5a5f6e", "", w=4, seed=8012)
    st = 1 - u
    for j in range(3):
        ph = (t * .8 + j / 3) % 1
        o += line([(130 + 10 * math.sin(ph * 8), -50 - 80 * ph), (140 + 10 * math.sin(ph * 8 + 1), -80 - 80 * ph)], 6, "#ffffff", seed=8013 + j,
                  op=st * (1 - ph))
    if u > .3:
        o += text("×3", -40, 60, 90, fill="#2f8fe0", stroke="#111", sw=6)
    return o


def ic_door(t, u):
    o = shape(lib.rect_pts(-80, -120, 80, 120), "#b8865a", "", w=5, seed=8020)
    o += shape(ellipse_pts(50, 10, 10, 10, 8), "#ffd35a", "", w=3, seed=8021)
    o += text("?", 40 + 6 * math.sin(t * 6), -10, 200 * (.5 + .5 * u), fill="#FFD23F", stroke="#111", sw=10)
    return o


def ic_three(t, u):
    o = ""
    for j in range(3):
        o += shape(lib.rrect(-120 + 82 * j, -110, -50 + 82 * j, -40, 10), "#f2b541", "", w=4, seed=8030 + j)
    o += text("3", -90, 40, 90, fill="#1d2448", stroke="#fff", sw=4)
    o += line([(-40, 20), (30, 20)], 8, "#1d2448", seed=8034)
    o += line([(10, 0), (30, 20), (10, 40)], 8, "#1d2448", seed=8035)
    o += text("0", 80, 50 * 1 + 4, 120 * (.6 + .4 * u), fill="#e2453a", stroke="#111", sw=8)
    return o


def ic_unsent(t, u):
    o = PR.thought_cloud(0, -30, .9, w=240, h=150, u=1.0, seed=3, inner=plain("ответ", -60, 12, 48, fill="#1d2448"))
    o += shape(lib.rrect(-90, 70, 90, 120, 25), "#c9cdd5", "", w=4, seed=8040)
    o += text("✕", 0, 112, 46, fill="#7d8597", stroke="#7d8597", sw=1)
    return o


def ic_keys(t, u):
    o = shape(lib.rrect(-90, -120, 90, 120, 16), "#f2f4f7", "", w=5, seed=8050)
    o += rect(-80, -110, 80, 110, "#dff1ff")
    o += line([(-80, 0), (80, 0)], 4, "#9aa0aa", taper=0, wmin=1, seed=8051)
    sw = 10 * math.sin(t * 5)
    kg = (f'<circle cx="0" cy="0" r="18" fill="none" stroke="#c9a640" stroke-width="7"/>'
          f'<path d="M16 6 L56 6 L56 18 M44 6 L44 16" fill="none" stroke="#c9a640" stroke-width="7"/>')
    o += f'<g transform="translate(-20 -30) rotate({sw:.1f})">{kg}</g>'
    o += PR.star4(30, -60, 14 * u + 1)
    return o


def ic_night(t, u):
    o = shape(lib.rrect(-125, -125, 125, 125, 16), "#2e3150", "", w=4, seed=8060)
    o += PR.moon(-60, -60, 26, .6)
    o += PR.laptop(20, 90, .3, 1.0, screen="page", lines=u, t=t)
    o += PR.sparkles(20, 20, .8, u, t, seed=8061, n=4, r=90)
    return o


def ic_timer(t, u):
    o = shape(lib.rrect(-120, -70, 120, 70, 30), "#1d2448", "", w=5, seed=8070)
    mins = 5 + int(55 * u)
    o += text(f"{mins}:00", 0, 30, 92, fill=LIME if mins < 6 else "#FFD23F", stroke="#111", sw=3)
    return o


def ic_planner(t, u):
    o = shape(lib.rrect(-90, -115, 90, 115, 12), "#3fa7a0", "", w=5, seed=8080)
    o += rect(40, -115, 56, 115, "#e2453a")
    for j in range(6):
        o += f'<circle cx="-90" cy="{-90 + 36 * j}" r="9" fill="none" stroke="#5a5f6e" stroke-width="5"/>'
    o += rect(-60, -70, 70, -30, "#fbf8f1", .9)
    for j in range(8):
        o += f'<circle cx="{-80 + 22 * j:.0f}" cy="{-100 + 9 * (j % 3):.0f}" r="3" fill="#9aa0aa" opacity="{.4 + .6 * u:.2f}"/>'
    o += PR.cobweb(-90, -115, .7 * u, t=t, ang=45, seed=4)
    return o


ICONS = [ic_tabs, ic_kettle, ic_door, ic_three, ic_unsent, ic_keys, ic_night, ic_timer, ic_planner]


def stamp(x, y, u, t):
    """Отметка: лаймовый круг маркера и галочка; u — проявление (0…1)."""
    if u <= 0:
        return ""
    s = lib.back_out(clamp(u / .6), 2.4) if u < .6 else 1.0
    o = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{118 * s:.1f}" fill="{LIME}" opacity=".35"/>'
    o += PR.check_mark(x + 70, y + 80, 2.2, ramp(u, .3, .5), w=8)
    return o


def card(t, focus=None, live=None):
    """Карточка бинго: рамка, «БИНГО» сверху, 9 клеток с рисунками; отметки — по MARKS. live — индекс клетки, чей рисунок
    анимируется (u растёт к отметке)."""
    o = [shape(lib.rrect(CX0 - 500, CY0 - 640, CX0 + 500, CY0 + 500, 40), "#ffe08a", "", w=7, seed=8100)]
    for j, ch in enumerate("БИНГО"):
        o.append(text(ch, CX0 - 340 + 170 * j, CY0 - 520, 110, fill=("#e2453a", "#2f8fe0", "#3fb26a", "#8a63d2", "#ff8a3d")[j], stroke="#111", sw=8))
    for i in range(9):
        x, y = cell_c(i)
        o.append(shape(lib.rrect(x - CELL / 2, y - CELL / 2, x + CELL / 2, y + CELL / 2, 24), "#fbf8f1", "", w=5, seed=8110 + i))
        if live == i:
            st = MARKS[i] - 1.6
            u = clamp((t - st) / 1.4)
        else:
            u = 1.0 if t > MARKS[i] else 0.0
        o.append(tf(ICONS[i](t, u), x, y, 1.0))
        o.append(stamp(x, y, (t - MARKS[i]) / .35, t))
    return "".join(o)


def paw(tx, ty, u, t):
    """Лапа кота снизу справа с маркером к точке (tx, ty); u 0 — у края, 1 — касается."""
    sx, sy = tx + 520, ty + 900
    x, y = sx + (tx - sx) * u, sy + (ty - sy) * u
    o = shape(lib.band([(x + 520, y + 900), (x + 60, y + 90)], 150, 120), CAT_FUR, "", w=6, seed=8200)
    o += shape(ellipse_pts(x + 50, y + 80, 80, 66, 16), CAT_FUR, "", w=6, seed=8201)
    for j, (dx, dy) in enumerate(((-10, 50), (30, 30), (70, 40))):
        o += blob(ellipse_pts(x + dx + 20, y + dy + 70, 14, 11, 8), PAD)
    mk = shape(lib.rrect(-34, -110, 34, 60, 16), "#e2453a", "", w=5, seed=8202) + shape(ellipse_pts(0, -110, 34, 12, 12), LIME, "", w=4, seed=8203)
    o += tf(mk, x + 10, y + 20, 1.0, -25)
    return o


def paw_u(t, tm):
    """Лапа: подлетает к клетке к tm, удар, отходит."""
    return clamp(1 - abs(t - tm) / .45) ** .6


def frame_s01(t):
    """ХУК: карточка бинго, клетки подпрыгивают волной, кот выглядывает справа с маркером."""
    o = [paper_bg(), card(t)]
    for i in range(9):
        pass
    o.append(cat(980, 1640, .9, t, dict(look=(-.8, -.5), smile=1.0, paw=.7, tail=12 * math.sin(t * 4))))
    o.append(PR.sparkles(540, 1000, 2.6, bump(t, W(0) + .6, .05, .5), t, seed=11, n=8, r=520))
    dx, dy = shake(t, W(0) + .6, 9)
    return hook_view("".join(o), t, HIT, 560, 1040, 1.0, 0, bg=PAPER, dx=dx, dy=dy)


def frame_s02(t):
    """«Посмотрим, сколько у тебя совпадёт»: кот заносит маркер над карточкой, счётчик «?/9»."""
    a, b = T0("s02"), T1("s02")
    o = [paper_bg(), card(t)]
    o.append(paw(540, 1000, .45 + .1 * math.sin(t * 6), t))
    o.append(text("?/9", 540, 1660, 140 * pop(t, W(2), .25), fill="#FFD23F", stroke="#111", sw=10) if t > W(2) else "")
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(5), 8)
    return view("".join(o), 560 + dx, 1080 + dy, .95 + .06 * u, 0, bg=PAPER, t=t)


def cell_frame(i, t):
    a, b = T0(f"s{i + 3:02d}"), T1(f"s{i + 3:02d}")
    tm = MARKS[i]
    x, y = cell_c(i)
    o = [paper_bg(), card(t, live=i)]
    o.append(PR.sparkles(x, y, 1.6, bump(t, tm, .05, .5), t, seed=300 + i, n=6, r=200))
    o.append(paw(x, y, paw_u(t, tm), t))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tm, 9)
    cx = x + (CX0 - x) * .08
    cy = y + (CY0 - y) * .08 + 20
    return view("".join(o), cx + dx, cy + dy, 2.45 + .12 * u, (-1.5 + 3 * u) * (1 if i % 2 else -1), bg=PAPER, t=t)


for _i in range(9):
    globals()[f"frame_s{_i + 3:02d}"] = (lambda i: (lambda t: cell_frame(i, t)))(_i)


def frame_s12(t):
    """«У меня бинго по всем девяти»: Дима крупно держит карточку, все клетки отмечены; на «бинго» вспышка и «БИНГО!»."""
    a, b = T0("s12"), T1("s12")
    tb = W(52)
    o = [plain_room(t), rug(540, RFL + 150, 600)]
    f = stand(240, t, "laugh82" if t > tb else "proud82", "d82_hold", head_add=.05)
    o.append(f["svg"])
    hx, hy = f["hold"]
    o.append(f'<g transform="translate({hx + 230:.1f} {hy - 60:.1f}) scale(.5) translate({-CX0} {-CY0})">{card(t)}</g>')
    o.append(cat(900, RFL, .8, t, dict(look=(-.7, -.6), smile=1.0, tail=12 * math.sin(t * 4))))
    if t > tb:
        o.append(f'<rect x="-1400" y="-1400" width="4000" height="4000" fill="#ffffff" opacity="{.6 * bump(t, tb, .03, .25):.3f}"/>')
        o.append(text("БИНГО!", 560, 470, 200 * pop(t, tb, .25), fill="#FFD23F", stroke="#111", sw=14))
        o.append(PR.sparkles(560, 520, 3.0, bump(t, tb, .05, .7), t, seed=121, n=9, r=480))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb, 12)
    return view("".join(o), 560 + dx, 1000 + dy, 1.1 + .06 * u, 0, t=t)


def comment_field(x, y, digit, t, t_d, k=1.0):
    box = (f'<rect x="-420" y="-150" width="840" height="300" rx="40" fill="#ffffff" stroke="#111" stroke-width="7"/>'
           + f'<path d="M-240 146 l-40 90 l120 -90 z" fill="#ffffff" stroke="#111" stroke-width="7" stroke-linejoin="round"/>'
           + f'<rect x="-416" y="110" width="832" height="36" fill="#ffffff"/>'
           + plain("комментарий", -360, -90, 40, fill="#9aa0aa"))
    return tf(box, x, y, k, -1.5) + word_print(t, t_d, x, y + 95 * k, 260 * k, digit)


def frame_s13(t):
    """ПРИЗЫВ: поле комментария с цифрой уже на первом кадре; цифра растёт 3 → 6 → 9 на словах; ниже карточка и кот."""
    a, b = T0("s13"), T1("s13")
    steps = [a - .45, W(59), W(60)]
    k = sum(1 for q in steps if t >= q)
    digit = ("3", "6", "9")[max(0, k - 1)]
    o = [paper_bg()]
    o.append(comment_field(540, 360, digit, t, steps[max(0, k - 1)], .8))
    o.append(f'<g transform="translate(470 1150) scale(.5) translate({-CX0} {-CY0})">{card(t)}</g>')
    o.append(cat(870, 1380, .8, t, dict(look=(-.6, -.7), smile=1.0, paw=.6, tail=12 * math.sin(t * 4))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, a + .05, 8)
    return view("".join(o), 540 + dx, 960 + dy, 1.0 + .04 * u, 0, bg=PAPER, t=t)


def frame_s14(t):
    """Петля: кадр хука — пустая карточка бинго (отметки сняты), кот с маркером."""
    a, b = T0("s14"), T1("s14")
    o = [paper_bg(), card(-10.0)]
    o.append(cat(980, 1640, .9, t, dict(look=(-.8, -.5), smile=1.0, paw=.7)))
    return loop_view("".join(o), t, a, b, HIT, 560, 1040, 1.0, bg=PAPER)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
