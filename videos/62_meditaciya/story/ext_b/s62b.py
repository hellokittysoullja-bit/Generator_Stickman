"""Рилс 62 «медитация», группа B — Дима и кот крупно: s06 (лицо Димы вплотную: один глаз распахивается пружиной, зрачок мечется,
бровь взлетает, капля пота), s10 (комната общим планом: расстроенный Дима в лотосе слева, кот входит шагами справа и садится с
отскоком, Дима косится), s11 (кот крупно три четверти: полуприкрытые глаза, взгляд в светящуюся точку, медленное дыхание, край тучи
тает). frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Люди и кот — ../common/people.py, cat.py; предметы — props.py; комната —
room.py (группа E), пока её нет — своя простая комната. Печатных букв и цифр нет."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import cat as Cat  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import (INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rect_pts, shape, smooth, spring)  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
E = people.EXPR


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def decay(t, t0, k=9.0, fr=22.0):
    if t < t0:
        return 0.0
    u = t - t0
    return math.exp(-k * u) * math.sin(2 * math.pi * fr * u)


def shake2(t, t0, amp, k=9.0, fr=19.0):
    return amp * decay(t, t0, k, fr), amp * .7 * decay(t, t0 + .013, k, fr * 1.13)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_of(t, times, dur=.14):
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            return math.sin(math.pi * u)
    return 0.0


def head_tf(res, ang_deg=0.0):
    """Трансформ в систему головы фигуры (для наложений на лицо)."""
    hx, hy = res["head"]
    return f"translate({hx:.2f} {hy:.2f}) rotate({ang_deg:.3f}) scale({res['scale']:.4f})"


# ═════════════════════════════ s06: лицо вплотную ═════════════════════════════
T_POTOM, T_PODUMAL = 8.32, 8.773


def s06(t):
    lib.dyn_begin()
    S = 3.3
    hx, hy = 0.0, 0.0
    # дыхание и мелкое покачивание головы с первого кадра; на «Потом» голова чуть дёргается назад
    ha = .03 * math.sin(2 * math.pi * (t - 7.75) / 1.6) - .05 * bump(t, T_POTOM, .3) + .04 * bump(t, T_PODUMAL, .3)
    jolt = -18 * bump(t, T_POTOM - .02, .24)
    open_u = t - T_POTOM
    ex = {"mouth": "flat", "bags": True}
    # до «Потом»: оба глаза закрыты спокойными дугами, брови сведены от старания, рот сжат
    if open_u < 0:
        ex.update(shut_n=1.0, shut_f=1.0, brows="pinch", mouth="flat")
    else:
        sc = 1.0 + .5 * spring(open_u, 2.6, 6.0)           # глаз распахивается пружиной (перелёт к 1.5, к 1.38)
        sc = 1.0 + (sc - 1.0) * .5
        ex.update(shut_n=1.0, shut_f=0.0, scale_f=sc, lid=1.0)
        # зрачок мечется: влево-вправо, всё быстрее, на «подумал» — замер вверху
        if t < T_PODUMAL:
            ph = (t - T_POTOM - .12)
            lx = .85 * math.sin(2 * math.pi * 3.1 * max(0.0, ph)) if ph > 0 else 0.0
            ex["look_f"] = (lx, .1 * math.sin(2 * math.pi * 6.2 * max(0.0, ph)))
        else:
            u2 = t - T_PODUMAL
            ex["look_f"] = (-.75 + .9 * math.sin(2 * math.pi * 2.4 * u2) * math.exp(-2.5 * u2), -.45)
        ub = clamp((t - T_PODUMAL + .02) / .16)
        ub = ease_out(ub, 3)
        ex["brows"] = ("pinch", "one_up", min(1.0, .35 * clamp(open_u / .15) + .65 * ub + .15 * bump(t, T_PODUMAL, .3)))
        ex["mouth"] = "o" if t > T_PODUMAL + .05 else "frown"
        ex["open"] = .25 + .2 * clamp((t - T_PODUMAL) / .3)
    res = people.figure("dima", hx, hy, S, ex, layers=("body",), head_ang=ha, head_off=(0, jolt / S))
    head = np.array(res["head"])
    ang = math.degrees(ha)
    # камера: голова в кадре, медленный наезд с первого кадра, на «Потом» — резкий наезд к распахнутому глазу
    eye_w = head + np.array([92 * S, -10 * S])     # дальний глаз (правый в кадре)
    face_c = head + np.array([24 * S, 0 * S])
    z0 = 1.0 + .03 * clamp((t - 7.75) / 1.6)
    zu = ease_out(clamp((t - T_POTOM) / .2), 3)
    zoom = z0 * (1 + .34 * zu) + .04 * bump(t, T_PODUMAL, .25)
    foc = face_c + (eye_w - face_c) * zu * .8
    sx, sy = shake2(t, T_POTOM, 16)
    sx2, sy2 = shake2(t, T_PODUMAL, 9)
    cx_, cy_ = foc[0] - (sx + sx2) / zoom, foc[1] + 60 - (sy + sy2) / zoom
    set_ink(1.0)
    o = []
    bg = lib.lin_grad([(0, "#F6CF9C", 1), (.55, "#F0BA80", 1), (1, "#E3A06A", 1)], 0, 0, 0, 1)
    o.append(f'<rect width="1080" height="1920" fill="url(#{bg})"/>')
    # тёплые штрихи-лучи по фону (вибрация тревоги после «Потом»)
    if open_u > 0:
        a = clamp(open_u / .15) * (0.55 + .25 * math.sin(t * 40))
        for i in range(10):
            th = i / 10 * 2 * math.pi + .2
            r0, r1 = 470, 640 + 30 * math.sin(t * 25 + i)
            o.append(line([(540 + math.cos(th) * r0, 820 + math.sin(th) * r0), (540 + math.cos(th) * r1, 820 + math.sin(th) * r1)], 7,
                          "#D98A4E", seed=600 + i, op=a, taper=.5, wmin=.2))
    w = [res["svg"]]
    # морщинка между бровей и складки лба от старания
    hk = []
    tense = 1.0 - .6 * clamp(open_u / .2) if open_u > 0 else 1.0
    hk.append(line([(56, -76), (60, -60)], 3.0, people.PAL["dima"]["SKIN_SH2"], seed=611, op=.9 * tense))
    hk.append(line([(68, -74), (68, -60)], 2.6, people.PAL["dima"]["SKIN_SH2"], seed=612, op=.8 * tense))
    # капля пота на виске (ближний, слева в кадре): выступает на «подумал» и сползает
    du = t - T_PODUMAL
    if du > 0:
        g = ease_out(clamp(du / .18), 3)
        slide = 40 * clamp((du - .25) / .5) ** 1.5
        hk.append(PR.sweat(-30, -62 + slide, 1.1 * g, 0))
        if du > .3:
            hk.append(PR.sweat(-58, -30 + 30 * clamp((du - .5) / .4), .6 * clamp((du - .3) / .15), 0))
    w.append(f'<g transform="{head_tf(res, ang)}">{"".join(hk)}</g>')
    # «вскрик» распахнутого глаза: короткие штрихи вокруг
    if 0 < open_u < .5:
        a = 1 - open_u / .5
        for i in range(5):
            th = -1.4 + i * .5
            r0 = 70 * S * .9
            c = eye_w
            o_ = [(c[0] + math.cos(th) * r0, c[1] + math.sin(th) * r0 * .9), (c[0] + math.cos(th) * (r0 + 60 * a + 20), c[1] + math.sin(th) * (r0 + 60 * a + 20) * .9)]
            w.append(line(o_, 9, INK, seed=630 + i, op=a, taper=.5, wmin=.2))
    o.append(f'<g transform="{lib.cam(cx_, cy_, zoom, -1.2 * bump(t, T_POTOM, .3))}">{"".join(w)}</g>')
    return lib.svg("".join(o))


# ═════════════════════════════ s11: кот крупно ═════════════════════════════
def s11(t):
    lib.dyn_begin()
    t0 = 15.95
    u = t - t0
    # кот (cat.py, анфас; голова чуть повёрнута — три четверти влево к точке)
    k = 3.4
    x, y = 420, 1830
    look_ = (-.25 - .15 * smooth(16.6, 16.9, t), .05 - .45 * smooth(16.6, 16.9, t))
    st = {"turn": -.55, "look": look_, "tail": -6 + 2 * math.sin(2 * math.pi * u / 3.3)}
    # полуприкрытые глаза: на «спокойно» веки опускаются до половины, редкое медленное моргание
    lid = .2 + .22 * ease_io(clamp((t - 16.22) / .45))
    bl = blink_of(t, [17.62], .38)
    st["blink"] = 1.0 if bl > .55 else min(.75, lid + (0.75 - lid) * bl)
    st["breath"] = 1.0
    st["ear"] = 0.0
    st["tilt"] = -3 + .8 * math.sin(2 * math.pi * u / 3.3)
    # медленное дыхание боками: заметный вдох-выдох (период 2.4 с)
    br = math.sin(2 * math.pi * (u + .3) / 2.4)
    st["sx"] = 1 + .022 * br
    st["sy"] = 1 + .014 * br
    cat = Cat.draw(x, y, k, st, t)
    # точка-пылинка перед носом
    nose = (x + (836 - 22 * .55 - Cat.CX) * k, y + (1112 - Cat.CBOT) * k)
    mx, my = 360 + 5 * math.sin(t * 1.3), 380 + 6 * math.sin(t * .9)
    glow_u = .25 + .75 * smooth(17.18, 17.6, t)
    set_ink(1.0)
    o = []
    bg = lib.lin_grad([(0, "#3B3A52", 1), (.45, "#5A5068", 1), (1, "#7A6672", 1)], 0, 0, 0, 1)
    o.append(f'<rect width="1080" height="1920" fill="url(#{bg})"/>')
    # пол-коврик (тёплая полоса) — кот сидит на нём
    o.append(shape([(-60, 1560), (1140, 1530), (1140, 2000), (-60, 2000)], "#6FA58A",
                   blob([(-60, 1620), (1140, 1600), (1140, 2000), (-60, 2000)], "#5B8C74"), w=4.0, seed=701))
    # край тучи Димы сверху: бледнеет и тает
    fade = 1 - smooth(16.3, 17.9, t)
    if fade > .02:
        st_ = PR.storm(380 + 40 * u, 150 - 60 * (1 - fade), 900, 300, 1.0, 1.0 * (.6 + .4 * fade), seed=4)
        o.append(f'<g opacity="{fade:.3f}">{st_}</g>')
    w = [cat]
    w.append(PR.mote(mx, my, 11, glow_u))
    # тонкая линия взгляда — едва заметная пунктирная дорожка от глаз к точке, появляется на «смотрел»
    gu = smooth(16.68, 17.0, t) * (1 - .6 * smooth(17.5, 18.1, t))
    if gu > .02:
        ex_ = (x + (CXL := (836 - 44 - 22 * .55 - Cat.CX)) * k, y + (1072 - Cat.CBOT) * k)
        pts = [(ex_[0] + 10, ex_[1] - 90), (mx + 10, my + 30)]
        n = 7
        for i in range(n):
            a = i / n
            if a > gu:
                break
            p = (pts[0][0] + (pts[1][0] - pts[0][0]) * a, pts[0][1] + (pts[1][1] - pts[0][1]) * a)
            w.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4" fill="#F2E4B8" opacity="{.55 * gu:.3f}"/>')
    z = 1.0 + .07 * ease_io(clamp((t - 15.95) / 2.4))
    fx_ = 520 - 40 * clamp(u / 2.4)
    o.append(f'<g transform="{lib.cam(fx_, 960 - 50 * clamp(u / 2.4), z, .3 * math.sin(u * .9))}">{"".join(w)}</g>')
    del nose
    return lib.svg("".join(o))


# ═════════════════════════════ s10: кот входит в комнату и садится рядом ═════════════════════════════
T_KOT, T_SEL, T_RYADOM = 15.26, 15.50, 15.733


def s10(t):
    lib.dyn_begin()
    DX = -175.0                     # подушка и Дима левее центра: справа место коту
    hx, hy = R.seat()
    hx += DX
    s = 1.08
    # Дима расстроен: сполз, губа дрожит, дыхание тяжёлое; на «рядом» косится на кота (голова чуть к нему)
    br = math.sin(2 * math.pi * (t - 14.55) / 1.7)
    if t < T_RYADOM:
        ex = dict(E["dima"]["upset"], trem=t)
    else:
        u = smooth(T_RYADOM, T_RYADOM + .18, t)
        ex = dict(E["dima"]["side_eye"], mouth="wobble", trem=t * .5, look=(.6 + .35 * u, .15 - .1 * u))
        if u < .5:
            ex = dict(E["dima"]["upset"], trem=t, look=(.6, .2))
    kw = people.lotus_kw("slump", hx, hy + 6 * br, s, sag=.6)
    kw["head_ang"] += .05 * br - .14 * smooth(T_RYADOM, T_RYADOM + .25, t)
    kw["lean"] += .015 * br
    fig = people.figure("dima", hx, hy + 6 * br, s, ex, **kw)
    # кот: шагает справа (лапы по очереди), на «кот» останавливается, на «сел» садится с отскоком, хвост обвивает лапы
    FLOOR_Y = 1745.0
    k = 1.25
    x_end = 790.0
    if t < T_KOT:
        u = clamp((t - 14.4) / (T_KOT - 14.4))
        x = 1400 + (x_end - 1400) * (1 - (1 - u) ** 1.6)
        walk = (t - 14.4) / .36
        st = {"turn": -.45, "look": (-.6, .1), "legs": .3, "perk": .4}
        cat = people.cat_walk(x, FLOOR_Y, k, t, st, period=.36)
    else:
        x = x_end
        sx_, sy_ = 1.0, 1.0
        legs = .3
        tail = -4.0
        st = {"turn": -.45 + .2 * smooth(T_SEL, T_SEL + .4, t), "look": (-.6 + .4 * smooth(T_SEL + .2, T_SEL + .6, t), .1), "perk": .4 * (1 - smooth(T_SEL, T_SEL + .3, t))}
        if t >= T_SEL:
            e = t - T_SEL
            legs = .3 * (1 - ease_out(clamp(e / .12), 2))
            sx_, sy_ = PR.squash(t, T_SEL + .1, amp=.16, freq=2.6, damp=6.0)
            tail = -4 + 14 * ease_out(clamp(e / .45), 3)
            st["blink"] = .35 * smooth(T_SEL + .3, T_SEL + .6, t)
        st.update(legs=legs, sx=sx_, sy=sy_, tail=tail, rot=-2 * decay(t, T_KOT, 6, 3))
        cat = people.cat_svg(x, FLOOR_Y, k, st, t)
    rb = R.room_bg(t, "evening")
    w = [rb["bg"], R.cushion_layer(1.0, DX), fig["svg"], cat, rb["front"]]
    # камера: общий план, лёгкая панорама за котом, мини-толчок на «сел»
    pan = 610 - 50 * ease_io(clamp((t - 14.55) / 1.2))
    sx, sy = shake2(t, T_SEL + .1, 5)
    set_ink(1.0)
    o = [f'<g transform="{lib.cam(pan - sx, 1080 - sy, 1.0 + .015 * clamp((t - 14.55) / 1.8))}">{"".join(w)}</g>']
    return lib.svg("".join(o))


def frame(sid, t):
    return {"s06": s06, "s10": s10, "s11": s11}[sid](t)
