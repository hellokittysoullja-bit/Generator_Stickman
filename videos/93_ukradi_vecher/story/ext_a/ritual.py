"""Картинка-ритуал для ТГ (обещана в призыве): python3 ritual.py out.svg, затем common/render.js png и обрезка до 1080×1350."""
import sys, os
E = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, E)
import s93 as M
from s93 import lib, PR, shape, line, blob, ellipse_pts, tf, INK
lib.DEFS.clear()
def txt(x, y, s, size, col=INK, anchor="middle", stroke=None):
    st = f' stroke="{stroke}" stroke-width="8" paint-order="stroke"' if stroke else ""
    return f'<text x="{x}" y="{y}" font-family="IDB" font-size="{size}" fill="{col}" text-anchor="{anchor}"{st}>{s}</text>'
o = ['<rect width="1080" height="1920" fill="#2b3360"/>']
for i in range(0, 1080, 130):
    o.append(f'<rect x="{i}" y="0" width="44" height="1350" fill="#3a4378"/>')
o.append(txt(540, 140, "МОЙ ВЕЧЕРНИЙ РИТУАЛ", 72, "#FFFFFF", stroke=INK))
o.append(txt(540, 205, "засыпаю за 10 минут", 44, "#ffcf6a"))
caps = [("Тёплый свет", "за час до сна"), ("5 минут —", "дела на бумагу"), ("Телефон", "на кухне"), ("Прохладная", "комната")]
for i in range(4):
    cx, cy = 290 + 500 * (i % 2), 470 + 470 * (i // 2)
    o.append(shape(lib.rrect(cx - 235, cy - 215, cx + 235, cy + 215, 30), "#fff8e6", "", w=5, seed=300 + i))
    ix, iy = cx, cy - 60
    n0 = len(o)
    if i == 0:
        o.append(PR.glow(ix, iy - 20, 170, .9, "#ffb347") + PR.night_lamp(ix, iy + 110, .85, on_u=1.0, t=0))
    elif i == 1:
        o.append(M.notebook(ix, iy, .62, -6, open_=1.0, lines_=.8) + PR.pencil(ix + 80, iy + 30, 1.0, -40))
    elif i == 2:
        o.append(shape(lib.rrect(ix - 140, iy + 40, ix + 140, iy + 70, 6), "#e9dcc0", "", w=4, seed=310))
        o.append(M.phone_up(ix - 20, iy - 30, .55, 90, glow=.6, charge=1.0))
        o.append(PR.charger(ix + 110, iy - 40, 1.2) + PR.cable([(ix + 110, iy - 6), (ix + 100, iy + 30), (ix + 60, iy + 40)], w=7, seed=3))
    else:
        o.append(shape(lib.rect_pts(ix - 110, iy - 110, ix + 110, iy + 110), "#9fc4e8", line([(ix, iy - 110), (ix, iy + 110)], 7, "#fff8e6", taper=0, wmin=1, seed=311) +
                       line([(ix - 110, iy), (ix + 110, iy)], 7, "#fff8e6", taper=0, wmin=1, seed=312), w=5, seed=313))
        for j, (dx, dy, r) in enumerate(((-40, -40, 30), (50, 30, -20), (-10, 60, 70))):
            o.append(M.leaf(ix + dx, iy + dy, 1.5, r, j))
    clip = lib.clip_rect(cx - 230, cy - 210, 460, 420)
    o[n0:] = [f'<g clip-path="url(#{clip})">{"".join(o[n0:])}</g>']
    o.append(shape(ellipse_pts(cx - 190, cy - 170, 38, 38, 18), "#ffc24a", "", w=4, seed=320 + i) + txt(cx - 190, cy - 152, str(i + 1), 50))
    o.append(txt(cx, cy + 120, caps[i][0], 50) + txt(cx, cy + 178, caps[i][1], 50))
o.append(M.cat(985, 1346, .44, 0.3, dict(smug=.8, look=(-.6, -.2), tilt=-6), mask=1.0))
o.append(shape(lib.rrect(150, 1215, 790, 1315, 48), "#2AABEE", "", w=4, seed=330) + txt(470, 1283, "t.me/ru_adhd", 56, "#FFFFFF"))
open(sys.argv[1], "w").write(lib.svg("".join(o)))
