"""Банки джема: стекло, джем своего цвета, крышка (металл или ткань в клетку), этикетка без букв — значок ягоды."""
import lib
from lib import INK, blob, ellipse_pts, f, line, shape

JAMS = ["#c8202e", "#7a1f4a", "#e86a1a", "#f2b31c", "#5a2a6e", "#a8123a", "#d84a6a", "#8fb52a", "#e8892a", "#4a1a3a",
        "#b3361c", "#f4d23a", "#6a3a1a", "#d63c8a", "#3a5aa8", "#9a2a1a", "#e85a4a", "#c27a12", "#6e8a1e", "#8a3a8a",
        "#ef9a3a", "#b0204a", "#2e3a7a", "#d4a01a"]
LIDS = ["#d8b04a", "#c94a3a", "#3a6ab0", "#e8e0c8", "#4a8a4a", "#d8b04a"]


def jar(cx, by, color, sc=1.0, sd=0, lid=None, label=True):
    """Банка, низ в (cx, by). Высота ~120*sc."""
    w, h = 64 * sc, 100 * sc
    lid = lid or LIDS[sd % len(LIDS)]
    x0, x1 = cx - w / 2, cx + w / 2
    top = by - h
    body = [(x0 + 6 * sc, by, 1), (x0, by - 8 * sc), (x0, top + 18 * sc), (x0 + 6 * sc, top + 6 * sc), (cx - w * .36, top),
            (cx + w * .36, top), (x1 - 6 * sc, top + 6 * sc), (x1, top + 18 * sc), (x1, by - 8 * sc), (x1 - 6 * sc, by, 1)]
    dark = lib.mul(color, (.62, .58, .62))
    inner = [blob([(x0 - 2, top + 16 * sc), (x1 + 2, top + 16 * sc), (x1 + 2, by + 2), (x0 - 2, by + 2)], color)]
    inner.append(blob([(cx + w * .1, top + 10 * sc), (x1 + 2, top + 10 * sc), (x1 + 2, by + 2), (cx + w * .2, by + 2)], dark, .9))
    inner.append(blob([(x0 - 2, top), (x1 + 2, top), (x1 + 2, top + 16 * sc), (x0 - 2, top + 16 * sc)], "#f2f0ea", .55))
    if label:
        lx0, lx1, ly0, ly1 = x0 + 7 * sc, x1 - 7 * sc, top + 38 * sc, top + 76 * sc
        inner.append(shape([(lx0, ly0, 1), (lx1, ly0, 1), (lx1, ly1, 1), (lx0, ly1, 1)], "#f6efdc",
                           blob(ellipse_pts(cx, (ly0 + ly1) / 2 + 2 * sc, 9 * sc, 9 * sc, 10), color)
                           + blob([(cx - 2 * sc, (ly0 + ly1) / 2 - 8 * sc), (cx + 9 * sc, (ly0 + ly1) / 2 - 14 * sc), (cx + 4 * sc, (ly0 + ly1) / 2 - 6 * sc)], "#4a8a3a")
                           + blob([(lx1 - 10 * sc, ly0), (lx1, ly0), (lx1, ly1), (lx1 - 10 * sc, ly1)], "#d8ccb0", .8),
                           w=1.8 * sc, seed=sd + 3))
    inner.append(line([(x0 + 9 * sc, top + 24 * sc), (x0 + 8 * sc, by - 14 * sc)], 5 * sc, "#ffffff", seed=sd + 4, op=.75, taper=.7))
    inner.append(line([(x1 - 10 * sc, top + 22 * sc), (x1 - 10 * sc, top + 34 * sc)], 3 * sc, "#ffffff", seed=sd + 5, op=.5))
    s = [shape(body, "#e9eef0", "".join(inner), w=3.2 * sc, seed=sd)]
    # крышка
    lt = top - 16 * sc
    lp = [(x0 + 2 * sc, top + 4 * sc, 1), (x0 + 2 * sc, lt + 2 * sc), (x0 + 6 * sc, lt), (x1 - 6 * sc, lt), (x1 - 2 * sc, lt + 2 * sc), (x1 - 2 * sc, top + 4 * sc, 1)]
    li = blob([(cx + w * .15, lt), (x1, lt), (x1, top + 6 * sc), (cx + w * .2, top + 6 * sc)], lib.mul(lid, (.7, .68, .7)), .9)
    li += line([(x0 + 8 * sc, lt + 4 * sc), (cx, lt + 3 * sc)], 2.4 * sc, "#ffffff", seed=sd + 6, op=.7)
    s.append(shape(lp, lid, li, w=3 * sc, seed=sd + 7))
    return "".join(s)
