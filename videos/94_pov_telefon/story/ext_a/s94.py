"""Рилс 94 «POV: ты взял телефон на минутку», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — общее время.
Весь ролик глазами Димы: в кадре его руки, телефон, комната, окно, кот на коленях; самого Димы нет. Камера дышит, как
голова (breath), моргания затемняют край сверху и снизу (blink). Время — только из shots.json (t0/t1) и voice/words.json;
числа в коде — длительности движений. Хук s01 — влёт правил 28–29 (anim.hook_cam); s10 — петля: к концу кадр как первый
(день за окном, лента на той же позиции, кот молодой).
NOCAM=1 — без влёта, тряски, дыхания, моргания и заголовка (замер движения рисунка)."""
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
import cat as CT  # noqa: E402
from ink import band  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape  # noqa: E402

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
END = SH["end"]
NOCAM = bool(os.environ.get("NOCAM"))


def W(i):
    return WORDS[i]["start"]


def WE(i):
    return WORDS[i]["end"]


def T0(sid):
    return SHOT[sid]["t0"]


def T1(sid):
    return SHOT[sid]["t1"]


def ramp(t, a, d):
    return clamp((t - a) / d)


def bump(t, a, up=.07, down=.25):
    u = t - a
    if u <= 0:
        return 0.0
    return min(1.0, u / up) * (math.exp(-(u - up) / down) if u > up else 1.0)


def shake(t, a, amp=10.0, dur=.3, f=12.0):
    u = t - a
    if u <= 0 or u > dur * 3 or NOCAM:
        return 0.0, 0.0
    e = math.exp(-u / dur * 2.5)
    return amp * e * math.sin(2 * math.pi * f * u), amp * .6 * e * math.cos(2 * math.pi * f * .8 * u)


def tf(inner, x, y, k=1.0, rot=0.0):
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k:.4f})">{inner}</g>'


def mixc(a, b, u):
    return lib.mix(a, b, clamp(u))


# ═════════════════════════ голова: дыхание и моргание ═════════════════════════
def breath(t):
    if NOCAM:
        return 0.0, 0.0, 0.0
    dx = 7 * math.sin(2 * math.pi * t / 3.7) + 3 * math.sin(2 * math.pi * t / 1.7 + 1)
    dy = 6 * math.sin(2 * math.pi * t / 4.3 + 1) + 2.5 * math.sin(2 * math.pi * t / 2.1)
    return dx, dy, .45 * math.sin(2 * math.pi * t / 5.1)


BLINKS = [2.02, 5.0, 9.98, 12.3, 15.3]          # не в хуке и не на склейках


def blink_layer(t):
    if NOCAM:
        return ""
    b = 0.0
    for a in BLINKS:
        u = (t - a) / .17
        if 0 <= u <= 1:
            b = max(b, math.sin(math.pi * u) ** .8)
    if b < .02:
        return ""
    h = 960 * b
    g = lib.lin_grad([(0, "#0c0a10", 1), (.82, "#0c0a10", 1), (1, "#0c0a10", 0)], 0, 0, 0, 1)
    g2 = lib.lin_grad([(0, "#0c0a10", 0), (.18, "#0c0a10", 1), (1, "#0c0a10", 1)], 0, 0, 0, 1)
    return (f'<rect x="0" y="0" width="1080" height="{h + 90:.1f}" fill="url(#{g})"/>'
            f'<rect x="0" y="{1920 - h - 90:.1f}" width="1080" height="{h + 90:.1f}" fill="url(#{g2})"/>')


def title(t):
    if NOCAM:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, text=SH["title"]["text"], t_in=SH["title"]["t_in"], t_out=SH["title"]["t_out"], hits=hits)


def view(body, t, cx, cy, s, rot=0.0, over="", bg="#efe2c8"):
    bx, by, br = breath(t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx + bx, cy + by, s, rot + br)}">{body}</g>'
                   f'{blink_layer(t)}{over}')


# ═════════════════════════ время суток ═════════════════════════
def night_at(t):
    """0 — день, 1 — ночь: за время ленты комната темнеет (s03–s05), с подъёма головы — ночь; петля s10 — снова день."""
    if t >= T0("s10"):
        return 0.0
    return clamp(.15 * ramp(t, T0("s03"), T1("s03") - T0("s03")) + .15 * ramp(t, T0("s04"), T1("s04") - T0("s04"))
                 + .55 * ramp(t, T0("s05"), T1("s05") - T0("s05")) + .15 * ramp(t, T0("s06"), .4))


# ═════════════════════════ комната и окно ═════════════════════════
WX0, WY0, WX1, WY1 = 120.0, -40.0, 960.0, 800.0


def cloud(x, y, k, op=1.0):
    pts = []
    for (cx, cy, r) in ((-60, 10, 46), (-10, -16, 60), (52, 0, 50), (90, 18, 34), (-96, 22, 30)):
        pts.append(blob(ellipse_pts(x + cx * k, y + cy * k, r * k, r * .8 * k, 18), "#ffffff", op))
    return "".join(pts)


def sky(t, night):
    o = []
    gd = lib.lin_grad([(0, "#58b4f0", 1), (1, "#c9ecff", 1)], 0, 0, 0, 1)
    o.append(f'<rect x="{WX0}" y="{WY0}" width="{WX1 - WX0}" height="{WY1 - WY0}" fill="url(#{gd})"/>')
    if night < .999:
        day = []
        sg = lib.rad_grad([(0, "#fff6c8", .95), (.35, "#ffe58a", .55), (1, "#ffe58a", 0)], 760, 150, 230)
        day.append(f'<circle cx="760" cy="150" r="230" fill="url(#{sg})"/>')
        day.append(shape(ellipse_pts(760, 150, 62, 62, 28), "#ffd54a", "", w=3.5, seed=941, ink_color="#e0a020"))
        for j, (x, y, k) in enumerate(((260, 120, 1.0), (520, 330, .8), (860, 420, .7), (330, 560, 1.1))):
            xx = WX0 - 200 + ((x + 70 * t * (1 + .3 * j)) - WX0 + 200) % (WX1 - WX0 + 400)
            day.append(cloud(xx, y, k, .92))
        # крыши и деревья за окном
        day.append(blob([(WX0, 700), (260, 640), (330, 660), (420, 600), (520, 640), (640, 590), (760, 630), (WX1, 610), (WX1, WY1), (WX0, WY1)],
                        "#8fcf86"))
        for j, (x, r) in enumerate(((210, 80), (430, 96), (700, 86), (900, 70))):
            sw = 4 * math.sin(t * 2.1 + j)
            day.append(shape(ellipse_pts(x + sw, 640 - r * .4, r, r * .85, 20), "#5fae5e", blob(ellipse_pts(x + sw + r * .3, 650 - r * .3, r * .6, r * .5, 14), "#4a9450", .8),
                             w=3.5, seed=950 + j))
        o.append(f'<g opacity="{1 - night:.3f}">{"".join(day)}</g>')
    if night > .001:
        nt = []
        gn = lib.lin_grad([(0, "#0b1230", 1), (1, "#2b3768", 1)], 0, 0, 0, 1)
        nt.append(f'<rect x="{WX0}" y="{WY0}" width="{WX1 - WX0}" height="{WY1 - WY0}" fill="url(#{gn})"/>')
        for j in range(26):
            x = WX0 + 30 + (j * 263) % (WX1 - WX0 - 60)
            y = WY0 + 60 + (j * 151) % 540
            tw = .55 + .45 * math.sin(t * 5 + j * 1.7)
            nt.append(f'<circle cx="{x}" cy="{y}" r="{2.2 + (j % 3)}" fill="#fff8d8" opacity="{tw:.2f}"/>')
        mg = lib.rad_grad([(0, "#fff4c0", .55), (1, "#fff4c0", 0)], 690, 230, 200)
        nt.append(f'<circle cx="690" cy="230" r="200" fill="url(#{mg})"/>')
        nt.append(shape(ellipse_pts(690, 230, 78, 78, 30), "#fff1b0", blob(ellipse_pts(720, 205, 70, 74, 26), "#1a2348"), w=3.5, seed=942,
                        ink_color="#c9b46a"))
        nt.append(blob([(WX0, 700), (260, 640), (330, 660), (420, 600), (520, 640), (640, 590), (760, 630), (WX1, 610), (WX1, WY1), (WX0, WY1)], "#1a2140"))
        for j, (x, y) in enumerate(((300, 650), (450, 610), (620, 640), (840, 625))):
            if (j + int(t * 1.3)) % 4:
                nt.append(f'<rect x="{x}" y="{y}" width="16" height="20" fill="#ffd36a" opacity=".85"/>')
        o.append(f'<g opacity="{night:.3f}">{"".join(nt)}</g>')
    return "".join(o)


def room(t, night):
    wall = mixc("#efe2c8", "#2a2742", night)
    o = [f'<rect x="-900" y="-1700" width="2900" height="4600" fill="{wall}"/>']
    if night < .99:      # солнечное пятно на стене
        o.append(blob([(-200, 300), (120, 260), (60, 980), (-260, 1040)], "#fff4d6", .5 * (1 - night)))
        o.append(blob([(960, 260), (1300, 300), (1360, 1040), (1020, 980)], "#fff4d6", .5 * (1 - night)))
    clip = lib.clip_rect(WX0, WY0, WX1 - WX0, WY1 - WY0)
    o.append(f'<g clip-path="url(#{clip})">{sky(t, night)}</g>')
    fr = mixc("#f7f1e6", "#5a5674", night)
    frs = mixc("#d8ccb6", "#3c3956", night)
    for (x0, y0, x1, y1) in ((WX0 - 26, WY0 - 26, WX1 + 26, WY0), (WX0 - 26, WY1, WX1 + 26, WY1 + 26), (WX0 - 26, WY0, WX0, WY1),
                             (WX1, WY0, WX1 + 26, WY1), ((WX0 + WX1) / 2 - 11, WY0, (WX0 + WX1) / 2 + 11, WY1), (WX0, 360, WX1, 380)):
        o.append(shape(lib.rect_pts(x0, y0, x1, y1), fr, blob(lib.rect_pts(x0, y1 - 6, x1, y1), frs), w=3.4, seed=int(x0 + y0)))
    o.append(shape(lib.rect_pts(WX0 - 70, WY1 + 20, WX1 + 70, WY1 + 70), mixc("#e8dcc6", "#47435f", night),
                   blob(lib.rect_pts(WX0 - 70, WY1 + 56, WX1 + 70, WY1 + 70), frs), w=4, seed=961))
    # цветок на подоконнике
    o.append(shape([(820, WY1 + 20), (900, WY1 + 20), (890, WY1 - 50), (830, WY1 - 50)], mixc("#e0784a", "#6a3a40", night), "", w=3.4, seed=962))
    for j, a in enumerate((-40, -10, 25, 55)):
        sw = 5 * math.sin(t * 1.6 + j)
        ax, ay = 860 + 90 * math.sin(math.radians(a)) + sw, WY1 - 50 - 90 * math.cos(math.radians(a))
        o.append(shape(band([(860, WY1 - 50), ((860 + ax) / 2, (WY1 - 50 + ay) / 2 - 10), (ax, ay)], 4, 30, step=6),
                       mixc("#62b06a", "#2f5a48", night), "", w=3, seed=963 + j))
    # шторы
    for side in (-1, 1):
        x0 = WX0 - 90 if side < 0 else WX1 + 90
        sw = 10 * math.sin(t * 1.3 + side)
        pts = [(x0 - side * 90, WY0 - 80), (x0 + side * 40, WY0 - 80), (x0 + side * 20 + sw, 400), (x0 + side * 50 + sw * 1.4, WY1 + 260),
               (x0 - side * 100, WY1 + 260)]
        inner = "".join(line([(x0 + side * k_ + sw * .5, WY0 - 60), (x0 + side * k_ * .8 + sw, WY1 + 240)], 2.4, mixc("#c45a50", "#4a2a3a", night),
                             seed=970 + k_, op=.7) for k_ in (-50, 0))
        o.append(shape(pts, mixc("#e9786a", "#5a3048", night), inner, w=4, seed=975 + side))
    return "".join(o)


# ═════════════════════════ экран телефона (координаты экрана: 0..SW × 0..SH) ═════════════════════════
SW, SH_ = 456.0, 924.0
CARD, GAP = 390.0, 22.0
PALS = [("#ff8a5c", "#ffd36e"), ("#5cc8ff", "#2f6fd6"), ("#9be36b", "#2e9e5a"), ("#c79bff", "#7a4fd6"), ("#ff6fa3", "#ffe0ea"),
        ("#ffd25c", "#ff7a3d")]


def heart(x, y, k, col="#ffffff", fill="none", sw=4.0):
    d = (f"M{x} {y + 14 * k} C{x - 26 * k} {y - 4 * k} {x - 18 * k} {y - 26 * k} {x} {y - 12 * k} "
         f"C{x + 18 * k} {y - 26 * k} {x + 26 * k} {y - 4 * k} {x} {y + 14 * k}Z")
    return f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"/>'


def bubble(x, y, k, col="#ffffff", sw=4.0):
    return (f'<ellipse cx="{x}" cy="{y - 2 * k}" rx="{18 * k}" ry="{14 * k}" fill="none" stroke="{col}" stroke-width="{sw}"/>'
            f'<path d="M{x - 10 * k} {y + 9 * k} L{x - 16 * k} {y + 20 * k} L{x - 2 * k} {y + 11 * k}" fill="none" stroke="{col}" stroke-width="{sw}" '
            f'stroke-linejoin="round"/>')


def plane(x, y, k, col="#ffffff", fill="none", sw=4.0, rot=0.0):
    p = [(-20, 2), (22, -18), (6, 20), (0, 8)]
    pts = " ".join(f"{px * k:.1f},{py * k:.1f}" for px, py in p)
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})"><polygon points="{pts}" fill="{fill}" stroke="{col}" stroke-width="{sw}" '
            f'stroke-linejoin="round"/><path d="M{22 * k:.1f} {-18 * k:.1f} L{0:.1f} {8 * k:.1f} L{-2 * k:.1f} {18 * k:.1f}" fill="none" '
            f'stroke="{col}" stroke-width="{sw * .8:.1f}" stroke-linejoin="round"/></g>')


def card_art(j, x, y, w, h, t):
    bg, ac = PALS[j % len(PALS)]
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>']
    kind = j % 4
    if kind == 0:      # солнце и холмы
        o.append(f'<circle cx="{x + w * .72}" cy="{y + h * .32}" r="{h * .17}" fill="{ac}"/>')
        o.append(f'<path d="M{x} {y + h} L{x} {y + h * .7} Q{x + w * .3} {y + h * .45} {x + w * .55} {y + h * .72} Q{x + w * .8} {y + h * .55} '
                 f'{x + w} {y + h * .68} L{x + w} {y + h}Z" fill="{lib.mul(bg, (.75, .8, .8))}"/>')
    elif kind == 1:    # человечек-кружок машет
        a = 25 * math.sin(t * 9 + j)
        o.append(f'<circle cx="{x + w * .5}" cy="{y + h * .36}" r="{h * .13}" fill="{ac}"/>')
        o.append(f'<rect x="{x + w * .41}" y="{y + h * .5}" width="{w * .18}" height="{h * .38}" rx="{w * .06}" fill="{ac}"/>')
        o.append(f'<rect x="{x + w * .57}" y="{y + h * .52}" width="{w * .2}" height="{h * .06}" rx="8" fill="{ac}" '
                 f'transform="rotate({-40 + a:.1f} {x + w * .58} {y + h * .55})"/>')
    elif kind == 2:    # горы
        o.append(f'<path d="M{x} {y + h} L{x + w * .3} {y + h * .3} L{x + w * .55} {y + h * .75} L{x + w * .72} {y + h * .45} L{x + w} {y + h}Z" '
                 f'fill="{ac}"/>')
        o.append(f'<path d="M{x + w * .3} {y + h * .3} L{x + w * .38} {y + h * .45} L{x + w * .22} {y + h * .45}Z" fill="#ffffff"/>')
    else:              # волны и мяч
        for k_ in range(3):
            yy = y + h * (.55 + .14 * k_)
            o.append(f'<path d="M{x} {yy} Q{x + w * .25} {yy - 24} {x + w * .5} {yy} T{x + w} {yy} L{x + w} {y + h} L{x} {y + h}Z" fill="{ac}" '
                     f'opacity="{.45 + .2 * k_:.2f}"/>')
        o.append(f'<circle cx="{x + w * .3}" cy="{y + h * .32 - 20 * abs(math.sin(t * 6 + j))}" r="{h * .1}" fill="#ffffff"/>')
    return "".join(o)


def feed(pos, t, share=None):
    """Лента карточек; pos — сколько пикселей пролистано. share — (press 0..1, pop 0..1): самолётик у карточки на экране."""
    o = [f'<rect width="{SW}" height="{SH_}" fill="#f2f2f6"/>']
    step = CARD + GAP
    j0 = int(math.floor((pos - 60) / step)) - 1
    for j in range(j0, j0 + 5):
        y = 60 + j * step - pos
        if y > SH_ or y + CARD < 0:
            continue
        o.append(f'<rect x="14" y="{y:.1f}" width="{SW - 28}" height="{CARD}" rx="22" fill="#ffffff"/>')
        c = lib.clip_rect(14, y, SW - 28, 260, 22)
        o.append(f'<g clip-path="url(#{c})">{card_art(j, 14, y, SW - 28, 260, t)}</g>')
        bg, ac = PALS[j % len(PALS)]
        o.append(f'<circle cx="52" cy="{y + 300:.1f}" r="22" fill="{ac}"/>')
        o.append(f'<rect x="88" y="{y + 286:.1f}" width="{150 + 40 * (j % 3)}" height="12" rx="6" fill="#c9c9d4"/>')
        o.append(f'<rect x="88" y="{y + 308:.1f}" width="{100 + 30 * (j % 2)}" height="10" rx="5" fill="#dedee6"/>')
        o.append(heart(48, y + 356, .85, "#4a4a5a", sw=3.4))
        o.append(bubble(108, y + 356, .85, "#4a4a5a", sw=3.4))
        if share is not None and j == SHARE_J:
            pr, pp = share
            k = .95 * (1 - .25 * pr) + .5 * bump_(pp)
            col = mixc("#4a4a5a", "#2f8cff", pp)
            if pp > 0:
                o.append(f'<circle cx="168" cy="{y + 356:.1f}" r="{26 + 30 * pp:.1f}" fill="#2f8cff" opacity="{.25 * (1 - pp):.3f}"/>')
            o.append(plane(168, y + 356, k * 1.0, col, mixc("#ffffff", "#2f8cff", pp), 3.6))
        else:
            o.append(plane(168, y + 356, .85, "#4a4a5a", "none", 3.4))
    o.append(status_bar("#2a2a34"))
    return "".join(o)


SHARE_J = 30


def bump_(u):
    return math.sin(math.pi * clamp(u)) if 0 < u < 1 else 0.0


def status_bar(col):
    o = [f'<rect x="{SW - 70}" y="20" width="40" height="18" rx="5" fill="none" stroke="{col}" stroke-width="2.4"/>',
         f'<rect x="{SW - 66}" y="24" width="26" height="10" rx="2" fill="{col}"/>']
    for k in range(4):
        o.append(f'<rect x="{SW - 140 + k * 11}" y="{38 - 6 - 4 * k}" width="7" height="{6 + 4 * k}" rx="1.5" fill="{col}"/>')
    o.append(f'<rect x="{SW / 2 - 60}" y="14" width="120" height="30" rx="15" fill="#0b0b10"/>')
    return "".join(o)


def lock(t, wake=1.0, clock_k=1.0, notif=None):
    """Экран блокировки: обои, часы со стрелками без цифр; notif — (drop 0..1, press 0..1, open 0..1)."""
    g = lib.lin_grad([(0, "#3a2a7a", 1), (.55, "#c0508a", 1), (1, "#ffb067", 1)], 0, 0, 0, 1)
    o = [f'<rect width="{SW}" height="{SH_}" fill="url(#{g})"/>']
    o.append(blob(ellipse_pts(SW * .2, SH_ * .8, 160, 120, 20), "#ffcf8a", .35))
    o.append(blob(ellipse_pts(SW * .9, SH_ * .55, 140, 160, 20), "#7a5ad6", .35))
    cx, cy, r = SW / 2, 290.0, 150 * clock_k
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 10}" fill="#ffffff" opacity=".18"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fbf8ff" opacity=".93"/>')
    for k in range(12):
        a = math.radians(k * 30)
        r0 = r * (.8 if k % 3 == 0 else .87)
        o.append(f'<line x1="{cx + r0 * math.sin(a):.1f}" y1="{cy - r0 * math.cos(a):.1f}" x2="{cx + r * .94 * math.sin(a):.1f}" '
                 f'y2="{cy - r * .94 * math.cos(a):.1f}" stroke="#2a2440" stroke-width="{7 if k % 3 == 0 else 4}" stroke-linecap="round"/>')
    mins = 47 + (t - 3.0) * 6          # минутная стрелка ползёт: время уходит
    hrs = 9 + mins / 60
    for ang, L, wd, col in ((hrs * 30, .5, 11, "#2a2440"), (mins * 6, .74, 7, "#2a2440"), (int(t * 2) * 6 * 5, .8, 3, "#ff4a5a")):
        a = math.radians(ang)
        o.append(f'<line x1="{cx - .12 * r * math.sin(a):.1f}" y1="{cy + .12 * r * math.cos(a):.1f}" x2="{cx + L * r * math.sin(a):.1f}" '
                 f'y2="{cy - L * r * math.cos(a):.1f}" stroke="{col}" stroke-width="{wd}" stroke-linecap="round"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="#ff4a5a"/>')
    o.append(f'<circle cx="70" cy="{SH_ - 90}" r="36" fill="#000000" opacity=".25"/><circle cx="{SW - 70}" cy="{SH_ - 90}" r="36" fill="#000000" '
             f'opacity=".25"/>')
    o.append(f'<rect x="70" y="{SH_ - 66}" width="20" height="30" rx="5" fill="#ffffff" opacity=".85"/>')
    o.append(f'<rect x="{SW - 88}" y="{SH_ - 102}" width="36" height="26" rx="6" fill="#ffffff" opacity=".85"/>')
    o.append(f'<rect x="{SW / 2 - 70}" y="{SH_ - 22}" width="140" height="8" rx="4" fill="#ffffff" opacity=".8"/>')
    if notif:
        dr, pr, op_ = notif
        y = -150 + (520 + 150) * dr
        k = 1 - .05 * pr
        x0, x1 = 22.0, SW - 22
        h = 120.0
        if op_ > 0:     # открывается: плашка растёт на весь экран
            u = ease_io(op_)
            x0, x1, y, h = x0 * (1 - u), x1 + (SW - x1) * u, y * (1 - u), h + (SH_ - h) * u
        gl = f'<rect x="{x0 - 4}" y="{y - 4}" width="{x1 - x0 + 8}" height="{h + 8}" rx="30" fill="#ffffff" opacity="{.5 * pr:.2f}"/>' if pr > 0 else ""
        pl = (gl + f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{h}" rx="28" fill="{mixc("#ffffff", "#ff5a7a", op_)}" opacity=".95"/>'
              f'<rect x="{x0 + 20}" y="{y + 26}" width="68" height="68" rx="18" fill="#ff3a5c"/>'
              f'<polygon points="{x0 + 46},{y + 44} {x0 + 46},{y + 76} {x0 + 72},{y + 60}" fill="#ffffff"/>'
              f'<rect x="{x0 + 108}" y="{y + 34}" width="190" height="16" rx="8" fill="#8a8aa0"/>'
              f'<rect x="{x0 + 108}" y="{y + 64}" width="260" height="13" rx="6.5" fill="#c4c4d2"/>'
              f'<circle cx="{x1 - 34}" cy="{y + 34}" r="9" fill="#ff3a5c"/>')
        o.append(f'<g transform="translate({SW / 2} {y + 60}) scale({k:.3f}) translate({-SW / 2} {-(y + 60)})">{pl}</g>')
    o.append(status_bar("#ffffff"))
    return f'<g opacity="{wake:.3f}">{"".join(o)}</g>' if wake < 1 else "".join(o)


VIDS = [("#ff5a5f", "#ffd25c", "ball"), ("#2bb3a3", "#fff3b0", "dance"), ("#6a5cff", "#ff9ad5", "cat"), ("#ff9f1c", "#ffffff", "star"),
        ("#1f9bff", "#b8f0ff", "wave"), ("#e0407a", "#ffe066", "ball"), ("#22c55e", "#fef08a", "dance"), ("#8b5cf6", "#fde68a", "star")]


def video(i, t):
    bg, ac, kind = VIDS[i % len(VIDS)]
    o = [f'<rect width="{SW}" height="{SH_}" fill="{bg}"/>']
    o.append(blob(ellipse_pts(SW * .5, SH_ * .45, 260, 260, 26), lib.mul(bg, (1.15, 1.15, 1.15)), .5))
    cx, cy = SW * .46, SH_ * .45
    if kind == "ball":
        h = abs(math.sin(t * 7)) * 160
        o.append(f'<ellipse cx="{cx}" cy="{cy + 190}" rx="{70 - h * .15:.1f}" ry="14" fill="#000000" opacity=".2"/>')
        o.append(f'<circle cx="{cx}" cy="{cy + 120 - h:.1f}" r="70" fill="{ac}"/>')
        o.append(f'<path d="M{cx - 70} {cy + 120 - h:.1f} Q{cx} {cy + 160 - h:.1f} {cx + 70} {cy + 120 - h:.1f}" fill="none" stroke="{bg}" stroke-width="8"/>')
    elif kind == "dance":
        a = 30 * math.sin(t * 10)
        o.append(f'<circle cx="{cx + 10 * math.sin(t * 10):.1f}" cy="{cy - 110}" r="54" fill="{ac}"/>')
        o.append(f'<rect x="{cx - 40}" y="{cy - 50}" width="80" height="170" rx="36" fill="{ac}"/>')
        for s_ in (-1, 1):
            o.append(f'<rect x="{cx - 8}" y="{cy - 40}" width="150" height="26" rx="13" fill="{ac}" '
                     f'transform="rotate({(-90 if s_ < 0 else -20) + a * s_:.1f} {cx} {cy - 30})"/>')
    elif kind == "cat":
        o.append(f'<ellipse cx="{cx}" cy="{cy + 80}" rx="110" ry="130" fill="{ac}"/>')
        o.append(f'<circle cx="{cx}" cy="{cy - 80}" r="86" fill="{ac}"/>')
        for s_ in (-1, 1):
            o.append(f'<polygon points="{cx + s_ * 30},{cy - 150} {cx + s_ * 84},{cy - 196} {cx + s_ * 80},{cy - 110}" fill="{ac}"/>')
            o.append(f'<ellipse cx="{cx + s_ * 32}" cy="{cy - 86}" rx="12" ry="{16 * (1 - .9 * (int(t * 3) % 5 == 0))}" fill="{bg}"/>')
        o.append(f'<path d="M{cx + 100} {cy + 160} Q{cx + 200} {cy + 120 + 30 * math.sin(t * 6):.1f} {cx + 170} {cy}" fill="none" '
                 f'stroke="{ac}" stroke-width="26" stroke-linecap="round"/>')
    elif kind == "star":
        a = t * 200
        pts = []
        for k in range(10):
            rr = 130 if k % 2 == 0 else 56
            an = math.radians(a + k * 36)
            pts.append(f"{cx + rr * math.sin(an):.1f},{cy - rr * math.cos(an):.1f}")
        o.append(f'<polygon points="{" ".join(pts)}" fill="{ac}"/>')
    else:
        for k in range(4):
            yy = cy - 60 + k * 70
            ph = t * 6 + k
            o.append(f'<path d="M0 {yy} Q{SW * .25} {yy - 40 * math.sin(ph):.1f} {SW * .5} {yy} T{SW} {yy} L{SW} {SH_} L0 {SH_}Z" fill="{ac}" '
                     f'opacity="{.3 + .15 * k:.2f}"/>')
    # интерфейс видео: значки справа, полосы снизу, прогресс
    o.append(heart(SW - 50, SH_ - 360, 1.1, "#ffffff", "#ffffff" if i % 2 else "none", 4.4))
    o.append(bubble(SW - 50, SH_ - 270, 1.1, "#ffffff", 4.4))
    o.append(plane(SW - 50, SH_ - 180, 1.1, "#ffffff", "none", 4.4))
    o.append(f'<circle cx="54" cy="{SH_ - 150}" r="26" fill="#ffffff" opacity=".9"/>')
    o.append(f'<rect x="94" y="{SH_ - 164}" width="170" height="14" rx="7" fill="#ffffff" opacity=".9"/>')
    o.append(f'<rect x="30" y="{SH_ - 110}" width="300" height="12" rx="6" fill="#ffffff" opacity=".7"/>')
    o.append(f'<rect x="0" y="{SH_ - 8}" width="{SW}" height="8" fill="#ffffff" opacity=".3"/>')
    o.append(f'<rect x="0" y="{SH_ - 8}" width="{SW * ((t * .9) % 1):.1f}" height="8" fill="#ffffff"/>')
    o.append(status_bar("#ffffff"))
    return "".join(o)


def video_stack(t, changes):
    """Ролики сменяются смахиванием вверх на моментах changes (0.13 с на смену)."""
    i = sum(1 for c in changes if t >= c)
    last = max([c for c in changes if t >= c], default=None)
    if last is None or t - last > .13:
        return video(i, t)
    u = ease_out((t - last) / .13, 2)
    return (f'<g transform="translate(0 {-SH_ * u:.1f})">{video(i - 1, t)}</g>'
            f'<g transform="translate(0 {SH_ * (1 - u):.1f})">{video(i, t)}</g>')


def black(t, flash=0.0):
    g = lib.lin_grad([(0, "#2a2c36", 1), (.5, "#0c0d12", 1), (1, "#16171e", 1)], 0, 0, 1, 1)
    o = f'<rect width="{SW}" height="{SH_}" fill="url(#{g})"/>'
    o += f'<path d="M{SW * .55} 0 L{SW} 0 L{SW} {SH_ * .35}Z" fill="#ffffff" opacity=".06"/>'
    if flash > 0:
        o += f'<rect width="{SW}" height="{SH_}" fill="#ffffff" opacity="{flash:.3f}"/>'
    return o


# ═════════════════════════ руки и телефон ═════════════════════════
SKIN, SKIN_SH, SKIN_SH2, NAIL = "#ecc4a2", "#d39f83", "#bf8a74", "#f6d9cb"
TOP, TOP_SH = "#d4a23e", "#a97b25"
LEGS, LEGS_SH = "#3d4c6e", "#2c3854"


def lap(night):
    o = []
    for j, (x, w_) in enumerate(((330, 360), (760, 380))):
        pts = ellipse_pts(x, 1720, w_ * .62, 330, 26)
        o.append(shape(pts, mixc(LEGS, "#1c2238", night * .7), blob(ellipse_pts(x + 60, 1800, w_ * .5, 260, 20), mixc(LEGS_SH, "#141a2c", night * .7), .7)
                       + line([(x - 40, 1450), (x - 10, 1700), (x + 20, 2000)], 2.4, "#5f6f92", seed=980 + j, op=.6), w=5, seed=982 + j))
    return "".join(o)


def sleeve(a, b, w0, w1, seed, night):
    pts = band([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), b], w0, w1, step=8)
    inner = line([(a[0] + 30, a[1]), (b[0] + 10, b[1] + 30)], 3, TOP_SH, seed=seed + 1, op=.7)
    return shape(pts, mixc(TOP, "#6a5230", night * .6), inner, w=5, seed=seed)


def fingertip(x, y, side, k=1.0, seed=0):
    """Кончик пальца, загнутый через край телефона: side −1 — палец выходит из-за левого края."""
    pts = band([(x + side * 34 * k, y), (x + side * 10 * k, y - 2 * k), (x - side * 18 * k, y + 2 * k)], 32 * k, 26 * k, step=2.5, cap=True)
    nail = blob(ellipse_pts(x - side * 8 * k, y + 1, 8 * k, 9 * k, 10), NAIL, .9)
    return shape(pts, SKIN, nail + line([(x + side * 14 * k, y - 10 * k), (x + side * 16 * k, y + 10 * k)], 1.5, SKIN_SH2, seed=seed + 1, op=.7), w=3.2,
                 seed=seed)


def thumb(base, tip, press=0.0, seed=0):
    bx, by = base
    tx, ty = tip
    mid = (bx + (tx - bx) * .55 + 18, by + (ty - by) * .55 + 10)
    w_tip = 46 * (1 + .08 * press)
    pts = band([(bx, by + 40), (bx, by), mid, (tx, ty)], 74, w_tip, step=3, cap=True)
    ang = math.atan2(ty - mid[1], tx - mid[0])
    nx, ny = tx - 16 * math.cos(ang), ty - 16 * math.sin(ang)
    inner = blob(ellipse_pts(nx, ny, 17, 15, 14, rot=math.degrees(ang)), NAIL, .95)
    inner += line([(mid[0] - 22, mid[1] + 6), (mid[0], mid[1] - 2), (mid[0] + 20, mid[1] + 8)], 1.8, SKIN_SH2, seed=seed + 2, op=.8)
    inner += blob(band([(bx, by + 30), mid], 40, 20, step=6), SKIN_SH, .45)
    return shape(pts, SKIN, inner, w=3.6, seed=seed)


def phone_rig(t, screen, px=540.0, py=850.0, rot=0.0, tip=None, press=0.0, night=0.0, glow=.6, cat=""):
    """Колени, рукава, ладони, телефон с экраном, пальцы на краях и большой палец (tip — точка экрана, None — палец у края).
    Ночью всё, кроме экрана, темнеет, руки подсвечены экраном."""
    o = [lap(night)]
    o.append(sleeve((60, 2150), (260, 1290), 230, 160, 990, night))
    o.append(sleeve((1030, 2150), (830, 1290), 230, 160, 993, night))
    o.append(cat)
    ph = []
    # ладони за телефоном
    ph.append(shape(ellipse_pts(-250, 360, 95, 190, 22, rot=12), SKIN, blob(ellipse_pts(-275, 420, 60, 130, 16), SKIN_SH, .6), w=3.8, seed=1001))
    ph.append(shape(ellipse_pts(258, 360, 95, 190, 22, rot=-12), SKIN, blob(ellipse_pts(283, 420, 60, 130, 16), SKIN_SH, .6), w=3.8, seed=1002))
    # корпус
    ph.append(shape(lib.rrect(-250, -490, 250, 490, 62), "#24262e", blob(lib.rrect(-246, -486, 246, 486, 58), "#3a3d48", .9)
                    + blob(lib.rrect(-236, -476, 236, 476, 50), "#101116"), w=4.6, seed=1003))
    ph.append(f'<rect x="250" y="-260" width="8" height="90" rx="4" fill="#3a3d48"/><rect x="-258" y="-300" width="8" height="60" rx="4" fill="#3a3d48"/>')
    c = lib.clip_rect(-SW / 2, -SH_ / 2, SW, SH_, 44)
    ph.append(f'<g clip-path="url(#{c})"><g transform="translate({-SW / 2} {-SH_ / 2})">{screen}</g></g>')
    for j, y in enumerate((170, 260, 350)):
        ph.append(fingertip(-238, y - 60, -1, 1.15, seed=1010 + j * 3))
    for j, y in enumerate((150, 240)):
        ph.append(fingertip(238, y - 60, 1, 1.15, seed=1020 + j * 3))
    ph.append(thumb((-262, 470), (-200, 400), 0, seed=1030))           # левый большой — на нижней рамке
    if tip is None:
        tip = (410, 800)
    ph.append(thumb((262, 440), (tip[0] - SW / 2, tip[1] - SH_ / 2), press, seed=1040))
    o.append(tf("".join(ph), px, py, 1.0, rot))
    body = "".join(o)
    if night < .01:
        return body
    mid = lib.uid("m")
    lib.DEFS.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-2000" y="-3000" width="5000" height="8000">'
                    f'<rect x="-2000" y="-3000" width="5000" height="8000" fill="#fff"/>'
                    f'<g transform="translate({px} {py}) rotate({rot})"><rect x="{-SW / 2}" y="{-SH_ / 2}" width="{SW}" height="{SH_}" rx="44" fill="#000"/></g></mask>')
    gg = lib.rad_grad([(0, "#9fd0ff", .35 * night * glow), (1, "#9fd0ff", 0)], px, py, 700)
    return (body + f'<rect x="-2000" y="-3000" width="5000" height="8000" fill="#0a0818" opacity="{.5 * night:.3f}" mask="url(#{mid})"/>'
            f'<circle cx="{px}" cy="{py}" r="700" fill="url(#{gg})"/>')


# ═════════════════════════ кот ═════════════════════════
def cat(x, y, k, t, rub=1.0, age=0.0, look=(0.0, 0.0), blink=None, rot=0.0, tilt=None):
    """Кот на коленях; rub — трётся о руку (голова и тело качаются, глаза закрыты); age — постарел: седая морда, очки."""
    ph = math.sin(t * 2 * math.pi / .9)
    st = dict(look=look, tail=8 * math.sin(t * 1.9), flame_e=1.0 - .5 * age,
              tilt=(10 * rub * ph if tilt is None else tilt), smile=1.0 if rub > .5 else 0.0,
              blink=(rub if blink is None else blink), ear=.4 * rub * max(0, ph))
    rr = rot + 5 * rub * ph
    o = CT.draw(x, y, k, st, t)
    o = f'<g transform="rotate({rr:.2f} {x} {y})">{o}</g>'
    if age > .01:
        a = age
        ov = []
        ov.append(blob(ellipse_pts(836, 1122, 50, 30, 20), "#c9cdcf", .85 * a))
        ov.append(blob(ellipse_pts(836, 1146, 30, 14, 14), "#b9bdbf", .8 * a))
        for sx in (-1, 1):
            ov.append(blob(ellipse_pts(836 + sx * 46, 1026, 24, 9, 12), "#d6d9db", .9 * a))
            ov.append(blob(ellipse_pts(836 + sx * 84, 1090, 16, 22, 12), "#aeb3b5", .6 * a))
        ov.append(shape([(826, 1108), (846, 1108), (836, 1119)], "#c47a72", w=2.6, seed=262))
        ov.append(line([(822, 1126), (829, 1132), (836, 1126), (843, 1132), (850, 1126)], 3, seed=264, op=a))
        gl = "#3a2a1c"
        for ex in (792, 880):
            ov.append(f'<circle cx="{ex}" cy="1072" r="44" fill="#e8f6ff" fill-opacity=".22" stroke="{gl}" stroke-width="6"/>')
            ov.append(f'<path d="M{ex - 24} 1052 L{ex - 10} 1040" stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity=".8"/>')
        ov.append(f'<path d="M836 1066 Q836 1056 836 1066" stroke="{gl}" stroke-width="6"/><line x1="824" y1="1066" x2="848" y2="1066" stroke="{gl}" stroke-width="6"/>')
        ov.append(f'<line x1="748" y1="1064" x2="716" y2="1052" stroke="{gl}" stroke-width="5"/><line x1="924" y1="1064" x2="956" y2="1052" stroke="{gl}" stroke-width="5"/>')
        hy = -(1 + 0.012 * math.sin(t * 2 * math.pi / 3.1) - 1) * (CT.CBOT - CT.NECK[1])
        head = f'<g transform="translate(0 {hy:.2f}) rotate({st["tilt"]:.2f} {CT.NECK[0]} {CT.NECK[1]})" opacity="{min(1.0, a * 1.5):.3f}">{"".join(ov)}</g>'
        o += (f'<g transform="rotate({rr:.2f} {x} {y})"><g transform="translate({x:.2f} {y:.2f}) scale({k:.4f}) translate({-CT.CX} {-CT.CBOT})">'
              f'{head}</g></g>')
    return o


# ═════════════════════════ лента и большой палец ═════════════════════════
FLICK = .5        # период смахивания, с


def scroll_pos(t, v0=520.0, amp=330.0, phase=.08):
    """Пролистано к моменту t: ровная скорость + толчки от каждого смахивания (инерция ease_out)."""
    k0 = math.floor((t - phase) / FLICK)
    p = v0 * t
    for k in range(int(k0) - 40, int(k0) + 1):
        tk = phase + k * FLICK
        p += amp * ease_out((t - tk) / .32, 3)
    return p


def thumb_tip(t, phase=.08, x0=300.0, y_lo=760.0, y_hi=470.0):
    """Большой палец смахивает вверх (0.2 с), отрывается и возвращается вниз."""
    u = ((t - phase) % FLICK) / FLICK
    if u < .4:
        v = ease_io(u / .4)
        return x0 - 30 * v, y_lo + (y_hi - y_lo) * v
    v = ease_io((u - .4) / .6)
    return x0 - 30 * (1 - v) + 40 * math.sin(math.pi * v), y_hi + (y_lo - y_hi) * v


# ═════════════════════════ хук ═════════════════════════
HIT01 = W(0) + .3 * (WE(0) - W(0))       # ударный слог «POV»


def hook_scene(t, night=0.0):
    tt = t
    sway = 4 * math.sin(tt * 3.1)
    scr = feed(scroll_pos(tt), tt)
    c = cat(800, 1650, .95, tt, rub=1.0)
    return room(tt, night) + phone_rig(tt, scr, 540 + sway, 850 + 3 * math.sin(tt * 2.3), .8 * math.sin(tt * 1.7), thumb_tip(tt), night=night, cat=c)


def hook_wrap(body, t, hit, bg="#efe2c8"):
    import anim
    hc = anim.hook_cam(t, hit=hit)
    z, r, dx, dy = hc["zoom"], hc["rot"], hc["dx"], hc["dy"]
    piv = 960.0
    tr = f"translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) scale({z:.5f}) translate(-540 {-piv})"
    blur = ""
    amt = hc["zoom_blur"] / 0.07
    if amt > 0.03:
        for dk, op in ((.03, .30), (.06, .2), (.1, .12)):
            blur += (f'<use href="#hk94" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk94">{body}</g></g>{blur}'


HOOK_VIEW = (540.0, 900.0, 1.12)


def frame_s01(t):
    body = hook_scene(t)
    cx, cy, s = HOOK_VIEW
    dx, dy = shake(t, HIT01, 12)
    bx, by, br = breath(t)
    v = f'<g transform="{lib.cam(cx + dx + bx, cy + dy + by, s, br)}">{body}</g>'
    if NOCAM:
        return lib.svg('<rect width="1080" height="1920" fill="#efe2c8"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT01) + title(t))


def frame_s02(t):
    a, b = T0("s02"), T1("s02")
    off = W(7) + .35                     # «минутку»: экран гаснет
    u = ease_io(ramp(t, a, b - a))
    if t < off:
        scr = feed(scroll_pos(t, v0=700, amp=380), t)
        tip = thumb_tip(t, x0=290)
    else:
        scr = black(t, flash=.5 * (1 - ramp(t, off, .12)))
        tip = None
    sway = 4 * math.sin(t * 3.1)
    body = room(t, 0) + phone_rig(t, scr, 540 + sway, 850, .8 * math.sin(t * 1.7), tip, cat=cat(800, 1650, .95, t, rub=1.0))
    dx, dy = shake(t, W(7) + .1, 12)
    s = 1.2 + .14 * u + .06 * bump(t, W(7) + .1)
    return view(body, t, 540 + dx, 860 + dy, s, -1.2 * u, over=title(t))


def frame_s03(t):
    a, b = T0("s03"), T1("s03")
    on = W(8)
    n = night_at(t)
    wake = ease_out(ramp(t, on, .16))
    scr = black(t) if wake <= 0 else (black(t) + f'<g opacity="{wake:.3f}">{lock(t)}</g>')
    push = ease_io(ramp(t, on + .15, W(11) - on - .1))
    hit = bump(t, W(11) + .05, .06, .22)
    tip = (330, 830) if t < on + .1 else (330 + 60 * ease_io(ramp(t, on + .1, .3)), 830 + 140 * ease_io(ramp(t, on + .1, .3)))
    body = room(t, n) + phone_rig(t, scr, 540, 850, 0, tip, press=1 - ramp(t, on, .15), night=n, cat=cat(800, 1650, .95, t, rub=.0, look=(-.3, -.8)))
    clock_y = 850 - SH_ / 2 + 290
    s = 1.15 + .75 * push + .12 * hit
    dx, dy = shake(t, W(11) + .05, 9)
    return view(body, t, 540 + dx, 870 + (clock_y - 870) * push + dy, s, 0)


def frame_s04(t):
    a, b = T0("s04"), T1("s04")
    n = night_at(t)
    dr = lib.back_out(ramp(t, W(13) + .02, .28), 1.6) if t > W(13) else 0.0
    press_t = W(14) + .02
    pr = bump(t, press_t, .05, .15)
    op_ = ease_io(ramp(t, press_t + .1, b - press_t - .1))
    scr = lock(t, notif=(dr, pr, op_))
    ty_ = 850 - SH_ / 2 + 580
    if t < press_t - .3:
        tip = (390, 840)
    else:
        v = ease_io(ramp(t, press_t - .3, .3))
        tip = (390 - 160 * v, 840 - 250 * v)
    body = room(t, n) + phone_rig(t, scr, 540, 850, 0, tip, press=pr, night=n, cat=cat(800, 1650, .95, t, rub=0, look=(-.3, -.8)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(13) + .2, 7)
    s = 1.42 - .12 * u + .05 * bump(t, W(13) + .2)
    return view(body, t, 540 + dx, 720 + (ty_ - 720) * .3 * u + dy, s, .6 * u)


def ratchet_times():
    return [W(15), W(16) + .05, W(17), W(18) + .02, W(19) + .05, W(19) + .3]


def frame_s05(t):
    a, b = T0("s05"), T1("s05")
    n = night_at(t)
    ch = ratchet_times()
    scr = video_stack(t, ch)
    last = max([c for c in ch if t >= c], default=a)
    u = clamp((t - last) / .2)
    tip = (330 - 20 * u, 720 - 300 * ease_io(u)) if u < 1 else (310, 420 + 300 * ease_io(clamp((t - last - .2) / .25)))
    body = room(t, n) + phone_rig(t, scr, 540, 850, 0, tip, night=n, glow=1.0, cat=cat(800, 1650, .95, t, rub=0, look=(-.2, -.9), blink=.3 * n))
    s = 1.18 + .1 * ease_io(ramp(t, a, b - a)) + sum(.035 * bump(t, c) for c in ch)
    return view(body, t, 540, 860, s, 0)


def look_up_scene(t, up, n):
    """up 0 — смотрит в телефон, 1 — поднял голову к окну: комната уходит вниз медленнее рук (параллакс)."""
    fg = phone_rig(t, video(5, t), 540, 850 + 1500 * up, 0, (300, 600), night=n, glow=1.0, cat=cat(800, 1650, .95, t, rub=0, look=(-.2, -.9)))
    return f'<g transform="translate(0 {460 * up:.1f})">{room(t, n)}</g>' + fg


def frame_s06(t):
    a, b = T0("s06"), T1("s06")
    n = night_at(t)
    up = ease_io(ramp(t, W(20), WE(21) - W(20) + .1))
    up = up + .04 * math.sin(math.pi * clamp((t - WE(21) - .1) / .5)) if t > WE(21) + .1 else up
    s = 1.12 - .06 * up + .04 * ease_io(ramp(t, WE(21), b - WE(21)))
    return view(look_up_scene(t, up, n), t, 540, 900 - 30 * up, s, 0)


def frame_s07(t):
    a, b = T0("s07"), T1("s07")
    n = night_at(t)
    down = 1 - ease_out(ramp(t, a, .3))
    o = []
    floor = mixc("#b98a5a", "#3a2c38", n)
    o.append(f'<rect x="-900" y="-1700" width="2900" height="4600" fill="{floor}"/>')
    for j in range(-6, 14):
        o.append(line([(-600, j * 150 + 40), (1700, j * 150 + 20)], 3, mixc("#8a6440", "#251c26", n), seed=1100 + j, op=.7))
    # колени по бокам, кот между ними, рука с телефоном сверху
    for j, x in enumerate((-60, 1140)):
        o.append(shape(ellipse_pts(x, 900, 300, 1100, 24), mixc(LEGS, "#1c2238", .7 * n), "", w=5, seed=1120 + j))
    sigh = bump(t, W(26) + .05, .1, .4)
    o.append(cat(540, 1560, 1.55, t, rub=0, age=1.0, look=(0, -.85), blink=.35 + .5 * sigh, tilt=-4 - 4 * sigh))
    o.append(f'<g transform="translate(250 220) rotate(28)">{phone_rig_small(t)}</g>')
    gg = lib.rad_grad([(0, "#9fd0ff", .3), (1, "#9fd0ff", 0)], 250, 220, 900)
    o.append(f'<rect x="-900" y="-1700" width="2900" height="4600" fill="#0a0818" opacity="{.35 * n:.3f}"/>')
    o.append(f'<circle cx="250" cy="220" r="900" fill="url(#{gg})"/>')
    hx, hy = CT.head_world(540, 1560, 1.55, {})
    if t > W(26):     # блик на очках на «темно»
        g = bump(t, W(26) + .05, .08, .3)
        o.append(f'<path d="M{hx - 70} {hy - 40} l12 -30 l12 30 l30 12 l-30 12 l-12 30 l-12 -30 l-30 -12Z" fill="#ffffff" opacity="{g:.3f}" '
                 f'transform="translate({-6} {-8})"/>')
    s = 1.0 + .12 * ease_io(ramp(t, a + .2, b - a)) + .05 * sigh
    dx, dy = shake(t, W(26) + .05, 8)
    return view("".join(o), t, 540 + dx, hy + 160 - 900 * down + dy, s, 0)


def phone_rig_small(t):
    """Опущенный телефон в руке (кадр у ног): видна рамка, экран светит."""
    o = [shape(ellipse_pts(0, 300, 150, 120, 20), SKIN, blob(ellipse_pts(20, 330, 110, 80, 14), SKIN_SH, .6), w=4, seed=1130)]
    o.append(shape(lib.rrect(-170, -330, 170, 330, 44), "#24262e", "", w=4, seed=1131))
    c = lib.clip_rect(-152, -312, 304, 624, 32)
    o.append(f'<g clip-path="url(#{c})"><g transform="translate(-152 -312) scale({304 / SW:.4f})">{video(6, t)}</g></g>')
    o.append(fingertip(-160, 120, -1, 1.2, seed=1140))
    o.append(fingertip(-160, 200, -1, 1.2, seed=1143))
    o.append(thumb((150, 330), (120, 160), 0, seed=1146))
    return "".join(o)


def frame_s08(t):
    a, b = T0("s08"), T1("s08")
    n = night_at(t)
    tt = t - a
    scr = feed(2000 + scroll_pos(tt, v0=600, amp=360), t)
    body = room(t, n) + phone_rig(t, scr, 540, 850, .6 * math.sin(t * 1.7), thumb_tip(tt), night=n, glow=1.0,
                                  cat=cat(800, 1650, .95, t, rub=0, age=1.0, look=(-.2, -.9), blink=.45))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(35) + .05, 6)
    return view(body, t, 540 + dx, 870 + dy, 1.16 + .1 * u, -.8 * u)


def frame_s09(t):
    a, b = T0("s09"), T1("s09")
    n = night_at(t)
    pt = W(36) + .15
    pos = (SHARE_J * (CARD + GAP)) + 60 - 300           # карточка с самолётиком — посередине экрана
    pos = pos + 160 * (1 - ease_out(ramp(t, a, .45), 3))
    pr = bump(t, pt, .05, .12)
    pp = ramp(t, pt + .06, .3)
    scr = feed(pos, t, share=(pr, pp))
    py_ = 60 + SHARE_J * (CARD + GAP) - pos + 356        # самолётик на экране
    px_ = 168.0
    if t < pt - .28:
        tip = (330, 760)
    elif t < pt + .25:
        v = ease_io(ramp(t, pt - .28, .28))
        tip = (330 + (px_ + 14 - 330) * v, 760 + (py_ + 40 - 760) * v)
    else:
        v = ease_io(ramp(t, pt + .25, .3))
        tip = (px_ + 14 + 150 * v, py_ + 40 + 300 * v)
    fly = ""
    if t > pt + .08:      # самолётик улетает вверх-вправо со следом
        u = ease_io(ramp(t, pt + .08, .6))
        fx, fy = px_ + 360 * u, py_ - 420 * u - 120 * math.sin(math.pi * u)
        trail = " ".join(f"{px_ + 360 * q:.1f},{py_ - 420 * q - 120 * math.sin(math.pi * q):.1f}" for q in [u * k / 8 for k in range(9)])
        fly = (f'<polyline points="{trail}" fill="none" stroke="#2f8cff" stroke-width="5" stroke-dasharray="12 12" opacity="{.8 * (1 - u * .5):.2f}"/>'
               + plane(fx, fy, 1.6, "#2f8cff", "#ffffff", 4.6, rot=-20 + 30 * u))
    scr = scr + fly
    body = room(t, n) + phone_rig(t, scr, 540, 850, 0, tip, press=pr, night=n, glow=1.0, cat=cat(800, 1650, .95, t, rub=0, age=1.0, look=(-.2, -.9), blink=.4))
    wx = 540 - SW / 2 + px_
    wy = 850 - SH_ / 2 + py_
    u = ease_io(ramp(t, a, pt - a))
    back = ease_io(ramp(t, pt + .2, b - pt - .2))
    k = u * (1 - .5 * back)
    s = 1.12 + .8 * k + .06 * bump(t, pt)
    return view(body, t, 540 + (wx - 540) * k, 870 + (wy - 870) * k, s, 0)


def frame_s10(t):
    a, b = T0("s10"), T1("s10")
    tt = t - END                         # петля: лента, палец и кот в той же фазе, что на кадре 0
    sway = 4 * math.sin(tt * 3.1)
    scr = feed(scroll_pos(tt), tt)
    body = room(t, 0) + phone_rig(t, scr, 540 + sway, 850 + 3 * math.sin(tt * 2.3), .8 * math.sin(tt * 1.7), thumb_tip(tt),
                                  cat=cat(800, 1650, .95, tt, rub=1.0))
    cx, cy, s = HOOK_VIEW
    out = ease_io(ramp(t, b - .7, .7))               # к концу — к виду кадра 0 (влёт начинается издалека)
    s = s * (1.06 - .06 * ease_io(ramp(t, a, .5))) * (1 - .26 * out)
    return view(body, t, cx, cy + 40 * out, s, -3.0 * out)


FRAMES = {k[6:]: v for k, v in dict(globals()).items() if k.startswith("frame_s")}


def frame(sid, t):
    lib.DEFS.clear()
    return FRAMES[sid](t)
