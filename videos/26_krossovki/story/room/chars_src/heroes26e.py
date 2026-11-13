"""Вечерние планы room рилса 26 «кроссовки» (s05 s13 s17): Дима сидит на диване при торшере (герой и кот рилса 24),
s13 — пишет ручкой на жёлтом стикере (правая рука — плечо и предплечье на двух суставах, кончик ручки ведёт IK,
рукав не отрывается от плеча); s17 — Димы нет, рядом с котом пустая открытая обувная коробка, крышка прислонена.
Запуск: python3 heroes26e.py → heroes26e.html (анимация — template26e.html)."""
import math
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import heroes24 as H  # noqa: E402
from heroes24 import shape, blob, line, rect_pts, blur, INK, HOOD, HOOD_SH, HOOD_SH2, FOLD  # noqa: E402
from ink import band, ellipse_pts, fill_d  # noqa: E402

_front24 = H.front_dima

# уши кота: заливка уха заходит в голову (закрывает контур головы у основания), но была ровного цвета шерсти, а верх
# головы — с подсветкой меха и тенью справа: на крупном плане по низу заливки шёл прямой шов («тёмный столб» под
# загнутым ухом). Теперь под деталями уха — те же пятна, что на голове (рисунок головы рилса 24), шва нет.
import inspect  # noqa: E402


def _head_inner():
    inner = blob([(884, 990), (940, 1050), (930, 1150), (866, 1150), (902, 1080)], H.CAT_SH, .85)
    inner += blob([(784, 1004), (836, 994), (880, 1004), (862, 1018), (804, 1020)], H.CAT_FUR, .6)
    for i, st in enumerate([[(800, 1004), (806, 1016)], [(836, 996), (838, 1010)], [(870, 1002), (866, 1014)]]):
        inner += line(st, 2, H.CAT_EDGE, seed=258 + i, op=.8)
    return inner


H._head_inner = _head_inner
_src = inspect.getsource(H.cat_ears).replace("""f'<g clip-path="url(#{c})">' + """, """f'<g clip-path="url(#{c})">' + _head_inner() + """)
assert _src.count("_head_inner()") == 2
exec(_src, H.__dict__)

# ─── стикер: на коленях, левая кисть придерживает его край, пишется две строки
ST = [(296, 1160, 1), (404, 1154, 1), (412, 1236, 1), (292, 1242, 1)]
ARM_S, ARM_E, ARM_W = (452, 1078), (520, 1222), (430, 1196)     # плечо, локоть, запястье (как поза N рилса 24)
TIP0 = (384, 1212)                                              # кончик ручки в покое


def st_p(u, v):
    """u: 0 левый … 1 правый, v: 0 верх … 1 низ стикера (билинейно по углам)."""
    a, b, c, d = [np.array(p[:2], float) for p in ST]
    top = a + (b - a) * u
    bot = d + (c - d) * u
    return tuple(top + (bot - top) * v)


def scrib_pts(row, seed):
    """Строка «от руки»: слова из петель разной высоты с выносными вверх и вниз, между словами перо поднято
    (отдельные подпути — dasharray и getPointAtLength идут по ним подряд). Без букв: на среднем плане читается как почерк."""
    rs = np.random.RandomState(seed)
    v0 = .40 + .27 * row
    words = [[5, 3], [3, 4, 2]][row]
    u = .2
    out = []
    for wl in words:
        n = wl * 3
        pts = []
        for k in range(n + 1):
            uu = u + .022 * k
            hgt = .07 + .03 * rs.uniform(-1, 1)
            if k % 3 == 1 and rs.uniform() < .35:
                hgt = .15                                    # выносной вверх
            v = v0 - hgt * (k % 2) + (.03 if (k % 7 == 5) else 0)
            pts.append(st_p(uu, v))
        out.append(pts)
        u += .022 * n + .045
    return out


def arm_parts(S, E, Wr, w=(62, 52, 44), seed=0):
    """Рукав худи на двух суставах: плечо (S→E) и предплечье с манжетой (E→Wr) — отдельными фигурами (из sleeve рилса 24)."""
    up = band([S, ((S[0] + E[0]) / 2, (S[1] + E[1]) / 2), E], w[0], w[1], step=5, cap=True)
    fa = band([Wr, ((E[0] + Wr[0]) / 2, (E[1] + Wr[1]) / 2), E], w[2], w[1], step=5, cap=True)
    ax = np.array(Wr, float) - np.array(E, float)
    L = np.linalg.norm(ax)
    ax /= L
    nx = np.array([-ax[1], ax[0]])
    inner = blob([tuple(np.array(E) + nx * 40), tuple(np.array(Wr) + nx * 40), tuple(np.array(Wr) + nx * 8), tuple(np.array(E) + nx * 10)],
                 HOOD_SH, .85)
    for i, u in enumerate((.12, .24, .7)):
        c = np.array(E) + ax * L * u
        inner += line([tuple(c + nx * 20), tuple(c + ax * 6), tuple(c - nx * 18)], 2.8, FOLD, seed=seed + i, op=.85, peak=.4)
    upper = shape(up, HOOD, blob([tuple(np.array(S) + 20), tuple(np.array(E) + 30), tuple(np.array(E) + (0, 40))], HOOD_SH, .7) +
                  line([tuple(np.array(E) + (-14, -40)), tuple(np.array(E) + (0, -24)), tuple(np.array(E) + (14, -36))], 2.8, FOLD,
                       seed=seed + 5, op=.8), w=5.2, seed=seed + 7)
    fore = shape(fa, HOOD, inner, w=5.2, seed=seed + 8)
    c0 = np.array(Wr) - ax * 22
    cf = band([tuple(c0), tuple(np.array(Wr) + ax * 2)], w[2] + 6, w[2] + 4, step=3, cap=False)
    rib = "".join(line([tuple(c0 + ax * k * 4 + nx * (w[2] / 2 + 2)), tuple(c0 + ax * k * 4 - nx * (w[2] / 2 + 2))], 1.8, HOOD_SH2,
                       seed=seed + 20 + k, op=.8) for k in range(1, 6))
    fore += shape(cf, HOOD_SH, rib, w=4.6, seed=seed + 9)
    return upper, fore


def sticker():
    s = []
    pc = H.clip_of(H.REG["plaid"])
    s.append(f'<g clip-path="url(#{pc})">' + blob([(p[0] + 6, p[1] + 8) for p in ST], "#0d160f", .45, blur(5)) + "</g>")
    inner = blob([st_p(0, 0), st_p(1, 0), st_p(1, .2), st_p(0, .2)], "#e9c22e", .9)          # клеевая полоса
    inner += blob([st_p(0, .78), st_p(1, .78), st_p(1, 1), st_p(0, 1)], "#f9e47a", .55)     # свет внизу
    inner += blob([st_p(.86, .55), st_p(1, .45), st_p(1, 1), st_p(.9, 1)], "#d9ae22", .5)  # чуть отогнутый правый край
    s.append(shape(ST, "#f6d443", inner, w=3.6, seed=1300))
    for r in range(2):
        d = "".join(fill_d(w, closed=False) for w in scrib_pts(r, 1310 + r))
        s.append(f'<path id="st_scrib{r}" d="{d}" fill="none" stroke="#24307a" stroke-width="3.0" stroke-linecap="round" '
                 f'stroke-linejoin="round" stroke-dasharray="600 600" stroke-dashoffset="600"/>')
    return "".join(s)


def shoebox():
    """Пустая обувная коробка на пледе слева от кота: передняя стенка, открытый верх с тёмным нутром и мятой бумагой,
    крышка прислонена к левому боку. Без надписей: на боку только белая полоса."""
    s = ['<g id="box17" style="display:none">']
    x0, x1, yt, yb, dp = 505, 650, 1162, 1238, 34      # передняя стенка, глубина (вверх-вправо)
    dx, dy = 18, -dp
    # тень на пледе
    pc = H.clip_of(H.REG["plaid"])
    s.append(f'<g clip-path="url(#{pc})">' + blob(ellipse_pts((x0 + x1) / 2 + 12, yb + 4, 100, 14, 14), "#0d160f", .55, blur(6)) + "</g>")
    # крышка прислонена к левому боку изнанкой к нам: оранжевый бортик по краю, внутри крафт
    lid = [(478, 1196, 1), (494, 1058, 1), (636, 1064, 1), (626, 1200, 1)]
    lin = [(491, 1186, 1), (505, 1070, 1), (624, 1075, 1), (615, 1190, 1)]
    s.append(shape(lid, "#e2753c", blob([(478, 1196), (494, 1058), (502, 1059), (487, 1197)], "#b9562a", .9), w=4.6, seed=1400))
    s.append(shape(lin, "#b98a58", blob([(491, 1186), (505, 1070), (624, 1075), (620, 1102), (500, 1098)], "#8a6036", .55) +
                   line([(520, 1120), (566, 1118)], 2, "#d2a878", seed=1411, op=.8), w=3.0, seed=1412))
    # открытый верх: нутро из крафта, дно в тени, задняя стенка изнутри светлее
    top = [(x0, yt, 1), (x0 + dx, yt + dy, 1), (x1 + dx, yt + dy, 1), (x1, yt, 1)]
    s.append(shape(top, "#4a3018", blob([(x0 + dx, yt + dy), (x1 + dx, yt + dy), (x1 + dx - 4, yt + dy + 16), (x0 + dx + 4, yt + dy + 16)],
                                        "#b98a58", .95) +
                   blob([(x1 + dx - 4, yt + dy), (x1 + dx, yt + dy), (x1, yt), (x1 - 12, yt)], "#8a6036", .9), w=4.4, seed=1402))
    # папиросная бумага свисает через передний край (коробку распаковали)
    tissue = [(x0 + 70, yt - 14), (x0 + 96, yt - 20), (x0 + 128, yt - 12), (x0 + 132, yt + 4), (x0 + 124, yt + 26), (x0 + 112, yt + 20),
              (x0 + 100, yt + 30), (x0 + 88, yt + 18), (x0 + 74, yt + 22), (x0 + 66, yt + 2)]
    # правый бок (в перспективе)
    side = [(x1, yt, 1), (x1 + dx, yt + dy, 1), (x1 + dx, yb + dy + 6, 1), (x1, yb, 1)]
    s.append(shape(side, "#b9562a", blob([(x1, yt), (x1 + dx, yt + dy), (x1 + dx, yt + dy + 18), (x1, yt + 18)], "#d06a34", .7), w=4.4, seed=1406))
    # передняя стенка
    front = [(x0, yt, 1), (x1, yt, 1), (x1, yb, 1), (x0, yb, 1)]
    inner = blob([(x0, yt + 50), (x1, yt + 50), (x1, yt + 62), (x0, yt + 62)], "#fbf3e6", .95)          # белая полоса
    inner += blob([(x0, yb - 14), (x1, yb - 14), (x1, yb), (x0, yb)], "#b9562a", .7)
    inner += blob([(x0, yt), (x1, yt), (x1, yt + 8), (x0, yt + 8)], "#f6a066", .8)
    inner += line([(x0 + 10, yt + 30), (x0 + 40, yt + 28)], 2, "#f6a066", seed=1408, op=.8)
    s.append(shape(front, "#e2753c", inner, w=4.8, seed=1407))
    s.append(shape(tissue, "#f4efe6", line([(x0 + 92, yt - 10), (x0 + 100, yt + 16)], 1.8, "#c9c0b0", seed=1404, op=.9) +
                   blob([(x0 + 66, yt + 2), (x0 + 132, yt + 4), (x0 + 124, yt + 26), (x0 + 74, yt + 22)], "#ddd5c6", .6), w=3.0, seed=1403))
    s.append("</g>")
    return "".join(s)


def front26():
    s = [_front24()]
    s.append('<g id="pose_S" style="display:none">')
    s.append(sticker())
    up, fore = arm_parts(H.L_S, (150, 1200), (236, 1218), seed=940)
    s.append(up + fore)
    s.append(H.hand_s(H.flat_hand, 262, 1214, 2, 950, 1.0))
    up, fore = arm_parts(ARM_S, ARM_E, ARM_W, seed=960)
    s.append(f'<g id="arm_up" transform="rotate(0 {ARM_S[0]} {ARM_S[1]})">{up}'
             f'<g id="arm_fore" transform="rotate(0 {ARM_E[0]} {ARM_E[1]})">{fore}'
             + H.pen(462, 1128, TIP0[0], TIP0[1], seed=970) + H.hand_s(H.fist, 432, 1162, 133, 980, 1.0) + "</g></g>")
    s.append("</g>")
    s.append(shoebox())
    return "".join(s)


def cat_brows():
    """Брови кота для сомнения (s02 лёжа — heroes26l): светлые штрихи шерсти над глазами, в осях головы."""
    return ""


H.front_dima = front26

if __name__ == "__main__":
    here = __file__.rsplit("/", 1)[0]
    svg = H.build()
    html = open(f"{here}/template26e.html").read().replace("<!--SVG-->", svg)
    open(f"{here}/heroes26e.html", "w").write(html)
    print("heroes26e.html", len(html) // 1024, "KB")
