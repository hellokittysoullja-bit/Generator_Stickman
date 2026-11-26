"""Рилс 132 «Срочные новости», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json (общая дорожка voice_merge.py: кот-диктор Даниил, Дима male2).
Студия: синий фон с софитами, большой экран за диктором, стол с логотипом «НОВОСТИ», бегущая строка внизу. Кот-диктор в
пиджаке, рубашке и красном галстуке (costume.py, внутри рисунка кота) во всех планах. Имя героя не звучит и не пишется.
NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402
import room as RM  # noqa: E402
import costume as CO  # noqa: E402

CO.install(CT)
HIT = stress(1, .4)
ST_BG, ST_BG2, DESK_C, DESK_SH = "#1f3a6e", "#2a4e8f", "#e8ecf4", "#b9c3d6"
TICKER = "СРОЧНО  •  ОН ОТКРЫЛ ПИСЬМО  •  СПУСТЯ 14 ДНЕЙ  •  "
SCR = (540.0, 760.0, 820.0, 500.0)      # экран студии: центр, ширина, высота
DY = 1290.0                             # верх стола диктора


def screen(inner, t, k=1.0, glow=0.0, pos=None):
    """Большой экран студии; inner — картинка в координатах экрана (центр 0,0; 820×500). pos — (x, y) центра вместо SCR."""
    cx, cy, w, h = SCR
    if pos:
        cx, cy = pos
    o = [shape(lib.rrect(-w / 2 - 22, -h / 2 - 22, w / 2 + 22, h / 2 + 22, 20), "#11151f", "", w=5, seed=14100)]
    c = lib.clip_rect(-w / 2, -h / 2, w, h, 10)
    o.append(f'<g clip-path="url(#{c})"><rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" fill="#f1ede2"/>{inner}</g>')
    if glow > 0:
        o.append(PR.glow(0, 0, 500, .3 * glow, "#ffffff"))
    return tf("".join(o), cx, cy, k)


def lights(t, alarm=0.0):
    o = []
    for j, x in enumerate((90, 990)):
        on = .5 + .5 * math.sin(t * 14 + j * math.pi) if alarm > 0 else 0
        col = "#ff3b30" if j == 0 else "#2f8fe0"
        o.append(shape(lib.rrect(x - 50, 260, x + 50, 330, 20), col, "", w=4, seed=14110 + j))
        if alarm > 0:
            o.append(PR.glow(x, 300, 320, .55 * on * alarm, col))
    return "".join(o)


def studio(t, alarm=0.0, scr_inner="", scr_glow=0.0, scr_pos=None, scr_k=1.0):
    o = [rect(-1400, -1400, 2600, 3400, ST_BG)]
    for j in range(-6, 16):
        o.append(rect(j * 110, -1400, j * 110 + 40, 3400, ST_BG2, .5))
    o.append(PR.glow(540, 700, 800, .25, "#9fc2ff"))
    o.append(lights(t, alarm))
    o.append(screen(scr_inner or logo_inner(t), t, k=scr_k, glow=scr_glow, pos=scr_pos))
    return o


def siren_inner(t):
    """Экран-тревога без надписи (под крупной надписью хука и кодовым словом текст экрана не нужен): красный фон и мигалка."""
    on = .5 + .5 * math.sin(t * 14)
    o = rect(-410, -250, 410, 250, "#d8352a") + rect(-410, 60, 410, 250, "#b02a20")
    o += PR.glow(0, 20, 260, .5 * on, "#fff1b0")
    o += shape([(-90, 90, 1), (-70, -40), (0, -90), (70, -40), (90, 90, 1)], "#ff6a4a", blob(ellipse_pts(-30, -10, 22, 40, 12), "#ffd0c0", .8), w=5, seed=14150)
    o += shape(lib.rrect(-130, 90, 130, 140, 12), "#11151f", "", w=4, seed=14151)
    for j, a in enumerate((-150, -110, -70, -30)):
        r = math.radians(a)
        o += line([(150 * math.cos(r) * .9, -20 + 150 * math.sin(r) * .9), (220 * math.cos(r), -20 + 220 * math.sin(r))], 10, "#ffffff", taper=0, wmin=1, seed=14152 + j, op=on)
        o += line([(-150 * math.cos(r) * .9, -20 + 150 * math.sin(r) * .9), (-220 * math.cos(r), -20 + 220 * math.sin(r))], 10, "#ffffff", taper=0, wmin=1, seed=14160 + j, op=on)
    return o


def logo_inner(t):
    return (rect(-410, -250, 410, 250, "#d8352a") + rect(-410, 60, 410, 250, "#b02a20")
            + text("НОВОСТИ", 0, 30, 120, fill="#ffffff", stroke="#7a1a10", sw=8))


def anchor_desk(t, x=540.0):
    o = shape(lib.rect_pts(-420, 0, 420, 60), DESK_C, "", w=5, seed=14120)
    o += shape([(-400, 60, 1), (400, 60, 1), (360, 520, 1), (-360, 520, 1)], "#c9d1e2", blob([(150, 60), (400, 60), (360, 520), (190, 520)], DESK_SH, .8),
               w=5, seed=14121)
    o += shape(lib.rrect(-230, 150, 230, 290, 22), "#d8352a", text("НОВОСТИ", 0, 248, 74, fill="#ffffff", stroke="#7a1a10", sw=6), w=4, seed=14122)
    return tf(o, x, DY)


def papers(x, y, k=1.0, rot=0.0, tap=0.0):
    o = shape(lib.rect_pts(-110, -150, 110, 0), "#fbf8f1", "".join(line([(-80, -120 + 26 * j), (80, -120 + 26 * j)], 2, "#c9d7ea", taper=0, wmin=1,
                                                                       seed=14130 + j) for j in range(5)), w=3.4, seed=14131)
    return tf(o, x, y - 20 * tap, k, rot)


def ticker(t):
    """Бегущая строка внизу кадра (экранная, поверх камеры)."""
    if NOCAM:
        return ""
    off = (t * 260) % 1400
    s = (f'<rect x="0" y="1590" width="1080" height="96" fill="#d8352a"/><rect x="0" y="1590" width="210" height="96" fill="#11151f"/>'
         + f'<g clip-path="url(#tk)"><text x="{230 - off:.1f}" y="1656" font-family="IDB" font-size="50" fill="#ffffff">{TICKER * 3}</text></g>'
         + text("СРОЧНО", 105, 1656, 46, fill="#ffffff", stroke="#11151f", sw=0.01))
    return '<defs><clipPath id="tk"><rect x="210" y="1590" width="870" height="96"/></clipPath></defs>' + s


def anchor(t, st=None, paw=0.0, x=540.0, y=None, k=1.25):
    st = dict(dict(look=(0, 0), smile=.6, tail=6 * math.sin(t * 1.7), paw=paw, paw_dx=-60.0), **(st or {}))
    return CT.draw(x, DY + 40 if y is None else y, k, st, t)


def studio_shot(t, st=None, alarm=0.0, scr_inner="", paw=0.0, extra_front="", pip=False):
    """pip=True — картинка на экране главная: экран слева выше, диктор справа и не закрывает её."""
    if pip:
        o = studio(t, alarm, scr_inner, scr_pos=(410, 700), scr_k=.8)
        o.append(anchor(t, dict(dict(look=(-.7, -.5), turn=-.3), **(st or {})), paw, x=800, k=1.1))
        o.append(anchor_desk(t, x=720))
        o.append(extra_front)
        return o
    o = studio(t, alarm, scr_inner)
    o.append(anchor(t, st, paw))
    o.append(papers(330, DY + 6, .9, -4))
    o.append(anchor_desk(t))
    o.append(extra_front)
    return o


def sview(body, t, cx, cy, s, rot=0.0):
    return view(body, cx, cy, s, rot, t=t, extra=ticker(t))


# ═════════════ лица-предметы ═════════════
def face(cx, cy, s=1.0, mood="calm", look=(0.0, 0.0), sd=0, rub=0.0):
    o = []
    for sx in (-1, 1):
        ex, ey = cx + sx * 30 * s, cy
        ry = 24 if mood == "shock" else 20
        o.append(shape(ellipse_pts(ex, ey, 18 * s, ry * s, 14), "#ffffff", "", w=3, seed=sd + 1 + sx))
        o.append(f'<circle cx="{ex + look[0] * 6 * s:.1f}" cy="{ey + 3 * s + look[1] * 6 * s:.1f}" r="{(5 if mood == "shock" else 8) * s:.1f}" fill="#111"/>')
        by = ey - 32 * s - (8 * s if mood == "shock" else 0)
        tl = 8 if mood == "doubt" else 0
        o.append(line([(ex - 16 * s, by + sx * tl * s * .5), (ex + 16 * s, by - sx * tl * s * .5)], 4.6 * s, seed=sd + 5 + sx))
    my = cy + 44 * s
    if mood == "shock":
        o.append(shape(ellipse_pts(cx, my, 16 * s, 22 * s, 14), "#5a2b33", "", w=3, seed=sd + 9))
    elif mood == "doubt":
        o.append(line([(cx - 22 * s, my + 4 * s), (cx, my - 4 * s), (cx + 22 * s, my + 6 * s)], 4.4 * s, seed=sd + 10))
    else:
        o.append(line([(cx - 22 * s, my), (cx, my + 8 * s), (cx + 22 * s, my)], 4.4 * s, seed=sd + 11))
    return "".join(o)


def mug_char(x, y, s, t, col="#e2453a", mood="shock", look=(0, 0), shake_=0.0, tilt=0.0, sd=0):
    o = [shape(lib.rrect(-110, -260, 110, 0, 26), col, blob(lib.rect_pts(40, -260, 110, 0), "#000000", .12), w=5, seed=14200 + sd)]
    o.append(shape(ellipse_pts(0, -258, 110, 22, 20), lib.mul(col, (.8, .8, .8)), blob(ellipse_pts(0, -254, 90, 14, 16), "#6b4a32"), w=4, seed=14201 + sd))
    o.append(line([(110, -200), (170, -190), (176, -100), (110, -80)], 16, col, taper=0, wmin=1, seed=14202 + sd))
    o.append(line([(110, -200), (170, -190), (176, -100), (110, -80)], 4, taper=0, wmin=1, seed=14203 + sd, op=.6))
    o.append(face(0, -150, 1.2, mood, look, sd=14210 + sd))
    rot = tilt + shake_ * 8 * math.sin(t * 22 + sd)
    return tf("".join(o), x, y, s, rot)


def sink(t, mugs):
    o = [rect(-1400, -1400, 2600, 3400, "#dfe8ee")]
    for i in range(-8, 18):
        for j in range(10):
            o.append(line([(i * 110, 500 + 110 * j), (i * 110 + 110, 500 + 110 * j)], 2, "#c4d2dc", taper=0, wmin=1, seed=14300 + j, op=.7))
            o.append(line([(i * 110, 500 + 110 * j), (i * 110, 610 + 110 * j)], 2, "#c4d2dc", taper=0, wmin=1, seed=14320 + i, op=.7))
    o.append(shape(lib.rect_pts(-200, 1380, 1300, 1460), "#c9b08a", "", w=5, seed=14340))
    o.append(shape([(120, 1390, 1), (960, 1390, 1), (900, 1700, 1), (180, 1700, 1)], "#b9c3d0", blob([(700, 1390), (960, 1390), (900, 1700), (720, 1700)], "#9aa6b6", .7),
                   w=5, seed=14341))
    o.append(line([(820, 1390), (820, 1180), (700, 1160)], 22, "#9aa6b6", taper=0, wmin=1, seed=14342))
    o.append(line([(820, 1390), (820, 1180), (700, 1160)], 5, taper=0, wmin=1, seed=14343, op=.5))
    o.extend(mugs)
    o.append(shape([(150, 1520, 1), (930, 1520, 1), (900, 1700, 1), (180, 1700, 1)], "#b9c3d0", "", w=5, seed=14344))
    return o


def street(t):
    o = [rect(-1400, -1400, 2600, 3400, "#bfe0f5")]
    for j, (x0, w, h, col) in enumerate(((-200, 420, 1100, "#e8c9a0"), (260, 360, 1300, "#d9a88a"), (660, 440, 1000, "#c9d6b8"), (1080, 400, 1200, "#e8c9a0"))):
        o.append(shape(lib.rect_pts(x0, RFL - h, x0 + w, RFL), col, "", w=5, seed=14400 + j))
        for r in range(int(h // 220)):
            for c in range(int(w // 140)):
                wx, wy = x0 + 40 + c * 140, RFL - h + 60 + r * 220
                o.append(shape(lib.rect_pts(wx, wy, wx + 80, wy + 120), "#9fc7e8", "", w=3, seed=14410 + j * 20 + r * 3 + c))
    o.append(rect(-1400, RFL, 2600, RFL + 1400, "#b8b2a6"))
    o.append(line([(-1400, RFL), (2600, RFL)], 5, seed=14450))
    return o


def mic(x, y, k=1.0, rot=0.0):
    o = line([(0, 0), (0, 190)], 22, "#2a2c30", taper=0, wmin=1, seed=14500)
    o += shape(ellipse_pts(0, -26, 44, 50, 18), "#5a5f6e", "".join(line([(-40, -26 + 14 * j), (40, -26 + 14 * j)], 2, "#3a3d46", taper=0, wmin=1,
                                                                   seed=14501 + j) for j in range(-3, 4)), w=4, seed=14502)
    o += shape(lib.rect_pts(-36, 36, 36, 96), "#d8352a", "", w=3.4, seed=14503)
    return tf(o, x, y, k, rot)


def lower_third(txt, u, y=1230):     # над полосой субтитров (центр 1430)
    if u <= .02 or NOCAM:
        return ""
    w = big_w(txt, 64) * 1.15 + 90
    x = -w + (40 + w) * ease_out(clamp(u))
    return (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="100" fill="#ffffff" stroke="#11151f" stroke-width="6"/>'
            + f'<rect x="{x:.1f}" y="{y}" width="24" height="100" fill="#d8352a"/>'
            + plain(txt, x + 54, y + 72, 64, fill="#11151f"))


def big_w(txt, size):
    import big_title
    return big_title.text_w(txt, size) * .92


def interview(t, talk=0.0, expr="calm82"):
    """Улица: Дима крупно по пояс, микрофон у подбородка (не закрывает лицо)."""
    o = street(t)
    k = .9
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    f0 = people.dima82(430, hip, k, expr, "d82_rest", t=t, feet="stand")
    mx, my = f0["mouth"]
    f = people.dima82(430, hip, k, expr, "d82_rest", t=t, feet="stand", head_add=.03 * math.sin(t * 7) * talk,
                      arms={"n": ("ik", (mx + 50, my + 190), -1)})
    wx, wy = f["wrist"]["n"]
    o.append(mic(wx - 56 * .9, wy - 106 * .9, .9, -28))     # хват ручки — в кисти, линза у подбородка
    o.append(f["svg"])
    return o, f


# ═════════════ планы ═════════════
def frame_s01(t):
    """ХУК: студия, мигалки, кот-диктор в пиджаке и галстуке бьёт лапой по столу, на экране «НОВОСТИ»."""
    o = studio_shot(t, dict(look=(0, 0), smile=0.0, perk=1.0), alarm=1.0, paw=.4 + .4 * bump(t, HIT, .05, .3), scr_inner=siren_inner(t))
    dx, dy = shake(t, HIT, 10)
    return lib.svg(hook_wrap(f'<g transform="{lib.cam(540 + dx, 1180 + dy, 1.45, 0)}">{"".join(o)}</g>', t, HIT) + ticker(t) + over(t)) \
        if not NOCAM else hook_view("".join(o), t, HIT, 540, 1180, 1.45)


def envelope_inner(t, u):
    o = shape(lib.rect_pts(-220, -130, 220, 150), "#fbf3df", "", w=5, seed=14600)
    if u > .02:
        o += shape(lib.rect_pts(-170, -130 - 200 * u, 170, 40), "#ffffff", "".join(line([(-130, -90 - 200 * u + 34 * j), (130, -90 - 200 * u + 34 * j)], 3,
                                                                                         "#9aa6b6", taper=0, wmin=1, seed=14601 + j) for j in range(4)),
                   w=3.4, seed=14605)
    fl = 1 - 2 * ease_out(clamp(u))
    o += f'<g transform="translate(0 -130) scale(1 {fl:.3f})">' + shape([(-220, 0, 1), (0, 150, 1), (220, 0, 1)], "#f3e3c0", "", w=4, seed=14606) + "</g>"
    o += line([(-220, 150), (0, 0), (220, 150)], 3, seed=14607, op=.6)
    return o


def frame_s02(t):
    """«он открыл письмо»: экран за котом крупно — конверт распахивается, письмо выезжает."""
    a, b = T0("s02"), T1("s02")
    o = studio_shot(t, dict(smile=.4), alarm=.5, scr_inner=envelope_inner(t, ramp(t, W(3), .4)), pip=True)
    u = ease_io(ramp(t, a, b - a))
    return sview("".join(o), t, 560, 900, 1.2 + .06 * u)


def cal14_inner(t, u):
    o = ""
    for j in range(14):
        cx_, cy_ = -300 + (j % 7) * 100, -40 + (j // 7) * 120
        o += shape(lib.rect_pts(cx_ - 42, cy_ - 50, cx_ + 42, cy_ + 50), "#ffffff", "", w=3, seed=14620 + j)
        v = clamp(u * 14 - j)
        if v > 0:
            o += line([(cx_ - 30, cy_ - 36), (cx_ - 30 + 60 * v, cy_ - 36 + 72 * v)], 7, "#d8352a", taper=0, wmin=1, seed=14640 + j)
    o += text("14 дней", 0, -150, 84, fill="#d8352a", stroke="#ffffff", sw=8) if u > .9 else ""
    return o


def frame_s03(t):
    """«спустя четырнадцать дней»: на экране календарь, клетки перечёркиваются одна за другой, «14 дней»."""
    a, b = T0("s03"), T1("s03")
    o = studio_shot(t, dict(smile=0.0, perk=1.0), scr_inner=cal14_inner(t, ramp(t, a, W(7) - a)), pip=True)
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(7), 8)
    return sview("".join(o), t, 560 + dx, 900 + dy, 1.2 + .06 * u)


def inbox(t, dust=0.0, web=0.0, label=0.0):
    """Входящие во весь экран: строки писем, одно — в пыли и паутине."""
    o = [rect(-1400, -1400, 2600, 3400, "#e9eef4")]
    o.append(shape(lib.rrect(60, 360, 1020, 1640, 30), "#ffffff", "", w=5, seed=14700))
    o.append(rect(60, 360, 1020, 470, "#2f8fe0"))
    o.append(plain("Входящие", 120, 438, 58, fill="#ffffff"))
    for j in range(6):
        y = 520 + 180 * j
        hot = j == 3
        o.append(shape(lib.rrect(100, y, 980, y + 150, 16), "#f6efdf" if hot else "#f4f6f9", "", w=3, seed=14710 + j))
        o.append(shape(ellipse_pts(170, y + 75, 40, 40, 14), ["#9fc2e8", "#ffd27a", "#d6c7f0", "#c8553d", "#9fe0a4", "#f0b6c0"][j], "", w=3, seed=14720 + j))
        o.append(line([(240, y + 55), (640 if hot else 560 + 40 * (j % 3), y + 55)], 10, "#3a3d46", taper=0, wmin=1, seed=14730 + j, op=.8))
        o.append(line([(240, y + 100), (860, y + 100)], 6, "#aab3c0", taper=0, wmin=1, seed=14740 + j))
        if hot:
            o.append(shape(ellipse_pts(930, y + 50, 16, 16, 10), "#d8352a", "", w=2, seed=14750))
            if dust > 0:
                o.append(f'<rect x="100" y="{y}" width="880" height="150" rx="16" fill="#8a7a60" opacity="{.35 * dust:.3f}"/>')
                for i in range(70):
                    rx, ry = (i * 97) % 860, (i * 53) % 140
                    o.append(blob(ellipse_pts(110 + rx, y + 6 + ry, 10, 7, 8), "#7a6a50", .8 * dust))
            if web > 0:
                o.append(PR.cobweb(975, y + 5, 1.6 * web, ang=90, seed=3))
                o.append(PR.cobweb(105, y + 5, 1.2 * web, ang=0, seed=5))
    if label > .02:
        o.append(f'<g transform="translate(560 1240) rotate(-4) scale({lib.back_out(clamp(label), 2.0):.3f})">'
                 + shape(lib.rrect(-260, -70, 260, 70, 20), "#FFD23F", "", w=5, seed=14760) + text("2 недели", 0, 26, 86, fill="#111", stroke="#111", sw=.01) + "</g>")
    return o


def frame_s04(t):
    """«Письмо пролежало во входящих»: список входящих, одно письмо в пыли."""
    a, b = T0("s04"), T1("s04")
    o = inbox(t, dust=ramp(t, a, b - a))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 1000, 1.0 + .12 * u, 0, t=t, extra=ticker(t))


def frame_s05(t):
    """«две недели»: пыль гуще, паутина растёт на письме, плашка «2 недели»."""
    a, b = T0("s05"), T1("s05")
    o = inbox(t, dust=1.0, web=ease_out(ramp(t, a, .5)), label=ramp(t, W(12) + .05, .25))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(13), 6)
    return view("".join(o), 540 + dx, 1130 + dy, 1.15 + .06 * u, 0, t=t, extra=ticker(t))


def archive(o):
    """Плёнка архива: сепия-вуаль и рамка."""
    o.append(rect(-1400, -1400, 2600, 3400, "#8a6a40", .12))
    return o


def frame_s06(t):
    """«Всё это время»: архив — Дима за столом захлопывает ноутбук с письмом."""
    a, b = T0("s06"), T1("s06")
    o = desk_room(t)
    shut = ease_in(ramp(t, W(15) - .25, .25))
    o.append(PR.laptop(640, DESK_Y - 8, 1.0, open_=1.0 - .95 * shut, screen="lines", lines=.3, t=t, seed=1))
    o.append(dima_desk(t, dict(people.EXPR["dima"]["guilty"], look=(.8, .1)), lean=.1, arms={"n": ("ik", (660, DESK_Y - 160 + 140 * shut), 1)})["svg"])
    o = archive(o)
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(15), 8)
    return view("".join(o), 560 + dx, 860 + dy, 1.4 + .05 * u, 0, t=t, extra=ticker(t))


def ease_in(u):
    return u * u


def frame_s07(t):
    """«он говорил: потом»: Дима на диване отмахивается, пузырь «потом»."""
    a, b = T0("s07"), T1("s07")
    o = [plain_room(t)]
    sf = RM.sofa(540, RFL, 1.0)
    o.append(sf["back"])
    x, k = 420.0, .7
    feet = {"n": ((x + 230 * k, RFL - 10), 0.0), "f": ((x + 180 * k, RFL - 16), 0.0)}
    wave = math.sin(t * 9)
    f = people.dima82(x, RFL - 330, k, "calm82", "sit_desk", t=t, feet=feet, lean_add=-.12,
                      arms={"n": ("ik", (x + 200 + 30 * wave, RFL - 640), -1)})
    o.append(f["svg"])
    o.append(sf["arm_r"])
    hx, hy = f["head"]
    o.append(PR.speech_bubble(hx + 240, hy - 190, 360, 170, pop(t, W(19) - .1, .25), seed=7, tail=(-130, 80)))
    if pop(t, W(19) - .1, .25) > .8:
        o.append(plain("потом", hx + 240, hy - 172, 70, fill="#1d2448", anchor="middle"))
    o = archive(o)
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(19), 6)
    return view("".join(o), 580 + dx, 1100 + dy, 1.2 + .06 * u, 0, t=t, extra=ticker(t))


def mugs_row(t, mood, shake_=0.0, rub=0.0, look=(0, -.3)):
    cols = ["#e2453a", "#2f8fe0", "#f3c84a"]
    out = []
    for j, (x, s, tl) in enumerate(((300, .95, -8), (560, 1.05, 3), (800, .9, 9))):
        out.append(mug_char(x, 1500, s, t, cols[j], mood if j != 2 or mood != "doubt" else "shock", look, shake_, tl + (6 * math.sin(t * 10) if mood == "doubt" else 0), sd=j * 7))
    return out


def frame_s08(t):
    """«Очевидцы в шоке»: кружки с лицами в раковине ахают."""
    a, b = T0("s08"), T1("s08")
    o = sink(t, mugs_row(t, "shock" if t > W(22) - .1 else "calm", shake_=bump(t, W(22), .05, .5)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(22), 10)
    return view("".join(o), 560 + dx, 1330 + dy, 1.35 + .06 * u, 0, t=t, extra=ticker(t))


def frame_s09(t):
    """«Кружки в раковине»: кружки крупно, рты открыты."""
    a, b = T0("s09"), T1("s09")
    o = sink(t, mugs_row(t, "shock", look=(.2, -.5)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1330, 1.6 + .06 * u, 0, t=t, extra=ticker(t))


def frame_s10(t):
    """«до сих пор не верят»: кружки качают головами, недоверчивые брови."""
    a, b = T0("s10"), T1("s10")
    o = sink(t, mugs_row(t, "doubt", look=(.6 * math.sin(t * 8), -.2)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(29), 6)
    return view("".join(o), 560 + dx, 1330 + dy, 1.45 + .06 * u, 0, t=t, extra=ticker(t))


def street_inner(t):
    o = rect(-410, -250, 410, 250, "#bfe0f5")
    for j, (x0, w, h, col) in enumerate(((-420, 260, 330, "#e8c9a0"), (-150, 240, 420, "#d9a88a"), (110, 300, 300, "#c9d6b8"))):
        o += shape(lib.rect_pts(x0, 250 - h, x0 + w, 250), col, "", w=4, seed=14800 + j)
    o += shape(ellipse_pts(0, 250, 90, 160, 20), "#2a2d36", "", w=3, seed=14810) + shape(ellipse_pts(0, 70, 56, 64, 16), "#f0c8a0", "", w=3, seed=14811)
    return o


def frame_s11(t):
    """«Как это произошло»: кот-диктор поворачивается к экрану, на экране — улица и силуэт героя."""
    a, b = T0("s11"), T1("s11")
    o = studio_shot(t, dict(smile=.6), scr_inner=street_inner(t), paw=.7, pip=True)
    u = ease_io(ramp(t, a, b - a))
    return sview("".join(o), t, 560, 930, 1.15 + .1 * u)


def frame_s12(t):
    """«рассказывает наш герой»: улица, Дима с микрофоном у подбородка, плашка «НАШ ГЕРОЙ»."""
    a, b = T0("s12"), T1("s12")
    o, f = interview(t)
    hx, hy = f["head"]
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 520, hy + 420, 1.25 + .05 * u, 0, t=t, extra=lower_third("НАШ ГЕРОЙ", ramp(t, W(35) - .1, .3)) + ticker(t))


def frame_s13(t):
    """Дима: «Я просто сел на две минуты»: Дима говорит в микрофон, врезка — стол, ноутбук и таймер 2:00."""
    a, b = T0("s13"), T1("s13")
    talk = abs(math.sin(t * 11)) if t < WE(42) else 0
    o, f = interview(t, talk, dict(people.EXPR["dima"]["calm82"], mouth="talk", open=.2 + .4 * talk, look=(.7, -.1)))
    hx, hy = f["head"]
    pop_u = pop(t, W(39), .25)
    if pop_u > .02:
        ins = shape(lib.rrect(-200, -170, 200, 170, 20), "#fbf8f1", "", w=5, seed=14900)
        ins += shape(lib.rect_pts(-160, 60, 160, 80), "#a8774a", "", w=3, seed=14901)
        ins += shape(lib.rrect(-90, -40, 90, 60, 8), "#2a2d36", blob(lib.rect_pts(-78, -30, 78, 50), "#9fc7ff"), w=3, seed=14902)
        ins += shape(ellipse_pts(110, -90, 64, 64, 24), "#ffffff", text("2:00", 0, 14, 42, fill="#1d2448", stroke="#ffffff", sw=3)[:0], w=4, seed=14903)
        ins += plain("2:00", 110, -76, 44, fill="#1d2448", anchor="middle")
        o.append(f'<g transform="translate({hx + 330:.1f} {hy - 30:.1f}) rotate(4) scale({pop_u:.3f})">{ins}</g>')
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 600, hy + 420, 1.2 + .05 * u, 0, t=t, extra=lower_third("НАШ ГЕРОЙ", 1.0) + ticker(t))


def mail_screen(t, u_line=0.0, sent=0.0):
    """Ноутбук крупно: открытое письмо, пишется одна строка; sent — самолётик улетает и «Отправлено»."""
    o = [desk_room(t)[0]]
    o.append(PR.laptop(540, DESK_Y + 120, 2.0, screen="lines", lines=0.0, t=t, seed=2))
    sx0, sy0 = 540, DESK_Y - 300
    o.append(shape(lib.rrect(sx0 - 300, sy0 - 190, sx0 + 300, sy0 + 190, 12), "#ffffff", "", w=4, seed=15000))
    o.append(rect(sx0 - 300, sy0 - 190, sx0 + 300, sy0 - 120, "#2f8fe0"))
    for j in range(3):
        o.append(line([(sx0 - 260, sy0 - 80 + 36 * j), (sx0 + 200 - 60 * j, sy0 - 80 + 36 * j)], 6, "#aab3c0", taper=0, wmin=1, seed=15001 + j))
    if u_line > 0:
        o.append(line([(sx0 - 260, sy0 + 60), (sx0 - 260 + 440 * clamp(u_line), sy0 + 60)], 10, "#1d2448", taper=0, wmin=1, seed=15010))
    if sent > .02:
        px, py = sx0 + 200 + 400 * ease_in(sent), sy0 + 120 - 520 * ease_in(sent)
        pl = shape([(-70, 0, 1), (60, -40, 1), (-10, 30, 1)], "#ffffff", "", w=4, seed=15020) + shape([(-10, 30, 1), (60, -40, 1), (0, 50, 1)], "#dfe8f4", "", w=4, seed=15021)
        o.append(tf(pl, px, py, 1.6, -20))
        if sent > .35:
            o.append(f'<g transform="translate({sx0} {sy0 + 130}) scale({lib.back_out(clamp((sent - .35) / .3), 2):.3f})">'
                     + shape(lib.rrect(-200, -46, 200, 46, 20), "#2a9a5a", "", w=4, seed=15030) + plain("✓ Отправлено", 0, 18, 50, fill="#ffffff", anchor="middle") + "</g>")
    return o


def frame_s14(t):
    """«Открыл, написал одну строку»: ноутбук крупно, письмо открыто, пишется одна строка."""
    a, b = T0("s14"), T1("s14")
    o = mail_screen(t, u_line=ramp(t, W(44), W(47) - W(44)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, DESK_Y - 280, 1.75 + .06 * u, 0, t=t, extra=ticker(t))


def frame_s15(t):
    """«и отправил»: бумажный самолётик улетает с экрана, плашка «Отправлено»."""
    a, b = T0("s15"), T1("s15")
    o = mail_screen(t, u_line=1.0, sent=ramp(t, W(48), .6))
    o.append(PR.sparkles(540, DESK_Y - 200, 1.8, bump(t, W(48) + .35, .05, .5), t, seed=151, n=6, r=300))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, DESK_Y - 280, 1.75 + .06 * u, 0, t=t, extra=ticker(t))


def frame_s16(t):
    """«На месте событий работает кот»: у стола героя кот-диктор в пиджаке с микрофоном говорит в камеру, Дима работает за ноутбуком."""
    a, b = T0("s16"), T1("s16")
    o = desk_room(t, sun=1.0)
    o.append(PR.laptop(600, DESK_Y - 8, 1.0, screen="lines", lines=.6, t=t, seed=1))
    tap = math.sin(t * 30)
    o.append(dima_desk(t, dict(people.EXPR["dima"]["calm82"], look=(.9, -.1)), lean=.18,
                       arms={"f": ("ik", (520 + 10 * tap, DESK_Y - 30), 1), "n": ("ik", (600 - 10 * tap, DESK_Y - 25), 1)})["svg"])
    st = dict(look=(0, 0), smile=1.0, paw=.85, paw_dx=-70.0, tilt=3 * math.sin(t * 4))
    o.append(CT.draw(900, DESK_Y - 4, .62, st, t))
    o.append(mic(900 - 70 * .62 * 1.6 * .85 - 30, DESK_Y - 220, .55, -20))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 640, 820, 1.3 + .06 * u, 0, t=t, extra=lower_third("НА МЕСТЕ СОБЫТИЙ", ramp(t, W(50), .3)) + ticker(t))


def frame_s17(t):
    """«Он сидел рядом всё это время»: кот сидит на столе рядом с Димой, Дима гладит его, сердечко."""
    a, b = T0("s17"), T1("s17")
    o = desk_room(t, sun=1.0)
    o.append(PR.laptop(560, DESK_Y - 8, 1.0, screen="lines", lines=.8, t=t, seed=1))
    tap = math.sin(t * 30)
    o.append(dima_desk(t, dict(people.EXPR["dima"]["calm82"], look=(.9, -.2), mouth="smile", smile=.8), lean=.12,
                       arms={"f": ("ik", (500 + 10 * tap, DESK_Y - 30), 1), "n": ("ik", (580 - 10 * tap, DESK_Y - 25), 1)})["svg"])
    o.append(CT.draw(820, DESK_Y - 4, .62, dict(look=(-.8, -.3), smile=1.0, tilt=-6), t))
    o.append(PR.heart(820, DESK_Y - 380, .9 * pop(t, W(56), .3), seed=2) if pop(t, W(56), .3) > .02 else "")
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 620, 820, 1.35 + .06 * u, 0, t=t, extra=ticker(t))


def frame_s18(t):
    return cta_code(t, T0("s18"), T1("s18"))


def frame_s19(t):
    """«чтобы следующая срочная новость»: кот-диктор в студии показывает лапой на зрителя, мигалки."""
    a, b = T0("s19"), T1("s19")
    o = studio_shot(t, dict(look=(0, 0), smile=1.0, perk=1.0), alarm=.6, paw=1.0, scr_inner=siren_inner(t))
    u = ease_io(ramp(t, a, b - a))
    return sview("".join(o), t, 540, 1180, 1.3 + .08 * u)


def you_inner(t, u):
    o = rect(-410, -250, 410, 250, "#d8352a")
    o += text("СРОЧНО", 0, -150, 90, fill="#ffffff", stroke="#7a1a10", sw=6)
    o += shape(ellipse_pts(0, 250, 150, 180, 20), "#11151f", "", w=3, seed=15100) + shape(ellipse_pts(0, 30, 80, 90, 16), "#11151f", "", w=3, seed=15101)
    o += PR.question_mark(0, 40, 1.0, u=u, col="#FFD23F")
    return o


def frame_s20(t):
    """«была про тебя»: экран студии крупно — «СРОЧНО», силуэт со знаком вопроса, мигалки."""
    a, b = T0("s20"), T1("s20")
    o = studio(t, alarm=1.0, scr_inner=you_inner(t, ramp(t, W(68) - .1, .35)))
    o.append(anchor(t, dict(look=(-.9, -.6), smile=1.0, turn=-.4), paw=.6, x=900, k=.9))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(68), 10)
    return sview("".join(o), t, 600 + dx, 880 + dy, 1.15 + .1 * u)


def frame_s21(t):
    """«С вами был кот»: кот-диктор стучит стопкой листов о стол."""
    a, b = T0("s21"), T1("s21")
    tap = abs(math.sin((t - a) * 9)) * (1 - ramp(t, W(73), .3))
    o = studio_shot(t, dict(look=(0, 0), smile=1.0), paw=.5 + .3 * tap, extra_front="")
    o.append(papers(700, DY - 40 - 60 * tap, 1.0, 6, 0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(72), 4)
    return sview("".join(o), t, 540 + dx, 1160 + dy, 1.35 + .05 * u)


def frame_s22(t):
    """«Хороших вам двух минут»: кот поднимает карточку «2 минуты» и машет."""
    a, b = T0("s22"), T1("s22")
    up = ease_out(ramp(t, W(76) - .2, .3))
    o = studio_shot(t, dict(look=(0, 0), smile=1.0, tilt=5 * math.sin(t * 5)), paw=.5 + .5 * up, scr_inner=siren_inner(t))
    card = shape(lib.rrect(-170, -110, 170, 110, 16), "#FFD23F", "", w=5, seed=15200) + text("2 минуты", 0, 22, 70, fill="#111", stroke="#111", sw=.01)
    o.append(tf(card, 700, DY - 330 - 260 * up, .85 + .2 * up, -6))
    o.append(PR.sparkles(700, DY - 600, 1.6, bump(t, W(76), .05, .5), t, seed=221, n=6, r=220))
    u = ease_io(ramp(t, a, b - a))
    return sview("".join(o), t, 580, 1080, 1.3 + .05 * u)


def frame_s23(t):
    """Петля: кадр хука — студия, мигалки, кот-диктор за столом."""
    a, b = T0("s23"), T1("s23")
    o = studio_shot(t, dict(look=(0, 0), smile=0.0, perk=1.0), alarm=1.0, paw=.4, scr_inner=siren_inner(t))
    import anim
    hc = anim.hook_cam(0.0, hit=HIT)
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 1180, 1.45 * (1 + (hc["zoom"] - 1) * u), hc["rot"] * u, t=t, extra=ticker(t))


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
