"""Сцена «мозг» рилса 35 (s01 s02 s07 s08 s10 s15): мозг-персонаж рилса 32 (ножки в кедах, ручки, большие глаза) в ночной
комнате, доли мозга горят отдельно (brain_art). Всё — функция общего времени ролика t, удары — по voice/words.json.
s01 «Говорят…» (0–1.5): влёт камеры, мозг серый и сонный, горит один уголок лба, плашка «10 %».
s02 «…десять процентов мозга» (1.5–3.75): батарейка заполняется на одно деление на «десять», «10 %» щёлкает;
    на «мозга» мозг виновато пожимает ручками, тусклые доли мигают и гаснут.
s07 «На самом деле работает почти весь мозг» (10.3–12.85): на «деле» открывает глаза, доли загораются по очереди.
s08 «просто разные части в разное время» (12.85–15.25): доли вспыхивают по очереди со значками глаз / ухо / рука / нота.
s10 «и занят своими делами» (16.95–18.7): мозг в ночном колпаке ставит коробки-воспоминания на полки.
s15 «…работает лучше» (25.95–27.3): мозг горит тёплым светом, на «лучше» — большой палец и подмигивание."""
import math

import numpy as np

import body as B
import brain_art as BA
import lib
from body import (EYE_L, EYE_R, FLOOR, HIP_L, HIP_R, SH_L, SH_R, Pose, arm, face, leg, rays, shadow, star, text, thumbs_up, toon_hand)
from brain_art import BCX, BCY
from lib import (INK, W, H, back_out, blob, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rect_pts, shape,
                 smooth, svg)

_ST = {}
WT = {}


def word_t(w, k=0):
    """Время начала слова (k-е вхождение) из озвучки."""
    if not WT:
        for x in lib.words():
            WT.setdefault(x["word"].strip(",.?!").lower(), []).append(x["start"])
    return WT[w][k]


# ───────────────────────── персонаж целиком
def char(pose, levels, fc, wl, wr, al, ar, cl=0.3, cr=0.3, bl=-40, br=40, legs="", live=0.0, halo=0.0, lit=None, pink=False, warm=0.0,
         behind="", front="", hands_l=None, hands_r=None, hat=""):
    """Ножки → ручки → (свечение, мозг, лицо, шапка) → кисти. hands_l/r — готовый SVG кисти вместо toon_hand."""
    B.set_skin(live)
    sc = pose.sc
    SL, SR = pose.pt(*SH_L), pose.pt(*SH_R)
    s = []
    if halo:
        s.append(f'<g transform="{pose.tf()}">{BA.halo(levels, lit, warm, halo)}</g>')
    s += [behind, legs, arm(SL, wl, bl, 1301, sc), arm(SR, wr, br, 1302, sc)]
    inner = ""
    inner += BA.brain(levels, lit, pink, warm) + fc + hat
    s.append(f'<g transform="{pose.tf()}">{inner}</g>')
    s.append(front)
    s.append(hands_l if hands_l is not None else toon_hand(wl[0], wl[1], al, cl, 1330, sc * 1.3))
    s.append(hands_r if hands_r is not None else toon_hand(wr[0], wr[1], ar, cr, 1360, sc * 1.3))
    return "".join(s)


def legs_for(pose, step=0.0, sd=1200, spread=0.0, lift_l=0.0, lift_r=0.0, live=None):
    if live is not None:
        B.set_skin(live)
    hl, hr = pose.pt(*HIP_L), pose.pt(*HIP_R)
    g = FLOOR - 26
    fl = (hl[0] - 18 - spread, g - lift_l)
    fr = (hr[0] + 14 + spread, g - lift_r)
    return leg(hr, fr, pose.sc, -1, sd) + leg(hl, fl, pose.sc, -1, sd + 20)


def y_for(sc):
    """Центр мозга так, чтобы ножки стояли на полу чуть согнутыми."""
    return FLOOR - 26 - 0.86 * 186 * sc - 106 * sc


def hang(pose, t, sw=0.0):
    """Ручки висят вдоль тела, чуть качаются."""
    sc = pose.sc
    SL, SR = pose.pt(*SH_L), pose.pt(*SH_R)
    a = 10 * math.sin(t * 2.1 + sw)
    wl = (SL[0] - 78 * sc + a * .4, SL[1] + 58 * sc)
    wr = (SR[0] + 78 * sc - a * .4, SR[1] + 58 * sc)
    return wl, wr, 118 + a * .3, 62 - a * .3


def lid_col(levels, live=0.0, lit=None, pink=False, warm=0.0):
    return BA.lobe_color("front", levels.get("front", 0.0), lit, pink, warm)


def lerp(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


# ───────────────────────── плашка и батарейка
def plate10(t, x, y, k, txt="10 %", pulse=0.0):
    """Тёмная плашка-индикатор с жёлтыми «10 %»."""
    if k <= 0.01:
        return ""
    w, h = 300, 150
    sc = k * (1 + pulse)
    inner = blob(rect_pts(-w / 2, h / 2 - 34, w / 2, h / 2, 0), "#141a36", .55)
    s = shape(rect_pts(-w / 2, -h / 2, w / 2, h / 2, 34), "#222a52", inner, w=6, seed=71)
    s += text(0, 44, txt, 120, "#ffe27a", sw=9)
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)}) rotate({f(-4 + 3 * math.sin(t * 2.3))})">{s}</g>'


def pointer(x0, y0, x1, y1, k, sd=0):
    """Пунктир от плашки к уголку мозга, рисуется от плашки."""
    if k <= 0.01:
        return ""
    n = 7
    s = []
    for i in range(n):
        u0, u1 = i / n, (i + 0.55) / n
        if u0 > k:
            break
        u1 = min(u1, k)
        s.append(line([(x0 + (x1 - x0) * u0, y0 + (y1 - y0) * u0), (x0 + (x1 - x0) * u1, y0 + (y1 - y0) * u1)], 7, "#ffe27a", taper=.2, wmin=.7,
                      seed=sd + i))
    if k >= 1:
        s.append(shape(ellipse_pts(x1, y1, 12, 12, 10), "#ffe27a", "", w=3.4, seed=sd + 20))
    return "".join(s)


def battery(x, y, level, t, sd=0, flash=0.0):
    """Вертикальная батарейка на 10 делений, низ-центр (x, y); level — делений (0..10, дробно)."""
    w, h = 190, 430
    s = []
    s.append(shadow(x, y + 10, 120, .5))
    s.append(shape(rect_pts(x - 40, y - h - 30, x + 40, y - h + 6, 10), "#9aa3b8", blob(rect_pts(x + 10, y - h - 30, x + 40, y - h + 6), "#6b7389", .7),
                   w=4.4, seed=sd + 1))
    inner = [f'<rect x="{x - w / 2 - 10}" y="{y - h - 10}" width="{w + 20}" height="{h + 20}" fill="#1a2040"/>']
    pad, gap = 16, 8
    cell = (h - 2 * pad - 9 * gap) / 10
    full = int(math.floor(level + 1e-6))
    part = level - full
    for i in range(10):
        y1 = y - pad - i * (cell + gap)
        y0 = y1 - cell
        if i < full or (i == full and part > 0.01):
            frac = 1.0 if i < full else part
            col = mix("#ffd23e", "#fff6b0", flash)
            yt = y1 - cell * frac
            inner.append(f'<rect x="{f(x - w / 2 + pad)}" y="{f(yt)}" width="{f(w - 2 * pad)}" height="{f(y1 - yt)}" rx="6" fill="{col}"/>')
            inner.append(f'<rect x="{f(x - w / 2 + pad + 8)}" y="{f(yt + 4)}" width="{f(w - 2 * pad - 60)}" height="6" rx="3" fill="#ffffff" opacity=".6"/>')
        else:
            inner.append(f'<rect x="{f(x - w / 2 + pad)}" y="{f(y0)}" width="{f(w - 2 * pad)}" height="{f(cell)}" rx="6" fill="#2c3460"/>')
    inner.append(blob(rect_pts(x + w / 2 - 34, y - h - 10, x + w / 2 + 10, y + 10), "#000000", .18))
    s.append(shape(rect_pts(x - w / 2, y - h, x + w / 2, y, 26), "#3a4478", "".join(inner), w=6, seed=sd + 2))
    if flash > 0.02:
        g = rad_grad([(0, "#ffe27a", .55 * flash), (1, "#ffe27a", 0)], x, y - 40, 220, 120)
        s.append(f'<ellipse cx="{x}" cy="{y - 40}" rx="220" ry="120" fill="url(#{g})"/>')
    return "".join(s)


# ───────────────────────── s01: хук
def s01(t):
    hit = word_t("говорят")          # 0.08
    sc = 1.25
    br = math.sin(t * 2.4)
    pose = Pose(540, y_for(sc) + 6 * br, sc * (1 + 0.012 * br), -2 + 2.5 * math.sin(t * 1.5), 1 + 0.015 * br)
    pulse = 0.5 + 0.5 * math.sin(t * 7.5)
    e = t - hit
    tip = 0.72 + 0.2 * pulse + 0.25 * math.exp(-max(e, 0) * 5) * (e > 0)
    lv = {"tip": min(1.0, tip)}
    wl, wr, al, ar = hang(pose, t)
    # сонное моргание
    op = 0.42
    bt = t - 0.95
    if 0 < bt < 0.3:
        op = 0.42 * (1 - math.sin(math.pi * bt / 0.3))
    fc = face(op, (0.4, 0.5), "flat", t, brow=0.0, lid_col=lid_col(lv), blush=0.0)
    art = [shadow(540, FLOOR + 6, 200 * sc / 1.25), char(pose, lv, fc, wl, wr, al, ar, 0.35, 0.35, -30, 30, legs_for(pose, live=0.0), 0.0, halo=1.0)]
    # уголок лба: вспышка-лучи на «Говорят»
    tx, ty = pose.pt(*BA.LOBE_CENTER["tip"])
    art.append(rays(tx, ty, e, 120, r=60, n=8, col="#ffe27a", dur=0.45))
    # плашка «10 %» падает сверху на «Говорят» и покачивается
    kk = back_out(clamp((t - hit) / 0.28), 2.2)
    px, py = 290, 430 - 160 * (1 - kk)
    art.append(pointer(px + 30, py + 80, tx - 6, ty - 18, smooth(hit + 0.15, hit + 0.45, t), 140))
    art.append(plate10(t, px, py, clamp(kk * 1.4), pulse=0.03 * pulse))
    # камера: влёт 1/1.4 → 1 за 0.22 с с поворотом, перелёт и отскок
    S = 1.08
    u = clamp(t / 0.22)
    k = ease_out(u, 3)
    over = 0.045 * math.exp(-max(t - 0.22, 0) * 9) * math.sin(min(max(t - 0.22, 0) * 14, math.pi)) if t > 0.22 else 0.0
    s = S * (1 / 1.4 + (1 - 1 / 1.4) * k) * (1 + over) * (1 + 0.025 * smooth(0.3, 1.7, t))
    rot = -6 * (1 - k) + 1.2 * over / 0.045 * 0.3
    return "".join(art), cam(540, 850 - 20 * (1 - k), s, rot)


# ───────────────────────── s02: батарейка и пожимание
def s02(t):
    ten = word_t("десять")           # 2.00
    brn = word_t("мозга")            # 2.96
    sc = 1.12
    br = math.sin(t * 2.4)
    e = t - brn
    shr = smooth(brn - 0.06, brn + 0.16, t) * (1 - 0.3 * smooth(brn + 0.6, brn + 0.85, t))
    sq = 1 + 0.015 * br - 0.05 * shr + B.ease_kick(t - ten, 0.03)
    pose = Pose(400, y_for(sc) - 4 * br - 26 * shr, sc, -2 + 2 * math.sin(t * 1.4) + 4 * shr, sq)
    # уровень: ползёт к одному делению, на «десять» щёлк
    if t < ten:
        lvl = 0.9 * ease_in(clamp((t - 1.3) / (ten - 1.3)), 1.6)
    else:
        el = t - ten
        lvl = 1.0 + 0.06 * math.exp(-el * 8) * math.sin(el * 30)
    lvl = max(0.0, lvl)
    flash = math.exp(-max(t - ten, 0) * 5) if t > ten else 0.0
    # доли: уголок горит; на «мозга» тусклые мигают и гаснут
    fl = 0.0
    if 0 < e < 0.55:
        fl = 0.32 * (0.5 + 0.5 * math.sin(e * 46)) * (1 - e / 0.55)
    lv = {"tip": 0.95 + 0.05 * math.sin(t * 7), "front": fl, "pariet": fl * .8, "temp": fl * .9, "occip": fl * .7, "cereb": fl * .6}
    # ручки: висят → на «мозга» ладони вверх в стороны (пожимает)
    wl0, wr0, al0, ar0 = hang(pose, t)
    SL, SR = pose.pt(*SH_L), pose.pt(*SH_R)
    upl = (SL[0] - 70 * sc, SL[1] - 95 * sc)
    upr = (SR[0] + 80 * sc, SR[1] - 100 * sc)
    wl, wr = lerp(wl0, upl, shr), lerp(wr0, upr, shr)
    al = al0 + (205 - al0) * shr
    ar = ar0 + (-25 - ar0) * shr
    # взгляд: на батарейку → в сторону, виновато
    look = lerp((0.9, -0.2), (-0.6, 0.5), smooth(brn - 0.1, brn + 0.15, t))
    mouth = "flat" if t < brn else "wobbly"
    fc = face(0.62 + 0.3 * smooth(ten - .05, ten + .1, t) - 0.25 * shr, look, mouth, t, brow=0.7 * shr + 0.4 * flash, brow_tilt=0.8 * shr,
              lid_col=lid_col(lv), blush=0.0)
    art = [shadow(pose.x, FLOOR + 6, 180), battery(840, 1010, lvl, t, 160, flash)]
    art.append(char(pose, lv, fc, wl, wr, al, ar, 0.1, 0.1, -30 + 70 * shr, 30 - 70 * shr, legs_for(pose, live=0.0), 0.0, halo=1.0))
    # «10 %» над батарейкой — щёлкает
    n = int(round(clamp(lvl, 0, 1) * 10)) if t < ten else 10
    pk = B.ease_kick(t - ten, 0.22, 14, 6)
    art.append(text(840, 470, f"{n} %", 140, "#ffe27a", sw=10, extra=f'transform="translate(840 420) scale({f(1 + pk)}) translate(-840 -420)"'))
    art.append(rays(840, 760, t - ten, 170, r=150, n=10, col="#ffe27a", dur=0.4, L0=50))
    # пожимание: дуги «эм…» над плечами
    if shr > 0.3 and e < 1.0:
        for side, (x, y) in ((-1, upl), (1, upr)):
            ph = clamp(e / 0.6)
            for k in range(2):
                r = 40 + 26 * k + 20 * ph
                a0 = -2.2 if side < 0 else -0.95
                pts = [(x + math.cos(a0 + i * .25) * r, y - 30 + math.sin(a0 + i * .25) * r) for i in range(5)]
                art.append(line(pts, 5, "#e9eeff", taper=.5, seed=180 + k + (side > 0) * 4, op=1 - ph * .7))
    # камера: наезд, толчок на «десять»
    u = clamp((t - 1.3) / 2.65)
    s = 1.0 + 0.08 * ease_io(u) + B.ease_kick(t - ten, 0.05, 16, 7) + B.ease_kick(e, 0.02)
    return "".join(art), cam(560 - 20 * u, 800 + 10 * u, s, -0.8 + 1.2 * u)


# ───────────────────────── s07: просыпается, доли загораются
def s07(t):
    dl = word_t("деле")              # 10.96
    seq = [("front", word_t("работает", 0)), ("pariet", word_t("почти")), ("temp", word_t("почти") + 0.18),
           ("occip", word_t("весь")), ("cereb", word_t("мозг"))]
    hit = word_t("мозг")             # 12.40
    sc = 1.25
    br = math.sin(t * 2.4)
    wake = smooth(dl - 0.04, dl + 0.06, t)
    jump = B.ease_kick(t - dl, 1.0, 12, 6)
    lv = {"tip": 0.95}
    for k, (lobe, tt) in enumerate(seq):
        lv[lobe] = smooth(tt - 0.03, tt + 0.12, t) * (0.92 if lobe != "cereb" else 0.85)
    total = sum(lv[k] for k, _ in seq) / 5
    pose = Pose(540, y_for(sc) + 5 * br * (1 - wake) - 30 * jump, sc, -3 * (1 - wake) + 2 * math.sin(t * 1.6) * wake,
                1 + 0.02 * br * (1 - wake) - 0.06 * jump)
    # ручки: висят, после «весь» поднимаются в изумлении
    wl0, wr0, al0, ar0 = hang(pose, t)
    amaze = smooth(seq[3][1], seq[3][1] + 0.25, t)
    SL, SR = pose.pt(*SH_L), pose.pt(*SH_R)
    upl = (SL[0] - 120 * sc, SL[1] - 120 * sc + 8 * math.sin(t * 9))
    upr = (SR[0] + 120 * sc, SR[1] - 130 * sc + 8 * math.sin(t * 9 + 1))
    wl, wr = lerp(wl0, upl, amaze), lerp(wr0, upr, amaze)
    al, ar = al0 + (230 - al0) * amaze, ar0 + (-50 - ar0) * amaze
    # лицо: спит → глаза распахиваются на «деле» → смотрит на загорающиеся доли
    if t < dl - 0.02:
        op = 0.0
    else:
        op = 0.55 + 0.45 * ease_out(clamp((t - dl + 0.02) / 0.1))
    look = (0.0, -0.9)
    for lobe, tt in seq:
        if t > tt:
            cx, cy = BA.LOBE_CENTER[lobe]
            look = (clamp((cx - (BCX - 70)) / 140, -1, 1), clamp((cy - BCY) / 120, -1, 0.6))
    mouth = "snore" if t < dl else ("o" if t > seq[3][1] else "smile")
    lc = lid_col(lv)
    fc = face(op, look, mouth, t, brow=0.6 * wake + 0.6 * amaze, lid_col=lc, blush=0.5 * total)
    art = [shadow(540, FLOOR + 6, 200), char(pose, lv, fc, wl, wr, al, ar, 0.0, 0.0, -40, 40, legs_for(pose, live=total), total, halo=1.2)]
    for k, (lobe, tt) in enumerate(seq):
        x, y = pose.pt(*BA.LOBE_CENTER[lobe])
        art.append(rays(x, y, t - tt, 200 + 10 * k, r=70, n=8, col=BA.LIT[lobe], dur=0.4, L0=40))
    # «Z» до пробуждения
    if t < dl + 0.1:
        for k in range(3):
            ph = ((t - 10.0) / 1.4 + k / 3) % 1
            kk = back_out(clamp(ph / 0.25), 2) * (1 - ease_in(clamp((ph - 0.75) / 0.25), 2)) * (1 - smooth(dl - .05, dl + .1, t))
            if kk > 0.04:
                zx, zy = 700 + 120 * ph, 520 - 200 * ph
                r = 24 * kk
                art.append(line([(zx - r, zy - r), (zx + r, zy - r), (zx - r, zy + r), (zx + r, zy + r)], 8 * kk + 3, "#cfe0ff", taper=.1, wmin=.8,
                                seed=240 + k))
    if t > dl - 0.02 and t < dl + 0.3:
        x, y = pose.pt(BCX - 73, BCY - 60)
        art.append(rays(x, y - 120, t - dl, 230, r=110, n=10, col="#e9eeff", dur=0.3, L0=36, w=7))
    u = clamp((t - 10.1) / 2.95)
    s = 1.02 + 0.10 * ease_io(u) + B.ease_kick(t - hit, 0.05, 16, 7) + B.ease_kick(t - dl, 0.025)
    return "".join(art), cam(540, 860 - 50 * u, s, 0.8 - 1.4 * u)


# ───────────────────────── s08: доли по очереди со значками
def icon_eye(sd):
    pts = [(-40, 0, 1), (-20, -20), (0, -26), (20, -20), (40, 0, 1), (20, 20), (0, 26), (-20, 20)]
    inner = shape(ellipse_pts(0, 0, 18, 18, 14), "#7a5ad8", f'<circle cx="0" cy="0" r="8" fill="{INK}"/><circle cx="-4" cy="-5" r="3.5" fill="#fff"/>',
                  w=3, seed=sd + 1)
    return shape(pts, "#ffffff", inner, w=4.2, seed=sd)


def icon_ear(sd):
    pts = [(-6, -40), (18, -38), (32, -18), (30, 8), (16, 26), (6, 40), (-10, 42), (-18, 30), (-8, 20), (4, 6), (-2, -10), (-18, -14), (-22, -30)]
    inner = line([(6, -24), (18, -14), (16, 2), (4, 10)], 4, "#b25a74", taper=.4, seed=sd + 2)
    return shape(pts, "#f8b4a4", inner, w=4.2, seed=sd)


def icon_note(sd):
    s = shape(ellipse_pts(-12, 22, 17, 12, 14, rot=-20), INK, "", w=2, seed=sd)
    s += line([(2, 20), (2, -34)], 7, INK, taper=.05, wmin=.95, seed=sd + 1)
    s += line([(2, -34), (24, -22), (26, -4)], 7, INK, taper=.3, wmin=.6, seed=sd + 2)
    return s


def icon_hand(sd):
    B.COL["skin"], B.COL["sh"] = "#f8c6a8", "#e0a084"
    return toon_hand(-6, 34, -90, 0.0, sd, 0.95, spread=1.2)


BADGES = [  # доля, слово, значок, положение (локально мозга)
    ("occip", "разные", icon_eye, (BCX + 290, BCY - 170)),
    ("temp", "части", icon_ear, (BCX - 320, BCY + 150)),
    ("pariet", "разное", icon_hand, (BCX + 40, BCY - 300)),
    ("cereb", "время", icon_note, (BCX + 320, BCY + 160)),
]


def badge(x, y, k, act, lobe, ic, sd):
    if k < 0.02:
        return ""
    col = BA.LIT[lobe]
    sc = k * (1 + 0.18 * act)
    s = []
    if act > 0.05:
        g = rad_grad([(0, col, .7 * act), (1, col, 0)], 0, 0, 130, 130)
        s.append(f'<circle cx="0" cy="0" r="130" fill="url(#{g})"/>')
    s.append(shape(ellipse_pts(0, 0, 66, 66, 24), col, "", w=5, seed=sd))
    s.append(shape(ellipse_pts(0, 0, 50, 50, 20), "#fbf6ea", "", w=3.4, seed=sd + 1))
    s.append(ic(sd + 10))
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)}) rotate({f(6 * math.sin(sd + 0.0))})">{"".join(s)}</g>'


def _inside(px, py, poly):
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i][:2]
        x2, y2 = poly[(i + 1) % n][:2]
        if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1 + 1e-9) + x1:
            c = not c
    return c


def city_points():
    """Огоньки «ночного города» внутри долей (локально): (x, y, доля, фаза)."""
    if "city" in _ST:
        return _ST["city"]
    BA.init()
    reg = BA._regions()
    brain_pts = BA.brain_outline()
    rs = np.random.RandomState(31)
    pts = []
    while len(pts) < 70:
        x, y = BCX + rs.uniform(-205, 205), BCY + rs.uniform(-140, 115)
        if not _inside(x, y, brain_pts):
            continue
        if math.hypot(x - EYE_L[0], y - EYE_L[1]) < 50 or math.hypot(x - EYE_R[0], y - EYE_R[1]) < 50 or math.hypot(x - BCX + 72, y - BCY - 74) < 40:
            continue
        lobe = "front"
        for k in ("tip", "pariet", "temp", "occip"):
            if _inside(x, y, reg[k]):
                lobe = k
        pts.append((x, y, lobe, rs.uniform(0, 6.28)))
    for k in range(8):
        x, y = BCX + rs.uniform(80, 200), BCY + rs.uniform(95, 160)
        if _inside(x, y, BA.CBL):
            pts.append((x, y, "cereb", rs.uniform(0, 6.28)))
    _ST["city"] = pts
    return pts


def city(t, lv):
    s = []
    for x, y, lobe, ph in city_points():
        a = lv.get(lobe, 0.0)
        tw = 0.5 + 0.5 * math.sin(t * 6 + ph * 3)
        r = 3.2 + 3.4 * a * tw
        if a * tw < 0.08:
            continue
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r + 4)}" fill="#fffbe0" opacity="{.25 * a * tw:.3f}"/>'
                 f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#fffbe0"/>')
    return f'<g clip-path="url(#{BA._G["oclip"]})">{"".join(s)}</g>'


def s08(t):
    sc = 1.08
    base = 0.3
    evs = [(lobe, word_t(w), ic, pos) for lobe, w, ic, pos in BADGES]
    lv = {k: base + 0.08 * math.sin(t * 3 + i) for i, k in enumerate(BA.LOBES)}
    lv["tip"] = max(lv["tip"], 0.7)
    act = {}
    last = None
    for lobe, tt, ic, pos in evs:
        e = t - tt
        a = smooth(-0.04, 0.06, e) * (1 - 0.65 * smooth(0.35, 0.8, e))
        if e > 0:
            last = lobe
        act[lobe] = a
        lv[lobe] = max(lv[lobe], base + (1 - base) * a)
    lv["front"] = max(lv["front"], 0.42 + 0.3 * smooth(12.7, 12.9, t) * (1 - smooth(13.2, 13.5, t)))
    bounce = sum(B.ease_kick(t - tt, 1.0, 14, 7) for _, tt, _, _ in evs)
    br = math.sin(t * 2.4)
    pose = Pose(540, y_for(sc) - 18 * bounce + 4 * br, sc, 2 * math.sin(t * 1.3), 1 + 0.015 * br - 0.04 * bounce)
    # ручки дирижируют
    SL, SR = pose.pt(*SH_L), pose.pt(*SH_R)
    wl = (SL[0] - 150 * sc + 20 * math.sin(t * 5.5), SL[1] - 70 * sc + 30 * math.sin(t * 5.5 + 1))
    wr = (SR[0] + 150 * sc + 20 * math.sin(t * 5.5 + 2), SR[1] - 80 * sc + 30 * math.sin(t * 5.5 + 3))
    look = (0.0, -0.4)
    if last:
        bx, by = dict((l_, p) for l_, _, _, p in evs)[last]
        look = (clamp((bx - (BCX - 70)) / 300, -1, 1), clamp((by - BCY) / 200, -1, 0.8))
    fc = face(1.0, look, "smile", t, brow=0.6, lid_col=lid_col(lv), blush=0.35)
    pr = f'<g transform="{pose.tf()}">{city(t, lv)}</g>'
    art = [shadow(540, FLOOR + 6, 180),
           char(pose, lv, fc, wl, wr, 220 + 10 * math.sin(t * 5.5), -40 + 10 * math.sin(t * 5.5 + 2), 0.0, 0.0, -50, 50, legs_for(pose, live=0.8),
                0.8, halo=0.9, front=pr)]
    for i, (lobe, tt, ic, pos) in enumerate(evs):
        x, y = pose.pt(*pos)
        e = t - tt
        k = back_out(clamp(e / 0.26), 2.4)
        if k > 0.02:
            lx, ly = pose.pt(*BA.LOBE_CENTER[lobe])
            # искра-нить от доли к значку
            u = clamp(e / 0.18)
            art.insert(1, line([(lx, ly), (lx + (x - lx) * u, ly + (y - ly) * u)], 5, BA.LIT[lobe], taper=.3, wmin=.6, seed=300 + i))
        art.append(badge(x, y + 6 * math.sin(t * 2.6 + i), k, act[lobe], lobe, ic, 400 + 40 * i))
        art.append(rays(x, y, e, 500 + 10 * i, r=72, n=8, col=BA.LIT[lobe], dur=0.35, L0=34, w=7))
    u = clamp((t - 12.65) / 2.8)
    return "".join(art), cam(540 - 20 * u, 740 + 10 * u, 1.04 + 0.04 * u, -0.6 + 1.0 * u)


# ───────────────────────── s10: ночная смена, коробки на полки
SHELF_X0, SHELF_X1 = 640, 1080
SHELF_Y = [520, 760, 1000]


def mem_box(x, y, w, h, kind, sd, rot=0.0):
    """Коробка-воспоминание: картон, скотч, наклейка-картинка (звезда / сердце / солнце / домик). (x, y) — низ-центр."""
    inner = blob(rect_pts(x + w * .18, y - h - 4, x + w / 2 + 4, y + 4), "#a8743e", .75)
    inner += blob(rect_pts(x - 10, y - h - 4, x + 10, y + 4), "#e8cf9a", .95)
    inner += line([(x - w / 2 + 6, y - h + 16), (x + w / 2 - 6, y - h + 16)], 3, "#8a5a2e", seed=sd + 2, op=.8)
    lx, ly = x - w * .22, y - h * .45
    inner += shape(rect_pts(lx - 22, ly - 20, lx + 22, ly + 20, 6), "#fbf6ea", "", w=2.6, seed=sd + 3)
    if kind == 0:
        inner += star(lx, ly, 16, "#ffd23e", sd + 4)
    elif kind == 1:
        inner += shape([(lx, ly + 13, 1), (lx - 15, ly - 2), (lx - 9, ly - 13), (lx, ly - 7, 1), (lx + 9, ly - 13), (lx + 15, ly - 2)], "#ff6f8e", "",
                       w=2.4, seed=sd + 4)
    elif kind == 2:
        inner += shape(ellipse_pts(lx, ly, 10, 10, 12), "#ffb13e", "", w=2.4, seed=sd + 4)
        for k in range(6):
            a = k * math.pi / 3
            inner += line([(lx + math.cos(a) * 13, ly + math.sin(a) * 13), (lx + math.cos(a) * 18, ly + math.sin(a) * 18)], 3, "#e08a1e", seed=sd + 5 + k)
    else:
        inner += shape([(lx - 13, ly + 14, 1), (lx - 13, ly - 2, 1), (lx, ly - 14, 1), (lx + 13, ly - 2, 1), (lx + 13, ly + 14, 1)], "#7ec8ff", "",
                       w=2.4, seed=sd + 4)
    s = shape(rect_pts(x - w / 2, y - h, x + w / 2, y, 8), "#d29a58", inner, w=4.4, seed=sd)
    if rot:
        s = f'<g transform="rotate({f(rot)} {f(x)} {f(y)})">{s}</g>'
    return s


def shelves(t, n_boxes_extra):
    s = []
    # стойки
    for x in (SHELF_X0 + 14, SHELF_X1 - 14):
        s.append(shape(rect_pts(x - 14, 380, x + 14, FLOOR - 4, 4), "#7a5a3c", blob(rect_pts(x + 2, 380, x + 14, FLOOR), "#5a3e26", .8), w=4,
                       seed=600 + x))
    for i, y in enumerate(SHELF_Y):
        s.append(shape(rect_pts(SHELF_X0 - 10, y, SHELF_X1 + 10, y + 26, 4), "#9a7048", blob(rect_pts(SHELF_X0 - 10, y + 14, SHELF_X1 + 10, y + 26), "#6e4c2e", .8),
                       w=4.4, seed=620 + i))
    return "".join(s)


def lights(t):
    """Гирлянда огоньков вдоль полок: бегущая волна."""
    s = []
    for i, y in enumerate(SHELF_Y):
        n = 9
        for k in range(n):
            x = SHELF_X0 + 20 + k * (SHELF_X1 - SHELF_X0 - 40) / (n - 1)
            ph = (t * 3.2 - k * 0.22 - i * 0.4) % 1
            on = math.exp(-ph * 4)
            col = mix("#5a6390", "#ffe27a", on)
            if on > 0.1:
                g = rad_grad([(0, "#ffe27a", .6 * on), (1, "#ffe27a", 0)], x, y + 34, 36, 36)
                s.append(f'<circle cx="{f(x)}" cy="{f(y + 34)}" r="36" fill="url(#{g})"/>')
            s.append(f'<circle cx="{f(x)}" cy="{f(y + 34)}" r="8" fill="{col}" stroke="{INK}" stroke-width="2.6"/>')
        s.append(line([(SHELF_X0 + 10, y + 26), (SHELF_X1 - 10, y + 26)], 2.4, INK, seed=640 + i, op=.8))
    return "".join(s)


def nightcap(t, sway):
    """Ночной колпак (локально мозга): конус в полоску, свисает назад, помпон."""
    bx0, bx1, by = BCX - 120, BCX + 110, BCY - 128
    tipx, tipy = BCX + 230 + 30 * sway, BCY - 120 + 60 + 20 * sway
    pts = [(bx0, by + 6), (BCX - 60, BCY - 250), (BCX + 60, BCY - 270), (BCX + 170, BCY - 220), (tipx, tipy), (BCX + 150, BCY - 170), (bx1, by - 4)]
    inner = ""
    for k in range(4):
        x = BCX - 70 + k * 70
        inner += blob([(x, BCY - 300), (x + 32, BCY - 300), (x + 52, BCY - 100), (x + 20, BCY - 100)], "#7ea8ff", .9)
    inner += blob([(BCX + 60, BCY - 300), (BCX + 300, BCY - 260), (BCX + 300, BCY - 100), (BCX + 60, BCY - 140)], "#1c2a6a", .25)
    s = shape(pts, "#3f62c8", inner, w=5, seed=700)
    band_pts = [(bx0 - 14, by + 14), (BCX - 20, by - 18), (bx1 + 14, by - 6), (bx1 + 10, by + 22), (BCX - 20, by + 12), (bx0 - 10, by + 40)]
    s += shape(band_pts, "#f6f3ec", blob([(bx0, by + 30), (bx1, by + 6), (bx1, by + 22), (bx0, by + 42)], "#d6d0c4", .8), w=4.4, seed=701)
    s += shape(ellipse_pts(tipx + 6, tipy + 16, 26, 26, 16), "#f6f3ec", blob(ellipse_pts(tipx + 14, tipy + 24, 16, 14, 10), "#d6d0c4", .8), w=4, seed=702)
    return s


def s10(t):
    zt = word_t("занят")             # 17.28
    dt = word_t("делами")            # 18.00
    sc = 0.95
    yb = y_for(sc)
    # путь: несёт коробку A к полке, ставит на «занят»; берёт B с пола, на «делами» ставит одной рукой и вытирает лоб другой
    x = 400 + 70 * smooth(16.75, zt - 0.05, t) - 30 * smooth(zt + 0.15, zt + 0.45, t) + 40 * smooth(dt - 0.35, dt - 0.05, t)
    stepph = (t - 16.75) * 2 * math.pi / 0.5
    walking = smooth(16.7, 16.8, t) * (1 - smooth(zt - 0.12, zt, t)) + smooth(dt - 0.38, dt - 0.3, t) * (1 - smooth(dt - 0.08, dt, t))
    crouch = smooth(zt + 0.2, zt + 0.38, t) * (1 - smooth(zt + 0.5, zt + 0.66, t))
    bob = -10 * abs(math.sin(stepph)) * walking
    e1, e2 = t - zt, t - dt
    pose = Pose(x, yb + bob + 50 * crouch, sc, 3 * math.sin(stepph) * walking - 6 * crouch + B.ease_kick(e1, -4), 1 - 0.06 * crouch)
    SL, SR = pose.pt(*SH_L), pose.pt(*SH_R)
    # коробка A: в руках перед мозгом → на средней полке
    BW, BH = 170, 120
    A_shelf = (735, SHELF_Y[1])
    B_shelf = (895, SHELF_Y[1])
    A_carry = (pose.x + 175, pose.y + 40)
    lift = smooth(zt - 0.45, zt - 0.05, t)
    A_pos = lerp(A_carry, (A_shelf[0], A_shelf[1] - 4), lift)
    if t >= zt:
        A_pos = (A_shelf[0], A_shelf[1] + B.ease_kick(e1, -10, 18, 8))
    # коробка B: на полу у ног → поднята правой рукой → на полке на «делами»
    B_floor = (pose.x + 160 if t < zt + 0.4 else 570, FLOOR - 2)
    B_floor = (640, FLOOR - 2)
    grabbed = t > zt + 0.45
    if not grabbed:
        B_pos = B_floor
    else:
        u = smooth(zt + 0.45, dt - 0.02, t)
        B_pos = (640 + (B_shelf[0] - 640) * u, FLOOR - 2 + (B_shelf[1] - FLOOR + 2) * ease_out(u, 2) - 80 * math.sin(math.pi * u))
        if t >= dt:
            B_pos = (B_shelf[0], B_shelf[1] + B.ease_kick(e2, -10, 18, 8))
    # руки
    if t < zt + 0.02:
        wl = (A_pos[0] - BW / 2 - 6, A_pos[1] - BH * .5)
        wr = (A_pos[0] + BW / 2 + 6, A_pos[1] - BH * .55)
        al, ar, cl, cr = 20, 160, 0.2, 0.2
    else:
        wl0, wr0, al0, ar0 = hang(pose, t)
        back = smooth(zt + 0.02, zt + 0.22, t)
        wl = lerp((A_shelf[0] - BW / 2 - 6, A_shelf[1] - BH * .5), wl0, back)
        al, cl = 20 + (al0 - 20) * back, 0.2
        # правая: к коробке B, держит её сверху, ставит
        if t < zt + 0.45:
            u = smooth(zt + 0.05, zt + 0.42, t)
            wr = lerp((A_shelf[0] + BW / 2 + 6, A_shelf[1] - BH * .55), (B_floor[0] + BW / 2 + 4, B_floor[1] - BH * .6), u)
            ar, cr = 160, 0.2
        elif t < dt + 0.12:
            wr = (B_pos[0] + BW / 2 + 4, B_pos[1] - BH * .6)
            ar, cr = 160, 0.25
        else:
            wr = lerp((B_shelf[0] + BW / 2 + 4, B_shelf[1] - BH * .6), wr0, smooth(dt + 0.12, dt + 0.4, t))
            ar, cr = 160 + (ar0 - 160) * smooth(dt + 0.12, dt + 0.4, t), 0.2
        # левая: вытирает лоб на «делами»
        wipe = smooth(dt - 0.3, dt - 0.1, t) * (1 - smooth(dt + 0.35, dt + 0.6, t))
        if wipe > 0:
            fx, fy = pose.pt(BCX - 120 + 60 * math.sin((t - dt) * 14), BCY - 120)
            wl = lerp(wl, (fx - 20, fy + 10), wipe)
            al = al + (-20 - al) * wipe
            cl = 0.1
    lv = {k: 0.45 + 0.2 * math.sin(t * 4 + i * 1.7) for i, k in enumerate(BA.LOBES)}
    lv["front"] = 0.7 + 0.2 * math.sin(t * 5)
    fc = face(1.0, (0.9, -0.1) if t < dt - 0.3 else (0.2, -0.6), "smile" if t < dt - 0.3 else "o", t, brow=0.5, lid_col=lid_col(lv), blush=0.3)
    stepl = 40 * max(0.0, math.sin(stepph)) * walking
    stepr = 40 * max(0.0, -math.sin(stepph)) * walking
    hat = nightcap(t, math.sin(t * 6) * 0.6 + B.ease_kick(e1, 1.0))
    boxesA = mem_box(A_pos[0], A_pos[1], BW, BH, 1, 800, rot=0 if t >= zt else 3 * math.sin(stepph))
    boxB = mem_box(B_pos[0], B_pos[1], BW * .85, BH * .85, 2, 820)
    fixed = mem_box(980, SHELF_Y[0], 150, 110, 0, 840) + mem_box(800, SHELF_Y[0], 140, 96, 3, 860) + mem_box(740, SHELF_Y[2], 160, 110, 3, 880)
    fixed += mem_box(930, SHELF_Y[2], 150, 120, 1, 900) + mem_box(1020, SHELF_Y[1], 90, 80, 0, 920)
    art = [shelves(t, 0), fixed, lights(t), shadow(pose.x, FLOOR + 6, 150)]
    legs = legs_for(pose, lift_l=stepl, lift_r=stepr, spread=10 * crouch, live=0.75)
    front = ""
    if t < zt + 0.02:
        front = boxesA
    else:
        art.append(boxesA)
    art.append(char(pose, lv, fc, wl, wr, al, ar, cl, cr, -40, 40, legs, 0.75, halo=0.7, front=front + boxB if grabbed else front,
                    behind="" if grabbed else boxB, hat=hat))
    art.append(rays(A_shelf[0], A_shelf[1] - 60, e1, 940, r=90, n=7, col="#ffe27a", dur=0.35, L0=30, w=6))
    art.append(rays(B_shelf[0], B_shelf[1] - 60, e2, 960, r=90, n=7, col="#ffe27a", dur=0.35, L0=30, w=6))
    if e2 > -0.15 and e2 < 0.7:
        fx, fy = pose.pt(BCX - 40, BCY - 170)
        k = clamp((e2 + 0.15) / 0.85)
        art.append(B.sweat(fx - 140 * k, fy - 60 * math.sin(math.pi * k) + 200 * k * k, 1.6 * (1 - 0.3 * k)))
    u = clamp((t - 16.75) / 2.15)
    return "".join(art), cam(665 + 30 * u, 820 - 10 * u, 1.0 + 0.04 * u, 0.6 - 1.0 * u)


# ───────────────────────── s15: тёплый свет, большой палец и подмигивание
def s15(t):
    hit = word_t("лучше")            # 26.64
    sc = 1.25
    br = math.sin(t * 2.6)
    e = t - hit
    raise_ = smooth(hit - 0.3, hit - 0.02, t)
    pose = Pose(610, y_for(sc) + 5 * br - 18 * B.ease_kick(e, 1.0, 12, 6), sc, 3 * math.sin(t * 1.8) - 4 * raise_, 1 + 0.015 * br)
    lv = {k: 0.88 + 0.08 * math.sin(t * 3 + i) for i, k in enumerate(BA.LOBES)}
    WARM = {"front": "#ffc46a", "tip": "#ffe08a", "pariet": "#ffa98f", "temp": "#ffb6c4", "occip": "#f7a0c0", "cereb": "#ffb38a"}
    wl0, wr0, al0, ar0 = hang(pose, t)
    SL = pose.pt(*SH_L)
    up = (SL[0] - 170 * sc, SL[1] - 60 * sc + 6 * math.sin(t * 6))
    wl = lerp(wl0, up, raise_)
    wr = (wr0[0] + 30 * math.sin(t * 3), wr0[1] - 60 * sc * math.sin(math.pi * clamp((t - 25.75) / 0.9)) * 0.5)
    B.set_skin(1.0)
    th_k = 1 + B.ease_kick(e, 0.25, 14, 6)
    if raise_ > 0.6:
        hl = thumbs_up(wl[0], wl[1], 1500, sc * 1.3 * th_k, mirror=True)
    else:
        hl = toon_hand(wl[0], wl[1], al0 + (200 - al0) * raise_, 0.2 + raise_, 1500, sc * 1.3)
    wink = t > hit - 0.04 and e < 0.75
    fc = face(1.0, (-0.5, -0.2), "grin", t, brow=0.6, lid_col=lid_col(lv, lit=WARM, warm=0.15), blush=0.8, wink_r=wink)
    art = [shadow(pose.x, FLOOR + 6, 200),
           char(pose, lv, fc, wl, wr, al0, ar0, 0.2, 0.3, -40, 40, legs_for(pose, live=1.0), 1.0, halo=1.3, lit=WARM, warm=0.15, hands_l=hl)]
    # искорки вокруг
    for j in range(9):
        a = j * 2 * math.pi / 9 + t * 0.6
        r = 380 + 30 * math.sin(t * 2 + j)
        sx, sy = pose.x + math.cos(a) * r, pose.y - 40 + math.sin(a) * r * .8
        k = 0.5 + 0.5 * math.sin(t * 7 + j * 1.3)
        art.append(star(sx, sy, 10 + 16 * k, "#ffe9a0", 1600 + j, rot=t * 40 + j * 20))
    if e > -0.02:
        art.append(rays(wl[0] + 10, wl[1] - 90 * sc, e, 1700, r=60, n=9, col="#ffe27a", dur=0.4, L0=44))
        for j in range(4):
            kk = back_out(clamp((e - j * 0.05) / 0.25), 2.4) * (1 - smooth(0.6, 0.9, e))
            if kk > 0.03:
                ex, ey = pose.pt(*EYE_R)
                art.append(star(ex + 60 + j * 34, ey - 70 - j * 26, 22 * kk, "#fff3b0", 1720 + j, rot=20 * j))
    u = clamp((t - 25.75) / 1.75)
    s = 1.12 + 0.06 * u + B.ease_kick(e, 0.06, 16, 7)
    return "".join(art), cam(570, 830 - 20 * u, s, -0.6 + 1.0 * u)


def build_static():
    if _ST.get("ok"):
        return
    _ST["bg"] = B.background()
    _ST["bgw"] = B.background(warm=1.0)
    BA.init()
    city_points()
    lib.static_done()
    _ST["ok"] = 1


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s01": s01, "s02": s02, "s07": s07, "s08": s08, "s10": s10, "s15": s15}[sid](t)
    bg = _ST["bgw"] if sid == "s15" else _ST["bg"]
    return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{cm}">{bg}{B.dust(t)}{art}</g>')
