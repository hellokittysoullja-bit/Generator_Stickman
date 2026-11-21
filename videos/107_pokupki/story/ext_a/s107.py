"""Рилс 107 «Покупки на эмоциях», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу); числа в коде — длительности движений.
Говорит Дима от первого лица (имя не звучит и не пишется). Сквозные места: телефон крупно в руке (хук «Оплатить», корзина, банк,
петля), комната с горой коробок, прихожая (курьер), кухня (пустой холодильник), стол у окна (пауза, идея, утро).
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
import room as RM  # noqa: E402
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
    if t < T1("s11") - .01 or t > k["t_out"]:
        return ""
    return kot_print(t, -9.0, 300, 330, 140)


def over(t):
    return title(t) + plate(t, SH["label"]) + plate(t, SH["label2"], w=520, size=76) + kot_small(t)


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
            blur += (f'<use href="#hk107" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk107">{body}</g></g>{blur}'


def cat(x, y, k, t, st=None):
    st = dict(dict(look=(-.4, -.2), tail=8 * math.sin(t * 1.7), flame_e=1.0), **(st or {}))
    return CT.draw(x, y, k, st, t)


# ═════════════════════════ телефон крупно в руке (хук, s05, s11, петля) ═════════════════════════
PH_C = (540.0, 980.0)
PX0, PY0, PX1, PY1 = PR.phone_frame_rect(*PH_C, 1.0)        # экран 560×1000
BTN = (540.0, PY1 - 240.0)                                  # зелёная кнопка «Вызов»
BTN_R = 92.0
PH_BG = "#3b3552"

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

FL = 1300.0
WALL, WALL_SH, FLOOR_C = "#efe2c8", "#e3d2b2", "#cdb48c"
DESK_Y = FL - 300
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

PAPER = "#f6efdf"


def paper_bg():
    return rect(-2000, -2000, 3500, 4000, PAPER) + "".join(
        line([(-1200, 200 + 90 * j), (2600, 200 + 90 * j)], 2, "#e3d6bb", taper=0, wmin=1, seed=6000 + j) for j in range(24))



# ═════════════════════════ мессенджер: иконка, список чатов, чат ═════════════════════════


GREEN, RED, BLUE = "#3fb26a", "#e2453a", "#2f8fe0"


# ═════════════════════════ предметы ═════════════════════════
BOX_COLS = ("#d9a066", "#c98f55", "#e0ae74", "#cf9a5c")


def parcel(x, y, k=1.0, rot=0.0, seed=0):
    """Коробка с посылкой (центр): картон, тёмный бок, скотч, белая наклейка без букв."""
    c = BOX_COLS[seed % 4]
    o = [blob(lib.rrect(-118, -82, 128, 96, 8), "#000000", .18)]
    inner = (blob(lib.rect_pts(60, -90, 130, 100), lib.mul(c, (.82, .8, .78)), .9)
             + blob(lib.rect_pts(-130, -14, 130, 14), "#efd79a", .95)
             + blob(lib.rect_pts(-90, 30, -20, 70), "#ffffff", .95)
             + line([(-80, 44), (-30, 44)], 3, "#9aa0a6", taper=0, wmin=1, seed=11 + seed)
             + line([(-80, 58), (-44, 58)], 3, "#9aa0a6", taper=0, wmin=1, seed=12 + seed))
    o.append(shape(lib.rrect(-120, -90, 120, 90, 8), c, inner, w=4.4, seed=7100 + seed))
    return tf("".join(o), x, y, k, rot)


def sneaker(x, y, k=1.0, rot=0.0, col="#e2574c"):
    o = [shape([(-120, 30), (-110, -30), (-40, -40), (10, -70), (60, -64), (70, -10), (130, 0), (140, 40), (-120, 46)], col,
               blob([(-120, 26), (140, 30), (140, 46), (-120, 46)], "#ffffff"), w=4, seed=7201)]
    for j in range(3):
        o.append(line([(-10 + 18 * j, -52 + 6 * j), (20 + 18 * j, -40 + 6 * j)], 4, "#ffffff", taper=0, wmin=1, seed=7202 + j))
    return tf("".join(o), x, y, k, rot)


def headphones(x, y, k=1.0, rot=0.0, col="#5a7bd6"):
    o = [line([(-80, 10), (-80, -40), (-40, -86), (40, -86), (80, -40), (80, 10)], 14, "#2a2d36", taper=0, wmin=1, seed=7211)]
    for s in (-1, 1):
        o.append(shape(lib.rrect(s * 80 - 30, -10, s * 80 + 30, 70, 22), col, "", w=4, seed=7212 + s))
    return tf("".join(o), x, y, k, rot)


def gamepad(x, y, k=1.0, rot=0.0, col="#7a6ad6"):
    o = [shape([(-120, -30), (120, -30), (140, 40), (110, 70), (60, 40), (-60, 40), (-110, 70), (-140, 40)], col, "", w=4, seed=7221)]
    o.append(line([(-80, 0), (-40, 0)], 8, "#ffffff", taper=0, wmin=1, seed=7222))
    o.append(line([(-60, -20), (-60, 20)], 8, "#ffffff", taper=0, wmin=1, seed=7223))
    for j, (dx, dy) in enumerate(((60, -12), (86, 10))):
        o.append(shape(ellipse_pts(dx, dy, 12, 12, 10), "#FFD23F", "", w=2.4, seed=7224 + j))
    return tf("".join(o), x, y, k, rot)


def tshirt(x, y, k=1.0, rot=0.0, col="#3fb26a"):
    o = [shape([(-50, -80), (-120, -50), (-100, 0), (-70, -10), (-70, 90), (70, 90), (70, -10), (100, 0), (120, -50), (50, -80),
                (25, -60), (-25, -60)], col, "", w=4, seed=7231)]
    return tf("".join(o), x, y, k, rot)


def mug_item(x, y, k=1.0, rot=0.0, col="#f0a44a"):
    o = [shape(lib.rrect(-60, -70, 60, 70, 12), col, "", w=4, seed=7241)]
    o.append(line([(60, -30), (100, -20), (100, 30), (60, 40)], 10, INK, taper=0, wmin=1, seed=7242))
    return tf("".join(o), x, y, k, rot)


ITEMS = (sneaker, headphones, gamepad, tshirt, mug_item)


def cart_icon(x, y, k=1.0, col="#1d2448", fill="#ffffff"):
    """Тележка магазина (центр корзины)."""
    o = [line([(-170, -110), (-120, -110), (-80, 80), (120, 80)], 12, col, taper=0, wmin=1, seed=7301)]
    o.append(shape([(-110, -70, 1), (170, -70, 1), (140, 40, 1), (-86, 40, 1)], fill, "", w=6, seed=7302, ink_color=col))
    for j in range(3):
        o.append(line([(-60 + 70 * j, -66), (-46 + 64 * j, 36)], 5, col, taper=0, wmin=1, seed=7303 + j, op=.6))
    for dx in (-50, 100):
        o.append(shape(ellipse_pts(dx, 116, 22, 22, 12), col, "", w=3, seed=7310 + (dx > 0)))
    return tf("".join(o), x, y, k)


def pause_sign(x, y, k=1.0, rot=0.0):
    """Знак паузы: жёлтый круг с двумя тёмными полосами."""
    o = [blob(ellipse_pts(10, 14, 130, 130, 30), "#000000", .25)]
    o.append(shape(ellipse_pts(0, 0, 130, 130, 30), "#FFD23F", "", w=7, seed=7401))
    for s in (-1, 1):
        o.append(shape(lib.rrect(s * 38 - 20, -62, s * 38 + 20, 62, 8), "#1d2448", "", w=3, seed=7402 + s))
    return tf("".join(o), x, y, k, rot)


def big_button(x, y, k, label, col, pressed=0.0, w=420):
    hh = 70
    dy = 10 * pressed
    o = [blob(lib.rrect(-w / 2, -hh + 16, w / 2, hh + 16, 40), lib.mul(col, (.7, .7, .7)))]
    o.append(shape(lib.rrect(-w / 2, -hh + dy, w / 2, hh + dy, 40), col, "", w=6, seed=7410 + len(label)))
    o.append(text(label, 0, 26 + dy, 74, fill="#ffffff", stroke="#111", sw=6))
    return tf("".join(o), x, y, k)


def coin(x, y, k=1.0, rot=0.0):
    o = [shape(ellipse_pts(0, 0, 50, 50, 18), "#f2c14e", blob(ellipse_pts(8, 8, 36, 36, 14), "#e0a83a", .7), w=4, seed=7501)]
    o.append(text("₽", 0, 22, 62, fill="#fff3c2", stroke="#b8801c", sw=3))
    return tf("".join(o), x, y, k, rot)


# ═════════════════════════ экран магазина «Оплатить» (хук s01, петля s18) ═════════════════════════
PAY = (540.0, PY1 - 170.0)


def pay_screen(t, pressed=0.0, flash=0.0):
    def scr(x0, y0, x1, y1):
        cx = (x0 + x1) / 2
        o = [rect(x0, y0, x1, y1, "#ffffff")]
        o.append(rect(x0, y0, x1, y0 + 120, "#ff7a3d"))
        o.append(plain("Корзина", x0 + 40, y0 + 82, 54, fill="#ffffff"))
        for j, (fn, col) in enumerate(((sneaker, "#e2574c"), (headphones, "#5a7bd6"), (gamepad, "#7a6ad6"))):
            yy = y0 + 230 + 190 * j
            o.append(shape(lib.rrect(x0 + 30, yy - 80, x1 - 30, yy + 80, 22), "#f4f1ea", "", w=3, seed=7600 + j))
            o.append(fn(x0 + 140, yy, .62, 0, col))
            o.append(line([(x0 + 260, yy - 26), (x1 - 80, yy - 26)], 10, "#c9ced6", taper=0, wmin=1, seed=7610 + j))
            o.append(plain(("4 990 ₽", "3 490 ₽", "2 990 ₽")[j], x0 + 260, yy + 46, 48, fill="#1d2448"))
        o.append(plain("Итого: 11 470 ₽", cx, y1 - 300, 50, fill="#1d2448", anchor="middle"))
        o.append(big_button(PAY[0], PAY[1], 1.0, "Оплатить", GREEN, pressed, w=480))
        if flash > .01:
            o.append(rect(x0, y0, x1, y1, "#fff6c8", .85 * flash))
        return "".join(o)
    return scr


HIT01 = stress(0, .55)                       # «ПерестАнь»: палец жмёт «Оплатить»


def fly_boxes(t, t0, n=12, seed=5):
    """Коробки вылетают из экрана к камере (растут и разлетаются)."""
    o = []
    for j in range(n):
        ta = t0 + .045 * j
        u = (t - ta) / .55
        if not 0 < u < 1.3:
            continue
        ang = math.radians(j * 137.5 + seed)
        r = 80 + 900 * lib.ease_in(min(u, 1.2), 1.6)
        x = 540 + r * math.cos(ang)
        y = 900 + r * .9 * math.sin(ang) - 180 * u
        o.append(parcel(x, y, .25 + 1.5 * u, 40 * u * (1 if j % 2 else -1) + j * 17, seed=j))
    return "".join(o)


def frame_s01(t):
    """ХУК: телефон крупно, корзина на 11 470 ₽; палец жмёт «Оплатить»; экран вспыхивает, из него вылетают коробки в камеру."""
    pressed = bump(t, HIT01, .04, .2)
    reach = ease_io(ramp(t, -.05, HIT01 + .05))
    rest = (PAY[0] + 210, PAY[1] + 330)
    tgt = (PAY[0] - 30, PAY[1] - 20)
    thumb = (rest[0] + (tgt[0] - rest[0]) * reach, rest[1] + (tgt[1] - rest[1]) * reach)
    if t > HIT01 + .15:
        u = ease_io(ramp(t, HIT01 + .15, .3))
        thumb = (tgt[0] + (rest[0] - tgt[0]) * u, tgt[1] + (rest[1] - tgt[1]) * u)
    flash = bump(t, HIT01, .03, .25)
    o = [phone_hand(t, pay_screen(t, pressed, flash), shake_u=.25 + .8 * bump(t, HIT01, .03, .3), thumb_to=thumb)]
    if t > HIT01:
        o.append(PR.tap_rings(PAY[0], PAY[1], ramp(t, HIT01, .35), 1.8, col="#FFD23F"))
        o.append(PR.glow(540, 900, 600, .6 * flash, "#fff1b0"))
    o.append(fly_boxes(t, HIT01 + .02))
    dx, dy = shake(t, HIT01, 14)
    cx = 555 + 20 * math.sin(t * 1.3)
    cy = 1000 - 40 * ease_io(ramp(t, 0, T1("s01")))
    s = 1.18 + .1 * ease_io(ramp(t, 0, T1("s01")))
    v = f'<g transform="{lib.cam(cx + dx, cy + dy, s, 0)}">{"".join(o)}</g>'
    if NOCAM:
        return lib.svg(f'<rect width="1080" height="1920" fill="{PH_BG}"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT01, bg=PH_BG) + over(t))


def frame_s18(t):
    """Петля: кадр хука — телефон с корзиной, палец тянется к «Оплатить»."""
    a, b = T0("s18"), T1("s18")
    import anim
    hc = anim.hook_cam(0.0, hit=HIT01)
    u = ease_io(ramp(t, a, b - a))
    rest = (PAY[0] + 210, PAY[1] + 330)
    tgt = (PAY[0] - 30, PAY[1] - 20)
    r = .5 * u
    thumb = (rest[0] + (tgt[0] - rest[0]) * r, rest[1] + (tgt[1] - rest[1]) * r)
    o = [phone_hand(t, pay_screen(t), shake_u=.25, thumb_to=thumb)]
    s = 1.18 * (1 + (hc["zoom"] - 1) * u)
    return view("".join(o), 555, 1000, s, hc["rot"] * u, bg=PH_BG, t=t)


# ═════════════════════════ s02: гора коробок засыпает Диму ═════════════════════════
RFL = 1560.0


def plain_room(t, wall=WALL, floor=FLOOR_C, x0=-1400.0, x1=2600.0):
    o = [rect(x0, -1400, x1, RFL, wall)]
    for i in range(int(x0 // 120), int(x1 // 120) + 1):
        o.append(rect(i * 120, -1400, i * 120 + 46, RFL, WALL_SH, .55))
    o.append(rect(x0, RFL - 46, x1, RFL, "#d8c3a0"))
    o.append(line([(x0, RFL - 46), (x1, RFL - 46)], 3, seed=7))
    o.append(rect(x0, RFL, x1, RFL + 1400, floor))
    o.append(line([(x0, RFL), (x1, RFL)], 5, seed=11))
    return "".join(o)


# слоты горы: (x, y центра, поворот, время-смещение)
PILE = [(300, 1480, -4, .0), (560, 1490, 3, .05), (800, 1478, -2, .1), (420, 1320, 6, .14), (690, 1330, -5, .18),
        (180, 1330, 8, .22), (920, 1320, -7, .26), (300, 1170, -6, .3), (800, 1180, 5, .34), (560, 1200, 2, .38),
        (180, 1170, -3, .42), (930, 1160, 6, .46), (380, 1020, 4, .5), (720, 1030, -4, .54)]


def frame_s02(t):
    """«на эмоциях»: Дима в комнате с телефоном, сверху сыплются коробки и ложатся горой по пояс; на «эмоциях» кот выныривает
    из горы сверху, Дима в шоке."""
    a, b = T0("s02"), T1("s02")
    o = [plain_room(t)]
    o.append(PR.window(1000, 1020, 300, 400, mode="evening", t=t, seed=3, curtain=False))
    k = .66
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    t_cat = W(3) + .25
    f = people.dima82(560, hip, k, "panic82", "d82_shrug", t=t, feet="stand", head_add=.05 * math.sin(t * 9))
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.sweat(hx - 80, hy - 40, 1.2, -20))
    # кот выныривает между верхними коробками (до рисования верхнего ряда)
    cu = ease_out(ramp(t, t_cat, .25))
    if cu > 0:
        cy = 1010 - 60 * cu + 200 * (1 - cu)
        o.append(cat(870, cy, .62, t, dict(look=(-.8, -.6), smile=1.0, perk=1.0, tail=16 * math.sin(t * 6))))
    t_fall = a - .55
    land_all = []
    for j, (x, y, r, dt) in enumerate(PILE):
        ta = t_fall + dt * 1.6
        u = clamp((t - ta) / .3)
        if u <= 0:
            continue
        yy = y - (1 - u * u) * 1500
        sq = 1.0
        if u >= 1:
            sq = 1 - .08 * bump(t, ta + .3, .03, .12)
            land_all.append(ta + .3)
        o.append(tf(parcel(0, 0, 1.0, r, seed=j), x, yy, .95 * (1 if u < 1 else 1), 0) if sq == 1.0 else
                 f'<g transform="translate({x} {y + 90}) scale(1 {sq:.3f}) translate({-x} {-y - 90})">{parcel(x, y, .95, r, seed=j)}</g>')
    for j, ta in enumerate(land_all[-3:]):
        o.append(PR.dust_puff(PILE[len(land_all) - 3 + j][0] if len(land_all) >= 3 else 540, 1560, 1.0, ramp(t, ta, .5), seed=j))
    if t > t_cat + .1:
        o.append(PR.sparkles(870, 760, 1.6, bump(t, t_cat + .1, .05, .45), t, seed=21, n=5, r=180))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = 0.0, 0.0
    for ta in land_all:
        sx, sy = shake(t, ta, 6, .2)
        dx += sx
        dy += sy
    dx2, dy2 = shake(t, W(3), 14)
    return view("".join(o), 560 + dx + dx2, 1080 + dy + dy2, 1.1 + .08 * u, -1.5 + 2 * u, t=t)


# ═════════════════════════ s03: месяц на календаре; s04: +12 000 ₽ ═════════════════════════
def wall_calendar(x, y, t, t0, t1, k=1.0):
    o = [blob(lib.rrect(x - 300 + 12, y - 330 + 14, x + 300 + 12, y + 330 + 14, 20), "#000000", .15)]
    o.append(shape(lib.rrect(x - 300, y - 330, x + 300, y + 330, 20), "#fffdf6", "", w=5, seed=7700))
    o.append(shape(lib.rrect(x - 300, y - 330, x + 300, y - 210, 20), "#d8453a", "", w=5, seed=7701))
    o.append(text("НОЯБРЬ", x, y - 248, 64, fill="#ffffff", stroke="#a8302a", sw=3))
    n = 30
    for d in range(n):
        r, c = divmod(d, 7)
        cx, cy = x - 240 + 80 * c, y - 150 + 92 * r
        o.append(plain(str(d + 1), cx, cy + 16, 40, fill="#1d2448", anchor="middle"))
        ta = t0 + (t1 - t0) * d / n
        u = ramp(t, ta, .1)
        if u > 0:
            o.append(line([(cx - 26, cy - 22), (cx - 26 + 52 * u, cy - 22 + 52 * u)], 6, "#d8453a", taper=.3, wmin=.5, seed=7710 + d))
            if u >= 1:
                o.append(line([(cx + 26, cy - 22), (cx - 26, cy + 30)], 6, "#d8453a", taper=.3, wmin=.5, seed=7750 + d))
    return "".join(o)


def frame_s03(t):
    """«За месяц я сэкономил»: настенный календарь «НОЯБРЬ», дни зачёркиваются один за другим; Дима рядом поднимает палец, кот на полу."""
    a, b = T0("s03"), T1("s03")
    o = [plain_room(t)]
    o.append(wall_calendar(400, 760, t, a + .05, W(8) - .05))
    k = .66
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    f = people.dima82(820, hip, k, "proud82", "d82_one", t=t, feet="stand", flip=True, head_add=.05 * bump(t, W(7), .08, .3))
    o.append(f["svg"])
    o.append(cat(330, RFL + 30, .62, t, dict(look=(.6, -.6), smile=1.0, tail=16 * math.sin(t * 4))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(7), 7)
    return view("".join(o), 600 + dx, 1000 + dy, 1.0 + .08 * u, 1 - 2 * u, t=t)


def frame_s04(t):
    """«двенадцать тысяч»: на бумаге счётчик «+12 000 ₽» набегает и бьёт, монетки сыплются, кот подпрыгивает от радости."""
    a, b = T0("s04"), T1("s04")
    t_n = W(8) + .02
    o = [paper_bg()]
    o.append(PR.glow(540, 820, 520, .55 * ramp(t, t_n, .3), "#d9f5c0"))
    u = ease_out(ramp(t, t_n, .45))
    val = int(round(12000 * u / 100.0)) * 100
    s = f"+{val // 1000} {val % 1000:03d} ₽" if val >= 1000 else f"+{val} ₽"
    k = pop(t, t_n - .02, .25) * (1 + .08 * bump(t, W(9), .05, .25))
    if k > .01:
        o.append(tf(text(s, 0, 0, 190, fill="#3fb26a", stroke="#111", sw=14), 540, 880, k, -3))
    for j in range(10):
        ta = t_n + .1 + .06 * j
        cu = (t - ta) / .8
        if 0 < cu < 1.2:
            x = 540 + (j - 4.5) * 95 + 30 * math.sin(j * 2.1)
            y = 560 + 1000 * cu * cu - 200 * cu
            o.append(coin(x, y, .9, 200 * cu * (1 if j % 2 else -1)))
    o.append(PR.sparkles(540, 840, 2.6, bump(t, t_n + .05, .05, .55), t, seed=31, n=7, r=460))
    jmp = math.sin(math.pi * clamp((t - W(9)) / .45))
    o.append(cat(540, 1560 - 160 * max(0.0, jmp), .82, t, dict(look=(0, -.8), smile=1.0, legs=max(0.0, jmp), tail=20 * math.sin(t * 6))))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_n + .02, 12)
    return view("".join(o), 540 + dx, 1020 + dy, 1.0 + .06 * uu, 0, bg=PAPER, t=t)


# ═════════════════════════ s05: скучно на диване ═════════════════════════
def frame_s05(t):
    """«Раньше скучно»: вечер, Дима на диване зевает и листает телефон, кот спит рядом (Z)."""
    a, b = T0("s05"), T1("s05")
    sc = RM.sofa_scene(t, "evening")
    o = [sc["bg"], sc["sofa"]]
    hx0, hip = RM.SOFA_DIMA
    feet = people.sit_kw(hx0, hip, .5)["feet"]
    yawn = ramp(t, W(11) - .1, .15) * (1 - ramp(t, WE(11) + .25, .2))
    ex = {"brows": "tired", "mouth": "o", "open": .3 + .65 * yawn, "lid": .45 - .3 * yawn, "look": (.3, .4), "bags": True}
    f = people.dima82(hx0, hip, .5, ex, "d82_mug", t=t, feet=feet, head_add=-.06 - .1 * yawn)
    o.append(f["svg"])
    px, py = f["hold"]
    sc_y = -60 + ((t * 160) % 60)
    scr = rect(-60, -112, 60, 112, "#ffffff")
    for j in range(5):
        yy = -112 + j * 60 + sc_y
        scr += shape(lib.rrect(-50, yy, 50, yy + 46, 6), ("#ffcfb0", "#c9e0ff", "#d9f0c9", "#f6d0f0", "#fff0b0")[j], "", w=1.6, seed=7800 + j)
    o.append(mini_phone(px + 10, py - 40, .45, -8, inner=scr))
    o.append(sc["front"])
    o.append(cat(2440, RM.SOFA_SEAT + 10, .42, t, dict(sleep=1.0, tail=4 * math.sin(t * 1.5))))
    o.append(PR.z_mark(2470, RM.SOFA_SEAT - 160 - 30 * ((t * .8) % 1), .8, 1 - ((t * .8) % 1)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(11), 5)
    return view("".join(o), 2200 + dx, 1330 + dy, 1.55 + .12 * u, 0, t=t)


# ═════════════════════════ s06: корзина наполняется ═════════════════════════
def cart_screen(t, drops, base=7):
    """Экран «Корзина»: большая тележка, товары падают в неё сверху в моменты drops; на значке счётчик растёт."""
    def scr(x0, y0, x1, y1):
        cx = (x0 + x1) / 2
        o = [rect(x0, y0, x1, y1, "#fff8f0")]
        o.append(rect(x0, y0, x1, y0 + 120, "#ff7a3d"))
        o.append(plain("Корзина", x0 + 40, y0 + 82, 54, fill="#ffffff"))
        n = sum(1 for d in drops if t >= d + .25)
        cy = y0 + 640
        inside = []
        for j, d in enumerate(drops):
            u = clamp((t - d) / .25)
            if u <= 0:
                continue
            fn = ITEMS[j % len(ITEMS)]
            tx, ty = cx - 100 + 75 * (j % 4), cy - 110 - 50 * (j // 4)
            yy = y0 + 120 + (ty - y0 - 120) * u * u
            inside.append(fn(tx, yy, .8, 20 * (1 - u) + 12 * (j % 3 - 1)))
        o.append(cart_icon(cx, cy, 1.55))
        o.append("".join(inside))
        k = 1 + .25 * max((bump(t, d + .25, .04, .2) for d in drops), default=0)
        o.append(tf(shape(ellipse_pts(0, 0, 70, 70, 24), RED, "", w=4, seed=7820) + text(str(base + n), 0, 26, 76, fill="#ffffff", stroke=RED, sw=1),
                    cx + 230, cy - 200, k))
        return "".join(o)
    return scr


def frame_s06(t):
    """«и корзина полная»: телефон крупно, в тележку падают товары один за другим, счётчик на значке растёт 7 → 12."""
    a, b = T0("s06"), T1("s06")
    drops = [a + .02 + .17 * j for j in range(5)]
    tap = (PX1 - 40 + 20 * math.sin(t * 9), PY1 - 60 + 20 * abs(math.sin(t * 11)))
    o = [phone_hand(t, cart_screen(t, drops), thumb_to=tap)]
    u = ease_io(ramp(t, a, b - a))
    dx, dy = 0.0, 0.0
    for d in drops:
        sx, sy = shake(t, d + .25, 5, .15)
        dx += sx
        dy += sy
    return view("".join(o), 560 + dx, 980 + dy, 1.08 + .1 * u, -1 + 2 * u, bg=PH_BG, t=t)


# ═════════════════════════ s07–s08: прихожая, курьер ═════════════════════════
FL82 = RM.FL82
HK = .85
HHIP = FL82 - 598 * HK
HDOOR = RM.HALL82["door"]


def bell_rings(x, y, t, ta):
    u = ramp(t, ta, .5)
    if not 0 < u < 1:
        return ""
    o = []
    for j in range(3):
        r = 40 + 50 * j + 60 * u
        o.append(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="none" stroke="#FFD23F" stroke-width="8" opacity="{(1 - u) * (.9 - .25 * j):.3f}"/>')
    return "".join(o)


def frame_s07(t):
    """«Курьер»: прихожая, звонок в дверь (кольца у звонка), дверь распахивается, на пороге курьер с коробкой в руках."""
    a, b = T0("s07"), T1("s07")
    h = RM.hall82(t, "evening")
    t_ring, t_open = a + .05, W(16) - .1
    ajar = ease_out(ramp(t, t_open, .3))
    o = [h["bg"], h["door"](ajar)]
    bx, by = HDOOR[0] + 400, FL82 - 820
    o.append(shape(lib.rrect(bx - 34, by - 44, bx + 34, by + 44, 10), "#f6efd8", blob(ellipse_pts(bx, by, 16, 16, 10), "#e2574c"), w=3, seed=7900))
    o.append(bell_rings(bx, by, t, t_ring) + PR.glow(bx, by, 160, .6 * bump(t, t_ring, .05, .4), "#fff1b0"))
    o.append(bell_rings(bx, by, t, t_ring + .3))
    if ajar > .05:
        ck = HK * .95
        chip = FL82 - 598 * ck
        cf = people.townsman82("courier", HDOOR[0] - 20, chip, ck, "rest", t=t, expr="smile" if "smile" in people.EXPR["cour82"] else "calm",
                               feet="stand")
        o.append(f'<g opacity="{clamp(ajar * 2):.3f}">{cf["svg"]}</g>')
        hx, hy = cf["head"]
        o.append(f'<g opacity="{clamp(ajar * 2):.3f}">{parcel(hx + 30, hy + 380 * ck, .9 * ck / .85, -3, seed=1)}</g>')
    o.append(cat(560, FL82, .8, t, dict(look=(.9, -.4), perk=1.0, tail=20 * math.sin(t * 6))))
    dx, dy = shake(t, t_ring, 9)
    dx2, dy2 = shake(t, t_open + .1, 7)
    push = ease_io(ramp(t, a, b - a))
    return view("".join(o), HDOOR[0] - 40 + 40 * push + dx + dx2, 1000 + dy + dy2, 1.0 + .12 * push, 0, t=t)


def frame_s08(t):
    """«а я уже забыл, что заказал»: Дима держит коробку и не понимает, что в ней; над ним «?»; кот обнюхивает коробку."""
    a, b = T0("s08"), T1("s08")
    h = RM.hall82(t, "evening")
    o = [h["bg"], h["door"](0.0)]
    t_q = W(19) + .05
    f = people.dima82(620, HHIP, HK, "puzzled82" if t > t_q - .2 else "calm82", "d82_hold", t=t, feet="stand",
                      head_add=.06 * math.sin(t * 4) - .04)
    hx_, hy_ = f["hold"]
    o.append(f["svg"])
    o.append(parcel(hx_ - 10, hy_ - 20, .95, -4 + 4 * math.sin(t * 3), seed=2))
    hx, hy = f["head"]
    if t > t_q:
        o.append(PR.question_mark(hx + 40, hy - 270, 2.2 * pop(t, t_q, .25), 1.0, col="#e2574c"))
        o.append(PR.question_mark(hx - 160, hy - 200, 1.2 * pop(t, t_q + .25, .25), 1.0, col="#e2574c", seed=2))
    sniff = ramp(t, W(21) - .1, .2)
    o.append(cat(980, FL82, .8, t, dict(look=(-.9, -.8), perk=.5 + .5 * sniff, paw_l=bump(t, W(21), .1, .3), tail=12 * math.sin(t * 4))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_q, 9)
    return view("".join(o), 700 + dx, 900 + dy, 1.0 + .1 * u, 1 - 2 * u, t=t)


# ═════════════════════════ s09: пустой холодильник ═════════════════════════
def fridge(x, y, u, t):
    """Холодильник (x, y — центр низа), дверь на петлях слева открывается к нам на u; внутри пусто, лампочка, одна муха.
    На двери магнит-листок «30»."""
    w, h = 300, 1000
    o = [blob(ellipse_pts(x + 10, y + 6, 330, 20, 16), "#000000", .18)]
    inner = ""
    if u > .01:
        g = lib.lin_grad([(0, "#e6f3ff", 1), (1, "#b9d6ec", 1)], 0, 0, 0, 1)
        inner += f'<rect x="{x - w + 24}" y="{y - h + 24}" width="{2 * w - 48}" height="{h - 48}" fill="url(#{g})"/>'
        for j in range(3):
            yy = y - h + 280 + 230 * j
            inner += line([(x - w + 30, yy), (x + w - 30, yy)], 6, "#9fb8cc", taper=0, wmin=1, seed=7950 + j)
        inner += PR.glow(x, y - h + 120, 260, .8 * u, "#ffffff")
        inner += shape(ellipse_pts(x, y - h + 90, 30, 22, 12), "#fffbe0", "", w=3, seed=7955)
        fx = x + 60 * math.sin(t * 7)
        fy = y - h + 420 + 40 * math.sin(t * 11)
        inner += blob(ellipse_pts(fx, fy, 22, 16, 10), INK) + blob(ellipse_pts(fx - 16, fy - 18, 18, 10, 8), "#ffffff", .9) \
            + blob(ellipse_pts(fx + 16, fy - 18, 18, 10, 8), "#ffffff", .9)
    o.append(shape(lib.rrect(x - w, y - h, x + w, y, 30), "#f4f6f8", inner, w=5, seed=7960))
    leaf = shape(lib.rrect(-w, -h, w, 0, 30), "#fbfcfd", blob(lib.rect_pts(w - 40, -h, w, 0), "#d9dee4", .8)
                 + line([(-w + 10, -h + 340), (w - 10, -h + 340)], 4, "#c9ced6", taper=0, wmin=1, seed=7961), w=5, seed=7962)
    leaf += shape(lib.rrect(w - 70, -h + 380, w - 44, -h + 640, 10), "#c9ced6", "", w=3, seed=7963)
    leaf += shape(lib.rrect(-160, -h + 100, 40, -h + 300, 6), "#fffdf6", text("30", -60, -h + 250, 120, fill="#d8453a", stroke="#fffdf6", sw=1),
                  w=3, seed=7964)
    leaf += shape(ellipse_pts(-60, -h + 104, 16, 16, 10), RED, "", w=2, seed=7965)
    sx = 1 - 1.75 * ease_io(clamp(u))
    o.append(f'<g transform="translate({x - w} {y}) scale({sx:.4f} 1) translate({w} 0)">{leaf}'
             + (f'<rect x="{-w}" y="{-h}" width="{2 * w}" height="{h}" fill="#000" opacity="{.3 * u:.3f}"/>' if u > .01 else "") + "</g>")
    return "".join(o)


def frame_s09(t):
    """«Конец месяца»: кухня, Дима открывает холодильник (на двери листок «30»), внутри пусто, лампочка и муха; Дима грустнеет."""
    a, b = T0("s09"), T1("s09")
    o = [plain_room(t, wall="#dfe8e0", floor="#b9b2a4")]
    for i in range(-10, 22):
        for j in range(4):
            o.append(line([(i * 110, 860 + 100 * j), (i * 110 + 110, 860 + 100 * j)], 2, "#c4d2c6", taper=0, wmin=1, seed=8000 + j, op=.7))
    t_open = W(23) - .05
    u = ease_out(ramp(t, t_open, .35))
    o.append(fridge(560, RFL, u, t))
    k = .66
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    sad = ramp(t, W(24) + .2, .2)
    ex = "wow82" if sad < .5 else {"brows": "worry", "mouth": "frown", "lid": .8, "look": (-.7, .1)}
    f = people.dima82(1010, hip, k, ex, "d82_rest", t=t, feet="stand", flip=True, head_add=-.06 * sad)
    o.append(f["svg"])
    hx, hy = f["head"]
    if sad > .5:
        o.append(PR.sweat(hx + 70, hy - 30, 1.1, 20))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_open + .2, 8)
    return view("".join(o), 610 + dx, 1080 + dy, 1.0 + .1 * uu, 0, t=t)


# ═════════════════════════ s10: банк, 37 ₽ ═════════════════════════
def bank_screen(t, t_hit):
    def scr(x0, y0, x1, y1):
        cx = (x0 + x1) / 2
        o = [rect(x0, y0, x1, y1, "#f2f4f8")]
        o.append(rect(x0, y0, x1, y0 + 120, "#2e8b57"))
        o.append(plain("Банк", x0 + 40, y0 + 82, 54, fill="#ffffff"))
        o.append(shape(lib.rrect(x0 + 30, y0 + 170, x1 - 30, y0 + 560, 30), "#ffffff", "", w=4, seed=8100))
        o.append(plain("Баланс", cx, y0 + 270, 50, fill="#6a6f7a", anchor="middle"))
        k = 1 + .18 * bump(t, t_hit, .05, .3)
        col = lib.mix("#1d2448", "#e2453a", ramp(t, t_hit - .1, .1))
        o.append(tf(text("37 ₽", 0, 0, 170, fill=col, stroke="#ffffff", sw=2), cx, y0 + 470, k))
        for j, (nm, val) in enumerate((("Доставка", "−1 290 ₽"), ("Магазин", "−2 490 ₽"), ("Доставка", "−990 ₽"), ("Магазин", "−3 490 ₽"))):
            yy = y0 + 660 + 100 * j
            o.append(plain(nm, x0 + 50, yy, 44, fill="#1d2448"))
            o.append(plain(val, x1 - 50, yy, 44, fill="#e2453a", anchor="end"))
        return "".join(o)
    return scr


def frame_s10(t):
    """«на еду не хватает»: телефон крупно, банк: баланс «37 ₽» краснеет и бьёт, ниже списания доставок; рука дрожит."""
    a, b = T0("s10"), T1("s10")
    t_hit = W(27) + .02
    o = [phone_hand(t, bank_screen(t, t_hit), shake_u=.3 + .7 * ramp(t, t_hit, .1), thumb_to=(PX1 + 40, PY1 + 40))]
    if t > t_hit:
        o.append(PR.sweat(PX1 + 40, PY0 + 200, 1.6, 20))
        o.append(PR.sparkles(540, PY0 + 470, 2.0, bump(t, t_hit, .05, .4), t, seed=33, n=5, r=300, col="#e2453a"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_hit, 14)
    return view("".join(o), 545 + dx, 880 + dy + 60 * u, 1.18 + .1 * u, 1 - 2 * u, bg=PH_BG, t=t)


# ═════════════════════════ s11: призыв «КОТ» ═════════════════════════
def frame_s11(t):
    """«Напиши «КОТ»»: поле комментария, крупно печатается жёлтое «КОТ»; Дима внизу слева, кот прыгает и садится рядом с ним."""
    a, b = T0("s11"), T1("s11")
    t_k = W(30) - .05
    o = [paper_bg()]
    cb = pop(t, a + .02, .22)
    if cb > .01:
        box = (f'<rect x="-420" y="-200" width="840" height="400" rx="40" fill="#ffffff" stroke="#111" stroke-width="7"/>'
               + f'<path d="M-260 196 l-40 90 l120 -90 z" fill="#ffffff" stroke="#111" stroke-width="7" stroke-linejoin="round"/>'
               + f'<rect x="-416" y="150" width="832" height="40" fill="#ffffff"/>'
               + plain("комментарий", -370, -130, 40, fill="#9aa0aa"))
        if t < t_k and int(t * 6) % 2 == 0:
            box += rect(-6, -60, 6, 60, "#2f6fd1")
        o.append(tf(box, 540, 590, cb, -1.5))
    o.append(PR.glow(540, 700, 420, .5 * ramp(t, t_k + .2, .3), "#ffe9a8"))
    o.append(kot_print(t, t_k, 540, 680, 300))
    o.append(PR.sparkles(540, 600, 2.4, bump(t, t_k + .3, .05, .5), t, seed=91, n=6, r=380))
    k = .62
    hip = 1640 - (people.LEG_LEN - 12) * k - 6
    f = people.dima82(330, hip, k, "proud82", "d82_rest", t=t, feet="stand", head_add=.05 * math.sin(t * 3))
    o.append(f["svg"])
    t_j = W(31) - .12
    j = ease_io(ramp(t, t_j, .4))
    x = 1180 + (620 - 1180) * j
    y = 1640 - 260 * math.sin(math.pi * j)
    o.append(cat(x, y, .9, t, dict(look=(-.7, -.4), legs=1.0 - j if j < 1 else 0.0, smile=1.0 if j >= 1 else .4, tail=10 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_k + .25, 8)
    return view("".join(o), 540 + dx, 1020 + dy, 1.0 + .06 * u, 0, bg=PAPER, t=t)


# ═════════════════════════ s12: пауза между «хочу» и «оплатить» ═════════════════════════
def frame_s12(t):
    """«между „хочу“ и „оплатить“ появилась пауза»: кнопки «ХОЧУ» (сверху) и «ОПЛАТИТЬ» (снизу) выскакивают вплотную; на «появилась»
    разъезжаются; на «пауза» кот справа лапой вдвигает между ними жёлтый знак паузы, кнопки вздрагивают."""
    a, b = T0("s12"), T1("s12")
    o = [paper_bg()]
    t_p = W(37)
    gap = ease_io(ramp(t, W(36), .35))
    yc = 1000
    ty, by = yc - 140 - 170 * gap, yc + 140 + 170 * gap
    kb = 1 - .06 * bump(t, t_p + .05, .04, .2)
    if t > W(33) - .05:
        k = pop(t, W(33) - .05, .22)
        o.append(tf(big_button(0, 0, 1.0, "ХОЧУ", "#ff7a3d", w=560), 540 + 8 * math.sin(t * 3), ty, 1.05 * k * kb, -3))
    if t > W(35) - .05:
        k = pop(t, W(35) - .05, .22)
        o.append(tf(big_button(0, 0, 1.0, "ОПЛАТИТЬ", GREEN, w=600), 540 + 8 * math.sin(t * 3 + 1), by, 1.05 * k * kb, 3))
    if gap > .05:
        for s in (-1, 1):
            o.append(line([(540 + 40 * s, yc - 120 * gap), (540 + 40 * s, yc + 120 * gap)], 6, "#9aa0a6", taper=.4, wmin=.5, seed=8200 + s, op=gap))
    lift = ease_out(ramp(t, t_p - .3, .3))
    paw = lift * (1 - ease_io(ramp(t, t_p + .35, .3)))
    sx, sy = 860 + (540 - 860) * lift, 1500 + (yc - 1500) * lift
    o.append(cat(880, 1720, .9, t, dict(look=(-.6, -.9), paw=paw, paw_dx=-40, smile=.4 + .6 * ramp(t, t_p, .2), perk=1.0,
                                       tail=12 * math.sin(t * 3))))
    if lift > 0:
        o.append(pause_sign(sx, sy, .5 + .6 * lift + .1 * bump(t, t_p, .04, .25), 10 * (1 - lift)))
        if t > t_p:
            o.append(PR.tap_rings(sx, sy, ramp(t, t_p, .35), 2.2, col="#FFD23F"))
            o.append(PR.sparkles(sx, sy, 2.2, bump(t, t_p, .05, .5), t, seed=41, n=6, r=280))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_p, 12)
    return view("".join(o), 560 + dx, 1080 + dy, .98 + .06 * u, 0, bg=PAPER, t=t)


# ═════════════════════════ s13, s14, s17: стол у окна ═════════════════════════
def phone_scr_pause(t, ta):
    scr = rect(-60, -112, 60, 112, "#ffffff") + rect(-60, -112, 60, -70, "#ff7a3d")
    k = pop(t, ta, .25)
    if k > .01:
        scr += pause_sign(0, 10, .38 * k)
    else:
        scr += shape(lib.rrect(-44, 40, 44, 80, 10), GREEN, "", w=2, seed=8301)
    return scr


def frame_s13(t):
    """«которую ты сам себе поставишь»: Дима за столом сам жмёт паузу в телефоне — на экране выскакивает знак паузы, над телефоном
    кольца; кот на столе кивает."""
    a, b = T0("s13"), T1("s13")
    t_p = W(40) + .05
    o = desk_room(t, mode="day", sun=.5, list_on=False)
    f = dima_desk(t, "proud82" if t > t_p + .1 else "sure82", head_add=-.08)
    o.append(f["svg"])
    wx, wy = f["hold"]
    px, py = wx + 10, wy - 50
    o.append(mini_phone(px, py, .62, -10, inner=phone_scr_pause(t, t_p)))
    if t > t_p:
        o.append(PR.tap_rings(px, py, ramp(t, t_p, .35), 1.0, col="#FFD23F"))
        o.append(PR.sparkles(px, py - 30, 1.4, bump(t, t_p, .05, .5), t, seed=43, n=5, r=150))
    nod = .5 + .5 * math.sin((t - W(42)) * 14) if W(42) < t < W(42) + .5 else 0.0
    o.append(cat(940, DESK_Y - 60, .42, t, dict(look=(-.8, -.4), smile=1.0, tilt=8 * nod, tail=14 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_p, 8)
    return view("".join(o), 620 + dx, 940 + dy, 1.35 + .12 * u, 1 - 2 * u, t=t)


def frame_s14(t):
    """«Вот что я поменял»: Дима за столом, над ним загорается лампочка, кот подходит и садится рядом; надпись «ВОТ ЧТО Я ПОМЕНЯЛ»."""
    a, b = T0("s14"), T1("s14")
    t_idea = W(43) + .15
    o = desk_room(t, mode="day", sun=.6, list_on=False)
    f = dima_desk(t, "wow82" if t > t_idea else "sure82", head_add=.08 * bump(t, t_idea, .08, .3) - .1)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.phone_flat(640, DESK_Y - 40, .55, 0, face_down=False, seed=1))
    if t > t_idea:
        o.append(PR.glow(hx, hy - 220, 200, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx, hy - 220 + 6 * math.sin(t * 5), .8 * pop(t, t_idea, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx, hy - 220, 1.4, bump(t, t_idea, .05, .5), t, seed=41, n=5, r=160))
    walk = ease_out(ramp(t, W(46) - .3, .35))
    o.append(cat(1000 - 140 * walk, DESK_Y - 60, .42, t, dict(look=(-.8, -.5), smile=.8, walk=(t * 3) if 0 < walk < 1 else None,
                                                          tail=12 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_idea, 9)
    return view("".join(o), 620 + dx, 940 + dy, 1.38 + .1 * u, -1 + 2 * u, t=t)


# ═════════════════════════ s15: товары в корзину; s16: ждать сутки ═════════════════════════
def shop_screen(t, taps):
    """Три карточки товара с кнопкой «В корзину»; по нажатию товар улетает в значок тележки вверху, счётчик растёт."""
    def scr(x0, y0, x1, y1):
        o = [rect(x0, y0, x1, y1, "#ffffff")]
        o.append(rect(x0, y0, x1, y0 + 120, "#ff7a3d"))
        o.append(plain("Магазин", x0 + 40, y0 + 82, 54, fill="#ffffff"))
        n = sum(1 for q in taps if t >= q + .3)
        cx_c, cy_c = x1 - 80, y0 + 62
        o.append(cart_icon(cx_c, cy_c, .3, col="#ffffff", fill="#ff7a3d"))
        if n:
            o.append(tf(shape(ellipse_pts(0, 0, 30, 30, 16), RED, "", w=3, seed=8400) + text(str(n), 0, 14, 40, fill="#ffffff", stroke=RED, sw=1),
                        cx_c + 34, cy_c - 34, 1 + .3 * bump(t, taps[n - 1] + .3, .04, .2)))
        for j, (fn, col) in enumerate(((sneaker, "#e2574c"), (headphones, "#5a7bd6"), (gamepad, "#7a6ad6"))):
            yy = y0 + 260 + 260 * j
            o.append(shape(lib.rrect(x0 + 30, yy - 110, x1 - 30, yy + 110, 22), "#f4f1ea", "", w=3, seed=8410 + j))
            u = clamp((t - taps[j]) / .3)
            if u <= 0:
                o.append(fn(x0 + 140, yy, .7, 0, col))
            elif u < 1:
                ix = x0 + 140 + (cx_c - x0 - 140) * ease_io(u)
                iy = yy + (cy_c - yy) * ease_io(u) - 120 * math.sin(math.pi * u)
                o.append(fn(ix, iy, .7 * (1 - .7 * u), 200 * u, col))
            pr = bump(t, taps[j], .04, .15)
            done = t > taps[j]
            o.append(shape(lib.rrect(x0 + 270, yy - 30 + 6 * pr, x1 - 60, yy + 50 + 6 * pr, 26), "#c9ced6" if done else "#ff7a3d", "", w=3, seed=8420 + j))
            o.append(plain("В корзине" if done else "В корзину", (x0 + 270 + x1 - 60) / 2, yy + 26 + 6 * pr, 40, fill="#ffffff", anchor="middle"))
        return "".join(o)
    return scr


def frame_s15(t):
    """«Всё, что хочу купить»: телефон крупно, палец жмёт «В корзину» у кроссовок, наушников и джойстика — товары улетают в тележку."""
    a, b = T0("s15"), T1("s15")
    taps = [a + .2, W(49) + .05, W(50) + .15]
    x0, y0, x1, y1 = PX0, PY0, PX1, PY1
    btn = [((x0 + 270 + x1 - 60) / 2 - 20, y0 + 260 + 260 * j - 10) for j in range(3)]
    k = sum(1 for q in taps if t >= q - .2)
    k = min(2, k)
    tgt = btn[k]
    prev = btn[k - 1] if k > 0 else (x1 + 60, y1 + 60)
    ta = taps[k] - .25
    u = ease_io(ramp(t, ta, .2))
    thumb = (prev[0] + (tgt[0] - prev[0]) * u, prev[1] + (tgt[1] - prev[1]) * u)
    o = [phone_hand(t, shop_screen(t, taps), thumb_to=thumb)]
    for q in taps:
        if t > q:
            p = btn[taps.index(q)]
            o.append(PR.tap_rings(p[0] + 20, p[1] + 10, ramp(t, q, .3), 1.0, col="#FFD23F"))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = 0.0, 0.0
    for q in taps:
        sx, sy = shake(t, q, 5, .15)
        dx += sx
        dy += sy
    return view("".join(o), 560 + dx, 1000 + dy, 1.06 + .08 * uu, -1 + 2 * uu, bg=PH_BG, t=t)


def day_timer(x, y, k, u, t):
    """Таймер «24 ч»: круг циферблата, зелёный сектор обходит круг на u."""
    o = [blob(ellipse_pts(x + 10, y + 14, 230 * k, 230 * k, 30), "#000000", .2)]
    o.append(shape(ellipse_pts(x, y, 230 * k, 230 * k, 30), "#ffffff", "", w=7, seed=8500))
    r = 200 * k
    if u > .005:
        a1 = -90 + 360 * clamp(u)
        large = 1 if a1 + 90 > 180 else 0
        ex, ey = x + r * math.cos(math.radians(a1)), y + r * math.sin(math.radians(a1))
        if u < .999:
            o.append(f'<path d="M{x} {y} L{x} {y - r} A{r} {r} 0 {large} 1 {ex:.1f} {ey:.1f} Z" fill="#7cc46a" opacity=".8"/>')
        else:
            o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#7cc46a" opacity=".8"/>')
    for j in range(12):
        a = math.radians(j * 30)
        o.append(line([(x + 205 * k * math.cos(a), y + 205 * k * math.sin(a)), (x + 225 * k * math.cos(a), y + 225 * k * math.sin(a))], 5, INK,
                      taper=0, wmin=1, seed=8510 + j))
    ha = math.radians(-90 + 360 * clamp(u))
    o.append(line([(x, y), (x + 170 * k * math.cos(ha), y + 170 * k * math.sin(ha))], 10, INK, taper=.3, wmin=.5, seed=8530))
    o.append(text("24 ч", x, y + 50 * k, 140 * k, fill="#1d2448", stroke="#ffffff", sw=10))
    return "".join(o)


def frame_s16(t):
    """«кладу в корзину и жду сутки»: большая тележка с тремя товарами, рядом таймер «24 ч» обходит круг (солнце и луна над ним
    меняются); кот сидит у тележки и сторожит; на «сутки» круг замыкается."""
    a, b = T0("s16"), T1("s16")
    o = [paper_bg()]
    t_in = W(52)
    items = []
    for j, (fn, col) in enumerate(((sneaker, "#e2574c"), (headphones, "#5a7bd6"), (gamepad, "#7a6ad6"))):
        ta = a + .05 + .12 * j
        u = clamp((t - ta) / .3)
        if u <= 0:
            continue
        items.append(fn(300 - 90 + 110 * j, 1200 - 600 * (1 - u * u) - 30 * (j % 2), .8, 10 * (j - 1)))
    o.append(cart_icon(320, 1330, 1.6))
    o.extend(items)
    uu = ease_io(ramp(t, t_in, WE(56) - t_in))
    o.append(day_timer(760, 720, 1.0, uu, t))
    sun_a = math.radians(180 + 180 * uu)
    sx, sy = 760 + 330 * math.cos(sun_a), 720 + 330 * math.sin(sun_a)
    o.append(PR.sun(sx, sy, 55, 1.0, t) if uu < .5 else PR.moon(sx, sy, 46))
    if t > WE(56) - .05:
        o.append(PR.sparkles(760, 720, 2.4, bump(t, WE(56) - .05, .05, .5), t, seed=51, n=6, r=300))
        o.append(PR.check_mark(760, 480, 2.0 * pop(t, WE(56), .25), 1.0, col="#2f9a4a", seed=3))
    o.append(cat(760, 1560, .8, t, dict(look=(-.8, -.3), perk=1.0, smile=.6 + .4 * ramp(t, WE(56), .2), tail=10 * math.sin(t * 2.5))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, WE(56), 9)
    return view("".join(o), 540 + dx, 1040 + dy, 1.0 + .07 * u, 0, bg=PAPER, t=t)


# ═════════════════════════ s17: утро, удаляю половину ═════════════════════════
def frame_s17(t):
    """«Половину утром удаляю сам»: утро, солнце в окне, Дима за столом с телефоном; рядом крупная карточка корзины — два товара из
    четырёх уезжают свайпом и тают; кот доволен; надпись «+12 000 ₽»."""
    a, b = T0("s17"), T1("s17")
    o = desk_room(t, mode="day", sun=1.0, list_on=False)
    f = dima_desk(t, "proud82", head_add=-.06 + .03 * math.sin(t * 3))
    o.append(f["svg"])
    wx, wy = f["hold"]
    o.append(mini_phone(wx + 10, wy - 50, .5, -10, screen="#ffffff", inner=rect(-60, -112, 60, -70, "#ff7a3d")))
    # карточка корзины над столом (в мире)
    cx, cy = 820, 640
    card = [blob(lib.rrect(-250 + 12, -300 + 14, 250 + 12, 300 + 14, 30), "#000000", .2)]
    card.append(shape(lib.rrect(-250, -300, 250, 300, 30), "#ffffff", rect(-250, -300, 250, -210, "#ff7a3d"), w=5, seed=8600))
    card.append(cart_icon(-190, -255, .22, col="#ffffff", fill="#ff7a3d"))
    card.append(plain("Корзина", -140, -240, 46, fill="#ffffff"))
    swipes = {1: W(58), 3: W(59) + .05}
    for j, (fn, col) in enumerate(((sneaker, "#e2574c"), (headphones, "#5a7bd6"), (gamepad, "#7a6ad6"), (tshirt, "#3fb26a"))):
        yy = -150 + 120 * j
        su = ease_io(ramp(t, swipes[j], .3)) if j in swipes else 0.0
        if su >= 1:
            continue
        row = shape(lib.rrect(-220, -50, 220, 50, 16), "#f4f1ea", "", w=3, seed=8610 + j) + fn(-150, 0, .4, 0, col) \
            + line([(-80, -10), (150, -10)], 10, "#c9ced6", taper=0, wmin=1, seed=8620 + j)
        if su > 0:
            row = rect(-220, -50, 220, 50, RED, .9) + row
        card.append(f'<g opacity="{1 - su:.3f}" transform="translate({-520 * su:.1f} {yy})">{row}</g>')
    o.append(tf("".join(card), cx, cy + 8 * math.sin(t * 2), .9 * pop(t, a + .02, .25), -2))
    for j, q in swipes.items():
        if t > q:
            o.append(PR.speed_arcs(cx + 120, cy - 150 + 120 * j, 1.0, 1 - ramp(t, q + .1, .4), t, seed=60 + j, n=3, ang=0))
    o.append(cat(1000, DESK_Y - 60, .42, t, dict(look=(-.6, -.6), smile=1.0, tail=22 * math.sin(t * 6))))
    o.append(PR.purr(960, DESK_Y - 260, .8, t, ramp(t, W(60), .2), seed=1))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(60), 8)
    return view("".join(o), 640 + dx, 860 + dy, 1.15 + .06 * u, 0, t=t)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
