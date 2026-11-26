"""Рилс 114 «Стоматолог», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json. Говорит Дима от первого лица. Места: комната с настенным календарём
(месяцы листаются, щека опухает), кабинет с креслом стоматолога, телефон с записью крупно. Призыв — TG-карточка v5
(scripts/story_cta_tg.py). NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people, REPO, COMMON  # noqa: E402

sys.path.insert(0, os.path.join(REPO, "scripts"))
import story_cta_tg as TG  # noqa: E402

HIT = stress(1, .3)
MONTHS = ["ЯНВ", "ФЕВ", "МАР", "АПР", "МАЙ", "ИЮН", "ИЮЛ", "АВГ", "СЕН", "ОКТ", "НОЯ", "ДЕК"]
CAL = (720.0, 820.0)
SKIN, SKIN_SH = "#ecc4a2", "#d9a984"


def month_cal(t, u, x=CAL[0], y=CAL[1], k=1.0, crosses=False):
    """Отрывной календарь: месяц по u (0 — январь, 1 — декабрь), верхний лист улетает вверх."""
    m = min(11, int(u * 12 * .9999))
    frac = u * 12 - m if u < 1 else 0.0
    o = [blob(lib.rect_pts(x - 230 + 12, y - 280 + 14, x + 230 + 12, y + 280 + 14), "#000000", .15)]

    def leaf(mi, dy=0.0, rot=0.0, op=1.0):
        inner = blob(lib.rect_pts(-230, -280, 230, -150), "#c8553d")
        inner += text(MONTHS[mi], 0, -180, 100, fill="#ffffff", stroke="#7a2a1e", sw=6)
        inner += text(str(mi + 1), 0, 120, 230, fill="#1d2448", stroke="#ffffff", sw=4)
        if crosses:
            inner += PR.cross_stroke((-140, -60), (140, 220), (140, -60), (-140, 220), u=1.0, w=24, seed=mi)
        g = shape(lib.rect_pts(-230, -280, 230, 280), "#fbf8f1", inner, w=4, seed=1700 + mi)
        return f'<g opacity="{op:.3f}" transform="translate({x:.1f} {y + dy:.1f}) rotate({rot:.2f}) scale({k:.3f})">{g}</g>'
    o.append(leaf(min(11, m + 1)) if frac > 0 and m < 11 else "")
    o.append(leaf(m, -500 * frac * frac, -25 * frac, 1 - frac) if frac > 0 and m < 11 else leaf(m))
    for j in range(5):
        o.append(shape(ellipse_pts(x - 160 + 80 * j, y - 285, 12, 18, 10), "#5a5f6e", "", w=3, seed=1750 + j))
    return "".join(o)


def cheek(f, sw, k=.78):
    """Опухшая щека: розовый бугор у ближней щеки (по рту и голове фигуры), sw 0…1."""
    if sw <= 0:
        return ""
    mx, my = f["mouth"]
    hx, hy = f["head"]
    cx, cy = mx - 62 * k, my - 6 * k
    r = (24 + 36 * sw) * k
    o = shape(ellipse_pts(cx, cy, r, r * .9, 20), SKIN, blob(ellipse_pts(cx + r * .2, cy + r * .3, r * .7, r * .5, 14), SKIN_SH, .6), w=4 * k, seed=1800)
    o += PR.glow(cx, cy, r * 1.4, .35 * sw, "#ff6a5a")
    return o


def room(t):
    o = [plain_room(t)]
    o.append(rug(540, RFL + 150, 600))
    return o


def frame_s01(t):
    """ХУК: календарь листает месяцы, Дима рядом держится за щёку, щека опухает."""
    u = clamp(t / 2.0) * .6
    o = room(t)
    o.append(month_cal(t, u))
    f = stand(260, t, "panic82" if t > .3 else "squint82", "d82_rest", head_add=.05)
    o.append(f["svg"])
    o.append(cheek(f, .3 + .3 * clamp(t / .9)))
    hx, hy = f["head"]
    o.append(PR.bolt(hx + 60, hy - 200, hx + 20, hy - 60, u=1.0, w=22, seed=int(t * 8) % 3) if (t * 6) % 1 < .5 else "")
    dx, dy = shake(t, HIT, 10)
    return hook_view("".join(o), t, HIT, 520, 960, 1.15, 0, dx=dx, dy=dy)


def dental_chair(x, y, k=1.0, light=1.0):
    """Кресло стоматолога (x, y — пол под основанием), спинка откинута, лампа на штанге, поднос с инструментом."""
    o = [shape(lib.rrect(x - 80, y - 60, x + 120, y, 14), "#c9cdd5", "", w=4, seed=1900)]
    o.append(shape(lib.rect_pts(x - 20, y - 280, x + 40, y - 60), "#aeb3bd", "", w=4, seed=1901))
    o.append(shape(lib.rrect(x - 160, y - 340, x + 260, y - 270, 30), "#5fa8c9", "", w=4, seed=1902))
    o.append(shape([(x - 160, y - 330, 1), (x - 110, y - 330, 1), (x - 300, y - 640, 1), (x - 360, y - 610, 1)], "#5fa8c9", "", w=4, seed=1903))
    o.append(shape(lib.rrect(x + 230, y - 300, x + 340, y - 250, 20), "#5fa8c9", "", w=4, seed=1904))
    o.append(line([(x + 380, y), (x + 380, y - 900), (x + 120, y - 980)], 14, "#7d8597", taper=0, wmin=1, seed=1905))
    o.append(shape(ellipse_pts(x + 90, y - 960, 90, 50, 18), "#e6e8ee", blob(ellipse_pts(x + 90, y - 940, 60, 26, 14), "#fff6c0", light), w=4, seed=1906))
    if light > 0:
        o.append(f'<path d="M{x + 30} {y - 930} L{x + 150} {y - 930} L{x + 60} {y - 420} L{x - 260} {y - 420} Z" fill="#fff4c0" opacity="{.35 * light:.3f}"/>')
    o.append(shape(lib.rect_pts(x + 420, y - 500, x + 640, y - 470), "#c9cdd5", "", w=4, seed=1907))
    o.append(line([(x + 530, y - 470), (x + 530, y)], 10, "#7d8597", taper=0, wmin=1, seed=1908))
    o.append(line([(x + 450, y - 500), (x + 520, y - 510)], 5, "#5a5f6e", seed=1909))
    o.append(line([(x + 550, y - 500), (x + 610, y - 515)], 5, "#5a5f6e", seed=1910))
    return "".join(o)


def frame_s02(t):
    """«сходил к стоматологу»: кабинет, лампа вспыхивает на «стоматологу», Дима садится в кресло; кот на подносе."""
    a, b = T0("s02"), T1("s02")
    tl = W(4)
    o = [plain_room(t, wall="#dfeef0", floor="#b9c4c9")]
    o.append(dental_chair(560, RFL, light=ramp(t, tl, .15)))
    k = .7
    hip = RFL - 330
    sit = ease_out(ramp(t, a - .1, .5))
    f = people.dima82(500, hip - 140 * (1 - sit), k, "squint82" if t < tl else "sure82", "d82_rest", t=t,
                      feet=people.sit_kw(500, hip, k)["feet"], lean_add=-.35 * sit)
    o.append(f["svg"])
    o.append(cheek(f, .6, k))
    o.append(cat(1110, RFL - 500, .55, t, dict(look=(-.9, -.4), smile=.6, tail=10 * math.sin(t * 3))))
    o.append(PR.sparkles(650, RFL - 960, 1.6, bump(t, tl, .05, .5), t, seed=21, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tl, 10)
    return view("".join(o), 640 + dx, 1100 + dy, 1.05 + .06 * u, -1 + 2 * u, t=t)


def frame_s03(t):
    """«которого откладывал целый год»: листы летят до декабря, каждый с красным крестом, щека всё больше."""
    a, b = T0("s03"), T1("s03")
    u = .55 + .45 * clamp((t - a) / max(.4, W(8) - a))
    o = room(t)
    o.append(month_cal(t, u, crosses=True))
    f = stand(260, t, "panic82", "d82_rest", head_add=.05)
    o.append(f["svg"])
    o.append(cheek(f, .6 + .4 * u))
    if t > W(8):
        o.append(text("12", 720, 520, 200 * pop(t, W(8), .25), fill="#e2453a", stroke="#111", sw=12))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(8), 12)
    return view("".join(o), 520 + dx, 960 + dy, 1.15 + .08 * uu, 0, t=t)


def phone(x, y, k, inner):
    o = shape(lib.rrect(-220, -400, 220, 400, 50), "#2a2d36", "", w=5, seed=2000)
    o += shape(lib.rrect(-196, -370, 196, 370, 32), "#fbf8f1", inner, w=3, seed=2001)
    return tf(o, x, y, k)


def btn(x, y, w, h, col, label, press=0.0, size=46):
    s = 1 - .08 * press
    o = shape(lib.rrect(-w / 2, -h / 2, w / 2, h / 2, h / 2), col, "", w=3.4, seed=2010)
    o += text(label, 0, size * .35, size, fill="#ffffff", stroke=lib.mul(col, (.7, .7, .7)), sw=3)
    return tf(o, x, y, s)


def finger(x, y, u):
    """Палец снизу справа к точке (x, y), u 0 — у края, 1 — касается."""
    sx, sy = 1150, 1900
    tx, ty = sx + (x - sx) * u, sy + (y - sy) * u
    o = shape(lib.band([(sx + 200, sy + 400), (tx + 30, ty + 50)], 170, 120), "#d9a441", "", w=5, seed=5101)
    o += shape(lib.band([(tx + 120, ty + 200), (tx + 10, ty + 10)], 110, 70), SKIN, "", w=5, seed=5102)
    o += shape(ellipse_pts(tx, ty, 44, 52, 14), "#f7ddd0", "", w=4, seed=5103)
    return o


def appt_card(y, label, crossed=0.0, ok=0.0):
    o = shape(lib.rrect(-170, y - 70, 170, y + 70, 20), "#e8f2ff", "", w=3, seed=2020)
    o += plain("Стоматолог", -140, y - 16, 36, fill="#5a5f6e")
    o += plain(label, -140, y + 44, 50, fill="#1d2448")
    if crossed > 0:
        o += PR.cross_stroke((-150, y - 50), (150, y + 50), (150, y - 50), (-150, y + 50), u=crossed, w=18, seed=2021)
    if ok > 0:
        o += PR.check_mark(120, y - 10, 1.8, ok, w=10)
    return o


def frame_s04(t):
    """«записывался и отменял»: телефон, запись «Пн 10:00» появляется, палец жмёт красное «Отменить» — крест; второй раз «Ср 9:00»."""
    a, b = T0("s04"), T1("s04")
    c1, c2 = W(13), W(13) + .45
    inner = plain("Запись", -150, -290, 50, fill="#1d2448")
    inner += tf(appt_card(0, "Пн 10:00", crossed=ramp(t, c1, .2)), 0, -150, pop(t, W(11), .2))
    if t > c1 + .15:
        inner += tf(appt_card(0, "Ср 9:00", crossed=ramp(t, c2, .2)), 0, 30, pop(t, c1 + .15, .2))
    pr = bump(t, c1 - .03, .04, .12) + bump(t, c2 - .03, .04, .12)
    inner += btn(0, 270, 300, 90, "#e2453a", "Отменить", pr)
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552"), PR.glow(540, 900, 700, .3, "#8fb7ff")]
    o.append(phone(540, 820, 1.6, inner))
    near = min(1.0, .86 + .14 * pr) if t > W(11) else ramp(t, a, .3) * .86
    o.append(finger(540, 820 + 270 * 1.6, near))
    if t > c1:
        n = 1 if t < c2 else 2
        o.append(text(f"×{n}", 880, 520, 200 * (1 + .2 * bump(t, c1 if n == 1 else c2, .04, .2)), fill="#e2453a", stroke="#111", sw=12))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, c2, 8)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .05 * u, 0, bg="#3b3552", t=t)


def frame_s05(t):
    """«пил обезболивающее»: Дима держит стакан и таблетку у рта, блистер почти пуст; щека опухшая."""
    a, b = T0("s05"), T1("s05")
    o = room(t)
    gulp = ramp(t, W(15), .4)
    f = stand(420, t, "squint82" if gulp < .5 else "sure82", "d82_hold", head_add=-.15 * gulp)
    o.append(f["svg"])
    o.append(cheek(f, .7))
    hx, hy = f["hold"]
    o.append(PR.glass(hx + 30, hy - 40 - 60 * gulp, 1.0, rot=-30 * gulp, fill=1 - .7 * gulp, t=t))
    blis = shape(lib.rrect(-120, -70, 120, 70, 14), "#c9cdd5", "".join(
        shape(ellipse_pts(-80 + 55 * (j % 4), -30 + 60 * (j // 4), 18, 18, 12), "#ffffff" if j < 7 else "#e9e2ff", "", w=2.4, seed=2100 + j)
        for j in range(8)), w=3, seed=2099)
    o.append(tf(blis, 820, 1180, 1.2, 12))
    o.append(text("×7", 820, 1040, 120, fill="#e2453a", stroke="#111", sw=10) if t > W(15) else "")
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(15), 6)
    return view("".join(o), 560 + dx, 1000 + dy, 1.18 + .06 * u, 0, t=t)


def frame_s06(t):
    """«а зуб болел всё сильнее»: Дима держится за щёку, щека раздувается толчками, молнии и красный пульс."""
    a, b = T0("s06"), T1("s06")
    o = room(t)
    beats = [W(18), W(20), W(20) + .25]
    pulse = max(bump(t, q, .05, .2) for q in beats)
    f0 = stand(500, t, "panic82", "d82_rest")
    hx0, hy0 = f0["mouth"]
    f = stand(500, t, "panic82", "d82_rest", arms={"n": ("ik", (hx0 + 30, hy0 + 30), -1)}, head_add=.08)
    o.append(f["svg"])
    sw = .7 + .3 * ramp(t, a, b - a) + .25 * pulse
    o.append(cheek(f, sw))
    hx, hy = f["head"]
    for j in range(3):
        if pulse > .1 or (t * 5 + j) % 1 < .3:
            ang = -2.2 + .7 * j
            o.append(PR.bolt(hx + 230 * math.cos(ang), hy + 230 * math.sin(ang), hx + 110 * math.cos(ang), hy + 110 * math.sin(ang), u=1.0, w=20, seed=j))
    o.append(PR.glow(hx, hy, 300, .4 * pulse, "#ff4a3a"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(18), 12)
    return view("".join(o), 520 + dx, 860 + dy, 1.45 + .12 * u, 0, t=t)


def frame_s07(t):
    """«Вот что я поменял»: Дима поднимает палец, над ним лампочка; календарь рядом; надпись сверху."""
    a, b = T0("s07"), T1("s07")
    ti = W(21) + .15
    o = room(t)
    o.append(month_cal(t, 11 / 12))
    f = stand(260, t, "wow82" if t > ti else "sure82", "d82_one", head_add=.06 * bump(t, ti, .08, .3))
    o.append(f["svg"])
    o.append(cheek(f, .5))
    hx, hy = f["head"]
    if t > ti:
        o.append(PR.glow(hx + 170, hy - 200, 220, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx + 170, hy - 200 + 8 * math.sin(t * 5), 1.2 * pop(t, ti, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx + 170, hy - 200, 1.8, bump(t, ti, .05, .5), t, seed=71, n=5, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ti, 9)
    return view("".join(o), 520 + dx, 1000 + dy, 1.15 + .05 * u, -1 + 2 * u, t=t)


def frame_s08(t):
    """«Записываюсь прямо сейчас»: телефон, палец жмёт зелёное «Записаться» на «сейчас», карточка с галочкой."""
    a, b = T0("s08"), T1("s08")
    tp = W(27)
    pr = bump(t, tp - .03, .04, .15)
    inner = plain("Запись", -150, -290, 50, fill="#1d2448")
    if t > tp:
        inner += tf(appt_card(0, "Сегодня", ok=ramp(t, tp + .2, .3)), 0, -100, pop(t, tp, .2))
    inner += btn(0, 270, 320, 100, "#3fb26a", "Записаться", pr, 44)
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552"), PR.glow(540, 900, 700, .3, "#8fb7ff")]
    o.append(phone(540, 820, 1.6, inner))
    near = .86 + .14 * pr if t > a + .2 else ramp(t, a - .1, .3) * .86
    o.append(finger(540, 820 + 270 * 1.6, near))
    o.append(PR.sparkles(540, 800, 2.0, bump(t, tp + .2, .05, .5), t, seed=81, n=7, r=300))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tp, 8)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .05 * u, 0, bg="#3b3552", t=t)


def frame_s09(t):
    """«на ближайшее время»: список окошек, первое «Сегодня 17:30» подсвечивается и выбирается пальцем."""
    a, b = T0("s09"), T1("s09")
    ts = W(29) + .2
    slots = ["Сегодня 17:30", "Завтра 9:00", "Пт 12:00", "Через месяц"]
    inner = plain("Свободно", -150, -290, 50, fill="#1d2448")
    for j, s_ in enumerate(slots):
        y = -170 + 120 * j
        on = j == 0 and t > ts
        inner += shape(lib.rrect(-170, y - 48, 170, y + 48, 20), "#3fb26a" if on else "#e8f2ff", "", w=3, seed=2200 + j)
        inner += plain(s_, -140, y + 16, 42, fill="#ffffff" if on else "#1d2448")
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552"), PR.glow(540, 900, 700, .3, "#8fb7ff")]
    o.append(phone(540, 820, 1.6, inner))
    pr = bump(t, ts - .03, .04, .15)
    o.append(finger(540 - 60 * 1.6, 820 - 170 * 1.6, .86 + .14 * pr if t > a + .15 else ramp(t, a - .1, .25) * .86))
    o.append(PR.sparkles(540, 820 - 170 * 1.6, 1.8, bump(t, ts, .05, .5), t, seed=91, n=6, r=260))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 900, 1.08 + .05 * u, 0, bg="#3b3552", t=t)


def frame_s10(t):
    """«а не когда будет удобно»: Дима отмахивается, облачко с календарём и «потом» перечёркнуто красным крестом."""
    a, b = T0("s10"), T1("s10")
    tx = W(35) - .05
    o = room(t)
    f = stand(300, t, "proud82", "d82_one", head_add=.04)
    o.append(f["svg"])
    hx, hy = f["head"]
    inner = PR.calendar(-75, 0, 120, 140, stamps=0, seed=3) + plain("потом", 0, 18, 40, fill="#1d2448")
    o.append(PR.thought_cloud(hx + 330, hy - 40, 1.3, w=300, h=200, u=pop(t, a, .25), seed=4, inner=inner))
    xu = ramp(t, tx, .25)
    if xu > 0:
        cx, cy = hx + 330, hy - 40
        o.append(PR.cross_stroke((cx - 230, cy - 160), (cx + 230, cy + 160), (cx + 230, cy - 160), (cx - 230, cy + 160), u=xu, w=36, seed=6))
    o.append(cat(900, RFL, .8, t, dict(look=(-.7, -.6), smile=.8)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tx + .15, 10)
    return view("".join(o), 640 + dx, 980 + dy, 1.05 + .05 * u, 0, t=t)


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


def frame_s11(t):
    return cta(t)


def frame_s12(t):
    return cta(t, 1.1, (540, 1000))


def frame_s13(t):
    return cta(t, 1.04)


def frame_s14(t):
    """«Теперь улыбаюсь без боли»: Дима широко улыбается, блеск на зубе; на «без боли» откусывает яблоко; кот рядом."""
    a, b = T0("s14"), T1("s14")
    o = room(t)
    o.append(PR.window(800, 1000, 300, 380, mode="day", t=t, seed=4, curtain=False))
    tb = W(54)
    f0 = stand(460, t, "laugh82", "d82_hold")
    mx, my = f0["mouth"]
    bite = ramp(t, tb - .3, .25)
    f = stand(460, t, "laugh82", "d82_hold", arms={"n": ("ik", (mx + 80 - 40 * bite, my + 160 - 120 * bite), -1)})
    o.append(f["svg"])
    hx, hy = f["hold"]
    o.append(PR.apple(mx + 70 - 40 * bite, my + 110 - 100 * bite, 1.1, bite=1.0 if t > tb else 0.0))
    o.append(PR.star4(mx + 20, my - 10, 28 * bump(t, W(52) + .2, .05, .5) + 1))
    o.append(PR.sparkles(mx, my, 1.4, bump(t, W(52) + .2, .05, .6), t, seed=141, n=6, r=140))
    o.append(cat(800, RFL, .8, t, dict(look=(-.7, -.6), smile=1.0, tail=10 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb, 6)
    return view("".join(o), 560 + dx, 960 + dy, 1.25 + .1 * u, 0, t=t)


def frame_s15(t):
    """Петля: кадр хука — календарь на январе, Дима держится за щёку."""
    a, b = T0("s15"), T1("s15")
    o = room(t)
    o.append(month_cal(t, 0.0))
    f = stand(260, t, "squint82", "d82_rest", head_add=.05)
    o.append(f["svg"])
    o.append(cheek(f, .3))
    return loop_view("".join(o), t, a, b, HIT, 520, 960, 1.15)


def frame(sid, t):
    if sid not in ("s11", "s12", "s13"):
        lib.DEFS.clear()
    return globals()["frame_" + sid](t)
