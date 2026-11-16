"""Призыв «подпишись на мой Телеграм-канал» для рилсов-историй формата 4 (вид "cta": "tg", владелец 16.11).

Рисованная обстановка (тёплая стена, стол), карточка канала в тёмной теме Телеграма (как профиль владельца,
assets/story_cta/tg_channel_ref.jpg): круглая аватарка, «СДВГ | Напарник» с лапками (нарисованы кодом), ссылка
t.me/ru_adhd, значок Телеграма с бумажным самолётиком (кодом), синяя кнопка «ПОДПИСАТЬСЯ» (#2AABEE). Кот рилсов
(common/cat.py) сидит справа, тянется лапой и нажимает кнопку → «ВЫ ПОДПИСАНЫ» с галочкой, вылетают самолётик и
сердечки. Числа подписчиков нет намеренно (владелец 16.11: не показываем и не выдумываем).

Всё время — параметрами: t0 (карточка начинает влетать) и press (лапа нажимает кнопку) — ставятся на слова рилса.

В сцене рилса (common уже в sys.path, как у scene_*.py / s78*.py):
    sys.path.insert(0, "<repo>/scripts"); import story_cta_tg as tg
    def frame(sid, t): return tg.frame(t, t0=W["подпишись"], press=W["канал"])        # готовый SVG 1080×1920
  или слоями поверх своей сцены: tg.layer(t, t0, press) -> (svg-группа карточки и кота, камера_dict).
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
CARD, CARD_SH, CARD_HI = "#1c1c1e", "#141416", "#2c2c2e"
GREY = "#8e8e93"
NAME = "СДВГ | Напарник"
LINK = "t.me/ru_adhd"

# раскладка (мир = экран при камере 1.0): всё главное выше 1300 px — ниже субтитры
CX0, CX1, CY0, CY1 = 64, 836, 150, 1200       # карточка
AV = (450, 380, 150)                           # аватарка: центр, радиус
NAME_Y, LINK_Y, SUB_Y = 646, 744, 806
BX0, BX1, BY0, BY1 = 112, 788, 950, 1096       # кнопка
BADGE = (98, 186, 66)                          # значок Телеграма на углу карточки
TABLE = 1262
CAT_X, CAT_Y, CAT_K = 846, 1272, 0.97
PAW_DX = 92.0                                  # лапа дотягивается до середины кнопки

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
        bg = bg.convert("RGB").resize((420, 420), Image.LANCZOS)
        b = io.BytesIO()
        bg.save(b, "JPEG", quality=90)
        _ST["av"] = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
    return _ST["av"]


# ───────────────────────── помощники
def _cl(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def _back(u, s=1.9):
    u = _cl(u) - 1
    return 1 + (s + 1) * u ** 3 + s * u ** 2


def _eo(u, p=3):
    return 1 - (1 - _cl(u)) ** p


def _eio(u):
    u = _cl(u)
    return u * u * (3 - 2 * u)


def _pop(t, a, d=0.28):
    """Масштаб «выскочить»: 0 → перелёт → 1."""
    return max(0.0, _back((t - a) / d)) if t > a else 0.0


def _sc(g, x, y, s, rot=0.0):
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({s:.4f}) translate({-x:.2f} {-y:.2f})">{g}</g>'


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
    """Значок Телеграма: синий круг, белый самолётик — рисованный (тушь как у всего кадра)."""
    from ink import ellipse_pts
    hi = lib.blob(ellipse_pts(cx - r * .28, cy - r * .34, r * .5, r * .32, 12, rot=-25), TG_BLUE_HI, .55)
    sh = lib.blob(ellipse_pts(cx + r * .2, cy + r * .55, r * .95, r * .45, 14), TG_BLUE_SH, .9)
    o = lib.shape(ellipse_pts(cx, cy, r, r, 18), TG_BLUE, sh + hi, w=5, seed=sd)
    body, fold, tail = plane_pts(cx - r * .04, cy + r * .02, r)
    o += lib.blob(tail, "#b9d6ea")
    o += lib.shape(body, "#ffffff", lib.blob(fold, "#d6e8f4"), w=2.6, seed=sd + 1)
    return o


def paw_print(lib, cx, cy, s, rot, col=GREY, sd=0):
    """Отпечаток лапки (вместо эмодзи 🐾, шрифта с ним нет)."""
    from ink import ellipse_pts
    o = lib.blob(lib.T(ellipse_pts(0, 6, 15, 12.5, 14), cx, cy, s, rot), col)
    for k, (dx, dy, rx) in enumerate([(-15, -12, 6), (-5, -20, 6.4), (6, -20, 6.4), (16, -12, 6)]):
        o += lib.blob(lib.T(ellipse_pts(dx, dy, rx, rx * 1.25, 10, rot=dx * 1.4), cx, cy, s, rot), col)
    return o


def heart(lib, cx, cy, sc, rot, sd, col="#e8413a", sh="#c22a26"):
    pts = []
    for k in range(20):
        a = 2 * math.pi * k / 20
        hx = 16 * math.sin(a) ** 3
        hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((hx, hy) + ((1,) if k in (0, 10) else ()))
    P = lambda q: lib.T(q, cx, cy, sc, rot)  # noqa: E731
    hl = lib.blob(P([(-11, -8), (-6, -12), (-3, -8), (-8, -3)]), "#ffb3a8")
    return lib.shape(P(pts), col, lib.blob(P([(2, -6), (16, -6), (16, 16), (0, 16)]), sh) + hl, w=3.4, seed=sd)


def _text(x, y, s, size, fill, anchor="middle", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="IDB" font-weight="900" font-size="{size}" '
            f'fill="{fill}" {extra}>{s}</text>')


# ───────────────────────── статика
def background(lib):
    s = []
    g = lib.lin_grad([(0, "#f3c98a", 1), (1, "#e6a862", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-600" y="-600" width="2300" height="{TABLE + 600}" fill="url(#{g})"/>')
    for x in range(-560, 1700, 120):
        s.append(f'<rect x="{x}" y="-600" width="44" height="{TABLE + 600}" fill="#ecb878"/>')
    s.append(lib.line([(-600, TABLE), (1700, TABLE)], 4.4, lib.INK, taper=.05, wmin=.9, seed=601))
    tp = [(-600, TABLE, 1), (1700, TABLE, 1), (1700, 2600, 1), (-600, 2600, 1)]
    inner = "".join(lib.line([(-600, TABLE + 46 + k * 58), (1700, TABLE + 50 + k * 58)], 2.4, "#b27a48", taper=.1, wmin=.7, seed=610 + k, op=.8)
                    for k in range(12))
    inner += lib.blob(lib.rect_pts(-600, TABLE, 1700, TABLE + 22), "#a8723f", .7)
    s.append(lib.shape(tp, "#c98f5a", inner, w=4.4, seed=602))
    lg = lib.rad_grad([(0, "#fff0c8", .5), (.6, "#ffd890", .14), (1, "#ffd890", 0)], 300, 300, 1300, 1300)
    s.append(f'<rect x="-600" y="-600" width="2300" height="3400" fill="url(#{lg})" style="mix-blend-mode:screen"/>')
    return "".join(s)


def card_static(lib):
    from ink import ellipse_pts
    s = []
    s.append(lib.blob(lib.rect_pts(CX0 + 26, CY1 - 20, CX1 + 40, CY1 + 30, 20), "#4a2a10", .4, lib.blur(14)))
    pts = lib.rect_pts(CX0, CY0, CX1, CY1, 64)
    inner = lib.blob(lib.rect_pts(CX1 - 60, CY0 - 10, CX1 + 10, CY1 + 10), CARD_SH, 1)
    inner += lib.blob(lib.rect_pts(CX0 - 10, CY1 - 44, CX1 + 10, CY1 + 10), CARD_SH, 1)
    inner += lib.line([(CX0 + 70, CY0 + 26), (CX1 - 140, CY0 + 22)], 5, "#3a3a3e", seed=620, op=.9)
    s.append(lib.shape(pts, CARD, inner, w=6, seed=621))
    # аватарка: круг с картинкой + тушь
    ax, ay, ar = AV
    cid = lib.clip_of(ellipse_pts(ax, ay, ar, ar, 28))
    s.append(f'<g clip-path="url(#{cid})"><image href="{_avatar_uri()}" x="{ax - ar}" y="{ay - ar}" width="{2 * ar}" height="{2 * ar}"/></g>')
    s.append(f'<path d="{lib.ink_closed(ellipse_pts(ax, ay, ar, ar, 28), 5.2, seed=622)}" fill="{lib.INK}"/>')
    return "".join(s)


def name_link(lib, t, t0):
    """Имя с лапками и ссылка: проявляются с подъёмом по очереди."""
    o = []
    for k, (y, d) in enumerate(((NAME_Y, 0.22), (LINK_Y, 0.32))):
        u = _eo((t - t0 - d) / 0.25)
        if u <= 0:
            continue
        dy = 26 * (1 - u)
        if k == 0:
            g = _text(422, y + dy, NAME, 66, "#ffffff")
            # лапки справа от имени (как 🐾 в названии канала)
            g += paw_print(lib, 770, y - 40 + dy, .95, 28, sd=640) + paw_print(lib, 800, y - 6 + dy, .78, 28, sd=641)
        else:
            g = _text(450, y + dy, LINK, 70, TG_BLUE)
            g += _text(450, SUB_Y + dy, "телеграм-канал", 40, GREY)     # без числа подписчиков
        o.append(f'<g opacity="{u:.3f}">{g}</g>')
    return "".join(o)


def button(lib, t, press, paw_pt=None):
    from ink import ellipse_pts
    e = t - press
    on = e >= 0.04
    dn = 0.0
    if e >= 0:
        dn = 12 * math.exp(-e * 10) if e < 0.4 else 0.0
    squeeze = 1 - 0.05 * math.exp(-max(0, e) * 9) * (e >= 0)
    pop = 1.0
    if on:
        pop = 1 + 0.07 * math.exp(-(e - 0.04) * 6) * math.sin((e - 0.04) * 24)
    cx, cy = (BX0 + BX1) / 2, (BY0 + BY1) / 2
    s = []
    col, sh, lip = (TG_BLUE, TG_BLUE_SH, "#14628d") if not on else (CARD_HI, "#232326", "#0e0e10")
    s.append(lib.shape(lib.rect_pts(BX0, BY0 + 16, BX1, BY1 + 14, 44), lip, "", w=5, seed=650))
    g = []
    pts = lib.rect_pts(BX0, BY0 + dn, BX1, BY1 + dn, 44)
    inner = lib.blob(lib.rect_pts(BX0, BY1 + dn - 30, BX1 + 4, BY1 + dn + 4), sh, 1)
    inner += lib.line([(BX0 + 56, BY0 + dn + 20), (BX1 - 200, BY0 + dn + 18)], 7, "#ffffff" if not on else "#48484c", seed=651, op=.5)
    # «рябь» от лапы — как отклик кнопки в приложении
    if e >= 0 and paw_pt and e < 0.6:
        r = 40 + 900 * _eo(e / 0.6, 2)
        inner += lib.blob(ellipse_pts(paw_pt[0], paw_pt[1], r, r, 24), "#ffffff", .32 * (1 - e / 0.6))
    g.append(lib.shape(pts, col, inner, w=5.6, seed=652))
    ty = cy + dn + 22
    if not on:
        g.append(_text(cx, ty, "ПОДПИСАТЬСЯ", 66, "#ffffff"))
    else:
        tx = cx + 46
        g.append(_text(tx, ty - 2, "ВЫ ПОДПИСАНЫ", 56, "#ffffff"))
        k = _eo((e - 0.04) / 0.2)
        p0, p1, p2 = (BX0 + 60, cy + dn - 2), (BX0 + 84, cy + dn + 22), (BX0 + 128, cy + dn - 30)
        if k < 0.4:
            q = max(k / 0.4, .05)
            ck = [p0, (p0[0] + (p1[0] - p0[0]) * q, p0[1] + (p1[1] - p0[1]) * q)]
        else:
            q = (k - .4) / .6
            ck = [p0, p1, (p1[0] + (p2[0] - p1[0]) * q, p1[1] + (p2[1] - p1[1]) * q)]
        g.append(lib.line(ck, 13, TG_BLUE, taper=.2, wmin=.6, seed=655))
    inner_g = "".join(g)
    s.append(f'<g transform="translate({cx:.1f} {cy + dn:.1f}) scale({pop * squeeze:.4f} {pop / max(squeeze, .9):.4f}) '
             f'translate({-cx:.1f} {-cy - dn:.1f})">{inner_g}</g>')
    return "".join(s)


# сердечки летят вверх-вправо, по стене справа от карточки — не на имя и не на ссылку
HEARTS = [(160, -900, -18, 1.2), (300, -760, 8, 1.0), (60, -1050, -6, 1.3), (420, -620, 16, 1.05), (230, -1150, -22, 0.9),
          (380, -980, 20, 0.95), (520, -820, 2, 0.8)]


def burst(lib, t, press):
    """После нажатия: сердечки фонтаном и самолётик Телеграма улетает петлёй вверх-вправо с пунктиром следа."""
    e = t - press - 0.05
    if e < 0:
        return ""
    s = []
    ox, oy = BX1 + 10, BY0 - 10
    for k, (vx, vy, rot, sz) in enumerate(HEARTS):
        ee = e - k * 0.035
        if ee <= 0:
            continue
        x = ox + vx * ee * 1.05
        y = oy + vy * ee + 950 * ee * ee
        sc = sz * 2.6 * min(1.0, ee / 0.12) * (1 - _cl((ee - 0.5) / 0.35))
        if sc < 0.2:
            continue
        s.append(heart(lib, x, y, sc, rot + 40 * ee * (1 if k % 2 else -1), 660 + k))
    # самолётик: кривая из кнопки вверх-вправо с петлёй
    def path(u):
        x = ox + 60 + 200 * u - 110 * math.sin(u * 2 * math.pi) * (1 - u)
        y = oy - 60 - 900 * u + 120 * (1 - math.cos(u * 2 * math.pi)) * (1 - u) * .5
        return x, y
    u = _cl(e / 1.1)
    ue = _eio(u) * .85 + u * .15
    if ue < 1:
        # пунктир следа
        n = 26
        pts = [path(ue * k / n) for k in range(n + 1)]
        for k in range(0, n - 1, 2):
            if k / n < ue - 0.35:
                continue
            s.append(lib.line([pts[k], pts[k + 1]], 5, "#ffffff", taper=.3, wmin=.5, seed=680 + k, op=.85))
        x, y = path(ue)
        x2, y2 = path(min(1.0, ue + 0.01))
        ang = math.degrees(math.atan2(y2 - y, x2 - x)) + 24
        r = 70 * min(1.0, e / 0.15) * (1 - _cl((ue - .8) / .2) * .5)
        body, fold, tail = plane_pts(x, y, r, ang)
        s.append(lib.blob(tail, "#b9d6ea"))
        s.append(lib.shape(body, "#ffffff", lib.blob(fold, "#cfe3f1"), w=4, seed=690))
    return "".join(s)


# ───────────────────────── кот
def cat_state(lib, cat, t, t0, press):
    """Кот въезжает справа, смотрит на карточку, тянет левую (от зрителя) лапу к кнопке и нажимает; после — в камеру, улыбка."""
    k_in = _eo((t - t0 - 0.2) / 0.38)
    X = CAT_X + 420 * (1 - k_in)
    Y = CAT_Y
    # лапа: подъём к кнопке за 0.45 с до нажатия, тычок, держит, возвращается
    a = press - 0.45
    pw = 1.45 * _eio((t - a) / 0.45)
    e = t - press
    tap = 0.0
    if e >= 0:
        tap = 0.10 * math.exp(-e * 10) * math.sin(min(e * 18, math.pi))
        if e > 0.35:
            pw *= 1 - _eio((e - 0.35) / 0.35)
    pw += tap
    look = (-0.85, 0.35) if t < press + 0.25 else (0.0, 0.0)
    if t < t0 + 0.6:
        look = (-0.6, -0.3)
    kc = _eio((t - press - 0.25) / 0.2)
    look = (look[0], look[1]) if kc <= 0 else (-0.85 * (1 - kc), 0.35 * (1 - kc))
    blink = 0.0
    for c, half in ((t0 + 0.95, 0.07), (press + 0.75, 0.08)):
        if c - half <= t <= c + half:
            blink = 1 - abs(t - c) / half
    tilt = -5 * _eio((t - t0 - 0.5) / 0.4) * (1 - kc) + 6 * kc * math.sin(max(0, t - press) * 3)
    tail = 6 * math.sin(t * 1.9) + 3 * math.sin(t * 3.3 + 1)
    st = dict(look=look, blink=blink, tilt=tilt, tail=tail, paw_l=pw, paw_l_dx=PAW_DX, perk=kc,
              smile=1.0 if kc > .5 else 0.0, flame_e=1.0 + 1.2 * math.exp(-max(0, e) * 2) * (e > 0))
    # кончик лапы в мире (для ряби кнопки)
    fx = cat.CX - 25
    tip = (fx - PAW_DX * pw * 1.6, 1306 - 150 * pw)
    paw_w = (X + (tip[0] - cat.CX) * CAT_K, Y + (tip[1] - cat.CBOT) * CAT_K)
    return X, Y, st, paw_w


# ───────────────────────── слой и кадр
def prepare(common=None):
    """Статика карточки (её defs) — вызвать в своей сцене ДО lib.static_done(), иначе dyn_begin() сотрёт её clipPath."""
    lib, _ = _mods(common)
    if "card" not in _ST:
        _ST["card"] = card_static(lib)


def layer(t, t0=0.15, press=1.7, common=None):
    """SVG-группа (мир 1080×1920): карточка, кот, всплеск; и камера (cx, cy, s, rot) — для своей сцены."""
    lib, cat = _mods(common)
    if "card" not in _ST:
        _ST["card"] = card_static(lib)
    X, Y, st, paw_w = cat_state(lib, cat, t, t0, press)
    # влёт карточки снизу с поворотом и перелётом
    u = (t - t0) / 0.36
    k = _back(u, 1.4) if u > 0 else 0.0
    dy = 1300 * (1 - k)
    rot = 7 * (1 - k)
    sc = 0.7 + 0.3 * k
    e = t - press
    g = [_ST["card"], name_link(lib, t, t0)]
    bs = _pop(t, t0 + 0.38, 0.3)
    if bs > 0:
        g.append(_sc(button(lib, t, press, paw_w), (BX0 + BX1) / 2, (BY0 + BY1) / 2, bs))
    bd = _pop(t, t0 + 0.3, 0.3)
    if bd > 0:
        wob = 6 * math.sin(t * 2.2) + (14 * math.exp(-e * 5) * math.sin(e * 20) if e > 0 else 0)
        g.append(_sc(tg_badge(lib, *BADGE), BADGE[0], BADGE[1], bd, -10 + wob))
    out = []
    if u > 0:
        out.append(f'<g transform="translate(450 {665 + dy:.1f}) rotate({rot:.2f}) scale({sc:.4f}) translate(-450 -665)">{"".join(g)}</g>')
    # свет огонька кота на стене
    fx, fy = X + (cat.FLAME_BASE[0] - cat.CX) * CAT_K, Y + (cat.FLAME_BASE[1] - cat.CBOT) * CAT_K
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    gr = lib.rad_grad([(0, "#ffb050", .34 * fl), (1, "#ffb050", 0)], fx, fy, 260, 260)
    out.insert(0, f'<rect x="{fx - 280:.1f}" y="{fy - 280:.1f}" width="560" height="560" fill="url(#{gr})" style="mix-blend-mode:screen"/>')
    out.append(cat.draw(X, Y, CAT_K, st, t))
    out.append(burst(lib, t, press))
    # камера: лёгкий наезд, толчок на нажатии
    v = _cl((t - t0) / 3.0)
    ccx, ccy, s = 540, 950 - 14 * v, 1.0 + 0.025 * _eio(v)
    if e >= 0:
        kk = math.exp(-e * 8)
        s *= 1 + 0.04 * kk * math.sin(min(e * 14, math.pi))
        ccx += 6 * kk * math.sin(e * 47)
        ccy += 8 * kk * math.sin(e * 39)
    return "".join(out), (ccx, ccy, s, 0.5 * math.sin(t * 0.9))


def frame(t, t0=0.15, press=1.7, common=None):
    """Готовый кадр SVG 1080×1920 (фон + карточка + кот)."""
    lib, cat = _mods(common)
    if "bg" not in _ST:
        _ST["bg"] = background(lib)
        prepare(common)
        lib.static_done()
    lib.dyn_begin()
    body, (ccx, ccy, s, rot) = layer(t, t0, press, common)
    return lib.svg(f'<rect width="{lib.W}" height="{lib.H}" fill="#e6a862"/><g transform="{lib.cam(ccx, ccy, s, rot)}">{_ST["bg"]}{body}</g>')


# ───────────────────────── демо
def _job(a):
    t, path, t0, press, common = a
    _mods(common)
    open(path, "w").write(frame(t, t0, press, common))
    return path


def render(out=None, dur=3.0, t0=0.15, press=1.7, common=None, sheet=None, nproc=2):
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
            subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-vf", "fps=4,scale=270:-1,tile=6x2", "-frames:v", "1", sheet])
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    sheet = args[args.index("--sheet") + 1] if "--sheet" in args else None
    common = args[args.index("--common") + 1] if "--common" in args else None
    pos = [a for a in args if a.endswith(".mp4")]
    print(render(pos[0] if pos else None, common=common, sheet=sheet))
