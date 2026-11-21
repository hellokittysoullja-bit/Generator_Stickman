"""Рилс 106 «Отвечу потом», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу); числа в коде — длительности движений.
Говорит Дима от первого лица (имя не звучит и не пишется). Сквозные места: телефон крупно в руке (хук, чаты, петля),
стол у окна (секундомер, стыд, идея, итог), телефон на столе рядом с котом (призыв).
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
    if t < T1("s07") - .01 or t > k["t_out"]:
        return ""
    return kot_print(t, -9.0, 300, 330, 140)


def over(t):
    return title(t) + plate(t, SH["label"]) + plate(t, SH["label2"], w=560, size=70) + kot_small(t)


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
            blur += (f'<use href="#hk106" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk106">{body}</g></g>{blur}'


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
BLUE, GREEN_OUT, GRAY = "#2f8fe0", "#DCF8C6", "#8a93a6"
NAMES = (("Лёха", "#e2874c"), ("Мама", "#e46a8f"), ("Работа", "#5a7bd6"), ("Лена", "#b06ad6"), ("Друзья", "#3fb26a"),
         ("Староста", "#d6a83a"), ("Саня", "#4cb8c9"), ("Курьер", "#8a6038"), ("Аня", "#e2574c"), ("Брат", "#6a8a3a"))
PREV = ("ты где?", "позвони, как сможешь", "скинь отчёт", "ну что, придёшь?", "идём в бар?", "скинь отчёт", "го завтра",
        "я у двери", "видел?", "ты жив?")
HIT01 = stress(2, .4)                       # «потОм»: палец жмёт иконку, счётчик тает


def bubble_icon(x, y, k=1.0, col="#ffffff"):
    """Белое облачко чата (значок мессенджера), центр."""
    pts = ellipse_pts(0, -6, 62, 50, 22)
    tail = [(-34, 30), (-50, 62), (-8, 40)]
    return tf(blob(pts, col) + blob(tail, col), x, y, k)


def ticks(x, y, k=1.0, col=BLUE, u=1.0, two=True):
    """Две галочки «прочитано» (x, y — центр)."""
    o = PR.check_mark(x - 10 * k, y, .32 * k, u, col=col, w=7, seed=11)
    if two:
        o += PR.check_mark(x + 14 * k, y, .32 * k, u, col=col, w=7, seed=12)
    return o


def badge(x, y, r, n, pulse=0.0):
    rr = r * (1 + .12 * pulse)
    o = shape(ellipse_pts(x, y, rr, rr, 24), "#e2453a", "", w=4, seed=5300)
    return o + text(str(n), x, y + rr * .36, rr * (1.0 if n < 10 else .92), fill="#ffffff", stroke="#e2453a", sw=1)


APP = (540.0, 900.0)                       # иконка мессенджера на главном экране


def home_screen(t, count, pulse=0.0, pressed=0.0):
    def scr(x0, y0, x1, y1):
        g = lib.lin_grad([(0, "#6a5acd", 1), (1, "#2b2f6a", 1)], 0, 0, 0, 1)
        o = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>']
        o.append(text("21:40", (x0 + x1) / 2, y0 + 150, 96, fill="#ffffff", stroke="#2b2f6a", sw=1))
        cols = ("#f0a44a", "#7ac46a", "#e46a8f", "#5ac0e0", "#c0a0f0", "#e2c04a", "#8ab0ff", "#f07a5a")
        for j in range(8):                 # мелкие иконки вокруг
            cx, cy = x0 + 90 + 127 * (j % 4), y0 + 250 + (j // 4) * 150 if j < 4 else y1 - 300 + ((j - 4) // 4) * 150
            cx = x0 + 90 + 127 * (j % 4)
            o.append(shape(lib.rrect(cx - 44, cy - 44, cx + 44, cy + 44, 18), cols[j], "", w=3, seed=5310 + j))
        k = 1.0 - .08 * pressed
        o.append(blob(lib.rrect(APP[0] - 120, APP[1] - 108, APP[0] + 128, APP[1] + 128, 50), "#000000", .25))
        o.append(tf(shape(lib.rrect(-120, -120, 120, 120, 50), BLUE, "", w=5, seed=5320) + bubble_icon(0, 0, 1.25), APP[0], APP[1], k))
        o.append(text("Чаты", APP[0], APP[1] + 182, 44, fill="#ffffff", stroke="#2b2f6a", sw=1))
        if count > 0:
            o.append(badge(APP[0] + 112 * k, APP[1] - 112 * k, 64, count, pulse))
        return "".join(o)
    return scr


def fly_bubbles(t, t0, dur, n=40, seed=3):
    """n пузырей с галочками вылетают из иконки по одному за dur секунд и разлетаются за экран."""
    o = []
    for j in range(n):
        ts = t0 + dur * j / n
        u = (t - ts) / .55
        if not 0 < u < 1:
            continue
        a = math.radians((j * 137.5 + seed * 40) % 360)
        dist = 300 + 520 * ease_out(u)
        x = APP[0] + 112 + math.cos(a) * dist
        y = APP[1] - 112 + math.sin(a) * dist * .9 - 120 * u
        s = (.6 + .5 * math.sin(j)) * (1 - .3 * u) * pop(t, ts, .12)
        b = (shape(lib.rrect(-90, -40, 90, 40, 26), "#ffffff", "", w=4, seed=5400 + j % 7)
             + ticks(10, 4, 1.6, BLUE, ease_out(clamp(u * 3))))
        o.append(f'<g opacity="{1 - ramp(u, .7, .3):.3f}">{tf(b, x, y, s, -12 + 24 * math.sin(j * 1.7))}</g>')
    return "".join(o)


def chat_row(x0, x1, y, j, state, t=0.0, hi=0.0):
    """Строка списка чатов: аватар, имя, превью; справа зелёный счётчик (state=('n', N)) или синие галочки (state=('ok', u))."""
    name, col = NAMES[j % len(NAMES)]
    o = []
    if hi > 0:
        o.append(rect(x0, y - 62, x1, y + 62, "#e8f2ff", hi))
    o.append(shape(ellipse_pts(x0 + 70, y, 44, 44, 20), col, "", w=3, seed=5500 + j))
    o.append(text(name[0], x0 + 70, y + 18, 50, fill="#ffffff", stroke=col, sw=1))
    o.append(plain(name, x0 + 136, y - 8, 40, fill="#1d2448"))
    o.append(plain(PREV[j % len(PREV)], x0 + 136, y + 40, 30, fill=GRAY))
    kind, v = state
    if kind == "n":
        o.append(shape(ellipse_pts(x1 - 56, y + 6, 30, 30, 16), "#3fb26a", "", w=2.6, seed=5520 + j))
        o.append(text(str(v), x1 - 56, y + 18, 32, fill="#ffffff", stroke="#3fb26a", sw=1))
    else:
        o.append(ticks(x1 - 56, y + 8, 1.2, BLUE, v))
    o.append(line([(x0 + 136, y + 62), (x1, y + 62)], 2, "#e3e6ee", taper=0, wmin=1, seed=5530 + j))
    return "".join(o)


def list_screen(t, states, total, scroll=0.0, hi=None):
    """Список чатов: шапка «Чаты» и общий счётчик; states[j] — состояние строки j; scroll — сдвиг строк вверх, px."""
    def scr(x0, y0, x1, y1):
        o = [rect(x0, y0, x1, y1, "#ffffff")]
        for j, st in enumerate(states):
            y = y0 + 230 + 128 * j - scroll
            if y0 + 120 < y < y1 + 70:
                o.append(chat_row(x0, x1, y, j, st, t, hi=(hi[1] if hi and hi[0] == j else 0.0)))
        o.append(rect(x0, y0, x1, y0 + 150, BLUE))
        o.append(text("Чаты", x0 + 40, y0 + 104, 60, fill="#ffffff", stroke=BLUE, sw=1, anchor="start"))
        if total > 0:
            o.append(badge(x0 + 250, y0 + 82, 40, total))
        else:
            o.append(ticks(x0 + 250, y0 + 86, 2.0, "#ffffff"))
        return "".join(o)
    return scr


def msg(x0, x1, y, s, out=False, k=1.0, tick_u=0.0, size=40):
    """Пузырь сообщения: входящее слева (белое), исходящее справа (зелёное, с галочками). y — центр."""
    w = 26 * len(s) * size / 40 + 70
    if out:
        a, b = x1 - 30 - w, x1 - 30
    else:
        a, b = x0 + 30, x0 + 30 + w
    o = shape(lib.rrect(a, y - 44, b, y + 44, 30), GREEN_OUT if out else "#ffffff", "", w=3.4, seed=5600 + len(s))
    o += plain(s, a + 32, y + 14, size, fill="#1d2448")
    if out and tick_u > 0:
        o += ticks(b - 36, y + 30, 1.0, BLUE, tick_u)
    cx = (a + b) / 2
    return f'<g transform="translate({cx:.1f} {y:.1f}) scale({k:.4f}) translate({-cx:.1f} {-y:.1f})">{o}</g>'


def chat_screen(t, name, col, incoming, typed="", typed_u=0.0, sent=None, cursor=True, extra=None):
    """Экран чата: шапка с именем, входящие [(текст, t_in)], поле ввода с печатающимся typed (typed_u 0…1);
    sent=(текст, t_send) — строка уходит из поля пузырём вверх, через 0.35 с синие галочки."""
    def scr(x0, y0, x1, y1):
        o = [rect(x0, y0, x1, y1, "#e9efe4")]
        for j in range(7):
            o.append(blob(ellipse_pts(x0 + 80 + 160 * (j % 3), y0 + 260 + 130 * j, 26, 26, 10), "#dfe7d8", .8))
        yy = y0 + 250
        for s, ta in incoming:
            if t >= ta:
                o.append(msg(x0, x1, yy, s, k=pop(t, ta, .2)))
            yy += 110
        if sent is not None and t >= sent[1]:
            u = ease_out(ramp(t, sent[1], .28))
            ty = (y1 - 80) + (yy - (y1 - 80)) * u
            o.append(msg(x0, x1, ty, sent[0], out=True, k=.9 + .1 * u, tick_u=ease_out(ramp(t, sent[1] + .35, .2))))
        if extra:
            o.append(extra(x0, y0, x1, y1, yy))
        o.append(rect(x0, y0, x1, y0 + 150, BLUE))
        o.append(shape(ellipse_pts(x0 + 70, y0 + 82, 40, 40, 18), col, "", w=3, seed=5700))
        o.append(text(name[0], x0 + 70, y0 + 98, 46, fill="#ffffff", stroke=col, sw=1))
        o.append(plain(name, x0 + 130, y0 + 98, 50, fill="#ffffff"))
        # поле ввода и кнопка «отправить»
        o.append(rect(x0, y1 - 140, x1, y1, "#f6f7f9"))
        o.append(shape(lib.rrect(x0 + 24, y1 - 116, x1 - 130, y1 - 40, 36), "#ffffff", "", w=3, seed=5701))
        shown = "" if (sent is not None and t >= sent[1]) else typed[:int(round(len(typed) * clamp(typed_u)))]
        if shown:
            o.append(plain(shown, x0 + 50, y1 - 64, 32, fill="#1d2448"))
        elif cursor:
            o.append(plain("Сообщение", x0 + 50, y1 - 64, 34, fill="#b0b6c2"))
        if cursor and int(t * 3) % 2 == 0 and not (sent is not None and t >= sent[1]):
            cx = x0 + 52 + 18.4 * len(shown)
            o.append(rect(cx, y1 - 100, cx + 5, y1 - 54, BLUE))
        o.append(shape(ellipse_pts(x1 - 70, y1 - 78, 44, 44, 18), BLUE if shown else "#c9d3e6", "", w=3, seed=5702))
        o.append(blob([(x1 - 92, y1 - 96), (x1 - 46, y1 - 78), (x1 - 92, y1 - 60), (x1 - 82, y1 - 78)], "#ffffff"))
        return "".join(o)
    return scr


SEND = (PX1 - 70, PY1 - 78)                # кнопка «отправить» на экране крупного телефона


# ═════════════════════════ s01 хук, s15 петля, s02 список, s04, s12, s13 ═════════════════════════
def hook_count(t):
    return int(math.ceil(40 * (1 - ease_io(ramp(t, HIT01 + .05, .62)))))


def frame_s01(t):
    """ХУК: телефон в руке, на иконке мессенджера «40», счётчик дёргается; на «потом» палец жмёт иконку, счётчик тает до 0, пузыри
    с галочками вылетают из иконки."""
    n = hook_count(t)
    pulse = abs(math.sin(t * 9)) if t < HIT01 else bump(t, HIT01, .05, .2)
    reach = ease_io(ramp(t, HIT01 - .32, .3)) * (1 - ease_io(ramp(t, HIT01 + .12, .3)))
    rest = (APP[0] + 150 + 18 * math.sin(t * 7), APP[1] + 360 + 12 * math.cos(t * 9))
    tgt = (APP[0] - 10, APP[1] - 10)
    thumb = (rest[0] + (tgt[0] - rest[0]) * reach, rest[1] + (tgt[1] - rest[1]) * reach)
    o = [phone_hand(t, home_screen(t, n, pulse, pressed=bump(t, HIT01, .04, .15)), shake_u=.5 if t < HIT01 else .1, thumb_to=thumb)]
    o.append(fly_bubbles(t, HIT01 + .05, .62))
    if t > HIT01:
        o.append(PR.tap_rings(APP[0], APP[1], ramp(t, HIT01, .35), 1.8, col="#FFD23F"))
        o.append(PR.sparkles(APP[0] + 112, APP[1] - 112, 2.0, bump(t, HIT01 + .7, .05, .45), t, seed=2, n=6, r=220))
    dx, dy = shake(t, HIT01, 14)
    cx = 555 + 20 * math.sin(t * 1.3)
    cy = 960 + 30 * ease_io(ramp(t, 0, T1("s01")))
    s = 1.28 + .08 * ease_io(ramp(t, 0, T1("s01")))
    v = f'<g transform="{lib.cam(cx + dx, cy + dy, s, 0)}">{"".join(o)}</g>'
    if NOCAM:
        return lib.svg(f'<rect width="1080" height="1920" fill="{PH_BG}"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT01, bg=PH_BG) + over(t))


def frame_s15(t):
    """Петля: кадр хука — телефон, на иконке «40», счётчик пульсирует."""
    a, b = T0("s15"), T1("s15")
    import anim
    hc = anim.hook_cam(0.0, hit=HIT01)
    u = ease_io(ramp(t, a, b - a))
    rest = (APP[0] + 150 + 18 * math.sin(t * 7), APP[1] + 360 + 12 * math.cos(t * 9))
    o = [phone_hand(t, home_screen(t, 40, abs(math.sin(t * 9))), shake_u=.5, thumb_to=rest)]
    s = 1.28 * (1 + (hc["zoom"] - 1) * u)
    return view("".join(o), 555, 960, s, hc["rot"] * u, bg=PH_BG, t=t)


def frame_s02(t):
    """«Сорок сообщений»: список чатов, зелёные счётчики один за другим становятся галочками, список едет вверх, общий счётчик тает."""
    a, b = T0("s02"), T1("s02")
    n = 10
    tf_ = [a + .12 + (b - a - .3) * j / (n - 1) for j in range(n)]
    states = [("ok", ease_out(ramp(t, tf_[j], .15))) if t >= tf_[j] else ("n", 4 + (j * 7) % 5) for j in range(n)]
    left = sum(1 for x in tf_ if t < x)
    total = int(round(40 * left / n))
    scroll = 260 * ease_io(ramp(t, a, b - a))
    o = [phone_hand(t, list_screen(t, states, total, scroll), typing=.0, thumb=True,
                    thumb_to=(PX0 + 300 + 30 * math.sin(t * 20), PY1 - 260 - 60 * abs(math.sin(t * 16))))]
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(4), 6)
    return view("".join(o), 560 + dx, 960 + dy, 1.06 + .08 * u, -1 + 2 * u, bg=PH_BG, t=t)


def frame_s04(t):
    """«Читал и закрывал»: на «Читал» чат «Лёха» въезжает справа, сообщения видны; на «закрывал» палец смахивает чат влево —
    под ним список, у Лёхи синие галочки, ответа нет."""
    a, b = T0("s04"), T1("s04")
    t_in, t_out = W(10) - .05, W(12) + .05
    name, col = NAMES[0]
    chat = chat_screen(t, name, col, [("ты где?", a - 1), ("завтра идём?", a - 1), ("ау?", W(11))], cursor=False)
    states = [("ok", 1.0)] + [("n", 3), ("n", 1), ("n", 2), ("n", 5), ("n", 1), ("n", 2)]
    lst = list_screen(t, states, 14)
    sin = 1 - ease_out(ramp(t, t_in, .22))
    sout = ease_io(ramp(t, t_out, .3))

    def scr(x0, y0, x1, y1):
        w = x1 - x0
        o = [lst(x0, y0, x1, y1)]
        dx = w * sin - w * 1.1 * sout
        if dx > -w * 1.09:
            o.append(f'<g transform="translate({dx:.1f} 0)">{chat(x0, y0, x1, y1)}</g>')
            o.append(f'<rect x="{x0 + dx - 30:.1f}" y="{y0}" width="30" height="{y1 - y0}" fill="#000" opacity=".12"/>')
        return "".join(o)
    if t < t_out:
        thumb = (PX0 + 380 - 60 * ease_io(ramp(t, t_in - .3, .3)), PY0 + 420 + 30 * math.sin(t * 6))
    else:
        u = ease_io(ramp(t, t_out - .05, .32))
        thumb = (PX1 - 60 - 560 * u, PY0 + 560 - 40 * u)
    o = [phone_hand(t, scr, thumb_to=thumb)]
    if t > t_out:
        o.append(PR.speed_arcs(PX0 + 120, PY0 + 560, 1.4, 1 - ramp(t, t_out + .1, .4), t, seed=4, n=3, ang=0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_out + .1, 8)
    return view("".join(o), 560 + dx, 960 + dy, 1.08 + .08 * u, 1 - 2 * u, bg=PH_BG, t=t)


def frame_s12(t):
    """«Отвечаю одной строкой сразу»: чат «Мама» открыт, одна строка печатается и на «сразу» улетает с галочками; следующий чат
    «Староста» въезжает справа, и строка уже печатается."""
    a, b = T0("s12"), T1("s12")
    t_send = W(43) + .02
    t_next = t_send + .55
    m_name, m_col = NAMES[1]
    s_name, s_col = NAMES[5]
    c1 = chat_screen(t, m_name, m_col, [("ты поел?", a - 1)], typed="Да, всё ок!", typed_u=ramp(t, W(40), t_send - .1 - W(40)),
                     sent=("Да, всё ок!", t_send))
    c2 = chat_screen(t, s_name, s_col, [("скинь отчёт", a - 1)], typed="Скину до вечера.", typed_u=ramp(t, t_next + .3, b - t_next - .3))
    sl = ease_out(ramp(t, t_next, .25))

    def scr(x0, y0, x1, y1):
        w = x1 - x0
        o = [f'<g transform="translate({-w * sl:.1f} 0)">{c1(x0, y0, x1, y1)}</g>']
        if sl > 0:
            o.append(f'<g transform="translate({w * (1 - sl):.1f} 0)">{c2(x0, y0, x1, y1)}</g>')
        return "".join(o)
    typing = 1.0 if (t < t_send - .1 or t > t_next + .3) else 0.0
    press = ease_io(ramp(t, t_send - .2, .18)) * (1 - ease_io(ramp(t, t_send + .05, .2)))
    if press > 0:
        rest = (PX0 + 300, PY1 - 70)
        thumb = (rest[0] + (SEND[0] - 22 - rest[0]) * press, rest[1] + (SEND[1] - 18 - rest[1]) * press)
        o = [phone_hand(t, scr, thumb_to=thumb)]
    else:
        o = [phone_hand(t, scr, typing=typing)]
    if t > t_send:
        o.append(PR.tap_rings(SEND[0], SEND[1], ramp(t, t_send, .3), 1.2, col="#FFD23F"))
        o.append(PR.sparkles(540, PY0 + 400, 1.8, bump(t, t_send + .35, .05, .4), t, seed=7, n=5, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_send, 8)
    return view("".join(o), 560 + dx, 1000 + dy, 1.04 + .08 * u, -1 + 2 * u, bg=PH_BG, t=t)


def frame_s13(t):
    """«пока открыл»: список чатов, у всех галочки, последний «Брат» с «1» подсвечивается на «пока» и на «открыл» становится
    галочкой; общий счётчик — галочка, искры."""
    a, b = T0("s13"), T1("s13")
    t_ok = W(45) + .1
    states = [("ok", 1.0)] * 6 + [("ok", ease_out(ramp(t, t_ok, .18))) if t >= t_ok else ("n", 1)]
    hi = (6, ramp(t, W(44), .15) * (1 - ramp(t, t_ok + .2, .3)))
    lst = list_screen(t, states, 0 if t >= t_ok else 1, scroll=0, hi=hi)
    yb = PY0 + 230 + 128 * 6
    reach = ease_io(ramp(t, W(44) - .1, .25)) * (1 - ease_io(ramp(t, t_ok, .25)))
    rest = (PX0 + 380, PY1 + 40)
    thumb = (rest[0] + (PX0 + 260 - rest[0]) * reach, rest[1] + (yb - 20 - rest[1]) * reach)
    o = [phone_hand(t, lst, thumb_to=thumb)]
    if t > t_ok:
        o.append(PR.tap_rings(PX0 + 280, yb, ramp(t, W(44) + .1, .3), 1.2, col="#FFD23F"))
        o.append(PR.sparkles(PX0 + 250, PY0 + 82, 2.0, bump(t, t_ok, .05, .45), t, seed=8, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_ok, 8)
    return view("".join(o), 560 + dx, 980 + dy, 1.12 - .06 * u, 0, bg=PH_BG, t=t)


def friends_photo(x, y, k, t):
    """Фото в чате: трое друзей в баре улыбаются, бокалы."""
    o = [shape(lib.rrect(-230, -170, 230, 170, 18), "#5a3a2a", "", w=4, seed=5800)]
    o.append(blob(lib.rrect(-216, -156, 216, -20, 10), "#7a4a30"))
    for j in range(6):
        o.append(shape(lib.rrect(-190 + 66 * j, -140, -164 + 66 * j, -60, 6), ("#4c9a5a", "#c98a3a", "#9a4a5a")[j % 3], "", w=2.4, seed=5810 + j))
    o.append(PR.glow(0, -60, 260, .4, "#ffd27a"))
    ex = {"brows": "calm", "mouth": "smile", "smile": 1.0, "lid": .8, "look": (0, 0)}
    for j, (st, px) in enumerate((("girl", -130), ("cap", 0), ("bob", 130))):
        people.C = dict(people.PAL[st])
        h = people.person_head(ex, st)
        o.append(blob(lib.rrect(px - 70, 70, px + 70, 170, 30), ("#e46a8f", "#5a7bd6", "#e2c04a")[j]))
        o.append(tf(h, px, 30 + 6 * math.sin(t * 5 + j), .34))
    o.append(shape(lib.rrect(170, 40, 206, 120, 6), "#f6d36a", "", w=2.4, seed=5820))
    c = lib.clip_rect(-230, -170, 460, 340)
    return tf(f'<g clip-path="url(#{c})">{"".join(o)}</g>' + shape(lib.rrect(-230, -170, 230, 170, 18), "none", "", w=5, seed=5821), x, y, k)


def frame_s06(t):
    """«А друзья перестали звать»: групповой чат «Друзья»: «идём в бар?», «я за!», на «звать» фото друзей в баре — Димы в чате нет."""
    a, b = T0("s06"), T1("s06")
    name, col = NAMES[4]
    t_ph = W(20) - .05

    def ex(x0, y0, x1, y1, yy):
        if t < t_ph:
            return ""
        return friends_photo((x0 + x1) / 2 - 20, yy + 140, 1.0 * pop(t, t_ph, .25), t)
    chat = chat_screen(t, name, col, [("Саня: идём в бар?", W(18) - .05), ("Аня: я за!", W(19) + .05)], cursor=False, extra=ex)
    o = [phone_hand(t, chat, thumb=False)]
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_ph, 8)
    return view("".join(o), 560 + dx, 980 + dy, 1.04 + .1 * u, 1 - 2 * u, bg=PH_BG, t=t)


# ═════════════════════════ стол у окна ═════════════════════════
def frame_s03(t):
    """«закрыл за двадцать минут»: Дима за столом с телефоном в руках, секундомер на стене заполняется, на «минут» — «20 МИН»;
    кот на столе."""
    a, b = T0("s03"), T1("s03")
    t_full = W(9) + .1
    o = desk_room(t, mode="day", sun=.8, list_on=False)
    f = dima_desk(t, "sure82" if t < t_full else "proud82", head_add=-.1)
    o.append(f["svg"])
    wx, wy = f["hold"]
    o.append(mini_phone(wx + 10, wy - 40, .5, -20, screen="#ffffff", inner=rect(-60, -112, 60, -70, BLUE)))
    sec = 360 * ease_io(ramp(t, a, t_full - a))
    o.append(PR.stopwatch(820, 520, .9, hand_a=sec, sector_a=sec, click=bump(t, t_full, .05, .3), t=t))
    if t > t_full - .05:
        s = pop(t, t_full - .05, .25)
        pl = (f'<rect x="-150" y="-56" width="300" height="104" rx="22" fill="#1d2448" stroke="#111" stroke-width="5"/>'
              + text("20 МИН", 0, 22, 62, fill="#9fe0b0", stroke="#1d2448", sw=2))
        o.append(f'<g transform="translate(820 790) scale({s:.4f})">{pl}</g>')
        o.append(PR.sparkles(820, 520, 1.8, bump(t, t_full, .05, .45), t, seed=10, n=6, r=230))
    o.append(cat(930, DESK_Y - 60, .42, t, dict(look=(-.7, -.6), smile=.6, tail=12 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_full, 9)
    return view("".join(o), 640 + dx, 840 + dy, 1.28 + .06 * u, 0, t=t)


def frame_s05(t):
    """«Через неделю стыдно отвечать»: Дима за столом прячет лицо в ладони; над чатом-пузырём «Лёха: завтра идём?» бирка
    «неделю назад»; телефон лежит на столе."""
    a, b = T0("s05"), T1("s05")
    t_hide = W(15) - .1
    feet = people.sit_kw(360, DHIP, .5)["feet"]
    probe = people.dima82(360, DHIP, .5, "squint82", "sit_desk", t=t, feet=feet, lean_add=.2, head_add=.15)
    hx, hy = probe["head"]
    h = ease_io(ramp(t, t_hide - .25, .25))
    down_f, down_n = (430, DESK_Y - 40), (500, DESK_Y - 40)
    up_f, up_n = (hx + 40, hy + 30), (hx + 95, hy + 20)
    tf_ = (down_f[0] + (up_f[0] - down_f[0]) * h, down_f[1] + (up_f[1] - down_f[1]) * h)
    tn_ = (down_n[0] + (up_n[0] - down_n[0]) * h, down_n[1] + (up_n[1] - down_n[1]) * h)
    arms = {"f": ("ik", tf_, 1), "n": ("ik", tn_, 1)}
    hands = {"f": {"dir": (.2, -1), "curl": (.1, .1, .12, .15), "thumb": .2}, "n": {"dir": (.2, -1), "curl": (.1, .1, .12, .15), "thumb": .2}}
    o = desk_room(t, mode="day", sun=.2, list_on=False)
    f = people.dima82(360, DHIP, .5, "squint82", "sit_desk", t=t, feet=feet, lean_add=.2 + .1 * h, head_add=.15 + .1 * h, arms=arms,
                      hands=hands)
    o.append(f["svg"])
    o.append(PR.phone_flat(640, DESK_Y - 40, .55, 0, face_down=False, seed=1))
    k = pop(t, a + .05, .22)
    if k > .01:
        bub = (shape(lib.rrect(-250, -60, 250, 60, 34), "#ffffff", "", w=4, seed=5900)
               + plain("Лёха: завтра идём?", -220, 16, 42))
        o.append(tf(bub, 720, 470 + 6 * math.sin(t * 3), .95 * k, -2))
    if t > W(14):
        s = pop(t, W(14), .22)
        tag = (f'<rect x="-170" y="-40" width="340" height="76" rx="38" fill="#8a93a6" stroke="#111" stroke-width="4"/>'
               + text("неделю назад", 0, 12, 40, fill="#ffffff", stroke="#8a93a6", sw=1))
        o.append(f'<g transform="translate(800 350) rotate(4) scale({s:.4f})">{tag}</g>')
    if h > .5:
        o.append(PR.sweat(hx - 60, hy - 60, 1.0, -20))
    o.append(cat(940, DESK_Y - 60, .42, t, dict(look=(-.9, -.2), perk=ramp(t, t_hide, .2), tail=6 * math.sin(t * 2))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(14) + .05, 8)
    return view("".join(o), 600 + dx, 820 + dy, 1.3 + .08 * u, 0, t=t)


def frame_s11(t):
    """«Вот что я поменял»: Дима за столом, над ним загорается лампочка, телефон на столе, кот подходит и садится рядом;
    маленькая надпись «ВОТ ЧТО Я ПОМЕНЯЛ»."""
    a, b = T0("s11"), T1("s11")
    t_idea = W(36) + .15
    o = desk_room(t, mode="day", sun=.6, list_on=False)
    f = dima_desk(t, "wow82" if t > t_idea else "sure82", head_add=.08 * bump(t, t_idea, .08, .3) - .1)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.phone_flat(640, DESK_Y - 40, .55, 0, face_down=False, seed=1))
    if t > t_idea:
        o.append(PR.glow(hx, hy - 220, 200, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx, hy - 220 + 6 * math.sin(t * 5), .8 * pop(t, t_idea, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx, hy - 220, 1.4, bump(t, t_idea, .05, .5), t, seed=41, n=5, r=160))
    walk = ease_out(ramp(t, W(39) - .3, .35))
    o.append(cat(1000 - 140 * walk, DESK_Y - 60, .42, t, dict(look=(-.8, -.5), smile=.8, walk=(t * 3) if 0 < walk < 1 else None,
                                                          tail=12 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_idea, 9)
    return view("".join(o), 620 + dx, 940 + dy, 1.38 + .1 * u, -1 + 2 * u, t=t)


def notif(t, t0):
    """Уведомление сверху экрана: «Друзья · Ты с нами сегодня?» — съезжает сверху с отскоком (экранные координаты)."""
    if t < t0:
        return ""
    u = ease_out(ramp(t, t0, .3), 2)
    y = -120 + (600 + 120) * u + 8 * math.sin(t * 3)
    s = .92 + .08 * lib.back_out(u, 2.0) if u < 1 else 1.0
    name, col = NAMES[4]
    b = (f'<rect x="-430" y="-96" width="860" height="200" rx="40" fill="#000" opacity=".25" transform="translate(8 12)"/>'
         + f'<rect x="-430" y="-96" width="860" height="200" rx="40" fill="#ffffff" stroke="#111" stroke-width="6"/>'
         + shape(lib.rrect(-400, -64, -264, 72, 34), BLUE, "", w=4, seed=5950) + bubble_icon(-332, 4, .8)
         + plain("Друзья", -232, -18, 50, fill="#1d2448") + plain("Ты с нами сегодня?", -232, 52, 54, fill="#1d2448"))
    return f'<g transform="translate(540 {y:.1f}) scale({s:.4f})">{b}</g>'


def frame_s14(t):
    """«Вчера меня снова позвали в бар»: Дима за столом смотрит в телефон и улыбается, кот машет хвостом; сверху уведомление
    «Ты с нами сегодня?»; надпись «СНОВА ЗОВУТ»."""
    a, b = T0("s14"), T1("s14")
    t_n = W(48) - .1
    joy = ramp(t, t_n + .15, .2)
    o = desk_room(t, mode="evening" if False else "day", sun=1.0, list_on=False)
    f = dima_desk(t, "laugh82" if joy > .5 else "sure82", head_add=-.08 + .05 * joy)
    o.append(f["svg"])
    wx, wy = f["hold"]
    o.append(mini_phone(wx + 10, wy - 40, .5, -20, screen="#ffffff", inner=rect(-60, -112, 60, -70, BLUE)
                        + shape(lib.rrect(-50, -50, 50, 0, 10), "#ffffff", "", w=2, seed=5960)))
    if t > t_n:
        o.append(PR.sparkles(wx + 10, wy - 80, 1.4, bump(t, t_n, .05, .5), t, seed=13, n=5, r=150))
    hx, hy = f["head"]
    if joy > 0:
        o.append(PR.heart(hx + 150, hy - 160 - 30 * ramp(t, t_n + .3, .8), .5 * pop(t, t_n + .3, .25), beat=bump(t, t_n + .3, .05, .3)))
    o.append(cat(930, DESK_Y - 60, .42, t, dict(look=(-.7, -.5), smile=1.0, proud=joy, tail=22 * math.sin(t * 7))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_n, 8)
    return view("".join(o), 640 + dx, 920 + dy, 1.25 + .07 * u, 0, t=t, extra=notif(t, t_n))


# ═════════════════════════ призыв: s07 «КОТ», s08–s10 телефон на столе и кот ═════════════════════════
def frame_s07(t):
    """«Напиши «КОТ»»: поле комментария, крупно печатается жёлтое «КОТ»; Дима внизу слева, кот прыгает и садится рядом с ним."""
    a, b = T0("s07"), T1("s07")
    t_k = W(22) - .05
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
    t_j = a + .85
    j = ease_io(ramp(t, t_j, .4))
    x = 1180 + (620 - 1180) * j
    y = 1640 - 260 * math.sin(math.pi * j)
    o.append(cat(x, y, .9, t, dict(look=(-.7, -.4), legs=1.0 - j if j < 1 else 0.0, smile=1.0 if j >= 1 else .4, tail=10 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_k + .25, 8)
    return view("".join(o), 540 + dx, 1020 + dy, 1.0 + .06 * u, 0, bg=PAPER, t=t)


DESK_TOP = "#c9a77c"
PD = (420.0, 900.0, 1.0)                   # телефон на столе: центр и масштаб
LINE = "Прости! Я в деле"


def desk_top_bg():
    o = [rect(-1400, -1400, 2600, 3200, DESK_TOP)]
    for j in range(16):
        o.append(line([(-1400, -200 + 200 * j), (2600, -200 + 200 * j + 40)], 3, "#b08d64", taper=0, wmin=1, seed=6400 + j, op=.7))
    return "".join(o)


def desk_phone(t, screen):
    """Телефон стоит на подставке на столе (без руки): рамка, экран screen."""
    x, y, k = PD
    o = [blob(lib.rrect(x - 300 * k + 30, y - 520 * k + 40, x + 300 * k + 30, y + 520 * k + 40, 60 * k), "#000000", .22)]
    o.append(PR.phone_frame(x, y, k, 1.0, glow_=.3, seed=1))
    x0, y0, x1, y1 = PR.phone_frame_rect(x, y, k)
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    inner = f'<g transform="translate({x0:.1f} {y0:.1f}) scale({(x1 - x0) / (PX1 - PX0):.4f}) translate({-PX0:.1f} {-PY0:.1f})">{screen(PX0, PY0, PX1, PY1)}</g>'
    o.append(f'<g clip-path="url(#{c})">{inner}</g>')
    return "".join(o), (x0, y0, x1, y1)


def to_desk(px, py):
    x0, y0, x1, y1 = PR.phone_frame_rect(*PD)
    s = (x1 - x0) / (PX1 - PX0)
    return x0 + (px - PX0) * s, y0 + (py - PY0) * s


def hanging_clock(x0, y0, x1, y1, yy, t, sent_t=None):
    """Часики «висит 5 дн» у входящего сообщения."""
    k = pop(t, W(25) - .05, .2)
    if k <= .01:
        return ""
    if sent_t is not None:
        k *= 1 - ramp(t, sent_t, .15)
        if k <= .01:
            return ""
    w = 1 + .1 * bump(t, W(26), .05, .3)
    c = (f'<rect x="-110" y="-30" width="220" height="60" rx="30" fill="#e2574c"/>'
         + text("висит 5 дн", 0, 13, 34, fill="#ffffff", stroke="#e2574c", sw=1))
    return f'<g transform="translate({x0 + 150:.1f} {y0 + 330:.1f}) rotate(-3) scale({k * w:.4f})">{c}</g>'


def lena(t, typed_u=0.0, sent_t=None, shake_t=None):
    name, col = NAMES[3]
    return chat_screen(t, name, col, [("ну что, придёшь?", -10)], typed=LINE, typed_u=typed_u,
                       sent=(LINE, sent_t) if sent_t is not None else None, extra=lambda a, b_, c, d, e: hanging_clock(a, b_, c, d, e, t, sent_t))


def frame_s08(t):
    """«каждое висящее сообщение»: телефон на столе, висящий чат «Лена: ну что, придёшь?», на «висящее» часики «висит 5 дн»,
    на «сообщение» пузырь вздрагивает; кот сидит рядом с телефоном и смотрит на экран."""
    a, b = T0("s08"), T1("s08")
    body, _ = desk_phone(t, lena(t))
    o = [desk_top_bg(), body]
    o.append(cat(910, 1440, .95, t, dict(look=(-.8, -.6), perk=ramp(t, W(25), .2), tail=10 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(26), 7)
    return view("".join(o), 580 + dx, 1000 + dy, .9 + .06 * u, -1 + 2 * u, bg=DESK_TOP, t=t)


def frame_s09(t):
    """«ответом в одну строку»: камера ближе к полю ввода, одна строка печатается; кот рядом заглядывает в экран."""
    a, b = T0("s09"), T1("s09")
    body, _ = desk_phone(t, lena(t, typed_u=ramp(t, W(28), WE(31) - W(28))))
    o = [desk_top_bg(), body]
    o.append(cat(910, 1440, .95, t, dict(look=(-.9, -.4), smile=.5, tail=10 * math.sin(t * 3))))
    fx, fy = to_desk(PX0 + 300, PY1 - 78)
    if t > WE(31):
        o.append(PR.sparkles(fx, fy, 1.4, bump(t, WE(31), .05, .4), t, seed=21, n=5, r=180))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, WE(31), 6)
    return view("".join(o), 545 + dx, 1180 + dy, 1.25 + .06 * u, 1 - 2 * u, bg=DESK_TOP, t=t)


def frame_s10(t):
    """«который не страшно отправить»: на «страшно» лапа кота жмёт «отправить», строка улетает пузырём вверх, две синие галочки;
    кот машет хвостом и улыбается."""
    a, b = T0("s10"), T1("s10")
    t_send = W(35) - .05
    body, _ = desk_phone(t, lena(t, typed_u=1.0, sent_t=t_send))
    o = [desk_top_bg(), body]
    sx, sy = to_desk(*SEND)
    reach = ease_io(ramp(t, t_send - .45, .35)) * (1 - ease_io(ramp(t, t_send + .1, .3)))
    done = t > t_send
    o.append(cat(910, 1440, .95, t, dict(look=(-.9, -.6) if not done else (-.3, -.2), smile=1.0 if done else .4,
                                         tail=(22 * math.sin(t * 7)) if done else 8 * math.sin(t * 3))))
    if reach > .01:
        tip = (sx + 10 + 300 * (1 - reach), sy + 6 + 160 * (1 - reach))
        o.append(people.cat_forearm((tip[0] + 260, tip[1] + 220), tip, k=1.6, claw=0.0, seed=3))
    if done:
        o.append(PR.tap_rings(sx, sy, ramp(t, t_send, .3), 1.0, col="#FFD23F"))
        o.append(PR.sparkles(*to_desk(540, PY0 + 400), 1.8, bump(t, t_send + .35, .05, .45), t, seed=22, n=6, r=200))
        o.append(PR.heart(860, 900 - 30 * ramp(t, t_send + .4, .8), .5 * pop(t, t_send + .4, .25), beat=bump(t, t_send + .4, .05, .3)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_send, 8)
    return view("".join(o), 580 + dx, 1020 + dy, .95 + .05 * u, 0, bg=DESK_TOP, t=t)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
