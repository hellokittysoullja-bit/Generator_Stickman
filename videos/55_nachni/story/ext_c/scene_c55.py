"""Рилс 55, группа C (комната): s15 s16 s17 s18 — основа scene_d рилса 51 (кот, Дима, ноутбук, таймер). Старые функции 51 ниже — не используются.
ИСХОДНО: Рилс 51 «назови чувство», группа D: спокойная комната Димы.
s13 (24.2–26.8): Дима у стола, кот рядом; глубокий вдох, выдох, плечи вниз, краснота с лица уходит, кулаки раскрываются.
s15 (29.1–32.3): телефон крупно, злой ответ стирается по буквам на «стирает» (30.0), на «пишет» (31.2) набирается спокойный.
s16 (32.3–34.2): кот рядом с Димой медленно моргает на «моргает» (33.52), мягкий тёплый свет, Дима улыбается.
s17 (34.2–36.9): кот и Дима смотрят в камеру, рукописное «кот» рисуется на слове (34.76), огонёк на хвосте.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Герои — people.py/cat.py/hand.py рилса 27 (тот же Дима и кот)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat as Cat  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import room  # noqa: E402
from lib import (DEFS, INK, blob, blur, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts,  # noqa: E402
                 shape, smooth, svg, T)

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["word"].strip(".,?!:").lower() == word.lower() and w["start"] >= after:
            return w["start"]
    raise KeyError(word)






T_KOT = wt("кот", 40.0)       # 34.76


_ST = {}
SKIN, SKIN_SH, SKIN_SH2, NAIL = "#ecc4a2", "#d39f83", "#bf8a74", "#f1cdbd"
HOOD, HOOD_SH, FOLD = "#d4a23e", "#a97b25", "#6b4a12"
BS = 0.6
D_HIP = np.array([250.0, 1262.0])
CAT_POS = (848.0, 1146.0, 0.68)
DESK_BACK, DESK_FRONT = 1108, 1160
PHONE_POS = (630, 1134)


_FONT = {}


def text_w(txt_, size):
    """Ширина строки шрифтом IDB (Inter Display Black из base.html) — для каретки."""
    if "f" not in _FONT:
        import base64
        import re
        from PIL import ImageFont
        p = "/tmp/a51d/IDB_scene.otf"
        if not os.path.exists(p):
            m = re.search(r"base64,([A-Za-z0-9+/=]+)", open(os.path.join(HERE, "base.html")).read())
            tmp = p + f".{os.getpid()}"
            open(tmp, "wb").write(base64.b64decode(m.group(1)))
            os.replace(tmp, p)
        _FONT["f"] = ImageFont.truetype(p, 100)
    return _FONT["f"].getlength(txt_) * size / 100.0


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


# ═════════════════════════════ комната ═════════════════════════════
def room_static():
    o = []
    wall, wall_sh = "#a9c3c0", "#8fada9"
    o.append(f'<rect x="-1600" y="-2200" width="4400" height="3600" fill="{wall}"/>')
    # обои: тонкие вертикальные полосы
    for k, x in enumerate(range(-1500, 2600, 130)):
        o.append(f'<rect x="{x}" y="-2200" width="22" height="3560" fill="{wall_sh}" opacity=".35"/>')
    # окно справа: тёмный вечер, луна, огни домов
    x0, y0, x1, y1 = 690, 250, 1130, 820
    sky = lin_grad([(0, "#1b2646", 1), (1, "#3d5078", 1)], 0, 0, 0, 1)
    inner = f'<rect x="{x0 - 10}" y="{y0 - 10}" width="{x1 - x0 + 20}" height="{y1 - y0 + 20}" fill="url(#{sky})"/>'
    inner += blob(ellipse_pts(880, 380, 46, 46, 18), "#f6efd2")
    inner += blob(ellipse_pts(900, 372, 40, 40, 18), "#1f2a4c")
    for (x, y) in [(760, 330), (1040, 320), (1000, 450), (790, 470), (950, 300)]:
        inner += blob(ellipse_pts(x, y, 4, 4, 6), "#f6efd2")
    inner += blob([(x0 - 10, 700), (800, 690), (800, 640), (900, 640), (900, 700), (1010, 680), (1010, 610), (1090, 610), (1090, 690),
                   (x1 + 10, 690), (x1 + 10, y1 + 10), (x0 - 10, y1 + 10)], "#141a30")
    for (x, y) in [(820, 720), (850, 760), (930, 720), (1040, 650), (1060, 730), (760, 780)]:
        inner += blob(rect_pts(x, y, x + 20, y + 28), "#f2c46a")
    inner += blob(rect_pts(900, y0, 922, y1), "#efe6d6") + blob(rect_pts(x0, 520, x1, 542), "#efe6d6")
    o.append(shape(rect_pts(x0, y0, x1, y1, 10), "#efe6d6", inner, w=5, seed=3001))
    o.append(shape(rect_pts(x0 - 24, y1 - 4, x1 + 24, y1 + 28, 6), "#efe6d6", "", w=4.4, seed=3002))
    # шторы
    for sx, xs in ((-1, 690), (1, 1130)):
        x_in, x_out = xs - sx * 10, xs + sx * 130
        cur = [(x_in, y0 - 40, 1), (x_out, y0 - 40, 1), (x_out, 900, 1), (x_in, 900, 1)]
        o.append(shape(cur, "#d98c6a", blob([(min(x_in, x_out) + 60, y0 - 40), (max(x_in, x_out), y0 - 40), (max(x_in, x_out), 900), (min(x_in, x_out) + 60, 900)],
                                            "#b9694c", .8) + "".join(line([(xs + sx * (14 + 28 * k), y0 - 30), (xs + sx * (14 + 28 * k), 890)],
                                                                          3, "#a35a40", taper=.1, wmin=.8, seed=3010 + k + (5 if sx > 0 else 0), op=.8)
                                                                     for k in range(4)), w=4.6, seed=3003 + sx))
        o.append(shape(rect_pts(min(x_in, x_out) - 4, y0 - 52, max(x_in, x_out) + 4, y0 - 36, 6), "#8a5f38", "", w=3.6, seed=3009 + sx))
    # полка слева с книгами и растением
    o.append(shape(rect_pts(40, 560, 600, 590, 4), "#a8794a", blob(rect_pts(40, 576, 600, 590), "#8a5f38"), w=4.4, seed=3020))
    bx = 80
    for k, (w_, h_, col) in enumerate([(34, 150, "#c4673f"), (30, 124, "#4f7fa8"), (38, 160, "#e9c46a"), (28, 132, "#6b9a6a"), (34, 144, "#8a5a9a")]):
        o.append(shape(rect_pts(bx, 560 - h_, bx + w_, 560, 3), col, blob(rect_pts(bx + w_ * .6, 560 - h_, bx + w_, 560), mix(col, "#000000", .2), .8),
                       w=3.6, seed=3030 + k))
        o.append(line([(bx + 6, 560 - h_ + 24), (bx + w_ - 6, 560 - h_ + 24)], 3, mix(col, "#ffffff", .5), taper=.1, wmin=.8, seed=3040 + k))
        bx += w_ + 4
    o.append(shape([(380, 560, 1), (480, 560, 1), (470, 490, 1), (390, 490, 1)], "#c4673f", blob([(440, 560), (480, 560), (470, 490), (440, 490)],
                                                                                                    "#9c4c2c"), w=4, seed=3050))
    for k in range(6):
        a = -2.4 + k * 0.5
        o.append(line([(430, 492), (430 + 70 * math.cos(a), 492 + 100 * math.sin(a))], 20, "#5f9a5a", taper=.6, seed=3051 + k))
    # картина над столом
    o.append(shape(rect_pts(300, 270, 560, 440, 6), "#efe6d6", blob(rect_pts(318, 288, 542, 422), "#e8c98a") +
                   blob([(318, 400), (400, 340), (460, 380), (542, 330), (542, 422), (318, 422)], "#7ea88a") +
                   blob(ellipse_pts(470, 335, 26, 26, 12), "#f4e6b0"), w=4.6, seed=3060))
    # пол
    o.append(f'<rect x="-1600" y="1330" width="4400" height="1000" fill="#8a6a52"/>')
    for k, y in enumerate(range(1370, 1700, 60)):
        o.append(line([(-1600, y), (2800, y + 2)], 2.6, "#6f5340", taper=.05, wmin=.9, seed=3070 + k, op=.8))
    o.append(shape(rect_pts(-1600, 1318, 2800, 1344), "#efe6d6", "", w=4.2, seed=3080))
    # коврик под ногами
    o.append(shape(ellipse_pts(430, 1486, 380, 60, 22), "#d98c6a", blob(ellipse_pts(450, 1494, 340, 40, 20), "#b9694c", .8), w=4.4, seed=3081))
    return "".join(o)


def desk_static():
    """Ножки (идут за героем) и столешница (поверх коленей)."""
    legs = []
    for k, x in enumerate((612, 1180)):
        legs.append(shape([(x - 16, DESK_FRONT + 40, 1), (x + 16, DESK_FRONT + 40, 1), (x + 12, 1478, 1), (x - 12, 1478, 1)], "#a8693f",
                          blob([(x + 2, DESK_FRONT + 40), (x + 16, DESK_FRONT + 40), (x + 12, 1478), (x + 2, 1478)], "#7f4b2b", .8), w=3.8, seed=3100 + k))
    top = []
    tp = [(340, DESK_BACK, 1), (1700, DESK_BACK, 1), (1740, DESK_FRONT, 1), (330, DESK_FRONT, 1)]
    inner = "".join(line([(340, DESK_BACK + 12 + k * 14), (1700, DESK_BACK + 12 + k * 14)], 2, "#b87a4a", taper=.1, wmin=.8, seed=3120 + k, op=.7)
                    for k in range(3))
    top.append(shape(tp, "#c88a58", inner, w=4.4, seed=3110))
    ap = [(330, DESK_FRONT, 1), (1740, DESK_FRONT, 1), (1740, DESK_FRONT + 56, 1), (330, DESK_FRONT + 56, 1)]
    top.append(shape(ap, "#a8693f", blob(rect_pts(330, DESK_FRONT + 36, 1740, DESK_FRONT + 56), "#7f4b2b", .8), w=4.6, seed=3111))
    top.append(shape(rect_pts(820, DESK_FRONT + 14, 920, DESK_FRONT + 34, 8), "#5e3720", "", w=3.2, seed=3112))
    return "".join(legs), "".join(top)


def lamp(t):
    """Настольная лампа справа: основание, два плеча, абажур; светит тёплым на стол."""
    o = []
    bx, by = 1090, DESK_BACK + 36
    o.append(blob(ellipse_pts(bx + 10, by + 4, 80, 12, 14), "#2a1408", .35))
    o.append(shape(ellipse_pts(bx, by - 6, 62, 16, 16), "#3b3f4c", "", w=4, seed=3200))
    o.append(line([(bx, by - 8), (bx - 50, by - 150), (bx - 20, by - 280)], 12, INK, taper=.05, wmin=.9, seed=3201))
    o.append(line([(bx, by - 8), (bx - 50, by - 150), (bx - 20, by - 280)], 6, "#9aa0ab", taper=.05, wmin=.9, seed=3202))
    sh = [(bx - 110, by - 292, 1), (bx + 60, by - 290, 1), (bx + 100, by - 210, 1), (bx - 150, by - 214, 1)]
    o.append(shape(sh, "#e9c46a", blob([(bx + 20, by - 290), (bx + 60, by - 290), (bx + 100, by - 210), (bx + 10, by - 212)], "#c89a3a", .8) +
                   blob(rect_pts(bx - 120, by - 286, bx + 40, by - 270), "#fbe9a8", .8), w=4.6, seed=3203))
    o.append(blob(ellipse_pts(bx - 26, by - 206, 56, 9, 12), "#fff3c0"))
    return "".join(o)


def lamp_light():
    """Тёплый свет лампы (screen) и мягкая тень по краям; поверх героев, под надписями."""
    bx, by = 700, 640
    g = rad_grad([(0, "#ffd890", .42), (.45, "#ffbe6a", .16), (1, "#ffbe6a", 0)], bx, by + 150, 800, 800)
    s = [f'<rect x="-1600" y="-2200" width="4400" height="3800" fill="url(#{g})" style="mix-blend-mode:screen"/>']
    g2 = rad_grad([(0, "#000000", 0), (.62, "#000000", 0), (1, "#1a0e18", .38)], 600, 1000, 1500, 1500)
    s.append(f'<rect x="-1600" y="-2200" width="4400" height="3800" fill="url(#{g2})"/>')
    return "".join(s)


def mug(t):
    x, y = 620, DESK_BACK + 34
    o = [blob(ellipse_pts(x + 6, y + 2, 52, 9, 12), "#2a1408", .3)]
    body = [(x - 38, y - 70, 1), (x + 38, y - 70, 1), (x + 34, y - 8), (x + 22, y, 1), (x - 22, y, 1), (x - 34, y - 8)]
    o.append(shape(body, "#f3ede2", blob([(x + 10, y - 70), (x + 38, y - 70), (x + 34, y - 8), (x + 22, y), (x + 8, y)], "#d8d0c0", .9) +
                   blob(rect_pts(x - 38, y - 50, x + 38, y - 36), "#3f7a72", .9), w=4.2, seed=3210))
    o.append(line([(x + 36, y - 56), (x + 66, y - 52), (x + 64, y - 22), (x + 30, y - 18)], 7, INK, taper=.1, wmin=.8, seed=3211))
    o.append(line([(x + 36, y - 56), (x + 66, y - 52), (x + 64, y - 22), (x + 30, y - 18)], 3, "#f3ede2", taper=.1, wmin=.8, seed=3212))
    o.append(blob(ellipse_pts(x, y - 70, 38, 8, 12), "#6b3f26"))
    # пар: три волнистые линии
    for k, dx in enumerate((-18, 2, 22)):
        ph = t * 1.3 + k * 1.7
        pts = [(x + dx + 8 * math.sin(ph + j * .8), y - 90 - j * 22) for j in range(6)]
        o.append(line(pts, 5, "#f4f1ea", taper=.8, wmin=.1, seed=3220 + k, peak=.4))
    return "".join(o)


def phone_desk(t, glow=0.0, buzz=0.0):
    """Телефон экраном вверх на столе (вид спереди-сверху, сплющен): тёмный корпус, светлый экран с полосками чата."""
    x, y = PHONE_POS
    o = []
    quad = [(x - 90, y - 22, 1), (x + 76, y - 30, 1), (x + 108, y + 14, 1), (x - 120, y + 24, 1)]
    o.append(blob([(q[0] + 10, q[1] + 16) for q in quad], "#2a1408", .3))
    o.append(blob([(q[0], q[1] + 10) for q in quad], "#15161c"))
    o.append(shape(quad, "#262833", "", w=3.6, seed=3230))
    scr = [(x - 80, y - 17, 1), (x + 68, y - 24, 1), (x + 94, y + 10, 1), (x - 106, y + 18, 1)]
    col = mix("#46537a", "#cfe6ff", .35 + .65 * glow)
    o.append(blob(scr, col))
    for k, (u0, u1, vv) in enumerate([(-70, 10, -8), (-76, 30, 3), (-88, -20, 12)]):
        o.append(line([(x + u0, y + vv), (x + u1, y + vv - 1)], 5, mix(col, "#ffffff", .7), taper=.1, wmin=.9, seed=3240 + k))
    if glow > 0.05:
        g = rad_grad([(0, "#cfe6ff", .5 * glow), (1, "#cfe6ff", 0)], x, y, 200, 70)
        o.append(f'<rect x="{x - 210}" y="{y - 90}" width="420" height="180" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    return "".join(o)


def pendant():
    """Подвесной абажур над столом (шнур уходит за верх кадра)."""
    x, y = 700, 560
    o = [line([(x, -400), (x, y - 70)], 6, INK, taper=.02, wmin=.95, seed=3250)]
    sh = [(x - 40, y - 70, 1), (x + 40, y - 70, 1), (x + 110, y + 30, 1), (x - 110, y + 30, 1)]
    o.append(shape(sh, "#e9c46a", blob([(x + 20, y - 70), (x + 40, y - 70), (x + 110, y + 30), (x + 30, y + 30)], "#c89a3a", .85), w=4.6, seed=3251))
    o.append(shape(rect_pts(x - 14, y - 84, x + 14, y - 68, 4), "#3b3f4c", "", w=3.2, seed=3252))
    o.append(blob(ellipse_pts(x, y + 30, 100, 11, 14), "#fff3c0"))
    return "".join(o)


def static_all():
    legs, top = desk_static()
    _ST["room"] = room_static()
    _ST["legs"] = legs
    _ST["top"] = top
    _ST["light"] = lamp_light()
    _ST["lamp"] = pendant()
    lib.static_done()


# ═════════════════════════════ герои ═════════════════════════════
def dima(lean, arms, hands, expr, head_ang=0.0, torso_k=1.0, head_off=(0, 0), hip_off=(0, 0), feet_dx=0.0):
    hip = D_HIP + np.array(hip_off, float)
    p = dict(hip=tuple(hip), scale=BS, lean=lean, torso_k=torso_k, feet={"n": ((470 + feet_dx, 1468), 0.0), "f": ((445 + feet_dx, 1462), 0.0)},
             arms=arms, hands=hands, expr=expr, head_ang=head_ang, head_off=head_off, hood=0.0, strings=(0, 0))
    return people.draw(p, "dima")


def fist(c, thumb=None):
    return dict(kind="open", flip=1, dir=(1, .35), curl=(c, c, c, c * .9), spread=.04 + .12 * (1 - c), thumb=c if thumb is None else thumb, bend=.1)


def cat_draw(t, st):
    x, y, k = CAT_POS
    sh = blob(ellipse_pts(x + 12, y + 6, 150 * k * 1.25, 12, 16), "#2a1408", .32)
    return sh + Cat.draw(x, y, k, st, t)


def flame_glow(t, st, k=1.0):
    x, y, ck = CAT_POS
    fx, fy = x + (995 - 836) * ck, y + (1076 - 1306) * ck
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    g = rad_grad([(0, "#ffb050", .5 * fl * k), (1, "#ffb050", 0)], fx, fy, 300, 300)
    return f'<rect x="{f(fx - 320)}" y="{f(fy - 320)}" width="640" height="640" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def motes(t, seed=5, n=26, box=(300, 560, 1100, 1180)):
    """Пылинки в тёплом свете лампы: плывут вверх, мерцают."""
    rs = np.random.RandomState(seed)
    o = []
    for i in range(n):
        x0, y0 = rs.uniform(box[0], box[2]), rs.uniform(box[1], box[3])
        sp, ph, r = rs.uniform(10, 26), rs.uniform(0, 6.28), rs.uniform(2.2, 4.6)
        y = box[1] + (y0 - box[1] - sp * t) % (box[3] - box[1])
        x = x0 + 18 * math.sin(t * .7 + ph)
        a = (0.55 + 0.35 * math.sin(t * 2.2 + ph)) * smooth(box[1], box[1] + 80, y) * (1 - smooth(box[3] - 120, box[3], y))
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#fff0c4" opacity="{a * .8:.2f}"/>')
    return "".join(o)


def world(t, d, cat_st, cam, extra_front="", glow=0.0, flame_k=1.0, with_motes=False, between="", chair_dx=0.0):
    set_ink(cam[2])
    w = [_ST["room"], _ST["lamp"]]
    w.append(room.chair(D_HIP[0] + chair_dx, D_HIP[1] + 4, 1, 2300))
    w.append(_ST["legs"])
    w.append(d.get("legs", ""))
    w.append(_ST["top"])
    w.append(_ST["light"])
    if with_motes:
        w.append(motes(t))
    w.append(phone_desk(t, glow))
    w.append(cat_draw(t, cat_st))
    w.append(d["arm_f"])
    w.append(d["body"])
    w.append(d["arm_n"])
    w.append(between)
    w.append(extra_front)
    # огонёк, пылинки
    w.append(flame_glow(t, cat_st, flame_k))
    return f'<g transform="{lib.cam(*cam)}">{"".join(w)}</g>'


def puff(t, t0, x, y, dur=1.1):
    """Выдох: три коротких штриха вылетают от рта вправо-вниз и истаивают (заливка, без прозрачности)."""
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return ""
    o = []
    for k in range(3):
        v = clamp(u * 1.3 - k * .12)
        if v <= 0 or v >= 1:
            continue
        L = 70 * math.sin(math.pi * v) ** .7
        x0 = x + 30 + 120 * ease_out(v) + k * 6
        y0 = y + 18 + 36 * v + (k - 1) * 30
        w = 9 * (1 - v) + 2
        pts = [(x0 - L, y0 - 4 * k), (x0 - L * .4, y0 + 5 * math.sin(v * 6 + k)), (x0, y0 + 3)]
        o.append(line(pts, w + 3, INK, taper=.8, wmin=.1, seed=5100 + k))
        o.append(line(pts, w, "#f4f7f6", taper=.8, wmin=.1, seed=5110 + k))
    return "".join(o)


# ═════════════════════════════ s13 ═════════════════════════════
def frame13(t):
    inh = smooth(24.12, 24.72, t)
    exh = smooth(24.80, 25.95, t)
    b = inh * (1 - exh)
    relax = smooth(24.72, 26.3, t)
    trem = (1 - smooth(24.0, 24.85, t))
    sx, sy = 2.2 * trem * math.sin(t * 52), 1.6 * trem * math.sin(t * 61 + 1)
    c = 1 - smooth(24.85, 25.7, t)
    flush = .92 * (1 - smooth(24.7, 26.7, t))
    closed = smooth(24.18, 24.36, t) * (1 - smooth(24.74, 24.9, t))
    sm = smooth(25.9, 26.7, t)
    expr = dict(lid=.62 - .3 * smooth(24.6, 25.4, t), look=(.55, .1 * relax), closed=closed, brows=("det", "calm", smooth(24.55, 25.5, t)),
                mouth="smile" if sm > .05 else "flat", smile=.3 + .5 * sm, flush=flush, blush=.5 * smooth(25.3, 26.4, t))
    lean = .11 - .06 * b + .035 * relax
    tk = 1.0 + .05 * b - .018 * relax
    arms = {"n": ("ik", (478 + 6 * relax, DESK_FRONT - 18 - 6 * b + sy)), "f": ("ik", (500 + 8 * relax, DESK_BACK + 8 + sy))}
    hands = {"n": fist(c), "f": fist(c)}
    d = dima(lean, arms, hands, expr, head_ang=-.05 * b + .045 * exh * (1 - relax * .3), torso_k=tk, head_off=(0, -10 * b + 6 * relax),
             hip_off=(sx, sy))
    mouth = d["head"] + np.array([62.0, 92.0]) * BS
    st = dict(look=(-1.0 + .25 * relax, .15), turn=-.9 + .3 * relax, blink=Cat_blink(t, [(25.55, .2, .35)]), ear=6 * bump(t, 24.5, .5) - 4 * bump(t, 25.4, .3),
              perk=.5 * smooth(24.2, 24.7, t) * (1 - smooth(24.9, 25.4, t)), tail=5 * osc(t, .45) + 2 * osc(t, 1.3), smile=1 if t > 26.0 else 0, tilt=-3 * smooth(24.4, 25.2, t) * (1 - smooth(25.6, 26.4, t)))
    u = clamp((t - 24.0) / 3.0)
    cam = (548 + 6 * u, 1185 - 6 * u, 1.2 + .09 * ease_io(u), -.7 + .9 * u)
    return world(t, d, st, cam, extra_front=puff(t, 24.82, *mouth, dur=1.2), flame_k=1.0 + .3 * relax, with_motes=True)


def Cat_blink(t, items):
    """items: (центр, полу-закрытие, выдержка) — плавное смыкание/раскрытие век."""
    b = 0.0
    for c, half, hold in items:
        a = c - half
        if a <= t <= c + hold + half:
            if t < c:
                b = ease_io((t - a) / half)
            elif t < c + hold:
                b = 1.0
            else:
                b = 1 - ease_io((t - c - hold) / half)
    return b


# ═════════════════════════════ s15: телефон крупно ═════════════════════════════
ANGRY = ("Да сколько можно?!", "Ты вообще слышишь?!")
CALM = ("Мне обидно.", "Поговорим?")
PX0, PX1, PY0, PY1 = 170, 910, 110, 1760            # корпус телефона
KEYS_Y = 990


def chars_visible(t):
    """Сколько знаков каждой реплики видно: (злые, спокойные) — целые числа."""
    na = len(ANGRY[0]) + len(ANGRY[1])
    nc = len(CALM[0]) + len(CALM[1])
    if t < ERASE_T0:
        a = na
    elif t >= ERASE_T1:
        a = 0
    else:
        u = (t - ERASE_T0) / (ERASE_T1 - ERASE_T0)
        a = int(round(na * (1 - (u ** 1.35))))     # зажатый «забой» разгоняется
    if t < TYPE_T0:
        c = 0
    elif t >= TYPE_T1:
        c = nc
    else:
        c = int(round(nc * ((t - TYPE_T0) / (TYPE_T1 - TYPE_T0))))
    return a, min(c, nc)


def split_lines(lines, n):
    out = []
    for ln in lines:
        k = min(n, len(ln))
        out.append(ln[:k])
        n -= k
        if n <= 0:
            n = 0
    return out


def txt(x, y, s, size, fill, weight=900, extra=""):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x}" y="{y}" font-family="IDB" font-weight="{weight}" font-size="{size}" fill="{fill}" {extra}>{s}</text>'


def thumb_poly(base, tip, w0, w1):
    """Большой палец: «сосиска» от основания к кончику с лёгким изгибом (две точки управления)."""
    b, tpt = np.array(base, float), np.array(tip, float)
    d = tpt - b
    n = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9)
    mid = b + d * .5 + n * 26
    S = lib.sample([tuple(b), tuple(mid), tuple(tpt)], False, 3.0)
    Tg = np.gradient(S, axis=0)
    Tg /= np.linalg.norm(Tg, axis=1, keepdims=True) + 1e-9
    N = np.stack([-Tg[:, 1], Tg[:, 0]], 1)
    Wd = np.linspace(w0, w1, len(S))[:, None] / 2
    L, R = S + N * Wd, S - N * Wd
    end, tn, nn = S[-1], Tg[-1], N[-1]
    r = w1 / 2
    cap = [tuple(end + nn * r * math.cos(a) + tn * r * math.sin(a)) for a in np.linspace(0, math.pi, 9)[1:-1]]
    step = max(1, len(S) // 9)
    return [tuple(p) for p in L[::step]] + [tuple(L[-1])] + cap + [tuple(R[-1])] + [tuple(p) for p in R[::-step]], tpt, tn, nn


def thumb_svg(base, tip, w0, w1, seed, press=0.0, side=1):
    pts, tpt, tn, nn = thumb_poly(base, tip, w0, w1)
    d = np.array(tip, float) - np.array(base, float)
    sh = blob([p for p in pts[:len(pts) // 2]], SKIN_SH, .55)
    o = shape(pts, SKIN, sh, w=5, seed=seed)
    # ноготь у кончика
    nl = w1 * .62
    c0 = tpt - tn * (w1 * .46)
    nail = ellipse_pts(c0[0], c0[1], w1 * .3, nl * .42, 10, rot=math.degrees(math.atan2(tn[1], tn[0])) + 90)
    o += shape(nail, NAIL, "", w=2.6, seed=seed + 5)
    # складка сустава
    m = np.array(base, float) + d * .55
    o += line([tuple(m - nn * w0 * .3), tuple(m + nn * w0 * .05)], 2.6, SKIN_SH2, seed=seed + 6, op=.8)
    return o


KEY_POS = []         # центры клавиш (x, y) — на левой и правой половине
for _r, (_n, _x0, _y) in enumerate([(10, 205, 1040), (9, 238, 1150), (7, 285, 1260)]):
    for _k in range(_n):
        KEY_POS.append((_r, _k, _x0 + _k * 68, _y))


def key_svg(x, y, w, h, press, seed, fill="#fbfaf7", icon=None):
    dy = 7 * press
    o = blob(rect_pts(x - w / 2, y - h / 2 + 8, x + w / 2, y + h / 2 + 8, 12), "#8a8f9c")
    o += shape(rect_pts(x - w / 2, y - h / 2 + dy, x + w / 2, y + h / 2 + dy - (4 if press else 0), 12),
               mix(fill, "#9bd0ff", .5 * press) if press else fill, "", w=3.2, seed=seed)
    if icon == "bksp":
        cx, cy = x, y + dy
        o += shape([(cx - 28, cy, 1), (cx - 8, cy - 18, 1), (cx + 28, cy - 18, 1), (cx + 28, cy + 18, 1), (cx - 8, cy + 18, 1)], "#e6e8ee", "", w=3, seed=seed + 1)
        o += line([(cx - 4, cy - 8), (cx + 14, cy + 8)], 4, INK, taper=.1, wmin=.9, seed=seed + 2)
        o += line([(cx + 14, cy - 8), (cx - 4, cy + 8)], 4, INK, taper=.1, wmin=.9, seed=seed + 3)
    return o


def rrect(x0, y0, x1, y1, r=0, n=7):
    """Скруглённый прямоугольник плотными точками дуг (без «рогов» у углов)."""
    if r <= 0:
        return [(x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)]
    r = min(r, (x1 - x0) / 2 - .5, (y1 - y0) / 2 - .5)
    out = []
    for (cx, cy, a0) in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)) + ((1,) if k in (0, n) else ()))
    return out


def phone_close(t):
    breath = 9 * math.sin(2 * math.pi * (t - 28.9) / 3.6)
    calm = smooth(29.0, 30.2, t)
    trem = (1 - calm) * 5.0
    tx, ty = trem * math.sin(t * 43), trem * math.sin(t * 57 + 1)
    na, nc = chars_visible(t)
    erasing = ERASE_T0 - .05 <= t <= ERASE_T1 + .08
    typing = TYPE_T0 - .05 <= t <= TYPE_T1 + .08
    o = []
    # ── руки позади телефона: ладони выглядывают по бокам корпуса (пальцы за ним, спереди только большие)
    for sd, sx in ((0, -1), (1, 1)):
        edge = PX0 if sx < 0 else PX1
        yy = 1330 + 8 * math.sin(t * 2 + sd)
        xa, xb = edge - sx * 40, edge + sx * 96
        palm = rrect(min(xa, xb), yy - 330, max(xa, xb), 1760, 56)
        inner = blob(rrect(min(edge + sx * 60, xb), yy - 320, max(edge + sx * 60, xb), 1750, 40), SKIN_SH, .85)
        inner += "".join(line([(edge + sx * 6, yy - 200 + k * 90), (edge + sx * 50, yy - 190 + k * 90)], 3, SKIN_SH2, seed=6040 + k + 7 * sd, op=.8)
                         for k in range(3))
        o.append(shape(palm, SKIN, inner, w=4.8, seed=6050 + sd))
    # ── корпус
    body = rrect(PX0, PY0, PX1, PY1, 96)
    o.append(blob(T(body, 14, 18), "#101018", .35))
    o.append(shape(body, "#2b2e3a", blob(rrect(PX0 + 8, PY0 + 8, PX0 + 24, PY1 - 8, 8), "#454a5c", .8), w=5.4, seed=6100))
    sx0, sx1, sy0, sy1 = PX0 + 22, PX1 - 22, PY0 + 24, PY1 - 24
    scr_id = lib.clip_of(rrect(sx0, sy0, sx1, sy1, 76))
    s = [f'<g clip-path="url(#{scr_id})">', f'<rect x="{sx0}" y="{sy0}" width="{sx1 - sx0}" height="{sy1 - sy0}" fill="#f6f3ec"/>']
    # шапка чата
    s.append(f'<rect x="{sx0}" y="{sy0}" width="{sx1 - sx0}" height="210" fill="#ffffff"/>')
    s.append(f'<rect x="{sx0}" y="{sy0 + 208}" width="{sx1 - sx0}" height="4" fill="#dad6cc"/>')
    s.append(blob(ellipse_pts(280, sy0 + 130, 46, 46, 16), "#9fc5a8"))
    s.append(blob(ellipse_pts(280, sy0 + 116, 14, 14, 10), "#f6f3ec") + blob(ellipse_pts(280, sy0 + 156, 26, 18, 10), "#f6f3ec"))
    s.append(blob(rrect(350, sy0 + 100, 590, sy0 + 124, 12), "#3a3e4c"))
    s.append(blob(rrect(350, sy0 + 136, 500, sy0 + 154, 9), "#b4b0a6"))
    # входящее сообщение: злое слово крупными знаками (заглушка из полос + «!»)
    bub = rrect(220, 360, 760, 560, 40)
    s.append(shape(bub, "#e4e0d6", blob(rrect(220, 520, 760, 560, 30), "#cfcabe", .8), w=3.2, seed=6110))
    for k, wd in enumerate((420, 330, 240)):
        s.append(blob(rrect(256, 396 + k * 46, 256 + wd, 420 + k * 46, 10), "#7a766c"))
    s.append(blob(rrect(720, 450, 740, 500, 6), "#c8463a"))
    # исходящий предыдущий пузырь, чтобы чат не пустовал
    s.append(shape(rrect(580, 600, 860, 668, 30), "#bfe2c4", "", w=3, seed=6111))
    s.append(blob(rrect(610, 626, 810, 644, 8), "#6a8f72"))
    # поле ввода
    k_ang = na / float(len(ANGRY[0]) + len(ANGRY[1]))
    fld_col = mix("#4a86d6", "#c8463a", .0)
    border = mix("#5aa56a", "#d8453a", k_ang)
    s.append(shape(rrect(200, 740, 780, 960, 56), "#ffffff", "", w=4.4, seed=6120, ink_color=border))
    ar_col = mix("#4fa563", "#d8453a", k_ang)
    s.append(blob(ellipse_pts(842, 850, 52, 52, 18), ar_col))
    s.append(line([(842, 884), (842, 820)], 9, "#ffffff", taper=.05, wmin=.9, seed=6121))
    s.append(line([(818, 842), (842, 818), (866, 842)], 9, "#ffffff", taper=.05, wmin=.9, seed=6122))
    # текст
    ta = split_lines(ANGRY, na)
    tc = split_lines(CALM, nc)
    ink_txt = mix("#2a2430", "#a82a22", k_ang)
    caret_on = int(t * 2.4) % 2 == 0
    if na > 0:
        for i, ln in enumerate(ta):
            if ln:
                s.append(txt(228, 826 + i * 62, ln, 46, "#a82a22" if k_ang > .5 else "#7a3a34"))
        li = max(0, len([x for x in ta if x]) - 1)
        cxp = 228 + len(ta[li]) * 29.5 if False else None
    else:
        for i, ln in enumerate(tc):
            if ln:
                s.append(txt(228, 826 + i * 62, ln, 46, "#23402b"))
    # каретка: ширина по числу знаков (шрифт моно-приблизительно)
    cur = ta if na > 0 else tc
    nz = [i for i, x in enumerate(cur) if x]
    if nz and caret_on:
        li = nz[-1]
        cx_ = 228 + text_w(cur[li], 46) + 4
        s.append(f'<rect x="{cx_:.1f}" y="{826 + li * 62 - 42}" width="6" height="54" rx="3" fill="#2a2430"/>')
    elif not nz and caret_on:
        s.append(f'<rect x="232" y="784" width="6" height="54" rx="3" fill="#2a2430"/>')
    # клавиатура
    s.append(f'<rect x="{sx0}" y="{KEYS_Y - 12}" width="{sx1 - sx0}" height="{sy1 - KEYS_Y + 12}" fill="#cfd3dc"/>')
    # нажатые клавиши
    pr = {}
    if typing and not erasing:
        i = int((t - TYPE_T0) / .07)
        for dk in (0, 1):
            ph = ((t - TYPE_T0) / .07 - i - dk * 0.5) % 1
        idx = [(i * 7 + 3) % len(KEY_POS), (i * 5 + 11) % len(KEY_POS)]
        pr[idx[0]] = 1.0 - ((t - TYPE_T0) / .07 % 1) * .8
    for j, (r_, k_, x_, y_) in enumerate(KEY_POS):
        s.append(key_svg(x_, y_, 58, 92, pr.get(j, 0.0), 6200 + j))
    s.append(key_svg(795, 1260, 120, 92, 1.0 if erasing else 0.0, 6300, fill="#b9bfcc", icon="bksp"))
    s.append(key_svg(245, 1260, 88, 92, 0, 6301, fill="#b9bfcc"))
    s.append(key_svg(560, 1370, 330, 92, 0, 6302))
    s.append(key_svg(250, 1370, 100, 92, 0, 6303, fill="#b9bfcc"))
    s.append(key_svg(830, 1370, 100, 92, 0, 6304, fill="#4a86d6"))
    s.append("</g>")
    o.append("".join(s))
    o.append(f'<path d="{lib.ink_closed(rrect(sx0, sy0, sx1, sy1, 76), 3.6, seed=6130)}" fill="{INK}"/>')
    # ── большие пальцы поверх экрана
    # левый: по клавишам слева, правый: на «забое» при стирании, потом по клавишам справа
    if erasing:
        rtip = (795 + 6 * math.sin(t * 30), 1262 + 8 * abs(math.sin(t * 24)) + 0)
    elif typing:
        i = (t - TYPE_T0) / .07
        rtip = (560 + 230 * (0.5 + 0.5 * math.sin(i * 1.9 + 1)), 1120 + 120 * (0.5 + 0.5 * math.sin(i * 2.7)) + 14 * (1 - 2 * abs((i % 1) - .5)))
    else:
        rtip = (700 + 12 * math.sin(t * 1.4), 1230 + 14 * math.sin(t * 1.1))
    if typing and not erasing:
        i = (t - TYPE_T0) / .07 + .5
        ltip = (240 + 260 * (0.5 + 0.5 * math.sin(i * 2.3)), 1090 + 110 * (0.5 + 0.5 * math.sin(i * 3.1 + 2)) + 14 * (1 - 2 * abs((i % 1) - .5)))
    else:
        ltip = (400 + 10 * math.sin(t * 1.3), 1190 + 12 * math.sin(t * 1.0 + 1))
    rr = 0.0 if not erasing else 1.0
    o.append(thumb_svg((PX1 - 20, 1600), (rtip[0], rtip[1] + 4 * rr), 122, 94, 6400, side=1))
    o.append(thumb_svg((PX0 + 20, 1600), ltip, 122, 94, 6410, side=-1))
    # рукава (горчичные) в нижних углах, поверх оснований пальцев
    for sx, sd in ((-1, 0), (1, 1)):
        xx = PX0 - 120 if sx < 0 else PX1 + 120
        sl = [(xx - sx * 260, 1560, 1), (xx + sx * 150, 1620, 1), (xx + sx * 200, 2100, 1), (xx - sx * 220, 2100, 1)]
        o.append(shape(sl, HOOD, blob([(xx, 1600), (xx + sx * 150, 1620), (xx + sx * 200, 2100), (xx, 2100)], HOOD_SH, .8) +
                       "".join(line([(xx - sx * 150 + sx * k * 50, 1650), (xx - sx * 150 + sx * k * 50 + sx * 20, 1900)], 3.4, FOLD, taper=.1, wmin=.8,
                                    seed=6500 + k + 9 * sd, op=.7) for k in range(5)), w=5, seed=6510 + sd))
    tile = f'translate({tx:.2f} {ty + breath:.2f})'
    return f'<g transform="{tile}">{"".join(o)}</g>'


def frame15(t):
    u = clamp((t - 28.9) / 3.6)
    cam = lib.cam(540 + 24 * (u - .5), 880 - 40 * u + 20, 1.0 + .1 * ease_io(u), -1.6 + 2.2 * u)
    bg = '<rect x="-400" y="-400" width="1900" height="2800" fill="#3a2a3a"/>'
    g = rad_grad([(0, "#ffd890", .38), (1, "#ffd890", 0)], 540, 800, 900, 900)
    bgl = f'<rect x="-400" y="-400" width="1900" height="2800" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    # живой фон: плавающие пылинки света за телефоном
    set_ink(1.0)
    body = phone_close(t)
    return f'<g transform="{cam}">{bg}{bgl}{motes(t, 9, 22, (-100, 200, 1180, 1700))}{body}</g>'


# ═════════════════════════════ s16, s17 ═════════════════════════════
def frame_pair(t, kind):
    sm = smooth(32.4, 33.4, t)
    if kind == "s16":
        look = (.85, .1)
        mouth = "smile"
        sml = .25 + .75 * smooth(32.5, 33.9, t)
        blink_d = Cat_blink(t, [(32.7, .06, 0.0)])
    else:
        look = (-.2 + .08 * osc(t, .2), .0)
        mouth = "smile"
        sml = .9
        blink_d = Cat_blink(t, [(35.4, .06, 0.0)])
    exh = smooth(32.3, 34.2, t)
    lean = .10 + .02 * math.sin(t * 1.3) - (.02 * exh if kind == "s16" else 0)
    expr = dict(lid=.34, look=look, closed=blink_d, brows="calm", mouth=mouth, smile=sml, blush=.55)
    hands = {"n": dict(kind="open", flip=1, dir=(1, .35), curl=(.3, .3, .35, .4), spread=.1, thumb=.3, bend=.1),
             "f": dict(kind="open", flip=1, dir=(1, .3), curl=(.3, .35, .4, .45), spread=.08, thumb=.4)}
    dx = 0.0
    if kind == "s17":
        dx = 170 * ease_io(clamp((t - 34.0) / 0.9))      # придвинулся к коту вместе со стулом
    arms = {"n": ("ik", (452 + .6 * dx + 4 * math.sin(t * 1.0), DESK_FRONT - 24)), "f": ("ik", (500 + .6 * dx, DESK_BACK + 10))}
    d = dima(lean, arms, hands, expr, head_ang=(-.03 if kind == "s17" else .02) + .012 * math.sin(t * 1.1), torso_k=.99,
             head_off=(0, 3 * math.sin(t * 2 * math.pi / 3.2)), hip_off=(dx, 0), feet_dx=dx)
    if kind == "s16":
        blink = Cat_blink(t, [(T_MORGAET - .28 + .28, .28, .28 + .08)])   # закрыт 33.52–33.88, открывается к 34.16
        st = dict(look=(-.95 + .25 * smooth(32.4, 33.0, t), .1), turn=-.7 + .5 * smooth(32.3, 33.1, t), blink=blink,
                  ear=5 * bump(t, 32.55, .5), tail=5 * osc(t, .45) + 2 * osc(t, 1.3), smile=1 if t > T_MORGAET - .1 else 0,
                  tilt=-2 + 2.5 * smooth(32.3, 33.6, t), perk=.2, flame_e=1.0)
        u = clamp((t - 32.1) / 2.3)
        cam = (545 + 25 * ease_io(u), 1015 - 10 * u, 1.45 + .17 * ease_io(u), -.8 + 1.2 * u)
        return world(t, d, st, cam, glow=.2, flame_k=1.2, with_motes=True)
    # s17
    st = dict(look=(.05 * osc(t, .3), .05), turn=0.0, blink=Cat_blink(t, [(35.9, .07, 0.0)]), ear=7 * bump(t, 34.2, .4) - 5 * bump(t, 35.2, .35),
              tail=7 * osc(t, .6) + 3 * osc(t, 1.7), smile=1, tilt=2 * osc(t, .25), perk=.3 * smooth(34.0, 34.6, t), flame_e=1.5)
    u = clamp((t - 34.0) / 2.9)
    cam = (560 + 70 * ease_io(u), 1040 + 10 * u, 1.24 + .3 * ease_io(u), -.6 + .8 * u)
    spark = sparks(t)
    wsvg = world(t, d, st, cam, glow=.35, flame_k=1.5 + .3 * math.sin(t * 9), with_motes=True, between=spark, chair_dx=dx)
    return wsvg + write_kot(t)


# ── рукописное «кот»
def _letter_paths():
    k = [[(0, 0), (0.02, 1.0)], [(0.9, 0.02), (0.1, 0.56)], [(0.2, 0.5), (0.95, 1.0)]]
    oo = [(0.5 + 0.5 * math.sin(a), 0.5 - 0.5 * math.cos(a)) for a in np.linspace(0.3, 2 * math.pi + 0.5, 24)]
    tt = [[(0.0, 0.0), (1.0, 0.0)], [(0.5, 0.0), (0.5, 1.0)]]
    return [("к", k, (34.76, 35.02)), ("о", [oo], (35.04, 35.30)), ("т", tt, (35.32, 35.56))]


def write_kot(t):
    if t < T_KOT - .02:
        return ""
    H_, Wd = 200, 160
    gap = 36
    total = 3 * Wd + 2 * gap
    x0 = 540 - total / 2
    y0 = 385
    o = []
    for li, (ch, strokes, (a, b)) in enumerate(_letter_paths()):
        lx = x0 + li * (Wd + gap)
        npt = sum(1 for _ in strokes)
        for si, st_ in enumerate(strokes):
            ta = a + (b - a) * si / len(strokes)
            tb = a + (b - a) * (si + 1) / len(strokes)
            u = clamp((t - ta) / (tb - ta))
            if u <= 0:
                continue
            P = lib.sample([(lx + px * Wd, y0 + py * H_) for px, py in st_], False, 4.0)
            n = max(2, int(len(P) * u))
            seg = [tuple(p) for p in P[:n]]
            if len(seg) < 2:
                continue
            o.append(line(seg, 40, INK, taper=.04, wmin=.96, seed=7000 + li * 5 + si))
            o.append(line(seg, 26, "#fff3cf", taper=.04, wmin=.96, seed=7050 + li * 5 + si))
    # подчёркивание
    u = clamp((t - 35.58) / .3)
    if u > 0:
        ux0, ux1 = x0 - 10, x0 + total + 10
        pts = [(ux0, y0 + H_ + 40 + 6 * math.sin(k * .9)) for k in (0,)] + [(ux0 + (ux1 - ux0) * v, y0 + H_ + 46 - 14 * math.sin(v * 3.1)) for v in np.linspace(0, u, 8)]
        o.append(line(pts, 26, INK, taper=.3, wmin=.6, seed=7100))
        o.append(line(pts, 15, "#ffb050", taper=.3, wmin=.6, seed=7101))
    # лёгкий «выскок» всей надписи на ударе
    e = t - T_KOT
    sc = 1 + .06 * math.exp(-e * 9) * math.sin(min(e * 14, math.pi)) if e >= 0 else 1
    return f'<g transform="translate({x0 + total / 2:.1f} {y0 + H_ / 2:.1f}) scale({sc:.4f}) translate({-(x0 + total / 2):.1f} {-(y0 + H_ / 2):.1f})">{"".join(o)}</g>'


def sparks(t):
    """Искры от огонька: летят вверх, гаснут (заливка, без прозрачности)."""
    x, y, ck = CAT_POS
    fx, fy = x + (995 - 836) * ck, y + (1076 - 1306) * ck - 30
    o = []
    rs = np.random.RandomState(11)
    for i in range(9):
        per = rs.uniform(.9, 1.5)
        ph = rs.uniform(0, per)
        u = ((t + ph) % per) / per
        sx = fx + rs.uniform(-22, 22) + 26 * math.sin(u * 5 + i)
        sy = fy - 160 * u - 20
        r = 6 * (1 - u) + 1.4
        o.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r:.1f}" fill="#ffd070"/>')
    return "".join(o)



# ═══════════════════ рилс 55: ноутбук, таймер, сон, призыв ═══════════════════
T_MIN = wt("минут", 35.0)          # 35.98 — звонок
T_ZAS = wt("засыпает")             # 38.13
T_KOT = wt("кот", 40.0)            # 40.35


def laptop(t, n_lines=0.0, glow=0.0, caret=True):
    """Ноутбук на столе (3/4): база с клавишами, экран с белым документом; строки-штрихи растут (n_lines — дробное число строк)."""
    o = []
    o.append(blob([(488, 1150), (820, 1150), (836, 1168), (480, 1168)], "#2a1408", .28))
    scr = [(530, 1124, 1), (790, 1124, 1), (806, 846, 1), (520, 852, 1)]
    inner = ""
    inner += blob([(540, 1112), (780, 1112), (792, 870), (532, 874)], "#f6f2e8")
    inner += blob([(700, 1112), (780, 1112), (792, 870), (720, 872)], "#e6e0d0", .9)
    for i in range(9):
        y = 905 + i * 38
        u = clamp(n_lines - i)
        if u <= 0:
            continue
        L = (200 - 30 * (i % 3) - 18 * (i % 2)) * u
        inner += line([(556, y), (556 + L, y - 1)], 8, "#3b4a6a", taper=.04, wmin=.95, seed=8100 + i)
    if caret:
        i = int(n_lines)
        u = n_lines - i
        cx = 556 + (200 - 30 * (i % 3) - 18 * (i % 2)) * u + 8
        if int(t * 2.2) % 2 == 0:
            inner += f'<rect x="{cx:.1f}" y="{905 + i * 38 - 14:.1f}" width="4" height="28" fill="#1c1622"/>'
    o.append(shape(scr, "#333a4c", inner, w=5, seed=8001))
    if glow > 0:
        g = rad_grad([(0, "#fff6d8", .34 * glow), (1, "#fff6d8", 0)], 660, 1000, 360, 300)
        o.append(f'<rect x="260" y="640" width="800" height="700" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    base_top = [(512, 1122, 1), (796, 1122, 1), (824, 1154, 1), (486, 1154, 1)]
    keys = ""
    for r in range(3):
        for c in range(9):
            x0 = 524 + c * 30 - r * 6 + r * 4
            keys += blob([(x0 + r * 9, 1130 + r * 8), (x0 + 22 + r * 9, 1130 + r * 8), (x0 + 24 + r * 10, 1135 + r * 8), (x0 + 1 + r * 10, 1135 + r * 8)], "#5a6176")
    o.append(shape(base_top, "#aeb4c2", keys, w=4.2, seed=8002))
    o.append(shape([(486, 1154, 1), (824, 1154, 1), (820, 1166, 1), (490, 1166, 1)], "#7c8294", "", w=3.6, seed=8003))
    return "".join(o)


def timer(t, rem, ring=0.0, x=1018.0, y=DESK_BACK + 40, sc=.74):
    """Кухонный таймер без цифр: круглый корпус, белый циферблат с красным сектором (rem 0..1 — сколько осталось), два звонка."""
    sh = 0.0
    if ring > 0:
        sh = 9 * math.sin(t * 2 * math.pi * 17) * ring
    o = [blob(ellipse_pts(x + 8, y + 2, 86, 11, 14), "#2a1408", .3)]
    cy = y - 70
    inner = ""
    for k in range(5):                        # пять делений-засечек
        a = math.radians(-90 + 72 * k)
        inner += line([(x + 60 * math.cos(a), cy + 60 * math.sin(a)), (x + 46 * math.cos(a), cy + 46 * math.sin(a))], 4, INK, taper=.05, wmin=.95, seed=8200 + k)
    # красный сектор
    if rem > .01:
        pts = [(x, cy)] + [(x + 52 * math.cos(math.radians(-90 + 360 * rem * v)), cy + 52 * math.sin(math.radians(-90 + 360 * rem * v))) for v in np.linspace(0, 1, 16)]
        inner = blob(pts, "#e2574c") + inner
    face = shape(ellipse_pts(x, cy, 66, 66, 28), "#f7f2e6", inner, w=4.4, seed=8210)
    # стрелка
    ang = math.radians(-90 + 360 * (1 - rem) * 0 + 0)
    hand = line([(x, cy), (x + 48 * math.cos(math.radians(-90 + 360 * rem)), cy + 48 * math.sin(math.radians(-90 + 360 * rem)))], 6, INK, taper=.1, wmin=.9, seed=8211)
    body = shape(ellipse_pts(x, cy, 80, 80, 30), "#e2574c", blob(ellipse_pts(x + 14, cy + 12, 70, 70, 26), "#b83f3a", .7), w=5, seed=8212)
    bells = ""
    for sx in (-1, 1):
        bells += shape(ellipse_pts(x + sx * 46, cy - 82, 24, 18, 14, rot=sx * 28), "#e9c46a", "", w=3.8, seed=8220 + sx)
    bells += line([(x - 50, cy - 70), (x, cy - 100), (x + 50, cy - 70)], 5, INK, taper=.05, wmin=.9, seed=8225)
    feet = line([(x - 56, cy + 66), (x - 66, y)], 9, INK, taper=.05, wmin=.9, seed=8226) + line([(x + 56, cy + 66), (x + 66, y)], 9, INK, taper=.05, wmin=.9, seed=8227)
    waves = ""
    if ring > 0:
        for k in range(3):
            u = (t * 3.4 + k / 3) % 1.0
            r_ = 105 + 110 * u
            for sx in (-1, 1):
                a0 = math.radians(-35 if sx < 0 else -35)
                pts = [(x + sx * r_ * math.cos(a), cy - 30 + r_ * math.sin(a)) for a in np.linspace(-.9, .5, 8)]
                if u < .85:
                    waves += line(pts, 16 * (1 - u) + 4, "#f2b53a", taper=.5, wmin=.3, seed=8230 + k * 3 + (sx > 0))
    g = f'<g transform="rotate({sh:.2f} {x} {y})">{feet}{body}{face}{hand}{bells}</g>'
    return f'<g transform="translate({x} {y}) scale({sc}) translate({-x} {-y})">' + "".join(o) + g + waves + "</g>"


def world2(t, d, cat_st, cam, lap=None, tim=None, extra_front="", glow=0.0, flame_k=1.0, between="", chair_dx=0.0):
    set_ink(cam[2])
    w = [_ST["room"], _ST["lamp"]]
    w.append(room.chair(D_HIP[0] + chair_dx, D_HIP[1] + 4, 1, 2300))
    w.append(_ST["legs"])
    w.append(d.get("legs", ""))
    w.append(_ST["top"])
    w.append(_ST["light"])
    w.append(motes(t))
    w.append(laptop(t, *(lap or (0.0, glow))))
    w.append(cat_draw(t, cat_st))
    if tim is not None:
        w.append(timer(t, *tim))
    w.append(d["arm_f"])
    w.append(d["body"])
    w.append(d["arm_n"])
    w.append(between)
    w.append(extra_front)
    w.append(flame_glow(t, cat_st, flame_k))
    return f'<g transform="{lib.cam(*cam)}">{"".join(w)}</g>'


def typing_hands(t, rate=7.0, ph=0.0):
    c1 = .35 + .3 * (.5 + .5 * math.sin(t * rate + ph))
    c2 = .35 + .3 * (.5 + .5 * math.sin(t * rate + ph + 2.1))
    return {"n": fist(c1), "f": fist(c2)}


def typer(t, expr, lean=.1, hx=0.0, rate=7.0, head_ang=0.0, head_dy=0.0, dx=0.0):
    arms = {"n": ("ik", (520 + hx + 10 * math.sin(t * rate), DESK_FRONT - 22 + 4 * math.sin(t * rate * 1.3))),
            "f": ("ik", (560 + hx + 8 * math.sin(t * rate + 2), DESK_BACK + 6 + 4 * math.sin(t * rate + 1)))}
    return dima(lean, arms, typing_hands(t, rate), expr, head_ang=head_ang, torso_k=1.0, head_off=(0, head_dy), hip_off=(dx, 0), feet_dx=dx)


def calm_expr(t, smile=.7, look=(.7, .25), closed=0.0):
    return dict(lid=.55, look=look, closed=closed, brows=("det", "calm", 1.0) if False else "calm", mouth="smile", smile=smile, blush=.5)


def kitty(t, **kw):
    st = dict(look=(-.6, .1), turn=-.5, blink=0.0, ear=0, perk=0.2, tail=5 * osc(t, .45) + 2 * osc(t, 1.3), smile=1, tilt=0, flame_e=1.0)
    st.update(kw)
    return st


def sleep_bubble(t, x, y, u):
    """Пузырь сна без букв: облачко с полумесяцем и звёздами, три кружка к голове кота."""
    if u <= 0:
        return ""
    sc = ease_out(u) * (1 + .03 * math.sin(t * 2.3))
    yy = y + 6 * math.sin(t * 1.7)
    o = []
    for k, (dx, dy, r) in enumerate([(-70, 150, 11), (-50, 100, 17), (-20, 52, 24)]):
        o.append(shape(ellipse_pts(x + dx, yy + dy, r, r, 14), "#f4f1ea", "", w=3.6, seed=8300 + k))
    cl = ellipse_pts(x, yy, 130, 96, 24)
    inner = blob(ellipse_pts(0, 0, 1, 1, 6), "#f4f1ea", 0)
    moon = blob(ellipse_pts(x - 6, yy, 46, 46, 20), "#f2d070") + blob(ellipse_pts(x + 14, yy - 8, 40, 40, 20), "#f4f1ea")
    stars = ""
    for (sx_, sy_, r) in [(x + 62, yy - 30, 12), (x + 78, yy + 24, 8), (x - 74, yy - 36, 8)]:
        stars += blob([(sx_, sy_ - r), (sx_ + r * .3, sy_ - r * .3), (sx_ + r, sy_), (sx_ + r * .3, sy_ + r * .3), (sx_, sy_ + r), (sx_ - r * .3, sy_ + r * .3),
                       (sx_ - r, sy_), (sx_ - r * .3, sy_ - r * .3)], "#f2b53a")
    o.append(shape(cl, "#f4f1ea", moon + stars, w=4.6, seed=8310))
    return f'<g transform="translate({x} {yy}) scale({sc:.4f}) translate({-x} {-yy})">{"".join(o)}</g>'


def frame15(t):
    """s15 34.9–37.6: таймер звенит на «минут» (35.98), Дима не замечает, печатает с улыбкой."""
    ring = smooth(T_MIN - .02, T_MIN + .05, t) * 1.0
    rem = clamp(1 - (t - 34.2) / (T_MIN - 34.2)) * .12 + .0 if t < T_MIN else 0.0
    rem = max(0.0, .14 * (1 - (t - 34.7) / (T_MIN - 34.7))) if t < T_MIN else 0.0
    n = 1.4 + 1.9 * (t - 34.7) / 2.9
    expr = calm_expr(t, smile=.55 + .35 * smooth(T_MIN, T_MIN + .8, t))
    d = typer(t, expr, rate=7.5, head_dy=2 * math.sin(t * 3))
    st = kitty(t, look=(-.5, .1), ear=7 * bump(t, T_MIN, .4), perk=.5 * smooth(T_MIN - .02, T_MIN + .1, t) * (1 - smooth(T_MIN + .4, T_MIN + .9, t)))
    u = clamp((t - 34.7) / 2.9)
    shake = 5 * math.exp(-(t - T_MIN) * 7) * math.sin((t - T_MIN) * 60) if t >= T_MIN else 0.0
    cam = (640 + 20 * (u - .5) + shake, 1265 - 14 * u + .6 * shake, 1.24 + .08 * ease_io(u) + .02 * bump(t, T_MIN, .25), -.9 + 1.5 * u)
    return world2(t, d, st, cam, lap=(n, .3), tim=(rem, ring), flame_k=1.0)


def frame16(t):
    """s16 37.6–39.4: кот сворачивается, глаза-дуги на «засыпает» (38.13), огонёк тлеет, пузырь сна."""
    sl = ease_io(clamp((t - 37.75) / 1.05))
    blink = smooth(T_ZAS - .22, T_ZAS + .05, t)
    expr = calm_expr(t, smile=.9)
    d = typer(t, expr, rate=7.0, head_dy=2 * math.sin(t * 3), head_ang=.02)
    st = kitty(t, look=(-.7 + .3 * sl, .2), blink=blink, sleep=sl, ear=-6 * sl, perk=0.0, tail=2 * osc(t, .3) * (1 - sl), flame_e=1.0 - .6 * sl,
               smile=0, turn=-.5 + .4 * sl)
    u = clamp((t - 37.4) / 2.2)
    cam = (650 + 50 * ease_io(u), 1190 - 40 * ease_io(u), 1.3 + .3 * ease_io(u), -.7 + .9 * u)
    bub = sleep_bubble(t, 900, 790, clamp((t - 38.65) / .5))
    return world2(t, d, st, cam, lap=(3.6 + .5 * (t - 37.4), .3), tim=(0.0, 0.0), between=bub, flame_k=1.0 - .65 * sl)


def frame17(t):
    """s17 39.4–41.2: кот крупно смотрит в камеру, над ним рукописное «кот» на 40.35; Дима печатает на фоне."""
    wk = smooth(39.45, 39.85, t)                        # проснулся
    expr = calm_expr(t, smile=.9)
    d = typer(t, expr, rate=7.0, head_dy=2 * math.sin(t * 3))
    st = kitty(t, look=(0.0, 0.05), turn=0.0, blink=(1 - wk) * 1.0 + Cat_blink(t, [(40.9, .06, 0.0)]) * wk, sleep=(1 - ease_io(wk)) * .9, flame_e=1.6,
               smile=1, ear=6 * bump(t, 39.7, .4), perk=.3 * wk)
    u = clamp((t - 39.2) / 2.2)
    cam = (870 - 10 * u, 985 + 4 * u, 2.4 + .3 * ease_io(u), .6 - .9 * u)
    spark = sparks(t)
    return svg_wrap(world2(t, d, st, cam, lap=(4.2, .3), tim=(0.0, 0.0), between=spark, flame_k=1.6 + .3 * math.sin(t * 9)) + write_kot55(t))


def svg_wrap(x):
    return x


def write_kot55(t):
    if t < T_KOT - .02:
        return ""
    H_, Wd, gap = 200, 160, 36
    total = 3 * Wd + 2 * gap
    x0, y0 = 540 - total / 2, 260
    o = []
    tm = [(T_KOT, T_KOT + .22), (T_KOT + .24, T_KOT + .46), (T_KOT + .48, T_KOT + .70)]
    for li, ((ch, strokes, _), (a, b)) in enumerate(zip(_letter_paths(), tm)):
        lx = x0 + li * (Wd + gap)
        for si, st_ in enumerate(strokes):
            ta = a + (b - a) * si / len(strokes)
            tb = a + (b - a) * (si + 1) / len(strokes)
            u = clamp((t - ta) / (tb - ta))
            if u <= 0:
                continue
            P = lib.sample([(lx + px * Wd, y0 + py * H_) for px, py in st_], False, 4.0)
            seg = [tuple(p) for p in P[:max(2, int(len(P) * u))]]
            if len(seg) < 2:
                continue
            o.append(line(seg, 40, INK, taper=.04, wmin=.96, seed=7000 + li * 5 + si))
            o.append(line(seg, 26, "#fff3cf", taper=.04, wmin=.96, seed=7050 + li * 5 + si))
    u = clamp((t - (T_KOT + .72)) / .28)
    if u > 0:
        ux0, ux1 = x0 - 10, x0 + total + 10
        pts = [(ux0 + (ux1 - ux0) * v, y0 + H_ + 46 - 14 * math.sin(v * 3.1)) for v in np.linspace(0, u, 8)]
        o.append(line(pts, 26, INK, taper=.3, wmin=.6, seed=7100))
        o.append(line(pts, 15, "#ffb050", taper=.3, wmin=.6, seed=7101))
    e = t - T_KOT
    sc = 1 + .06 * math.exp(-e * 9) * math.sin(min(e * 14, math.pi)) if e >= 0 else 1
    return f'<g transform="translate({x0 + total / 2:.1f} {y0 + H_ / 2:.1f}) scale({sc:.4f}) translate({-(x0 + total / 2):.1f} {-(y0 + H_ / 2):.1f})">{"".join(o)}</g>'


def frame18(t):
    """s18 41.2–42.9: Дима, кот и ноутбук с готовой строкой, Дима оглядывается на зрителя; дрейф назад, тепло."""
    turn = smooth(41.55, 42.1, t)
    expr = calm_expr(t, smile=.55 + .35 * turn, look=(.7 - .7 * turn, .25 * (1 - turn)))
    typing = 1 - smooth(41.45, 41.8, t)
    rate = 7.0
    d = typer(t, expr, rate=rate * typing + .01, head_ang=-.07 * turn, head_dy=2 * math.sin(t * 3) - 6 * turn, lean=.1 - .04 * turn)
    st = kitty(t, look=(-.2, .1), turn=-.2, flame_e=1.2, ear=5 * bump(t, 41.4, .4), tail=6 * osc(t, .5))
    u = clamp((t - 41.0) / 2.1)
    cam = (640 - 40 * u, 1180 + 20 * u, 1.55 - .3 * ease_io(u), .5 - .9 * u)
    return world2(t, d, st, cam, lap=(5.0, .5, False), tim=(0.0, 0.0), between=sparks(t), flame_k=1.2)


def frame(sid, t):
    if not _ST:
        static_all()
    lib.dyn_begin()
    if sid in ("s07", "s08", "s09"):
        import cafe55
        return cafe55.frame(sid, t)
    body = {"s15": frame15, "s16": frame16, "s17": frame17, "s18": frame18}[sid](t)
    return svg(f'<rect width="1920" height="1920" fill="#2a1f2a"/>{body}')
