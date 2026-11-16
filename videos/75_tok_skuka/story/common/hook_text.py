"""Рукописный текстовый хук рилса 75 «Зачем он жмёт 190 раз?» (пишет группа C; s01 и s02 зовут ОДНУ функцию hook_text(t)).

Тем же пером, что common/hand_kot.py: штрих — полоса переменной толщины (вниз толще, вверх и на связках тоньше), концы
скруглены, перо идёт по длине линии. Формы букв — скелеты букв Caveat (scripts/writeon.layout + letter_strokes, порядок
штрихов как у руки: стойки сверху вниз, петли против часовой), почерк неровный фиксированным зерном (одинаково в каждом
кадре). Текст приклеен к ЭКРАНУ (координаты кадра 1080×1920, не мира): камера и тряска его не двигают; живая дрожь
штриха — ±0.6 px 12 раз в секунду (функция времени ролика, на склейке s01→s02 ни пикселя скачка).

    hook_text(t, t_start=None, t_full=None, fade=1.0) -> SVG (кадр)
        t_start — начало письма (по умолчанию −0.03: в кадре 0 уже первые штрихи), t_full — всё дописано (по умолчанию 0.33);
        fade — общая прозрачность (s02 у склейки держит 1.0 до t1, гаснет склейкой).
    BOX — (x0, y0, x1, y1) занятая надписью зона экрана (для проверки, что за буквами нет предметов).
Под «190» — жёлтый маркер (появляется, когда дописана вторая строка)."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

LINES = ("Зачем он жмёт", "190 раз?")
SIZE = (232, 236)               # кегль строк Caveat: строчная (x-высота) ≈ 0.39 кегля → 90+ px
BASE = (218, 362)               # базовые линии строк (экран)
SX = (.76, .72)                  # сжатие строк по ширине (почерк убористый: строка 1 влезает в 1080 с полями)
UP_K = .55                      # прописные и выносные выше x-высоты и ниже базы — короче (школьный почерк: заглавная ≈ 1.5 строчной)
CX = (532, 718)                 # центры строк по x: вторая строка правее (над головой Димы слева — чисто)
COL = "#1d2448"                 # тёмные чернила, как «кот» hand_kot
MARK = "#ffd23a"
T_START = -0.03
T_FULL = 0.33
SLANT = math.tan(math.radians(6))
_C = {}


def _letters():
    """Буквы строк: [(строка, [штрихи: (N×2 точки xy экрана, радиусы)])]. Считается один раз на процесс."""
    if "L" in _C:
        return _C["L"]
    import writeon as WO
    out = []
    rs = np.random.RandomState(75)
    for li, (txt, size, base, sx) in enumerate(zip(LINES, SIZE, BASE, SX)):
        Wc, Hc = 1600, int(size * 1.8)
        fnt = WO._font(size)
        asc, desc = fnt.getmetrics()
        y0 = Hc / 2 - (asc + desc) / 2
        bl = y0 + asc                                      # база строки в холсте буквы
        xt = y0 + fnt.getbbox("а")[1]                      # верх строчных
        xh = bl - xt
        lets = WO.layout(txt, size, Wc, Hc, 800, Hc / 2, seed=11 + li, jitter=1.0, max_w=1580)
        for L in lets:
            sts = []
            for st in WO.letter_strokes(L):
                p = st["path"][:, ::-1].astype(float)          # (y, x) → (x, y)
                y = p[:, 1]
                y = np.where(y < xt, xt - (xt - y) * UP_K, np.where(y > bl, bl + (y - bl) * UP_K, y))
                p[:, 1] = y - bl + base
                p[:, 0] = CX[li] + (p[:, 0] - 800) * sx
                # наклон почерка вокруг середины строчных, неровность руки
                p[:, 0] += -(p[:, 1] - (base - xh / 2)) * SLANT
                p += rs.normal(0, .35, p.shape)
                r = np.asarray(st["r"], float)
                if st["kind"] == "dot":
                    r = np.maximum(r, 5.0)
                sts.append((p, r * (.92 + .08 * sx), st["kind"]))
            if sts:
                out.append((li, L["ch"], sts))
    _C["L"] = out
    _C["xh"] = xh
    return out


def _lens():
    if "len" in _C:
        return _C["len"]
    lets = _letters()
    segs = []
    for li, ch, sts in lets:
        for p, r, kind in sts:
            ln = float(np.sum(np.linalg.norm(np.diff(p, axis=0), axis=1))) if len(p) > 1 else 1.0
            segs.append((li, p, r, kind, max(ln, 6.0)))
    tot = sum(s[4] for s in segs)
    _C["len"] = (segs, tot)
    return _C["len"]


def _width(p, r):
    """Толщина пера: вниз толще, вверх тоньше (как hand_kot), основа — толщина буквы шрифта."""
    d = np.gradient(p, axis=0)
    down = d[:, 1] / (np.linalg.norm(d, axis=1) + 1e-9)
    w = 2 * r * (0.72 + 0.42 * np.clip(.2 + .8 * down, 0, 1))
    if len(w) > 5:
        w = np.convolve(np.r_[w[:3][::-1], w, w[-3:][::-1]], np.ones(5) / 5, "valid")[1:-1][:len(p)]
        if len(w) < len(p):
            w = np.r_[w, np.full(len(p) - len(w), w[-1])]
    n = len(w)
    a = np.minimum(1, np.arange(n) / 4 + .45)
    b = np.minimum(1, (n - 1 - np.arange(n)) / 6 + .35)
    return w * a * b


def _poly(Q, W):
    d = np.gradient(Q, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
    N = np.stack([-d[:, 1], d[:, 0]], 1)
    L, R = Q + N * (W / 2)[:, None], Q - N * (W / 2)[:, None]
    pp = [tuple(p) for p in L] + [tuple(p) for p in R[::-1]]
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pp) + "Z"


def _jit(t):
    """Живая дрожь штриха: 12 раз в секунду, ±0.6 px — одна и та же функция времени ролика в s01 и s02."""
    k = int(math.floor(t * 12 + 1e-6))
    return .6 * math.sin(k * 12.9898) , .6 * math.sin(k * 78.233 + 1.3)


def _box():
    segs, _ = _lens()
    P = np.vstack([s[1] for s in segs])
    rmax = max(float(s[2].max()) for s in segs)
    return (float(P[:, 0].min() - rmax), float(P[:, 1].min() - rmax), float(P[:, 0].max() + rmax), float(P[:, 1].max() + rmax))


def mark_rect():
    """Маркер под «190»: прямоугольник по штрихам первых трёх букв второй строки."""
    lets = [x for x in _letters() if x[0] == 1][:3]
    P = np.vstack([p for _, _, sts in lets for p, _, _ in sts])
    return float(P[:, 0].min()) - 14, float(P[:, 1].max()) - 46, float(P[:, 0].max()) + 18, float(P[:, 1].max()) + 8


def hook_text(t, t_start=None, t_full=None, fade=1.0):
    if fade <= .003:
        return ""
    ts = T_START if t_start is None else t_start
    tf = T_FULL if t_full is None else t_full
    if t < ts:
        return ""
    u = min(1.0, (t - ts) / max(1e-6, tf - ts))
    segs, tot = _lens()
    jx, jy = _jit(t)
    done = u * tot
    acc = 0.0
    o = []
    l1_end = sum(s[4] for s in segs if s[0] == 0)
    # маркер под «190»: проявляется мазком слева направо, когда перо ушло на вторую строку
    mu = min(1.0, max(0.0, (done - l1_end) / max(1.0, (tot - l1_end) * .45)))
    if mu > 0:
        x0, y0, x1, y1 = mark_rect()
        xe = x0 + (x1 - x0) * mu
        pts = f"M{x0:.1f} {y0 + 6:.1f}L{xe:.1f} {y0:.1f}L{xe + 4:.1f} {y1:.1f}L{x0 - 4:.1f} {y1 + 4:.1f}Z"
        o.append(f'<path d="{pts}" fill="{MARK}" opacity=".85"/>')
    for li, p, r, kind, ln in segs:
        if acc >= done:
            break
        q = min(1.0, (done - acc) / ln)
        acc += ln
        if len(p) < 2:
            continue
        if q < 1:
            L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
            n = max(2, int(np.searchsorted(L, L[-1] * q)) + 1)
            P_, R_ = p[:n], r[:n]
        else:
            P_, R_ = p, r
        Q = P_ + np.array([jx, jy])
        Wd = _width(Q, R_) if len(Q) > 2 else 2 * R_
        o.append(f'<path d="{_poly(Q, Wd)}" fill="{COL}"/>')
        o.append(f'<circle cx="{Q[0][0]:.1f}" cy="{Q[0][1]:.1f}" r="{Wd[0] / 2:.2f}" fill="{COL}"/>')
        o.append(f'<circle cx="{Q[-1][0]:.1f}" cy="{Q[-1][1]:.1f}" r="{Wd[-1] / 2:.2f}" fill="{COL}"/>')
    g = "".join(o)
    return g if fade >= .999 else f'<g opacity="{fade:.3f}">{g}</g>'


def BOX():
    return _box()
