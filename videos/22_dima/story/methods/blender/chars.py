"""2D-рисунок героев в пикселях кадра 1080×1920 (без bpy): Дима, телефон, плед, кот, тапки.

draw(t) -> список элементов {'layer', 'kind': 'fill'|'line', 'pts', 'rgba', 'w', 'press'}.
Формы — контуры SVG-путей; тени и блики — геометрией shapely (форма минус сдвинутая форма = полумесяц
тени), свет экрана и огонька — стопкой колец с малой прозрачностью в слое сложения.
t — время в секундах (0..3): моргания, большой палец, мигание экрана, огонёк.
"""
import math
import re

from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Point, Polygon
from shapely.ops import unary_union

SCREEN_PX = (594, 862)   # где светит экран (лицевая сторона телефона, к Диме)
CAT_DX = 18
FLAME_BASE = (984, 1004)
FLAME_PX = (FLAME_BASE[0] + CAT_DX, FLAME_BASE[1])  # огонёк кота

# слои снизу вверх; ADD — слой сложения света
LAYERS = ['shadow', 'slippers', 'dima', 'dima_eyes', 'dima_top', 'plaid', 'arm', 'thumb', 'phone', 'hand',
          'light', 'cat', 'cat_eyes', 'flame', 'glow']
ADD_LAYERS = {'light', 'glow'}
MUL_LAYERS = {'shadow'}
ANIM_LAYERS = {'dima_eyes', 'thumb', 'hand', 'light', 'cat_eyes', 'flame', 'glow'}

INK = '#120f1a'


def rgb(h, a=1.0):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


# ---------------------------------------------------------------- пути

def _cubic(p0, p1, p2, p3, n):
    out = []
    for i in range(1, n + 1):
        t = i / n
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        c = 3 * (1 - t) * t * t
        d = t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def path(d, step=5.0):
    """Абсолютный SVG-путь (M L C Q S Z) -> список точек; несколько M -> берётся первый контур."""
    toks = re.findall(r'[MLCQSZ]|-?\d+(?:\.\d+)?', d)
    pts = []
    cur = (0.0, 0.0)
    last_c = None
    i = 0
    cmd = None
    while i < len(toks):
        if toks[i] in 'MLCQSZ':
            cmd = toks[i]
            i += 1
            if cmd == 'Z':
                continue
        nums = []

        def take(k):
            nonlocal i
            v = [float(x) for x in toks[i:i + k]]
            i += k
            return v
        if cmd == 'M':
            x, y = take(2)
            cur = (x, y)
            pts.append(cur)
            cmd = 'L'
            last_c = None
        elif cmd == 'L':
            x, y = take(2)
            n = max(1, int(math.dist(cur, (x, y)) / step))
            pts += [(cur[0] + (x - cur[0]) * k / n, cur[1] + (y - cur[1]) * k / n) for k in range(1, n + 1)]
            cur = (x, y)
            last_c = None
        elif cmd == 'C':
            a = take(6)
            p1, p2, p3 = (a[0], a[1]), (a[2], a[3]), (a[4], a[5])
            n = max(2, int((math.dist(cur, p1) + math.dist(p1, p2) + math.dist(p2, p3)) / step))
            pts += _cubic(cur, p1, p2, p3, n)
            last_c = p2
            cur = p3
        elif cmd == 'S':
            a = take(4)
            p1 = (2 * cur[0] - last_c[0], 2 * cur[1] - last_c[1]) if last_c else cur
            p2, p3 = (a[0], a[1]), (a[2], a[3])
            n = max(2, int((math.dist(cur, p1) + math.dist(p1, p2) + math.dist(p2, p3)) / step))
            pts += _cubic(cur, p1, p2, p3, n)
            last_c = p2
            cur = p3
        elif cmd == 'Q':
            a = take(4)
            q, p3 = (a[0], a[1]), (a[2], a[3])
            p1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
            p2 = (p3[0] + 2 / 3 * (q[0] - p3[0]), p3[1] + 2 / 3 * (q[1] - p3[1]))
            n = max(2, int((math.dist(cur, q) + math.dist(q, p3)) / step))
            pts += _cubic(cur, p1, p2, p3, n)
            cur = p3
            last_c = None
        del nums
    # убрать повторы
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) > 0.5:
            out.append(p)
    return out


def poly(d):
    return Polygon(path(d)).buffer(0)


def ellipse(cx, cy, rx, ry, rot=0.0, n=72):
    p = Polygon([(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)])
    return affinity.rotate(p, rot, origin=(cx, cy)) if rot else p


def chaikin(pts, it=2):
    for _ in range(it):
        out = []
        n = len(pts)
        for k in range(n):
            a, b = pts[k], pts[(k + 1) % n]
            out.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            out.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        pts = out
    return pts


def tufty(p, every=22, amp=9, seed=0):
    """Пушистый край: клочки шерсти наружу по контуру (кот), углы скруглены сглаживанием Чайкина."""
    ring = p.exterior
    L = ring.length
    n = max(8, int(L / every))
    c = p.centroid
    out = []
    for k in range(n):
        for f, a_ in ((0.0, -0.1), (0.45, 0.55), (0.62, 1.0), (0.8, 0.35)):
            s0 = L * (k + f) / n
            q = ring.interpolate(s0)
            q2 = ring.interpolate(s0 + 1.0)
            tx, ty = q2.x - q.x, q2.y - q.y
            ln = math.hypot(tx, ty) or 1
            nx_, ny_ = ty / ln, -tx / ln
            if (q.x - c.x) * nx_ + (q.y - c.y) * ny_ < 0:
                nx_, ny_ = -nx_, -ny_
            a = amp * a_ * (0.65 + 0.35 * math.sin(k * 2.3 + seed))
            out.append((q.x + nx_ * a, q.y + ny_ * a))
    return Polygon(chaikin(out, 2)).buffer(0)


# ---------------------------------------------------------------- элементы

class Canvas:
    def __init__(self):
        self.items = []
        self.dx = 0.0
        self.dy = 0.0

    def _off(self, pts):
        if not (self.dx or self.dy):
            return pts
        return [(x + self.dx, y + self.dy) for x, y in pts]

    def fill(self, layer, geom, color, alpha=1.0):
        rgba = rgb(color, alpha) if isinstance(color, str) else color
        for g in _polys(geom):
            pts = list(g.exterior.coords)[:-1]
            if len(pts) >= 3:
                self.items.append({'layer': layer, 'kind': 'fill', 'pts': self._off(pts), 'rgba': rgba})

    def line(self, layer, pts, w=4.5, color=INK, taper=True, closed=False, alpha=1.0, wobble=0.18, seed=0):
        if isinstance(pts, (Polygon, MultiPolygon)):
            for g in _polys(pts):
                self.line(layer, list(g.exterior.coords)[:-1], w, color, taper=False, closed=True, alpha=alpha,
                          wobble=wobble, seed=seed)
            return
        if isinstance(pts, str):
            pts = path(pts)
        n = len(pts)
        if n < 2:
            return
        press = []
        for k in range(n):
            u = k / (n - 1)
            p = 1.0 + wobble * math.sin(u * 9.0 + seed * 1.7) * math.sin(u * 3.1 + seed)
            if taper and not closed:
                p *= min(1.0, 0.25 + 1.6 * min(u, 1 - u) * 2.2)
            press.append(max(0.15, p))
        rgba = rgb(color, alpha) if isinstance(color, str) else color
        self.items.append({'layer': layer, 'kind': 'line', 'pts': self._off(pts), 'rgba': rgba, 'w': w, 'press': press,
                           'closed': closed})

    def shape(self, layer, geom, color, w=4.5, line=INK, seed=0):
        self.fill(layer, geom, color)
        if w:
            self.line(layer, geom, w, line, seed=seed)

    def glow(self, layer, cx, cy, r, color, alpha=0.08, rings=14, clip=None, squash=1.0):
        """Мягкий свет: кольца от большого к малому, каждое добавляет немного (слой сложения)."""
        c = rgb(color)
        for k in range(rings):
            rr = r * (1 - k / rings)
            e = ellipse(cx, cy, rr, rr * squash, n=48)
            if clip is not None:
                e = e.intersection(clip)
            if e.is_empty:
                continue
            self.fill(layer, e, (c[0] * alpha, c[1] * alpha, c[2] * alpha, 1.0))


def soft_shadow(c, layer, geom, spread=40, rings=12, k=0.93, tint=(0.80, 0.82, 1.0)):
    """Мягкая тень слоем умножения: форма, раздутая на spread и сужающаяся кольцами."""
    for i in range(rings):
        g = geom.buffer(spread * (1 - 2 * i / rings))
        if g.is_empty:
            break
        f = (1 - (1 - k) * tint[0], 1 - (1 - k) * tint[1], 1 - (1 - k) * tint[2], 1.0)
        c.fill(layer, g.simplify(1.0), f)


def _polys(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if hasattr(g, 'geoms'):
        out = []
        for x in g.geoms:
            out += _polys(x)
        return out
    return []


def shade(p, dx, dy):
    """Полумесяц тени: форма минус она же, сдвинутая к свету."""
    return p.difference(affinity.translate(p, dx, dy))


def smooth(t0, t1, t):
    x = min(1.0, max(0.0, (t - t0) / (t1 - t0)))
    return x * x * (3 - 2 * x)


def blink(t, at, dur=0.22):
    """0 — открыт, 1 — закрыт: быстро вниз, чуть медленнее вверх."""
    if t < at or t > at + dur:
        return 0.0
    u = (t - at) / dur
    return smooth(0, 0.35, u) if u < 0.35 else 1 - smooth(0.45, 1.0, u)


# ---------------------------------------------------------------- палитра (уже в ночном свете)

SKIN = '#8f8fc4'        # лицо в холодном свете экрана
SKIN_LIT = '#b9c4ef'
SKIN_SH = '#5f5a8e'
BAGS = '#6a5d92'
HAIR = '#3a2a32'
HAIR_SH = '#251a22'
HAIR_HI = '#5a4652'
HOOD = '#8a7a3c'        # горчичное худи ночью
HOOD_SH = '#5e5430'
HOOD_LIT = '#a9a066'
PLAID = '#3f6656'
PLAID_D = '#2a4a3f'
PLAID_L = '#6f9a7e'
PLAID_SH = '#22382f'
FUR = '#1d1b29'
FUR_HI = '#3d3f63'
FUR_WARM = '#6b3a2a'
EYE_G = '#a8d94a'
STRIPE = '#f08a3a'


# ---------------------------------------------------------------- Дима

HEAD = ('M 270 822 C 268 742 326 692 396 692 C 456 692 490 742 490 800 C 490 826 494 842 500 856 '
        'C 504 868 498 876 490 880 C 492 932 476 980 438 1002 C 408 1018 368 1018 342 1004 '
        'C 304 986 280 952 274 914 C 270 884 270 852 270 822 Z')

# линия роста волос: зубцы чёлки падают на лоб
HAIRLINE = [(240, 980), (284, 936), (296, 880), (306, 840), (332, 806), (360, 798), (384, 826), (398, 800),
            (424, 794), (444, 818), (456, 794), (480, 788), (500, 772), (520, 600), (200, 600), (200, 980)]
TUFTS = [  # пряди, торчащие сзади и на макушке
    'M 276 870 C 246 862 222 868 204 884 C 214 858 236 840 270 834 Z',
    'M 270 812 C 238 800 214 776 204 748 C 230 764 254 772 278 772 Z',
    'M 284 752 C 262 724 256 696 264 664 C 278 694 296 710 318 716 Z',
    'M 330 708 C 330 680 346 654 370 640 C 364 664 370 684 386 696 Z',
    'M 402 696 C 420 672 448 662 474 664 C 456 676 448 690 448 706 Z',
    'M 456 716 C 478 712 496 716 510 730 C 494 730 484 736 480 746 Z',
]

EAR = 'M 304 860 C 284 842 260 848 260 876 C 260 904 278 920 300 918 C 308 904 310 878 304 860 Z'

NECK = 'M 338 990 C 340 1016 338 1040 330 1062 L 414 1066 C 408 1042 406 1020 414 998 Z'

TORSO = ('M 150 1190 C 150 1140 176 1092 226 1070 C 260 1056 300 1052 336 1058 C 372 1062 410 1062 446 1060 '
         'C 492 1060 528 1084 548 1120 C 560 1144 566 1166 568 1190 Z')

HOOD_SHAPE = ('M 236 1074 C 230 1034 256 1000 300 992 C 316 990 326 998 334 1012 C 344 1034 370 1046 400 1040 '
              'C 418 1020 432 1004 452 1004 C 476 1010 486 1036 480 1060 C 456 1078 412 1084 370 1082 '
              'C 312 1080 268 1082 236 1074 Z')

PLAID_SHAPE = ('M 120 1196 C 160 1150 230 1136 300 1140 C 380 1146 460 1160 540 1178 C 600 1190 650 1200 700 1204 '
               'C 760 1206 820 1214 880 1212 C 930 1210 960 1176 990 1168 C 1020 1162 1044 1180 1060 1196 '
               'C 1074 1210 1086 1214 1096 1216 L 1096 1452 '
               'C 1046 1462 1000 1440 950 1452 C 900 1468 846 1446 794 1460 C 736 1476 690 1452 630 1466 '
               'C 566 1480 510 1456 450 1470 C 388 1484 330 1462 272 1474 C 226 1484 176 1470 136 1476 '
               'C 120 1420 116 1300 120 1196 Z')

SLEEVE = ('M 452 1066 C 500 1074 534 1100 552 1136 C 566 1162 576 1176 590 1174 C 598 1150 600 1090 604 1012 '
          'L 660 1006 C 662 1080 660 1160 640 1198 C 618 1232 566 1234 534 1210 C 500 1184 482 1142 450 1112 Z')

CUFF = 'M 600 1000 C 616 992 642 992 658 1000 L 656 1030 C 640 1022 618 1022 602 1030 Z'
FIST = ('M 602 1010 C 592 990 594 960 606 944 C 620 928 650 924 676 930 C 700 936 710 956 708 984 '
        'C 706 1010 690 1030 664 1034 C 636 1038 612 1030 602 1010 Z')


def hair_geom():
    head = poly(HEAD)
    region = Polygon(HAIRLINE).buffer(0)
    hair = head.buffer(12).intersection(region)
    for d in TUFTS:
        hair = hair.union(poly(d))
    return hair.buffer(4).buffer(-4)


def phone_geom():
    """iPhone 14 Pro спиной к зрителю, повёрнут на 3/4: спинка с блоком из трёх камер, левый торец к Диме."""
    cx, cy, ang = 650, 872, 7.0
    w, h, r = 106, 214, 22
    rect = Polygon([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)])
    body = rect.buffer(-r).buffer(r, quad_segs=12)
    side = affinity.translate(body, -12, 3).difference(body)
    cam = Polygon([(-w / 2 + 9, -h / 2 + 9), (-w / 2 + 58, -h / 2 + 9), (-w / 2 + 58, -h / 2 + 60),
                   (-w / 2 + 9, -h / 2 + 60)]).buffer(-10).buffer(10, quad_segs=8)
    lens = [Point(-w / 2 + 23, -h / 2 + 23).buffer(10.5), Point(-w / 2 + 23, -h / 2 + 47).buffer(10.5),
            Point(-w / 2 + 45, -h / 2 + 35).buffer(10.5)]
    flash = Point(-w / 2 + 46, -h / 2 + 19).buffer(3.4)
    lidar = Point(-w / 2 + 46, -h / 2 + 51).buffer(3.0)
    logo = Point(2, -8).buffer(10)

    def place(g):
        g = affinity.rotate(g, ang, origin=(0, 0))
        return affinity.translate(g, cx, cy)
    return {'body': place(body), 'side': place(side), 'cam': place(cam), 'lens': [place(x) for x in lens],
            'flash': place(flash), 'lidar': place(lidar), 'logo': place(logo), 'center': (cx, cy), 'ang': ang}


def draw_dima(c, t):
    head = poly(HEAD)
    hair = hair_geom()
    # --- худи: туловище, капюшон за шеей, шнурки
    torso = poly(TORSO)
    c.shape('dima', torso, HOOD, 4.5)
    c.fill('dima', shade(torso, 34, 0).intersection(torso), HOOD_SH)
    c.fill('dima', torso.intersection(Point(500, 1120).buffer(80)).difference(shade(torso, 34, 0)), HOOD_LIT)
    hood = poly(HOOD_SHAPE)
    c.shape('dima', hood, HOOD, 4.2)
    c.fill('dima', shade(hood, 0, -14).intersection(hood), HOOD_SH)
    c.line('dima', 'M 262 1070 C 300 1060 340 1062 372 1078', 2.4)
    neck = poly(NECK)
    c.shape('dima', neck, SKIN_SH, 4)
    c.line('dima', 'M 344 1040 C 360 1050 386 1052 410 1046', 2.2, '#3f3a5e')
    for x0 in (372, 404):
        c.line('dima', 'M %d 1080 C %d 1100 %d 1120 %d 1140' % (x0, x0 - 4, x0 + 3, x0 - 2), 3.0, '#d8cfa0')
        c.fill('dima', Point(x0 - 2, 1142).buffer(5), '#cfc59a')
    c.line('dima', 'M 196 1140 C 226 1124 258 1124 286 1136', 2.4)
    c.line('dima', 'M 470 1100 C 496 1120 516 1150 524 1180', 2.4)
    # --- голова
    c.shape('dima', head, SKIN, 4.5)
    c.fill('dima', shade(head, 46, 4).intersection(head), SKIN_SH)
    c.fill('dima', head.intersection(ellipse(470, 900, 46, 90)).difference(shade(head, 46, 4)), SKIN_LIT, 0.8)
    # щетина: голубоватая дымка по челюсти + штрихи
    jaw = head.intersection(poly('M 296 930 C 340 962 404 968 476 938 L 500 1040 L 296 1040 Z'))
    c.fill('dima', jaw, '#6d6ea2', 0.6)
    import random
    rnd = random.Random(4)
    for _ in range(80):
        x = rnd.uniform(320, 480)
        y = rnd.uniform(944, 1006)
        if head.buffer(-8).contains(Point(x, y)) and not Point(x, y).within(Point(448, 958).buffer(13)):
            c.line('dima', [(x, y), (x + rnd.uniform(-1.5, 1.5), y + 2.6)], 1.7, '#3d3860', taper=False, wobble=0)
    # нос: выступает за щёку (3/4 вправо)
    c.fill('dima', poly('M 476 862 C 492 876 508 894 504 906 C 498 914 486 914 476 908 Z'), SKIN_LIT)
    c.line('dima', 'M 478 858 C 494 876 510 894 504 906 C 498 914 484 914 474 906', 3.8)
    # рот: короткая усталая линия, чуть вниз
    c.line('dima', 'M 432 960 C 444 955 456 956 466 962', 3.4)
    c.line('dima', 'M 344 1002 C 368 1014 396 1014 418 1006', 2.2, '#3f3a5e')
    # --- волосы
    c.shape('dima', hair, HAIR, 4.5)
    c.fill('dima', shade(hair, -14, 4).intersection(hair), HAIR_HI, 0.9)
    c.fill('dima', shade(hair, 16, -6).intersection(hair), HAIR_SH)
    for d in ('M 300 760 C 330 730 370 716 410 718', 'M 284 820 C 296 790 318 768 344 758',
              'M 420 740 C 444 744 464 756 476 772', 'M 250 862 C 262 848 276 842 290 840'):
        c.line('dima', d, 2.2, '#140c12')
    # ухо поверх волос
    ear = poly(EAR)
    c.shape('dima', ear, SKIN, 4.2)
    c.fill('dima', shade(ear, 8, 0).intersection(ear), SKIN_SH)
    c.line('dima', 'M 294 872 C 280 866 272 878 278 894 C 284 900 290 900 292 892', 2.4)


def draw_brows(c, t):
    c.line('dima_top', 'M 372 812 C 388 804 406 802 424 808', 4.4)
    c.line('dima_top', 'M 456 810 C 466 806 478 808 488 814', 4.0)


def draw_dima_eyes(c, t):
    """Глаза: белки касаются, веки устало опущены, мешки; зрачки — в телефон."""
    k = blink(t, 1.15)
    eyes = [(414, 860, 34, 37), (474, 858, 26, 34)]
    look = (9, 9)
    head = poly(HEAD)
    for i, (ex, ey, rx, ry) in enumerate(eyes):
        e = ellipse(ex, ey, rx, ry)
        bag = ellipse(ex - 2, ey + ry * 0.55, rx * 1.08, ry * 0.72).difference(e)
        c.fill('dima_eyes', bag.intersection(head.buffer(6)), BAGS, 0.95)
        c.line('dima_eyes', 'M %f %f C %f %f %f %f %f %f' % (ex - rx * 0.9, ey + ry * 0.75, ex - rx * 0.4, ey + ry * 1.35,
                                                          ex + rx * 0.5, ey + ry * 1.35, ex + rx * 0.9, ey + ry * 0.8), 2.8)
        c.line('dima_eyes', 'M %f %f C %f %f %f %f %f %f' % (ex - rx * 0.6, ey + ry * 1.25, ex - rx * 0.2, ey + ry * 1.55,
                                                          ex + rx * 0.4, ey + ry * 1.55, ex + rx * 0.7, ey + ry * 1.3), 1.8,
               '#3f3a5e')
        c.fill('dima_eyes', e, '#e6eaff')
        c.fill('dima_eyes', shade(e, -6, -6).intersection(e), '#c4c8ee')
        px, py = ex + look[0] + rx * 0.25, ey + look[1]
        c.fill('dima_eyes', Point(px, py).buffer(6.5 if i == 0 else 5.5), INK)
        c.fill('dima_eyes', Point(px - 2, py - 2.5).buffer(1.6), '#e6eaff')
        lid_y = ey - ry + ry * 2 * (0.44 + 0.58 * k)
        tilt = -6 if i == 0 else -4
        cut = Polygon([(ex - rx - 5, ey - ry - 10), (ex + rx + 5, ey - ry - 10), (ex + rx + 5, lid_y + tilt),
                       (ex - rx - 5, lid_y - tilt)])
        lid = e.buffer(1.5).intersection(cut)
        c.fill('dima_eyes', lid, SKIN_LIT if i == 1 else SKIN)
        c.line('dima_eyes', [(ex - rx + 1, lid_y - tilt + 1), (ex + rx - 1, lid_y + tilt + 1)], 4.2, wobble=0.05)
        c.line('dima_eyes', e, 4.0, seed=i)


def thumb_flick(t):
    return smooth(0.35, 0.55, t) - smooth(0.55, 0.85, t) + smooth(1.75, 1.95, t) - smooth(1.95, 2.25, t)


def draw_phone_hand(c, t):
    ph = phone_geom()
    # большой палец на экране (за телефоном): кончик выглядывает из-за левого торца и листает
    f = thumb_flick(t)
    thumb = poly('M 614 960 C 596 934 586 904 592 880 C 598 866 614 864 620 878 C 626 904 634 934 638 958 Z')
    thumb = affinity.translate(affinity.rotate(thumb, -5 * f, origin=(624, 960)), 0, -22 * f)
    c.shape('thumb', thumb, SKIN_LIT, 4.0)
    c.line('thumb', [(596, 888 - 22 * f), (604, 884 - 22 * f)], 2.2)
    # телефон
    c.shape('phone', ph['side'], '#454a66', 3.6)
    c.shape('phone', ph['body'], '#191a23', 4.4)
    c.fill('phone', shade(ph['body'], -10, 10).intersection(ph['body']), '#2c2e3f')
    c.fill('phone', shade(ph['body'], 10, -10).intersection(ph['body']), '#0e0e15')
    c.shape('phone', ph['cam'], '#262837', 3)
    c.fill('phone', shade(ph['cam'], -4, 4).intersection(ph['cam']), '#363a50')
    for L in ph['lens']:
        c.shape('phone', L.buffer(2.5), '#30344a', 2.0)
        c.shape('phone', L, '#08080d', 2.2)
        c.fill('phone', affinity.scale(L, 0.45, 0.45), '#1c2340')
        b = L.centroid
        c.fill('phone', Point(b.x - 3, b.y - 3).buffer(2.0), '#8a96c4')
    c.fill('phone', ph['flash'], '#c8c2a0')
    c.fill('phone', ph['lidar'], '#05050a')
    c.line('phone', ph['logo'], 1.6, '#30334a')
    # свет экрана, просочившийся по левому торцу
    edge = ph['side'].buffer(-1.5)
    c.fill('phone', edge, '#9fd2ff', 0.8)
    # кулак: держит низ телефона, кончики пальцев на правом торце
    fist = poly(FIST)
    c.shape('hand', fist, SKIN, 4.4)
    c.fill('hand', shade(fist, -14, -6).intersection(fist), SKIN_SH)
    for k, y0 in enumerate((940, 962, 984, 1006)):
        tip = ellipse(708, y0, 13, 11.5)
        c.shape('hand', tip, SKIN if k else SKIN_LIT, 3.4)
        c.fill('hand', shade(tip, -4, -3).intersection(tip), SKIN_SH)
    for d in ('M 624 952 C 646 948 670 948 690 954', 'M 622 976 C 646 972 672 972 692 978',
              'M 626 1000 C 648 998 672 998 690 1002'):
        c.line('hand', d, 2.2, '#2a2540')


def draw_plaid(c, t):
    pl = poly(PLAID_SHAPE)
    c.fill('plaid', pl, PLAID)

    def warp(x, y):
        return (x + 10 * math.sin(y / 37.0) + 6 * math.sin(x / 90.0), y + 12 * math.sin(x / 61.0) + 0.05 * (x - 500))
    for x0 in range(100, 1110, 96):
        a = [warp(x0, y) for y in range(1100, 1520, 20)]
        b = [warp(x0 + 36, y) for y in range(1520, 1100, -20)]
        c.fill('plaid', Polygon(a + b).buffer(0).intersection(pl), PLAID_D, 0.7)
    for y0 in range(1104, 1500, 96):
        a = [warp(x, y0) for x in range(90, 1120, 20)]
        b = [warp(x, y0 + 36) for x in range(1120, 90, -20)]
        c.fill('plaid', Polygon(a + b).buffer(0).intersection(pl), PLAID_D, 0.7)
    for x0, y0 in ((154, 1158), (172, 1176)):
        pass
    for x0 in range(150, 1110, 96):
        ls = LineString([warp(x0, y) for y in range(1100, 1520, 20)]).intersection(pl)
        for g in getattr(ls, 'geoms', [ls]):
            if not g.is_empty and g.length > 10:
                c.line('plaid', list(g.coords), 2.0, PLAID_L, taper=False, wobble=0, alpha=0.8)
    for y0 in range(1154, 1500, 96):
        ls = LineString([warp(x, y0) for x in range(90, 1120, 20)]).intersection(pl)
        for g in getattr(ls, 'geoms', [ls]):
            if not g.is_empty and g.length > 10:
                c.line('plaid', list(g.coords), 2.0, PLAID_L, taper=False, wobble=0, alpha=0.8)
    # объём: тень по низу (перегиб через край сиденья), тень от руки, ног и кота
    c.fill('plaid', pl.intersection(poly('M 100 1338 C 400 1352 700 1352 1100 1342 L 1100 1500 L 100 1500 Z')),
           PLAID_SH, 0.55)
    c.fill('plaid', shade(pl, 0, -30).intersection(pl), PLAID_SH, 0.7)
    c.fill('plaid', ellipse(838, 1236, 124, 22).intersection(pl), '#0f1a15', 0.8)
    c.fill('plaid', ellipse(600, 1214, 80, 26).intersection(pl), '#0f1a15', 0.55)
    # свет экрана на верхней кромке
    c.fill('plaid', pl.intersection(ellipse(560, 1176, 170, 40)), '#7fb0a0', 0.25)
    for d in ('M 580 1260 C 610 1300 616 1360 606 1450', 'M 760 1266 C 790 1320 800 1390 790 1456',
              'M 340 1210 C 360 1270 360 1350 350 1462', 'M 940 1244 C 956 1300 964 1380 956 1446',
              'M 250 1180 C 300 1196 340 1220 360 1260', 'M 660 1206 C 700 1226 726 1246 742 1274',
              'M 960 1200 C 990 1210 1010 1226 1020 1250'):
        c.line('plaid', d, 2.8, '#14221c')
    c.line('plaid', 'M 140 1330 C 400 1342 700 1346 1090 1338', 2.4, '#14221c')
    c.line('plaid', pl, 4.6)
    # бахрома по нижнему краю
    ring = LineString(path('M 136 1476 C 176 1470 226 1484 272 1474 C 330 1462 388 1484 450 1470 '
                           'C 510 1456 566 1480 630 1466 C 690 1452 736 1476 794 1460 C 846 1446 900 1468 950 1452 '
                           'C 1000 1440 1046 1462 1096 1452'))
    n = int(ring.length / 14)
    for k in range(n):
        p = ring.interpolate(k * ring.length / n)
        c.line('plaid', [(p.x, p.y + 1), (p.x + 1.5 * math.sin(k), p.y + 15)], 3.0, '#355a4a', taper=False, wobble=0)


def draw_arm(c, t):
    sl = poly(SLEEVE)
    c.shape('arm', sl, HOOD, 4.6)
    c.fill('arm', shade(sl, 20, -6).intersection(sl), HOOD_SH)
    c.fill('arm', sl.intersection(Point(610, 1060).buffer(64)).difference(shade(sl, 20, -6)), HOOD_LIT)
    c.line('arm', 'M 540 1130 C 562 1160 584 1174 600 1176', 2.4)
    c.line('arm', 'M 510 1160 C 528 1182 544 1192 560 1198', 2.2)
    c.line('arm', 'M 626 1100 C 636 1120 640 1140 636 1160', 2.2)
    c.shape('arm', poly(CUFF), HOOD_SH, 3.8)


def screen_flicker(t):
    """Яркость экрана: дрожь подсветки и провал на смене ролика после каждого свайпа."""
    return 1.0 + 0.06 * math.sin(t * 23.0) * math.sin(t * 7.0) \
        - 0.3 * (smooth(0.55, 0.6, t) - smooth(0.6, 0.85, t)) \
        - 0.3 * (smooth(1.95, 2.0, t) - smooth(2.0, 2.25, t))


def flame_flicker(t):
    return 1 + 0.12 * math.sin(t * 13) + 0.06 * math.sin(t * 31)


def draw_light(c, t):
    """Свет экрана: на лице, руке, худи; мигает со сменой ролика."""
    flick = screen_flicker(t)
    sx, sy = SCREEN_PX
    face = poly(HEAD).union(poly(EAR)).union(hair_geom())
    c.glow('light', sx - 40, sy + 10, 250, '#9fd0ff', 0.026 * flick, 24, clip=face)
    c.glow('light', sx, sy + 160, 200, '#9fd0ff', 0.024 * flick, 20, clip=poly(SLEEVE).union(poly(TORSO)))
    c.glow('light', sx - 6, sy, 130, '#8fc8ff', 0.017 * flick, 20, squash=1.5)
    return flick


# ---------------------------------------------------------------- кот

CAT_BODY = ('M 742 1238 C 724 1200 722 1150 740 1108 C 760 1080 800 1070 830 1072 C 864 1074 900 1090 914 1122 '
            'C 930 1160 926 1206 908 1238 Z')
CAT_HEAD = ('M 716 1006 C 712 958 742 920 790 910 C 812 906 840 906 862 912 C 906 924 930 962 928 1006 '
            'C 926 1050 896 1084 854 1094 C 830 1100 806 1100 784 1094 C 744 1082 718 1050 716 1006 Z')
EAR_R = 'M 862 924 C 872 896 884 870 896 850 C 908 872 916 902 918 936 Z'           # правое: стоит
EAR_L = 'M 734 952 C 726 928 728 908 740 892 C 756 898 772 900 790 912 C 770 928 752 940 734 952 Z'  # левое: загнуто
TAIL_LINE = ('M 896 1214 C 960 1218 1008 1176 1010 1116 C 1012 1076 990 1050 966 1054 '
             'C 946 1058 940 1080 952 1092 C 962 1100 976 1096 980 1086')


def tail_geom():
    pts = path(TAIL_LINE, 3.0)
    n = len(pts)
    g = None
    for k, (x, y) in enumerate(pts):
        r = 21 - 9 * (k / (n - 1))
        d = Point(x, y).buffer(r, quad_segs=6)
        g = d if g is None else g.union(d)
    return g


def draw_cat(c, t):
    c.dx = CAT_DX
    tail = tufty(tail_geom().simplify(1.0), 16, 7, seed=3)
    c.shape('cat', tail, FUR, 4.5)
    c.fill('cat', shade(tail, 8, 0).intersection(tail), FUR_WARM, 0.85)
    body = tufty(poly(CAT_BODY), 20, 8, seed=1)
    c.shape('cat', body, FUR, 5)
    c.fill('cat', shade(body, 12, 0).intersection(body), FUR_HI, 0.9)
    c.fill('cat', shade(body, -10, 0).intersection(body), FUR_WARM, 0.7)
    # лапы с оранжевыми подушечками
    for x0 in (782, 858):
        paw = ellipse(x0, 1232, 26, 16)
        c.shape('cat', paw, FUR, 4)
        c.fill('cat', ellipse(x0, 1236, 10, 7), STRIPE)
        for dx in (-12, 0, 12):
            c.fill('cat', Point(x0 + dx, 1224).buffer(3.6), STRIPE)
    c.line('cat', 'M 820 1150 C 818 1180 818 1210 820 1236', 3.0)
    # уши
    er = poly(EAR_R)
    c.shape('cat', er, FUR, 4.5)
    c.fill('cat', poly('M 872 922 C 878 900 886 882 894 870 C 902 888 906 906 908 928 Z'), '#7a4a4a')
    el = poly('M 730 960 C 724 930 728 900 742 874 C 762 880 784 892 800 910 Z')
    c.shape('cat', el, FUR, 4.5)
    c.fill('cat', poly('M 742 940 C 740 920 744 900 750 888 C 764 894 776 902 786 912 Z'), '#7a4a4a')
    # голова
    head = tufty(poly(CAT_HEAD), 22, 9, seed=2)
    c.shape('cat', head, FUR, 5)
    c.fill('cat', shade(head, 14, 2).intersection(head), FUR_HI, 0.9)
    c.fill('cat', shade(head, -12, 2).intersection(head), FUR_WARM, 0.6)
    # левое ухо загнуто вниз: клапан поверх головы, сгиб — светлой линией
    flap = poly('M 738 878 C 752 868 778 872 796 888 C 800 904 792 918 776 926 C 762 922 748 914 738 900 '
                'C 734 892 734 884 738 878 Z')
    c.shape('cat', flap, FUR, 4.2)
    c.fill('cat', shade(flap, 6, 6).intersection(flap), FUR_HI, 0.9)
    c.line('cat', 'M 742 882 C 758 874 778 876 794 890', 2.4, '#565a86')
    # усы
    for dy, ang in ((-4, -6), (6, 2), (16, 10)):
        c.line('cat', [(742, 1040 + dy), (692, 1034 + dy + ang)], 1.6, '#b8b8d8', wobble=0.05)
        c.line('cat', [(902, 1040 + dy), (976, 1032 + dy + ang)], 1.6, '#b8b8d8', wobble=0.05)
    # полоски на щеках: по две с каждой стороны
    for y0 in (1032, 1046):
        c.line('cat', [(740, y0), (770, y0 + 3)], 5.0, STRIPE, wobble=0.1)
        c.line('cat', [(874, y0 + 3), (904, y0)], 5.0, STRIPE, wobble=0.1)
    # нос и рот
    c.fill('cat', poly('M 812 1042 L 832 1042 L 822 1054 Z').buffer(2), '#d78a8a')
    c.line('cat', 'M 822 1054 C 822 1062 814 1068 806 1064', 2.6, '#0a0a10')
    c.line('cat', 'M 822 1054 C 822 1062 830 1068 838 1064', 2.6, '#0a0a10')
    c.dx = 0


def draw_cat_eyes(c, t):
    c.dx = CAT_DX
    k = blink(t, 2.25, 0.36)  # кошачье медленное моргание
    for i, ex in enumerate((786, 858)):
        ey = 1004
        e = ellipse(ex, ey, 31, 35)
        c.fill('cat_eyes', e, EYE_G)
        c.fill('cat_eyes', e.difference(affinity.translate(e, 0, 10)), '#7aa83a')
        c.fill('cat_eyes', ellipse(ex + 1, ey + 1, 11, 25), '#06060a')
        c.fill('cat_eyes', Point(ex + 8, ey - 13).buffer(5.5), '#ffffff')
        c.fill('cat_eyes', Point(ex - 9, ey + 14).buffer(2.4), '#e8f6c0')
        if k > 0:
            lid_y = ey - 36 + 72 * k
            cut = Polygon([(ex - 40, ey - 45), (ex + 40, ey - 45), (ex + 40, lid_y), (ex - 40, lid_y)])
            c.fill('cat_eyes', e.buffer(2).intersection(cut), FUR)
            c.line('cat_eyes', [(ex - 30, lid_y), (ex + 30, lid_y)], 4.0)
        c.line('cat_eyes', e, 4.2, seed=i + 5)
    c.dx = 0


def flame_poly(t, scale=1.0):
    """Огонёк: капля с тремя языками, языки колышутся (волна бежит вверх, кончик ходит сильнее)."""
    fx, fy = FLAME_BASE
    base_y = fy + 30
    pts = []
    n = 90
    for k in range(n):
        a = 2 * math.pi * k / n          # 0 — верх
        up = math.cos(a)                 # 1 вверху, -1 внизу
        side = math.sin(a)
        h = 64 * scale if up > 0 else 22 * scale
        w = 20 * scale * (1 - 0.25 * up)
        tongues = 1 + 0.22 * max(0.0, up) * math.cos(3 * a + 0.6 * math.sin(t * 7))
        y = -up * h * tongues
        x = side * w * (0.75 + 0.25 * (1 - max(0.0, up)))
        hgt = max(0.0, -y / (64 * scale))
        sway = 6 * scale * math.sin(t * 8.5 - hgt * 3.0) * hgt ** 1.4
        lick = 2.5 * scale * math.sin(t * 15.0 + a * 4) * hgt
        pts.append((fx + x + sway + lick, base_y + y * 0.86))
    return Polygon(chaikin(pts, 1)).buffer(0)


def draw_flame(c, t):
    c.dx = CAT_DX
    f = flame_poly(t)
    c.shape('flame', f, '#ff8c24', 3.2, line='#4a1a06')
    mid = flame_poly(t * 1.07 + 0.3, 0.68)
    c.fill('flame', affinity.translate(mid, 0, 6), '#ffc04a')
    core = flame_poly(t * 1.13 + 0.7, 0.36)
    c.fill('flame', affinity.translate(core, 0, 12), '#fff2b0')
    fx, fy = FLAME_BASE
    k = flame_flicker(t)
    c.glow('glow', fx, fy + 10, 150 * k, '#ff7a22', 0.022, 24)
    c.glow('glow', fx, fy + 10, 60 * k, '#ffcf6a', 0.035, 14)
    c.dx = 0


# ---------------------------------------------------------------- тапки

def draw_slippers(c, t):
    for (x0, y0, ang) in ((300, 1760, -14), (450, 1790, 8)):
        s = affinity.rotate(ellipse(x0, y0, 92, 40), ang, origin=(x0, y0))
        c.shape('slippers', s, '#4a3f6a', 5)
        c.fill('slippers', shade(s, 0, -10).intersection(s), '#2c2546')
        top = affinity.rotate(ellipse(x0 + 34, y0 - 6, 52, 30), ang, origin=(x0, y0))
        c.shape('slippers', top.intersection(s.buffer(4)), '#6a5f94', 4)
        c.fill('slippers', affinity.rotate(ellipse(x0 + 34, y0 - 14, 30, 10), ang, origin=(x0, y0)), '#8a80b4', 0.7)


def draw_shadows(c, t):
    """Тени героев на спинке дивана и стене: свет экрана справа от лица — тень уходит влево."""
    head = affinity.translate(poly(HEAD).union(hair_geom()), -46, 26)
    body = affinity.translate(poly(TORSO), -30, 10)
    soft_shadow(c, 'shadow', head.union(body).buffer(-20), 34, 12, 0.94)
    c.dx = CAT_DX
    cat = affinity.translate(poly(CAT_HEAD).union(poly(CAT_BODY)), -54, 18)
    soft_shadow(c, 'shadow', cat.buffer(-16), 28, 10, 0.94, (0.85, 0.9, 1.0))
    c.dx = 0


def draw(t=0.0):
    c = Canvas()
    draw_shadows(c, t)
    draw_slippers(c, t)
    draw_dima(c, t)
    draw_dima_eyes(c, t)
    draw_brows(c, t)
    draw_plaid(c, t)
    draw_arm(c, t)
    draw_phone_hand(c, t)
    draw_light(c, t)
    draw_cat(c, t)
    draw_cat_eyes(c, t)
    draw_flame(c, t)
    return c.items


if __name__ == '__main__':
    it = draw(0.0)
    print(len(it), 'items', sum(len(i['pts']) for i in it), 'points')
