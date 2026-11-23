"""Рилс 108 «Уборка», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу); числа в коде — длительности движений.
Говорит Дима от первого лица (имя не звучит и не пишется). Сквозные места: прихожая со стулом и горой одежды (хук, чисто, гости,
уборка, итог, петля), комната со шкафом, телефон с таймером.
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
    if t < T1("s13") - .01 or t > k["t_out"]:
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
            blur += (f'<use href="#hk108" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk108">{body}</g></g>{blur}'


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


def day_timer(x, y, k, u, t, label="24 ч"):
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
    o.append(text(label, x, y + 50 * k, 140 * k, fill="#1d2448", stroke="#ffffff", sw=10))
    return "".join(o)


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


def frame_s13(t):
    """«Напиши «КОТ»»: поле комментария, крупно печатается жёлтое «КОТ»; Дима внизу слева, кот прыгает и садится рядом с ним."""
    a, b = T0("s13"), T1("s13")
    t_k = a - .1
    o = [paper_bg()]
    cb = 1.0
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
    t_j = a + .25
    j = ease_io(ramp(t, t_j, .4))
    x = 1180 + (620 - 1180) * j
    y = 1640 - 260 * math.sin(math.pi * j)
    o.append(cat(x, y, .9, t, dict(look=(-.7, -.4), legs=1.0 - j if j < 1 else 0.0, smile=1.0 if j >= 1 else .4, tail=10 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_k + .25, 8)
    return view("".join(o), 540 + dx, 1020 + dy, 1.0 + .06 * u, 0, bg=PAPER, t=t)




# ═════════════════════════ одежда, стул, шкаф, корзина ═════════════════════════
CLOTH = ("#e2574c", "#5a7bd6", "#3fb26a", "#f0a44a", "#b06ad6", "#4cb8c9", "#e46a8f", "#8a6038", "#d6a83a", "#6a8a3a")


def garment(x, y, k=1.0, rot=0.0, seed=0):
    """Сложенная вещь (центр): мягкий валик с рукавом, свисающим сбоку, и складкой."""
    c = CLOTH[seed % len(CLOTH)]
    sh = lib.mul(c, (.78, .78, .82))
    w = 120 + 30 * ((seed * 7) % 3)
    o = []
    side = 1 if seed % 2 else -1
    if seed % 3 != 2:
        o.append(shape([(side * (w - 30), -6), (side * (w + 10), 10), (side * (w + 20), 70), (side * (w - 10), 76), (side * (w - 40), 20)], sh, "",
                       w=3.4, seed=9100 + seed))
    o.append(shape(lib.rrect(-w, -30, w, 30, 26), c, blob(lib.rrect(-w, 8, w, 30, 18), sh, .85)
                   + line([(-w + 30, -4), (w - 40, -8)], 3, sh, taper=.4, wmin=.5, seed=9110 + seed), w=4, seed=9120 + seed))
    return tf("".join(o), x, y, k, rot)


def chair(x, y, k=1.0):
    """Стул (x, y — центр сиденья сверху): спинка слева."""
    o = [shape(lib.rrect(-120, 0, 120, 26, 8), "#a8774a", blob(lib.rect_pts(-120, 16, 120, 26), "#8a6038", .8), w=4, seed=1011)]
    o.append(shape([(-120, 4, 1), (-96, 4, 1), (-86, -340, 1), (-112, -340, 1)], "#a8774a", "", w=4, seed=1012))
    o.append(shape(lib.rrect(-118, -330, -20, -250, 10), "#a8774a", "", w=3.4, seed=1015))
    for s in (-1, 1):
        o.append(shape([(s * 96 - 10, 24, 1), (s * 96 + 10, 24, 1), (s * 104 + 10, 300, 1), (s * 104 - 10, 300, 1)], "#8a6038", "", w=3.4,
                       seed=1013 + s))
    return tf("".join(o), x, y, k)


CH = (380.0, RM.FL82 - 300.0)      # центр сиденья стула в прихожей


def pile_slots(n, x, y, seed=0):
    """Куда ложатся вещи горы: снизу вверх, со сдвигом (x, y — центр сиденья)."""
    out = []
    for j in range(n):
        jx = 26 * math.sin(j * 2.3 + seed) + 6 * j * math.sin(seed + .7)
        out.append((x + jx, y - 26 - 52 * j, 8 * math.sin(j * 1.7 + seed)))
    return out


def pile(t, n, x=CH[0], y=CH[1], t_add=None, sway=0.0, seed=0):
    """Гора из n вещей на стуле; t_add[j] — когда вещь j упала сверху (падает 0.12 с); sway — качание всей горы."""
    o = []
    for j, (px, py, r) in enumerate(pile_slots(n, x, y, seed)):
        ta = None if t_add is None else t_add[j]
        if ta is not None and t < ta:
            continue
        u = 1.0 if ta is None else clamp((t - ta) / .12)
        yy = py - (1 - u) * 260
        hh = y - py
        ox = sway * hh * .06 * math.sin(t * 9)
        o.append(garment(px + ox, yy, 1.0, r + sway * 3 * math.sin(t * 9 + j * .2), seed=j + seed))
    return "".join(o)


def wardrobe(x, y, open_u=1.0, fill=1.0, seed=0):
    """Шкаф (x, y — центр низа), створки открыты на open_u; внутри полки с вещами (fill — доля полных полок)."""
    w, h = 170, 960
    inner = rect(x - w + 16, y - h + 16, x + w - 16, y - 16, "#6e4a2c")
    for j in range(4):
        yy = y - h + 230 + 210 * j
        inner += line([(x - w + 16, yy), (x + w - 16, yy)], 8, "#8a6038", taper=0, wmin=1, seed=9200 + j)
        if j < round(4 * fill):
            for q in range(2):
                inner += garment(x - 60 + 120 * q, yy - 36, .45, 0, seed=j * 2 + q + seed)
    o = [blob(ellipse_pts(x + 10, y + 6, 200, 16, 14), "#000000", .18)]
    o.append(shape(lib.rect_pts(x - w, y - h, x + w, y), "#a8774a", inner, w=5, seed=9210))
    for s in (-1, 1):
        sx = 1 - 1.6 * ease_io(clamp(open_u))
        leaf = shape(lib.rect_pts(0, -h, s * w, 0), "#b88a5a", blob(ellipse_pts(s * (w - 30), -h / 2, 10, 10, 8), "#d8b24a"), w=4, seed=9220 + s)
        o.append(f'<g transform="translate({x - s * w} {y}) scale({sx:.4f} 1) translate({s * w} 0)">'
                 f'<g transform="translate({-s * w} 0) scale({s} 1) translate({s * w} 0) scale({s} 1)">{leaf}</g></g>')
    return "".join(o)


def basket(x, y, k=1.0, seed=0):
    """Корзина для белья (x, y — центр низа)."""
    o = [blob(ellipse_pts(x + 6, y + 4, 120 * k, 12 * k, 12), "#000000", .18)]
    pts = [(x - 110 * k, y - 220 * k, 1), (x + 110 * k, y - 220 * k, 1), (x + 90 * k, y, 1), (x - 90 * k, y, 1)]
    inner = "".join(line([(x - 110 * k + 20 * k * j, y - 210 * k), (x - 90 * k + 18 * k * j, y)], 3, "#b99560", taper=0, wmin=1, seed=9300 + j)
                    for j in range(12))
    o.append(shape(pts, "#e3c48c", inner, w=4, seed=9310))
    o.append(shape(lib.rrect(x - 120 * k, y - 236 * k, x + 120 * k, y - 206 * k, 10), "#d1b075", "", w=3.4, seed=9311))
    return "".join(o)


WR = (90.0, RM.FL82)       # шкаф в прихожей
BK = (580.0, RM.FL82)      # корзина


def hall(t, door=0.0, mode="evening", ward=0.0, ward_fill=1.0):
    h = RM.hall82(t, mode)
    return [h["bg"], h["door"](door), wardrobe(*WR, ward, ward_fill), chair(*CH)]


def dima_h(x, t, expr="calm82", pose="d82_rest", flip=False, **kw):
    return people.dima82(x, HHIP, HK, expr, pose, t=t, feet="stand", flip=flip, **kw)


def guests(t, x, k=HK * .95, op=1.0, expr="calm", look=False):
    """Двое гостей: мама с пакетом и студентка с рюкзаком (смотрят влево — внутрь прихожей)."""
    hip = RM.FL82 - 598 * k
    o = []
    for kind, dx in (("student", 150), ("mom", -40)):
        f = people.townsman82(kind, x + dx, hip, k, "rest", t=t, expr=expr if expr in people.EXPR[people._TOWN[kind]] else "calm",
                              feet="stand", flip=True)
        o.append(f["svg"])
    return f'<g opacity="{op:.3f}">{"".join(o)}</g>'


HIT01 = stress(0, .5)


def hook_times(n=26, t0=-.25, t1=.78):
    return [t0 + (t1 - t0) * (j / (n - 1)) ** 1.3 for j in range(n)]


def frame_s01(t):
    """ХУК: прихожая, на стул сверху валятся вещи, гора растёт до потолка и качается; камера едет вверх за верхушкой; Дима в шоке."""
    times = hook_times()
    o = hall(t, ward=.0)
    f = dima_h(850, t, "panic82", "d82_shrug", flip=True, head_add=-.12)
    o.append(f["svg"])
    n_on = sum(1 for q in times if t >= q)
    o.append(pile(t, len(times), t_add=times, sway=.4 + .8 * ramp(t, .4, .4)))
    top = CH[1] - 26 - 52 * max(0, n_on - 1)
    o.append(PR.speed_arcs(CH[0], top - 120, 1.0, .8, t, seed=2, n=3, ang=90))
    hx, hy = f["head"]
    o.append(PR.sweat(hx + 70, hy - 40, 1.2, 20))
    dx, dy = shake(t, HIT01, 10)
    cy = 1150 + (min(top, 1150) - 1150) * .75
    v = f'<g transform="{lib.cam(560 + dx, cy + 200 + dy, .78, 0)}">{"".join(o)}</g>'
    if NOCAM:
        return lib.svg(f'<rect width="1080" height="1920" fill="{BG}"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT01) + over(t))


FLOOR_HEAP = [(380 + 330 * math.sin(j * 2.1), RM.FL82 - 20 - 46 * (j // 6) - 10 * math.cos(j), 40 * math.sin(j * 1.3)) for j in range(22)]


def frame_s02(t):
    """«всю квартиру»: гора на стуле кренится и рушится на пол; Дима отскакивает; на «квартиру» кот выныривает сверху кучи."""
    a, b = T0("s02"), T1("s02")
    t_fall = W(3) - .25
    o = hall(t)
    f = dima_h(820, t, "panic82", "d82_shrug", flip=True, head_add=.05 * math.sin(t * 9))
    o.append(f["svg"])
    slots = pile_slots(26, *CH)
    for j, (px, py, r) in enumerate(slots):
        d = t_fall + .013 * (25 - j)
        u = clamp((t - d) / .3)
        if u <= 0:
            tilt = 4 * ramp(t, a, t_fall - a) * (CH[1] - py) / 400
            o.append(garment(px + tilt * 20, py, 1.0, r + tilt, seed=j))
            continue
        tx, ty, tr = FLOOR_HEAP[j % 22]
        x = px + (tx - px) * u + 120 * math.sin(math.pi * u) * (1 if j % 2 else -1)
        y = py + (ty - py) * u * u
        o.append(garment(x, y, 1.0, r + (tr - r) * u + 180 * u * (1 - u), seed=j))
    t_cat = W(3) + .3
    cu = ease_out(ramp(t, t_cat, .25))
    if cu > 0:
        o.append(cat(400, RM.FL82 - 230 + 160 * (1 - cu), .55, t, dict(look=(.7, -.6), smile=1.0, perk=1.0, tail=16 * math.sin(t * 6))))
        o.append(garment(330, RM.FL82 - 120, 1.0, 10, seed=3) + garment(470, RM.FL82 - 110, 1.0, -8, seed=6))
        o.append(PR.sparkles(400, RM.FL82 - 400, 1.6, bump(t, t_cat, .05, .45), t, seed=21, n=5, r=180))
    for j in range(3):
        o.append(PR.dust_puff(250 + 160 * j, RM.FL82, 1.2, ramp(t, W(3) + .05, .5), seed=j))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(3), 16)
    return view("".join(o), 560 + dx, 1060 + dy, .86 + .06 * u, -1.5 + 2 * u, t=t)


def frame_s19(t):
    """Петля: кадр хука — стул в прихожей, гора начинает расти."""
    a, b = T0("s19"), T1("s19")
    import anim
    hc = anim.hook_cam(0.0, hit=HIT01)
    u = ease_io(ramp(t, a, b - a))
    times = hook_times()
    tt = -.25 + (t - a)
    o = hall(t)
    f = dima_h(850, t, "puzzled82", "d82_shrug", flip=True, head_add=-.12)
    o.append(f["svg"])
    o.append(pile(tt, 26, t_add=times, sway=.3))
    s = .78 * (1 + (hc["zoom"] - 1) * u)
    return view("".join(o), 560, 1350, s, hc["rot"] * u, t=t)


# ═════════════════════════ s03 таймер, s04 чисто ═════════════════════════
def mmss(sec):
    sec = max(0, int(sec))
    return f"{sec // 60}:{sec % 60:02d}" if sec < 600 else "10:00"


def frame_s03(t):
    """«Десять минут в день»: на бумаге круглый таймер «10:00», стрелка пошла, цифры убывают; кот рядом смотрит."""
    a, b = T0("s03"), T1("s03")
    t_go = W(5)
    run = max(0.0, t - t_go)
    u = run / 1.2 * .12
    o = [paper_bg()]
    o.append(PR.glow(540, 820, 480, .4, "#d9f5c0"))
    o.append(day_timer(540, 860, 1.3 * pop(t, a, .25) * (1 + .06 * bump(t, W(4), .05, .25)), u, t, label=mmss(600 - run * 45)))
    o.append(cat(830, 1560, .8, t, dict(look=(-.6, -.8), perk=1.0, smile=.8, tail=14 * math.sin(t * 4))))
    o.append(PR.sparkles(540, 860, 2.4, bump(t, W(4), .05, .45), t, seed=11, n=6, r=360))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(4), 8)
    return view("".join(o), 540 + dx, 1040 + dy, 1.0 + .06 * uu, 0, bg=PAPER, t=t)


def frame_s04(t):
    """«и у меня чисто»: та же прихожая, стул пустой, шкаф закрыт, Дима довольный, кот на стуле; на «чисто» искры."""
    a, b = T0("s04"), T1("s04")
    o = hall(t, mode="morning")
    f = dima_h(760, t, "proud82", "d82_one", flip=True, head_add=.05 * bump(t, W(11), .08, .3))
    o.append(f["svg"])
    o.append(cat(CH[0] + 10, CH[1] + 4, .6, t, dict(look=(.7, -.4), smile=1.0, tail=14 * math.sin(t * 4))))
    tc = W(11) + .05
    for j, (sx, sy) in enumerate(((CH[0], CH[1] - 250), (WR[0], WR[1] - 700), (760, 700))):
        o.append(PR.sparkles(sx, sy, 1.8, bump(t, tc + .08 * j, .05, .6), t, seed=30 + j, n=5, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tc, 8)
    return view("".join(o), 520 + dx, 1080 + dy, .82 + .06 * u, 1 - 2 * u, t=t)


# ═════════════════════════ s05 ждал выходного ═════════════════════════
DAYS = ("ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС")


def week(x, y, t, t_circle, t0, t1):
    o = [blob(lib.rrect(x - 330 + 12, y - 250 + 14, x + 330 + 12, y + 250 + 14, 20), "#000000", .15)]
    o.append(shape(lib.rrect(x - 330, y - 250, x + 330, y + 250, 20), "#fffdf6", "", w=5, seed=7700))
    o.append(shape(lib.rrect(x - 330, y - 250, x + 330, y - 150, 20), "#3f6fb0", "", w=5, seed=7701))
    o.append(text("НЕДЕЛЯ", x, y - 178, 60, fill="#ffffff", stroke="#2a4f88", sw=3))
    for d, nm in enumerate(DAYS):
        r, c = divmod(d, 4)
        cx, cy = x - 240 + 160 * c, y - 50 + 160 * r
        o.append(text(nm, cx, cy + 22, 64, fill="#d8453a" if d >= 5 else "#1d2448", stroke="#fffdf6", sw=2))
        if d < 5:
            ta = t0 + (t1 - t0) * d / 5
            u = ramp(t, ta, .1)
            if u > 0:
                o.append(line([(cx - 50, cy - 40), (cx - 50 + 100 * u, cy - 40 + 80 * u)], 8, "#1d2448", taper=.3, wmin=.5, seed=7710 + d))
    cu = ramp(t, t_circle, .3)
    if cu > 0:
        cx, cy = x - 240 + 160 * 1, y - 50 + 160
        pts = [(cx + 90 * math.cos(math.radians(-100 + 380 * cu * k / 24)), cy + 70 * math.sin(math.radians(-100 + 380 * cu * k / 24)))
               for k in range(25)]
        o.append(line(pts, 9, "#d8453a", taper=.2, wmin=.6, seed=7790))
    return "".join(o)


def frame_s05(t):
    """«Ждал выходного на генеральную»: на стене неделя, суббота обведена красным; будни зачёркиваются, а гора на стуле рядом растёт."""
    a, b = T0("s05"), T1("s05")
    o = hall(t, mode="evening")
    o.append(week(700, 640, t, W(13), a + .3, W(15)))
    times = [a - 1 + .001 * j for j in range(6)] + [a + .15 + (b - a - .3) * j / 12 for j in range(12)]
    o.append(pile(t, 18, t_add=times, sway=.2))
    o.append(cat(820, RM.FL82, .7, t, dict(look=(-.8, -.7), perk=1.0, tail=10 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(15) + .1, 7)
    return view("".join(o), 560 + dx, 980 + dy - 120 * u, .82 + .04 * u, 0, t=t)


# ═════════════════════════ s06–s07 шкаф ═════════════════════════
RW = (330.0, RFL)


def frame_s06(t):
    """«Начинал с одного шкафа»: комната, шкаф распахнут, Дима выгребает вещи — они летят дугой на пол, куча растёт."""
    a, b = T0("s06"), T1("s06")
    o = [plain_room(t)]
    o.append(wardrobe(*RW, 1.0, 1.0 - .6 * ramp(t, a, b - a), seed=2))
    f = people.dima82(680, RFL - (people.LEG_LEN - 12) * .66 - 6, .66, "rush82", "d82_shrug", t=t, feet="stand", flip=True,
                      head_add=.05 * math.sin(t * 8))
    o.append(f["svg"])
    for j in range(14):
        ta = a - .3 + .1 * j
        u = clamp((t - ta) / .4)
        if u <= 0:
            continue
        sx, sy = RW[0] + 40, RW[1] - 600 + 40 * (j % 4)
        tx, ty = 520 + 260 * math.sin(j * 2.4), RFL - 20 - 30 * (j // 5)
        x = sx + (tx - sx) * u
        y = sy + (ty - sy) * u - 360 * math.sin(math.pi * u)
        o.append(garment(x, y, .8, 360 * u * (1 if j % 2 else -1) * (1 - u) + 10 * math.sin(j), seed=j + 4))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(19), 7)
    return view("".join(o), 520 + dx, 1100 + dy, .95 + .08 * u, -1 + 2 * u, t=t)


def frame_s07(t):
    """«и бросал на середине»: Дима сидит посреди вываленной одежды, лицо уставшее, плечи опущены; шкаф полупустой; кот запрыгивает
    на кучу."""
    a, b = T0("s07"), T1("s07")
    o = [plain_room(t)]
    o.append(wardrobe(*RW, 1.0, .5, seed=2))
    hip = RFL - 40
    tired = {"brows": "tired", "mouth": "tired", "lid": .35, "look": (.2, .5)}
    f = people.dima82(560, hip, .66, tired, "d82_rest", t=t, feet=None, head_add=-.12 - .04 * ramp(t, W(21), .3), lean_add=.1)
    o.append(f["svg"])
    for j in range(16):
        x = 560 + 330 * math.sin(j * 2.1)
        y = RFL - 10 - 40 * (j % 3) + 10 * math.cos(j)
        o.append(garment(x, y, .85, 30 * math.sin(j * 1.3), seed=j + 4))
    for j in range(7):
        o.append(garment(440 + 45 * j, RFL - 70 - 30 * (j % 2), .85, 12 * math.sin(j), seed=j + 21))
    hx, hy = f["head"]
    o.append(PR.sweat(hx + 70, hy - 30, 1.0, 20))
    tj = W(23) - .2
    j = ease_io(ramp(t, tj, .35))
    cx_ = 1100 + (840 - 1100) * j
    cy_ = RFL + (RFL - 120 - RFL) * j - 200 * math.sin(math.pi * j)
    o.append(cat(cx_, cy_, .6, t, dict(look=(-.8, -.3), legs=1.0 - j if j < 1 else 0.0, smile=.3, tail=10 * math.sin(t * 2))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(21), 6)
    return view("".join(o), 600 + dx, 1180 + dy, 1.05 + .08 * u, 0, t=t)


# ═════════════════════════ s08–s09 гости и гора ═════════════════════════
def frame_s08(t):
    """«А гости заставали»: звонок у двери, дверь распахивается, в проёме двое гостей; гора на стуле в кадре слева."""
    a, b = T0("s08"), T1("s08")
    t_ring, t_open = W(25) - .05, W(26) - .1
    ajar = ease_out(ramp(t, t_open, .3))
    o = hall(t, door=ajar)
    o.append(pile(t, 18))
    bx, by = HDOOR[0] + 400, RM.FL82 - 820
    o.append(shape(lib.rrect(bx - 34, by - 44, bx + 34, by + 44, 10), "#f6efd8", blob(ellipse_pts(bx, by, 16, 16, 10), "#e2574c"), w=3, seed=7900))
    o.append(bell_rings(bx, by, t, t_ring) + bell_rings(bx, by, t, t_ring + .25))
    o.append(PR.glow(bx, by, 160, .6 * bump(t, t_ring, .05, .4), "#fff1b0"))
    if ajar > .05:
        o.append(guests(t, HDOOR[0] - 20, op=clamp(ajar * 2)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_ring, 9)
    return view("".join(o), 700 + 40 * u + dx, 1040 + dy, .8 + .06 * u, 0, t=t)


def frame_s09(t):
    """«гору на стуле»: Дима раскинул руки перед стулом и заслоняет гору, гора торчит над ним; гости в дверях смотрят, «!»."""
    a, b = T0("s09"), T1("s09")
    o = hall(t, door=1.0)
    o.append(pile(t, 18, sway=.3))
    f = dima_h(420, t, "rush82", "d82_shrug", head_add=.05 * math.sin(t * 7))
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.sweat(hx - 70, hy - 40, 1.2, -20))
    o.append(guests(t, HDOOR[0] + 20))
    te = W(29)
    if t > te - .05:
        o.append(PR.question_mark(HDOOR[0] + 60, 380, 1.6 * pop(t, te - .05, .25), 1.0, col="#e2574c"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, te, 10)
    return view("".join(o), 650 + dx, 1000 + dy, .8 + .06 * u, 1 - 2 * u, t=t)


# ═════════════════════════ s10 решение, s11 таймер, s12 уборка ═════════════════════════
def frame_s10(t):
    """«Вот что я поменял»: прихожая, гора на стуле, Дима поднимает палец, над ним лампочка; кот садится рядом; надпись сверху."""
    a, b = T0("s10"), T1("s10")
    t_idea = W(30) + .15
    o = hall(t)
    o.append(pile(t, 14))
    f = dima_h(760, t, "wow82" if t > t_idea else "sure82", "d82_one", flip=True, head_add=.08 * bump(t, t_idea, .08, .3))
    o.append(f["svg"])
    hx, hy = f["head"]
    if t > t_idea:
        o.append(PR.glow(hx, hy - 300, 240, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx, hy - 300 + 8 * math.sin(t * 5), 1.2 * pop(t, t_idea, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx, hy - 300, 2.0, bump(t, t_idea, .05, .5), t, seed=41, n=5, r=220))
    walk = ease_out(ramp(t, W(33) - .35, .35))
    o.append(cat(1080 - 140 * walk, RM.FL82, .75, t, dict(look=(-.8, -.5), smile=.8, walk=(t * 3) if 0 < walk < 1 else None,
                                                       tail=12 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_idea, 9)
    return view("".join(o), 680 + dx, 1060 + dy, .88 + .08 * u, -1 + 2 * u, t=t)


def timer_screen(t, t_go):
    def scr(x0, y0, x1, y1):
        cx = (x0 + x1) / 2
        o = [rect(x0, y0, x1, y1, "#1d2448")]
        o.append(plain("Таймер", cx, y0 + 110, 56, fill="#ffffff", anchor="middle"))
        run = max(0.0, t - t_go)
        u = run / 600 * 40
        r = 210
        o.append(f'<circle cx="{cx}" cy="{y0 + 450}" r="{r}" fill="none" stroke="#3a4570" stroke-width="26"/>')
        if u > .002:
            a1 = -90 + 360 * min(u, .999)
            ex, ey = cx + r * math.cos(math.radians(a1)), y0 + 450 + r * math.sin(math.radians(a1))
            o.append(f'<path d="M{cx} {y0 + 450 - r} A{r} {r} 0 {1 if a1 + 90 > 180 else 0} 1 {ex:.1f} {ey:.1f}" fill="none" '
                     f'stroke="#7cc46a" stroke-width="26" stroke-linecap="round"/>')
        o.append(text(mmss(600 - run * 40), cx, y0 + 490, 130, fill="#ffffff", stroke="#1d2448", sw=2))
        on = t > t_go
        o.append(shape(ellipse_pts(cx, y1 - 220, 90, 90, 24), "#e2574c" if on else GREEN, "", w=4, seed=8701))
        o.append(text("Стоп" if on else "Старт", cx, y1 - 204, 44, fill="#ffffff", stroke="#111", sw=1))
        return "".join(o)
    return scr


def frame_s11(t):
    """«Таймер на десять минут»: телефон крупно, таймер «10:00»; палец жмёт «Старт», кольцо пошло, цифры убывают."""
    a, b = T0("s11"), T1("s11")
    t_go = W(36) - .05
    btn = (540 - 20, PY1 - 240)
    reach = ease_io(ramp(t, t_go - .35, .3)) * (1 - ease_io(ramp(t, t_go + .15, .3)))
    rest = (PX1 + 60, PY1 + 60)
    thumb = (rest[0] + (btn[0] - rest[0]) * reach, rest[1] + (btn[1] - rest[1]) * reach)
    o = [phone_hand(t, timer_screen(t, t_go), thumb_to=thumb)]
    if t > t_go:
        o.append(PR.tap_rings(540, PY1 - 220, ramp(t, t_go, .35), 1.6, col="#FFD23F"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_go, 9)
    return view("".join(o), 555 + dx, 980 + dy, 1.1 + .1 * u, -1 + 2 * u, bg=PH_BG, t=t)


def mini_timer(x, y, k, t, t_go):
    run = max(0.0, t - t_go)
    return day_timer(x, y, k, run / 600 * 40, t, label=mmss(600 - run * 40))


def frame_s12(t):
    """«убираю только то, что вижу»: прихожая, вещи со стула по одной улетают в шкаф и в корзину; таймер в углу идёт; стул пустеет."""
    a, b = T0("s12"), T1("s12")
    o = hall(t, ward=1.0, ward_fill=.5)
    o.append(basket(*BK))
    n = 12
    slots = pile_slots(n, *CH)
    span = WE(42) - .15 - a
    for j in range(n - 1, -1, -1):
        px, py, r = slots[j]
        ta = a + .05 + span * (n - 1 - j) / n
        u = clamp((t - ta) / .35)
        if u <= 0:
            o.append(garment(px, py, 1.0, r, seed=j))
            continue
        if u >= 1:
            continue
        to_bk = j % 2 == 0
        tx, ty = (BK[0], BK[1] - 200) if to_bk else (WR[0], WR[1] - 500 - 60 * (j % 3))
        x = px + (tx - px) * ease_io(u)
        y = py + (ty - py) * ease_io(u) - 300 * math.sin(math.pi * u)
        o.append(garment(x, y, 1.0 - .4 * u, r + 300 * u, seed=j))
    f = dima_h(820, t, "proud82", "d82_one", flip=True, head_add=.03 * math.sin(t * 4))
    o.append(f["svg"])
    o.append(mini_timer(560, 330, .5, t, T0("s11") + .5))
    if t > WE(42) - .1:
        o.append(PR.sparkles(CH[0], CH[1] - 150, 2.0, bump(t, WE(42) - .1, .05, .5), t, seed=61, n=6, r=220))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, WE(42), 7)
    return view("".join(o), 520 + dx, 1050 + dy, .82 + .06 * u, 0, t=t)


# ═════════════════════════ s14–s15 после призыва ═════════════════════════
def frame_s14(t):
    """«чтобы самому поменять это»: Дима сам кладёт последнюю футболку в корзину; кот на чистом стуле смотрит."""
    a, b = T0("s14"), T1("s14")
    o = hall(t)
    o.append(basket(*BK))
    t_drop = W(48) + .05
    f = dima_h(760, t, "proud82", "d82_hold", flip=True)
    o.append(f["svg"])
    wx, wy = f["hold"]
    u = clamp((t - t_drop) / .3)
    if u < 1:
        gx = wx + (BK[0] - wx) * u
        gy = wy - 20 + (BK[1] - 200 - wy + 20) * u * u
        o.append(garment(gx, gy, .9, -10 + 60 * u, seed=2))
    if t > t_drop + .3:
        o.append(PR.sparkles(BK[0], BK[1] - 260, 1.6, bump(t, t_drop + .3, .05, .5), t, seed=71, n=5, r=180))
    o.append(cat(CH[0] + 10, CH[1] + 4, .6, t, dict(look=(.8, -.2), smile=.8, tail=14 * math.sin(t * 3))))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_drop + .3, 7)
    return view("".join(o), 560 + dx, 1000 + dy, .95 + .08 * uu, 1 - 2 * uu, t=t)


def frame_s15(t):
    """«в своей жизни навсегда»: чистая прихожая, Дима стоит у стула и смотрит на кота, кот на чистом стуле жмурится; на «навсегда»
    сердечко."""
    a, b = T0("s15"), T1("s15")
    o = hall(t, mode="morning")
    o.append(basket(*BK))
    f = dima_h(700, t, "proud82", "d82_rest", flip=True, head_add=-.06)
    o.append(f["svg"])
    o.append(cat(CH[0] + 10, CH[1] + 4, .65, t, dict(look=(.6, -.6), smile=1.0, blink=1.0 if W(52) < t < W(52) + .15 else 0.0,
                                                   tail=18 * math.sin(t * 4))))
    th = W(53)
    if t > th:
        o.append(PR.heart(CH[0] + 120, CH[1] - 360 - 40 * ramp(t, th, .8), .8 * pop(t, th, .25), beat=bump(t, th, .05, .3)))
    o.append(PR.purr(CH[0] - 80, CH[1] - 300, .9, t, 1.0, seed=1))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, th, 7)
    return view("".join(o), 560 + dx, 1060 + dy, 1.0 + .1 * u, 0, t=t)


# ═════════════════════════ s16–s18 гости без предупреждения ═════════════════════════
def frame_s16(t):
    """«Вчера гости пришли»: дверь распахивается, гости шагают внутрь; стул чистый, на нём кот."""
    a, b = T0("s16"), T1("s16")
    t_open = W(55) - .1
    ajar = ease_out(ramp(t, t_open, .3))
    o = hall(t, door=ajar, mode="evening")
    o.append(basket(*BK))
    o.append(cat(CH[0] + 10, CH[1] + 4, .6, t, dict(look=(.8, -.3), perk=1.0, tail=14 * math.sin(t * 5))))
    if ajar > .05:
        step = ease_out(ramp(t, t_open + .15, .5))
        o.append(guests(t, HDOOR[0] - 20 - 160 * step, op=clamp(ajar * 2)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_open, 9)
    return view("".join(o), 720 - 60 * u + dx, 1040 + dy, .82 + .06 * u, 0, t=t)


def frame_s17(t):
    """«без предупреждения»: гости смотрят на чистый стул — на нём кот машет хвостом; искры чистоты."""
    a, b = T0("s17"), T1("s17")
    o = hall(t, door=1.0, mode="evening")
    o.append(basket(*BK))
    o.append(cat(CH[0] + 10, CH[1] + 4, .7, t, dict(look=(.9, -.2), smile=1.0, tail=26 * math.sin(t * 7))))
    o.append(guests(t, HDOOR[0] - 160, expr="smile"))
    o.append(PR.sparkles(CH[0], CH[1] - 200, 2.0, bump(t, a + .1, .05, .6), t, seed=81, n=6, r=230))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560 + 60 * u, 1060, .9 + .08 * u, 0, t=t)


def frame_s18(t):
    """«и мне было не стыдно»: Дима улыбается между стулом с котом и гостями; надпись «БЕЗ СТЫДА»."""
    a, b = T0("s18"), T1("s18")
    o = hall(t, door=1.0, mode="evening")
    o.append(basket(*BK))
    o.append(cat(CH[0] + 10, CH[1] + 4, .6, t, dict(look=(.8, -.4), smile=1.0, tail=18 * math.sin(t * 5))))
    joy = ramp(t, W(62), .2)
    f = dima_h(560, t, "laugh82" if joy > .5 else "proud82", "d82_one", head_add=.04 * math.sin(t * 3))
    o.append(f["svg"])
    o.append(guests(t, HDOOR[0] + 200, expr="smile"))
    hx, hy = f["head"]
    if joy > 0:
        o.append(PR.heart(hx + 90, hy - 220 - 30 * ramp(t, W(62), .8), .6 * pop(t, W(62), .25), beat=bump(t, W(62), .05, .3)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(62), 7)
    return view("".join(o), 720 + dx, 1080 + dy, .82 + .06 * u, 0, t=t)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
