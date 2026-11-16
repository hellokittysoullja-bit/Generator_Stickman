"""Призыв «подпишись на мой Телеграм-канал» для рилсов-историй формата 4 (вид "cta": "tg", владелец 16.11), v2.

Рисованная обстановка (тёплая стена, стол с тетрадкой и кружкой), крупная карточка канала в тёмной теме Телеграма
(как профиль владельца, assets/story_cta/tg_channel_ref.jpg): круглая аватарка с кольцом, «СДВГ | Напарник» с лапками
(кодом), ссылка t.me/ru_adhd, значок Телеграма с бумажным самолётиком (кодом), синяя кнопка «ПОДПИСАТЬСЯ» (#2AABEE)
со свечением. Кот рилсов (common/cat.py) сидит на столе с кадра 0, смотрит на влетевшую карточку, короткой лапой жмёт
кнопку → кнопка проседает и отпружинивает, рябь, плавно темнеет в «ВЫ ПОДПИСАНЫ», галочка рисуется штрихом, по дугам
улетают сердечки и самолётик. Числа подписчиков нет намеренно (владелец 16.11: не показываем и не выдумываем).

v2 (владелец 16.11: «моушн красивый, плавный, и стиль красивый»): влёт пружиной с перелётом и наклоном, парение,
каскад элементов (аватар → имя → ссылка → кнопка), дыхание кнопки, плавная смена цвета, мягкий наезд и отъезд камеры.

Всё время — параметрами: t0 (карточка начинает влетать) и press (лапа нажимает кнопку, ≥ t0 + 1.0) — на слова рилса.

В сцене рилса (common уже в sys.path, как у scene_*.py / s78*.py):
    sys.path.insert(0, "<repo>/scripts"); import story_cta_tg as tg
    def frame(sid, t): return tg.frame(t, t0=W["подпишись"], press=W["Телеграм"])        # готовый SVG 1080×1920
  или слоем: tg.prepare() до lib.static_done(); body, (cx, cy, s, rot) = tg.layer(t, t0, press)
Демо: python3 scripts/story_cta_tg.py [out.mp4] [--sheet sheet.jpg] [--common videos/NN/story/common]
"""
import base64
import io
import math
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_COMMON = os.path.join(REPO, "videos", "78_lenta_slabak", "story", "common")
AVATAR = os.path.join(REPO, "assets", "story_cta", "tg_avatar.png")

TG_BLUE, TG_BLUE_SH, TG_BLUE_HI = "#2AABEE", "#1d8fcc", "#7fd0f7"
DONE, DONE_SH = "#2c2c30", "#1f1f22"
GREY = "#8e8e93"
NAME = "СДВГ | Напарник"
LINK = "t.me/ru_adhd"

# раскладка (мир = экран при камере 1.0): всё главное выше 1300 px — ниже субтитры
CX0, CX1, CY0, CY1 = 90, 990, 44, 812          # карточка: 83 % ширины, над котом
CARD_C = ((CX0 + CX1) / 2, (CY0 + CY1) / 2)
AV = (540, 184, 124)                            # аватарка: центр, радиус
NAME_Y, LINK_Y, SUB_Y, DESC_Y = 404, 508, 562, 612
DESC = "истории про Диму и кота каждый вечер"
BX0, BX1, BY0, BY1 = 190, 890, 650, 770         # кнопка по центру карточки, целиком видна
BTX = 540                                       # центр надписи кнопки
BADGE = (134, 92, 58)                           # значок Телеграма на углу карточки
TABLE = 1272
CAT_X, CAT_Y, CAT_K = 420, 1288, 1.2            # кот сидит на столе под карточкой, крупно
RISE = 0.5                                      # на нажатие привстаёт: задние лапы вытягиваются (cat.py legs)
PAW_DX, PAW_PW = 29.4, 2.66                     # лапа cat.py тянется вверх к нижнему краю кнопки (≈ x 600)

_ST = {}


def _mods(common=None):
    """lib, cat из common рилса (если сцена уже положила свой common в sys.path — берётся он)."""
    try:
        import cat  # noqa: F401
        import lib  # noqa: F401
    except ImportError:
        sys.path.insert(0, common or DEFAULT_COMMON)
    import cat
    import lib
    return lib, cat


def _avatar_uri():
    if "av" not in _ST:
        from PIL import Image
        im = Image.open(AVATAR).convert("RGBA")
        bg = Image.new("RGBA", im.size, (246, 243, 234, 255))
        bg.alpha_composite(im)
        bg = bg.convert("RGB").resize((440, 440), Image.LANCZOS)
        b = io.BytesIO()
        bg.save(b, "JPEG", quality=90)
        _ST["av"] = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
    return _ST["av"]


# ───────────────────────── кривые
def _cl(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def _back(u, s=1.6):
    u = _cl(u) - 1
    return 1 + (s + 1) * u ** 3 + s * u ** 2


def _expo(u):
    u = _cl(u)
    return 1.0 if u >= 1 else 1 - 2 ** (-10 * u)


def _eio(u):
    u = _cl(u)
    return u * u * u * (u * (6 * u - 15) + 10)          # smootherstep: без скачка скорости на концах


def _spring(e, freq=1.25, damp=6.5):
    """0 → 1 с одним мягким перелётом (≈8 %) и затуханием; e — секунды."""
    if e <= 0:
        return 0.0
    return 1 - math.exp(-damp * e) * math.cos(2 * math.pi * freq * e)


def _mixc(a, b, u):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * _cl(u)) for x, y in zip(a, b))


def _sc(g, x, y, s, rot=0.0, op=1.0):
    o = f' opacity="{op:.3f}"' if op < 0.999 else ""
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.3f}) scale({s:.4f}) translate({-x:.2f} {-y:.2f})"{o}>{g}</g>'


def _text(x, y, s, size, fill, anchor="middle", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="IDB" font-weight="900" font-size="{size}" '
            f'fill="{fill}" {extra}>{s}</text>')


# ───────────────────────── рисунки
def plane_pts(cx, cy, r, rot=0.0):
    """Бумажный самолётик Телеграма (корпус, сгиб, хвостик) в круге радиуса r."""
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def P(q):
        x, y = q[0] * r, q[1] * r
        return (cx + x * c - y * s, cy + x * s + y * c) + ((1,) if len(q) > 2 else ())
    body = [P(q) for q in [(-0.56, -0.02, 1), (0.50, -0.44, 1), (0.33, 0.46, 1), (0.06, 0.26, 1), (-0.12, 0.10, 1)]]
    fold = [P(q) for q in [(0.50, -0.44, 1), (-0.12, 0.10, 1), (0.06, 0.26, 1)]]
    tail = [P(q) for q in [(-0.12, 0.10, 1), (-0.06, 0.42, 1), (0.06, 0.26, 1)]]
    return body, fold, tail


def tg_badge(lib, cx, cy, r, sd=700):
    """Значок Телеграма: синий круг с бликом, белый самолётик — рисованный."""
    from ink import ellipse_pts
    g = lib.rad_grad([(0, "#5cc6f5", 1), (1, "#1b93d3", 1)], cx - r * .3, cy - r * .4, r * 1.6)
    hi = lib.blob(ellipse_pts(cx - r * .3, cy - r * .42, r * .46, r * .26, 12, rot=-25), "#ffffff", .3)
    o = lib.blob(ellipse_pts(cx + 4, cy + 10, r, r, 18), "#0b3550", .35, lib.blur(8))
    o += lib.shape(ellipse_pts(cx, cy, r, r, 18), f"url(#{g})", hi, w=4.4, seed=sd)
    body, fold, tail = plane_pts(cx - r * .04, cy + r * .02, r)
    o += lib.blob(tail, "#b9d6ea")
    o += lib.shape(body, "#ffffff", lib.blob(fold, "#d6e8f4"), w=2.4, seed=sd + 1)
    return o


def paw_print(lib, cx, cy, s, rot, col=GREY):
    """Отпечаток лапки (вместо эмодзи 🐾 — шрифта с ним нет)."""
    from ink import ellipse_pts
    o = lib.blob(lib.T(ellipse_pts(0, 6, 15, 12.5, 14), cx, cy, s, rot), col)
    for dx, dy, rx in [(-15, -12, 6), (-5, -20, 6.4), (6, -20, 6.4), (16, -12, 6)]:
        o += lib.blob(lib.T(ellipse_pts(dx, dy, rx, rx * 1.25, 10, rot=dx * 1.4), cx, cy, s, rot), col)
    return o


def heart(lib, cx, cy, sc, rot, sd, col="#ff5a6e", sh="#d63a52"):
    pts = []
    for k in range(20):
        a = 2 * math.pi * k / 20
        hx = 16 * math.sin(a) ** 3
        hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((hx, hy) + ((1,) if k in (0, 10) else ()))
    P = lambda q: lib.T(q, cx, cy, sc, rot)  # noqa: E731
    hl = lib.blob(P([(-11, -8), (-6, -12), (-3, -8), (-8, -3)]), "#ffd0d6")
    return lib.shape(P(pts), col, lib.blob(P([(2, -6), (16, -6), (16, 16), (0, 16)]), sh) + hl, w=3.2, seed=sd)


# ───────────────────────── статика
def background(lib):
    """Стена с обоями, стол на всю нижнюю половину: доски, тетрадка с карандашом, кружка; пол внизу."""
    from ink import ellipse_pts
    s = []
    g = lib.lin_grad([(0, "#f3c98a", 1), (1, "#e6a862", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-600" y="-600" width="2300" height="{TABLE + 600}" fill="url(#{g})"/>')
    for x in range(-560, 1700, 120):
        s.append(f'<rect x="{x}" y="-600" width="44" height="{TABLE + 600}" fill="#ecb878"/>')
    # столешница (вид сверху-спереди), край стола, пол
    FRONT = 1700
    s.append(lib.line([(-600, TABLE), (1700, TABLE)], 4.4, lib.INK, taper=.05, wmin=.9, seed=601))
    tg = lib.lin_grad([(0, "#cf955f", 1), (1, "#b97e4a", 1)], 0, 0, 0, 1)
    tp = [(-600, TABLE, 1), (1700, TABLE, 1), (1700, FRONT, 1), (-600, FRONT, 1)]
    inner = "".join(lib.line([(-600, TABLE + 70 + k * 92 + k * k * 6), (1700, TABLE + 74 + k * 92 + k * k * 6)], 2.4, "#a8703e",
                             taper=.1, wmin=.7, seed=610 + k, op=.7) for k in range(5))
    for k, (x, y) in enumerate([(160, 1330), (520, 1400), (860, 1520), (300, 1600), (700, 1640)]):
        inner += lib.line([(x, y), (x + 120, y + 4), (x + 220, y + 1)], 2.0, "#b07745", taper=.6, seed=640 + k, op=.6)
    inner += lib.blob(lib.rect_pts(-600, TABLE, 1700, TABLE + 18), "#a8723f", .55)
    s.append(lib.shape(tp, f"url(#{tg})", inner, w=4.4, seed=602))
    s.append(lib.shape([(-600, FRONT, 1), (1700, FRONT, 1), (1700, FRONT + 70, 1), (-600, FRONT + 70, 1)], "#9a6234",
                       lib.blob(lib.rect_pts(-600, FRONT + 46, 1700, FRONT + 72), "#7d4c26", .9), w=4.6, seed=603))
    s.append(lib.shape([(-600, FRONT + 70, 1), (1700, FRONT + 70, 1), (1700, 2700, 1), (-600, 2700, 1)], "#6e4a32",
                       lib.blob(lib.rect_pts(-600, FRONT + 70, 1700, FRONT + 110), "#3e2718", .55), w=4.4, seed=604))
    # тетрадка с карандашом (слева) и кружка (справа) — на столе, ниже главного
    nb = lib.T([(-130, -70, 1), (130, -82, 1), (138, 70, 1), (-124, 82, 1)], 210, 1440, 1, -6)
    ni = "".join(lib.line(lib.T([(-100, y), (110, y - 3)], 210, 1440, 1, -6), 2, "#9ab8d8", seed=650 + i, op=.8)
                 for i, y in enumerate(range(-40, 70, 26)))
    ni += lib.line(lib.T([(-88, -70), (-84, 80)], 210, 1440, 1, -6), 2.2, "#e07a7a", seed=657, op=.8)
    s.append(lib.blob(lib.T(lib.rect_pts(-120, -60, 150, 96, 10), 216, 1452, 1, -6), "#5a3418", .28, lib.blur(10)))
    s.append(lib.shape(nb, "#fbf6ea", ni, w=4.2, seed=658))
    pc = lib.T([(-150, -9, 1), (110, -9, 1), (150, 0, 1), (110, 9, 1), (-150, 9, 1)], 260, 1540, 1, -14)
    s.append(lib.shape(pc, "#f2c23a", lib.blob(lib.T([(-150, 0), (110, 0), (110, 9), (-150, 9)], 260, 1540, 1, -14), "#d79e1d"), w=3.4, seed=659))
    s.append(lib.blob(ellipse_pts(970, 1480, 90, 22, 16), "#5a3418", .3, lib.blur(8)))
    mug = [(900, 1350, 1), (1040, 1350, 1), (1032, 1470), (1010, 1484), (930, 1484), (908, 1470)]
    s.append(lib.line([(1036, 1378), (1084, 1386), (1088, 1428), (1034, 1444)], 10, "#c64e43", taper=.1, wmin=.8, seed=661))
    s.append(lib.shape(mug, "#e9685a", lib.blob([(990, 1350), (1040, 1350), (1032, 1470), (1000, 1484)], "#c64e43", .9) +
                       lib.line([(920, 1380), (924, 1450)], 6, "#ff9d8f", seed=662, op=.8), w=4.6, seed=663))
    s.append(lib.shape(ellipse_pts(970, 1352, 70, 14, 16), "#5b3420", "", w=3.4, seed=664))
    lg = lib.rad_grad([(0, "#fff0c8", .5), (.6, "#ffd890", .14), (1, "#ffd890", 0)], 300, 300, 1300, 1300)
    s.append(f'<rect x="-600" y="-600" width="2300" height="3400" fill="url(#{lg})" style="mix-blend-mode:screen"/>')
    return "".join(s)


def card_static(lib):
    """Карточка: мягкий градиент, большие скругления, тонкий светлый кант и блик; без содержимого."""
    s = []
    pts = lib.rect_pts(CX0, CY0, CX1, CY1, 84)
    g = lib.lin_grad([(0, "#2b2b31", 1), (.55, "#1d1d21", 1), (1, "#141417", 1)], 0, 0, .25, 1)
    inner = lib.blob(lib.rect_pts(CX0 + 8, CY0 + 8, CX1 - 8, CY1 - 8, 78), "none",
                     extra='stroke="#ffffff" stroke-opacity=".10" stroke-width="3"')
    inner += lib.line([(CX0 + 110, CY0 + 22), (CX1 - 220, CY0 + 18)], 6, "#ffffff", seed=620, op=.16)
    inner += lib.line([(CX0 + 22, CY0 + 120), (CX0 + 18, CY0 + 380)], 5, "#ffffff", seed=623, op=.10)
    s.append(lib.shape(pts, f"url(#{g})", inner, w=5, seed=621))
    _ST["card_shadow"] = lib.blob(lib.rect_pts(CX0 + 18, CY0 + 40, CX1 + 26, CY1 + 46, 90), "#5a3110", .38, lib.blur(26))
    return "".join(s)


def avatar_static(lib):
    from ink import ellipse_pts
    ax, ay, ar = AV
    s = [lib.blob(ellipse_pts(ax, ay + 10, ar + 18, ar + 18, 28), "#000000", .35, lib.blur(12))]
    s.append(f'<circle cx="{ax}" cy="{ay}" r="{ar + 13}" fill="none" stroke="{TG_BLUE}" stroke-width="5" stroke-opacity=".9"/>')
    cid = lib.clip_of(ellipse_pts(ax, ay, ar, ar, 28))
    s.append(f'<g clip-path="url(#{cid})"><image href="{_avatar_uri()}" x="{ax - ar}" y="{ay - ar}" width="{2 * ar}" height="{2 * ar}"/></g>')
    s.append(f'<path d="{lib.ink_closed(ellipse_pts(ax, ay, ar, ar, 28), 4.4, seed=622)}" fill="{lib.INK}"/>')
    return "".join(s)


# ───────────────────────── динамика карточки
def _rise(t, a, d=0.42, dy=34):
    """Каскадное проявление: (opacity, сдвиг вниз, масштаб) с expo-out."""
    u = _expo((t - a) / d)
    return u, dy * (1 - u), 0.92 + 0.08 * u


def content(lib, t, t0):
    o = []
    s = 0.82 + 0.18 * _back((t - t0) / 0.5, 2.0)          # аватар — вместе с карточкой, с лёгким pop
    o.append(_sc(_ST["avatar"], AV[0], AV[1], s, 5 * (1 - _cl(s))))
    for k, (a, y) in enumerate(((0.30, NAME_Y), (0.40, LINK_Y), (0.50, SUB_Y))):
        op, dy, sc = _rise(t, t0 + a)
        if op <= 0.002:
            continue
        if k == 0:
            g = _text(505, y, NAME, 86, "#ffffff") + paw_print(lib, 912, y - 50, 1.05, 28) + paw_print(lib, 944, y - 12, .86, 28)
        elif k == 1:
            g = _text(540, y, LINK, 98, TG_BLUE)
        else:
            g = _text(540, y, "телеграм-канал", 40, GREY)       # без числа подписчиков
            g += _text(540, DESC_Y, DESC, 36, "#b4b4ba")
        o.append(_sc(g, 540, y + dy - 20, sc, 0, op))
    bs = _back((t - t0 - 0.86) / 0.5, 1.4) if t > t0 + 0.86 else 0.0
    if bs > 0:
        wob = 4 * math.sin(t * 2.2)
        o.append(_sc(tg_badge(lib, *BADGE), BADGE[0], BADGE[1], bs, -12 + wob))
    return "".join(o)


def button(lib, t, t0, press, touch):
    """Кнопка: появляется expo, дышит свечением; нажатие — проседает за 2 кадра и отпружинивает, рябь от точки
    касания, цвет плавно в тёмный, надписи меняются крест-накрест, галочка рисуется штрихом."""
    a = t0 + 0.60
    op, _, _ = _rise(t, a, 0.45)
    if op <= 0.002:
        return ""
    sc_in = 0.86 + 0.14 * _back((t - a) / 0.5, 1.5)
    e = t - press
    # проседание: 0 → 12 px за 2 кадра, затем пружина обратно с перелётом вверх
    if e < 0:
        dn = 0.0
    elif e < 2 / 30:
        dn = 12 * e / (2 / 30)
    else:
        ee = e - 2 / 30
        dn = 12 * math.exp(-ee * 9) * math.cos(2 * math.pi * 2.2 * ee)
    cu = _eio((e - 0.03) / 0.28)               # смена цвета
    col = _mixc(TG_BLUE, DONE, cu)
    sh = _mixc(TG_BLUE_SH, DONE_SH, cu)
    lip = _mixc("#14628d", "#0d0d0f", cu)
    breath = 0.5 + 0.5 * math.sin(2 * math.pi * (t - a) / 1.3)
    pre = 1 - cu
    cx, cy = (BX0 + BX1) / 2, (BY0 + BY1) / 2
    s = []
    # синее свечение (дышит до нажатия, гаснет после)
    gl = lib.rad_grad([(0, TG_BLUE, .55), (1, TG_BLUE, 0)], cx, cy + 10, 420, 120)
    s.append(f'<ellipse cx="{cx:.1f}" cy="{cy + 12:.1f}" rx="{430 + 30 * breath:.1f}" ry="{130 + 16 * breath:.1f}" fill="url(#{gl})" '
             f'opacity="{(.45 + .4 * breath) * pre * op:.3f}"/>')
    s.append(lib.shape(lib.rect_pts(BX0, BY0 + 14, BX1, BY1 + 12, 62), lip, "", w=4.6, seed=650))
    pts = lib.rect_pts(BX0, BY0 + dn, BX1, BY1 + dn, 62)
    inner = lib.blob(lib.rect_pts(BX0, BY1 + dn - 28, BX1 + 4, BY1 + dn + 4), sh, 1)
    inner += lib.line([(BX0 + 70, BY0 + dn + 18), (BX1 - 230, BY0 + dn + 16)], 7, "#ffffff", seed=651, op=.45 * pre + .08)
    if 0 <= e < 0.7:
        from ink import ellipse_pts
        r = 30 + 760 * _expo(e / 0.7)
        inner += lib.blob(ellipse_pts(touch[0], touch[1] + dn, r, r, 28), "#ffffff", .30 * (1 - _eio(e / 0.7)))
    s.append(lib.shape(pts, col, inner, w=5.2, seed=652))
    ty = cy + dn + 25
    o1 = 1 - _eio((e - 0.02) / 0.16)
    if o1 > 0.002:
        s.append(f'<g opacity="{o1:.3f}">' + _text(BTX, ty + 1, "ПОДПИСАТЬСЯ", 66, sh) + _text(BTX, ty - 2, "ПОДПИСАТЬСЯ", 66, "#ffffff") + "</g>")
    o2 = _eio((e - 0.12) / 0.2)
    if o2 > 0.002:
        tx = BTX + 34
        s.append(_sc(_text(tx, ty - 2, "ВЫ ПОДПИСАНЫ", 58, "#ffffff"), tx, ty - 20, 0.9 + 0.1 * o2, 0, o2))
        k = _eio((e - 0.16) / 0.3)
        if k > 0:
            x0 = tx - 288
            d = f"M{x0 - 26:.1f} {cy + dn:.1f} L{x0 - 4:.1f} {cy + dn + 22:.1f} L{x0 + 34:.1f} {cy + dn - 26:.1f}"
            L = 31 + 62
            s.append(f'<path d="{d}" fill="none" stroke="{TG_BLUE}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round" '
                     f'stroke-dasharray="{L}" stroke-dashoffset="{L * (1 - k):.2f}"/>')
    return _sc("".join(s), cx, cy, sc_in, 0, op)


# (сдвиг вправо, подъём) в конце дуги: от точки нажатия вправо-вверх, мимо надписей
HEARTS = [(470, 300, -18, 1.1), (540, 420, 10, 1.0), (430, 520, -6, 1.05), (560, 260, 16, 0.95), (500, 600, -20, 0.85),
          (450, 360, 18, 0.9), (520, 480, 4, 0.8)]


def burst(lib, t, press, touch):
    """Сердечки по дугам с замедлением и затуханием; самолётик улетает дугой вправо-вверх с пунктиром следа."""
    e = t - press - 0.06
    if e < 0:
        return ""
    s = []
    ox, oy = touch
    for k, (dx_, dy_, rot, sz) in enumerate(HEARTS):
        ee = e - k * 0.045
        if ee <= 0:
            continue
        u = 1 - math.exp(-2.4 * ee)              # дуга с замедлением: сначала вправо вдоль низа кнопки, потом вверх мимо текста
        x = ox + dx_ * u
        y = oy + 60 * u * (1 - u) - dy_ * u ** 4
        a = _back(ee / 0.28, 2.2) * (1 - _eio((ee - 0.55) / 0.45))
        if a < 0.02:
            continue
        s.append(heart(lib, x, y, sz * 2.4 * a, rot + 18 * math.sin(ee * 4 + k), 660 + k))
    # самолётик по кубической дуге
    u = _cl(e / 1.15)
    if u < 1:
        P = [(BX1 - 40, BY0 + 20), (1160, BY0 - 60), (900, 300), (1200, 60)]

        def bez(v):
            m = 1 - v
            return (m ** 3 * P[0][0] + 3 * m * m * v * P[1][0] + 3 * m * v * v * P[2][0] + v ** 3 * P[3][0],
                    m ** 3 * P[0][1] + 3 * m * m * v * P[1][1] + 3 * m * v * v * P[2][1] + v ** 3 * P[3][1])
        ue = 1 - (1 - u) ** 2.2
        n = 30
        for k in range(0, n, 2):
            v0, v1 = ue * k / n, ue * (k + 1) / n
            fade = _cl(1 - (ue - v0) / 0.45) * (1 - _eio((u - .7) / .3))
            if fade > 0.03:
                s.append(lib.line([bez(v0), bez(v1)], 5, "#ffffff", taper=.3, wmin=.5, seed=680 + k, op=.85 * fade))
        x, y = bez(ue)
        x2, y2 = bez(min(1.0, ue + 0.01))
        ang = math.degrees(math.atan2(y2 - y, x2 - x)) + 24
        r = 74 * _back(e / 0.25, 1.8)
        body, fold, tail = plane_pts(x, y, r, ang)
        g = lib.blob(tail, "#b9d6ea") + lib.shape(body, "#ffffff", lib.blob(fold, "#cfe3f1"), w=3.6, seed=690)
        s.append(f'<g opacity="{1 - _eio((u - .75) / .25):.3f}">{g}</g>')
    return "".join(s)


def steam(lib, t):
    """Пар над кружкой — движение с кадра 0."""
    o = []
    for k in range(3):
        ph = (t * 0.55 + k / 3) % 1.0
        x0 = 940 + k * 28
        pts = [(x0 + 12 * math.sin(ph * 6 + k + j * 1.3), 1330 - j * 40 - ph * 70) for j in range(4)]
        a = math.sin(math.pi * ph)
        o.append(lib.line(pts, 6, "#ffffff", taper=.8, wmin=.2, seed=730 + k, op=.55 * a))
    return "".join(o)


# ───────────────────────── кот
def cat_state(lib, cat, t, t0, press):
    """Кот сидит на столе под карточкой с кадра 0; смотрит на влетающую карточку, на нажатие привстаёт и тянет лапу вверх, жмёт
    короткой лапой (лапа cat.py, не вытянутая палка), после — в камеру, улыбка, огонёк вспыхивает."""
    X = CAT_X
    land = _eio((t - t0 - 0.15) / 0.35)
    perk = math.exp(-max(0.0, t - t0 - 0.45) * 2.5) * land
    a = press - 0.45
    rise = _eio((t - a + 0.1) / 0.35)            # привстаёт чуть раньше, чем тянет лапу
    pw = PAW_PW * _eio((t - a) / 0.45)
    e = t - press
    if e >= 0:
        pw += 0.05 * math.exp(-e * 9) * math.sin(min(e * 16, math.pi))
        back = _eio((e - 0.35) / 0.45)
        pw *= 1 - back
        rise *= 1 - back
    legs = RISE * rise
    Y = CAT_Y - 64 * legs * CAT_K                  # лапы стоят на столе, тело поднимается
    kb = _eio((t - press + 0.75) / 0.35)         # взгляд на кнопку
    kc = _eio((t - press - 0.3) / 0.3)           # в камеру
    look0 = (0.15, 0.1)
    look1 = (0.25, -0.95)
    look2 = (0.6, -0.9)
    lk = [look0[i] + (look1[i] - look0[i]) * land for i in (0, 1)]
    lk = [lk[i] + (look2[i] - lk[i]) * kb for i in (0, 1)]
    lk = [lk[i] * (1 - kc) for i in (0, 1)]
    blink = 0.0
    for c, half in ((0.08 if t0 > 0.3 else t0 + 1.0, 0.07), (press + 0.95, 0.08)):
        if c - half <= t <= c + half:
            blink = 1 - abs(t - c) / half
    tilt = 4 * land * (1 - kb) + 5 * kc * math.sin(max(0.0, t - press) * 2.6)
    tail = 6 * math.sin(t * 1.9) + 3 * math.sin(t * 3.3 + 1)
    st = dict(look=tuple(lk), blink=blink, tilt=tilt, tail=tail, paw=pw, paw_dx=PAW_DX, legs=legs, perk=max(perk, kc),
              smile=1.0 if kc > .5 else 0.0, flame_e=1.0 + 1.0 * math.exp(-max(0.0, e) * 2) * (e > 0))
    fx = cat.CX + 25
    tip = (fx + PAW_DX * PAW_PW * 1.6, 1306 - 150 * PAW_PW)
    Yr = CAT_Y - 64 * RISE * CAT_K
    touch = (X + (tip[0] - cat.CX) * CAT_K, Yr + (tip[1] - cat.CBOT) * CAT_K)
    return X, Y, st, touch


# ───────────────────────── слой и кадр
def prepare(common=None):
    """Статика карточки (её defs) — вызвать в своей сцене ДО lib.static_done(), иначе dyn_begin() сотрёт её defs."""
    lib, _ = _mods(common)
    if "card" not in _ST:
        _ST["card"] = card_static(lib)
        _ST["avatar"] = avatar_static(lib)


def layer(t, t0=0.1, press=1.7, common=None):
    """SVG-группа (мир 1080×1920): карточка, кот, всплеск, пар; и камера (cx, cy, s, rot)."""
    lib, cat = _mods(common)
    prepare(common)
    X, Y, st, touch = cat_state(lib, cat, t, t0, press)
    e = t - t0
    out = []
    # свет огонька кота на стене
    fx, fy = X + (cat.FLAME_BASE[0] - cat.CX) * CAT_K, Y + (cat.FLAME_BASE[1] - cat.CBOT) * CAT_K
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    gr = lib.rad_grad([(0, "#ffb050", .34 * fl), (1, "#ffb050", 0)], fx, fy, 260, 260)
    out.append(f'<rect x="{fx - 280:.1f}" y="{fy - 280:.1f}" width="560" height="560" fill="url(#{gr})" style="mix-blend-mode:screen"/>')
    out.append(steam(lib, t))
    if e > 0:
        # влёт пружиной: масштаб, подъём и наклон — у каждого своя частота, чтобы карточка «приземлялась», а не падала
        k_s = _spring(e, 1.15, 6.0)
        k_y = _spring(e, 1.0, 5.5)
        k_r = _spring(e, 0.9, 4.8)
        sc = 0.32 + 0.68 * k_s
        dy = 620 * (1 - k_y)
        rot = -11 * (1 - k_r)
        # парение после приземления
        hv = _eio((e - 0.6) / 0.6)
        dy += hv * 5 * math.sin(2 * math.pi * (t - t0) / 2.6)
        rot += hv * 0.35 * math.sin(2 * math.pi * (t - t0) / 3.4 + 1)
        op = _cl(e / 0.12)
        px, py = CARD_C[0], CY1
        sh = _ST["card_shadow"]
        card = _ST["card"] + content(lib, t, t0) + button(lib, t, t0, press, touch)
        out.append(f'<g opacity="{op:.3f}" transform="translate({px:.1f} {py + dy:.2f}) rotate({rot:.3f}) scale({sc:.4f}) '
                   f'translate({-px:.1f} {-py:.1f})">{sh}{card}</g>')
    out.append(cat.draw(X, Y, CAT_K, st, t))
    out.append(burst(lib, t, press, touch))
    # камера: мягкий наезд к карточке, лёгкий толчок на нажатии, отъезд после
    pin = _eio((t - t0 - 0.1) / 1.0)
    pout = _eio((t - press - 0.35) / 1.2)
    s = 1.0 + 0.022 * pin - 0.02 * pout           # мягкий наезд и отъезд; всё в кадре с запасом
    ccx = 540 + 4 * math.sin(t * 0.7)
    ccy = 960 - 12 * pin + 10 * pout + 4 * math.sin(t * 0.9)
    s *= 1 + 0.022 * math.exp(-((t - press - 0.08) / 0.13) ** 2)
    return "".join(out), (ccx, ccy, s, 0.35 * math.sin(t * 0.8))


def frame(t, t0=0.1, press=1.7, common=None):
    """Готовый кадр SVG 1080×1920 (фон + карточка + кот)."""
    lib, cat = _mods(common)
    if "bg" not in _ST:
        _ST["bg"] = background(lib)
        prepare(common)
        lib.static_done()
    lib.dyn_begin()
    body, (ccx, ccy, s, rot) = layer(t, t0, press, common)
    return lib.svg(f'<rect width="{lib.W}" height="{lib.H}" fill="#6e4a32"/><g transform="{lib.cam(ccx, ccy, s, rot)}">{_ST["bg"]}{body}</g>')


# ───────────────────────── демо
def _job(a):
    t, path, t0, press, common = a
    _mods(common)
    open(path, "w").write(frame(t, t0, press, common))
    return path


def render(out=None, dur=3.2, t0=0.1, press=1.75, common=None, sheet=None, nproc=2):
    from multiprocessing import Pool
    common = common or DEFAULT_COMMON
    rjs = os.path.join(common, "render.js")
    tmp = tempfile.mkdtemp(prefix="tgcta_")
    try:
        n = int(round(dur * 30))
        jobs = [(k / 30, os.path.join(tmp, f"f{k:04d}.svg"), t0, press, common) for k in range(n)]
        with Pool(nproc) as p:
            svgs = p.map(_job, jobs, chunksize=4)
        open(os.path.join(tmp, "list.txt"), "w").write("\n".join(svgs))
        subprocess.check_call(["node", rjs, os.path.join(tmp, "list.txt"), "mp4", str(nproc), os.path.join(tmp, "seg")])
        segs = sorted(x for x in os.listdir(tmp) if x.startswith("seg_") and x.endswith(".mp4"))
        open(os.path.join(tmp, "concat.txt"), "w").write("".join(f"file '{os.path.join(tmp, s)}'\n" for s in segs))
        out = out or os.path.join(REPO, "assets", "story_cta", "demo_tg.mp4")
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "concat.txt"),
                               "-c", "copy", "-movflags", "+faststart", out])
        if sheet:
            subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-vf", "fps=6,scale=216:-1,tile=10x2", "-frames:v", "1", sheet])
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    sheet = args[args.index("--sheet") + 1] if "--sheet" in args else None
    common = args[args.index("--common") + 1] if "--common" in args else None
    pos = [a for a in args if a.endswith(".mp4")]
    print(render(pos[0] if pos else None, common=common, sheet=sheet))
