"""Сцена «Дима, 01:47» — SVG, доведённый до уровня образцов. Запуск: python3 scene.py → scene.html.

Слои: базовый рисунок в «дневных» плоских цветах с одной тенью (cel) → ночь умножением (multiply) →
свет экрана/огонька/луны осветлением (screen) и резкий рим-свет по силуэту → светящееся поверх → виньетка и зерно.
Части для анимации — группы с id (см. ANIM_IDS в конце).
"""
import math
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from ink import band, ellipse_pts, fill_d, fur, ink_closed, ink_open, sample  # noqa: E402

W, H = 1080, 1920
INK = "#1c1622"
DEFS = []
_uid = [0]


def uid(p="c"):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


def shape(pts, fill, inner="", w=5.0, seed=0, ink=True, id=None, attrs="", var=0.28, weight=0.45, ink_color=INK):
    """Заливка + внутреннее (тени, узор) по маске силуэта + тушь переменной толщины."""
    d = fill_d(pts)
    gid = f' id="{id}"' if id else ""
    out = [f"<g{gid} {attrs}>", f'<path d="{d}" fill="{fill}"/>']
    if inner:
        c = uid()
        DEFS.append(f'<clipPath id="{c}"><path d="{d}"/></clipPath>')
        out.append(f'<g clip-path="url(#{c})">{inner}</g>')
    if ink:
        out.append(f'<path d="{ink_closed(pts, w, var=var, weight=weight, seed=seed)}" fill="{ink_color}"/>')
    out.append("</g>")
    return "".join(out)


def clip_of(pts):
    c = uid()
    DEFS.append(f'<clipPath id="{c}"><path d="{fill_d(pts)}"/></clipPath>')
    return c


def line(pts, w=4.0, color=INK, taper=0.6, wmin=0.12, seed=3, peak=0.5, op=1.0, extra=""):
    d = ink_open(pts, w, taper=taper, wmin=wmin, seed=seed, peak=peak)
    o = f' opacity="{op}"' if op != 1 else ""
    return f'<path d="{d}" fill="{color}"{o} {extra}/>'


def blob(pts, color, op=1.0, extra=""):
    o = f' opacity="{op}"' if op != 1 else ""
    return f'<path d="{fill_d(pts)}" fill="{color}"{o} {extra}/>'


def rect_pts(x0, y0, x1, y1, r=0):
    if r <= 0:
        return [(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)]
    k = r * 0.3
    return [(x0 + r, y0), (x1 - r, y0), (x1 - k, y0 + k), (x1, y0 + r), (x1, y1 - r), (x1 - k, y1 - k), (x1 - r, y1),
            (x0 + r, y1), (x0 + k, y1 - k), (x0, y1 - r), (x0, y0 + r), (x0 + k, y0 + k)]


def blur(sd):
    i = f"bl{sd}".replace(".", "_")
    if not any(f'id="{i}"' in x for x in DEFS):
        DEFS.append(f'<filter id="{i}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{sd}"/></filter>')
    return f'filter="url(#{i})"'


def T(pts, dx, dy, s=1.0, rot=0.0, cx=0.0, cy=0.0):
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for p in pts:
        x, y = (p[0] - cx) * s, (p[1] - cy) * s
        q = (cx + x * c - y * sn + dx, cy + x * sn + y * c + dy)
        out.append(q + ((1,) if len(p) > 2 and p[2] else ()))
    return out


# ───────────────────────────── узоры ─────────────────────────────
def patterns():
    leaf = "#b09670"
    sprig = (
        f'<path d="M24 18 C20 34 28 48 24 64" stroke="{leaf}" stroke-width="2" fill="none"/>'
        f'<ellipse cx="17" cy="32" rx="7" ry="3.2" transform="rotate(-35 17 32)" fill="{leaf}"/>'
        f'<ellipse cx="31" cy="40" rx="7" ry="3.2" transform="rotate(35 31 40)" fill="{leaf}"/>'
        f'<ellipse cx="18" cy="50" rx="6" ry="2.8" transform="rotate(-30 18 50)" fill="{leaf}"/>'
        f'<circle cx="24" cy="15" r="4.2" fill="{leaf}"/><circle cx="24" cy="15" r="1.6" fill="#c9b18b"/>'
    )
    DEFS.append(f"""
<pattern id="pWall" width="96" height="150" patternUnits="userSpaceOnUse">
 <rect width="96" height="150" fill="#c8b08a"/>
 <rect x="0" width="48" height="150" fill="#c2a982"/>
 <rect x="46" width="2.5" height="150" fill="#b29770"/><rect x="0" width="1.5" height="150" fill="#d0b994"/>
 <g>{sprig}</g><g transform="translate(48 75)">{sprig}</g>
 <circle cx="72" cy="20" r="1.6" fill="{leaf}"/><circle cx="24" cy="100" r="1.6" fill="{leaf}"/>
</pattern>
<pattern id="pPlaid" width="88" height="88" patternUnits="userSpaceOnUse">
 <rect width="88" height="88" fill="#7aa66a"/>
 <rect x="0" width="34" height="88" fill="#5b8a50" opacity=".85"/>
 <rect y="0" width="88" height="34" fill="#5b8a50" opacity=".85"/>
 <rect width="34" height="34" fill="#3f6b3c"/>
 <rect x="56" width="5" height="88" fill="#d9e3a8" opacity=".75"/><rect y="56" width="88" height="5" fill="#d9e3a8" opacity=".75"/>
 <rect x="15" width="3" height="88" fill="#2a4630"/><rect y="15" width="88" height="3" fill="#2a4630"/>
 <rect x="74" width="2" height="88" fill="#a33f35" opacity=".8"/><rect y="74" width="88" height="2" fill="#a33f35" opacity=".8"/>
</pattern>
<pattern id="pPlaidTop" href="#pPlaid" patternTransform="rotate(-5) scale(1 .62)"/>
<pattern id="pPlaidFront" href="#pPlaid" patternTransform="rotate(1.5) translate(20 0)"/>
<pattern id="pSofa" width="22" height="22" patternUnits="userSpaceOnUse">
 <rect width="22" height="22" fill="#8e5a4a"/><circle cx="5" cy="5" r="1.4" fill="#7e4d3f"/><circle cx="16" cy="16" r="1.4" fill="#7e4d3f"/>
</pattern>
<pattern id="pPillow" width="54" height="54" patternUnits="userSpaceOnUse" patternTransform="rotate(-8)">
 <rect width="54" height="54" fill="#dccdb6"/>
 <g fill="#c99a98"><circle cx="13" cy="13" r="3"/><circle cx="9" cy="10" r="2.2"/><circle cx="17" cy="10" r="2.2"/><circle cx="9" cy="16" r="2.2"/><circle cx="17" cy="16" r="2.2"/></g>
 <circle cx="13" cy="13" r="1.4" fill="#e9d79a"/>
 <ellipse cx="22" cy="20" rx="4" ry="1.8" transform="rotate(30 22 20)" fill="#9cb58a"/>
 <g fill="#b9a0b8" transform="translate(27 27)"><circle cx="13" cy="13" r="2.6"/><circle cx="9" cy="10" r="1.9"/><circle cx="17" cy="10" r="1.9"/><circle cx="9" cy="16" r="1.9"/><circle cx="17" cy="16" r="1.9"/></g>
</pattern>
<pattern id="pFloor" width="1080" height="600" patternUnits="userSpaceOnUse">
 <rect width="1080" height="600" fill="#7c5a42"/>
</pattern>
<pattern id="pRug" width="70" height="70" patternUnits="userSpaceOnUse" patternTransform="scale(1 .55)">
 <rect width="70" height="70" fill="#97423a"/>
 <path d="M35 8 L60 35 L35 62 L10 35Z" fill="#7c2f2c"/>
 <path d="M35 20 L48 35 L35 50 L22 35Z" fill="#d7a24e"/>
 <path d="M35 28 L42 35 L35 42 L28 35Z" fill="#2f4a5a"/>
 <circle cx="0" cy="0" r="5" fill="#d7a24e"/><circle cx="70" cy="0" r="5" fill="#d7a24e"/>
 <circle cx="0" cy="70" r="5" fill="#d7a24e"/><circle cx="70" cy="70" r="5" fill="#d7a24e"/>
</pattern>
<pattern id="pRugBorder" width="40" height="40" patternUnits="userSpaceOnUse" patternTransform="scale(1 .55)">
 <rect width="40" height="40" fill="#d8b47a"/>
 <path d="M0 20 L10 8 L20 20 L30 8 L40 20 L30 32 L20 20 L10 32Z" fill="#7c2f2c"/>
</pattern>
<pattern id="pCurtain" width="60" height="80" patternUnits="userSpaceOnUse">
 <rect width="60" height="80" fill="#e4dccb"/>
 <circle cx="15" cy="20" r="2.4" fill="#cdbfa6"/><circle cx="45" cy="60" r="2.4" fill="#cdbfa6"/>
</pattern>
""")


# ───────────────────────────── стена, окно, полка ─────────────────────────────
def wall():
    s = [f'<rect width="{W}" height="1450" fill="url(#pWall)"/>']
    # мягкая грязь и затенение по углам (ambient occlusion)
    s.append(f'<rect width="{W}" height="1450" fill="url(#gWallAO)"/>')
    # отклеившийся стык обоев и пятно
    s.append(line([(470, 0), (468, 300), (472, 640)], 2.2, "#9d8462", seed=11, op=.8))
    s.append(blob([(466, 0), (500, 0), (497, 46), (482, 70, 1), (470, 40)], "#d6c19d"))
    s.append(line([(470, 2), (482, 70), (498, 40)], 2.4, seed=12))
    s.append(blob(ellipse_pts(860, 1330, 90, 26, 10, jitter=.15, seed=3), "#a68d68", .35))
    # трещина
    s.append(line([(80, 820), (96, 846), (90, 872), (104, 900)], 2.0, "#8f7656", seed=13))
    return "".join(s)


def baseboard_floor():
    s = []
    s.append(f'<rect y="1430" width="{W}" height="490" fill="#7c5a42"/>')
    # доски: перспектива — швы реже к зрителю
    ys = [1460, 1492, 1532, 1580, 1640, 1712, 1800, 1905]
    prev = 1430
    rs = np.random.RandomState(5)
    for i, y in enumerate(ys):
        shade = ["#7c5a42", "#76553e", "#83604a", "#795841"][i % 4]
        s.append(f'<rect y="{prev}" width="{W}" height="{y - prev}" fill="{shade}"/>')
        s.append(line([(-10, y), (540, y + rs.uniform(-1, 1)), (1090, y)], 3.2, "#3e2a20", taper=.3, wmin=.5, seed=20 + i))
        off = rs.uniform(0, 300)
        for x in np.arange(off, W, 360 + i * 40):
            s.append(line([(x, prev + 2), (x + (x - 540) * 0.04, y - 2)], 2.6, "#3e2a20", taper=.4, seed=30 + i))
        # сучки и волокна
        for _ in range(3):
            x = rs.uniform(20, 1060)
            s.append(line([(x, prev + (y - prev) * .45), (x + 60, prev + (y - prev) * .5), (x + 120, prev + (y - prev) * .42)],
                          1.6, "#5e4231", seed=int(x), op=.6))
        prev = y
    # плинтус
    s.append(shape(rect_pts(-10, 1405, 1090, 1438), "#d7cdb9",
                   inner=f'<rect x="-10" y="1428" width="1100" height="12" fill="#b9ae99"/>', w=4, seed=40))
    # розетка над столом с вилкой
    s.append(shape(rect_pts(88, 1028, 136, 1084, 8), "#e6dfcf",
                   inner='<rect x="88" y="1070" width="50" height="14" fill="#c9c0ac"/>', w=3.5, seed=41))
    s.append(blob(ellipse_pts(112, 1056, 15, 15, 10), "#cfc6b2"))
    s.append(shape(rect_pts(100, 1046, 124, 1074, 5), "#2a2a30", w=3, seed=42))
    s.append(line([(112, 1074), (114, 1110), (100, 1140), (80, 1150)], 4.5, "#26232c", taper=.2, wmin=.7, seed=43))
    return "".join(s)


def window():
    s = []
    # штора-тюль за рамой не нужна: сначала стекло
    x0, y0, x1, y1 = 630, 120, 1040, 700
    # небо (база под умножение — светлее, чем будет)
    s.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#gSky)"/>')
    # облака-полосы
    s.append(blob([(640, 300), (760, 286), (880, 300), (1000, 292), (1040, 304), (1040, 322), (900, 318), (760, 326), (640, 318)],
                  "#5e6fa8", .45))
    # дом напротив
    bx = [(630, 430), (760, 430), (760, 395), (905, 395), (905, 450), (1040, 450)]
    bpts = [(x, y, 1) for x, y in bx] + [(1040, 700, 1), (630, 700, 1)]
    s.append(shape(bpts, "#3b4470", w=3, seed=50, inner=''.join(
        f'<rect x="{x}" y="{y}" width="26" height="34" fill="#2a3158"/>'
        for x in range(648, 1030, 46) for y in range(462, 700, 58) if not (x < 760 and y < 440))))
    # антенны и крыша
    s.append(line([(800, 395), (800, 356)], 3, seed=51) + line([(786, 366), (816, 362)], 2.4, seed=52))
    s.append(line([(950, 450), (952, 412)], 3, seed=53) + line([(938, 420), (966, 418)], 2.4, seed=54))
    # рама окна
    fr = "#e4ddcf"
    frame_outer = rect_pts(x0 - 22, y0 - 22, x1 + 22, y1 + 6)
    s.append(f'<path d="{fill_d(frame_outer)} {fill_d(rect_pts(x0, y0, x1, y1))}" fill="{fr}" fill-rule="evenodd"/>')
    s.append(f'<path d="{ink_closed(frame_outer, 4.5, seed=55)}" fill="{INK}"/>')
    s.append(f'<path d="{ink_closed(rect_pts(x0, y0, x1, y1), 4, seed=56)}" fill="{INK}"/>')
    # импосты: вертикальный и форточка
    s.append(shape(rect_pts(826, y0, 846, y1), fr, w=3.6, seed=57,
                   inner='<rect x="839" y="120" width="7" height="580" fill="#c7bfae"/>'))
    s.append(shape(rect_pts(x0, 300, 826, 318), fr, w=3.6, seed=58,
                   inner='<rect x="630" y="312" width="200" height="6" fill="#c7bfae"/>'))
    s.append(shape(rect_pts(846, 300, x1, 318), fr, w=3.6, seed=59,
                   inner='<rect x="846" y="312" width="200" height="6" fill="#c7bfae"/>'))
    # ручка
    s.append(shape(rect_pts(812, 470, 822, 520, 4), "#c9c0b0", w=2.6, seed=60))
    # тень рамы на стекле
    s.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="12" fill="#1a1f3b" opacity=".5"/>')
    # подоконник
    sill = [(596, 700, 1), (1074, 700, 1), (1086, 716, 1), (1086, 738, 1), (584, 738, 1), (584, 716, 1)]
    s.append(shape(sill, "#e9e2d4", w=4.5, seed=61, inner='<rect x="580" y="724" width="520" height="16" fill="#cfc6b4"/>'))
    s.append(blob([(590, 738), (1080, 738), (1070, 770), (600, 770)], "#5b4a36", .35, blur(6)))
    # на подоконнике: кактус в горшке и банка-кружка
    s.append(shape([(668, 700, 1), (664, 660, 1), (716, 660, 1), (712, 700, 1)], "#c46a43", w=3.6, seed=62,
                   inner='<rect x="660" y="660" width="60" height="10" fill="#a5532f"/><rect x="690" y="660" width="30" height="40" fill="#a5532f" opacity=".5"/>'))
    cac = [(678, 662), (674, 620), (690, 596), (706, 620), (702, 662)]
    s.append(shape(cac, "#6f9a5a", w=3.4, seed=63, inner=blob([(692, 598), (708, 622), (702, 662), (692, 662)], "#557a45")))
    s.append(shape([(674, 630), (656, 622), (652, 600), (662, 598), (668, 616), (676, 616)], "#6f9a5a", w=3, seed=64))
    for (x, y) in [(684, 615), (690, 640), (698, 625), (686, 650)]:
        s.append(line([(x, y), (x + 4, y - 3)], 1.6, seed=x))
    s.append(shape(rect_pts(940, 650, 980, 700, 6), "#3d6a8c", w=3.6, seed=65,
                   inner='<rect x="962" y="650" width="20" height="50" fill="#2f5470"/>'))
    s.append(f'<path d="M980 664 C998 664 998 690 980 688" stroke="{INK}" stroke-width="4" fill="none"/>')
    return "".join(s)


def curtains():
    s = []
    # карниз
    s.append(shape(rect_pts(570, 90, 1090, 104, 5), "#7a5a40", w=3.6, seed=70))
    for x in [578, 1082]:
        s.append(shape(ellipse_pts(x, 97, 12, 12, 10), "#8a6a4e", w=3, seed=x))
    # левая штора (тюль, собрана): складки — линии переменной толщины
    L = [(588, 104), (690, 104), (700, 300), (684, 520), (700, 735), (640, 740), (596, 730), (582, 520), (590, 300)]
    inner = blob([(588, 104), (618, 104), (612, 400), (606, 740), (590, 740)], "#c9bea9", .9)
    inner += blob([(650, 104), (664, 104), (668, 400), (660, 740), (646, 740), (650, 400)], "#cfc4af", .8)
    for i, x in enumerate([616, 640, 662, 682]):
        inner += line([(x, 110), (x + 4 - i * 3, 300), (x - 6, 500), (x + 4, 730)], 2.6, "#8c806c", seed=70 + i, op=.85)
    s.append(shape(L, "url(#pCurtain)", inner, w=4, seed=71, attrs='opacity=".96"'))
    # завязка
    s.append(shape([(586, 470), (700, 486), (702, 506), (588, 494)], "#b8875c", w=3.4, seed=72))
    R = [(990, 104), (1090, 104), (1090, 740), (1000, 744), (982, 520), (996, 300)]
    inner = blob([(1050, 104), (1070, 104), (1074, 740), (1052, 740)], "#c9bea9", .9)
    for i, x in enumerate([1012, 1036, 1062]):
        inner += line([(x, 110), (x - 4, 320), (x + 6, 520), (x - 2, 736)], 2.6, "#8c806c", seed=80 + i, op=.85)
    s.append(shape(R, "url(#pCurtain)", inner, w=4, seed=73, attrs='opacity=".96"'))
    return "".join(s)


def poster_shelf():
    s = []
    # плакат: горы и солнце, скотч, отогнутый угол
    P = [(96, 210, 1), (318, 200, 1), (324, 470, 1), (296, 500, 1), (102, 498, 1)]
    inner = '<rect x="80" y="190" width="260" height="320" fill="#e9dcc0"/>'
    inner += blob(ellipse_pts(250, 290, 38, 38, 12), "#e8874a")
    inner += blob([(90, 470), (150, 340), (190, 400), (230, 320), (330, 470)], "#3f6f7a")
    inner += blob([(150, 340), (168, 372), (146, 380), (132, 372)], "#e9dcc0")
    inner += blob([(230, 320), (250, 352), (226, 356), (214, 350)], "#e9dcc0")
    inner += blob([(90, 470), (330, 440), (330, 520), (90, 520)], "#2b4d55")
    s.append(shape(P, "#e9dcc0", inner, w=4, seed=90))
    s.append(shape([(296, 500, 1), (324, 470, 1), (300, 478, 1)], "#cbbd9f", w=3, seed=91))
    s.append(blob([(296, 500), (326, 472), (330, 490), (304, 508)], "#6d5a40", .35, blur(3)))
    for (x, y, r) in [(92, 206, -20), (316, 198, 25), (100, 494, 15)]:
        s.append(f'<rect x="{x - 22}" y="{y - 8}" width="44" height="16" fill="#efe6c8" opacity=".85" transform="rotate({r} {x} {y})"/>')
    # полка
    s.append(blob([(36, 652), (350, 652), (340, 690), (40, 690)], "#5b4632", .35, blur(5)))
    s.append(shape(rect_pts(30, 628, 352, 652), "#8d6649", w=4.4, seed=92,
                   inner='<rect x="30" y="644" width="330" height="10" fill="#6c4c35"/>'))
    for x in [70, 300]:
        s.append(shape([(x, 652, 1), (x + 14, 652, 1), (x + 14, 700, 1)], "#4a4a52", w=3, seed=x))
    books = [(44, 520, 30, "#3e5f8a"), (76, 500, 26, "#a5473d"), (104, 532, 34, "#d0a64c"), (140, 512, 24, "#5d7d58")]
    for i, (x, y, wd, c) in enumerate(books):
        inner = f'<rect x="{x + wd * .62}" y="{y}" width="{wd}" height="140" fill="#000" opacity=".22"/>'
        inner += f'<rect x="{x}" y="{y + 18}" width="{wd}" height="5" fill="#f0e2bb" opacity=".7"/>'
        inner += f'<rect x="{x}" y="{y + 100}" width="{wd}" height="5" fill="#f0e2bb" opacity=".7"/>'
        s.append(shape(rect_pts(x, y, x + wd, 628, 3), c, inner, w=3.8, seed=93 + i))
    # наклонённая книга
    lb = T(rect_pts(168, 520, 196, 628, 3), 0, 0, rot=14, cx=196, cy=628)
    s.append(shape(lb, "#7b4f7a", f'<rect x="150" y="500" width="80" height="140" fill="#000" opacity=".0"/>', w=3.8, seed=97))
    # горшок с вьющимся растением
    s.append(shape([(244, 628, 1), (236, 584, 1), (300, 584, 1), (292, 628, 1)], "#d9d0c0", w=3.8, seed=98,
                   inner='<rect x="270" y="580" width="40" height="50" fill="#b8ae9c"/>'))
    vine = [(262, 586), (250, 620), (256, 680), (246, 740), (258, 800)]
    s.append(line(vine, 3.2, "#3c5a33", seed=99, taper=.3, wmin=.4))
    for i, (x, y, r) in enumerate([(250, 640, -30), (260, 700, 30), (246, 760, -25), (258, 800, 20), (240, 600, -50),
                                   (280, 575, -10), (262, 566, 20), (296, 578, 40)]):
        lp = T(ellipse_pts(0, 0, 15, 7, 8), x, y, rot=r)
        s.append(shape(lp, ["#6b9a58", "#5a8a4a"][i % 2], w=2.6, seed=100 + i,
                       inner=line([(x - 12, y), (x + 12, y)], 1.6, "#3f6a35", seed=i)))
    # рамка с фото
    s.append(shape([(312, 560, 1), (348, 556, 1), (350, 628, 1), (312, 628, 1)], "#a77b55", w=3.6, seed=105,
                   inner=f'<rect x="318" y="566" width="26" height="54" fill="#98b8c4"/>' +
                   blob([(318, 610), (330, 590), (344, 606), (344, 620), (318, 620)], "#6d8f63")))
    # наушники на гвоздике
    s.append(blob(ellipse_pts(520, 470, 3, 3, 6), INK))
    hp = [(492, 540), (494, 484), (520, 466), (546, 484), (548, 540)]
    s.append(line(hp, 9, "#2b2b33", taper=.1, wmin=.8, seed=106))
    for x in [486, 554]:
        s.append(shape(ellipse_pts(x, 552, 16, 24, 12), "#2f2f38", w=3.6, seed=x,
                       inner=blob(ellipse_pts(x + (6 if x < 520 else -6), 556, 9, 18, 10), "#4b4b58")))
    return "".join(s)


def table_clock():
    s = []
    s.append(blob([(-20, 1452), (200, 1452), (196, 1478), (-20, 1478)], "#2b1d14", .45, blur(6)))
    wood, dk = "#8a6346", "#64462f"
    for x in [12, 150]:
        s.append(shape([(x, 1205, 1), (x + 20, 1205, 1), (x + 18, 1462, 1), (x + 3, 1462, 1)], wood, w=4, seed=x,
                       inner=f'<rect x="{x + 12}" y="1200" width="10" height="270" fill="{dk}"/>'))
    s.append(shape(rect_pts(-12, 1345, 178, 1366), wood, f'<rect x="-12" y="1358" width="200" height="10" fill="{dk}"/>', w=4, seed=110))
    # книги и кружка на нижней полке
    s.append(shape(rect_pts(4, 1322, 120, 1345, 3), "#4a6d8e", '<rect x="4" y="1337" width="120" height="8" fill="#365470"/>', w=3.4, seed=111))
    s.append(shape(rect_pts(14, 1302, 108, 1322, 3), "#b5563f", '<rect x="14" y="1315" width="100" height="8" fill="#8e3f2c"/>', w=3.4, seed=112))
    s.append(shape([(124, 1300), (164, 1300), (162, 1345), (126, 1345)], "#e3dccb", w=3.4, seed=113,
                   inner='<rect x="146" y="1296" width="22" height="52" fill="#c4bba7"/>'))
    s.append(f'<path d="M126 1310 C108 1310 108 1336 126 1334" stroke="{INK}" stroke-width="4" fill="none"/>')
    # столешница
    top = [(-14, 1186, 1), (182, 1186, 1), (186, 1212, 1), (-14, 1212, 1)]
    s.append(shape(top, wood, f'<rect x="-14" y="1202" width="210" height="12" fill="{dk}"/>'
                   + line([(10, 1194), (90, 1196), (160, 1193)], 1.6, "#6e4f37", seed=114), w=4.4, seed=115))
    # часы
    s.append(blob([(20, 1186), (176, 1186), (170, 1196), (24, 1196)], "#1b120c", .45, blur(3)))
    body = rect_pts(22, 1112, 172, 1188, 12)
    s.append(shape(body, "#26222c", blob(rect_pts(22, 1170, 172, 1188, 6), "#17141c") +
                   blob([(30, 1118), (164, 1118), (160, 1124), (34, 1124)], "#4a4554", .8), w=4.4, seed=116, id="clock"))
    s.append(shape(rect_pts(34, 1124, 160, 1172, 6), "#1a0a0e", w=3, seed=117))
    return "".join(s)


SEG = {"0": "abcdef", "1": "bc", "4": "fgbc", "7": "abc"}


def seven_seg(ch, x, y, w=22, h=36, t=5.4):
    """Цифра из семи сегментов (рисует код). Наклон 6°."""
    hs = h / 2
    segs = {
        "a": [(x + t * .6, y), (x + w - t * .6, y), (x + w - t * 1.4, y + t), (x + t * 1.4, y + t)],
        "g": [(x + t, y + hs - t / 2), (x + w - t, y + hs - t / 2), (x + w - t * .5, y + hs), (x + w - t, y + hs + t / 2),
              (x + t, y + hs + t / 2), (x + t * .5, y + hs)],
        "d": [(x + t * 1.4, y + h - t), (x + w - t * 1.4, y + h - t), (x + w - t * .6, y + h), (x + t * .6, y + h)],
        "f": [(x, y + t * .6), (x + t, y + t * 1.4), (x + t, y + hs - t * .6), (x, y + hs - t * .2)],
        "b": [(x + w, y + t * .6), (x + w, y + hs - t * .2), (x + w - t, y + hs - t * .6), (x + w - t, y + t * 1.4)],
        "e": [(x, y + hs + t * .2), (x + t, y + hs + t * .6), (x + t, y + h - t * 1.4), (x, y + h - t * .6)],
        "c": [(x + w, y + hs + t * .2), (x + w, y + h - t * .6), (x + w - t, y + h - t * 1.4), (x + w - t, y + hs + t * .6)],
    }
    out = []
    for k in "abcdefg":
        on = k in SEG[ch]
        pts = segs[k]
        d = "M" + "L".join(f"{px - (py - y) * .1:.1f} {py:.1f}" for px, py in pts) + "Z"
        out.append(f'<path d="{d}" fill="{"#ff5a3c" if on else "#3a1214"}" opacity="{1 if on else .55}"/>')
    return "".join(out)


def clock_digits():
    s = ['<g id="clock_digits">']
    x = 46
    for ch in "01:47":
        if ch == ":":
            s.append('<rect x="98" y="1137" width="5" height="5" fill="#ff5a3c" transform="skewX(-6)"/>'
                     '<rect x="96" y="1154" width="5" height="5" fill="#ff5a3c" transform="skewX(-6)"/>')
            x += 14
            continue
        s.append(seven_seg(ch, x + 8, 1130))
        x += 28
    s.append("</g>")
    return "".join(s)


# ───────────────────────────── диван, подушка ─────────────────────────────
def sofa_back():
    s = []
    s.append(blob([(150, 1468), (1100, 1468), (1100, 1500), (150, 1500)], "#20140d", .55, blur(9)))
    back = [(196, 1260, 1), (190, 1010), (206, 966), (260, 952), (560, 958), (760, 950), (960, 956), (1100, 952, 1), (1100, 1262, 1)]
    inner = blob([(190, 990), (1100, 985), (1100, 1262), (190, 1262)], "#7c4b3d", .6)
    inner += blob([(196, 960), (1100, 950), (1100, 975), (200, 985)], "#a8705d", .8)
    for x in [612, 880]:
        inner += line([(x, 960), (x + 6, 1100), (x - 2, 1250)], 3.6, seed=x, op=.9)
        inner += blob([(x + 2, 960), (x + 40, 962), (x + 34, 1250), (x + 4, 1250)], "#6f4136", .45)
    inner += line([(210, 990), (600, 996), (1090, 986)], 2.4, "#5b3328", seed=120, op=.7)
    s.append(shape(back, "url(#pSofa)", inner, w=5.2, seed=121))
    return "".join(s)


def sofa_arm():
    s = []
    arm = [(160, 1450, 1), (156, 1110), (168, 1060), (210, 1036), (270, 1040), (306, 1070), (314, 1120), (306, 1450, 1)]
    inner = blob([(156, 1120), (314, 1120), (314, 1450), (156, 1450)], "#7a4a3c", .5)
    inner += blob([(250, 1050), (310, 1080), (314, 1450), (280, 1450)], "#5e372d", .55)
    inner += blob(ellipse_pts(222, 1090, 52, 40, 12), "#a06a57", .55)
    inner += line([(176, 1300), (290, 1300)], 2.4, "#5b3328", seed=122, op=.7)
    # потёртость и дырка с поролоном
    inner += blob(ellipse_pts(214, 1220, 26, 14, 10, jitter=.2, seed=4), "#b07c66", .7)
    s.append(shape(arm, "url(#pSofa)", inner, w=5.4, seed=123))
    s.append(line([(178, 1110), (194, 1068), (236, 1056), (274, 1076), (282, 1110), (262, 1132), (222, 1132)], 3.4, seed=124))
    hole = [(204, 1356), (222, 1344, 1), (238, 1356), (252, 1350, 1), (258, 1372), (240, 1384, 1), (214, 1382)]
    s.append(shape(hole, "#3b211a", w=2.6, seed=125))
    s.append(shape(fur([(214, 1362), (230, 1356), (248, 1364), (236, 1376), (218, 1374)], 5, 3, seed=6), "#efe6c9", w=2.2, seed=126))
    return "".join(s)


def sofa_front():
    s = []
    seat = [(300, 1288, 1), (1100, 1288, 1), (1100, 1450, 1), (300, 1450, 1)]
    inner = blob([(300, 1420), (1100, 1420), (1100, 1450), (300, 1450)], "#5e372d", .7)
    inner += line([(300, 1300), (1100, 1300)], 2.4, "#5b3328", seed=127, op=.6)
    s.append(shape(seat, "url(#pSofa)", inner, w=5.2, seed=128))
    for x in [196, 1040]:
        s.append(shape([(x, 1446, 1), (x + 26, 1446, 1), (x + 20, 1478, 1), (x + 6, 1478, 1)], "#4a3324", w=3.6, seed=x))
    return "".join(s)


def pillow():
    P = [(226, 1182, 1), (246, 1080), (236, 948, 1), (330, 932), (446, 920, 1), (448, 1040), (470, 1168, 1), (350, 1190)]
    inner = blob([(226, 1182), (246, 1080), (236, 948), (290, 1000), (300, 1150)], "#b49f86", .55)
    inner += blob([(300, 1140), (470, 1160), (470, 1190), (226, 1190)], "#a99179", .6)
    inner += line([(260, 960), (300, 1010), (288, 1080)], 2.6, "#8b7660", seed=129, op=.8)
    inner += line([(430, 940), (400, 990)], 2.4, "#8b7660", seed=130, op=.8)
    return shape(P, "url(#pPillow)", inner, w=5, seed=131)


# ───────────────────────────── Дима ─────────────────────────────
HX, HY, HR = 446, 862, -7  # центр головы и наклон


def head_tf():
    return f"translate({HX} {HY}) rotate({HR})"


def H2G(x, y):
    c, s_ = math.cos(math.radians(HR)), math.sin(math.radians(HR))
    return HX + x * c - y * s_, HY + x * s_ + y * c


SKIN, SKIN_SH, SKIN_SH2 = "#ecc4a2", "#d39f83", "#bf8a74"
HAIR, HAIR_SH = "#5a3826", "#3d2418"
HOOD, HOOD_SH, HOOD_SH2 = "#d4a23e", "#a97b25", "#8c6219"

FACE = [(-30, -120), (40, -116), (88, -84), (110, -32), (116, 18), (108, 62), (84, 98), (46, 120), (6, 126), (-34, 112),
        (-68, 82), (-94, 38), (-106, -16), (-96, -72), (-66, -108)]
EYE_N = (18, -10, 50, 50)    # cx, cy, rx, ry — ближний глаз
EYE_F = (94, -8, 40, 47)     # дальний (ракурс 3/4)


def hood_body():
    s = []
    # капюшон, лежащий под головой на подушке
    hood = [(292, 1046), (296, 980), (330, 944), (390, 936), (440, 968), (520, 990), (560, 1010), (520, 1048), (400, 1060)]
    inner = blob([(296, 980), (330, 944), (390, 936), (420, 960), (360, 1000), (300, 1030)], HOOD_SH2, .9)
    inner += line([(316, 980), (350, 958), (392, 952)], 2.6, "#6b4a12", seed=140, op=.8)
    s.append(shape(hood, HOOD, inner, w=5, seed=141))
    # туловище в худи (дальше его закрывает плед)
    body = [(286, 1100), (300, 1040), (360, 1010), (430, 1018), (480, 1030), (540, 1016), (600, 1036), (642, 1080),
            (662, 1150, 1), (300, 1170, 1)]
    inner = blob([(286, 1060), (360, 1040), (420, 1100), (380, 1170), (286, 1170)], HOOD_SH, .9)
    inner += blob([(560, 1030), (640, 1070), (662, 1150), (600, 1150), (590, 1080)], HOOD_SH, .8)
    # складки
    inner += line([(350, 1060), (390, 1080), (410, 1120)], 3, "#6b4a12", seed=142, op=.85)
    inner += line([(520, 1060), (500, 1090), (508, 1130)], 3, "#6b4a12", seed=143, op=.85)
    inner += line([(440, 1100), (470, 1120)], 2.4, "#6b4a12", seed=144, op=.7)
    s.append(shape(body, HOOD, inner, w=5.2, seed=145, id="dima_body"))
    # шея и вырез
    nk = [(420, 960), (474, 958), (486, 1030), (452, 1046), (418, 1030)]
    s.append(shape(nk, SKIN, blob([(420, 960), (474, 958), (480, 990), (420, 1000)], SKIN_SH, .95) +
                   blob([(420, 960), (440, 960), (440, 1040), (418, 1040)], SKIN_SH2, .6), w=4.6, seed=146))
    collar = [(404, 1026), (432, 1044), (470, 1048), (500, 1030), (510, 1046), (474, 1066), (432, 1064), (396, 1044)]
    s.append(shape(collar, HOOD_SH, "", w=4.4, seed=147))
    # шнурки капюшона
    for (x0, y0, x1, y1, sd) in [(446, 1058, 438, 1124, 148), (480, 1056, 496, 1118, 149)]:
        s.append(line([(x0, y0), ((x0 + x1) / 2 + 3, (y0 + y1) / 2), (x1, y1)], 5.5, "#efe3c4", taper=.2, wmin=.8, seed=sd))
        s.append(line([(x0, y0), ((x0 + x1) / 2 + 3, (y0 + y1) / 2), (x1, y1)], 1.8, INK, taper=.2, wmin=.8, seed=sd + 1, op=.6))
        s.append(shape(rect_pts(x1 - 5, y1, x1 + 5, y1 + 16, 2), "#b9b9c4", w=2.6, seed=sd + 2))
    return "".join(s)


def head():
    s = [f'<g id="dima_head" transform="{head_tf()}">']
    # волосы сзади (за ухом и затылком, на подушке)
    back_hair = [(-60, -110), (-110, -86), (-150, -40, 1), (-122, -30), (-140, 10, 1), (-108, 6), (-104, 40, 1), (-80, 20), (-70, -40)]
    s.append(shape(back_hair, HAIR_SH, "", w=4.6, seed=150))
    # ухо
    ear = [(-86, -16), (-110, -26), (-128, -4), (-124, 30), (-104, 52), (-84, 46)]
    s.append(shape(ear, SKIN, blob([(-128, -4), (-124, 30), (-104, 52), (-110, 20)], SKIN_SH, .9), w=4.6, seed=151))
    s.append(line([(-96, 30), (-114, 18), (-112, -2), (-98, -10)], 3, seed=152))
    # лицо
    inner = []
    # тень: затылочная сторона и под подбородком (свет экрана справа)
    inner.append(blob([(-110, -130), (-40, -130), (-62, -40), (-58, 40), (-24, 130), (-110, 130)], SKIN_SH, .95))
    inner.append(blob([(-20, 100), (50, 112), (100, 80), (110, 140), (-30, 140)], SKIN_SH, .85))
    # щетина: синеватый налёт по челюсти
    inner.append(blob([(-60, 70), (-20, 92), (30, 104), (80, 92), (104, 70), (110, 130), (-60, 130)], "#9e8a96", .45))
    rs = np.random.RandomState(7)
    for _ in range(90):
        x, y = rs.uniform(-50, 104), rs.uniform(76, 124)
        if (x - 30) ** 2 / 90 ** 2 + (y - 60) ** 2 / 66 ** 2 > 1.0 or y > 118 - abs(x - 30) * .15:
            continue
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rs.uniform(1, 1.8):.1f}" fill="#5c4446" opacity=".55"/>')
    # румянец/красные от усталости веки вокруг глаз
    inner.append(blob(ellipse_pts(54, -10, 100, 62, 14), "#d9a08f", .35))
    s.append(shape(FACE, SKIN, "".join(inner), w=5.4, seed=153, id="dima_face"))
    # мешки под глазами — два полумесяца и вторая складка
    for (cx, cy, rx, ry, sd) in [(EYE_N[0], EYE_N[1], EYE_N[2], EYE_N[3], 154), (EYE_F[0], EYE_F[1], EYE_F[2], EYE_F[3], 155)]:
        bag = [(cx - rx * .85, cy + ry * .55), (cx, cy + ry * 1.38), (cx + rx * .85, cy + ry * .55), (cx, cy + ry * .9)]
        s.append(blob(bag, "#a77f8c", .75))
        s.append(line([(cx - rx * .8, cy + ry * .7), (cx, cy + ry * 1.36), (cx + rx * .75, cy + ry * .75)], 3.2, seed=sd))
        s.append(line([(cx - rx * .5, cy + ry * 1.25), (cx + rx * .05, cy + ry * 1.6), (cx + rx * .5, cy + ry * 1.3)], 2.2, seed=sd + 5, op=.75))
    # глаза: белки, зрачки, веки (веко — группа под маской глаза, двигается при моргании)
    for nm, (cx, cy, rx, ry), sd in [("F", EYE_F, 160), ("N", EYE_N, 161)]:
        ep = ellipse_pts(cx, cy, rx, ry, 14)
        cid = clip_of(ep)
        s.append(f'<g id="dima_eye_{nm}">')
        s.append(f'<path d="{fill_d(ep)}" fill="#f6f2ea"/>')
        s.append(f'<g clip-path="url(#{cid})">')
        # тень от века на белке
        s.append(blob([(cx - rx, cy - ry), (cx + rx, cy - ry), (cx + rx, cy + 6), (cx - rx, cy + 2)], "#c9c2d6", .9))
        # зрачок смотрит вправо — на экран
        s.append(f'<g class="dima_pupil" id="dima_pupil_{nm}"><ellipse cx="{cx + rx * .42:.1f}" cy="{cy + 14:.1f}" rx="6.8" ry="7.4" fill="{INK}"/></g>')
        # веко: кожа сверху + край века (утолщённый штрих) + ресничная тень
        lid_y = cy - ry * .02
        lid = [(cx - rx - 10, cy - ry - 30), (cx + rx + 10, cy - ry - 30), (cx + rx + 10, lid_y - 6), (cx + rx * .4, lid_y + 4),
               (cx - rx * .3, lid_y + 1), (cx - rx - 10, lid_y - 10)]
        s.append(f'<g id="dima_lid_{nm}">')
        s.append(blob(lid, SKIN))
        s.append(blob([(cx - rx - 10, cy - ry - 30), (cx + rx + 10, cy - ry - 30), (cx + rx + 10, lid_y - 20), (cx - rx - 10, lid_y - 22)],
                      "#d9a08f", .5))
        s.append(line([(cx - rx - 6, lid_y - 9), (cx - rx * .3, lid_y + 1.5), (cx + rx * .4, lid_y + 4), (cx + rx + 6, lid_y - 5)],
                      6.2, seed=sd, taper=.4, wmin=.35))
        s.append("</g></g>")
        s.append(f'<path d="{ink_closed(ep, 4.6, seed=sd + 2)}" fill="{INK}"/>')
        s.append("</g>")
    # брови — уставшие, чуть вверх у переносицы
    s.append(line([(-26, -74), (6, -82), (44, -78)], 7.5, HAIR_SH, seed=162, peak=.4))
    s.append(line([(74, -78), (102, -84), (128, -74)], 6.5, HAIR_SH, seed=163, peak=.55))
    # нос (3/4): крючок
    s.append(line([(66, 18), (82, 44), (76, 56), (62, 54)], 4.2, seed=164, peak=.45))
    s.append(blob(ellipse_pts(72, 56, 6, 2.5, 8), SKIN_SH, .8))
    # рот: усталая полуулыбка-гримаса
    s.append(f'<g id="dima_mouth">')
    s.append(line([(36, 86), (60, 84), (82, 87), (90, 92)], 4.6, seed=165, peak=.45))
    s.append(line([(54, 98), (70, 98)], 2.6, seed=166, op=.7))
    s.append("</g>")
    # волосы: лохматые, торчат назад и вверх
    hair = [(108, -40), (104, -78), (82, -110), (92, -150, 1), (52, -128), (36, -170, 1), (8, -138), (-18, -178, 1), (-40, -136),
            (-86, -162, 1), (-90, -128), (-142, -128, 1), (-112, -96), (-156, -78, 1), (-118, -64), (-140, -34, 1), (-104, -38),
            (-94, -14, 1), (-80, -42), (-62, -70), (-22, -88), (12, -92), (30, -76, 1), (50, -98), (80, -86, 1), (98, -62), (108, -40, 1)]
    inner = blob([(-160, -190), (-20, -190), (-30, -130), (-70, -100), (-80, -40), (-160, -20)], HAIR_SH, .95)
    inner += blob([(10, -150), (60, -120), (100, -80), (70, -112), (40, -128)], "#7a5038", .9)
    for i, st in enumerate([[(-10, -150), (-30, -120), (-60, -100)], [(30, -140), (10, -110), (-20, -96)],
                            [(70, -120), (60, -100), (40, -94)], [(-70, -130), (-96, -110), (-112, -84)],
                            [(-40, -100), (-70, -80), (-84, -56)]]):
        inner += line(st, 3.2, "#2a170f", seed=170 + i, op=.85)
    s.append(shape(hair, HAIR, inner, w=5.2, seed=171, id="dima_hair"))
    s.append("</g>")
    return "".join(s)


# телефон и рука: локальные координаты телефона
PX, PY, PR = 672, 806, -11


def phone_arm():
    s = []
    # рукав (предплечье) — поверх тела и пледа
    sl = [(608, 1154), (602, 1100), (612, 1030), (626, 952), (684, 946), (690, 1030), (684, 1104), (664, 1156), (636, 1170)]
    inner = blob([(660, 940), (690, 940), (690, 1170), (650, 1170), (668, 1060)], HOOD_SH, .95)
    inner += line([(618, 1080), (640, 1094), (650, 1120)], 3, "#6b4a12", seed=180, op=.85)
    inner += line([(616, 1010), (640, 1018)], 2.6, "#6b4a12", seed=181, op=.75)
    inner += line([(630, 1130), (652, 1146)], 2.6, "#6b4a12", seed=182, op=.75)
    s.append(shape(sl, HOOD, inner, w=5.2, seed=183, id="dima_forearm"))
    cuff = [(624, 960), (620, 930), (684, 924), (690, 954)]
    rib = "".join(line([(x, 932 - (x - 620) * .1), (x + 1, 958 - (x - 620) * .1)], 2, "#8c6219", seed=x, op=.8)
                  for x in range(630, 686, 9))
    s.append(shape(cuff, HOOD_SH, rib, w=4.6, seed=184))
    s.append(f'<g id="dima_hand_phone" transform="translate({PX} {PY}) rotate({PR})">')
    # большой палец — за телефоном? нет: он выходит к экрану по левому краю, его видно (группа для анимации)
    # ладонь снизу
    palm = [(-46, 70), (-30, 54), (10, 48), (44, 60), (52, 100), (40, 140), (-10, 150), (-44, 130)]
    s.append(shape(palm, SKIN, blob([(-46, 90), (52, 110), (40, 150), (-44, 150)], SKIN_SH, .9), w=4.8, seed=185))
    # сам телефон
    back = rect_pts(-40, -92, 40, 92, 16)
    side = [(-40, -88), (-52, -84), (-54, 84), (-40, 90)]
    s.append(shape(side, "#3a3a46", line([(-48, -80), (-50, 80)], 3, "#8fb8ff", seed=186), w=3.6, seed=187, id="phone_side"))
    inner = blob([(10, -92), (40, -92), (40, 92), (24, 92)], "#26262e", .9)
    inner += blob([(-40, -92), (-28, -92), (-30, 92), (-40, 92)], "#4a4a58", .7)
    cam = rect_pts(-32, -84, 6, -44, 10)
    s.append(shape(back, "#18181e", inner, w=4.6, seed=188, id="phone"))
    s.append(shape(cam, "#2c2c36", blob(rect_pts(-32, -60, 6, -44, 6), "#202028"), w=3.4, seed=189))
    for (lx, ly) in [(-20, -74), (-20, -54), (-4, -64)]:
        s.append(shape(ellipse_pts(lx, ly, 8.5, 8.5, 10), "#0e0e14", w=2.6, seed=int(lx * ly) % 97,
                       inner=f'<circle cx="{lx}" cy="{ly}" r="4.6" fill="#232c4a"/><circle cx="{lx - 2}" cy="{ly - 2}" r="1.7" fill="#9fb4e8"/>'))
    s.append('<circle cx="-4" cy="-78" r="3" fill="#e8e0c8"/><circle cx="-4" cy="-50" r="2.6" fill="#3a3a44"/>')
    # пальцы через заднюю крышку к правому краю
    for i, (y, ln) in enumerate([(4, 92), (30, 96), (56, 90)]):
        fp = band([(-38, y + 8), (0, y + 2), (40, y), (52, y + 10)], 27, 23, cap=True)
        s.append(shape(fp, SKIN, blob([(-40, y + 14), (60, y + 10), (60, y + 30), (-40, y + 30)], SKIN_SH, .85),
                       w=4.4, seed=190 + i))
        s.append(line([(30, y - 6), (34, y + 8)], 2.2, seed=195 + i, op=.7))
    # большой палец: от ладони вверх по левому краю, кончик — на экране
    s.append('<g id="dima_thumb">')
    th = band([(-40, 74), (-56, 40), (-62, 10), (-56, -14)], 30, 24, cap=True)
    s.append(shape(th, SKIN, blob([(-80, 0), (-58, 0), (-56, 80), (-80, 80)], SKIN_SH, .8), w=4.6, seed=199, id="dima_thumb_shape"))
    s.append(line([(-50, -12), (-42, -8)], 2.2, seed=200, op=.7))
    s.append("</g>")
    s.append("</g>")
    return "".join(s)


# ───────────────────────────── плед ─────────────────────────────
def plaid():
    s = []
    top = [(396, 1260), (404, 1160), (450, 1118), (540, 1108), (610, 1120), (690, 1146), (770, 1164), (840, 1150),
           (912, 1166), (980, 1136), (1040, 1124), (1100, 1140, 1), (1100, 1300, 1), (700, 1306), (420, 1300)]
    inner = []
    # тени под складками и от тела
    inner.append(blob([(396, 1230), (540, 1180), (700, 1200), (900, 1210), (1100, 1200), (1100, 1310), (396, 1310)], "#203a24", .35))
    inner.append(blob([(690, 1146), (770, 1164), (760, 1230), (700, 1200)], "#203a24", .3))
    inner.append(blob([(960, 1140), (1040, 1124), (1100, 1140), (1100, 1220), (1010, 1190)], "#203a24", .3))
    inner.append(blob([(470, 1130), (560, 1112), (610, 1124), (560, 1140), (500, 1150)], "#f4f8d0", .18))
    for i, st in enumerate([[(440, 1160), (480, 1200), (520, 1250)], [(600, 1150), (640, 1190), (660, 1250)],
                            [(760, 1180), (800, 1210), (790, 1270)], [(980, 1160), (1010, 1210), (1040, 1260)],
                            [(860, 1180), (900, 1200)]]):
        inner.append(line(st, 3.4, seed=210 + i, op=.85))
    s.append(shape(top, "url(#pPlaidTop)", "".join(inner), w=5.4, seed=215, id="plaid_top"))
    # свисающий край с бахромой
    front = [(408, 1290, 1), (700, 1300), (1100, 1290, 1), (1100, 1428, 1), (1040, 1418), (960, 1434), (880, 1416), (790, 1436),
             (700, 1414), (610, 1430), (520, 1408), (440, 1396), (400, 1380)]
    inner = []
    for i, (x0, x1) in enumerate([(470, 520), (650, 700), (840, 880), (990, 1040)]):
        inner.append(blob([(x0, 1300), (x0 + 30, 1300), (x1 + 10, 1440), (x1 - 30, 1440)], "#1b301e", .45))
        inner.append(line([(x0 + 10, 1302), (x0 + 22, 1360), (x1 - 8, 1430)], 3.2, seed=220 + i, op=.85))
    inner.append(blob([(400, 1290), (1100, 1290), (1100, 1312), (400, 1312)], "#1b301e", .4))
    s.append(shape(front, "url(#pPlaidFront)", "".join(inner), w=5.4, seed=225, id="plaid_front"))
    # бахрома
    S_ = sample([(404, 1384), (440, 1398), (520, 1410), (610, 1432), (700, 1416), (790, 1438), (880, 1418), (960, 1436),
                 (1040, 1420), (1100, 1430)], False, step=11)
    rs = np.random.RandomState(9)
    for i, (x, y) in enumerate(S_):
        ln = rs.uniform(14, 22)
        s.append(line([(x, y - 2), (x + rs.uniform(-3, 3), y + ln * .5), (x + rs.uniform(-4, 4), y + ln)], 3.6, "#4f7c48",
                      seed=300 + i, taper=.6, wmin=.3, peak=.3))
    return "".join(s)


# ───────────────────────────── кот ─────────────────────────────
CAT, CAT_SH, CAT_FUR = "#2f2b37", "#1b1821", "#4b4559"
CX, CY = 836, 1080


def cat():
    s = ['<g id="cat">']
    # хвост: за телом справа, кольцо-завиток и огонёк на кончике (группа для покачивания)
    s.append('<g id="cat_tail">')
    tail_c = [(905, 1268), (968, 1262), (1012, 1226), (1024, 1170), (1008, 1126), (978, 1112), (958, 1128), (962, 1150), (982, 1152),
              (990, 1136)]
    tp = band(tail_c, 46, 22)
    tp = fur(tp, 7, 4, seed=21)
    s.append(shape(tp, CAT, blob([(1000, 1120), (1040, 1150), (1030, 1260), (980, 1270)], CAT_SH, .8), w=4.8, seed=230))
    s.append(line([(986, 1240), (1002, 1210), (1006, 1178)], 2.4, CAT_FUR, seed=231, op=.9))
    # огонёк
    s.append('<g id="cat_flame">')
    fl = [(990, 1132), (1006, 1110), (1006, 1088), (1000, 1068), (1010, 1046, 1), (1018, 1072), (1026, 1062, 1), (1028, 1092),
          (1016, 1130), (1000, 1140)]
    fl = T(fl, -6, 4)
    s.append(shape(fl, "#ff8a2a", blob(T([(996, 1134), (1006, 1104), (1004, 1080), (1012, 1094), (1018, 1080), (1022, 1104),
                                        (1012, 1134)], -6, 4), "#ffbe55"), w=3.2, seed=232, ink_color="#8a2f10"))
    s.append(blob(T([(1002, 1132), (1008, 1112), (1012, 1100), (1016, 1114), (1012, 1132)], -6, 4), "#fff0b8"))
    s.append("</g>")
    s.append("</g>")
    # тело — грушей, пушистый край
    body = [(760, 1296), (744, 1240), (756, 1180), (790, 1140), (880, 1140), (916, 1180), (928, 1240), (912, 1296)]
    bp = fur(body, 9, 5, seed=22)
    inner = blob([(860, 1140), (930, 1180), (930, 1300), (870, 1300), (880, 1220)], CAT_SH, .9)
    inner += blob([(800, 1170), (836, 1160), (872, 1170), (860, 1240), (836, 1260), (812, 1240)], CAT_FUR, .55)
    for i, st in enumerate([[(816, 1190), (826, 1208)], [(850, 1192), (844, 1212)], [(834, 1214), (836, 1236)]]):
        inner += line(st, 2.2, "#6a6380", seed=240 + i, op=.8)
    s.append(shape(bp, CAT, inner, w=5, seed=241))
    # задние лапы с оранжевыми подушечками (сидит, лапы вперёд — как у эталона)
    for sx, sd in [(-1, 242), (1, 243)]:
        px = CX + sx * 70
        foot = ellipse_pts(px, 1286, 34, 26, 12, rot=sx * 12)
        s.append(shape(foot, CAT, blob(T(ellipse_pts(px, 1292, 26, 20, 10), sx * 4, 0), CAT_SH, .5), w=4.6, seed=sd))
        s.append(blob(ellipse_pts(px + sx * 3, 1294, 13, 10, 10, rot=sx * 10), "#e8823a"))
        for k in range(3):
            ang = math.radians(-90 + (k - 1) * 42 + sx * 10)
            s.append(blob(ellipse_pts(px + sx * 3 + math.cos(ang) * 19, 1294 + math.sin(ang) * 15, 5, 4.4, 8), "#e8823a"))
    # передние лапки
    for sx, sd in [(-1, 244), (1, 245)]:
        fx = CX + sx * 26
        paw = [(fx - 20, 1306), (fx - 18, 1250), (fx + 18, 1250), (fx + 20, 1306)]
        s.append(shape(paw, CAT, blob([(fx + sx * 6, 1250), (fx + 20 * sx, 1250), (fx + 20 * sx, 1306), (fx + sx * 8, 1306)], CAT_SH, .7),
                       w=4.6, seed=sd))
        for k in (-7, 7):
            s.append(line([(fx + k, 1294), (fx + k, 1306)], 2.2, seed=sd + k))
    # голова: широкая, пушистые щёки
    hd = [(744, 1060), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (920, 1112), (880, 1146), (790, 1146), (752, 1112)]
    hp = fur(hd, 10, 5, seed=23)
    inner = blob([(880, 990), (940, 1050), (930, 1150), (860, 1150), (900, 1080)], CAT_SH, .85)
    inner += blob([(780, 1004), (836, 994), (880, 1004), (860, 1020), (800, 1022)], CAT_FUR, .55)
    s.append(shape(hp, CAT, inner, w=5.2, seed=250, id="cat_head"))
    # уши: правое (от зрителя) стоит, левое загнуто вниз
    re_ = [(872, 1004), (904, 930, 1), (928, 1030)]
    s.append(shape(fur(re_, 5, 4, seed=24), CAT, blob([(882, 1006), (904, 952), (916, 1020)], "#9b6150"), w=4.6, seed=251, id="cat_ear_R"))
    s.append(line([(890, 994), (902, 970)], 2, "#d79a84", seed=252, op=.8))
    le = [(760, 1018), (764, 976), (790, 956, 1), (802, 994), (784, 980), (748, 1004, 1)]
    s.append(shape(le, CAT, blob([(764, 980), (790, 958), (800, 990), (780, 978)], CAT_FUR, .6), w=4.6, seed=253, id="cat_ear_L"))
    s.append(line([(752, 1002), (772, 986), (794, 976)], 2.6, seed=254))
    # глаза: большие зелёные, вертикальный зрачок, блик; веко-шерсть для моргания
    for nm, ex, sd in [("L", CX - 44, 255), ("R", CX + 44, 256)]:
        ep = ellipse_pts(ex, 1072, 33, 37, 14)
        cid = clip_of(ep)
        s.append(f'<g id="cat_eye_{nm}"><path d="{fill_d(ep)}" fill="#b8e04a"/>')
        s.append(f'<g clip-path="url(#{cid})">')
        s.append(blob(ellipse_pts(ex, 1050, 34, 20, 10), "#8fb83a", .9))
        s.append(blob(ellipse_pts(ex, 1098, 26, 10, 10), "#d8f27a", .6))
        s.append(f'<g id="cat_pupil_{nm}"><ellipse cx="{ex}" cy="1074" rx="11" ry="23" fill="#0f0d14"/>'
                 f'<circle cx="{ex + 6}" cy="1060" r="5.2" fill="#fff"/><circle cx="{ex - 6}" cy="1088" r="2" fill="#fff" opacity=".8"/></g>')
        s.append(f'<g id="cat_lid_{nm}" class="cat_lid_up" transform="translate(0 -84)"><rect x="{ex - 40}" y="990" width="80" height="84" fill="{CAT}"/>'
                 + line([(ex - 36, 1070), (ex, 1076), (ex + 36, 1070)], 4.6, seed=sd) + "</g>")
        s.append(f'<g id="cat_lidlo_{nm}" class="cat_lid_lo" transform="translate(0 48)"><rect x="{ex - 40}" y="1072" width="80" height="50" fill="{CAT}"/></g>')
        s.append(f'</g><path d="{ink_closed(ep, 4.4, seed=sd + 3)}" fill="{INK}"/></g>')
    # полоски на щеках — по две
    for sx in (-1, 1):
        for k, dy in enumerate((0, 14)):
            x0 = CX + sx * 74
            s.append(line([(x0, 1100 + dy), (x0 + sx * 30, 1094 + dy + k * 3)], 5.2, "#e8823a", seed=260 + k + sx, taper=.3, wmin=.5))
    # нос, рот, усы
    s.append(shape([(826, 1106), (846, 1106), (836, 1118)], "#c47a72", w=2.6, seed=262))
    s.append(line([(836, 1118), (836, 1124)], 2.4, seed=263))
    s.append(line([(820, 1124), (828, 1132), (836, 1124), (844, 1132), (852, 1124)], 3, seed=264))
    for sx in (-1, 1):
        for k, (dy, dl) in enumerate([(-4, -8), (4, 2), (12, 12)]):
            x0 = CX + sx * 60
            s.append(line([(x0, 1114 + dy), (x0 + sx * 50, 1110 + dy + dl * .4), (x0 + sx * 96, 1106 + dy + dl)], 1.8, "#cfc8dc",
                          seed=270 + k + sx, op=.75))
    s.append("</g>")
    return "".join(s)


# ───────────────────────────── пол: коврик, тапки ─────────────────────────────
def rug_slippers():
    s = []
    rug = [(150, 1560), (960, 1556), (1030, 1640), (1080, 1880), (1080, 1930, 1), (20, 1930, 1), (60, 1700), (100, 1610)]
    inner = '<rect x="0" y="1540" width="1100" height="400" fill="url(#pRugBorder)"/>'
    inn = [(200, 1590), (920, 1586), (970, 1660), (1010, 1930), (80, 1930), (120, 1680), (150, 1620)]
    inner += f'<path d="{fill_d(inn)}" fill="url(#pRug)"/>'
    inner += f'<path d="{ink_closed(inn, 3.2, seed=280)}" fill="#3a1a18" opacity=".8"/>'
    inner += blob([(150, 1560), (960, 1556), (1000, 1600), (120, 1604)], "#000", .18)
    s.append(blob([(140, 1556), (970, 1550), (1080, 1640), (1080, 1600), (100, 1600)], "#000", .25, blur(5)))
    s.append(shape(rug, "#97423a", inner, w=5, seed=281))
    # бахрома дальнего края
    for x in np.arange(170, 950, 14):
        s.append(line([(x, 1560), (x - 1, 1544)], 2.6, "#d8c49a", seed=int(x), taper=.4))
    # тапок 1 — стоит
    s.append(blob(ellipse_pts(372, 1716, 92, 22, 12), "#000", .35, blur(5)))
    sl1 = [(282, 1700), (300, 1666), (380, 1650), (450, 1664), (470, 1696), (440, 1720), (320, 1724)]
    s.append(shape(sl1, "#e4d9c3", blob([(282, 1700), (470, 1696), (440, 1724), (320, 1728)], "#bfb39b"), w=4.6, seed=282))
    up = [(300, 1690), (316, 1662), (380, 1648), (414, 1660), (396, 1690), (340, 1700)]
    s.append(shape(up, "#5f6f96", blob([(300, 1690), (396, 1690), (380, 1700), (310, 1700)], "#46557a") +
                   line([(330, 1670), (360, 1662)], 2, "#8c9cc4", seed=283), w=4.6, seed=284))
    s.append(shape([(410, 1666), (450, 1668), (462, 1690), (420, 1694)], "#3a3036", w=3.4, seed=285))
    # тапок 2 — перевёрнут на бок
    s.append(blob(ellipse_pts(570, 1780, 90, 20, 12), "#000", .35, blur(5)))
    sl2 = [(486, 1770), (500, 1736), (560, 1720), (650, 1740), (664, 1772), (600, 1790), (520, 1790)]
    s.append(shape(sl2, "#5f6f96", blob([(486, 1770), (664, 1772), (600, 1792), (520, 1792)], "#46557a"), w=4.6, seed=286))
    sole = [(490, 1772), (520, 1786), (600, 1788), (662, 1774), (664, 1792), (600, 1804), (520, 1802), (486, 1786)]
    s.append(shape(sole, "#cbbfa6", "", w=4, seed=287))
    s.append(line([(520, 1746), (560, 1736), (610, 1742)], 2.2, "#8c9cc4", seed=288))
    # носок, скомканный
    sock = [(800, 1700), (830, 1680), (880, 1690), (900, 1712), (870, 1730), (820, 1730)]
    s.append(blob(ellipse_pts(850, 1728, 56, 12, 10), "#000", .3, blur(4)))
    s.append(shape(sock, "#d7d4ce", blob([(800, 1712), (900, 1712), (870, 1734), (820, 1734)], "#aaa59c") +
                   blob([(860, 1684), (884, 1690), (896, 1708), (874, 1704)], "#c94b3c"), w=4.2, seed=289))
    s.append(line([(820, 1702), (850, 1712), (870, 1704)], 2.2, seed=290, op=.7))
    return "".join(s)


# ───────────────────────────── свет ─────────────────────────────
def gradients():
    DEFS.append("""
<linearGradient id="gSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c3c86"/><stop offset=".7" stop-color="#4f5fa6"/><stop offset="1" stop-color="#6f74a8"/></linearGradient>
<linearGradient id="gWallAO" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b2f22" stop-opacity=".35"/><stop offset=".25" stop-color="#3b2f22" stop-opacity="0"/><stop offset=".85" stop-color="#3b2f22" stop-opacity="0"/><stop offset="1" stop-color="#3b2f22" stop-opacity=".3"/></linearGradient>
<linearGradient id="gNight" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a64a8"/><stop offset=".55" stop-color="#6670b2"/><stop offset="1" stop-color="#4a5294"/></linearGradient>
<radialGradient id="gPhone" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(600 830) scale(470 420)"><stop offset="0" stop-color="#9cc6ff" stop-opacity=".75"/><stop offset=".25" stop-color="#6ea2f0" stop-opacity=".42"/><stop offset=".6" stop-color="#4a74c8" stop-opacity=".14"/><stop offset="1" stop-color="#4a74c8" stop-opacity="0"/></radialGradient>
<radialGradient id="gPhoneCore" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(612 800) scale(120 150)"><stop offset="0" stop-color="#e6f2ff" stop-opacity=".8"/><stop offset="1" stop-color="#9cc6ff" stop-opacity="0"/></radialGradient>
<radialGradient id="gFlame" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(1006 1092) scale(280 260)"><stop offset="0" stop-color="#ffb05a" stop-opacity=".85"/><stop offset=".2" stop-color="#ff8a3a" stop-opacity=".45"/><stop offset=".55" stop-color="#d0602a" stop-opacity=".14"/><stop offset="1" stop-color="#d0602a" stop-opacity="0"/></radialGradient>
<radialGradient id="gClock" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(98 1150) scale(190 120)"><stop offset="0" stop-color="#ff5a3c" stop-opacity=".5"/><stop offset="1" stop-color="#ff5a3c" stop-opacity="0"/></radialGradient>
<radialGradient id="gMoon" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(712 196) scale(120 120)"><stop offset="0" stop-color="#fff6d8" stop-opacity=".7"/><stop offset=".4" stop-color="#c8d4ff" stop-opacity=".25"/><stop offset="1" stop-color="#c8d4ff" stop-opacity="0"/></radialGradient>
<radialGradient id="gVig" cx="540" cy="900" r="1250" gradientUnits="userSpaceOnUse"><stop offset=".45" stop-color="#fff"/><stop offset="1" stop-color="#2a2440"/></radialGradient>
<filter id="fGrain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="4" result="n"/><feColorMatrix type="matrix" values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  .9 .9 .9 0 -1.1"/></filter>
<filter id="fSoft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>
""")


def lights():
    """Над ночью: свет осветлением (screen), рим-свет резкой формой по силуэту, светящееся поверх."""
    s = []
    # лунный свет из окна: пятна на стене и пледе
    s.append(f'<g style="mix-blend-mode:screen" opacity=".22" {blur(16)}>'
             + blob([(560, 760), (840, 770), (760, 1190), (430, 1170)], "#6f86c8")
             + blob([(860, 770), (1060, 780), (1080, 1180), (800, 1180)], "#6f86c8") + "</g>")
    # экран телефона: большое пятно и ядро
    s.append(f'<g id="phone_glow" style="mix-blend-mode:screen"><rect width="{W}" height="{H}" fill="url(#gPhone)"/>'
             f'<rect width="{W}" height="{H}" fill="url(#gPhoneCore)"/></g>')
    # огонёк кота
    s.append(f'<g id="flame_glow" style="mix-blend-mode:screen"><rect width="{W}" height="{H}" fill="url(#gFlame)"/></g>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#gClock)" style="mix-blend-mode:screen"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#gMoon)" style="mix-blend-mode:screen"/>')
    return "".join(s)


def rim_lights():
    """Резкий рим-свет экрана на лице, волосах, руке; оранжевый — на коте от огонька."""
    s = ['<g id="rim_phone" style="mix-blend-mode:screen">']
    # лицо: правая сторона (к экрану) — заплатка формой «cel», по маске лица
    fc = uid()
    DEFS.append(f'<clipPath id="{fc}"><path d="{fill_d(FACE)}" transform="{head_tf()}"/></clipPath>')
    s.append(f'<g clip-path="url(#{fc})"><g transform="{head_tf()}">'
             + blob([(40, -130), (130, -130), (130, 130), (60, 126), (90, 70), (98, 10), (70, -60)], "#7aa6f0", .55)
             + blob([(96, -60), (130, -60), (130, 90), (104, 60), (110, 10)], "#cfe2ff", .55) + "</g></g>")
    # волосы спереди
    s.append(f'<g transform="{head_tf()}">' + blob([(80, -86), (98, -62), (108, -40), (96, -50), (78, -78)], "#9fc0ff", .6) + "</g>")
    # шея/ворот
    s.append(blob([(470, 960), (486, 1030), (476, 1034), (462, 970)], "#7aa6f0", .45))
    # рука и рукав: левая кромка, обращённая к экрану
    s.append(blob([(626, 952), (612, 1030), (604, 1100), (618, 1100), (628, 1030), (640, 956)], "#7aa6f0", .5))
    s.append(f'<g transform="translate({PX} {PY}) rotate({PR})">'
             + blob([(-74, -16), (-56, -20), (-50, 20), (-58, 70), (-66, 60), (-70, 20)], "#bcd6ff", .55, 'id="thumb_rim"')
             + blob([(-48, 56), (-36, 52), (-38, 110), (-48, 120)], "#7aa6f0", .45) + "</g>")
    s.append("</g>")
    # кот: тёплый рим справа от огонька, холодный слева от экрана
    s.append('<g style="mix-blend-mode:screen">')
    s.append(blob(fur([(920, 1020), (932, 1060), (924, 1112), (900, 1140), (912, 1100), (918, 1060)], 5, 4, seed=31), "#ff9a4a", .55))
    s.append(blob(fur([(914, 1180), (928, 1240), (920, 1290), (906, 1290), (914, 1240), (904, 1190)], 5, 4, seed=32), "#ff9a4a", .5))
    s.append(blob([(904, 940), (924, 1030), (914, 1028), (902, 962)], "#ff9a4a", .5))
    s.append(blob([(990, 1150), (1024, 1170), (1014, 1230), (1004, 1180)], "#ffb060", .6))
    s.append(blob(fur([(752, 1020), (742, 1062), (752, 1110), (762, 1100), (754, 1062), (762, 1024)], 4, 4, seed=33), "#8fb0f0", .45))
    s.append(blob([(758, 1170), (746, 1236), (758, 1236), (766, 1176)], "#8fb0f0", .35))
    s.append("</g>")
    return "".join(s)


def glowing():
    s = []
    # луна с кратерами и звёзды — поверх ночи (окно)
    s.append(shape(ellipse_pts(712, 196, 34, 34, 14), "#fbf3d6", blob(ellipse_pts(722, 206, 30, 30, 12), "#e4d9b0", .9) +
                   blob(ellipse_pts(700, 186, 7, 6, 8), "#d8cba0") + blob(ellipse_pts(724, 214, 5, 4, 8), "#d8cba0") +
                   blob(ellipse_pts(716, 180, 3.5, 3, 8), "#d8cba0"), w=3, seed=310, ink_color="#3a3d66"))
    rs = np.random.RandomState(11)
    for _ in range(26):
        x, y = rs.uniform(640, 1030), rs.uniform(130, 380)
        if 670 < x < 760 and 150 < y < 240 or 826 < x < 846 or 298 < y < 320:
            continue
        r = rs.uniform(1, 2.6)
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#eef0ff" opacity="{rs.uniform(.5, 1):.2f}"/>')
    s.append(f'<path d="M960 170 l3 9 l9 3 l-9 3 l-3 9 l-3 -9 l-9 -3 l9 -3z" fill="#fffbe6"/>')
    # светящиеся окна дома напротив (часть тёмные), тёплые, с силуэтами штор
    lit = [(648, 462), (694, 462), (786, 404), (878, 404), (924, 520), (970, 578), (648, 636), (740, 520), (1016, 462)]
    for i, (x, y) in enumerate(lit):
        if 826 < x < 846:
            continue
        col = ["#ffd27a", "#ffe6a8", "#ffb85c"][i % 3]
        s.append(f'<rect x="{x}" y="{y}" width="26" height="34" fill="{col}"/>')
        if i % 2 == 0:
            s.append(f'<rect x="{x}" y="{y}" width="9" height="34" fill="#c98a3c" opacity=".7"/>')
        s.append(f'<rect x="{x - 8}" y="{y - 8}" width="42" height="50" fill="{col}" opacity=".18" {blur(6)}/>')
    # цифры часов
    s.append(clock_digits())
    s.append(f'<g {blur(4)} opacity=".7" style="mix-blend-mode:screen">{clock_digits().replace("clock_digits", "clock_digits_glow")}</g>')
    # кромка экрана телефона
    s.append(f'<g transform="translate({PX} {PY}) rotate({PR})" id="screen_edge">'
             + line([(-53, -78), (-55, 0), (-54, 80)], 4.4, "#cfe6ff", taper=.3, wmin=.4, seed=320)
             + f'<path d="M-56 -80 L-58 82" stroke="#bfe0ff" stroke-width="10" opacity=".5" {blur(5)}/></g>')
    # глаза кота отсвечивают
    for ex in (CX - 44, CX + 44):
        s.append(f'<ellipse cx="{ex}" cy="1072" rx="30" ry="34" fill="#c6f05a" opacity=".22" {blur(8)} style="mix-blend-mode:screen"/>')
    return "".join(s)


def build():
    patterns()
    gradients()
    base = "".join([
        wall(), window(), curtains(), poster_shelf(), baseboard_floor(), rug_slippers(), table_clock(),
        sofa_back(), sofa_arm(), pillow(), hood_body(), head(), sofa_front(), plaid(), phone_arm(), cat(),
    ])
    night = (f'<rect width="{W}" height="{H}" fill="url(#gNight)" style="mix-blend-mode:multiply"/>'
             f'<rect width="{W}" height="{H}" fill="url(#gVig)" style="mix-blend-mode:multiply"/>')
    top = lights() + rim_lights() + glowing()
    grain = f'<rect id="grain" width="{W}" height="{H}" filter="url(#fGrain)" opacity=".5" style="mix-blend-mode:overlay"/>'
    svg = (f'<svg id="scene" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{"".join(DEFS)}</defs><g id="base">{base}</g><g id="night">{night}</g><g id="light">{top}</g>{grain}</svg>')
    return svg


if __name__ == "__main__":
    svg = build()
    here = __file__.rsplit("/", 1)[0]
    html = open(f"{here}/template.html").read().replace("<!--SVG-->", svg)
    open(f"{here}/scene.html", "w").write(html)
    print("scene.html", len(html) // 1024, "KB")
