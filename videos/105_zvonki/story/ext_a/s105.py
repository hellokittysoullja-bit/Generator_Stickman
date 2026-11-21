"""Рилс 105 «Звонки», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу); числа в коде — длительности движений.
Говорит Дима от первого лица (имя не звучит и не пишется). Сквозные места: телефон крупно в руке (хук, палец, петля),
стол у окна с листом «5 ЗВОНКОВ» на стене (утро, телефон экраном вниз, идея, разговор, итог), запись к врачу, бумажка.
NOCAM=1 — без влёта, тряски и надписей (замер движения рисунка)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(STORY)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
sys.path.insert(1, os.path.join(REPO, "scripts"))
import big_title  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import cat as CT  # noqa: E402
import props as PR  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
NOCAM = bool(os.environ.get("NOCAM"))


def W(i):
    return WORDS[i]["start"]


def WE(i):
    return WORDS[i]["end"]


def stress(i, u):
    return W(i) + (WE(i) - W(i)) * u


def T0(sid):
    return SHOT[sid]["t0"]


def T1(sid):
    return SHOT[sid]["t1"]


def ramp(t, a, d):
    return clamp((t - a) / d)


def bump(t, a, up=.08, down=.3):
    if a is None:
        return 0.0
    u = t - a
    if u <= 0:
        return 0.0
    return min(1.0, u / up) * (math.exp(-(u - up) / down) if u > up else 1.0)


def shake(t, a, amp=10.0, dur=.35, f=11.0):
    if a is None or NOCAM:
        return 0.0, 0.0
    u = t - a
    if u <= 0 or u > dur * 3:
        return 0.0, 0.0
    e = math.exp(-u / dur * 2.5)
    return amp * e * math.sin(2 * math.pi * f * u), amp * .6 * e * math.cos(2 * math.pi * f * .8 * u)


def pop(t, a, d=.24):
    u = clamp((t - a) / d)
    return lib.back_out(u, 2.2) if u < 1 else 1.0


def rect(x0, y0, x1, y1, col, op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{col}"{o}/>'


def tf(inner, x, y, k=1.0, rot=0.0):
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k:.4f})">{inner}</g>'


def text(s, x, y, size, fill="#ffffff", stroke="#111", sw=10.0, anchor="middle", op=1.0):
    """Надпись шрифтом IDB (вшит в base.html) с обводкой."""
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="IDB" font-size="{size:.1f}" text-anchor="{anchor}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw:.1f}" stroke-linejoin="round" paint-order="stroke"{o} '
            f'style="font-kerning:none">{s}</text>')


def plain(s, x, y, size, fill="#1d2448", anchor="start", op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="IDB" font-size="{size:.1f}" text-anchor="{anchor}" fill="{fill}"{o} '
            f'style="font-kerning:none">{s}</text>')


# ═════════════════════════ экранные надписи ═════════════════════════
def title(t):
    if NOCAM:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, text=SH["title"]["text"], t_in=SH["title"]["t_in"], t_out=SH["title"]["t_out"], hits=hits)


def plate(t, spec, y=220.0, w=660.0, size=58.0):
    """Маленькая жёлтая плашка вверху кадра (в безопасной зоне, выше лиц): выскакивает и тает."""
    if NOCAM:
        return ""
    a, b = spec["t_in"], spec["t_out"]
    if t < a or t > b + .15:
        return ""
    u = ease_out(ramp(t, a + .02, .2))
    op = 1.0 - ramp(t, b, .15)
    s = .6 + .4 * lib.back_out(u, 2.0) if u < 1 else 1.0
    body = (f'<rect x="{-w / 2}" y="-62" width="{w}" height="104" rx="22" fill="#FFD23F" stroke="#111" stroke-width="6"/>'
            + text(spec["text"], 0, 18, size, fill="#111", stroke="#111", sw=0.01))
    return f'<g opacity="{op:.3f}" transform="translate(540 {y}) rotate(-2) scale({s:.4f})">{body}</g>'


def kot_print(t, t0, x, y, size):
    """Кодовое слово печатными: жирный IDB, жёлтый с чёрной обводкой и тенью (как «КОТ» в рилсах 101–104); буквы выскакивают по
    одной с t0 (по 0.09 с), y — базовая линия, x — центр слова."""
    if t < t0:
        return ""
    o = []
    w = size * .74
    for j, ch in enumerate("КОТ"):
        u = clamp((t - t0 - .09 * j) / .2)
        if u <= 0:
            continue
        s = lib.back_out(u, 2.6) if u < 1 else 1.0
        cx = x + (j - 1) * w
        letter = (f'<text x="0" y="10" font-family="IDB" font-size="{size:.1f}" text-anchor="middle" fill="#000" opacity=".35" '
                  f'stroke="#000" stroke-width="{size * .12:.1f}" stroke-linejoin="round">{ch}</text>'
                  + text(ch, 0, 0, size, fill="#FFD23F", stroke="#111", sw=size * .11))
        o.append(f'<g transform="translate({cx:.1f} {y:.1f}) rotate({-3 + 2 * j}) scale({s:.4f})">{letter}</g>')
    return "".join(o)


def kot_small(t):
    """«КОТ» держится маленьким вверху до конца призыва (план s13)."""
    if NOCAM:
        return ""
    k = SH["kot"]
    if t < T1("s12") - .01 or t > k["t_out"]:
        return ""
    return kot_print(t, -9.0, 300, 330, 140)


def over(t):
    return title(t) + plate(t, SH["label"]) + plate(t, SH["label2"], w=380, size=70) + kot_small(t)


BG = "#efe2c8"


def view(body, cx, cy, s, rot=0.0, bg=BG, t=0.0, extra=""):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{extra}{over(t)}')


def hook_wrap(body, t, hit, bg=BG):
    import anim
    hc = anim.hook_cam(t, hit=hit)
    z, r, dx, dy = hc["zoom"], hc["rot"], hc["dx"], hc["dy"]
    piv = 960.0
    tr = f"translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) scale({z:.5f}) translate(-540 {-piv})"
    blur = ""
    amt = hc["zoom_blur"] / 0.07
    if amt > 0.03:
        for dk, op in ((.03, .30), (.06, .2), (.1, .12)):
            blur += (f'<use href="#hk105" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk105">{body}</g></g>{blur}'


def cat(x, y, k, t, st=None):
    st = dict(dict(look=(-.4, -.2), tail=8 * math.sin(t * 1.7), flame_e=1.0), **(st or {}))
    return CT.draw(x, y, k, st, t)


# ═════════════════════════ телефон крупно в руке (хук, s05, s11, петля) ═════════════════════════
PH_C = (540.0, 980.0)
PX0, PY0, PX1, PY1 = PR.phone_frame_rect(*PH_C, 1.0)        # экран 560×1000
BTN = (540.0, PY1 - 240.0)                                  # зелёная кнопка «Вызов»
BTN_R = 92.0
PH_BG = "#3b3552"


def handset(x, y, k=1.0, rot=0.0, col="#ffffff"):
    """Значок трубки (центр)."""
    pts = [(-40, -18), (-30, -30), (-14, -26), (-10, -10), (-18, -2), (-8, 14), (4, 22), (12, 16), (26, 18), (32, 32), (22, 42), (-4, 40),
           (-30, 18), (-42, -2)]
    return tf(blob(pts, col), x, y, k, rot)


def clinic_avatar(x, y, r):
    o = [shape(ellipse_pts(x, y, r, r, 28), "#ffffff", "", w=4, seed=5101)]
    a, b = r * .22, r * .62
    o.append(blob([(x - a, y - b), (x + a, y - b), (x + a, y - a), (x + b, y - a), (x + b, y + a), (x + a, y + a), (x + a, y + b), (x - a, y + b),
                   (x - a, y + a), (x - b, y + a), (x - b, y - a), (x - a, y - a)], "#e2574c"))
    return "".join(o)


def call_screen(t, t_press=None, t_end=None):
    """Экран вызова «Поликлиника»: до t_press — зелёная «Вызов», после — «идёт вызов 00:0N», волны, красная «сброс»."""
    def scr(x0, y0, x1, y1):
        g = lib.lin_grad([(0, "#3a4a7a", 1), (1, "#1d2448", 1)], 0, 0, 0, 1)
        o = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>']
        cx = (x0 + x1) / 2
        on = t_press is not None and t >= t_press
        if on:
            for j in range(3):
                ph = ((t - t_press) * 1.4 + j / 3) % 1.0
                o.append(f'<circle cx="{cx}" cy="{y0 + 260}" r="{110 + 170 * ph:.1f}" fill="none" stroke="#9fe0b0" stroke-width="6" '
                         f'opacity="{.7 * (1 - ph):.3f}"/>')
        o.append(clinic_avatar(cx, y0 + 260, 108))
        o.append(text("Поликлиника", cx, y0 + 462, 66, fill="#ffffff", stroke="#1d2448", sw=4))
        o.append(text("8 495 123 45 67", cx, y0 + 530, 40, fill="#c9d6ff", stroke="#1d2448", sw=1))
        if not on:
            o.append(shape(ellipse_pts(BTN[0], BTN[1], BTN_R, BTN_R, 28), "#3fb26a", "", w=5, seed=5110))
            o.append(handset(BTN[0], BTN[1] + 4, 1.25))
            o.append(text("Вызов", BTN[0], BTN[1] + BTN_R + 66, 46, fill="#ffffff", stroke="#1d2448", sw=2))
        else:
            sec = int(t - t_press) + 1
            o.append(text("идёт вызов", cx, y0 + 610, 44, fill="#9fe0b0", stroke="#1d2448", sw=1))
            o.append(text(f"00:0{min(sec, 9)}", cx, y0 + 690, 60, fill="#ffffff", stroke="#1d2448", sw=2))
            u = ease_out(ramp(t, t_press, .16))
            r = BTN_R * (.82 + .18 * u)
            o.append(shape(ellipse_pts(BTN[0], BTN[1], r, r, 28), lib.mix("#3fb26a", "#e2574c", u), "", w=5, seed=5111))
            o.append(handset(BTN[0], BTN[1] + 4, 1.25, 135 * u))
        return "".join(o)
    return scr


def phone_hand(t, screen, typing=0.0, shake_u=0.0, thumb_to=None, bg=PH_BG, thumb=True):
    """Телефон в руке крупно (экран — SVG screen(x0, y0, x1, y1)); большой палец тянется к thumb_to; рукав худи снизу."""
    cx, cy = PH_C
    o = [rect(-900, -1400, 2200, 2600, bg)]
    for j, (bx, by, br) in enumerate(((-120, 260, 160), (1180, 420, 210), (60, 1700, 190), (1120, 1600, 150))):
        o.append(blob(ellipse_pts(bx, by, br, br, 22), "#ffd9a0", .08 + .03 * math.sin(t * 2 + j)))
    o.append(PR.glow(cx, cy, 900, .35, "#8fb7ff"))
    o.append(PR.phone_frame(cx, cy, 1.0, 1.0, glow_=.4, seed=1))
    x0, y0, x1, y1 = PX0, PY0, PX1, PY1
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    o.append(f'<g clip-path="url(#{c})">{screen(x0, y0, x1, y1)}</g>')
    # ладонь снизу и рукав худи (горчичный)
    o.append(shape([(x1 + 40, y1 + 520), (x1 + 420, y1 + 380), (x1 + 640, y1 + 1200), (x0 + 100, y1 + 1200)], "#d9a441",
                   blob([(x1 + 40, y1 + 700), (x1 + 640, y1 + 600), (x1 + 640, y1 + 1200), (x0 + 100, y1 + 1200)], "#b9862c", .7), w=5, seed=5019))
    o.append(shape([(x0 - 70, y1 - 160), (x0 + 40, y1 + 40), (x1 + 20, y1 + 120), (x1 + 200, y1 + 560), (x0 + 60, y1 + 760), (x0 - 140, y1 + 600)],
                   "#ecc4a2", blob([(x0 - 70, y1 + 200), (x1 + 100, y1 + 300), (x1 + 160, y1 + 600), (x0 - 140, y1 + 600)], "#d9a984", .7), w=5,
                   seed=5020))
    if thumb:
        if thumb_to is not None:
            tx, ty = thumb_to
        else:
            tx = x0 + 160 + 200 * (.5 + .5 * math.sin(t * 9)) * typing
            ty = y1 - 70 - 40 * abs(math.sin(t * 22)) * typing
        o.append(shape(lib.band([(x1 + 110, y1 + 420), (tx + 30, ty + 40)], 120, 92), "#ecc4a2", "", w=5, seed=5021))
        o.append(shape(ellipse_pts(tx + 22, ty + 18, 30, 38, 14), "#f7ddd0", "", w=3, seed=5022))
    sx = 14 * shake_u * math.sin(t * 60)
    sy = 6 * shake_u * math.cos(t * 47)
    rot = 1.2 * shake_u * math.sin(t * 38)
    return f'<g transform="translate({sx:.2f} {sy:.2f}) rotate({rot:.2f} {cx} {cy + 600})">{"".join(o)}</g>'


THUMB_HOVER = (BTN[0] - 10, BTN[1] + 130)          # кончик пальца под кнопкой (точка thumb_to)


def thumb_hover(t, t0, dips=1.6, depth=70.0):
    """Палец зависает: тянется к кнопке и отдёргивается (dips раз в секунду), дрожит."""
    d = .5 - .5 * math.cos((t - t0) * 2 * math.pi * dips)
    tx = THUMB_HOVER[0] + 8 * math.sin(t * 41) + 20 * d
    ty = THUMB_HOVER[1] - depth * d + 6 * math.cos(t * 53)
    return tx, ty


HIT01 = stress(2, .4)                       # «звонкИ»: лапа кота жмёт «Вызов»
PAW_IN = .16


def paw(t, t_hit):
    """Лапа кота влетает справа сверху и жмёт кнопку к t_hit, прижимает и остаётся."""
    u = ramp(t, t_hit - PAW_IN, PAW_IN)
    if u <= 0:
        return ""
    e = ease_out(u, 2)
    tip0 = (1380.0, 600.0)
    tip = (tip0[0] + (BTN[0] + 18 - tip0[0]) * e, tip0[1] + (BTN[1] - 14 - tip0[1]) * e)
    press = bump(t, t_hit, .04, .12)
    tip = (tip[0] - 6 * press, tip[1] + 14 * press)
    base = (tip[0] + 430, tip[1] - 330)
    return people.cat_forearm(base, tip, k=3.2, claw=0.0, seed=3)


def frame_s01(t):
    """ХУК: телефон дрожит в руке, палец зависает над «Вызов» и отдёргивается; на «звонки» лапа кота влетает и жмёт — вызов пошёл."""
    t_press = HIT01
    if t < HIT01 - .3:
        thumb = thumb_hover(t, 0.0)
    else:
        u = ease_out(ramp(t, HIT01 - .3, .25))
        h = thumb_hover(HIT01 - .3, 0.0)
        thumb = (h[0] + 90 * u, h[1] + 170 * u)          # палец отдёргивается: лапа быстрее
    shake_u = 1.0 if t < HIT01 else .25
    o = [phone_hand(t, call_screen(t, t_press), shake_u=shake_u, thumb_to=thumb)]
    o.append(paw(t, HIT01))
    if t > HIT01:
        o.append(PR.tap_rings(BTN[0], BTN[1], ramp(t, HIT01, .35), 1.6, col="#FFD23F"))
        o.append(PR.sparkles(BTN[0], BTN[1], 2.0, bump(t, HIT01, .05, .4), t, seed=2, n=6, r=220))
    if t < HIT01:
        o.append(PR.sweat(PX1 + 150, PY1 + 160, 1.4, 20))
    dx, dy = shake(t, HIT01, 14)
    cx = 560 + 20 * math.sin(t * 1.3)
    cy = 1010 + 50 * ease_io(ramp(t, 0, T1("s01")))
    s = 1.04 + .06 * ease_io(ramp(t, 0, T1("s01")))
    v = f'<g transform="{lib.cam(cx + dx, cy + dy, s, 0)}">{"".join(o)}</g>'
    if NOCAM:
        return lib.svg(f'<rect width="1080" height="1920" fill="{PH_BG}"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT01, bg=PH_BG) + over(t))


def frame_s16(t):
    """Петля: кадр хука — телефон дрожит, палец над «Вызов»."""
    a, b = T0("s16"), T1("s16")
    import anim
    hc = anim.hook_cam(0.0, hit=HIT01)
    u = ease_io(ramp(t, a, b - a))
    o = [phone_hand(t, call_screen(t), shake_u=1.0, thumb_to=thumb_hover(t, a))]
    o.append(PR.sweat(PX1 + 150, PY1 + 160, 1.4, 20))
    s = 1.04 * (1 + (hc["zoom"] - 1) * u)
    return view("".join(o), 560, 1010, s, hc["rot"] * u, bg=PH_BG, t=t)


def frame_s05(t):
    """«Палец над кнопкой»: ближе к кнопке, большой палец дрожит и не жмёт, капля пота."""
    a, b = T0("s05"), T1("s05")
    o = [phone_hand(t, call_screen(t), shake_u=.7, thumb_to=thumb_hover(t, a, dips=2.2, depth=95))]
    o.append(PR.sweat(PX1 + 120, PY1 + 120, 1.6, 20 + 6 * math.sin(t * 9)))
    if t > W(17):
        o.append(PR.question_mark(BTN[0] + 250, BTN[1] - 260, 1.3 * pop(t, W(17), .25), 1.0, col="#FFD23F"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(17), 6)
    return view("".join(o), BTN[0] + 40 + dx, BTN[1] - 120 + dy, 1.55 + .15 * u, -2 + 3 * u, bg=PH_BG, t=t)


# ═════════════════════════ стол у окна, лист «5 ЗВОНКОВ» на стене ═════════════════════════
FL = 1300.0
WALL, WALL_SH, FLOOR_C = "#efe2c8", "#e3d2b2", "#cdb48c"
DESK_Y = FL - 300
CALLS = ("Поликлиника", "Сантехник", "Банк", "Страховая", "Бабушке")
LIST_C = (790.0, 590.0)


def call_list(x, y, k, t, strikes, pen_on=True):
    """Лист «5 ЗВОНКОВ» на кнопке (центр): пять строк; strikes — моменты, когда строку вычёркивает красный маркер (0.2 с)."""
    o = [blob(lib.rrect(-232, -282, 248, 302, 10), "#000000", .14)]
    o.append(shape(lib.rrect(-240, -290, 240, 290, 10), "#fffdf6", "", w=4.4, seed=7000))
    o.append(shape(ellipse_pts(0, -272, 14, 14, 10), "#e2574c", "", w=3, seed=7001))
    o.append(text("5 ЗВОНКОВ", 0, -198, 62, fill="#1d2448", stroke="#fffdf6", sw=2))
    o.append(line([(-200, -170), (200, -170)], 4, "#1d2448", taper=0, wmin=1, seed=7002))
    pen = None
    for j, s in enumerate(CALLS):
        yy = -100 + 88 * j
        o.append(shape(ellipse_pts(-188, yy - 16, 18, 18, 12), "#ffffff", "", w=3, seed=7010 + j))
        o.append(handset(-188, yy - 16, .32, 0, "#3fb26a"))
        o.append(plain(s, -150, yy, 50))
        ts = strikes[j] if j < len(strikes) else None
        if ts is not None and t >= ts:
            u = ease_io(ramp(t, ts, .2))
            wlen = 20 + 25.5 * len(s)
            xe = -160 + (wlen + 20) * u
            o.append(line([(-160, yy - 14), (-160 + (xe + 160) * .5, yy - 20), (xe, yy - 12)], 11, "#d8453a", taper=.1, wmin=.7, seed=7020 + j))
            if u < 1:
                pen = (xe, yy - 14)
    if pen is not None and pen_on:
        o.append(PR.red_marker(pen[0] + 70, pen[1] - 40, 1.5, -40))
    return tf("".join(o), x, y, k, -2)


def chair(x, y, k=1.0):
    o = [shape(lib.rrect(-100, -16, 110, 10, 6), "#a8774a", "", w=4, seed=1011)]
    o.append(shape([(-100, -16, 1), (-80, -16, 1), (-70, -330, 1), (-92, -330, 1)], "#a8774a", "", w=4, seed=1012))
    for s in (-1, 1):
        o.append(shape([(s * 80 - 9, 8, 1), (s * 80 + 9, 8, 1), (s * 86 + 9, 240, 1), (s * 86 - 9, 240, 1)], "#8a6038", "", w=3.4, seed=1013 + s))
    return tf("".join(o), x, y, k)


def mini_phone(x, y, k, rot=0.0, screen="#2f3a55", inner=""):
    """Телефон в руке (центр), экран 120×220 в своих координатах."""
    o = [shape(lib.rrect(-72, -128, 72, 128, 22), "#2a2d36", "", w=4, seed=9700)]
    o.append(shape(lib.rrect(-60, -112, 60, 112, 12), screen, inner, w=2.4, seed=9701))
    return tf("".join(o), x, y, k, rot)


def desk_room(t, strikes=(), mode="day", sun=0.0, list_on=True):
    o = [rect(-1400, -1400, 2600, FL, WALL)]
    for i in range(-12, 22):
        o.append(rect(i * 120, -1400, i * 120 + 46, FL, WALL_SH, .55))
    o.append(rect(-1400, FL, 2600, FL + 1400, FLOOR_C))
    o.append(line([(-1400, FL), (2600, FL)], 5, seed=11))
    o.append(PR.window(150, 700, 300, 420, mode=mode, t=t, seed=3, curtain=False))
    if sun > 0:
        o.append(PR.glow(150, 500, 420, .35 * sun, "#fff1b0"))
    if list_on:
        o.append(call_list(LIST_C[0], LIST_C[1], .62, t, strikes, pen_on=False))
    o.append(chair(320, FL - 240, 1.0))
    o.append(PR.desk(680, DESK_Y, w=660, depth=100, leg_h=260, seed=7))
    return o


DHIP = FL - 290


def dima_desk(t, expr="calm82", pose="sit_desk", arms=None, hands=None, head_add=0.0, lean=.1):
    feet = people.sit_kw(360, DHIP, .5)["feet"]
    kw = {}
    if arms:
        kw["arms"] = arms
    if hands:
        kw["hands"] = hands
    return people.dima82(360, DHIP, .5, expr, pose, t=t, feet=feet, lean_add=lean, head_add=head_add, **kw)


def dima_call(t, expr="proud82", head_add=0.0):
    """Дима за столом, телефон у уха (ближняя рука к виску, телефон закрывает ухо, лицо открыто)."""
    feet = people.sit_kw(360, DHIP, .5)["feet"]
    probe = people.dima82(360, DHIP, .5, expr, "sit_desk", t=t, feet=feet, lean_add=.1, head_add=head_add)
    tx, ty = probe["temple"]
    tgt = (tx - 70 * .5, ty + 150 * .5)
    arms = {"f": ("ang", 0.16, 0.16), "n": ("ik", tgt, 1)}
    hands = {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"dir": (.3, -1), "curl": (.7, .75, .8, .8), "thumb": .6}}
    f = people.dima82(360, DHIP, .5, expr, "sit_desk", t=t, feet=feet, lean_add=.1, head_add=head_add, arms=arms, hands=hands)
    hx, hy = f["head"]
    ph = mini_phone(tx - 34, ty + 18, .42, -14, screen="#1d2448")
    return f, ph


def frame_s02(t):
    """«Пять звонков я»: утро, Дима за столом смотрит на лист «5 ЗВОНКОВ» на стене, кот на столе; лист выскакивает на «звонков»."""
    a, b = T0("s02"), T1("s02")
    o = desk_room(t, mode="day", sun=1.0, list_on=False)
    k = .62 * pop(t, W(4) - .05, .22)
    if k > .01:
        o.append(call_list(LIST_C[0], LIST_C[1], k, t, (), pen_on=False))
    f = dima_desk(t, "sure82", head_add=-.15)
    o.append(f["svg"])
    o.append(mini_phone(600, DESK_Y - 70, .55, -70))
    o.append(cat(870, DESK_Y - 60, .42, t, dict(look=(-.2, -.9), smile=.6, tail=12 * math.sin(t * 3))))
    o.append(PR.sparkles(LIST_C[0], LIST_C[1], 1.6, bump(t, W(4), .05, .4), t, seed=5, n=5, r=230))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(4), 7)
    return view("".join(o), 640 + dx, 790 + dy, 1.3 + .06 * u, 0, t=t)


def frame_s03(t):
    """«закрыл за одно утро»: лист крупно, пять строк вычёркиваются красным маркером одна за другой; на «утро» — последняя."""
    a, b = T0("s03"), T1("s03")
    t5 = W(9)
    strikes = [a + .05 + j * (t5 - a - .05) / 4 for j in range(5)]
    o = [rect(-1400, -1400, 2600, 3000, WALL)]
    for i in range(-12, 22):
        o.append(rect(i * 120, -1400, i * 120 + 46, 3000, WALL_SH, .55))
    o.append(call_list(540, 1000, 1.45, t, strikes))
    o.append(PR.sparkles(540, 1000, 3.0, bump(t, t5 + .2, .05, .45), t, seed=6, n=6, r=430))
    dx, dy = 0.0, 0.0
    for ts in strikes:
        sx, sy = shake(t, ts + .18, 4)
        dx += sx
        dy += sy
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .06 * u, 1 - 2 * u, t=t)


# ═════════════════════════ s04: номер в заметке висит неделю ═════════════════════════
def tear_sheet(n, x, y, k=1.0, rot=0.0):
    o = [shape(lib.rrect(-200, -150, 200, 230, 8), "#fffdf6", "", w=4, seed=6000 + n % 5)]
    o.append(text(str(n), 0, 120, 230, fill="#1d2448" if n % 7 else "#d8453a", stroke="#fffdf6", sw=2))
    o.append(text("ноябрь", 0, -80, 44, fill="#6a6f7a", stroke="#fffdf6", sw=1))
    return tf("".join(o), x, y, k, rot)


def tear_calendar(x, y, t, times, first=14, k=1.0):
    """Отрывной календарь: красная шапка, стопка листов; листы слетают в моменты times (каждый уносит день)."""
    o = [shape(lib.rrect(-230, -290, 230, 260, 14), "#c9b28a", "", w=4, seed=6100)]
    o.append(shape(lib.rrect(-230, -290, 230, -180, 14), "#d8453a", "", w=4, seed=6101))
    for j in (-90, 90):
        o.append(shape(ellipse_pts(j, -290, 12, 18, 10), "#9aa0aa", "", w=3, seed=6102 + (j > 0)))
    n_off = sum(1 for q in times if t >= q)
    o.append(tear_sheet(first + n_off, 0, -10))
    for j, q in enumerate(times):
        u = (t - q) / .5
        if 0 <= u < 1:
            fx = (160 + 90 * (j % 3)) * u * (1 if j % 2 else -1)
            fy = -10 - 260 * u + 900 * u * u
            o.append(f'<g opacity="{1 - u:.3f}">{tear_sheet(first + j, fx, fy, 1 - .3 * u, (40 if j % 2 else -40) * u)}</g>')
    return tf("".join(o), x, y, k)


def note_screen(t, t_tag, web=0.0):
    def scr(x0, y0, x1, y1):
        o = [rect(x0, y0, x1, y1, "#fffbea")]
        o.append(rect(x0, y0, x1, y0 + 130, "#FFD23F"))
        o.append(plain("Заметка", x0 + 40, y0 + 88, 56, fill="#1d2448"))
        for j in range(8):
            o.append(line([(x0 + 30, y0 + 250 + 110 * j), (x1 - 30, y0 + 250 + 110 * j)], 2, "#eadfb8", taper=0, wmin=1, seed=5200 + j))
        o.append(plain("позвонить:", x0 + 40, y0 + 230, 48, fill="#6a6f7a"))
        o.append(plain("Поликлиника", x0 + 40, y0 + 340, 62))
        o.append(plain("8 495 123 45 67", x0 + 40, y0 + 440, 54, fill="#2f6fd1"))
        if t >= t_tag:
            s = pop(t, t_tag, .25)
            tag = (f'<rect x="-170" y="-62" width="340" height="104" rx="20" fill="#e2574c" stroke="#111" stroke-width="5"/>'
                   + text("7 ДНЕЙ", 0, 22, 66, fill="#ffffff", stroke="#111", sw=6))
            o.append(f'<g transform="translate({(x0 + x1) / 2:.1f} {y0 + 640:.1f}) rotate(-6) scale({s:.4f})">{tag}</g>')
        if web > .01:
            o.append(PR.cobweb(x1 - 10, y0 + 140, 1.6 * web, t=t, ang=135, span=90, L=200, seed=4))
            o.append(PR.cobweb(x0 + 10, y1 - 10, 1.3 * web, t=t, ang=-45, span=90, L=200, seed=5))
        return "".join(o)
    return scr


def frame_s04(t):
    """«Номер в заметке висит неделю»: телефон с заметкой «Поликлиника» и номером на столе; отрывной календарь на стене сбрасывает
    листы 14 → 21, по экрану растёт паутина; на «неделю» бирка «7 ДНЕЙ»."""
    a, b = T0("s04"), T1("s04")
    t_tag = W(14) + .12
    o = [rect(-1400, -1400, 2600, 1500, WALL)]
    for i in range(-12, 22):
        o.append(rect(i * 120, -1400, i * 120 + 46, 1500, WALL_SH, .55))
    times = [a + .1 + j * (W(14) - a - .1) / 7 for j in range(7)]
    o.append(tear_calendar(280, 820, t, times, k=.72))
    o.append(PR.desk(540, 1560, w=1500, depth=120, leg_h=300, seed=8))
    web = ramp(t, a + .2, W(14) - a)
    x0, y0, x1, y1 = PR.phone_frame_rect(760, 1060, .62)
    o.append(PR.phone_frame(760, 1060, .62, 1.0, glow_=.3, seed=2))
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    scr = note_screen(t, t_tag, web)
    o.append(f'<g clip-path="url(#{c})"><g transform="translate({x0} {y0}) scale({(x1 - x0) / 560:.4f}) translate({-PX0} {-PY0})">'
             f'{scr(PX0, PY0, PX1, PY1)}</g></g>')
    o.append(PR.sparkles(760, 1160, 1.6, bump(t, t_tag, .05, .4), t, seed=7, n=5, r=250))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_tag, 10)
    return view("".join(o), 560 + dx, 1000 + dy, .98 + .08 * u, 0, t=t)


# ═════════════════════════ s06: телефон экраном вниз ═════════════════════════
def frame_s06(t):
    """«и я опять кладу телефон»: Дима за столом держит телефон у лица, опускает и кладёт экраном вниз, вздыхает; кот смотрит."""
    a, b = T0("s06"), T1("s06")
    t_put = W(21) + .2
    u = ease_io(ramp(t, a + .15, t_put - a - .15))
    feet = people.sit_kw(360, DHIP, .5)["feet"]
    probe = people.dima82(360, DHIP, .5, "puzzled82", "sit_desk", t=t, feet=feet, lean_add=.1)
    hx, hy = probe["head"]
    up = (hx + 150, hy + 130)
    down = (600, DESK_Y - 30)
    tgt = (up[0] + (down[0] - up[0]) * u, up[1] + (down[1] - up[1]) * u)
    arms = {"f": ("ang", 0.16, 0.16), "n": ("ik", tgt, -1)}
    hands = {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"curl": (.6, .65, .7, .7), "thumb": .5}}
    sad = t > t_put + .1
    o = desk_room(t, strikes=(), mode="day", sun=.5)
    f = people.dima82(360, DHIP, .5, "squint82" if sad else "puzzled82", "sit_desk", t=t, feet=feet, lean_add=.1 + .12 * ramp(t, t_put, .3),
                      head_add=.1 * ramp(t, t_put, .3), arms=arms, hands=hands)
    o.append(f["svg"])
    if t < t_put:
        wx, wy = f["hold"]
        o.append(mini_phone(wx + 6, wy - 30, .5, -20 - 50 * u, screen="#3a4a7a", inner=clinic_avatar(0, -40, 30)))
    else:
        o.append(PR.phone_flat(610, DESK_Y - 40, .55, 0, face_down=True, seed=1))
        o.append(PR.dust_puff(610, DESK_Y - 30, .7, ramp(t, t_put, .5), seed=2))
    hx, hy = f["head"]
    if sad:
        o.append(PR.breath_wave(hx + 60, hx + 200, hy + 60, 10, t, w=5, col="#9aa0aa", n=1.2))
    o.append(cat(880, DESK_Y - 60, .42, t, dict(look=(-.9, -.1), perk=ramp(t, t_put, .2), tail=10 * math.sin(t * 3))))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_put, 9)
    return view("".join(o), 600 + dx, 960 + dy, 1.45 + .08 * uu, 0, t=t)


# ═════════════════════════ s07–s08: запись к врачу ═════════════════════════
MONTHS = (("НОЯБРЬ", 5), ("ДЕКАБРЬ", 0))


def month_grid(name, first_dow, ndays, t, blocked_t=None, free=None, free_t=None):
    """Месяц на карточке (центр 0,0; ширина 700): имя, дни недели, сетка; blocked_t — с этого момента клетки гаснут «нет мест»."""
    o = [text(name, 0, -300, 64, fill="#1d2448", stroke="#ffffff", sw=2)]
    for j, d in enumerate("ПВСЧПСВ"):
        o.append(plain(d, -300 + 100 * j, -210, 36, fill="#8a90a0", anchor="middle"))
    for n in range(1, ndays + 1):
        i = first_dow + n - 1
        cx, cy = -300 + 100 * (i % 7), -130 + 92 * (i // 7)
        col, tcol = "#eef2fa", "#1d2448"
        if blocked_t is not None and t >= blocked_t + .012 * n:
            col, tcol = "#e9e4e4", "#b9b0b0"
        if free == n and free_t is not None and t >= free_t:
            col, tcol = "#3fb26a", "#ffffff"
        o.append(shape(lib.rrect(cx - 40, cy - 38, cx + 40, cy + 38, 12), col, "", w=2.6, seed=8000 + n))
        o.append(plain(str(n), cx, cy + 14, 38, fill=tcol, anchor="middle"))
        if blocked_t is not None and t >= blocked_t + .012 * n:
            o.append(line([(cx - 26, cy - 24), (cx + 26, cy + 24)], 4, "#d8453a", taper=0, wmin=1, seed=8100 + n, op=.8))
    return "".join(o)


def booking_card(t, slide=0.0, blocked_t=None, stamp_t=None, free_t=None):
    o = [blob(lib.rrect(-380, -560, 400, 600), "#000000", .14)]
    o.append(shape(lib.rrect(-390, -570, 390, 570), "#ffffff", "", w=5, seed=8200))
    o.append(shape(lib.rrect(-390, -570, 390, -430), "#2f6fd1", "", w=5, seed=8201))
    o.append(text("ЗАПИСЬ К ВРАЧУ", 0, -478, 60, fill="#ffffff", stroke="#1d2448", sw=3))
    c = lib.clip_rect(-380, -420, 760, 980)
    g1 = f'<g transform="translate({-800 * slide:.1f} 60)">{month_grid("НОЯБРЬ", 5, 30, t, blocked_t)}</g>'
    g2 = f'<g transform="translate({800 - 800 * slide:.1f} 60)">{month_grid("ДЕКАБРЬ", 0, 31, t, blocked_t=None, free=22, free_t=free_t)}</g>'
    o.append(f'<g clip-path="url(#{c})">{g1}{g2 if slide > 0 else ""}</g>')
    for s in (-1, 1):
        o.append(line([(s * 300, -228), (s * 330, -240), (s * 300, -252)], 6, "#8a90a0", taper=0, wmin=1, seed=8210 + s))
    if stamp_t is not None and t >= stamp_t:
        u = clamp((t - stamp_t) / .12)
        s = 1.8 - .8 * ease_out(u)
        st = (f'<rect x="-250" y="-80" width="500" height="160" rx="16" fill="#ffffff" fill-opacity=".85" stroke="#d8453a" stroke-width="14"/>'
              + text("МЕСТ НЕТ", 0, 40, 100, fill="#d8453a", stroke="#d8453a", sw=.01))
        o.append(f'<g opacity="{(.4 + .6 * u) * (1 - slide):.3f}" transform="translate(0 200) rotate(-12) scale({s:.4f})">{st}</g>')
    return "".join(o)


def frame_s07(t):
    """«А запись к врачу»: карточка записи на ноябрь; на «врачу» клетки гаснут одна за другой и бьёт штамп «МЕСТ НЕТ»."""
    a, b = T0("s07"), T1("s07")
    t_bl = W(26) - .05
    o = [rect(-1400, -1400, 2600, 3200, "#dfe8f3")]
    o.append(tf(booking_card(t, 0.0, t_bl, W(26) + .05), 540, 960, 1.0, -1.5))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(26) + .05, 14)
    return view("".join(o), 540 + dx, 980 + dy, 1.02 + .07 * u, 0, bg="#dfe8f3", t=t)


def frame_s08(t):
    """«на следующий месяц»: лист ноября уезжает, декабрь, свободна одна дата 22; Дима внизу слева хватается за голову."""
    a, b = T0("s08"), T1("s08")
    slide = ease_io(ramp(t, a, .45))
    t_free = W(30)
    o = [rect(-1400, -1400, 2600, 3200, "#dfe8f3")]
    o.append(tf(booking_card(t, slide, a - 1.0, a - 1.0, t_free), 640, 860, .82, -1.5))
    if t > t_free:
        o.append(PR.sparkles(640 + (-300 + 100 * 0) * .82 + 82, 860 + (60 - 130 + 92 * 3) * .82, 1.0, bump(t, t_free, .05, .4), t, seed=8, n=4, r=90))
    k = .5
    hip = 1720 - (people.LEG_LEN - 12) * k - 6
    f = people.dima82(250, hip, k, "panic82", "d82_shrug", t=t, feet="stand", head_add=.05 * math.sin(t * 7))
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.sweat(hx - 60, hy - 40, 1.1, -20))
    o.append(rect(-1400, 1720, 2600, 3200, "#b9c6d6"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_free, 8)
    return view("".join(o), 560 + dx, 1000 + dy, .98 + .05 * u, 0, bg="#dfe8f3", t=t)


# ═════════════════════════ s09–s11: решение — первая фраза на бумажке ═════════════════════════
def slip(x, y, k, t, t0=None, dur=1.6, rot=-4, pen=True, blank=False):
    """Бумажка с фразой «Здравствуйте, / хочу записаться...»: пишется буква за буквой с t0 за dur; ручка в руке идёт за последней буквой."""
    L1, L2 = "Здравствуйте,", "хочу записаться..."
    o = [blob(lib.rrect(-322, -150, 338, 172), "#000000", .14)]
    o.append(shape(lib.rrect(-330, -160, 330, 160, 8), "#fffdf6", "", w=4.2, seed=8300))
    for j in range(3):
        o.append(line([(-300, -60 + 92 * j), (300, -60 + 92 * j)], 2, "#d7e3f1", taper=0, wmin=1, seed=8301 + j))
    n_all = len(L1) + len(L2)
    n = n_all if t0 is None else int(n_all * clamp((t - t0) / dur))
    if blank:
        n = 0
    s1, s2 = L1[:min(n, len(L1))], L2[:max(0, n - len(L1))]
    size = 58
    o.append(plain(s1, -290, -72, size, fill="#1d2448"))
    o.append(plain(s2, -290, 22, size, fill="#1d2448"))
    tip = None
    if t0 is not None and 0 < n < n_all and pen:
        if n <= len(L1):
            tip = (-290 + big_title.text_w(s1, size), -80)
        else:
            tip = (-290 + big_title.text_w(s2, size), 14)
        tip = (tip[0] + 4 * math.sin(t * 40), tip[1] + 5 * math.cos(t * 33))
    if tip is not None:
        px, py = tip
        hand = shape([(px + 20, py + 10), (px + 120, py - 30), (px + 330, py + 60), (px + 420, py + 300), (px + 160, py + 330), (px + 60, py + 140)],
                     "#ecc4a2", blob([(px + 160, py + 120), (px + 420, py + 300), (px + 160, py + 330)], "#d9a984", .7), w=4.4, seed=8310)
        sleeve = shape([(px + 300, py + 130), (px + 520, py + 60), (px + 760, py + 520), (px + 420, py + 640)], "#d9a441", "", w=4.4, seed=8311)
        o.append(sleeve)
        o.append(PR.pen(px + 52, py - 70, 1.15, rot=-30))
        o.append(hand)
    return tf("".join(o), x, y, k, rot)


def frame_s09(t):
    """«Вот что я поменял»: Дима за столом, над ним загорается лампочка, перед ним на столе чистая бумажка, кот садится рядом;
    маленькая надпись «ВОТ ЧТО Я ПОМЕНЯЛ»."""
    a, b = T0("s09"), T1("s09")
    t_idea = W(31) + .15
    o = desk_room(t, mode="day", sun=.6)
    f = dima_desk(t, "wow82" if t > t_idea else "sure82", head_add=.08 * bump(t, t_idea, .08, .3) - .1)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(tf(shape(lib.rrect(-80, -26, 80, 26, 4), "#fffdf6", "", w=3, seed=8320), 620, DESK_Y - 60, 1.0, -4))
    o.append(PR.pen(700, DESK_Y - 66, .6, rot=-80))
    if t > t_idea:
        o.append(PR.glow(hx, hy - 220, 200, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx, hy - 220 + 6 * math.sin(t * 5), .8 * pop(t, t_idea, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx, hy - 220, 1.4, bump(t, t_idea, .05, .5), t, seed=41, n=5, r=160))
    walk = ease_out(ramp(t, W(34) - .3, .35))
    o.append(cat(1000 - 140 * walk, DESK_Y - 60, .42, t, dict(look=(-.8, -.5), smile=.8, walk=(t * 3) if 0 < walk < 1 else None,
                                                          tail=12 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_idea, 9)
    return view("".join(o), 620 + dx, 940 + dy, 1.38 + .1 * u, -1 + 2 * u, t=t)


DESK_TOP = "#c9a77c"


def desk_top_bg():
    o = [rect(-1400, -1400, 2600, 3200, DESK_TOP)]
    for j in range(16):
        o.append(line([(-1400, -200 + 200 * j), (2600, -200 + 200 * j + 40)], 3, "#b08d64", taper=0, wmin=1, seed=6400 + j, op=.7))
    return "".join(o)


def frame_s10(t):
    """«Пишу первую фразу на бумажке»: бумажка крупно сверху, рука ручкой пишет «Здравствуйте, хочу записаться...»."""
    a, b = T0("s10"), T1("s10")
    o = [desk_top_bg()]
    o.append(PR.mug(170, 560, 1.1) if hasattr(PR, "mug") else "")
    o.append(slip(520, 960, 1.35, t, t0=W(35) + .05, dur=W(39) + .35 - W(35)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(39) + .4, 5)
    return view("".join(o), 560 + dx, 1040 + dy, 1.0 + .06 * u, -1 + 2 * u, bg=DESK_TOP, t=t)


def frame_s11(t):
    """«и звоню, не перечитывая»: бумажка на столе вверх ногами (не перечитываю), палец сразу жмёт «Вызов» — вызов пошёл."""
    a, b = T0("s11"), T1("s11")
    t_press = W(41) + .02
    rest = (THUMB_HOVER[0] + 160, THUMB_HOVER[1] + 220)
    tgt = (BTN[0] - 22, BTN[1] - 18)
    reach = ease_io(ramp(t, a, t_press - a)) * (1 - ease_io(ramp(t, t_press + .15, .3)))
    thumb = (rest[0] + (tgt[0] - rest[0]) * reach, rest[1] + (tgt[1] - rest[1]) * reach)
    flip = ease_io(ramp(t, W(42), .3))
    body = phone_hand(t, call_screen(t, t_press), thumb_to=thumb, bg=DESK_TOP)
    sy = abs(1 - 2 * flip)
    sl = f'<g transform="translate(540 250) scale(.85 {.85 * max(sy, .02):.3f})">{slip(0, 0, 1.0, t, rot=3, blank=flip > .5)}</g>'
    o = [desk_top_bg(), sl, body.replace(rect(-900, -1400, 2200, 2600, DESK_TOP), "", 1)]
    if t > t_press:
        o.append(PR.tap_rings(BTN[0], BTN[1], ramp(t, t_press, .3), 1.4, col="#FFD23F"))
        o.append(PR.sparkles(BTN[0], BTN[1], 1.8, bump(t, t_press, .05, .4), t, seed=9, n=5, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_press, 9)
    return view("".join(o), 540 + dx, 1000 + dy, .78 + .05 * u, 2 - 3 * u, bg=DESK_TOP, t=t)


# ═════════════════════════ s12: призыв «КОТ» ═════════════════════════
PAPER = "#f6efdf"


def paper_bg():
    return rect(-2000, -2000, 3500, 4000, PAPER) + "".join(
        line([(-1200, 200 + 90 * j), (2600, 200 + 90 * j)], 2, "#e3d6bb", taper=0, wmin=1, seed=6000 + j) for j in range(24))


def frame_s12(t):
    """«Напиши слово «КОТ»»: на бумаге крупно печатается жёлтое «КОТ»; Дима внизу слева, кот прыгает и садится рядом с ним."""
    a, b = T0("s12"), T1("s12")
    t_k = W(46) - .05
    o = [paper_bg()]
    cb = pop(t, a + .02, .25)
    if cb > .01:
        box = (f'<rect x="-420" y="-200" width="840" height="400" rx="40" fill="#ffffff" stroke="#111" stroke-width="7"/>'
               + f'<path d="M-260 196 l-40 90 l120 -90 z" fill="#ffffff" stroke="#111" stroke-width="7" stroke-linejoin="round"/>'
               + f'<rect x="-416" y="150" width="832" height="40" fill="#ffffff"/>'
               + plain("комментарий", -370, -130, 40, fill="#9aa0aa"))
        if t < t_k and int(t * 3) % 2 == 0:
            box += rect(-6, -60, 6, 60, "#2f6fd1")
        o.append(tf(box, 540, 590, cb, -1.5))
    o.append(PR.glow(540, 700, 420, .5 * ramp(t, t_k + .2, .3), "#ffe9a8"))
    o.append(kot_print(t, t_k, 540, 680, 300))
    o.append(PR.sparkles(540, 600, 2.4, bump(t, t_k + .3, .05, .5), t, seed=91, n=6, r=380))
    k = .62
    hip = 1640 - (people.LEG_LEN - 12) * k - 6
    f = people.dima82(330, hip, k, "proud82", "d82_rest", t=t, feet="stand", head_add=.05 * math.sin(t * 3))
    o.append(f["svg"])
    t_j = W(47) - .05
    j = ease_io(ramp(t, t_j, .4))
    x = 1180 + (620 - 1180) * j
    y = 1640 - 260 * math.sin(math.pi * j)
    o.append(cat(x, y, .9, t, dict(look=(-.7, -.4), legs=1.0 - j if j < 1 else 0.0, smile=1.0 if j >= 1 else .4, tail=10 * math.sin(t * 3))))
    if j >= 1:
        o.append(PR.heart(480, 1060 - 30 * ramp(t, t_j + .4, .8), .6 * pop(t, t_j + .4, .25), beat=bump(t, t_j + .4, .05, .3)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_k + .25, 8)
    return view("".join(o), 540 + dx, 1020 + dy, 1.0 + .06 * u, 0, bg=PAPER, t=t)


def frame_s13(t):
    """«поменять это в своей жизни навсегда»: Дима за столом говорит по телефону, бумажка перед ним, улыбается; кот рядом мурчит,
    на «навсегда» сердечко."""
    a, b = T0("s13"), T1("s13")
    o = desk_room(t, strikes=[a - 2, a - 2, a - 2], mode="day", sun=.8)
    talk = .5 + .5 * math.sin(t * 13)
    f, ph = dima_call(t, "laugh82" if talk > .55 else "proud82", head_add=.03 * math.sin(t * 4))
    o.append(f["svg"])
    o.append(ph)
    o.append(tf(shape(lib.rrect(-80, -26, 80, 26, 4), "#fffdf6", line([(-60, -6), (50, -6)], 3, "#1d2448", taper=0, wmin=1, seed=8331)
                      + line([(-60, 10), (30, 10)], 3, "#1d2448", taper=0, wmin=1, seed=8332), w=3, seed=8330), 620, DESK_Y - 60, 1.0, -4))
    o.append(cat(820, DESK_Y - 60, .42, t, dict(look=(-.9, -.4), smile=1.0, blink=1.0 if abs(t - (a + .9)) < .07 else 0.0,
                                               tail=10 * math.sin(t * 2.5))))
    o.append(PR.purr(770, DESK_Y - 270, .9, t, ramp(t, W(53), .2), seed=1))
    hx, hy = f["head"]
    for j in range(2):
        ph_ = ((t - a) * 1.6 + j / 2) % 1.0
        o.append(f'<path d="M{hx - 120 - 30 * ph_:.1f} {hy - 40 - 30 * ph_:.1f} q-30 40 0 80" fill="none" stroke="#2f9a4a" stroke-width="5" '
                 f'stroke-linecap="round" opacity="{.8 * (1 - ph_):.3f}"/>')
    t_h = W(54) + .1
    if t > t_h:
        o.append(PR.heart(hx + 140, hy - 200 - 30 * ramp(t, t_h, .8), .55 * pop(t, t_h, .25), beat=bump(t, t_h, .05, .3)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_h, 6)
    return view("".join(o), 590 + dx, 900 + dy, 1.32 + .08 * u, 1 - 2 * u, t=t)


# ═════════════════════════ s14–s15: итог 9:15, «5 ИЗ 5» ═════════════════════════
def frame_s14(t):
    """«В девять пятнадцать»: настенные часы крупно, стрелки бегут к 9:15 и встают с отскоком на «пятнадцать»; цифры 9:15 под часами."""
    a, b = T0("s14"), T1("s14")
    t_set = W(57) + .1
    o = [rect(-1400, -1400, 2600, 3200, WALL)]
    for i in range(-12, 22):
        o.append(rect(i * 120, -1400, i * 120 + 46, 3200, WALL_SH, .55))
    o.append(PR.window(140, 1500, 340, 560, mode="day", t=t, seed=4, curtain=False))
    o.append(PR.glow(140, 1200, 520, .45, "#fff1b0"))
    u = ease_io(ramp(t, a, t_set - a))
    m = 6 + 9 * u
    if t > t_set:
        m = 15 + 1.2 * math.exp(-(t - t_set) * 8) * math.sin((t - t_set) * 40)
    ah, am = PR.clock_hm(9, m)
    o.append(PR.glow(540, 860, 520, .3 + .4 * bump(t, t_set, .05, .4), "#fff1b0"))
    o.append(PR.clock(540, 860, 330, ah, am, seed=1))
    if t > t_set - .05:
        s = pop(t, t_set - .05, .25)
        pl = (f'<rect x="-190" y="-80" width="380" height="140" rx="26" fill="#1d2448" stroke="#111" stroke-width="6"/>'
              + text("9:15", 0, 36, 108, fill="#9fe0b0", stroke="#1d2448", sw=2))
        o.append(f'<g transform="translate(540 1330) scale({s:.4f})">{pl}</g>')
        o.append(PR.sparkles(540, 860, 2.6, bump(t, t_set, .05, .45), t, seed=10, n=6, r=420))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_set, 9)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .07 * uu, -1 + 2 * uu, t=t)


def frame_s15(t):
    """«все пять вычеркнуты»: лист на стене, четыре строки уже вычеркнуты, пятая — на «вычеркнуты»; Дима откидывается и выдыхает,
    кот доволен; надпись «5 ИЗ 5»."""
    a, b = T0("s15"), T1("s15")
    t5 = W(60)
    strikes = [a - 3] * 4 + [t5 - .1]
    o = desk_room(t, strikes=(), mode="day", sun=1.0, list_on=False)
    o.append(call_list(LIST_C[0], LIST_C[1] + 20, .8, t, strikes))
    rel = ramp(t, t5, .3)
    f = dima_desk(t, "proud82" if rel > .5 else "calm82", head_add=-.12 - .1 * rel, lean=-.05 * rel)
    o.append(f["svg"])
    hx, hy = f["head"]
    if rel > 0:
        o.append(PR.breath_wave(hx + 60, hx + 220, hy + 50, 12, t, w=6, col="#7fbfe6", n=1.3))
    o.append(PR.phone_flat(610, DESK_Y - 40, .55, 0, face_down=False, seed=1))
    o.append(cat(930, DESK_Y - 60, .42, t, dict(look=(-.6, -.6), smile=1.0, proud=1.0, tail=16 * math.sin(t * 4))))
    o.append(PR.sparkles(LIST_C[0], LIST_C[1], 2.2, bump(t, t5 + .1, .05, .5), t, seed=12, n=6, r=280))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t5 + .1, 8)
    return view("".join(o), 650 + dx, 900 + dy, 1.25 + .06 * u, 0, t=t)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
