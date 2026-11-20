"""Рилс 96 «"Просто соберись" не работает», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу); числа в коде — длительности движений.
Сквозной образ: облачко-мотивация с молнией. Пока его ждут — оно пустое и серое (табличка над Димой, как встречающий на
вокзале); после маленького действия оно оживает, бежит вприпрыжку за Димой и садится ему на плечо.
NOCAM=1 — без влёта, тряски и заголовка (замер движения рисунка); MASK=1 — только рисунок хука белым на чёрном."""
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
MASK = bool(os.environ.get("MASK"))


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


def title(t):
    if NOCAM or MASK:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, text=SH["title"]["text"], t_in=SH["title"]["t_in"], t_out=SH["title"]["t_out"], hits=hits)


BG = "#efe2c8"


def view(body, cx, cy, s, rot=0.0, over="", bg=BG):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


# ═════════════════════════ комната ═════════════════════════
FL = 1300.0
WALL, WALL_SH, FLOOR_C = "#efe2c8", "#e3d2b2", "#cdb48c"


def room(t, x0=-1400.0, x1=2600.0, dusk=0.0, masked=False, wall=None):
    if masked:
        return ""
    wc = lib.mix(wall or WALL, "#c9b6a8", dusk)
    o = [rect(x0, -1400, x1, FL, wc)]
    for i in range(int(x0 // 120), int(x1 // 120) + 1):
        xa = i * 120
        o.append(rect(xa, -1400, xa + 46, FL, lib.mix(WALL_SH, "#b9a698", dusk), .55))
    o.append(rect(x0, FL - 46, x1, FL, "#d8c3a0"))
    o.append(line([(x0, FL - 46), (x1, FL - 46)], 3, seed=7))
    o.append(rect(x0, FL, x1, FL + 1400, lib.mix(FLOOR_C, "#8c7a66", dusk)))
    o.append(line([(x0, FL), (x1, FL)], 5, seed=11))
    for i in range(int(x0 // 300), int(x1 // 300) + 1):
        xa = i * 300
        o.append(line([(xa, FL + 20), (xa + (xa - 540) * .9, FL + 900)], 2.4, "#b0966c", seed=20 + i % 9, op=.8))
    return "".join(o)


def chair(x, y, k=1.0):
    o = [shape(lib.rrect(-100, -16, 110, 10, 6), "#a8774a", "", w=4, seed=1011)]
    o.append(shape([(-100, -16, 1), (-80, -16, 1), (-70, -330, 1), (-92, -330, 1)], "#a8774a", "", w=4, seed=1012))
    for s in (-1, 1):
        o.append(shape([(s * 80 - 9, 8, 1), (s * 80 + 9, 8, 1), (s * 86 + 9, 240, 1), (s * 86 - 9, 240, 1)], "#8a6038", "", w=3.4, seed=1013 + s))
    return tf("".join(o), x, y, k)


# ═════════════════════════ облачко-мотивация ═════════════════════════
def bolt_icon(k=1.0, col="#FFD23F", sh="#F2B21B"):
    pts = [(14, -78), (-38, 6), (-4, 6), (-20, 78), (40, -14), (6, -14), (24, -78)]
    inn = blob([(14, -78), (-38, 6), (-4, 6), (-12, 30)], sh, .7)
    return f'<g transform="scale({k:.3f})">{shape(pts, col, inn, w=4.2, seed=9601)}</g>'


def mot(x, y, k=1.0, lit=0.0, t=0.0, face=0.0, legs=0.0, run=0.0, squash=0.0, rot=0.0, seed=0, sad=0.0):
    """Облачко-мотивация: (x, y) — центр облака. lit 0 — серое, молния — пустой контур; 1 — белое, молния золотая, свечение.
    face 0…1 — глазки и улыбка (живое), legs — ножки-палочки, run — фаза бега (ножки по очереди), squash — сжатие при прыжке."""
    o = []
    if lit > .02:
        o.append(PR.glow(0, 0, 260, .55 * lit, "#ffe58a"))
    col = lib.mix("#c3c6cf", "#ffffff", lit)
    if legs > .01:
        for j, s in enumerate((-1, 1)):
            ph = math.sin(2 * math.pi * run + j * math.pi)
            fx, fy = s * 46 + 26 * ph * legs, 118 + 10 * max(0.0, -ph)
            o.append(line([(s * 40, 70), (fx, fy * legs + 70 * (1 - legs))], 7, INK, taper=0, wmin=1, seed=9610 + j))
            o.append(blob(ellipse_pts(fx + 8, fy * legs + 70 * (1 - legs) + 2, 20 * legs, 9 * legs, 10), INK))
    inner = ""
    if lit < .98:
        bo = bolt_icon(.95, lib.mix("#d6d8de", "#FFD23F", lit), lib.mix("#c3c6cf", "#F2B21B", lit))
        inner = f'<g transform="translate(0 {-95:.1f})" opacity="{.75 + .25 * lit:.3f}">{bo}</g>' if lit < .5 else ""
    cl = PR.cloud(0, 95, 300, 190, 1 + .12 * squash, 1 - .18 * squash, seed=seed, col=col, inner=inner)
    o.append(cl)
    if lit >= .5:
        o.append(f'<g transform="translate(0 {-5 + 8 * squash:.1f})">{bolt_icon(.95 * (1 + .1 * math.sin(t * 9) * lit))}</g>')
        if lit > .5:
            o.append(PR.sparkles(0, -10, 1.6, (lit - .5) * 2, t, seed=seed + 3, n=4, r=170))
    if face > .01:
        ex = 62
        for s in (-1, 1):
            o.append(blob(ellipse_pts(s * ex + (0 if s < 0 else 0), 30, 9, 12 * face, 10), INK))
        if sad < .5:
            o.append(line([(-26, 58), (0, 70 * face + 58 * (1 - face)), (26, 58)], 5, INK, taper=.2, wmin=.6, seed=9620))
        else:
            o.append(line([(-22, 68), (0, 58), (22, 68)], 5, INK, taper=.2, wmin=.6, seed=9621))
    return tf("".join(o), x, y, k, rot)


def sign_stick(hx, hy, top, k=1.0, lit=0.0, t=0.0, rot=0.0, seed=0, face=0.0, sad=0.0):
    """Табличка-облачко на палке: рука в (hx, hy), облачко на высоте top."""
    rr = math.radians(rot)
    tx, ty = hx + math.sin(rr) * (hy - top), top + (1 - math.cos(rr)) * (hy - top)
    o = line([(hx, hy + 30 * k), (tx, ty + 100 * k)], 11 * k, "#9a6a3c", taper=0, wmin=1, seed=9630)
    return o + mot(tx, ty, k, lit, t, rot=rot, seed=seed, face=face, sad=sad)


def hanging_sign(x, y, k, t, swing=0.0, lit=0.0, seed=0):
    """Табличка-облачко висит на двух нитках с потолка; swing — угол раскачки в градусах."""
    top = y - 900
    piv = f'rotate({swing:.2f} {x:.1f} {top:.1f})'
    st = line([(x - 90 * k, top), (x - 90 * k, y - 60 * k)], 3, "#7a6a58", taper=0, wmin=1, seed=9640) + \
        line([(x + 90 * k, top), (x + 90 * k, y - 60 * k)], 3, "#7a6a58", taper=0, wmin=1, seed=9641)
    return f'<g transform="{piv}">{st}{mot(x, y, k, lit, t, seed=seed)}</g>'


# ═════════════════════════ Дима ═════════════════════════
def dima_sit(x, hip, k, expr, t, pose="sit_desk", lean=0.0, head_add=0.0, flip=False, **kw):
    feet = people.sit_kw(x, hip, k)["feet"]
    return people.dima82(x, hip, k, expr, pose, t=t, feet=feet, lean_add=lean, head_add=head_add, flip=flip, **kw)


def slap_u(t, slaps):
    """0 — руки отведены, 1 — ладони на щеках: быстрый удар (0.07 с) и отскок (0.2 с)."""
    p = 0.0
    for s in slaps:
        u = t - s
        if -0.07 < u <= 0:
            p = max(p, 1 + u / .07)
        elif 0 < u < .22:
            p = max(p, 1 - u / .22)
    return ease_io(p)


def dima_slap(x, hip, k, t, slaps, expr="strain", lean=0.0, sit=True):
    """Дима хлопает себя по щекам обеими ладонями (двухпроходно: голова → цели рук); голова дёргается на хлопке."""
    p = slap_u(t, slaps)
    jolt = 0.0
    for s in slaps:
        jolt += bump(t, s, .03, .12) * (1 if int(round(s * 10)) % 2 else -1)
    feet = people.sit_kw(x, hip, k)["feet"] if sit else "stand"
    probe = people.dima82(x, hip, k, expr, "d82_rest", t=t, feet=feet, lean_add=lean, head_add=.06 * jolt)
    hx, hy = probe["head"]
    mx, my = probe["mouth"]
    near = (hx - 70 * k + (1 - p) * -130 * k, my + 40 * k + (1 - p) * 120 * k)
    far = (mx + 46 * k + (1 - p) * 140 * k, my - 14 * k + (1 - p) * 80 * k)
    arms = {"n": ("ik", near, 1), "f": ("ik", far, -1)}
    hands = {"n": {"dir": (.25, -1), "curl": (.05, .05, .08, .1), "spread": .25, "thumb": .15},
             "f": {"dir": (-.2, -1), "curl": (.05, .05, .08, .1), "spread": .25, "thumb": .15}}
    f = people.dima82(x, hip, k, expr, "d82_rest", t=t, feet=feet, lean_add=lean, head_add=.06 * jolt, arms=arms, hands=hands)
    f["slap"] = p
    return f


def steam(hx, hy, k, t, u, seed=0):
    """Пар из ушей: белые клубы вылетают в обе стороны и тают (злость)."""
    if u <= .01:
        return ""
    o = []
    for s, ex in ((-1, -80), (1, 70)):
        for j in range(3):
            ph = ((t * 2.4 + j / 3 + (seed + (s > 0)) * .17) % 1.0)
            px = hx + ex * k + s * (40 + 160 * ph) * k
            py = hy - 10 * k - 120 * ph * k + 14 * math.sin(t * 9 + j)
            r = (26 + 46 * ph) * k * u
            o.append(shape(ellipse_pts(px, py, r, r * .8, 12), "#ffffff", "", w=3.2, seed=9650 + j + 3 * (s > 0)))
    return f'<g opacity="{.95 * u:.3f}">{"".join(o)}</g>'


def flush(hx, hy, k, u):
    if u <= .01:
        return ""
    return (f'<ellipse cx="{hx + 6 * k:.1f}" cy="{hy + 8 * k:.1f}" rx="{88 * k:.1f}" ry="{96 * k:.1f}" fill="#ff3b2f" '
            f'opacity="{.38 * u:.3f}" style="mix-blend-mode:multiply"/>')


def spin_clock(x, y, r, t, speed=3.0, seed=0, calm=0.0):
    """Часы: speed — оборотов минутной стрелки в секунду (бешено), calm 1 — идут спокойно."""
    sp = speed * (1 - calm) + .02 * calm
    return PR.clock(x, y, r, angle_h=t * sp * 30 + 40, angle_m=t * sp * 360 + 200, seed=seed)


# ═════════════════════════ хук s01–s03 ═════════════════════════
HIT01 = stress(1, .55)                       # «говоРЯТ»: хлопок по щекам
SLAPS = [-.12, .22, HIT01, .93, stress(2, .4), stress(3, .3), stress(3, .75), stress(5, .3)]
DX, DHIP, DK = 360.0, FL - 290, .5            # Дима за столом
DESK = (650.0, FL - 300)
LAP = (680.0, FL - 330)
SIGN = (470.0, 520.0)
CLOCK = (735.0, 470.0)


def desk_world(t, masked=False, sign_lit=0.0, swing=None, slaps=SLAPS, expr="strain", screen="dark", lines=0.0, clock_calm=0.0,
               jab=None, typing=False, mot_on=None):
    o = [room(t, masked=masked)]
    o.append(spin_clock(*CLOCK, 78, t, 3.2, calm=clock_calm))
    if clock_calm < .5:
        o.append(PR.speed_arcs(CLOCK[0] + 110, CLOCK[1], .9, 1.0, t, seed=2, n=3, ang=0))
    sw = swing if swing is not None else 7 * math.sin(t * 7.5) + 5 * bump(t, HIT01, .05, .3)
    if mot_on is None:
        o.append(hanging_sign(SIGN[0], SIGN[1], .78, t, sw, sign_lit, seed=1))
    o.append(chair(DX - 40, FL - 240, 1.0))
    o.append(PR.desk(DESK[0], DESK[1], w=520, depth=100, leg_h=260, seed=7))
    if typing:
        f = dima_sit(DX, DHIP, DK, "type73", t, pose="sit_desk", lean=.12 + .03 * math.sin(t * 9))
    elif jab is not None:
        f = dima_sit(DX, DHIP, DK, "squint82", t, pose=("sit_desk", "d82_press"), u=jab, lean=.15)
    else:
        f = dima_slap(DX, DHIP, DK, t, slaps, expr=expr, lean=.05)
    o.append(f["svg"])
    o.append(PR.laptop(LAP[0], LAP[1], .5, open_=1.0, screen=screen, lines=lines, t=t))
    if not typing and jab is None:
        hx, hy = f["head"]
        o.append(people.strain_marks((hx, hy), DK, t, .9))
        p = f["slap"]
        if p > .85:
            for s, ex in ((-1, -70), (1, 60)):
                o.append(PR.sparkles(hx + ex, hy + 30, .8, 1.0, t, seed=5 + (s > 0), n=3, r=60))
    if mot_on is not None:
        o.append(mot_on)
    return "".join(o), f


def hook_cam_scene(t):
    """Камера сцены (часть рисунка): плывёт от часов к Диме и вниз, чуть приближаясь."""
    u = ease_io(clamp((t + .2) / 1.5))
    return 640 - 110 * u, 740 + 30 * u + 10 * math.sin(t * 6), 1.6 + .12 * u


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
            blur += (f'<use href="#hk96" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk96">{body}</g></g>{blur}'


MASK_F = '<filter id="mk96"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 9 0"/></filter>'


def frame_s01(t):
    cx, cy, s = hook_cam_scene(t)
    if MASK:
        lib.DEFS.append(MASK_F)
        body, _ = desk_world(t, masked=True)
        return lib.svg(f'<rect width="1080" height="1920" fill="#000"/><g transform="{lib.cam(cx, cy, s, 0)}"><g filter="url(#mk96)">{body}</g></g>')
    body, _ = desk_world(t)
    dx, dy = shake(t, HIT01, 14)
    v = f'<g transform="{lib.cam(cx + dx, cy + dy, s, 0)}">{body}</g>'
    if NOCAM:
        return lib.svg(f'<rect width="1080" height="1920" fill="{BG}"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT01) + title(t))


def frame_s02(t):
    """«Просто соберись»: крупно лицо и ладони, часы крутятся за плечом, табличка качается."""
    a, b = T0("s02"), T1("s02")
    u = ease_io(ramp(t, a, b - a))
    body, f = desk_world(t)
    hx, hy = f["head"]
    hit = stress(3, .3)
    dx, dy = shake(t, hit, 10)
    z = 2.55 + .2 * u + .12 * bump(t, hit, .04, .25)
    return view(body, hx + 40 + dx, hy - 30 + dy, z, -2 + 3 * u, over=title(t))


def frame_s03(t):
    """«и сделай. Вот»: Дима тычет пальцем в клавиатуру — экран пустой; табличка над ним серая, молния мигает и гаснет."""
    a, b = T0("s03"), T1("s03")
    jab = max(bump(t, q, .06, .14) for q in (stress(5, .1), stress(5, .6), W(6), stress(7, .3)))
    flick = 1.0 if any(abs(t - (W(6) + d)) < .04 for d in (0, .12)) else 0.0
    body, f = desk_world(t, jab=jab, sign_lit=.45 * flick)
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(6), 7)
    return view(body, 520 + dx, 860 + dy - 30 * u, 1.55 + .12 * u, 1.5 - 2.5 * u, over=title(t))


def frame(sid, t):
    if sid != "s06":
        lib.DEFS.clear()
    return globals()["frame_" + sid](t)
