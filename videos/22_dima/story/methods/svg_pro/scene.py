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
REG = {}
_uid = [0]


def uid(p="c"):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


def shape(pts, fill, inner="", w=5.0, seed=0, ink=True, id=None, attrs="", var=0.28, weight=0.45, ink_color=INK):
    """Заливка + внутреннее (тени, узор) по маске силуэта + тушь переменной толщины."""
    d = fill_d(pts)
    if id:
        REG[id] = pts
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


def rim(pts, color, dx, dy, op=1.0, tf=None, id=None, cut=()):
    """Рим-свет: полумесяц по краю силуэта = фигура минус та же фигура со сдвигом (резкая cel-граница).
    Кладётся в группу со screen: чёрный «резец» ничего не осветляет."""
    d = fill_d(pts)
    c = clip_of(pts)
    gid = f' id="{id}"' if id else ""
    fill = f"url(#{color})" if color.startswith("g") else color
    g = (f'<g{gid} clip-path="url(#{c})" opacity="{op}"><path d="{d}" fill="{fill}"/>'
         f'<path d="{d}" transform="translate({dx} {dy})" fill="#000"/>'
         + "".join(f'<path d="{fill_d(c_)}" fill="#000"/>' for c_ in cut) + '</g>')
    return f'<g transform="{tf}">{g}</g>' if tf else g


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
    s.append(line([(470, 40), (468, 300), (472, 640)], 2.2, "#9d8462", seed=11, op=.8))
    # потолок и карниз-плинтус
    s.append(f'<rect width="{W}" height="34" fill="#d9d2c4"/><rect y="24" width="{W}" height="10" fill="#bdb4a3"/>')
    s.append(line([(-10, 34), (540, 35), (1090, 33)], 4.4, seed=12, taper=.2, wmin=.6))
    s.append(f'<rect y="36" width="{W}" height="40" fill="#3b2f22" opacity=".18" {blur(8)}/>')
    s.append(blob(ellipse_pts(860, 1330, 90, 26, 10, jitter=.15, seed=3), "#a68d68", .35))
    # стикеры у полки — каракули без букв
    for i, (x, y, r, c) in enumerate([(90, 760, -6, "#f2d65a"), (134, 778, 5, "#f5a6b8"), (100, 812, 3, "#9fd6a8")]):
        sp = T(rect_pts(-20, -20, 20, 20), x, y, rot=r)
        s.append(shape(sp, c, blob(T([(-20, 12), (20, 12), (20, 20), (-20, 20)], x, y, rot=r), "#000", .12), w=2.6, seed=60 + i))
        s.append(line(T([(-12, -6), (-2, -9), (8, -5), (12, -8)], x, y, rot=r), 1.8, "#3a3550", seed=63 + i, op=.8))
        s.append(line(T([(-12, 3), (6, 1)], x, y, rot=r), 1.6, "#3a3550", seed=66 + i, op=.8))
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
    s.append(blob([(-20, 1452), (170, 1452), (166, 1478), (-20, 1478)], "#2b1d14", .45, blur(6)))
    wood, dk = "#8a6346", "#64462f"
    for x in [4, 120]:
        s.append(shape([(x, 1205, 1), (x + 20, 1205, 1), (x + 18, 1462, 1), (x + 3, 1462, 1)], wood, w=4, seed=x,
                       inner=f'<rect x="{x + 12}" y="1200" width="10" height="270" fill="{dk}"/>'))
    s.append(shape(rect_pts(-12, 1345, 150, 1366), wood, f'<rect x="-12" y="1358" width="200" height="10" fill="{dk}"/>', w=4, seed=110))
    # книги и кружка на нижней полке
    s.append(shape(rect_pts(-4, 1322, 96, 1345, 3), "#4a6d8e", '<rect x="-4" y="1337" width="120" height="8" fill="#365470"/>', w=3.4, seed=111))
    s.append(shape(rect_pts(4, 1302, 86, 1322, 3), "#b5563f", '<rect x="4" y="1315" width="100" height="8" fill="#8e3f2c"/>', w=3.4, seed=112))
    s.append(shape([(100, 1300), (138, 1300), (136, 1345), (102, 1345)], "#e3dccb", w=3.4, seed=113,
                   inner='<rect x="122" y="1296" width="22" height="52" fill="#c4bba7"/>'))
    s.append(f'<path d="M102 1310 C86 1310 86 1336 102 1334" stroke="{INK}" stroke-width="4" fill="none"/>')
    # столешница
    top = [(-14, 1186, 1), (154, 1186, 1), (158, 1212, 1), (-14, 1212, 1)]
    s.append(shape(top, wood, f'<rect x="-14" y="1202" width="180" height="12" fill="{dk}"/>'
                   + line([(10, 1194), (80, 1196), (140, 1193)], 1.6, "#6e4f37", seed=114), w=4.4, seed=115))
    # часы
    s.append(blob([(4, 1186), (150, 1186), (146, 1196), (8, 1196)], "#1b120c", .45, blur(3)))
    body = rect_pts(2, 1106, 150, 1188, 12)
    s.append(shape(body, "#26222c", blob(rect_pts(2, 1172, 150, 1188, 6), "#17141c") +
                   blob([(10, 1112), (142, 1112), (138, 1118), (14, 1118)], "#4a4554", .8), w=4.4, seed=116, id="clock"))
    s.append(shape(rect_pts(12, 1118, 140, 1172, 6), "#1a0a0e", w=3, seed=117))
    return "".join(s)


SEG = {"0": "abcdef", "1": "bc", "4": "fgbc", "7": "abc"}


def seven_seg(ch, x, y, w=22, h=40, t=5.6, glow=False):
    """Цифра из семи сегментов (рисует код). Наклон ~6°."""
    hs = h / 2
    g = t * .35
    segs = {
        "a": [(x + g, y), (x + w - g, y), (x + w - t - g, y + t), (x + t + g, y + t)],
        "d": [(x + t + g, y + h - t), (x + w - t - g, y + h - t), (x + w - g, y + h), (x + g, y + h)],
        "g": [(x + t * .5 + g, y + hs), (x + t + g, y + hs - t / 2), (x + w - t - g, y + hs - t / 2), (x + w - t * .5 - g, y + hs),
              (x + w - t - g, y + hs + t / 2), (x + t + g, y + hs + t / 2)],
        "f": [(x, y + g), (x + t, y + t + g), (x + t, y + hs - t / 2 - g), (x, y + hs - g)],
        "e": [(x, y + hs + g), (x + t, y + hs + t / 2 + g), (x + t, y + h - t - g), (x, y + h - g)],
        "b": [(x + w, y + g), (x + w, y + hs - g), (x + w - t, y + hs - t / 2 - g), (x + w - t, y + t + g)],
        "c": [(x + w, y + hs + g), (x + w, y + h - g), (x + w - t, y + h - t - g), (x + w - t, y + hs + t / 2 + g)],
    }
    out = []
    for k in "abcdefg":
        on = k in SEG[ch]
        if glow and not on:
            continue
        d = "M" + "L".join(f"{px - (py - y - h) * .1:.1f} {py:.1f}" for px, py in segs[k]) + "Z"
        out.append(f'<path d="{d}" fill="{"#ff5a3c" if on else "#3a1416"}" opacity="{1 if on else .22}"/>')
    return "".join(out)


def clock_digits(glow=False, id="clock_digits"):
    s = [f'<g id="{id}">']
    x = 18
    for ch in "01:47":
        if ch == ":":
            s.append(f'<rect x="{x + 3}" y="1131" width="5.5" height="5.5" fill="#ff5a3c"/>'
                     f'<rect x="{x + 1}" y="1150" width="5.5" height="5.5" fill="#ff5a3c"/>')
            x += 13
            continue
        s.append(seven_seg(ch, x, 1124, glow=glow))
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
HX, HY, HR = 446, 878, -7  # центр головы и наклон


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
    s.append(shape(nk, SKIN, blob([(420, 960), (474, 958), (480, 1000), (420, 1006)], SKIN_SH, .95) +
                   blob([(420, 960), (440, 960), (440, 1040), (418, 1040)], SKIN_SH2, .6), w=4.6, seed=146, id="dima_neck"))
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
PX, PY, PR = 668, 818, -11


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
    # сам телефон (спинкой к зрителю, в 3/4): торец слева — сторона экрана
    back = rect_pts(-46, -98, 46, 98, 18)
    side = [(-46, -94), (-60, -88), (-62, 88), (-46, 96)]
    s.append(shape(side, "#2e2e3a", "", w=3.6, seed=187, id="phone_side"))
    inner = blob([(14, -98), (46, -98), (46, 98), (26, 98)], "#24242c", .95)
    inner += blob([(-46, -98), (-30, -98), (-32, 98), (-46, 98)], "#4c4c5c", .75)
    inner += blob([(-24, -98), (-14, -98), (-18, 98), (-28, 98)], "#3a3a48", .5)
    s.append(shape(back, "#1a1a21", inner, w=4.8, seed=188, id="phone"))
    cam = rect_pts(-38, -90, 4, -46, 11)
    s.append(shape(cam, "#34343f", blob(rect_pts(-38, -64, 4, -46, 6), "#26262f") + blob([(-36, -88), (2, -88), (0, -84), (-34, -84)], "#55556a"),
                   w=3.6, seed=189, id="phone_cam"))
    for (lx, ly) in [(-25, -78), (-25, -57), (-8, -67)]:
        s.append(shape(ellipse_pts(lx, ly, 9.5, 9.5, 10), "#55556a", w=2.8, seed=int(abs(lx * ly)) % 97,
                       inner=f'<circle cx="{lx}" cy="{ly}" r="6.6" fill="#0c0c12"/><circle cx="{lx}" cy="{ly}" r="3.6" fill="#1d2848"/>'
                             f'<circle cx="{lx - 2.4}" cy="{ly - 2.4}" r="1.8" fill="#a9bdf0"/>'))
    s.append('<circle cx="-8" cy="-82" r="3.2" fill="#e8e0c8"/><circle cx="-8" cy="-52" r="2.8" fill="#121218"/>')
    # кисть: ладонь под телефоном, тыльная сторона справа; пальцы обхватывают правый край, кончики — на спинке
    palm = [(-70, 126), (-56, 92), (-20, 82), (30, 86), (62, 70), (78, 30), (84, -14), (66, -30), (56, 10), (52, 60), (40, 112), (0, 140),
            (-40, 146)]
    s.append(shape(palm, SKIN, blob([(-70, 120), (60, 100), (40, 150), (-60, 150)], SKIN_SH, .9) +
                   blob([(70, -30), (90, -20), (86, 80), (66, 70)], SKIN_SH, .8) +
                   line([(-30, 120), (0, 126), (24, 116)], 2.2, seed=184, op=.6), w=4.8, seed=185, id="dima_palm"))
    for i, y in enumerate([-24, 4, 32, 60]):
        fp = band([(70, y + 22), (52, y + 8), (34, y + 2), (16, y + 4)], 25, 21, cap=True)
        s.append(shape(fp, SKIN, blob([(10, y + 12), (80, y + 18), (80, y + 40), (10, y + 30)], SKIN_SH, .8), w=4.2, seed=190 + i,
                       id=f"dima_finger{i}"))
        s.append(line([(48, y + 1), (46, y + 14)], 2, seed=195 + i, op=.6))
    # большой палец: от ладони вверх по левому краю, кончик заходит на экран (группа для пролистывания)
    s.append('<g id="dima_thumb">')
    th = band([(-44, 76), (-60, 44), (-68, 12), (-62, -14)], 26, 21, cap=True)
    s.append(shape(th, SKIN, blob([(-90, 0), (-66, 0), (-58, 90), (-90, 90)], SKIN_SH, .75), w=4.4, seed=199, id="dima_thumb_shape"))
    s.append(line([(-58, -14), (-50, -9)], 2, seed=200, op=.7))
    s.append("</g>")
    s.append("</g>")
    return "".join(s)


# ───────────────────────────── плед ─────────────────────────────
def plaid():
    s = []
    top = [(302, 1296, 1), (308, 1206), (350, 1168), (420, 1132), (480, 1112), (540, 1108), (610, 1120), (690, 1146), (770, 1164),
           (840, 1150), (912, 1166), (980, 1136), (1040, 1124), (1100, 1140, 1), (1100, 1300, 1), (700, 1306), (420, 1300)]
    inner = []
    # тени под складками и от тела
    inner.append(blob([(300, 1230), (540, 1180), (700, 1200), (900, 1210), (1100, 1200), (1100, 1310), (300, 1310)], "#203a24", .35))
    inner.append(blob([(300, 1200), (360, 1170), (400, 1300), (300, 1300)], "#203a24", .3))
    inner.append(line([(340, 1190), (370, 1230), (372, 1280)], 3.2, seed=209, op=.85))
    inner.append(blob([(690, 1146), (770, 1164), (760, 1230), (700, 1200)], "#203a24", .3))
    inner.append(blob([(960, 1140), (1040, 1124), (1100, 1140), (1100, 1220), (1010, 1190)], "#203a24", .3))
    inner.append(blob([(470, 1130), (560, 1112), (610, 1124), (560, 1140), (500, 1150)], "#f4f8d0", .18))
    for i, st in enumerate([[(440, 1160), (480, 1200), (520, 1250)], [(600, 1150), (640, 1190), (660, 1250)],
                            [(760, 1180), (800, 1210), (790, 1270)], [(980, 1160), (1010, 1210), (1040, 1260)],
                            [(860, 1180), (900, 1200)]]):
        inner.append(line(st, 3.4, seed=210 + i, op=.85))
    s.append(shape(top, "url(#pPlaidTop)", "".join(inner), w=5.4, seed=215, id="plaid_top"))
    # свисающий край с бахромой
    front = [(304, 1290, 1), (700, 1300), (1100, 1290, 1), (1100, 1428, 1), (1040, 1418), (960, 1434), (880, 1416), (790, 1436),
             (700, 1414), (610, 1430), (520, 1408), (440, 1396), (360, 1404), (308, 1390)]
    inner = []
    for i, (x0, x1) in enumerate([(470, 520), (650, 700), (840, 880), (990, 1040)]):
        inner.append(blob([(x0, 1300), (x0 + 30, 1300), (x1 + 10, 1440), (x1 - 30, 1440)], "#1b301e", .45))
        inner.append(line([(x0 + 10, 1302), (x0 + 22, 1360), (x1 - 8, 1430)], 3.2, seed=220 + i, op=.85))
    inner.append(blob([(300, 1290), (1100, 1290), (1100, 1312), (300, 1312)], "#1b301e", .4))
    inner.append(blob([(304, 1290), (340, 1290), (350, 1410), (304, 1400)], "#1b301e", .4))
    s.append(shape(front, "url(#pPlaidFront)", "".join(inner), w=5.4, seed=225, id="plaid_front"))
    # бахрома
    S_ = sample([(310, 1392), (360, 1406), (440, 1398), (520, 1410), (610, 1432), (700, 1416), (790, 1438), (880, 1418), (960, 1436),
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


TAIL_C = [(900, 1272), (970, 1266), (1018, 1236), (1042, 1190), (1040, 1140), (1018, 1104), (984, 1090), (956, 1102), (950, 1128),
          (964, 1142), (982, 1134), (982, 1116)]
FLAME_BASE = (990, 1088)


def flame_pts(k=1.0):
    bx, by = FLAME_BASE
    P = [(-22, 4), (-26, -18), (-16, -40), (-14, -62), (-4, -50), (2, -86, 1), (12, -58), (22, -70, 1), (26, -40), (24, -12), (16, 4), (0, 10)]
    return [(bx + x * k, by + y * k) + ((1,) if len(q) > 2 else ()) for q in P for x, y in [q[:2]]]


def cat():
    s = ['<g id="cat">']
    # хвост: за телом справа, закручен завитком, огонёк на верхней дуге (группа — для покачивания)
    s.append('<g id="cat_tail">')
    tp = band(TAIL_C, 46, 13, step=7)
    tp = fur(tp, 5, 7, seed=21)
    s.append(shape(tp, CAT, blob([(1006, 1110), (1046, 1150), (1036, 1270), (980, 1276)], CAT_SH, .85) +
                   line([(986, 1240), (1004, 1206), (1010, 1170)], 2.4, CAT_FUR, seed=231, op=.9) +
                   line([(966, 1126), (970, 1114), (982, 1110)], 2.4, INK, seed=232, op=.9), w=4.8, seed=230, id="cat_tail_shape"))
    s.append('<g id="cat_flame">')
    s.append(shape(flame_pts(1.0), "#ff8a2a", blob(flame_pts(.68), "#ffbe55"), w=3.4, seed=233, ink_color="#7a2a10", var=.2))
    s.append(blob([(FLAME_BASE[0] - 8, FLAME_BASE[1] + 2), (FLAME_BASE[0] - 6, FLAME_BASE[1] - 22), (FLAME_BASE[0] + 2, FLAME_BASE[1] - 40),
                   (FLAME_BASE[0] + 8, FLAME_BASE[1] - 20), (FLAME_BASE[0] + 6, FLAME_BASE[1] + 2)], "#fff2c0"))
    s.append("</g></g>")
    # тело — грушей, мягкий пушистый край
    body = [(760, 1296), (744, 1240), (756, 1180), (790, 1142), (880, 1142), (916, 1180), (928, 1240), (912, 1296)]
    bp = fur(body, 7, 7, seed=22)
    inner = blob([(860, 1140), (930, 1180), (930, 1300), (874, 1300), (888, 1220)], CAT_SH, .9)
    inner += blob([(800, 1172), (836, 1162), (872, 1172), (862, 1240), (836, 1262), (810, 1240)], CAT_FUR, .5)
    for i, st in enumerate([[(816, 1190), (826, 1208)], [(852, 1192), (846, 1212)], [(834, 1214), (836, 1236)], [(806, 1222), (814, 1238)]]):
        inner += line(st, 2.2, "#6a6380", seed=240 + i, op=.8)
    s.append(shape(bp, CAT, inner, w=5, seed=241, id="cat_body"))
    # задние лапы с оранжевыми подушечками (как у эталона)
    for sx, sd in [(-1, 242), (1, 243)]:
        px = CX + sx * 70
        foot = ellipse_pts(px, 1286, 34, 26, 12, rot=sx * 12)
        s.append(shape(foot, CAT, blob(T(ellipse_pts(px, 1292, 26, 20, 10), sx * 4, 0), CAT_SH, .5), w=4.6, seed=sd))
        s.append(blob(ellipse_pts(px + sx * 3, 1296, 13, 10, 10, rot=sx * 10), "#e8823a"))
        for k in range(3):
            ang = math.radians(-90 + (k - 1) * 42 + sx * 10)
            s.append(blob(ellipse_pts(px + sx * 3 + math.cos(ang) * 19, 1296 + math.sin(ang) * 15, 5, 4.4, 8), "#e8823a"))
    # передние лапки
    for sx, sd in [(-1, 244), (1, 245)]:
        fx = CX + sx * 25
        paw = [(fx - 20, 1306, 1), (fx - 19, 1252), (fx + 19, 1252), (fx + 20, 1306, 1)]
        s.append(shape(paw, CAT, blob([(fx + sx * 6, 1250), (fx + 20 * sx, 1250), (fx + 20 * sx, 1306), (fx + sx * 8, 1306)], CAT_SH, .7),
                       w=4.6, seed=sd))
        for k in (-7, 7):
            s.append(line([(fx + k, 1294), (fx + k, 1306)], 2.2, seed=sd + k))
    # уши за головой: правое (от зрителя) стоит, левое загнуто вниз
    re_ = [(864, 1010), (902, 924, 1), (930, 1034)]
    s.append(shape(re_, CAT, blob([(878, 1010), (902, 948), (918, 1024)], "#9b6150") +
                   line([(888, 1000), (900, 968)], 2, "#d79a84", seed=252, op=.8), w=4.8, seed=251, id="cat_ear_R"))
    # левое ухо: обычное ухо с розовым внутри, верхушка загнута наружу-вниз пушистой «шапочкой» (как у эталона)
    ear = [(748, 1032, 1), (742, 990), (746, 958), (770, 942), (798, 952), (812, 1004, 1)]
    s.append(shape(ear, CAT, blob([(758, 1022), (768, 972), (804, 1004)], "#9b6150") +
                   line([(764, 1010), (772, 984)], 2, "#d79a84", seed=256, op=.8), w=4.6, seed=253))
    flap = [(732, 1000, 1), (736, 966), (754, 944), (782, 938), (802, 954), (788, 970), (766, 968), (748, 980)]
    s.append(shape(fur(flap, 4, 5, seed=26), CAT, blob([(736, 966), (754, 944), (782, 938), (790, 950), (760, 956)], CAT_FUR, .55),
                   w=4.6, seed=254, id="cat_ear_L"))
    # голова: широкая, пушистые щёки
    hd = [(744, 1062), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (922, 1112), (884, 1146), (788, 1146), (750, 1112)]
    hp = fur(hd, 8, 6, seed=23)
    inner = blob([(884, 990), (940, 1050), (930, 1150), (866, 1150), (902, 1080)], CAT_SH, .85)
    inner += blob([(784, 1004), (836, 994), (880, 1004), (862, 1018), (804, 1020)], CAT_FUR, .5)
    inner += blob([(806, 1108), (836, 1100), (866, 1108), (860, 1140), (812, 1140)], CAT_FUR, .35)
    s.append(shape(hp, CAT, inner, w=5.2, seed=250, id="cat_head"))
    # глаза: большие зелёные, вертикальный зрачок, блик; веко-шерсть для моргания
    for nm, ex, sd in [("L", CX - 44, 255), ("R", CX + 44, 256)]:
        ep = ellipse_pts(ex, 1072, 34, 38, 14)
        cid = clip_of(ep)
        s.append(f'<g id="cat_eye_{nm}"><path d="{fill_d(ep)}" fill="#b8e04a"/>')
        s.append(f'<g clip-path="url(#{cid})">')
        s.append(blob(ellipse_pts(ex, 1048, 36, 20, 10), "#86b236", .95))
        s.append(blob(ellipse_pts(ex, 1100, 26, 10, 10), "#dcf47e", .7))
        s.append(f'<g id="cat_pupil_{nm}"><ellipse cx="{ex}" cy="1074" rx="11.5" ry="24" fill="#0f0d14"/>'
                 f'<circle cx="{ex + 7}" cy="1059" r="5.6" fill="#fff"/><circle cx="{ex - 6}" cy="1090" r="2.2" fill="#fff" opacity=".8"/></g>')
        s.append(f'<g id="cat_lid_{nm}" transform="translate(0 -84)"><rect x="{ex - 40}" y="990" width="80" height="84" fill="{CAT}"/>'
                 + line([(ex - 36, 1070), (ex, 1076), (ex + 36, 1070)], 4.6, seed=sd) + "</g>")
        s.append(f'<g id="cat_lidlo_{nm}" transform="translate(0 48)"><rect x="{ex - 40}" y="1072" width="80" height="50" fill="{CAT}"/></g>')
        s.append(f'</g><path d="{ink_closed(ep, 4.4, seed=sd + 3)}" fill="{INK}"/></g>')
    # полоски на щеках — по две
    for sx in (-1, 1):
        for k, dy in enumerate((0, 14)):
            x0 = CX + sx * 76
            s.append(line([(x0, 1100 + dy), (x0 + sx * 30, 1094 + dy + k * 3)], 5.4, "#ee8a3c", seed=260 + k + sx, taper=.3, wmin=.5))
    # нос, рот, усы
    s.append(shape([(826, 1108), (846, 1108), (836, 1119)], "#c47a72", w=2.6, seed=262))
    s.append(line([(836, 1119), (836, 1124)], 2.4, seed=263))
    s.append(line([(822, 1124), (829, 1131), (836, 1124), (843, 1131), (850, 1124)], 3, seed=264))
    for sx in (-1, 1):
        for k, (dy, dl) in enumerate([(-4, -8), (4, 2), (12, 12)]):
            x0 = CX + sx * 62
            s.append(line([(x0, 1114 + dy), (x0 + sx * 50, 1110 + dy + dl * .4), (x0 + sx * 92, 1106 + dy + dl)], 1.8, "#cfc8dc",
                          seed=270 + k + sx, op=.7))
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
    for (cx, cy, rot, sc, sd) in [(372, 1708, -14, 1.0, 282), (548, 1770, 10, .96, 286)]:
        def P(pts, cx=cx, cy=cy, rot=rot, sc=sc):
            return T([(x * sc, y * sc * .62) + tuple(q[2:]) for q in pts for x, y in [q[:2]]], cx, cy, rot=rot)
        s.append(blob(P(ellipse_pts(4, 30, 96, 30, 12)), "#000", .4, blur(5)))
        sole = [(-84, 0), (-78, -26), (-44, -38), (30, -40), (74, -30), (94, -4), (90, 18), (68, 34), (20, 40), (-44, 38), (-76, 24)]
        s.append(shape(P(T(sole, 0, 10)), "#8f8676", w=4.2, seed=sd))
        s.append(shape(P(sole), "#d8cfbf", blob(P([(-84, 10), (94, 6), (68, 40), (-76, 40)]), "#b7ad9b", .8), w=4.4, seed=sd + 1))
        hole = [(-74, -6), (-62, -24), (-34, -28), (-18, -16), (-20, 10), (-36, 22), (-64, 18)]
        s.append(shape(P(hole), "#3a3236", blob(P([(-74, -6), (-62, -24), (-34, -28), (-40, -10), (-70, 6)]), "#241e22"), w=3.4, seed=sd + 2))
        up = [(-22, -36), (30, -46), (76, -34), (100, -6), (94, 22), (70, 40), (20, 46), (-22, 34), (-16, 18), (-12, 0), (-16, -18)]
        inner = blob(P([(-30, 10), (100, 6), (80, 50), (-30, 50)]), "#4c5878", .9)
        inner += blob(P([(-30, -46), (-4, -46), (-6, 46), (-30, 46)]), "#8e99b8", .9)
        inner += line(P([(20, -28), (50, -24), (76, -12)]), 2.2, "#9aa6c6", seed=sd + 3)
        s.append(shape(P(up), "#6b7899", inner, w=4.6, seed=sd + 4))
    # коробка из-под пиццы, крышка приоткрыта
    s.append(blob([(820, 1582), (1080, 1570), (1080, 1610), (830, 1616)], "#000", .35, blur(6)))
    box = [(828, 1546, 1), (1060, 1536, 1), (1072, 1580, 1), (836, 1594, 1)]
    s.append(shape(box, "#c9a77a", blob([(828, 1580), (1072, 1568), (1072, 1580), (836, 1594)], "#a8865c") +
                   line([(846, 1558), (1050, 1550)], 2, "#8a6a44", seed=291, op=.7), w=4.6, seed=292))
    lid = [(834, 1548, 1), (1056, 1538, 1), (1040, 1490, 1), (858, 1502, 1)]
    s.append(shape(lid, "#d9bb8e", blob(ellipse_pts(946, 1518, 34, 10, 10), "#b4413a", .55) +
                   blob([(834, 1548), (1056, 1538), (1052, 1528), (838, 1538)], "#b49468"), w=4.4, seed=293))
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
<linearGradient id="gNight" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a54a2"/><stop offset=".5" stop-color="#5660ae"/><stop offset="1" stop-color="#363e86"/></linearGradient>
<radialGradient id="gPhone" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(590 820) scale(460 420)"><stop offset="0" stop-color="#9cc6ff" stop-opacity=".6"/><stop offset=".25" stop-color="#6ea2f0" stop-opacity=".42"/><stop offset=".6" stop-color="#4a74c8" stop-opacity=".14"/><stop offset="1" stop-color="#4a74c8" stop-opacity="0"/></radialGradient>
<radialGradient id="gPhoneCore" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(596 812) scale(90 120)"><stop offset="0" stop-color="#d8eaff" stop-opacity=".45"/><stop offset="1" stop-color="#9cc6ff" stop-opacity="0"/></radialGradient>
<radialGradient id="gFlame" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(1000 1070) scale(300 280)"><stop offset="0" stop-color="#ffb05a" stop-opacity=".85"/><stop offset=".2" stop-color="#ff8a3a" stop-opacity=".45"/><stop offset=".55" stop-color="#d0602a" stop-opacity=".14"/><stop offset="1" stop-color="#d0602a" stop-opacity="0"/></radialGradient>
<radialGradient id="gClock" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(76 1146) scale(200 130)"><stop offset="0" stop-color="#ff5a3c" stop-opacity=".5"/><stop offset="1" stop-color="#ff5a3c" stop-opacity="0"/></radialGradient>
<radialGradient id="gMoon" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(770 200) scale(130 130)"><stop offset="0" stop-color="#fff6d8" stop-opacity=".7"/><stop offset=".4" stop-color="#c8d4ff" stop-opacity=".25"/><stop offset="1" stop-color="#c8d4ff" stop-opacity="0"/></radialGradient>
<radialGradient id="gVig" cx="540" cy="900" r="1250" gradientUnits="userSpaceOnUse"><stop offset=".4" stop-color="#fff"/><stop offset="1" stop-color="#1e1a34"/></radialGradient>
<filter id="fGrain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="4" result="n"/><feColorMatrix type="matrix" values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  .9 .9 .9 0 -1.1"/></filter>
<filter id="fSoft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>
""")


def lights():
    """Над ночью: свет осветлением (screen), рим-свет резкой формой по силуэту, светящееся поверх."""
    s = []
    # лунный свет из окна: пятна на стене и пледе
    # лунный свет из окна: проекция рамы на пол и коврик (4 стекла, тени импостов), мягко
    panes = []
    for (u0, u1) in [(0, .47), (.53, 1)]:
        for (v0, v1) in [(0, .3), (.34, 1)]:
            q = []
            for (u, v) in [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]:
                x = 600 + u * 420 - v * 150 - u * v * 40
                y = 1500 + v * 380 + u * 20
                q.append((x, y, 1))
            panes.append(blob(q, "#7d95d8"))
    s.append(f'<g style="mix-blend-mode:screen" opacity=".2" {blur(7)}>{"".join(panes)}</g>')
    s.append(f'<g style="mix-blend-mode:screen" opacity=".16" {blur(18)}>'
             + blob([(640, 960), (1080, 960), (1080, 1300), (600, 1300)], "#6f86c8") + "</g>")
    # экран телефона: большое пятно и ядро
    DEFS.append(f'<mask id="mPhone"><rect width="{W}" height="{H}" fill="#fff"/>'
                f'<path d="{fill_d(rect_pts(-46, -98, 46, 98, 18))}" transform="translate({PX} {PY}) rotate({PR})" fill="#000"/></mask>')
    s.append(f'<g style="mix-blend-mode:screen" mask="url(#mPhone)"><g id="phone_glow"><rect width="{W}" height="{H}" fill="url(#gPhone)"/>'
             f'<rect width="{W}" height="{H}" fill="url(#gPhoneCore)"/></g></g>')
    # огонёк кота
    s.append(f'<g id="flame_glow" style="mix-blend-mode:screen"><rect width="{W}" height="{H}" fill="url(#gFlame)"/></g>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#gClock)" style="mix-blend-mode:screen"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#gMoon)" style="mix-blend-mode:screen"/>')
    return "".join(s)


def rim_lights():
    """Рим-свет: полумесяц на стороне к источнику, ширина 12–24 px, яркость гаснет с расстоянием от источника
    (заливка — радиальный градиент источника), поэтому читается как свет, а не как обводка."""
    tf, hf = head_tf(), f"translate({PX} {PY}) rotate({PR})"
    DEFS.append('<radialGradient id="gRimP" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(600 820) scale(260 300)">'
                '<stop offset="0" stop-color="#b9d6ff"/><stop offset=".5" stop-color="#6f9ff0"/><stop offset="1" stop-color="#3a5cb0" stop-opacity="0"/></radialGradient>'
                '<radialGradient id="gRimF" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(996 1060) scale(150 170)">'
                '<stop offset="0" stop-color="#ffc070"/><stop offset=".45" stop-color="#ff8a3a"/><stop offset="1" stop-color="#c05020" stop-opacity="0"/></radialGradient>'
                '<radialGradient id="gRimW" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(700 1000) scale(200 300)">'
                '<stop offset="0" stop-color="#7d98e0"/><stop offset="1" stop-color="#7d98e0" stop-opacity="0"/></radialGradient>')
    # градиенты в глобальных координатах, а рим головы рисуется в локальных — поэтому голова получает свой градиент
    DEFS.append(f'<radialGradient id="gRimPH" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" '
                f'gradientTransform="rotate({-HR}) translate({600 - HX} {820 - HY}) scale(260 300)">'
                '<stop offset="0" stop-color="#b9d6ff"/><stop offset=".5" stop-color="#6f9ff0"/><stop offset="1" stop-color="#3a5cb0" stop-opacity="0"/></radialGradient>')
    DEFS.append(f'<radialGradient id="gFaceL" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" '
                f'gradientTransform="translate(150 -10) scale(230 210)">'
                '<stop offset="0" stop-color="#7fa8f0" stop-opacity=".75"/><stop offset=".55" stop-color="#5a80d0" stop-opacity=".35"/>'
                '<stop offset="1" stop-color="#3a5cb0" stop-opacity="0"/></radialGradient>')
    s = ['<g id="rim_phone" style="mix-blend-mode:screen">']
    # лицо: мягкий заливающий свет экрана по маске лица (как в образце — лицо целиком светлее), плюс узкий блик по скуле
    fc = clip_of(FACE)
    hair = REG["dima_hair"]
    s.append(f'<g transform="{tf}"><g clip-path="url(#{fc})"><rect x="-140" y="-140" width="280" height="280" fill="url(#gFaceL)"/>'
             f'<path d="{fill_d(hair)}" fill="#000"/></g></g>')
    s.append(rim(REG["dima_hair"], "gRimPH", -6, 5, .45, tf))
    s.append(f'<g transform="{hf}">')
    s.append(f'<g id="thumb_rim">{rim(REG["dima_thumb_shape"], "#a9ccff", 8, 2, .6)}</g>')
    s.append("</g>")
    nc = clip_of(REG["dima_neck"])
    s.append(f'<g clip-path="url(#{nc})"><rect x="400" y="940" width="100" height="120" fill="url(#gRimP)" opacity=".35"/></g>')
    s.append("</g>")
    s.append('<g id="rim_flame" style="mix-blend-mode:screen">')
    s.append(rim(REG["cat_head"], "gRimF", -8, 5, .8))
    s.append(rim(REG["cat_ear_R"], "gRimF", -6, 4, .8))
    s.append(f'<g id="tail_rim">{rim(REG["cat_tail_shape"], "gRimF", -2, 6, .65)}</g>')
    s.append("</g>")
    return "".join(s)


def glowing():
    s = []
    # луна с кратерами и звёзды — поверх ночи (окно)
    s.append(shape(ellipse_pts(770, 200, 34, 34, 14), "#fbf3d6", blob(ellipse_pts(780, 210, 30, 30, 12), "#e4d9b0", .9) +
                   blob(ellipse_pts(758, 190, 7, 6, 8), "#d8cba0") + blob(ellipse_pts(782, 218, 5, 4, 8), "#d8cba0") +
                   blob(ellipse_pts(774, 184, 3.5, 3, 8), "#d8cba0"), w=3, seed=310, ink_color="#3a3d66"))
    rs = np.random.RandomState(11)
    for _ in range(26):
        x, y = rs.uniform(708, 982), rs.uniform(130, 380)
        if 726 < x < 816 and 154 < y < 246 or 822 < x < 850 or 296 < y < 322:
            continue
        r = rs.uniform(1, 2.6)
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#eef0ff" opacity="{rs.uniform(.5, 1):.2f}"/>')
    s.append(f'<path d="M960 170 l3 9 l9 3 l-9 3 l-3 9 l-3 -9 l-9 -3 l9 -3z" fill="#fffbe6"/>')
    # светящиеся окна дома напротив (часть тёмные), тёплые, с силуэтами штор
    lit = [(740, 462), (786, 578), (878, 462), (924, 578), (740, 636), (924, 462), (878, 636)]
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
    s.append(f'<g {blur(5)} opacity=".9" style="mix-blend-mode:screen">{clock_digits(True, "clock_digits_glow")}</g>')
    # кромка экрана телефона
    s.append(f'<g transform="translate({PX} {PY}) rotate({PR})" id="screen_edge">'
             + line([(-59, -82), (-61, 0), (-60, 84)], 4.6, "#d7ebff", taper=.3, wmin=.4, seed=320)
             + f'<path d="M-62 -84 L-64 86" stroke="#bfe0ff" stroke-width="12" opacity=".55" {blur(6)}/></g>')
    # глаза кота отсвечивают
    s.append('<g id="cat_eye_glow">')
    for ex in (CX - 44, CX + 44):
        s.append(f'<ellipse cx="{ex}" cy="1072" rx="30" ry="34" fill="#c6f05a" opacity=".22" {blur(8)} style="mix-blend-mode:screen"/>')
    s.append("</g>")
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
