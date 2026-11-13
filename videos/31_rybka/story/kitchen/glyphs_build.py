"""Один раз: контуры букв Caveat 600 (OFL) для трёх строк списка s11 + «ход пера» каждой буквы (скелет растра, обход
от левого конца) -> glyphs.json. Буквы в сцене проявляются маской по ходу пера, а не шторкой."""
import json
import math
import os
import sys

import numpy as np
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from skimage.draw import polygon as skpoly
from skimage.morphology import skeletonize
from scipy import ndimage

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "assets", "fonts", "Caveat-Variable.ttf")
LINES = ["хлеб", "оплатить свет", "маме позвонить", "покормить кота"]
R = 0.25   # пикселей растра на единицу шрифта (upm 1000 -> 250 px)


def contours(gs, name):
    rp = DecomposingRecordingPen(gs)
    gs[name].draw(rp)
    out, cur = [], []
    pos = None
    for op, args in rp.value:
        if op == "moveTo":
            cur = [args[0]]
            pos = args[0]
        elif op == "lineTo":
            cur.append(args[0]); pos = args[0]
        elif op == "qCurveTo":
            pts = [pos] + list(args)
            # разбить на квадратичные сегменты с неявными точками
            ctrl = pts[1:-1]
            on = [pts[0]]
            segs = []
            p0 = pts[0]
            for i, c in enumerate(ctrl):
                p1 = pts[-1] if i == len(ctrl) - 1 else ((c[0] + ctrl[i + 1][0]) / 2, (c[1] + ctrl[i + 1][1]) / 2)
                for t in np.linspace(0, 1, 8)[1:]:
                    cur.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]))
                p0 = p1
            pos = pts[-1]
        elif op == "curveTo":
            p0 = pos
            c1, c2, p1 = args
            for t in np.linspace(0, 1, 10)[1:]:
                cur.append(tuple((1 - t) ** 3 * np.array(p0) + 3 * (1 - t) ** 2 * t * np.array(c1) + 3 * (1 - t) * t * t * np.array(c2) + t ** 3 * np.array(p1)))
            pos = p1
        elif op in ("closePath", "endPath"):
            if cur:
                out.append(cur)
            cur = []
    return out


def stroke_path(cs, bounds):
    x0, y0, x1, y1 = bounds
    pad = 6
    Wd, Hd = int((x1 - x0) * R) + 2 * pad, int((y1 - y0) * R) + 2 * pad
    m = np.zeros((Hd, Wd), bool)
    for c in cs:
        c = np.array(c)
        rr, cc = skpoly((y1 - c[:, 1]) * R + pad, (c[:, 0] - x0) * R + pad, (Hd, Wd))
        mm = np.zeros_like(m); mm[rr, cc] = True
        m ^= mm
    dist = ndimage.distance_transform_edt(m)
    width = float(dist.max() * 2 + 2) / R
    sk = skeletonize(m)
    ys, xs = np.nonzero(sk)
    pts = set(zip(xs.tolist(), ys.tolist()))

    def nb(p):
        return [(p[0] + dx, p[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy) and (p[0] + dx, p[1] + dy) in pts]
    ends = [p for p in pts if len(nb(p)) == 1]
    order = []
    left = set(pts)
    cand = ends if ends else list(pts)
    cur = min(cand, key=lambda p: (p[0] - 0.3 * p[1]))
    strokes = []
    stroke = [cur]
    left.discard(cur)
    d = None
    while left:
        ns = [q for q in nb(cur) if q in left]
        if ns:
            if d is not None:
                ns.sort(key=lambda q: -((q[0] - cur[0]) * d[0] + (q[1] - cur[1]) * d[1]))
            q = ns[0]
            d = (q[0] - cur[0], q[1] - cur[1])
            cur = q
            stroke.append(cur)
            left.discard(cur)
        else:
            strokes.append(stroke)
            le = [p for p in left if len([q for q in nb(p) if q in left]) <= 1] or list(left)
            cur = min(le, key=lambda p: (p[0] - cur[0]) ** 2 + (p[1] - cur[1]) ** 2)
            stroke = [cur]
            left.discard(cur)
            d = None
    strokes.append(stroke)
    # отбросить крошки, проредить, перевести в единицы шрифта (y вверх)
    out = []
    for st in strokes:
        if len(st) < 3:
            continue
        st = st[::2] + [st[-1]]
        out.append([[round((x - pad) / R + x0, 1), round(y1 - (y - pad) / R, 1)] for x, y in st])
    return out, width


def main():
    f = TTFont(SRC)
    f = instancer.instantiateVariableFont(f, {"wght": 600})
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    res = {"upm": f["head"].unitsPerEm, "lines": []}
    for text in LINES:
        gl = []
        for ch in text:
            name = cmap[ord(ch)]
            adv = hmtx[name][0]
            bp = BoundsPen(gs)
            gs[name].draw(bp)
            sp = SVGPathPen(gs)
            gs[name].draw(sp)
            g = {"ch": ch, "adv": adv, "bounds": list(bp.bounds) if bp.bounds else None, "d": sp.getCommands()}
            if bp.bounds:
                g["strokes"], g["width"] = stroke_path(contours(gs, name), bp.bounds)
            gl.append(g)
        res["lines"].append(gl)
    json.dump(res, open(sys.argv[1], "w"))
    for gl in res["lines"]:
        print(sum(g["adv"] for g in gl), [len(g.get("strokes", [])) for g in gl])


main()
