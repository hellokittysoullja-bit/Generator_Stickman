"""Рилс 133 «Инструкция к человеку с СДВГ», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json (один голос Даниил — голос инструкции). Лист инструкции как у техники: кремовая
бумага с синей рамкой и сеткой, номера пунктов в кругах, выноски, пиктограммы; вместо прибора на схеме стоит Дима. Кот —
сервисный мастер в спецовке (common/costume.py «overalls», cat.WEAR: одежда внутри групп кота, во всех планах, и в призыве).
Призыв — TG-карточка v5 (scripts/story_cta_tg.py). Имя героя не пишется. NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people, REPO, COMMON  # noqa: E402
import costume  # noqa: E402
from ink import band  # noqa: E402

sys.path.insert(0, os.path.join(REPO, "scripts"))
import story_cta_tg as TG  # noqa: E402

costume.use("overalls")
HIT = stress(0, .35)
BLUE_D, BLUE_L, GRID = "#23407a", "#4f78b8", "#cfdcef"
SHEET = "#fbf8ef"
INK2 = "#1d2448"
DX = 400.0          # Дима на схеме
CATX = 850.0        # кот-мастер


# ═════════════ лист инструкции ═════════════
def sheet(t, header=True):
    o = [rect(-1400, -1400, 2600, 3400, "#d9c7a6")]
    o.append(blob(lib.rect_pts(46, 296, 1066, 1786), "#000000", .16))
    o.append(shape(lib.rect_pts(30, 280, 1050, 1770), SHEET, "", w=4, seed=8000))
    for i in range(1, 20):
        x = 30 + 1020 * i / 20
        o.append(line([(x, 290), (x, 1760)], 1.6, GRID, taper=0, wmin=1, seed=8010 + i, op=.7))
    for i in range(1, 29):
        y = 280 + 1490 * i / 29
        o.append(line([(40, y), (1040, y)], 1.6, GRID, taper=0, wmin=1, seed=8040 + i, op=.7))
    o.append(f'<rect x="56" y="306" width="968" height="1438" fill="none" stroke="{BLUE_D}" stroke-width="6"/>')
    o.append(f'<rect x="68" y="318" width="944" height="1414" fill="none" stroke="{BLUE_D}" stroke-width="2.5"/>')
    if header:
        o.append(rect(68, 318, 1012, 392, BLUE_D))
        o.append(plain("ИНСТРУКЦИЯ", 96, 372, 50, fill="#ffffff"))
        o.append(plain("СДВГ", 984, 372, 50, fill="#ffd23f", anchor="end"))
    # основание схемы: линия земли со штриховкой
    o.append(line([(110, RFL), (990, RFL)], 6, BLUE_D, taper=0, wmin=1, seed=8003))
    for j in range(22):
        x = 120 + 40 * j
        o.append(line([(x, RFL + 4), (x - 26, RFL + 40)], 2.4, BLUE_L, taper=0, wmin=1, seed=8100 + j))
    return "".join(o)


def badge(n, x, y, u=1.0, r=78.0):
    if u <= .01:
        return ""
    s = lib.back_out(clamp(u), 2.4) if u < 1 else 1.0
    o = shape(ellipse_pts(0, 0, r, r, 30), BLUE_D, blob(ellipse_pts(-r * .25, -r * .3, r * .55, r * .4, 16), "#3a5c9c", .7), w=5, seed=8200)
    o += f'<circle cx="0" cy="0" r="{r - 12:.1f}" fill="none" stroke="#ffffff" stroke-width="4" opacity=".8"/>'
    o += text(str(n), 0, r * .42, r * 1.25, fill="#ffffff", stroke=BLUE_D, sw=.01)
    return tf(o, x, y, s, -6 + 6 * clamp(u))


def callout(p, q, n, u=1.0, sd=0):
    """Выноска: точка на предмете p, линия к кружку с номером n в q (рисуется u 0…1)."""
    if u <= .01:
        return ""
    u = clamp(u)
    e = (p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u)
    o = line([p, e], 3.4, BLUE_D, taper=0, wmin=1, seed=8300 + sd)
    o += f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="9" fill="{BLUE_D}"/>'
    if u > .7:
        s = clamp((u - .7) / .3)
        o += tf(shape(ellipse_pts(0, 0, 34, 34, 20), "#ffffff", "", w=3.4, seed=8310 + sd, ink_color=BLUE_D) + text(str(n), 0, 15, 44, fill=BLUE_D,
                                                                                                                   stroke="#fff", sw=.01), q[0], q[1], s)
    return o


def dima(t, expr="calm82", pose="d82_rest", x=DX, **kw):
    return stand(x, t, expr, pose, **kw)


def master(t, x=CATX, y=RFL, k=1.0, st=None, wrench=0.0):
    """Кот-мастер в спецовке. wrench 0…1 — поднимает гаечный ключ (правая лапа вверх, ключ в лапе)."""
    st = dict(dict(look=(-.7, -.2), smile=.6, tail=8 * math.sin(t * 1.7)), **(st or {}))
    if wrench > 0:
        st.setdefault("paw", .9 * wrench)
        st.setdefault("paw_dx", -40.0)
    return cat(x, y, k, t, st)


def wrench_hold(tip, raised):
    """Гаечный ключ в правой лапе мастера (тот же, что был в кармане спецовки): лапа внизу — ключ стоит у лапы, поднята — ключ вверх."""
    rot = 20 * (1 - raised) - 30 * raised
    pts = costume.wrench_pts(0, 0, 1.15, 0)
    o = shape(pts, "#b9c0c8", line([(-3, -10), (-3, -60)], 2.4, "#ffffff", seed=8400, op=.6), w=3.4, seed=8401)
    return f'<g transform="translate({tip[0]:.2f} {tip[1] + 6:.2f}) rotate({rot:.2f})">{o}</g>'


CT.WEAR["hold"] = wrench_hold


def spinner(x, y, r, t, op=1.0):
    """Колесо загрузки: 8 точек, яркая бежит по кругу."""
    if op <= .01:
        return ""
    o = shape(ellipse_pts(x, y, r + 30, r + 30, 30), "#ffffff", "", w=4, seed=8500)
    ph = t * 10
    for j in range(8):
        a = 2 * math.pi * j / 8
        v = (j - ph) % 8
        a_ = .25 + .75 * (v / 8)
        o += f'<circle cx="{x + r * math.cos(a):.1f}" cy="{y + r * math.sin(a):.1f}" r="{r * .2:.1f}" fill="{BLUE_D}" opacity="{a_:.3f}"/>'
    return f'<g opacity="{op:.3f}">{o}</g>'


def thermometer(x, y, k, level, t):
    """Термометр: колба внизу (x, y), шкала вверх ~420; level 0…1 — ртуть."""
    o = shape(lib.rrect(-30, -440, 30, -40, 28), "#ffffff", "", w=4.4, seed=8600)
    for j in range(7):
        yy = -110 - 50 * j
        o += line([(-30, yy), (-12, yy)], 3, INK2, taper=0, wmin=1, seed=8610 + j)
    hgt = 60 + 330 * clamp(level)
    col = "#e2453a" if level > .55 else "#f08a3a"
    o += rect(-12, -40 - hgt, 12, -30, col)
    o += shape(ellipse_pts(0, 0, 58, 58, 24), col, blob(ellipse_pts(-16, -16, 18, 14, 10), "#ffb3a8", .8), w=4.4, seed=8601)
    return tf(o, x, y, k)


def battery(x, y, k, level, col=None):
    """Батарейка горизонтально (центр x, y): корпус 300×150, ячейки по уровню."""
    col = col or ("#3fb26a" if level > .5 else "#f2b04a" if level > .2 else "#e2453a")
    o = shape(lib.rrect(-150, -75, 150, 75, 18), "#ffffff", "", w=5.4, seed=8700)
    o += shape(lib.rrect(150, -30, 178, 30, 6), "#ffffff", "", w=4, seed=8701)
    w_ = 268 * clamp(level)
    if w_ > 2:
        o += shape(lib.rrect(-134, -59, -134 + w_, 59, 10), col, blob(lib.rect_pts(-130, -55, -134 + w_ - 4, -30), "#ffffff", .35), w=2.6, seed=8702)
    return tf(o, x, y, k)


def plug_cable(p0, p1, sag=80, seed=0):
    m = ((p0[0] + p1[0]) / 2, max(p0[1], p1[1]) + sag)
    return PR.cable([p0, m, p1], col="#2a2d36", w=9, seed=seed)


def prohibit(x, y, k, inner, u=1.0, cross_u=1.0):
    if u <= .01:
        return ""
    s = lib.back_out(clamp(u), 2.2) if u < 1 else 1.0
    o = f'<circle cx="0" cy="0" r="170" fill="#ffffff"/>' + inner
    o += f'<circle cx="0" cy="0" r="160" fill="none" stroke="#e2453a" stroke-width="34"/>'
    cu = clamp(cross_u)
    if cu > 0:
        a = (-113, -113)
        b = (-113 + 226 * cu, -113 + 226 * cu)
        o += f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#e2453a" stroke-width="34" stroke-linecap="round"/>'
    return tf(o, x, y, k * s)


def megaphone_icon(t):
    o = shape([(-90, -40, 1), (-30, -40, 1), (60, -100, 1), (60, 100, 1), (-30, 40, 1), (-90, 40, 1)], BLUE_D, "", w=4, seed=8800)
    for j in range(3):
        r = 40 + 30 * j + 8 * math.sin(t * 14 + j)
        o += f'<path d="M{80 + r * .3:.1f} {-r * .8:.1f} Q{90 + r:.1f} 0 {80 + r * .3:.1f} {r * .8:.1f}" fill="none" stroke="{BLUE_D}" stroke-width="10" stroke-linecap="round"/>'
    return o


def shake_icon(t):
    """Две руки трясут человечка-пиктограмму."""
    j = 14 * math.sin(t * 40)
    o = f'<circle cx="{j:.1f}" cy="-80" r="34" fill="{BLUE_D}"/>'
    o += shape([(-40 + j, -40, 1), (40 + j, -40, 1), (30 + j, 70, 1), (-30 + j, 70, 1)], BLUE_D, "", w=4, seed=8810)
    for sx in (-1, 1):
        o += shape(lib.rrect(-26, -22, 26, 22, 10), "#f2c7a5", "", w=3.6, seed=8812 + sx).replace("<g ", f'<g transform="translate({sx * 70 + j * .5:.1f} -10)" ', 1)
        o += line([(sx * 92 + j * .5, -10), (sx * 140, -6)], 18, "#f2c7a5", taper=0, wmin=1, seed=8814 + sx)
        o += line([(sx * 116, -46), (sx * 130, -60)], 4, BLUE_D, seed=8816 + sx)
    return o


def star5(x, y, r, u=1.0, col="#ffd23f", rot=0.0):
    if u <= .01:
        return ""
    s = lib.back_out(clamp(u), 2.6) if u < 1 else 1.0
    pts = []
    for j in range(10):
        a = math.radians(-90 + 36 * j)
        rr = r if j % 2 == 0 else r * .45
        pts.append((rr * math.cos(a), rr * math.sin(a), 1))
    return tf(shape(pts, col, blob([(p[0] * .5 - r * .1, p[1] * .5 - r * .15) for p in pts], "#fff2a8", .7), w=4.4, seed=8900), x, y, s, rot)


def trophy(x, y, k, u=1.0):
    if u <= .01:
        return ""
    s = lib.back_out(clamp(u), 2.2) if u < 1 else 1.0
    o = shape([(-80, -170, 1), (80, -170, 1), (70, -90), (30, -40), (-30, -40), (-70, -90)], "#f2c14e", blob([(-60, -160), (-20, -160), (-30, -60), (-50, -90)],
                                                                                                         "#fff1b0", .7), w=4.6, seed=8950)
    for sx in (-1, 1):
        o += line([(sx * 76, -150), (sx * 118, -140), (sx * 104, -96), (sx * 60, -86)], 9, "#c8952a", taper=0, wmin=1, seed=8951 + sx)
    o += shape(lib.rect_pts(-16, -44, 16, 0), "#e0a83a", "", w=3.6, seed=8953)
    o += shape(lib.rrect(-60, 0, 60, 34, 6), "#8a6038", "", w=3.6, seed=8954)
    return tf(o, x, y, k * s)


def timer_face(x, y, k, left, pulse=0.0):
    m, s_ = int(left // 60), int(left % 60)
    o = shape(ellipse_pts(0, 0, 120, 120, 30), "#ffffff", text(f"{m}:{s_:02d}", 0, 26, 76, fill=INK2, stroke="#ffffff", sw=4), w=5.4, seed=9000)
    o += shape(lib.rrect(-20, -150, 20, -118, 6), "#e2453a", "", w=3.4, seed=9001)
    return tf(o, x, y, k * (1 + .2 * pulse))


def paper_plane(x, y, k, rot=0.0):
    o = shape([(-90, 10, 1), (100, -40, 1), (-40, 60, 1)], "#ffffff", blob([(-40, 60), (100, -40), (-10, 30)], "#dbe4f2"), w=4, seed=9100)
    o += shape([(-40, 60, 1), (100, -40, 1), (-30, 90, 1)], "#eef2f8", "", w=3.6, seed=9101)
    return tf(o, x, y, k, rot)


def heat_marks(hx, hy, u, t):
    if u <= .01:
        return ""
    return PR.smoke_curls(hx, hy - 170, 1.3 * u, u, t, seed=3, col="#e8e2d8", n=3)


# ═════════════ планы ═════════════
def frame_s01(t):
    """ХУК: лист инструкции влетает (уже с первого кадра на экране), Дима стоит на схеме как прибор, выноски 1–4,
    кот-мастер в спецовке стукает ключом по основанию."""
    o = [sheet(t)]
    tap = bump(t, HIT, .06, .25)
    f = dima(t, "wow82", "d82_shrug", head_add=.05 * tap)
    o.append(f["svg"])
    hx, hy = f["head"]
    for n, (p, q) in enumerate([((hx - 60, hy), (150, 520)), ((DX - 90, 1020), (150, 960)), ((DX + 60, 1180), (690, 760)), ((DX - 40, 1450), (150, 1380))]):
        o.append(callout(p, q, n + 1, 1.0, n))
    o.append(master(t, x=860, k=1.2, st=dict(look=(-.9, -.2), smile=1.0, perk=1.0, tilt=-6 * tap), wrench=.7 + .3 * tap))
    o.append(PR.sparkles(DX + 120, 1500, 1.4, tap, t, seed=11, n=5, r=160))
    dx, dy = shake(t, HIT, 10)
    return hook_view("".join(o), t, HIT, 560, 1060, 1.06, 0, dx=dx, dy=dy)


def tag(x, y, u, t):
    """Бирка «СДВГ» на нитке у запястья."""
    if u <= .01:
        return ""
    sw = 8 * math.sin(t * 5)
    s = lib.back_out(clamp(u), 2.4) if u < 1 else 1.0
    o = line([(0, 0), (10, 70)], 3, INK2, seed=9200)
    o += shape([(-60, 70, 1), (90, 70, 1), (110, 120, 1), (90, 170, 1), (-60, 170, 1)], "#ffd23f", text("СДВГ", 20, 140, 64, fill=INK2, stroke="#ffd23f", sw=.01),
               w=4, seed=9201)
    o += f'<circle cx="-36" cy="120" r="10" fill="#ffffff" stroke="{INK2}" stroke-width="3"/>'
    return tf(o, x, y, s, sw)


def frame_s02(t):
    """«к человеку с СДВГ»: Дима на подставке как прибор, выноски дорисовываются, на запястье бирка «СДВГ», кот подкручивает ключом."""
    a, b = T0("s02"), T1("s02")
    o = [sheet(t)]
    o.append(shape(lib.rrect(DX - 200, RFL - 30, DX + 200, RFL + 10, 10), "#9aa6b8", "", w=4, seed=9210))
    f = dima(t, "puzzled82", "d82_rest", fl=RFL - 30)
    o.append(f["svg"])
    hx, hy = f["head"]
    wx, wy = f["wrist"]["n"]
    pts = [((hx - 60, hy), (150, 520)), ((DX - 90, 1000), (150, 960)), ((DX + 60, 1160), (700, 760)), ((DX - 40, 1430), (150, 1380))]
    for n, (p, q) in enumerate(pts):
        o.append(callout(p, q, n + 1, ramp(t, a - .2 + .25 * n, .35), n))
    o.append(tag(wx, wy, ramp(t, W(4) - .1, .25), t))
    turn = math.sin(t * 14) * (t > W(2))
    o.append(master(t, x=CATX - 40, st=dict(look=(-.9, -.4), smile=.8), wrench=.85 + .15 * turn))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(4), 8)
    return view("".join(o), 560 + dx, 1060 + dy, 1.06 + .06 * u, 0, t=t)


def frame_s03(t):
    """«Пункт первый. Не перегревать»: номер 1, рядом термометр, ртуть ползёт вверх, над головой Димы пар, он краснеет."""
    a, b = T0("s03"), T1("s03")
    o = [sheet(t)]
    o.append(badge(1, 170, 500, ramp(t, a - .2, .3)))
    lvl = .25 + .7 * ease_in(ramp(t, W(7), WE(8) - W(7)))
    o.append(thermometer(800, 1300, 1.25, lvl, t))
    hot = clamp((lvl - .5) / .4)
    f = dima(t, dict(people.EXPR["dima"]["strain"], blush=.3 + .7 * hot), "d82_rest", x=DX - 20)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(heat_marks(hx, hy, hot, t))
    if hot > .3:
        o.append(PR.sweat(hx + 90, hy - 40, 1.1))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(8), 7)
    return view("".join(o), 560 + dx, 1040 + dy, 1.05 + .07 * u, 0, t=t)


def frame_s04(t):
    """«сорок дел сразу»: вокруг головы Димы кружит хоровод листков, счётчик «40» в углу."""
    a, b = T0("s04"), T1("s04")
    o = [sheet(t)]
    f = dima(t, "panic82", "d82_shrug", x=DX + 120)
    o.append(f["svg"])
    hx, hy = f["head"]
    n = 18
    for j in range(n):
        ang = 2 * math.pi * j / n + (t - a) * 3.2
        r = 300 + 40 * math.sin(j * 1.7)
        o.append(PR.flying_sheet(hx + r * math.cos(ang), hy + 30 + r * .55 * math.sin(ang), .55, rot=math.degrees(ang) * .5 + 20 * j, seed=j,
                                 kind="lines", flap=math.sin(t * 8 + j)))
    cnt = int(round(12 + 28 * ease_out(ramp(t, a - .1, .5))))
    o.append(tf(shape(lib.rrect(-120, -80, 120, 80, 24), "#e2453a", text(str(cnt), 0, 34, 104, fill="#ffffff", stroke="#7a1a14", sw=6), w=5, seed=9300),
                870, 520, 1.0 + .15 * bump(t, a + .45, .05, .25), 6))
    o.append(badge(1, 170, 500, 1.0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(10), 8)
    return view("".join(o), 560 + dx, 1020 + dy, 1.08 + .06 * u, 0, t=t)


def frame_s05(t):
    """«вызывают зависание»: Дима застыл с поднятыми руками, лицо пустое, над головой колесо загрузки; кот-мастер чешет затылок."""
    a, b = T0("s05"), T1("s05")
    o = [sheet(t)]
    o.append(rect(-1400, -1400, 2600, 3400, "#9fc0e8", .14))
    f = dima(t, "zombie", "d82_shrug", x=DX)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(spinner(hx + 230, hy - 60, 70, t))
    o.append(master(t, st=dict(look=(-.9, -.5), smile=0.0, tilt=10, perk=0.0, ear=-8), wrench=.5))
    o.append(badge(1, 170, 500, 1.0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(13), 6)
    return view("".join(o), 560 + dx, 1050 + dy, 1.08 + .07 * u, 0, t=t)


def chest_battery(f, level, k=.55, col=None):
    nx, ny = f["neck"]
    return battery(nx + 10, ny + 150, k, level, col)


def frame_s06(t):
    """«Пункт второй»: номер 2, у Димы на груди батарейка почти пустая, Дима устал."""
    a, b = T0("s06"), T1("s06")
    o = [sheet(t)]
    o.append(badge(2, 170, 500, ramp(t, a - .2, .3)))
    f = dima(t, "sleepy", "d82_rest")
    o.append(f["svg"])
    lv = .14 + .03 * math.sin(t * 9)
    o.append(chest_battery(f, lv))
    o.append(master(t, st=dict(look=(-.9, -.1), smile=.4), wrench=.3))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 520, 1000, 1.12 + .06 * u, 0, t=t)


def frame_s07(t):
    """«Заряжать интересом»: кот втыкает провод от яркой лампочки-идеи в батарейку на груди Димы, батарейка заполняется зелёным."""
    a, b = T0("s07"), T1("s07")
    o = [sheet(t)]
    o.append(badge(2, 170, 500, 1.0))
    ch = ease_io(ramp(t, W(17) - .15, .7))
    f = dima(t, dict(people.EXPR["dima"]["calm82"], smile=.4 + .5 * ch, lid=.5 + .4 * ch), "d82_rest")
    o.append(f["svg"])
    nx, ny = f["neck"]
    bx, by = nx + 10, ny + 150
    bulb = (820, 720)
    o.append(plug_cable((bulb[0], bulb[1] + 60), (bx + 100, by), sag=160, seed=3))
    o.append(PR.idea_bulb(bulb[0], bulb[1], 1.5, on=.6 + .4 * ch, t=t, seed=2))
    o.append(chest_battery(f, .14 + .84 * ch))
    if ch > .1:
        o.append(PR.sparkles(bx, by, 1.2, ch, t, seed=71, n=5, r=150))
    o.append(master(t, x=CATX + 20, st=dict(look=(-.9, -.6), smile=1.0, perk=1.0), wrench=1.0))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 580, 1000, 1.05 + .05 * u, 0, t=t)


def frame_s08(t):
    """«Скучные дела»: рядом с Димой серая высокая стопка бумаг, он зевает."""
    a, b = T0("s08"), T1("s08")
    o = [sheet(t)]
    o.append(badge(2, 170, 500, 1.0))
    o.append(PR.paper_stack(760, RFL, 2.0, n=14, seed=5, mess=.4))
    o.append(rect(560, 600, 980, RFL, "#8a8f99", .0))
    f = dima(t, "sleepy", "d82_rest", x=DX - 40, head_add=-.08)
    o.append(f["svg"])
    nx, ny = f["neck"]
    o.append(battery(nx + 10, ny + 150, .55, .9))
    hx, hy = f["head"]
    o.append(PR.zzz(hx + 120, hy - 160, 1.0, t, ramp(t, a, .3)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1060, 1.1 + .05 * u, 0, t=t)


def frame_s09(t):
    """«разряжают батарею за минуту»: батарейка крупно, тает от полной к нулю, секундомер «1:00» отсчитывает, Дима сползает."""
    a, b = T0("s09"), T1("s09")
    o = [sheet(t)]
    d = ease_in(ramp(t, a - .1, WE(23) - a))
    o.append(battery(660, 860, 1.3, .95 - .93 * d))
    left = 60 * (1 - d)
    o.append(timer_face(840, 560, .8, left, bump(t, W(23), .05, .3)))
    f = dima(t, "slump", "d82_rest", x=260, head_add=-.12 * d, lean_add=.1 * d)
    o.append(f["svg"])
    o.append(badge(2, 170, 500, 1.0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(23), 9)
    return view("".join(o), 560 + dx, 1000 + dy, 1.05 + .05 * u, 0, t=t)


def frame_s10(t):
    """«Пункт третий. Если завис»: номер 3, Дима застыл посреди шага, колесо загрузки, лист слегка синеет."""
    a, b = T0("s10"), T1("s10")
    o = [sheet(t)]
    o.append(badge(3, 170, 500, ramp(t, a - .2, .3)))
    fr = ramp(t, W(27), .2)
    o.append(rect(-1400, -1400, 2600, 3400, "#9fc0e8", .16 * fr))
    f = dima(t if fr < 1 else W(27) + .2, "zombie", "d82_one", x=DX + 60)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(spinner(hx, hy - 250, 64, t, op=fr))
    o.append(master(t, x=CATX + 30, k=.9, st=dict(look=(-.9, -.4), smile=.0, perk=1.0)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(27), 6)
    return view("".join(o), 560 + dx, 1050 + dy, 1.08 + .06 * u, 0, t=t)


def frame_s11(t):
    """«не кричать и не трясти»: две пиктограммы-запрета — рупор и трясущие руки, кот-мастер поднимает лапу «стоп»."""
    a, b = T0("s11"), T1("s11")
    o = [sheet(t)]
    o.append(badge(3, 170, 500, 1.0))
    o.append(prohibit(320, 620, .95, megaphone_icon(t), ramp(t, a - .25, .25), ramp(t, W(29), .25)))
    o.append(prohibit(760, 620, .95, shake_icon(t), ramp(t, a - .05, .25), ramp(t, W(32), .25)))
    f = dima(t, "zombie", "d82_one", x=300, k=.52)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(spinner(hx + 170, hy - 20, 46, t))
    o.append(master(t, x=780, y=RFL, k=1.05, st=dict(look=(-.8, -.3), smile=.0, paw=ease_out(ramp(t, W(29) - .2, .2)), paw_dx=20)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(32), 7)
    return view("".join(o), 550 + dx, 1060 + dy, 1.04 + .05 * u, 0, t=t)


def frame_s12(t):
    """«Дать две минуты и посидеть рядом»: Дима сидит на основании схемы, кот-мастер садится рядом и прислоняется, таймер 2:00 тикает,
    колесо загрузки тает."""
    a, b = T0("s12"), T1("s12")
    o = [sheet(t)]
    o.append(badge(3, 170, 500, 1.0))
    o.append(shape(lib.rrect(170, RFL - 200, 760, RFL - 150, 14), "#c9a06a", "", w=4, seed=9400))
    for x_ in (200, 730):
        o.append(line([(x_, RFL - 150), (x_, RFL)], 12, "#8a6038", taper=0, wmin=1, seed=9401 + x_))
    k = .7
    hip = RFL - 230
    calm = ease_io(ramp(t, W(37), .6))
    f = people.dima82(360, hip, k, dict(people.EXPR["dima"]["calm82"], lid=.6 + .3 * calm, smile=.3 + .5 * calm, look=(.7, .2)), "d82_rest", t=t,
                      feet=people.sit_kw(360, hip, k)["feet"])
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(spinner(hx, hy - 220, 56, t, op=1 - ease_io(ramp(t, W(35), .9))))
    j = ease_io(ramp(t, a - .15, .45))
    cx_ = 980 + (600 - 980) * j
    cy_ = RFL - 200 - 120 * math.sin(math.pi * j)
    o.append(master(t, x=cx_, y=cy_, k=.95, st=dict(look=(-.9, -.1), smile=1.0, legs=1 - j if j < 1 else 0.0, tilt=-8 * calm)))
    left = 120 - 40 * clamp((t - W(34)) / 3.0)
    o.append(timer_face(830, 600, .9, left, bump(t, W(35), .05, .3)))
    if calm > .2:
        o.append(PR.heart(560, 860, .9 * calm, seed=2))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1080, 1.1 + .06 * u, 0, t=t)


def frame_s13(t):
    """«Пункт четвёртый. Хвалить за начало»: номер 4, Дима за столом открывает ноутбук, на «начало» кот клеит ему на плечо золотую звезду."""
    a, b = T0("s13"), T1("s13")
    o = [sheet(t)]
    o.append(badge(4, 170, 500, ramp(t, a - .2, .3)))
    o.append(PR.desk(640, RFL - 300, w=560, depth=90, leg_h=300, seed=7))
    op = ease_out(ramp(t, a + .2, .6))
    o.append(PR.laptop(660, RFL - 306, 1.1, open_=op, screen="lines", lines=.2 * op, t=t, seed=1))
    k = .62
    hip = RFL - 300
    o.append(chair(330, RFL - 240, 1.0))
    f = people.dima82(330, hip, k, dict(people.EXPR["dima"]["calm82"], smile=.5 + .4 * ramp(t, W(43), .3), look=(.9, .1)), "sit_desk", t=t,
                      feet=people.sit_kw(330, hip, k)["feet"], arms={"f": ("ik", (600, RFL - 330), 1), "n": ("ik", (660, RFL - 320), 1)})
    o.append(f["svg"])
    nx, ny = f["neck"]
    st_u = ramp(t, W(43) - .05, .3)
    o.append(star5(nx - 10, ny + 60, 56, st_u, rot=-10))
    o.append(PR.sparkles(nx, ny + 40, 1.2, bump(t, W(43), .05, .5), t, seed=131, n=6, r=150))
    o.append(master(t, x=920, k=.85, st=dict(look=(-.9, -.4), smile=1.0, paw=bump(t, W(43) - .15, .1, .4), paw_dx=-40)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(43), 6)
    return view("".join(o), 580 + dx, 1100 + dy, 1.1 + .06 * u, 0, t=t)


def frame_s14(t):
    """«а не только за результат»: справа на основании кубок, у Димы на груди звезда за начало и кубок за результат, кот хлопает."""
    a, b = T0("s14"), T1("s14")
    o = [sheet(t)]
    o.append(badge(4, 170, 500, 1.0))
    f = dima(t, "proud82", "d82_one", x=DX - 30)
    o.append(f["svg"])
    nx, ny = f["neck"]
    o.append(star5(nx - 10, ny + 60, 56, 1.0, rot=-10))
    o.append(trophy(790, 900, 1.5, ramp(t, W(48) - .2, .3)))
    o.append(PR.sparkles(790, 760, 1.6, bump(t, W(48), .05, .5), t, seed=141, n=6, r=200))
    o.append(master(t, x=820, k=.9, st=dict(look=(-.8, -.5), smile=1.0, perk=1.0, paw=.3 + .3 * abs(math.sin(t * 12)), paw_dx=-30)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(48), 7)
    return view("".join(o), 560 + dx, 1060 + dy, 1.06 + .05 * u, 0, t=t)


def warranty_card(x, y, k, stamp_u, rot=-4):
    o = shape(lib.rect_pts(-330, -200, 330, 200), "#fffdf4", "", w=5, seed=9500)
    o += f'<rect x="-300" y="-170" width="600" height="340" fill="none" stroke="{BLUE_L}" stroke-width="3"/>'
    o += text("ГАРАНТИЯ", 0, -70, 96, fill=BLUE_D, stroke="#fffdf4", sw=.01)
    for j in range(3):
        o += line([(-260, -10 + 50 * j), (60, -10 + 50 * j)], 3, GRID, taper=0, wmin=1, seed=9502 + j)
    if stamp_u > .01:
        s = 1.6 - .6 * clamp(stamp_u / .6) if stamp_u < .6 else 1.0
        op = clamp(stamp_u / .3)
        st = f'<circle cx="0" cy="0" r="96" fill="none" stroke="#d8352a" stroke-width="12"/>'
        st += f'<circle cx="0" cy="0" r="74" fill="none" stroke="#d8352a" stroke-width="4"/>'
        st += check_path()
        o += f'<g opacity="{op * .9:.3f}" transform="translate(190 60) rotate(-14) scale({s:.3f})">{st}</g>'
    return tf(o, x, y, k, rot)


def check_path():
    return '<path d="M-40 0 L-10 32 L46 -34" fill="none" stroke="#d8352a" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>'


def frame_s15(t):
    """«Гарантия: при правильном обращении»: талон «ГАРАНТИЯ» крупно, кот-мастер ставит лапой красный штамп с галочкой."""
    a, b = T0("s15"), T1("s15")
    o = [sheet(t)]
    hit = W(49) + .35
    o.append(warranty_card(540, 860, 1.25, ramp(t, hit - .1, .5)))
    lift = 1 - ease_out(ramp(t, hit - .1, .15)) if t < hit + .2 else ease_out(ramp(t, hit + .2, .3))
    o.append(master(t, x=720, y=RFL, k=1.15, st=dict(look=(-.6, -.8), smile=1.0, perk=1.0, paw=.4 + .6 * lift, paw_dx=-60)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, hit, 10)
    return view("".join(o), 560 + dx, 1040 + dy, 1.06 + .05 * u, 0, t=t)


def frame_s16(t):
    """«работает лучше, чем вы думаете»: Дима за столом быстро печатает, на экране строки растут, стрелка вверх, искры, кот доволен."""
    a, b = T0("s16"), T1("s16")
    o = [sheet(t)]
    o.append(PR.desk(640, RFL - 300, w=560, depth=90, leg_h=300, seed=7))
    o.append(PR.laptop(660, RFL - 306, 1.1, screen="lines", lines=clamp((t - a) / (b - a)), t=t, seed=1))
    k = .62
    hip = RFL - 300
    o.append(chair(330, RFL - 240, 1.0))
    tap = math.sin(t * 34)
    f = people.dima82(330, hip, k, dict(people.EXPR["dima"]["proud82"], look=(.9, .1)), "sit_desk", t=t, feet=people.sit_kw(330, hip, k)["feet"],
                      arms={"f": ("ik", (600 + 10 * tap, RFL - 330), 1), "n": ("ik", (680 - 10 * tap, RFL - 320), 1)})
    o.append(f["svg"])
    gu = ease_out(ramp(t, W(54) - .2, .4))
    if gu > 0:
        ar = [(380, 760), (520, 660), (620, 700), (800, 520)]
        n_ = max(2, int(2 + (len(ar) - 2) * gu + .999))
        o.append(line(ar[:n_], 14, "#3fb26a", taper=0, wmin=1, seed=9600))
        if gu > .9:
            o.append(shape([(770, 500, 1), (850, 480, 1), (820, 560, 1)], "#3fb26a", "", w=4, seed=9601))
    o.append(PR.sparkles(660, 1050, 1.6, bump(t, W(54), .05, .5), t, seed=161, n=6, r=220))
    o.append(master(t, x=890, k=.72, st=dict(look=(-.9, -.4), smile=1.0, perk=1.0, tilt=5 * math.sin(t * 6))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(54), 6)
    return view("".join(o), 580 + dx, 1080 + dy, 1.08 + .06 * u, 0, t=t)


GK = .62
GHIP = RFL - (people.LEG_LEN - 12) * GK - 6
PHY = GHIP - 190


def frame_s17(t):
    """«Перешли тому, кто живёт с таким человеком»: лист инструкции складывается в самолётик и летит к телефону в руке соседки,
    она улыбается; Дима и кот машут вслед."""
    a, b = T0("s17"), T1("s17")
    o = [rect(-1400, -1400, 2600, 3400, "#efe2c8")]
    o.append(plain_room(t))
    fold = ease_io(ramp(t, a - .1, .45))
    fl = ease_io(ramp(t, W(59) - .1, W(62) - W(59) + .3))
    # лист → самолётик
    if fold < 1:
        sw = 360 * (1 - fold) + 120
        sh_ = 480 * (1 - fold) + 80
        o.append(tf(shape(lib.rect_pts(-sw / 2, -sh_ / 2, sw / 2, sh_ / 2), SHEET, blob(lib.rect_pts(-sw / 2, -sh_ / 2, sw / 2, -sh_ / 2 + 50), BLUE_D),
                          w=4, seed=9700), 560, 700, 1.0, -20 * fold))
    else:
        px = 560 + (740 - 560) * fl
        py = 700 - 200 * math.sin(math.pi * fl) + (PHY - 700) * fl
        o.append(PR.speed_arcs(px - 120, py, 1.0, 1.0, t, seed=9, n=3, ang=0) if 0 < fl < 1 else "")
        o.append(paper_plane(px, py, 1.1 - .4 * fl, -10 + 30 * fl))
    k, hip = GK, GHIP
    g = people.figure("girl", 860, hip, k, expr={"brows": "up", "mouth": "smile", "smile": .3 + .6 * ramp(t, W(62), .4), "lid": .9, "look": (-.6, -.1)},
                      feet=people.stand_kw(860, hip, k, "girl")["feet"], arms={"f": ("ang", 0.18, 0.18), "n": ("ik", (760, hip - 120), 1)})
    o.append(g["svg"])
    glow_ = ramp(t, W(62) - .1, .3)
    o.append(mini_phone(740, PHY, .75, 8, screen="#2f3a55" if glow_ < .5 else "#eef3fa",
                        inner=(shape(lib.rect_pts(-40, -70, 40, 70), SHEET, blob(lib.rect_pts(-40, -70, 40, -50), BLUE_D), w=2, seed=9710) if glow_ > .5 else "")))
    f = stand(250, t, "proud82", "d82_one", k=.66)
    o.append(f["svg"])
    o.append(master(t, x=470, k=.8, st=dict(look=(.8, -.5), smile=1.0, perk=1.0)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1020, 1.1 + .05 * u, 0, t=t)


def cta(t, zoom=1.0, focus=None):
    c = SH["cta"]
    if "bg" not in TG._ST:
        TG._ST["bg"] = TG.background(lib)
        TG.prepare(COMMON)
        lib.static_done()
    lib.dyn_begin()
    body, (cx, cy, s, rot) = TG.layer(t, c["t0"], c["press"], COMMON)
    if focus:
        cx, cy = cx + (focus[0] - cx) * .3, cy + (focus[1] - cy) * .3
    return lib.svg(f'<rect width="1080" height="1920" fill="#6e4a32"/><g transform="{lib.cam(cx, cy, s * zoom, rot)}">{TG._ST["bg"]}{body}</g>{over(t)}')


def frame_s18(t):
    return cta(t)


def frame_s19(t):
    return cta(t, 1.1, (540, 1000))


def frame_s20(t):
    return cta(t, 1.04)


def frame_s21(t):
    """Петля: кадр хука — лист инструкции, Дима на схеме с выносками, кот-мастер с ключом."""
    a, b = T0("s21"), T1("s21")
    o = [sheet(t)]
    f = dima(t, "wow82", "d82_shrug")
    o.append(f["svg"])
    hx, hy = f["head"]
    for n, (p, q) in enumerate([((hx - 60, hy), (150, 520)), ((DX - 90, 1020), (150, 960)), ((DX + 60, 1180), (690, 760)), ((DX - 40, 1450), (150, 1380))]):
        o.append(callout(p, q, n + 1, 1.0, n))
    o.append(master(t, x=860, k=1.2, st=dict(look=(-.9, -.2), smile=1.0, perk=1.0), wrench=.7))
    return loop_view("".join(o), t, a, b, HIT, 560, 1060, 1.06)


def ease_in(u):
    return u * u


def frame(sid, t):
    if sid not in ("s18", "s19", "s20"):
        lib.DEFS.clear()
    return globals()["frame_" + sid](t)


_ = band
