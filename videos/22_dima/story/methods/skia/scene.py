"""Ночь Димы — процедурное 2D на skia-python (CPU-растр, без браузера).

Что здесь своё по сравнению с SVG-наброском (../../code/night.html, геометрия взята оттуда же):
  * кисть переменной ширины: контур — полигон вдоль кривой, толще на стороне тени, сужается на концах;
  * тень «одна на фигуру» кодом: фигура минус та же фигура, сдвинутая к свету (PathOps);
  * свет: ночь — multiply с градиентом и виньеткой, экран/окна/огонёк — screen/plus с размытием;
  * процедурные фактуры: обои, доски с волокном, тартан пледа, мех кота зубцами, щетина, звёзды;
  * деформация пути по точкам (огонёк колышется формой, как сетка рига), моргание, листание.

python3 scene.py            -> still.png + замер времени кадра
python3 scene.py --anim     -> ещё anim.mp4 (3 с, 30 к/с)
Нужно: skia-python (pip, колесо 15 МБ, 50 МБ на диске), numpy, ffmpeg. В контейнере нет libEGL.so.1 —
импорт skia падает; достаточно симлинка на libEGL из Chromium Playwright в LD_LIBRARY_PATH (рендер всё равно на CPU).
"""
import math
import re
import subprocess
import sys
import time
from pathlib import Path as FsPath

import numpy as np
import skia

W, H = 1080, 1920
HERE = FsPath(__file__).resolve().parent
INK = (24, 21, 30)

# ---------------------------------------------------------------- геометрия


def parse(d):
    """SVG path d -> skia.Path (M L H V C S Q T Z, абсолютные и относительные)."""
    toks = re.findall(r'[MmLlHhVvCcSsQqTtZz]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?', d)
    p = skia.Path()
    i, cmd = 0, None
    x = y = sx = sy = 0.0
    lc = None  # последняя контрольная для S/T

    def nums(k):
        nonlocal i
        v = [float(t) for t in toks[i:i + k]]
        i += k
        return v
    while i < len(toks):
        if re.match(r'[A-Za-z]', toks[i]):
            cmd = toks[i]
            i += 1
            if cmd in 'Zz':
                p.close()
                x, y = sx, sy
                lc = None
                continue
        rel = cmd.islower()
        c = cmd.upper()
        ox, oy = (x, y) if rel else (0.0, 0.0)
        if c == 'M':
            a, b = nums(2)
            x, y = a + ox, b + oy
            sx, sy = x, y
            p.moveTo(x, y)
            cmd = 'l' if rel else 'L'
            lc = None
        elif c == 'L':
            a, b = nums(2)
            x, y = a + ox, b + oy
            p.lineTo(x, y)
            lc = None
        elif c == 'H':
            (a,) = nums(1)
            x = a + ox
            p.lineTo(x, y)
            lc = None
        elif c == 'V':
            (b,) = nums(1)
            y = b + oy
            p.lineTo(x, y)
            lc = None
        elif c == 'C':
            a = nums(6)
            x1, y1, x2, y2, x3, y3 = a[0] + ox, a[1] + oy, a[2] + ox, a[3] + oy, a[4] + ox, a[5] + oy
            p.cubicTo(x1, y1, x2, y2, x3, y3)
            lc = ('C', x2, y2)
            x, y = x3, y3
        elif c == 'S':
            a = nums(4)
            x1, y1 = (2 * x - lc[1], 2 * y - lc[2]) if lc and lc[0] == 'C' else (x, y)
            x2, y2, x3, y3 = a[0] + ox, a[1] + oy, a[2] + ox, a[3] + oy
            p.cubicTo(x1, y1, x2, y2, x3, y3)
            lc = ('C', x2, y2)
            x, y = x3, y3
        elif c == 'Q':
            a = nums(4)
            x1, y1, x2, y2 = a[0] + ox, a[1] + oy, a[2] + ox, a[3] + oy
            p.quadTo(x1, y1, x2, y2)
            lc = ('Q', x1, y1)
            x, y = x2, y2
        elif c == 'T':
            a = nums(2)
            x1, y1 = (2 * x - lc[1], 2 * y - lc[2]) if lc and lc[0] == 'Q' else (x, y)
            x2, y2 = a[0] + ox, a[1] + oy
            p.quadTo(x1, y1, x2, y2)
            lc = ('Q', x1, y1)
            x, y = x2, y2
    return p


def ell(cx, cy, rx, ry=None):
    return skia.Path.Oval(skia.Rect.MakeXYWH(cx - rx, cy - (ry or rx), 2 * rx, 2 * (ry or rx)))


def rect(x, y, w, h, r=0):
    if r:
        return skia.Path.RRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r))
    return skia.Path.Rect(skia.Rect.MakeXYWH(x, y, w, h))


def poly(pts, closed=True):
    return skia.Path.Polygon([skia.Point(*q) for q in pts], closed)


def moved(path, dx, dy):
    q = skia.Path(path)
    q.offset(dx, dy)
    return q


def xf(path, m):
    q = skia.Path(path)
    q.transform(m)
    return q


def rot(path, deg, cx, cy):
    return xf(path, skia.Matrix.RotateDeg(deg, skia.Point(cx, cy)))


def union(*ps):
    out = skia.Path(ps[0])
    for q in ps[1:]:
        out = skia.Op(out, q, skia.PathOp.kUnion_PathOp)
    return out


def warp(path, fn):
    """Деформация по точкам пути (контрольные тоже): основа «сетки» для огонька и меха."""
    out = skia.Path()
    it = skia.Path.Iter(path, False)
    V = skia.Path.Verb
    while True:
        v, pts = it.next()
        if v == V.kDone_Verb:
            break
        q = [fn(pt.x(), pt.y()) for pt in pts]
        if v == V.kMove_Verb:
            out.moveTo(*q[0])
        elif v == V.kLine_Verb:
            out.lineTo(*q[1])
        elif v == V.kQuad_Verb:
            out.quadTo(*q[1], *q[2])
        elif v == V.kConic_Verb:
            out.conicTo(*q[1], *q[2], it.conicWeight())
        elif v == V.kCubic_Verb:
            out.cubicTo(*q[1], *q[2], *q[3])
        elif v == V.kClose_Verb:
            out.close()
    return out


def fur(cx, cy, rx, ry, n, depth, seed, skip=None):
    """Пушистый овал: зубцы меха с разной длиной и наклоном (процедурно)."""
    r = np.random.default_rng(seed)
    pts = []
    for k in range(n):
        a0 = 2 * math.pi * k / n
        a1 = a0 + math.pi / n * (0.9 + 0.3 * r.random())
        if skip and skip[0] < (a0 % (2 * math.pi)) < skip[1]:
            pts.append((cx + rx * math.cos(a0), cy + ry * math.sin(a0)))
            continue
        dd = depth * (0.6 + 0.8 * r.random())
        pts.append((cx + rx * math.cos(a0), cy + ry * math.sin(a0)))
        lean = 0.35 * (r.random() - 0.5)
        pts.append((cx + (rx + dd) * math.cos(a1 + lean), cy + (ry + dd) * math.sin(a1 + lean)))
    p = skia.Path()
    p.moveTo(*pts[0])
    for k in range(1, len(pts)):
        a, b = pts[k - 1], pts[k]
        p.quadTo((a[0] + b[0]) / 2 + (b[1] - a[1]) * 0.12, (a[1] + b[1]) / 2 - (b[0] - a[0]) * 0.12, *b)
    p.close()
    return p

# ---------------------------------------------------------------- цвет и кисть


def C(rgb, a=255):
    if isinstance(rgb, str):
        rgb = tuple(int(rgb[i:i + 2], 16) for i in (1, 3, 5))
    return skia.ColorSetARGB(int(a), int(rgb[0]), int(rgb[1]), int(rgb[2]))


def rgbt(hexs):
    return tuple(int(hexs[i:i + 2], 16) for i in (1, 3, 5))


def shade_of(rgb, k=0.74):
    r, g, b = rgbt(rgb) if isinstance(rgb, str) else rgb
    return (r * k * 0.95, g * k * 0.97, min(255, b * k * 1.08 + 6))


def paint(color, a=255, blend=None, blur=0, shader=None, style=None, sw=None):
    p = skia.Paint(AntiAlias=True)
    p.setColor(C(color, a) if not isinstance(color, int) else color)
    if shader is not None:
        p.setShader(shader)
    if blend is not None:
        p.setBlendMode(blend)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.BlurStyle.kNormal_BlurStyle, blur))
    if style == 'stroke':
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(sw)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def wobble(s, ph):
    return 0.5 * math.sin(s * 0.031 + ph) + 0.3 * math.sin(s * 0.083 + 2.1 * ph) + 0.2 * math.sin(s * 0.19 + 3.7 * ph)


class Brush:
    """Кисть переменной ширины: контур -> полигон. Толще там, где нормаль смотрит от света."""

    def __init__(self, light=(0.55, -0.83), step=2.2):
        self.light = light
        self.step = step
        self.ph = 0.0

    def stroke(self, path, w, light=None, taper=True, press=1.0):
        lx, ly = light or self.light
        out = []
        pm = skia.PathMeasure(path, False)
        while True:
            L = pm.getLength()
            if L > 1:
                closed = pm.isClosed()
                n = max(4, int(L / self.step))
                ss = np.linspace(0, L, n + (0 if closed else 1), endpoint=not closed)
                P, N = [], []
                for s in ss:
                    r = pm.getPosTan(float(s))
                    if not r:
                        continue
                    pos, tan = r
                    P.append((pos.x(), pos.y()))
                    N.append((tan.y(), -tan.x()))
                P, N = np.array(P), np.array(N)
                if len(P) >= 3:
                    if closed:  # нормаль наружу
                        c = P.mean(0)
                        if np.mean(np.sum(N * (P - c), 1)) < 0:
                            N = -N
                    self.ph += 1.7
                    side = np.clip(-(N[:, 0] * lx + N[:, 1] * ly), 0, 1) if closed else 0.5
                    wv = np.array([wobble(s, self.ph) for s in ss[:len(P)]])
                    wid = w * press * (0.72 + 0.62 * side) * (1 + 0.16 * wv)
                    if not closed and taper:
                        sl = ss[:len(P)]
                        tp = np.minimum(1, np.minimum(sl, L - sl) / min(18, L / 3)) ** 0.7
                        wid = wid * (0.15 + 0.85 * tp)
                    a = P + N * (wid / 2)[:, None]
                    b = P - N * (wid / 2)[:, None]
                    q = skia.Path()
                    if closed:
                        q.addPoly([skia.Point(*v) for v in a], True)
                        q.addPoly([skia.Point(*v) for v in b[::-1]], True)
                        q.setFillType(skia.PathFillType.kEvenOdd)
                    else:
                        q.addPoly([skia.Point(*v) for v in np.vstack([a, b[::-1]])], True)
                    out.append(q)
            if not pm.nextContour():
                break
        return out


class Painter:
    def __init__(self, canvas, t=0.0):
        self.c = canvas
        self.t = t
        self.brush = Brush()
        self.rims = []   # контровой свет: рисуется после ночи (screen)
        self.cat_sil = None

    def rim(self, path, toward, w, color, a=200, region=None):
        """Полоса света по краю фигуры со стороны источника: фигура минус она же, сдвинутая от света."""
        if isinstance(path, str):
            path = parse(path)
        r = skia.Op(path, moved(path, -toward[0] * w, -toward[1] * w), skia.PathOp.kDifference_PathOp)
        if r is not None and region is not None:
            r = skia.Op(r, region, skia.PathOp.kIntersect_PathOp)
        if r is not None:
            self.rims.append((r, color, a))

    def ink(self, path, w=4.6, light=None, color=INK, taper=True, a=255):
        p = paint(color, a)
        for q in self.brush.stroke(path, w, light, taper):
            self.c.drawPath(q, p)

    def line(self, d_or_path, w=3.4, color=INK, a=255):
        path = parse(d_or_path) if isinstance(d_or_path, str) else d_or_path
        self.ink(path, w, color=color, taper=True, a=a)

    def shape(self, path, fill, ink=4.6, light=None, off=13, shade=0.74, shadow=True, shader=None, a=255):
        if isinstance(path, str):
            path = parse(path)
        self.c.drawPath(path, paint(fill, a, shader=shader))
        if shadow:
            lx, ly = light or self.brush.light
            lit = moved(path, lx * off, ly * off)
            sh = skia.Op(path, lit, skia.PathOp.kDifference_PathOp)
            if sh is not None:
                self.c.drawPath(sh, paint(shade_of(fill, shade), a))
        if ink:
            self.ink(path, ink, light)
        return path

    def clip(self, path):
        self.c.save()
        self.c.clipPath(path, skia.ClipOp.kIntersect, True)

    def unclip(self):
        self.c.restore()

# ---------------------------------------------------------------- сцена


def seven_seg(pp, x, y, text, h, color):
    """Цифры часов рисует код: семисегментный индикатор."""
    segs = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc',
            '7': 'abc', '8': 'abcdefg', '9': 'abcdfg'}
    w, t = h * 0.52, h * 0.13
    out = skia.Path()
    for ch in text:
        if ch == '1':
            x -= w * 0.45
        if ch == ':':
            out.addPath(ell(x + t, y + h * 0.3, t * 0.55))
            out.addPath(ell(x + t, y + h * 0.7, t * 0.55))
            x += t * 3
            continue
        S = {'a': (x + t, y, w - 2 * t, t), 'g': (x + t, y + h / 2 - t / 2, w - 2 * t, t), 'd': (x + t, y + h - t, w - 2 * t, t),
             'f': (x, y + t * 0.6, t, h / 2 - t * 1.1), 'b': (x + w - t, y + t * 0.6, t, h / 2 - t * 1.1),
             'e': (x, y + h / 2 + t * 0.5, t, h / 2 - t * 1.1), 'c': (x + w - t, y + h / 2 + t * 0.5, t, h / 2 - t * 1.1)}
        for k in segs[ch]:
            sx, sy, sw, sh = S[k]
            out.addPath(rect(sx, sy, sw, sh, t * 0.45))
        x += w + t * 1.6
    return out


def draw(canvas, t=0.0):
    pp = Painter(canvas, t)
    c = canvas
    c.clear(C('#000000'))
    c.save()
    c.scale(W / 1020, W / 1020)
    c.translate(-30, -100)
    rng = np.random.default_rng(11)

    # ---- стена: обои кодом
    c.drawRect(skia.Rect.MakeXYWH(0, 0, 1080, 1520), paint('#c9b18a'))
    for x in range(0, 1080, 80):
        c.drawRect(skia.Rect.MakeXYWH(x, 60, 26, 1460), paint('#bea47c'))
        for y in range(60, 1500, 120):
            yy = y + (40 if (x // 80) % 2 else 0)
            fl = union(ell(x + 53, yy + 30, 5), ell(x + 47, yy + 25, 3), ell(x + 59, yy + 25, 3), ell(x + 47, yy + 35, 3), ell(x + 59, yy + 35, 3))
            c.drawPath(fl, paint('#a98d66', 200))
            c.drawPath(parse(f'M{x+53} {yy+38} q-4 14 2 26'), paint('#a98d66', 200, style='stroke', sw=2))
    # тень под потолком и за диваном (мягкий градиент — не тень фигуры)
    c.drawRect(skia.Rect.MakeXYWH(0, 60, 1080, 120), paint('#000000', shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, 60), skia.Point(0, 180)], [C('#5a4630', 90), C('#5a4630', 0)])))
    c.drawRect(skia.Rect.MakeXYWH(0, 0, 1080, 60), paint('#a38f6e'))
    pp.line('M0 60 H1080', 3.5)

    # ---- полка
    pp.brush.light = (0.55, -0.83)
    for y in (330, 560):
        pp.shape(rect(40, y, 300, 22), '#8a6447', off=8)
    books = [(62, 230, 34, 100, '#4f6d8f'), (96, 245, 28, 85, '#b2553f'), (124, 222, 38, 108, '#d9b55b'),
             (270, 250, 44, 80, '#e8e1d2'), (62, 470, 40, 90, '#8c5f8a'), (102, 455, 30, 105, '#4f6d8f')]
    for x, y, w, h, col in books:
        pp.shape(rect(x, y, w, h, 3), col, off=9)
        pp.line(f'M{x+6} {y+14} h{w-12}', 2.2, color=(0, 0, 0), a=110)
        pp.line(f'M{x+6} {y+h-16} h{w-12}', 2.2, color=(0, 0, 0), a=110)
    pp.shape(rot(rect(168, 262, 96, 30, 3), -8, 216, 277), '#6f8e5a', off=8)
    pp.shape('M262 560 q-6 -60 14 -80 q20 20 14 80 z', '#7aa25f', off=8)
    # свисающее растение
    pp.line('M290 330 q-10 40 -2 80 q8 40 -4 90', 3.6, color='#3f5e33')
    for cx, cy, a in ((282, 372, -30), (300, 420, 30), (280, 468, -25), (296, 512, 20)):
        pp.shape(rot(ell(cx, cy, 17, 10), a, cx, cy), '#6f9a55', ink=3.4, off=5)
    pp.shape('M268 300 q22 -40 44 0 l-6 32 h-32 z', '#b8694a', off=8)
    pp.shape('M266 296 q24 -18 48 0 q-24 10 -48 0 z', '#4c3a2c', ink=2.5, shadow=False)
    # часы
    pp.shape(rect(180, 490, 140, 68, 10), '#2a2a30', off=7)
    c.drawPath(rect(192, 500, 116, 48, 6), paint('#120f12'))

    # ---- окно
    c.drawRect(skia.Rect.MakeXYWH(610, 150, 420, 590), paint('#000000', shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, 150), skia.Point(0, 740)], [C('#0d1230'), C('#2c3a72')])))
    for _ in range(40):
        sx, sy = 630 + rng.random() * 380, 170 + rng.random() * 300
        c.drawPath(ell(sx, sy, 0.8 + rng.random() * 1.4), paint('#e8ecff', int(120 + 120 * rng.random())))
    for bx, by, bw, bh in ((630, 470, 190, 270), (840, 520, 180, 220), (760, 420, 70, 60)):
        c.drawRect(skia.Rect.MakeXYWH(bx, by, bw, bh), paint('#121732'))
    lit = []
    for bx, by, bw, bh in ((630, 470, 190, 270), (840, 520, 180, 220)):
        for yy in range(by + 22, by + bh - 20, 44):
            for xx in range(bx + 14, bx + bw - 20, 36):
                lit.append((xx, yy, rng.random() < 0.33))
    for xx, yy, on in lit:
        if not on:
            c.drawRect(skia.Rect.MakeXYWH(xx, yy, 20, 28), paint('#1c2242'))
    win_frame = skia.Path()
    win_frame.addPath(rect(600, 140, 440, 610))
    win_frame.addPath(rect(628, 168, 384, 554))
    win_frame.setFillType(skia.PathFillType.kEvenOdd)
    pp.shape(win_frame, '#ece5d6', off=10)
    pp.shape(rect(806, 168, 24, 554), '#ece5d6', off=8)
    pp.shape(rect(590, 740, 460, 34), '#ece5d6', off=8)
    # шторы со складками
    for d in ('M560 90 q30 300 0 690 h70 q26 -300 6 -690 z', 'M1080 90 v690 h-56 q-24 -330 -4 -690 z'):
        cp = parse(d)
        pp.shape(cp, '#d8b98e', ink=0, off=16)
        pp.clip(cp)
        for k in range(0, 1080, 60):
            for j in range(90, 790, 90):
                c.drawPath(ell(k + 20 + (j // 90 % 2) * 26, j + 22, 6), paint('#c28f7c', 210))
        pp.unclip()
        pp.ink(cp, 4.8)
    pp.line('M584 120 q-6 300 8 640', 2.6, a=150)
    pp.line('M1046 120 q-10 320 2 640', 2.6, a=150)
    c.drawRect(skia.Rect.MakeXYWH(540, 86, 540, 9), paint(INK))

    # ---- пол
    c.drawRect(skia.Rect.MakeXYWH(0, 1500, 1080, 520), paint('#8a6447'))
    r2 = np.random.default_rng(5)
    for row, y in enumerate(range(1500, 2020, 70)):
        x = -r2.integers(0, 300)
        while x < 1080:
            ln = int(r2.integers(260, 470))
            tone = r2.uniform(0.88, 1.08)
            col = tuple(min(255, v * tone) for v in rgbt('#8a6447'))
            c.drawRect(skia.Rect.MakeXYWH(x, y, ln, 70), paint(col))
            for g in range(3):  # волокно
                gy = y + 14 + g * 18 + r2.uniform(-4, 4)
                ph = r2.uniform(0, 6)
                c.drawPath(parse(f'M{x+8} {gy} C {x+ln*0.3} {gy+6*math.sin(ph)} {x+ln*0.6} {gy-6*math.cos(ph)} {x+ln-8} {gy}'),
                           paint('#6b4a33', 90, style='stroke', sw=1.6))
            pp.line(f'M{x} {y+2} V{y+68}', 2.6, color='#4e3524', a=220)
            x += ln
        pp.line(f'M0 {y+69} H1080', 2.6, color='#4e3524', a=220)
    pp.shape(rect(-10, 1490, 1100, 26), '#6b4a33', off=8)
    # ковёр
    rug = parse('M520 1760 l520 -20 l40 170 h-600 z')
    pp.shape(rug, '#8c3f3a', off=14, ink=0)
    pp.clip(rug)
    for k in range(-4, 30):
        c.drawPath(parse(f'M{500+k*24} 1740 l60 200'), paint('#6f2f2c', 120, style='stroke', sw=5))
    pp.unclip()
    pp.ink(rug, 4.8)
    pp.line('M552 1782 l470 -18 l30 120 h-520 z', 4.5, color='#d6a05a')
    for k in range(0, 22):
        pp.line(f'M{526+k*24} {1760-k*0.9} l-3 -16', 2.2, color='#d6c39a')
    # тапки
    for x0, y0, a in ((250, 1640, -14), (340, 1660, 8)):
        sole = rot(ell(x0, y0, 62, 24), a, x0, y0)
        pp.shape(sole, '#43506e', off=6)
        top = rot(parse(f'M{x0-10} {y0-20} q40 -26 70 0 q-6 22 -36 24 q-30 0 -34 -24 z'), a, x0, y0)
        pp.shape(top, '#7f93b8', off=9)
        pp.shape(rot(ell(x0 + 18, y0 - 14, 14, 8), a, x0, y0), '#e5e0d4', ink=3, off=4)

    # ---- диван
    sofa_parts = ['M150 1010 q0 -40 40 -40 h790 q40 0 40 40 v300 h-870 z', 'M110 1240 h900 v190 h-900 z',
                  'M70 1110 q0 -50 60 -50 h80 q50 0 50 50 v340 h-190 z', 'M960 1110 q0 -40 50 -40 h40 q30 0 30 40 v340 h-120 z']
    for x in (96, 1000):
        pp.shape(rect(x, 1450, 30, 40), '#3b2a20', off=6)
    for d in sofa_parts:
        sp = parse(d)
        pp.shape(sp, '#8b5d4c', ink=0, off=18)
        pp.clip(sp)
        for xx in range(0, 1080, 46):
            for yy in range(960, 1460, 46):
                c.drawPath(ell(xx + 11, yy + 11, 3), paint('#7a4f40'))
                c.drawPath(ell(xx + 34, yy + 34, 3), paint('#7a4f40'))
        pp.unclip()
        pp.ink(sp, 5)
    pp.line('M560 985 q0 120 -4 250', 3, a=140)   # шов спинки
    pp.shape('M215 1030 q90 -40 170 10 q20 90 -10 160 q-90 30 -170 -20 q-20 -80 10 -150 z', '#e7ddc8', off=16)
    pp.line('M250 1080 q50 -10 90 10', 3)

    # ---- Дима (свет — от телефона снизу-спереди)
    t_ = t
    pp.brush.light = (0.2, 1.0)
    pp.shape('M330 990 q110 -60 230 0 q-30 40 -115 40 q-85 0 -115 -40 z', '#c8962f', off=12)
    torso = pp.shape('M285 1030 q30 -50 160 -50 q130 0 165 50 l40 260 h-410 z', '#d9a83c', off=26, light=(-0.4, -1))
    pp.line('M350 1100 q14 60 6 150', 3, a=150)
    pp.line('M560 1100 q-10 60 0 150', 3, a=150)
    pp.line('M418 1000 v70', 3.2)
    pp.line('M474 1000 v76', 3.2)
    pp.shape(rect(412, 1068, 12, 16, 3), '#ece5d6', ink=2.6, shadow=False)
    pp.shape(rect(468, 1074, 12, 16, 3), '#ece5d6', ink=2.6, shadow=False)
    pp.shape('M410 950 h70 v45 q-35 20 -70 0 z', '#e6b593', off=14, light=(0, 1))
    # голова
    ear = pp.shape(ell(342, 860, 20, 30), '#f0c4a2', off=8)
    pp.line('M346 845 q-10 14 2 30', 2.6)
    head = parse('M352 790 C 350 720, 520 705, 548 785 C 568 850, 552 925, 505 962 C 472 988, 405 988, 378 952 C 350 915, 352 850, 352 790 Z')
    pp.shape(head, '#f0c4a2', off=26, light=(-0.55, 0.85), shade=0.8)
    pp.clip(head)  # щетина процедурно
    rs = np.random.default_rng(2)
    for _ in range(170):
        sx, sy = 372 + rs.random() * 190, 915 + rs.random() * 70
        if (sx - 455) ** 2 / 95 ** 2 + (sy - 905) ** 2 / 70 ** 2 > 1 and sy > 925:
            c.drawPath(ell(sx, sy, 1.3 + rs.random()), paint('#8e6d5c', 170))
    pp.unclip()
    # мешки
    for d in ('M378 876 q40 26 80 0', 'M464 874 q38 24 76 0'):
        c.drawPath(parse(d), paint('#b07e74', 120, style='stroke', sw=10, blur=2))
        pp.line(d.replace('q40 26', 'q40 20').replace('q38 24', 'q38 18'), 2.4, color='#7a5048', a=200)
    # глаза + моргание
    b = max(_blink(t_, 0.9), _blink(t_, 2.5))
    eyes = [(418, 842, 44, 40, 432, 860), (502, 840, 42, 39, 512, 858)]
    for ex, ey, rx, ry, px, py in eyes:
        e = ell(ex, ey, rx, ry)
        c.drawPath(e, paint('#fbfaf6'))
        pp.clip(e)
        c.drawPath(ell(px, py, 7.5), paint('#15131a'))
        c.drawPath(ell(px - 2.5, py - 2.5, 2.2), paint('#ffffff', 220))
        c.drawRect(skia.Rect.MakeXYWH(ex - 50, ey - 55, 100, 51 + (ry * 2 + 2) * b), paint('#e6b593'))
        pp.unclip()
        lidy = ey - 4 + (ry * 2 - 2) * b * 0.98
        pp.line(f'M{ex-rx+2} {lidy} q{rx} {-6 + 6*b} {rx*2-4} 0', 5.4)
        pp.ink(e, 4.6)
    pp.line('M382 784 q30 -10 62 4', 7.5)
    pp.line('M476 786 q30 -12 60 0', 7.5)
    pp.line('M462 868 q-6 30 6 38 q10 4 16 -4', 3.4)
    pp.line('M440 934 q22 -6 46 2', 4.2)
    # волосы
    hair = parse('M338 850 C 318 780, 330 712, 392 690 C 396 660, 440 646, 468 668 C 492 640, 548 650, 552 690 '
                 'C 590 688, 600 740, 574 786 L 556 760 C 548 738, 520 724, 492 736 C 470 716, 430 720, 412 742 '
                 'C 390 736, 368 760, 366 792 C 360 812, 352 832, 338 850 Z')
    spikes = parse('M392 690 l-20 -30 l38 18 z M468 668 l4 -36 l18 30 z M552 690 l30 -24 l-6 36 z M338 850 l-24 -18 l20 -8 z '
                   'M420 655 l-6 -30 l26 22 z M574 760 l26 6 l-22 18 z')
    hair = union(hair, spikes)
    pp.shape(hair, '#4a3324', off=16, light=(0.3, 1), shade=0.7)
    pp.rim(hair, (0.6, -0.8), 7, '#7f95d8', 150)   # контур волос светом окна
    for d in ('M420 700 q20 -10 40 2', 'M500 690 q24 -6 38 10', 'M372 740 q10 -26 30 -34', 'M540 720 q14 10 18 30'):
        pp.line(d, 2.8, color='#22160e')
    for d in ('M398 700 q22 -14 46 -6', 'M500 676 q20 -4 34 6'):
        pp.line(d, 4, color='#7a5a44', a=170)       # блик на прядях
    # руки и телефон
    pp.brush.light = (0.0, -1.0)
    pp.shape('M300 1040 q-40 80 -20 170 q10 30 50 24 q40 -10 90 -90 l-34 -26 q-40 50 -58 46 q-6 -50 10 -110 z', '#d9a83c', off=16, light=(1, -0.3))
    pp.shape('M598 1040 q40 80 20 170 q-10 30 -50 24 q-40 -10 -90 -90 l34 -26 q40 50 58 46 q6 -50 -10 -110 z', '#d9a83c', off=16, light=(-1, -0.3))
    pp.line('M330 1180 q24 10 48 -10', 3)
    pp.line('M568 1180 q-24 10 -48 -10', 3)
    phone = rect(402, 1020, 92, 150, 16)
    pp.shape(phone, '#141317', off=6, light=(-1, 0))
    pp.line('M407 1040 v110', 2.2, color='#5a6a9a', a=200)     # блик ребра от окна
    pp.shape(rect(412, 1030, 40, 40, 10), '#25242b', ink=2.4, shadow=False)
    for lx_, ly_ in ((423, 1041), (441, 1050), (423, 1059)):
        c.drawPath(ell(lx_, ly_, 7), paint('#0b0b0d'))
        pp.ink(ell(lx_, ly_, 7), 2.2, color='#55555f')
        c.drawPath(ell(lx_ - 2, ly_ - 2, 1.8), paint('#8fa6e0', 200))
    c.drawPath(ell(443, 1036, 2.6), paint('#d8d2b8'))
    pp.shape('M392 1120 q-6 -40 20 -44 q14 0 14 20 v40 q-14 20 -34 -16 z', '#f0c4a2', off=8, light=(1, -0.5))
    pp.shape('M504 1120 q6 -40 -20 -44 q-14 0 -14 20 v40 q14 20 34 -16 z', '#f0c4a2', off=8, light=(-1, -0.5))
    s = max(_swipe(t_, 0.4), _swipe(t_, 1.7))
    thumb = moved(parse('M478 1052 q8 -14 20 -6 q8 8 -4 22 q-10 4 -16 -16 z'), -4 * s, -16 * s)
    pp.shape(thumb, '#f0c4a2', ink=3.8, off=5, light=(-1, 0))

    # ---- плед: тартан кодом
    pp.brush.light = (0.55, -0.83)
    plaid = parse('M250 1235 q120 -40 260 -20 q260 20 470 0 q40 0 50 40 l10 180 q-420 40 -800 10 q-40 -100 10 -210 z')
    c.drawPath(plaid, paint('#9fb98a'))
    pp.clip(plaid)
    c.save()
    c.rotate(-6, 600, 1300)
    for x in range(100, 1200, 64):
        c.drawRect(skia.Rect.MakeXYWH(x, 1100, 30, 400), paint('#5f7f50', 120))
        c.drawRect(skia.Rect.MakeXYWH(x + 40, 1100, 3, 400), paint('#e9dcae', 120))
    for y in range(1150, 1500, 64):
        c.drawRect(skia.Rect.MakeXYWH(100, y, 1100, 30), paint('#5f7f50', 120))
        c.drawRect(skia.Rect.MakeXYWH(100, y + 44, 1100, 3), paint('#b4553e', 110))
    c.restore()
    for d in ('M260 1300 q300 30 760 -10', 'M320 1380 q260 20 660 -6'):  # складки: тень + блик
        c.drawPath(parse(d), paint('#26371f', 90, style='stroke', sw=16, blur=6))
        c.drawPath(moved(parse(d), 0, -12), paint('#ffffff', 40, style='stroke', sw=8, blur=4))
    c.drawPath(skia.Op(plaid, moved(plaid, 0, -22), skia.PathOp.kDifference_PathOp), paint('#1f2c18', 80))
    pp.unclip()
    pp.ink(plaid, 5.2)
    pp.line('M262 1300 q300 30 760 -10', 3, color='#2c3d24', a=170)
    pp.line('M320 1380 q260 20 660 -6', 3, color='#2c3d24', a=170)

    # ---- кот (свет — огонёк справа)
    pp.brush.light = (0.9, -0.45)
    tail = parse('M915 1300 q80 10 92 -60 q8 -50 -30 -60 q-30 -4 -32 22 q0 20 22 20')
    tp = paint('#000000', style='stroke', sw=30)
    tail_fill = skia.Path()
    tp.getFillPath(tail, tail_fill)
    tail_fill = skia.Op(tail_fill, tail_fill, skia.PathOp.kUnion_PathOp)
    pp.shape(tail_fill, '#25232d', off=8, shade=0.6)
    body = fur(832, 1252, 92, 80, 34, 9, 4)
    pp.shape(body, '#25232d', off=16, shade=0.62)
    pp.shape('M790 1222 q40 -18 84 0 q-6 54 -42 74 q-36 -20 -42 -74 z', '#34313f', ink=0, shadow=False)
    for px in (790, 874):
        pp.shape(fur(px, 1326, 28, 16, 12, 3, px), '#25232d', off=6, shade=0.62)
        c.drawPath(ell(px, 1331, 11, 7), paint('#f08a5a'))
        for k in (-14, 0, 14):
            c.drawPath(ell(px + k, 1319, 4, 3.2), paint('#f08a5a'))
    # уши: левое (от зрителя) загнуто
    pp.shape('M752 1084 q-26 -34 0 -58 q34 -10 50 24 z', '#25232d', off=8, shade=0.6)
    pp.shape('M760 1072 q0 -24 22 -26 q10 10 8 28 z', '#c98274', ink=2.4, shadow=False)
    pp.line('M752 1050 q18 -4 34 8', 2.6, color='#0d0c10')
    pp.shape('M884 1080 l18 -86 l46 82 z', '#25232d', off=8, shade=0.6)
    pp.shape('M898 1068 l8 -50 l26 48 z', '#c98274', ink=2.4, shadow=False)
    head_c = fur(832, 1135, 100, 82, 40, 11, 9, skip=(4.3, 5.2))
    pp.shape(head_c, '#25232d', off=16, shade=0.62)
    # отсвет огонька: силуэт кота (без PathOps — у меха зубцы с самопересечениями), свет — градиентом
    sil = skia.Path()
    for part in (head_c, body, tail_fill, parse('M884 1080 l18 -86 l46 82 z')):
        sil.addPath(part)
    pp.cat_sil = sil   # отсвет огонька по шерсти справа
    cb = _blink(t_, 1.6, 0.24)
    for ex in (795, 868):
        e = ell(ex, 1128, 27)
        c.drawPath(e, paint('#a5d64c'))
        pp.clip(e)
        c.drawPath(ell(ex, 1140, 27, 14), paint('#7aa834'))     # нижняя тень радужки
        c.drawPath(ell(ex + 1, 1130, 9, 16), paint('#0f0e12'))
        c.drawPath(ell(ex - 7, 1119, 5.5), paint('#ffffff'))
        c.drawRect(skia.Rect.MakeXYWH(ex - 30, 1098, 60, 58 * cb), paint('#25232d'))
        pp.unclip()
        pp.ink(e, 3.8)
        if cb > 0.6:
            pp.line(f'M{ex-24} {1128} q24 12 48 0', 3.6)
    c.drawPath(parse('M826 1160 h12 l-6 8 z'), paint('#e69a8a'))
    pp.line('M832 1168 q-8 10 -16 4', 3, color='#0d0c10')
    pp.line('M832 1168 q8 10 16 4', 3, color='#0d0c10')
    for d in ('M752 1158 l26 -4', 'M754 1172 l24 0', 'M912 1158 l-26 -4', 'M910 1172 l-24 0'):
        pp.line(d, 5.5, color='#f28a2e')
    for d in ('M770 1164 l-64 -8', 'M770 1170 l-62 10', 'M894 1164 l64 -8', 'M894 1170 l62 10'):
        pp.line(d, 2.0, color='#d8d2e2', a=200)
    c.restore()
    return pp


HANDS = ('M392 1120 q-6 -40 20 -44 q14 0 14 20 v40 q-14 20 -34 -16 z', 'M504 1120 q6 -40 -20 -44 q-14 0 -14 20 v40 q14 20 34 -16 z')
THUMB = 'M478 1052 q8 -14 20 -6 q8 8 -4 22 q-10 4 -16 -16 z'


def _blink(t, at, dur=0.2):
    x = (t - at) / dur
    return 0.0 if x < 0 or x > 1 else math.sin(math.pi * x)


def _swipe(t, at):
    x = (t - at) / 0.35
    return 0.0 if x < 0 or x > 1 else math.sin(math.pi * x)


def _sm(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


def light_pass(canvas, t, flame_path, rims=(), cat_sil=None):
    c = canvas
    c.save()
    c.scale(W / 1020, W / 1020)
    c.translate(-30, -100)
    full = skia.Rect.MakeXYWH(0, 0, 1080, 2000)
    # ночь: multiply, сверху темнее, по краям виньетка
    c.drawRect(full, paint('#000000', blend=skia.BlendMode.kMultiply, shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, 100), skia.Point(0, 1950)], [C('#5d67aa'), C('#7882c2'), C('#5a63a3')], [0, 0.55, 1])))
    c.drawRect(full, paint('#000000', blend=skia.BlendMode.kMultiply, shader=skia.GradientShader.MakeRadial(
        skia.Point(560, 1050), 1150, [C('#ffffff'), C('#ffffff'), C('#8890c0')], [0, 0.55, 1])))
    # лунный свет из окна на стену/диван (мягкая трапеция)
    c.drawPath(poly([(630, 760), (1010, 760), (900, 1250), (420, 1250)]),
               paint('#9fb2ff', 40, blend=skia.BlendMode.kScreen, blur=40))
    # свет экрана: на лицо и руки, плюс общий ореол; мерцает, вспыхивает после свайпа
    flash = max(_sm(1 - abs(t - 0.75) / 0.2), _sm(1 - abs(t - 2.05) / 0.2))
    k = 0.85 + 0.07 * math.sin(t * 23) * math.sin(t * 7.3) + 0.3 * flash
    c.drawRect(full, paint('#000000', blend=skia.BlendMode.kScreen, shader=skia.GradientShader.MakeRadial(
        skia.Point(450, 960), 260, [C('#a8c8ff', 115 * k), C('#6f93d8', 45 * k), C('#3b4f9a', 0)], [0, 0.45, 1])))
    face = parse('M352 790 C 350 720, 520 705, 548 785 C 568 850, 552 925, 505 962 C 472 988, 405 988, 378 952 C 350 915, 352 850, 352 790 Z')
    c.save()
    c.clipPath(union(face, ell(342, 860, 20, 30), parse(HANDS[0]), parse(HANDS[1]), parse(THUMB)), skia.ClipOp.kIntersect, True)
    c.drawRect(full, paint('#000000', blend=skia.BlendMode.kScreen, shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, 1040), skia.Point(0, 760)], [C('#bcd2ff', 70 * k), C('#7f9be0', 15 * k)])))
    c.restore()
    # огонёк: тёплый ореол + блик на шерсти кота справа
    fk = 0.9 + 0.1 * math.sin(t * 13.1)
    c.drawRect(full, paint('#000000', blend=skia.BlendMode.kScreen, shader=skia.GradientShader.MakeRadial(
        skia.Point(970, 1180), 170, [C('#ffb35c', 170 * fk), C('#ff7a1a', 50 * fk), C('#ff7a1a', 0)], [0, 0.35, 1])))
    if cat_sil is not None:
        c.save()
        c.clipPath(cat_sil, skia.ClipOp.kIntersect, True)
        c.drawRect(full, paint('#000000', blend=skia.BlendMode.kScreen, shader=skia.GradientShader.MakeRadial(
            skia.Point(985, 1190), 150, [C('#ff9a3c', 190 * fk), C('#ff7a1a', 60 * fk), C('#ff7a1a', 0)], [0, 0.45, 1])))
        c.restore()
    for r, col, a in rims:
        c.drawPath(r, paint(col, a, blend=skia.BlendMode.kScreen, blur=1.5))
    # светящееся: луна, окна дома, часы, огонёк
    c.drawPath(ell(930, 250, 95), paint('#fff3c8', 80, blur=30))
    c.drawPath(ell(930, 250, 36), paint('#f6edc6'))
    for cx, cy, r in ((918, 242, 7), (942, 262, 5), (934, 232, 3.5)):
        c.drawPath(ell(cx, cy, r), paint('#ddd09c'))
    rng = np.random.default_rng(11)
    for _ in range(40):
        rng.random(); rng.random(); rng.random(); rng.random()
    for bx, by, bw, bh in ((630, 470, 190, 270), (840, 520, 180, 220)):
        for yy in range(by + 22, by + bh - 20, 44):
            for xx in range(bx + 14, bx + bw - 20, 36):
                if rng.random() < 0.33:
                    c.drawRect(skia.Rect.MakeXYWH(xx - 3, yy - 3, 26, 34), paint('#f2b85b', 70, blur=6))
                    c.drawRect(skia.Rect.MakeXYWH(xx, yy, 20, 28), paint('#f2c86b'))
    digits = seven_seg(None, 203, 507, '01:47', 34, None)
    c.drawPath(digits, paint('#ff3a2a', 160, blur=6))
    c.drawPath(digits, paint('#ff5a40'))
    c.drawPath(flame_path, paint('#ff9b2f', 120, blur=14))
    c.drawPath(flame_path, paint('#ff9b2f'))
    core = warp(flame_path, lambda x, y: (968 + (x - 968) * 0.55, 1212 + (y - 1212) * 0.62))
    c.drawPath(core, paint('#ffe07a'))
    for q in Brush(light=(0.9, -0.45)).stroke(flame_path, 3.4):
        c.drawPath(q, paint(INK))
    c.restore()


def flame(t):
    base = parse('M938 1182 q-30 -18 -18 -52 q8 -20 2 -40 q22 12 26 34 q8 -16 4 -32 q26 22 18 56 q-6 26 -32 34 z')
    base.offset(30, 30)
    bx, by, h = 968, 1214, 95.0

    def f(x, y):
        u = min(1.0, max(0.0, (by - y) / h))
        dx = (u ** 1.4) * (9 * math.sin(t * 9.0 - u * 3.0) + 4 * math.sin(t * 15.7 - u * 5))
        st = 1 + 0.08 * math.sin(t * 11.3)
        return x + dx, by - (by - y) * st
    return warp(base, f)


def frame(t):
    surf = skia.Surface(W, H)
    with surf as canvas:
        pp = draw(canvas, t)
        light_pass(canvas, t, flame(t), pp.rims, pp.cat_sil)
    img = surf.toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3].astype(np.int16)
    # зерно: 12 раз в секунду, монохромное
    g = np.random.default_rng(int(t * 12)).normal(0, 3.4, (H, W, 1))
    img = np.clip(img + g, 0, 255).astype(np.uint8)
    return img


def save_png(arr, path):
    img = skia.Image.fromarray(np.dstack([arr, np.full(arr.shape[:2], 255, np.uint8)]), skia.kRGBA_8888_ColorType)
    img.save(str(path), skia.kPNG)


if __name__ == '__main__':
    t0 = time.time()
    a = frame(0.0)
    t1 = time.time()
    save_png(a, HERE / 'still.png')
    print(f'кадр: {1000*(t1-t0):.0f} мс (рисование + свет + зерно), png {1000*(time.time()-t1):.0f} мс')
    # что сколько стоит
    s = skia.Surface(W, H)
    with s as cv:
        q0 = time.time(); pp = draw(cv, 0.0); q1 = time.time(); light_pass(cv, 0.0, flame(0.0), pp.rims, pp.cat_sil); q2 = time.time()
    print(f'  сцена {1000*(q1-q0):.0f} мс, свет {1000*(q2-q1):.0f} мс')
    if '--anim' in sys.argv:
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt',
                               'rgb24',
                               '-s', f'{W}x{H}', '-r', '30', '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                               '-crf', '18', str(HERE / 'anim.mp4')], stdin=subprocess.PIPE)
        a0 = time.time()
        for f in range(90):
            ff.stdin.write(frame(f / 30).tobytes())
        ff.stdin.close()
        ff.wait()
        print(f'anim.mp4: 90 кадров за {time.time()-a0:.1f} с')
