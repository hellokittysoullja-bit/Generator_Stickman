"""Рилс 30 (агент B): мозг с ручками (как в рилсах 25–28, тот же рисунок brain_art) — здесь ещё и на ножках —
и двери-вкладки (над каждой дверью цветной язычок вкладки со значком, без букв). Ночная синяя комната сцен мозга.
s07 «каждый раз, когда ты переключаешься» (12.3–14.2; клип 12.1–14.4): мозг выглядывает из двери почты, на «каждый»
     (12.40) прыгает к двери отчёта и открывает её на «раз» (12.72), на «переключаешься» (13.28) захлопывает её и бежит
     к двери чата, пыль из-под ног; камера едет за ним.
s08 «голове нужно время, чтобы вспомнить, где ты был» (14.2–17.0; клип 14.0–17.2): тёмно, мозг у двери отчёта светит
     фонариком и ищет; над ним на «время» (14.88) выскакивают песочные часы и сыплются; на «вспомнить» (15.52) свободной
     рукой чешет макушку; на «где ты был» (16.08–16.96) луч находит закладку-флажок на двери, она вспыхивает, мозг
     подпрыгивает. Всё — функция общего времени ролика t."""
import math

import numpy as np

import brain_art
import icons
import lib
import scene_brain as sb
from brain_art import BCX, BCY
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg)

FLOOR = sb.FLOOR          # 1160
_ST = {}
CS = 0.62                 # масштаб персонажа
LEG = 230.0               # длина ноги (локально)
BODY_Y = -(LEG + 120)     # центр мозга над полом (локально)
SKIN, SKIN_SH = sb.SKIN, sb.SKIN_SH

# двери: центр по x, цвет язычка, значок
DOORS = [(250.0, ("#ffd25e", "#e0a92c"), "envelope"), (800.0, ("#8fd3ff", "#4f9fd8"), "report"), (1350.0, ("#ff9fc2", "#e06a98"), "chat")]
DW, DH = 300.0, 600.0     # проём


# ───────────────────────── двери-вкладки
def door_back(cx, inner_glow, sd):
    """Проём (тёмная комната за дверью), рама, язычок вкладки над рамой."""
    x0, x1 = cx - DW / 2, cx + DW / 2
    y0, y1 = FLOOR - DH, FLOOR
    s = []
    s.append(shape(rect_pts(x0, y0, x1, y1), "#141a33", blob(rect_pts(x0, y0, x1, y0 + 60), "#0c1026", .9), w=4, seed=sd))
    if inner_glow > 0.01:
        g = rad_grad([(0, "#3a4a8c", .9 * inner_glow), (1, "#3a4a8c", 0)], cx, y1 - 160, 170, 260)
        s.append(f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(DW)}" height="{f(DH)}" fill="url(#{g})"/>')
    return "".join(s)


def door_frame(cx, col, ic, sd, lit=0.0):
    x0, x1 = cx - DW / 2, cx + DW / 2
    y0, y1 = FLOOR - DH, FLOOR
    c, csh = col
    s = []
    # язычок вкладки: трапеция со скруглёнными верхними углами, стоит на раме
    tw = DW + 40
    ty = y0 - 26
    tab = [(cx - tw / 2 - 26, ty, 1), (cx - tw / 2 + 14, ty - 112), (cx - tw / 2 + 40, ty - 128, 1), (cx + tw / 2 - 40, ty - 128, 1),
           (cx + tw / 2 - 14, ty - 112), (cx + tw / 2 + 26, ty, 1)]
    cc = mix(c, "#fff6c8", lit)
    s.append(shape(tab, cc, blob([(cx - tw / 2, ty - 30), (cx + tw / 2 + 30, ty - 30), (cx + tw / 2 + 30, ty), (cx - tw / 2, ty)], csh, .9) +
                   line([(cx - tw / 2 + 30, ty - 108), (cx - 40, ty - 116)], 4, "#ffffff", seed=sd + 1, op=.7), w=5, seed=sd + 2))
    s.append(f'<g transform="translate({f(cx)} {f(ty - 64)}) scale(.95)">{icons.ICONS[ic](sd + 10)}</g>')
    # рама
    fr = [(x0 - 26, y1, 1), (x0 - 26, y0 - 26, 1), (x1 + 26, y0 - 26, 1), (x1 + 26, y1, 1), (x1, y1, 1), (x1, y0, 1), (x0, y0, 1), (x0, y1, 1)]
    s.append(shape(fr, "#e9e2d2", blob(rect_pts(x1, y0 - 26, x1 + 26, y1), "#c9bfa9") + blob(rect_pts(x0 - 26, y0 - 26, x1 + 26, y0 - 14), "#c9bfa9"),
                   w=4.6, seed=sd + 3))
    return "".join(s)


def door_leaf(cx, theta, col, sd):
    """Створка на петлях у правого косяка (открывается внутрь). theta 0 — закрыта, 1 — открыта (≈80°)."""
    x0, x1 = cx - DW / 2, cx + DW / 2
    y0, y1 = FLOOR - DH, FLOOR
    th = clamp(theta, -0.05, 1.0)
    a = math.radians(80 * th)
    wv = DW * math.cos(a)
    if wv < 6:
        return ""
    shrink = 0.07 * math.sin(max(a, 0)) * DH
    xl = x1 - wv
    pts = [(xl, y0 + shrink * .4, 1), (x1, y0, 1), (x1, y1, 1), (xl, y1 - shrink * .6, 1)]
    base = mix("#8a5a3a", "#5e3c26", 0.7 * math.sin(max(a, 0)))
    inner = ""
    for k, (a0, b0) in enumerate([(0.08, 0.44), (0.54, 0.92)]):
        ya, yb = y0 + DH * a0, y0 + DH * b0
        m = wv * .16
        inner += shape([(xl + m, ya + shrink * .3, 1), (x1 - m, ya, 1), (x1 - m, yb, 1), (xl + m, yb - shrink * .3, 1)], lib.mul(base, (.86, .84, .84)),
                       "", w=3, seed=sd + 1 + k)
    inner += blob([(x1 - wv * .25, y0), (x1, y0), (x1, y1), (x1 - wv * .25, y1)], lib.mul(base, (.8, .78, .8)), .8)
    # цветная полоса язычка на створке сверху (дверь «своего» цвета)
    inner += blob([(xl, y0 + shrink * .4), (x1, y0), (x1, y0 + 26), (xl, y0 + 26 + shrink * .2)], col[0], .95)
    s = shape(pts, base, inner, w=4.6, seed=sd + 5)
    # ручка
    hx = xl + wv * .12
    s += shape(ellipse_pts(hx, (y0 + y1) / 2 + 30, 13 * max(.4, wv / DW), 13, 12), "#f0c85a", "", w=3, seed=sd + 6)
    return s


def room_bg():
    s = [sb.background()]
    # плинтус уже в фоне; добавим вторую полосу-обои (вертикальные штрихи редко)
    for k in range(-6, 22):
        x = k * 120
        s.append(line([(x, 80), (x + 4, FLOOR - 40)], 2.2, "#2a3766", taper=.2, wmin=.6, seed=40 + k, op=.7))
    return "".join(s)


# ───────────────────────── персонаж: мозг на ножках
def foot(ax, ay, dirx, sd, lift=0.0):
    """Ступня-валик вперёд (dirx −1 — влево), пятка у лодыжки."""
    pts = []
    L, Hh = 84.0, 36.0
    for k in range(14):
        a = 2 * math.pi * k / 14
        x = (L / 2) * math.cos(a)
        y = (Hh / 2) * math.sin(a)
        if y > 0:
            y *= 0.75
        pts.append((ax + dirx * (L / 2 - 14) + x, ay - Hh / 2 + 2 + y))
    rot = -dirx * 18 * lift
    inner = blob([(ax - L, ay - 4), (ax + L, ay - 4), (ax + L, ay + 10), (ax - L, ay + 10)], SKIN_SH, .9)
    g = shape(pts, SKIN, inner, w=3.6, seed=sd)
    return f'<g transform="rotate({f(rot)} {f(ax)} {f(ay)})">{g}</g>'


def char(p):
    """Персонаж в локальных координатах (пол — y=0, смотрит влево, −x — вперёд).
    p: lean, squash, legs: [(foot_x, foot_y, lift) ×2], wl, wr, al, ar, cl, cr, extra_back, extra_hand."""
    pose = sb.Pose(p.get("bx", 0.0), BODY_Y + p.get("by", 0.0), 1.0, p.get("lean", 0.0), p.get("sq", 1.0))
    hips = [pose.pt(BCX - 70, BCY + 112), pose.pt(BCX + 40, BCY + 118)]
    s = []
    # дальняя нога (правая, x+) рисуется первой
    for k in (1, 0):
        fx_, fy_, lift = p["legs"][k]
        hp = hips[k]
        bend = 26 if k == 0 else 22
        s.append(sb.arm(hp, (fx_, fy_ - 14), bend, 900 + k * 5, 1.4))
        s.append(foot(fx_, fy_, -1, 920 + k, lift))
    SL, SR = pose.pt(*sb.SH_L), pose.pt(*sb.SH_R)
    s.append(sb.arm(SL, p["wl"], p.get("bl", -40), 931, 1.0))
    s.append(sb.arm(SR, p["wr"], p.get("br", 40), 932, 1.0))
    s.append(f'<g transform="{pose.tf()}">{_ST["brain"]}</g>')
    s.append(p.get("extra_back", ""))
    s.append(sb.toon_hand(p["wl"][0], p["wl"][1], p["al"], p.get("cl", 0.2), 960, 1.3))
    s.append(sb.toon_hand(p["wr"][0], p["wr"][1], p["ar"], p.get("cr", 0.2), 990, 1.3, spread=p.get("spread", 1.0)))
    s.append(p.get("extra_hand", ""))
    return "".join(s), pose


def place(svg_local, x, y, face_right):
    fx = -CS if face_right else CS
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(fx)} {f(CS)})">{svg_local}</g>'


def to_world(pt, x, y, face_right):
    fx = -CS if face_right else CS
    return x + pt[0] * fx, y + pt[1] * CS


def stand_legs(t, sway=0.0):
    return [(-60 + sway, 0.0, 0.0), (55 + sway, 0.0, 0.0)]


def run_legs(ph, amp=1.0):
    out = []
    for k, off in enumerate((0.0, math.pi)):
        a = ph + off
        fx_ = (-5 if k == 0 else 0) - 95 * math.cos(a) * amp
        fy_ = -max(0.0, math.sin(a)) * 80 * amp
        out.append((fx_, fy_, max(0.0, math.sin(a)) * amp))
    return out


def puff(x, y, e, sd, r0=26):
    """Облачко пыли: клубы одним силуэтом (внутренние контуры закрыты заливкой), растёт и тает сжатием."""
    if e < 0 or e > 0.6:
        return ""
    u = e / 0.6
    rs = np.random.RandomState(sd)
    k_ = (0.55 + 0.7 * ease_out(u)) * math.sin(math.pi * clamp(u)) ** 0.6
    if r0 * k_ < 4:
        return ""
    cl = []
    for k in range(5):
        dx = (k - 2) * r0 * 0.55 * (0.7 + 0.6 * ease_out(u)) + rs.uniform(-5, 5)
        r = r0 * rs.uniform(0.6, 0.95) * k_ * (1.15 if k == 2 else 1)
        dy = -abs(k - 2) * -r0 * 0.12 - r0 * 0.25 * (2 - abs(k - 2)) * k_
        cl.append((x + dx, y - 6 + dy - 16 * ease_out(u), r))
    s = []
    for px, py, r in cl:
        s.append(shape(ellipse_pts(px, py, r, r * .85, 12), "#6f7fb8", "", w=2.6, seed=sd + 3, var=.15))
    for px, py, r in cl:
        s.append(blob(ellipse_pts(px, py, r - 3, r * .85 - 3, 12), "#6f7fb8"))
    for px, py, r in cl:
        s.append(blob(ellipse_pts(px - r * .1, py - r * .3, r * .7, r * .45, 12), "#8e9dd2"))
    return "".join(s)


# ═══════════════════════════════ s07 ═══════════════════════════════
HOP0, HOP1 = 12.40, 12.70    # «каждый» — прыжок к двери отчёта
OPEN2 = 12.72                # «раз»
SLAM = 13.28                 # «переключаешься»
RUN0, RUN1 = 13.36, 14.02


def s07_state(t):
    """x мира, высота прыжка, ноги, смотрит вправо?, фаза бега."""
    x1, x2, x3 = DOORS[0][0] + 170, DOORS[1][0] - 230, DOORS[2][0] - 230
    if t < HOP0 - 0.08:
        # выглядывает из двери почты: стоит справа от проёма, качается
        return dict(x=x1 + 6 * math.sin(t * 5), hop=0.0, legs=stand_legs(t), right=False, mode="peek")
    if t < HOP0:
        u = (t - (HOP0 - 0.08)) / 0.08            # присел перед прыжком
        return dict(x=x1, hop=0.0, crouch=ease_io(u), legs=stand_legs(t), right=True, mode="crouch")
    if t < HOP1:
        u = (t - HOP0) / (HOP1 - HOP0)
        x = x1 + (x2 - x1) * ease_io(u)
        h = 190 * 4 * u * (1 - u)
        lg = [(-40, -40 * math.sin(math.pi * u), 1.0), (70, -60 * math.sin(math.pi * u), 1.0)]
        return dict(x=x, hop=h, legs=lg, right=True, mode="hop", u=u)
    if t < RUN0:
        e = t - HOP1
        land = math.exp(-e * 9) * math.cos(e * 20) if e < 0.4 else 0.0
        return dict(x=x2, hop=0.0, land=land, legs=stand_legs(t), right=True, mode="door2")
    if t < RUN1:
        u = (t - RUN0) / (RUN1 - RUN0)
        x = x2 + (x3 - x2) * (u * u * (3 - 2 * u) * 0.35 + u * 0.65)
        ph = (t - RUN0) * 26
        return dict(x=x, hop=abs(math.sin(ph)) * 22, legs=run_legs(ph), right=True, mode="run", ph=ph)
    e = t - RUN1
    return dict(x=x3 + 18 * (1 - math.exp(-e * 10)), hop=0.0, land=math.exp(-e * 8) * math.cos(e * 18) * .6, legs=stand_legs(t), right=True,
                mode="door3")


def leaf_angles07(t):
    d1 = 0.85 * (1 - smooth(HOP0 + 0.05, HOP0 + 0.35, t))
    d2 = 0.0
    if t > OPEN2 - 0.04:
        d2 = 0.9 * back_out(clamp((t - OPEN2 + 0.04) / 0.2), 1.4)
    if t > SLAM - 0.02:
        e = t - SLAM + 0.02
        d2 = 0.9 * (1 - ease_in(clamp(e / 0.09), 2))
        if e > 0.09:
            d2 = -0.04 * math.exp(-(e - .09) * 12) * math.sin((e - .09) * 50)
    d3 = 0.0
    if t > 14.05:
        d3 = 0.55 * back_out(clamp((t - 14.05) / 0.25), 1.6)
    return d1, d2, d3


def arms07(st, t):
    """Руки в локальных координатах персонажа (смотрит влево: −x — вперёд)."""
    m = st["mode"]
    by = BODY_Y
    if m == "peek":
        # держится за косяк и заглядывает: левая рука вперёд на косяк, правая машет
        return dict(wl=(-250, by + 40), al=200, cl=0.6, wr=(150, by + 120 + 10 * math.sin(t * 9)), ar=60, cr=0.2)
    if m == "crouch":
        return dict(wl=(-170, by + 150), al=150, cl=0.3, wr=(170, by + 150), ar=30, cr=0.3)
    if m == "hop":
        u = st["u"]
        return dict(wl=(-200, by - 40 - 60 * math.sin(math.pi * u)), al=230, cl=0.1, wr=(200, by - 30 - 60 * math.sin(math.pi * u)), ar=-50, cr=0.1)
    if m == "door2":
        e = t - OPEN2
        # тянет ручку на себя, потом держит
        reach = smooth(-0.1, 0.05, e)
        hx = -230 + 40 * smooth(0.0, 0.2, e)
        if t > SLAM - 0.08:
            k = smooth(SLAM - 0.08, SLAM, t)
            return dict(wl=(-250 - 40 * k, by + 60), al=180, cl=0.1, wr=(130, by + 140), ar=50, cr=0.2, spread=1.4)
        return dict(wl=(hx, by + 70 + 20 * (1 - reach)), al=185, cl=0.7 * reach, wr=(150, by + 130), ar=50, cr=0.2)
    if m == "run":
        ph = st["ph"]
        sw = math.sin(ph)
        return dict(wl=(-200 - 60 * sw, by + 150 - 30 * abs(sw)), al=150 + 20 * sw, cl=0.5, wr=(190 + 60 * sw, by + 160 - 30 * abs(sw)),
                    ar=30 - 20 * sw, cr=0.5, bl=-60, br=60)
    e = t - RUN1
    reach = smooth(0.0, 0.2, e)
    return dict(wl=(-180 - 70 * reach, by + 70), al=185, cl=0.7 * smooth(0.15, 0.3, e), wr=(150, by + 130), ar=50, cr=0.2)


def slam_fx(t, cx):
    e = t - (SLAM + 0.07)
    if e < 0 or e > 0.4:
        return ""
    s = []
    u = e / 0.4
    x1 = cx + DW / 2
    for k in range(5):
        y = FLOOR - DH + 80 + k * 110
        L = 70 * (1 - u)
        s.append(line([(x1 + 30 + 40 * ease_out(u), y), (x1 + 30 + 40 * ease_out(u) + L, y - 10)], 9, "#ffe27a", taper=.5, seed=1700 + k))
        s.append(line([(cx - DW / 2 - 30 - 40 * ease_out(u), y), (cx - DW / 2 - 30 - 40 * ease_out(u) - L, y - 10)], 9, "#ffe27a", taper=.5,
                      seed=1710 + k))
    # пыль из-под двери
    for k in range(2):
        s.append(puff(cx - 150 + k * 300, FLOOR + 6, e, 1720 + k, 34))
    return "".join(s)


def run_dust(t):
    s = []
    if t < RUN0:
        return ""
    # шаг каждые pi/26 с; на каждом касании — облачко за пяткой
    for n in range(0, 40, 2):
        tn = RUN0 + n * math.pi / 26
        if tn > min(t, RUN1 + 0.02):
            break
        st = s07_state(tn + 1e-4)
        e = t - tn
        x = st["x"] - 40 + (n % 2) * 30
        s.append(puff(x - 30 - 60 * ease_out(min(e / .5, 1)), FLOOR + 2, e, 1800 + n, 30))
    # прыжок: облачко на отрыве и приземлении
    s.append(puff(DOORS[0][0] + 170, FLOOR + 2, t - HOP0, 1850, 26))
    s.append(puff(DOORS[1][0] - 230, FLOOR + 2, t - HOP1, 1851, 30))
    return "".join(s)


def s07(t):
    st = s07_state(t)
    d = leaf_angles07(t)
    s = []
    s.append(_ST["room"])
    glow = [0.6, 0.6 * smooth(OPEN2, OPEN2 + .2, t) * (1 - smooth(SLAM, SLAM + .08, t)), 0.5 * smooth(14.05, 14.3, t)]
    for i, (cx, col, ic) in enumerate(DOORS):
        s.append(door_back(cx, glow[i], 1100 + i * 40))
        s.append(door_leaf(cx, d[i], col, 1120 + i * 40))
        s.append(door_frame(cx, col, ic, 1140 + i * 40, lit=glow[i] * .4))
    s.append(slam_fx(t, DOORS[1][0]))
    s.append(run_dust(t))
    # персонаж
    a = arms07(st, t)
    crouch = st.get("crouch", 0.0)
    land = st.get("land", 0.0)
    p = dict(a)
    p["legs"] = st["legs"]
    p["by"] = 40 * crouch + 30 * max(land, 0)
    p["sq"] = 1 - 0.12 * crouch - 0.08 * land + (0.06 if st["mode"] == "hop" else 0)
    p["lean"] = {"run": -12, "hop": -8}.get(st["mode"], 0) + 2 * math.sin(t * 3)
    if st["mode"] == "door2" and t > SLAM - 0.1:
        p["lean"] = -6
    body, _ = char(p)
    x, y = st["x"], FLOOR - st["hop"]
    s.insert(len(s), sb.shadow(x, FLOOR + 6, 120 * (1 - 0.3 * clamp(st["hop"] / 190)), .5))
    s.append(place(body, x, y, st["right"]))
    # камера едет за мозгом с отставанием
    cx = cam_x07(t)
    e = t - SLAM - 0.07
    shake = 8 * math.exp(-max(e, 0) * 8) * math.sin(e * 55) * (e > 0)
    cm = cam(cx + shake, 925, 1.2 + 0.02 * math.sin(t * 1.3), 0.8 * math.sin(t * 1.1) + 0.6 * shake / 8)
    return "".join(s), cm


def cam_x07(t):
    # сглаженное следование: средневзвешенное по прошлому
    acc, wsum = 0.0, 0.0
    for k in range(10):
        tt = t - k * 0.035
        w = math.exp(-k * 0.35)
        acc += (s07_state(tt)["x"] + 120) * w
        wsum += w
    return min(max(acc / wsum, 470), 1300)


# ═══════════════════════════════ s08 ═══════════════════════════════
TIME_T = 14.88       # «время»
REMEMBER = 15.52     # «вспомнить»
WHERE0, WHERE1 = 16.08, 16.96
FOUND = 16.10
D8 = (700.0, ("#8fd3ff", "#4f9fd8"), "report")
FLAG = (720.0, FLOOR - DH + 150)          # закладка на двери (на створке, у верхней филёнки)
CH8X = 330.0                              # где стоит мозг


def beam_target(t):
    """Куда светит фонарик: блуждает по стене и двери, на «где» находит закладку."""
    if t >= FOUND:
        k = ease_out(clamp((t - FOUND + 0.3) / 0.3))
        wx = 760 + 150 * math.sin(1.9 * (FOUND - 0.3) + 0.4)
        wy = 900 + 150 * math.sin(1.3 * (FOUND - 0.3))
        return (wx + (FLAG[0] - wx) * k + 4 * math.sin(t * 7) * k, wy + (FLAG[1] - wy) * k)
    tt = min(t, FOUND - 0.3)
    wx = 760 + 150 * math.sin(1.9 * tt + 0.4)
    wy = 900 + 150 * math.sin(1.3 * tt)
    if t > FOUND - 0.3:
        k = ease_io((t - (FOUND - 0.3)) / 0.3)
        return (wx + (FLAG[0] - wx) * k, wy + (FLAG[1] - wy) * k)
    return (wx, wy)


def flashlight(L=200.0):
    """Фонарик в локальных координатах кисти: от (0,0) вдоль +x."""
    s = shape([(-6, -15, 1), (L - 30, -15, 1), (L, -26, 1), (L, 26, 1), (L - 30, 15, 1), (-6, 15, 1)], "#3f4a6e",
              blob([(-6, 4), (L, 4), (L, 26), (-6, 15)], "#2b3352", .9) + line([(4, -8), (L - 36, -8)], 3.4, "#7f8cb8", seed=1901), w=4, seed=1900)
    s += shape([(L, -26, 1), (L + 10, -28, 1), (L + 10, 28, 1), (L, 26, 1)], "#fff6c8", "", w=3.4, seed=1902)
    s += shape(rect_pts(L - 70, -21, L - 52, -14, 3), "#e2543f", "", w=2.2, seed=1903)
    return s


def hourglass(x, y, sc, t, rot):
    """Песочные часы: две колбы, рамки; песок сверху убывает, струйка, горка снизу растёт."""
    e = t - TIME_T
    fill = clamp(e / 2.2)
    s = []
    s.append(shape(rect_pts(-62, -112, 62, -92, 8), "#9a5f34", blob(rect_pts(-62, -100, 62, -92, 8), "#6e4123", .9), w=4, seed=2000))
    s.append(shape(rect_pts(-62, 92, 62, 112, 8), "#9a5f34", blob(rect_pts(-62, 104, 62, 112, 8), "#6e4123", .9), w=4, seed=2001))
    glass = [(-50, -92), (50, -92), (46, -60), (12, -8), (12, 8), (46, 60), (50, 92), (-50, 92), (-46, 60), (-12, 8), (-12, -8), (-46, -60)]
    top_h = 70 * (1 - fill)
    sand = "#f2c25a"
    inner = ""
    if top_h > 2:
        yt = -8 - top_h
        wt = 12 + (46 - 12) * (top_h / 84)
        inner += blob([(-wt, yt), (wt, yt), (12, -8), (-12, -8)], sand)
    bh = 18 + 54 * fill
    inner += blob([(-50, 92), (50, 92), (46, 92 - bh * .6), (0, 92 - bh), (-46, 92 - bh * .6)], sand)
    inner += blob([(10, 92), (50, 92), (46, 92 - bh * .6), (20, 92 - bh * .7)], "#d9a440", .9)
    if 0 < fill < 1:
        inner += line([(0, -6), (1, 40), (0, 92 - bh + 4)], 5, sand, taper=.1, wmin=.8, seed=2002)
        for k in range(3):
            yy = ((t * 260 + k * 33) % 90) - 6
            inner += f'<circle cx="{f(1.5 * math.sin(k + t * 9))}" cy="{f(yy)}" r="3" fill="{sand}"/>'
    s.append(shape(glass, "#dff2ff", inner + blob([(-44, -86), (-30, -86), (-40, -60), (-46, -60)], "#ffffff", .9), w=4.2, seed=2003))
    for k, xx in enumerate((-56, 56)):
        s.append(shape(rect_pts(xx - 6, -92, xx + 6, 92, 3), "#b07a48", "", w=3, seed=2004 + k))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">{"".join(s)}</g>'


def bookmark(x, y, found_e, sd):
    """Закладка-флажок: красная лента с вырезом, торчит из-под верхнего края створки; найдено — вспыхивает и машет."""
    wave = 0.0
    if found_e > 0:
        wave = 8 * math.exp(-found_e * 3) * math.sin(found_e * 16)
    pts = [(-26, -10, 1), (26, -10, 1), (24 + wave * .3, 70, 1), (0 + wave * .6, 52, 1), (-24 + wave * .3, 70, 1)]
    col = "#e2543f"
    inner = blob([(8, -10), (26, -10), (24 + wave * .3, 70), (10, 60)], "#b93a2a", .9) + line([(-14, -2), (-12, 40)], 4, "#ff9c8a", seed=sd + 2)
    s = shape(pts, col, inner, w=4, seed=sd)
    s += shape(rect_pts(-34, -22, 34, -6, 4), "#c94a36", "", w=3.4, seed=sd + 1)
    sc = 1 + 0.25 * math.exp(-max(found_e, 0) * 5) * (found_e > 0)
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)})">{s}</g>'


def qmark(x, y, sc, sd):
    pts_txt = (f'<text x="0" y="0" text-anchor="middle" font-family="IDB" font-weight="900" font-size="120" fill="#ffe27a" '
               f'stroke="{INK}" stroke-width="9" stroke-linejoin="round" paint-order="stroke">?</text>')
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)})">{pts_txt}</g>'


def emark(x, y, sc):
    t_ = (f'<text x="0" y="0" text-anchor="middle" font-family="IDB" font-weight="900" font-size="130" fill="#ffe27a" '
          f'stroke="{INK}" stroke-width="9" stroke-linejoin="round" paint-order="stroke">!</text>')
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)})">{t_}</g>'


def s08(t):
    s = [_ST["room"]]
    cx = D8[0]
    s.append(door_back(cx, 0.0, 2100))
    s.append(door_leaf(cx, 0.0, D8[1], 2120))
    s.append(door_frame(cx, D8[1], D8[2], 2140))
    fe = t - FOUND
    # затемнение комнаты, кроме пятна луча (луч и пятно — свет поверх)
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{H + 1800}" fill="#05081a" opacity=".55"/>')
    # персонаж
    jump = 0.0
    ej = t - 16.52
    if ej > 0:
        jump = 120 * max(0.0, math.sin(clamp(ej / 0.36) * math.pi)) if ej < 0.36 else 0.0
    land = 0.0
    if ej > 0.36:
        land = math.exp(-(ej - .36) * 9) * math.cos((ej - .36) * 20)
    x, y = CH8X, FLOOR - jump
    bt = beam_target(t)
    # правая (дальняя от зрителя) рука держит фонарик: мир → локальные (персонаж смотрит вправо, зеркально)
    by = BODY_Y
    # плечо правой руки в мире (приблизительно) — для направления луча
    sw = (x - (BCX + 128 - BCX) * CS * -1, y + (by + 96) * CS)
    # кисть: на 70% пути к цели по направлению, на длине руки
    dx, dy = bt[0] - sw[0], bt[1] - sw[1]
    Ld = math.hypot(dx, dy) + 1e-6
    reach = 150 * CS
    hw = (sw[0] + dx / Ld * reach, sw[1] + dy / Ld * reach)
    ang_w = math.degrees(math.atan2(dy, dx))
    # в локальных координатах (зеркало по x): x_loc = -(xw - x)/CS, y_loc = (yw - y)/CS; угол: 180 - ang
    wr_loc = (-(hw[0] - x) / CS, (hw[1] - y) / CS)
    ar_loc = 180 - ang_w
    # левая рука: на «вспомнить» чешет макушку, иначе у бока; на «был» вскидывается
    er = t - REMEMBER
    scratch = smooth(-0.15, 0.05, er) * (1 - smooth(0.4, 0.55, er))
    top = (BCX - 10 - BCX, BCY - 150 - BCY + BODY_Y)
    rest = (-170, by + 150)
    wl = (rest[0] + (top[0] + 30 - rest[0]) * scratch + 22 * math.sin(er * 40) * scratch, rest[1] + (top[1] - 95 - rest[1]) * scratch)
    al = 150 + (100 - 150) * scratch
    if ej > 0:
        k = smooth(0, 0.12, ej)
        wl = (wl[0] + (-200 - wl[0]) * k, wl[1] + (by - 120 - wl[1]) * k)
        al = al + (230 - al) * k
    fl = f'<g transform="translate({f(wr_loc[0])} {f(wr_loc[1])}) rotate({f(ar_loc)})">{flashlight()}</g>'
    p = dict(wl=wl, al=al, cl=0.5 if scratch > .5 else 0.2, wr=wr_loc, ar=ar_loc, cr=0.85, extra_back=fl,
             legs=stand_legs(t, 0) if ej < 0 or ej > 0.36 else [(-40, -30, 1.0), (60, -40, 1.0)])
    p["lean"] = 4 * math.sin(t * 1.6) - 6 * scratch
    p["by"] = 30 * max(land, 0)
    p["sq"] = 1 - 0.06 * land + 0.05 * (jump > 0)
    body, pose = char(p)
    # луч: от конца фонарика к цели — светлый конус с градиентом
    lens = (hw[0] + math.cos(math.radians(ang_w)) * 210 * CS, hw[1] + math.sin(math.radians(ang_w)) * 210 * CS)
    ex, ey = bt
    vx, vy = ex - lens[0], ey - lens[1]
    Lb = math.hypot(vx, vy) + 1e-6
    nx, ny = -vy / Lb, vx / Lb
    spot_r = 120
    cone = [(lens[0] + nx * 16, lens[1] + ny * 16), (ex + nx * spot_r, ey + ny * spot_r), (ex - nx * spot_r, ey - ny * spot_r),
            (lens[0] - nx * 16, lens[1] - ny * 16)]
    g = lib.lin_grad([(0, "#fff6c8", .55), (1, "#fff6c8", .18)], lens[0], lens[1], ex, ey, units="userSpaceOnUse")
    s.append(f'<path d="{lib.fill_d([c + (1,) for c in cone])}" fill="url(#{g})"/>')
    g2 = rad_grad([(0, "#fff6c8", .75), (.6, "#fff1b0", .35), (1, "#fff1b0", 0)], ex, ey, spot_r * 1.15, spot_r * 1.15)
    s.append(f'<circle cx="{f(ex)}" cy="{f(ey)}" r="{f(spot_r * 1.15)}" fill="url(#{g2})"/>')
    # найденная закладка поверх тьмы — яркая
    k = 0.0
    if fe > -0.05:
        k = smooth(-0.05, 0.1, fe)
        g3 = rad_grad([(0, "#ffe27a", .8 * k), (1, "#ffe27a", 0)], FLAG[0], FLAG[1] + 20, 150, 150)
        s.append(f'<circle cx="{f(FLAG[0])}" cy="{f(FLAG[1] + 20)}" r="150" fill="url(#{g3})"/>')
        if k > 0.5:
            s.append(bookmark(FLAG[0], FLAG[1], fe, 2160))
    if k <= 0.5:
        # до находки закладка видна только внутри пятна фонарика
        cid = lib.uid("cl")
        lib.DEFS.append(f'<clipPath id="{cid}"><circle cx="{f(ex)}" cy="{f(ey)}" r="{f(spot_r * 0.95)}"/></clipPath>')
        s.append(f'<g clip-path="url(#{cid})">{bookmark(FLAG[0], FLAG[1], fe, 2160)}</g>')
    if 0 < fe < 0.45:
        for j in range(10):
            a = j * math.pi / 5 + .3
            u = clamp(fe / 0.45)
            r0 = 70 + 90 * ease_out(u)
            L = 36 * (1 - u)
            s.append(line([(FLAG[0] + math.cos(a) * r0, FLAG[1] + 20 + math.sin(a) * r0),
                           (FLAG[0] + math.cos(a) * (r0 + L), FLAG[1] + 20 + math.sin(a) * (r0 + L))], 8, "#ffe27a", taper=.5, seed=2180 + j))
    s.append(sb.shadow(x, FLOOR + 6, 120 * (1 - 0.3 * jump / 120), .5))
    s.append(place(body, x, y, True))
    # песочные часы над головой
    head = to_world((BCX - BCX, BCY - BCY + BODY_Y - 150), x, y, True)
    eh = t - TIME_T
    if eh > -0.05:
        k = back_out(clamp((eh + 0.05) / 0.25), 2.2) * (1 - smooth(WHERE0 - 0.1, WHERE0 + 0.1, t))
        if k > 0.02:
            flip = 180 * ease_io(clamp((eh) / 0.25)) if eh > 0 else 0
            s.append(hourglass(head[0] - 10, head[1] - 175 + 6 * math.sin(t * 4), 0.95 * k, t, -180 + flip + 5 * math.sin(t * 3)))
    # вопрос на «вспомнить», восклицание на «где ты был»
    if er > -0.05 and t < WHERE0 + 0.05:
        k = back_out(clamp((er + 0.05) / 0.22), 2.4) * (1 - smooth(WHERE0 - 0.05, WHERE0 + 0.05, t))
        if k > 0.02:
            s.append(qmark(head[0] + 140, head[1] - 90 + 6 * math.sin(t * 5), k, 2190))
    if fe > 0:
        k = back_out(clamp(fe / 0.2), 2.6)
        s.append(emark(head[0] + 40, head[1] - 60 - jump, k))
    # камера: лёгкий наезд, к закладке под конец
    u = clamp((t - 14.0) / 3.2)
    kf = smooth(FOUND, FOUND + 0.6, t)
    cm = cam(560 + 30 * kf, 950 - 20 * kf, 1.3 + 0.07 * ease_io(u) + 0.03 * math.exp(-max(fe, 0) * 5) * (fe > 0), -0.6 + 1.0 * u)
    return "".join(s), cm


def build_static():
    if _ST:
        return
    _ST["room"] = room_bg()
    _ST["brain"] = brain_art.brain(0, 0, stem=False)
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s07": s07, "s08": s08}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{cm}">{art}{sb.dust(t)}</g>')
