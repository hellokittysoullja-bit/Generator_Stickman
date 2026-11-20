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


# ═════════════════════════ s04–s05, s07: ждёт у двери, как на вокзале ═════════════════════════
DOOR_X = 860.0
BENCH_X = 380.0


def dima_bench(t, expr, lift=1.0, rot=0.0, lit=0.0, lean=0.0, sag=0.0, sign=True, face=0.0, sad=0.0):
    """Дима сидит на скамейке и держит над головой табличку-облачко на палке (встречающий на вокзале)."""
    sx, sy = PR.bench_seat(BENCH_X, FL, 1.0)
    hip = sy - 12
    feet = people.sit_kw(BENCH_X - 20, hip, .5)["feet"]
    hand = (BENCH_X + 70 - 40 * sag, hip - 330 * lift + 90 * sag)
    arms = {"n": ("ik", hand, -1)} if sign else None
    hands = {"n": {"dir": (.1, -1), "curl": (.8, .85, .85, .85), "thumb": .6}} if sign else None
    f = people.dima82(BENCH_X - 20, hip, .5, expr, "d82_rest", t=t, feet=feet, lean_add=lean + .1 * sag, head_add=.12 * sag,
                      arms=arms, hands=hands)
    o = [PR.bench(BENCH_X, FL, 1.0), f["svg"]]
    if sign:
        o.append(sign_stick(hand[0], hand[1], hand[1] - 330, .72, lit, t, rot=rot, seed=2, face=face, sad=sad))
        o.append(people.hand_svg("dima", (hand[0] - 2, hand[1] + 6), (.1, -1), .5, curl=(.8, .85, .85, .85), thumb=.6, seed=771))
    return "".join(o), f


def station_world(t, web=0.0, spin=3.0):
    o = [room(t, x0=-800, x1=2000)]
    o.append(PR.door(DOOR_X, FL, .92, 0.0, seed=1))
    o.append(spin_clock(DOOR_X, 300, 82, t, spin, seed=3))
    o.append(PR.speed_arcs(DOOR_X + 115, 300, .8, 1.0, t, seed=4, n=3, ang=0))
    if web > .01:
        o.append(PR.cobweb(DOOR_X - 236 * .92 + 4, FL - 960 * .92 + 4, 1.4 * web, t=t, ang=0, span=90, L=170, seed=1))
        o.append(PR.cobweb(BENCH_X - 236, FL - 330, 1.0 * web, t=t, ang=-90, span=90, L=150, seed=2))
    return "".join(o)


def frame_s04(t):
    """«правда. Ты ждёшь мотивацию, чтобы начать»: Дима на скамейке у закрытой двери держит над головой табличку-облачко,
    как встречающий на вокзале; часы над дверью несутся, паутина растёт; на «мотивацию» табличка подпрыгивает (с надеждой)."""
    a, b = T0("s04"), T1("s04")
    web = ease_io(ramp(t, W(11), b - W(11)))
    hope = bump(t, W(10), .08, .35)
    o = [station_world(t, web)]
    g, f = dima_bench(t, "hope" if t < W(11) else "look82", lift=1 + .15 * hope + .04 * math.sin(t * 5), rot=4 * math.sin(t * 4))
    o.append(g)
    o.append(PR.cobweb(f["head"][0] - 10, f["head"][1] - 70, .55 * web, t=t, ang=200, span=80, L=140, seed=3))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(10), 7)
    return view("".join(o), 600 - 40 * u + dx, 860 + dy, 1.12 + .14 * u, -1.5 + 2.5 * u)


def frame_s05(t):
    """«она всё не приходит, и ты злишься на себя»: дверь стоит закрытой, Дима хмурится, на «злишься» краснеет, из ушей пар,
    он трясёт табличку."""
    a, b = T0("s05"), T1("s05")
    mad = ease_out(ramp(t, W(20) - .05, .3))
    o = [station_world(t, 1.0, spin=3.0)]
    shake_r = (14 * math.sin(t * 26)) * mad
    g, f = dima_bench(t, "frowny" if t < W(20) else "shout78", lift=1.0 + .05 * math.sin(t * 20) * mad, rot=shake_r, lean=.05 * mad)
    o.append(g)
    hx, hy = f["head"]
    o.append(PR.cobweb(hx - 10, hy - 70, .55, t=t, ang=200, span=80, L=140, seed=3, tremble=mad, torn=.6 * mad))
    o.append(flush(hx, hy, .5, mad))
    o.append(steam(hx, hy, .5, t, mad))
    door_look = ease_io(ramp(t, a, W(17) - a))
    u = ease_io(ramp(t, a, b - a))
    cx = 700 - 260 * door_look
    dx, dy = shake(t, W(20), 11)
    s = 1.35 + .35 * door_look + .12 * u + .1 * bump(t, W(20), .05, .3)
    return view("".join(o), cx + dx, 820 - 40 * door_look + dy, s, 1 - 2 * u)


def frame_s06(t):
    import story_cta_tg as tg
    press = W(26) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=os.path.join(STORY, "common"))


def frame_s07(t):
    """«ждать мотивацию»: Дима оплыл на скамейке, весь в паутине, табличка повисла, часы всё несутся."""
    a, b = T0("s07"), T1("s07")
    sag = ease_io(ramp(t, a, .6))
    o = [station_world(t, 1.0)]
    g, f = dima_bench(t, "glum", lift=.85, rot=-18 * sag + 2 * math.sin(t * 3), sag=sag)
    o.append(g)
    hx, hy = f["head"]
    o.append(PR.cobweb(hx - 20, hy - 60, .75, t=t, ang=190, span=100, L=150, seed=3))
    o.append(PR.cobweb(hx + 60, hy + 160, .6, t=t, ang=-30, span=90, L=130, seed=5))
    o.append(PR.spider(hx + 40, hy - 150 + 60 * ease_io(ramp(t, a + .2, .7)), .5, t=t) if hasattr(PR, "spider") else "")
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(31), 6)
    return view("".join(o), hx + 60 + dx, hy + 60 + dy, 1.9 + .2 * u, 0)


# ═════════════════════════ s08–s09: схема «действие → мотивация» ═════════════════════════
def sole(k=1.0, col="#6a5848"):
    o = blob(ellipse_pts(0, -34, 34, 50, 18), col) + blob(ellipse_pts(4, 52, 26, 30, 16), col)
    for j, (dx, dy, r) in enumerate(((-26, -98, 11), (-6, -108, 10), (14, -104, 9), (30, -92, 8))):
        o += blob(ellipse_pts(dx, dy, r, r, 10), col)
    return f'<g transform="scale({k:.3f}) rotate(14)">{o}</g>'


def badge(x, y, k, kind, lit=0.0, t=0.0, seed=0):
    o = []
    if lit > .01:
        o.append(PR.glow(0, 0, 260, .7 * lit, "#ffe58a"))
    o.append(shape(ellipse_pts(0, 0, 170, 170, 30), lib.mix("#fffaf0", "#fff3c4", lit), "", w=6, seed=9700 + seed))
    if kind == "bolt":
        o.append(bolt_icon(1.35 * (1 + .06 * math.sin(t * 8) * lit), lib.mix("#cfd2d8", "#FFD23F", max(lit, .0) if lit > 0 else 1.0)))
    else:
        o.append(sole(1.05))
    if lit > .3:
        o.append(PR.sparkles(0, 0, 2.0, lit, t, seed=seed + 7, n=5, r=210))
    return tf("".join(o), x, y, k)


def big_arrow(x0, x1, y, u=1.0, pulse=0.0):
    if u <= .01:
        return ""
    xe = x0 + (x1 - x0) * u
    s = 1 + .15 * pulse
    h = 46 * s
    d = 1 if x1 >= x0 else -1
    body = [(x0, y - h / 2, 1), (xe - d * 70, y - h / 2, 1), (xe - d * 70, y - h * 1.4, 1), (xe, y, 1), (xe - d * 70, y + h * 1.4, 1),
            (xe - d * 70, y + h / 2, 1), (x0, y + h / 2, 1)]
    return shape(body, "#e2574c", "", w=5, seed=9710)


def scheme_bg():
    return rect(-2000, -2000, 3000, 4000, "#f6efdf") + "".join(
        line([(-600, 200 + 90 * j), (1700, 200 + 90 * j)], 2, "#e3d6bb", taper=0, wmin=1, seed=9720 + j) for j in range(20))


def frame_s08(t):
    """«Правда в том, что мотивация»: как думают все — сначала молния (мотивация), большая стрелка, потом шаг (дело)."""
    a, b = T0("s08"), T1("s08")
    o = [scheme_bg()]
    p1 = pop(t, a + .05, .3)
    p2 = pop(t, W(37) + .2, .3)
    arr = ease_out(ramp(t, W(36), .5))
    o.append(big_arrow(410, 690, 900, arr))
    o.append(badge(250, 900, .85 * p1, "bolt", 0.0, t, seed=1))
    o.append(badge(850, 900, .85 * p2, "step", 0.0, t, seed=2))
    o.append(PR.question_mark(540, 640, 1.3, ease_out(ramp(t, W(38) - .1, .35)) if t > W(38) - .1 else 0.0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(37), 7)
    return view("".join(o), 540 + dx, 860 + dy, 1.05 + .1 * u, 0)


def frame_s09(t):
    """«приходит не до дела, а после»: кружки меняются местами (молния дугой над, шаг под), стрелка теперь от шага к молнии;
    на «после» молния загорается и искрит."""
    a, b = T0("s09"), T1("s09")
    o = [scheme_bg()]
    sw = ease_io(ramp(t, W(39), WE(41) - W(39)))
    lit = ease_out(ramp(t, W(43), .3))
    bx = 250 + 600 * sw
    by = 900 - 330 * math.sin(math.pi * sw)
    sx = 850 - 600 * sw
    sy = 900 + 330 * math.sin(math.pi * sw)
    cross = bump(t, W(39), .1, .5)
    if sw < .05:
        o.append(big_arrow(410, 690, 900, 1.0))
        o.append(line([(470, 830), (630, 970)], 14, "#2b2b30", taper=.1, wmin=.6, seed=9730) if cross > .05 else "")
    if sw > .95:
        o.append(big_arrow(410, 690, 900, ease_out(ramp(t, WE(41), .3)), pulse=bump(t, W(43), .06, .3)))
    o.append(badge(sx, sy, .85, "step", 0.0, t, seed=2))
    o.append(badge(bx, by, .85 * (1 + .12 * bump(t, W(43), .05, .3)), "bolt", lit, t, seed=1))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(43), 9)
    return view("".join(o), 540 + dx, 880 + dy, 1.12 + .08 * u, 0)


# ═════════════════════════ s10: главный вопрос ═════════════════════════
def cat(x, y, k, t, st=None):
    st = dict(dict(look=(-.6, -.3), tail=8 * math.sin(t * 1.7), flame_e=1.0), **(st or {}))
    return CT.draw(x, y, k, st, t)


def stand_hip(k):
    return FL - (people.LEG_LEN - 12) * k - 6


def frame_s10(t):
    """«А главное решение узнаешь к концу ролика»: Дима чешет висок, над ним выскакивает большой знак вопроса; кот на
    столе смотрит на нас и подмигивает на «концу»."""
    a, b = T0("s10"), T1("s10")
    o = [room(t)]
    o.append(chair(DX - 40, FL - 240, 1.0))
    o.append(PR.desk(DESK[0] + 60, DESK[1], w=520, depth=100, leg_h=260, seed=7))
    o.append(PR.laptop(LAP[0] + 60, LAP[1], .5, open_=.15, screen="dark", t=t))
    k = .5
    tap = .5 + .5 * math.sin(t * 14)
    f = people.dima82_temple(300, stand_hip(k), k, tap=tap, t=t, expr="puzzled82", feet="stand")
    o.append(f["svg"])
    hx, hy = f["head"]
    qp = pop(t, W(45), .3)
    o.append(PR.glow(hx + 20, hy - 250, 200, .4 * qp, "#fff1b0"))
    o.append(tf(PR.question_mark(0, 0, 1.0, 1.0, w=13), hx + 20, hy - 250 + 10 * math.sin(t * 4), 1.6 * qp, 8 * math.sin(t * 3)))
    o.append(PR.sparkles(hx + 20, hy - 250, 1.6, bump(t, W(46), .05, .4), t, seed=8, n=5, r=150))
    wink = 1.0 if abs(t - (W(49) + .12)) < .14 else 0.0
    look = ramp(t, W(47), .3)
    o.append(cat(830, DESK[1] - 100, .38, t, dict(look=(-.7 + 1.0 * look, -.3 + .5 * look), smug=.7 * look, blink_R=wink, tilt=-8 * look)))
    u = ease_io(ramp(t, a, b - a))
    zoom = ease_io(ramp(t, W(48), .4))
    cx = 470 + 220 * zoom
    dx, dy = shake(t, W(46), 7)
    return view("".join(o), cx + dx, 800 + dy - 40 * u, 1.25 + .1 * u + .45 * zoom, 0)


# ═════════════════════════ s11–s12: маленький шаг, за ним бежит мотивация ═════════════════════════
def frame_s11(t):
    """«Сначала маленькое действие»: облачко-табличка лежит на полу, Дима делает крошечный шажок — подошва-отпечаток
    вспыхивает; молния лежащего облачка мигнула жёлтым."""
    a, b = T0("s11"), T1("s11")
    k = .5
    st = ramp(t, W(52), WE(52) - W(52) + .1)
    ph = .5 * ease_io(st)
    x = 520 + 70 * ease_io(st)
    o = [room(t)]
    o.append(tf(sole(.55, "#b59a74"), 470, FL + 60, 1.0, -80))
    glow_u = ease_out(ramp(t, W(53), .3))
    if glow_u > 0:
        o.append(PR.glow(615, FL + 70, 160, .8 * glow_u, "#ffe58a"))
        o.append(tf(sole(.55, lib.mix("#b59a74", "#f2b21b", glow_u)), 615, FL + 70, 1.0, -80))
        o.append(PR.sparkles(615, FL + 60, 1.2, bump(t, W(53), .05, .4), t, seed=11, n=4, r=100))
    f = people.dima82_walk(x, stand_hip(k), k, ph, t=t, expr="squint82" if t < W(53) else "sure82", mug=False)
    o.append(f["svg"])
    flick = .6 * bump(t, W(53) + .1, .05, .25)
    o.append(mot(170, FL - 70, .55, flick, t, rot=-12, seed=3))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(53), 7)
    return view("".join(o), 470 + 60 * u + dx, 1080 + dy, 1.35 + .12 * u, 0)


def run_cloud(t, t_on, x_fn, ground, k=.6, lit=1.0, seed=3):
    """Облачко-мотивация бежит вприпрыжку: ножки, прыжки дугами по 0.32 с, сжатие на приземлении."""
    ph = max(0.0, t - t_on) / .32
    hop = abs(math.sin(math.pi * ph))
    land = max(0.0, 1 - (ph % 1.0) / .25) if ph > 0 else 0.0
    y = ground - 120 * k - 170 * k * hop
    return mot(x_fn(t), y, k, lit, t, face=1.0, legs=1.0, run=ph * .5, squash=.6 * land * (1 - hop), rot=6 * math.sin(math.pi * ph), seed=seed)


def frame_s12(t):
    """«потом появляется желание»: Дима идёт вправо, за ним вприпрыжку бежит ожившее облачко с молнией; на «желание»
    молния вспыхивает золотом."""
    a, b = T0("s12"), T1("s12")
    k = .5
    x = 420 + 230 * (t - a)
    o = [room(t, x0=-800, x1=2400)]
    f = people.dima82_walk(x, stand_hip(k), k, (t - a) / .6, t=t, expr="calm82", mug=False)
    lit = .45 + .55 * ease_out(ramp(t, W(56), .3))
    o.append(run_cloud(t, a - .3, lambda tt: x - 330 + 60 * ease_out(ramp(tt, a, b - a)), FL, .55, lit))
    o.append(f["svg"])
    o.append(PR.sparkles(x - 300, FL - 300, 1.6, bump(t, W(56), .05, .45), t, seed=12, n=5, r=160))
    dx, dy = shake(t, W(56), 8)
    return view("".join(o), x - 140 + dx, 1000 + dy, 1.3, 0)


# ═════════════════════════ s13–s14: кабинет психолога ═════════════════════════
OFFICE = "#dfe6d6"


def office_room(t):
    o = [room(t, x0=-800, x1=2200, wall=OFFICE)]
    o.append(shape(lib.rect_pts(560, 360, 900, 760), "#cfe3ef", line([(730, 360), (730, 760)], 6, "#f6f1e6", taper=0, wmin=1, seed=9740), w=4.4,
                   seed=9741))
    return "".join(o)


def clipboard(x, y, k, rot=-8, tick=0.0):
    o = shape(lib.rrect(-80, -110, 80, 110, 8), "#a8794a", "", w=4, seed=9900)
    o += shape(lib.rect_pts(-66, -90, 66, 100), "#fbf8f0", "".join(line([(-50, -50 + 34 * j), (40, -50 + 34 * j)], 3, "#b9b2a4", seed=9901 + j)
                                                                 for j in range(4)), w=3, seed=9905)
    o += shape(lib.rrect(-34, -124, 34, -96, 6), "#9aa0aa", "", w=3, seed=9906)
    if tick > .01:
        o += PR.check_mark(10, 30, .7, tick, col="#2f9a4a")
    return tf(o, x, y, k, rot)


def sofa(x, y, k=1.0):
    o = shape(lib.rrect(-260, -300, 260, -120, 40), "#8aa0c8", "", w=4.4, seed=9750)
    o += shape(lib.rrect(-300, -170, 300, -40, 30), "#9db2d8", "", w=4.4, seed=9751)
    for s in (-1, 1):
        o += shape(lib.rrect(s * 300 - 50, -230, s * 300 + 50, -30, 30), "#7d93bb", "", w=4.4, seed=9752 + s)
        o += line([(s * 240, -30), (s * 250, 0)], 10, INK, taper=0, wmin=1, seed=9754 + s)
    return tf(o, x, y, k)


def frame_s13(t):
    """«Психологи называют это поведенческой активацией»: кабинет, психолог в кресле с планшетом (без букв) ставит галочку,
    клиент на диване понурый, над ним серое облачко с грустной мордочкой."""
    a, b = T0("s13"), T1("s13")
    k = .5
    o = [office_room(t)]
    o.append(chair(760, FL - 240, 1.0))
    tick = ease_out(ramp(t, W(61), .35))
    hip = FL - 290
    clip_at = (760 - 150, hip - 170)
    sci = people.scientist82("a", 760, hip, k, "rest", t=t, expr="talk" if W(58) < t < WE(61) and int(t * 7) % 2 else "focus", feet="sit", flip=True,
                             arms={"n": ("ik", clip_at, 1)}, hands={"n": {"dir": (-.3, -1), "curl": (.8, .8, .8, .8), "thumb": .6}})
    o.append(sci["svg"])
    o.append(clipboard(clip_at[0] - 10, clip_at[1] - 70, .75, 10, tick))
    o.append(sofa(240, FL, .9))
    c = people.subject82(250, FL - 150, k, "rest", t=t, expr="focus", feet="sit")
    o.append(c["svg"])
    hx, hy = c["head"]
    o.append(mot(hx, hy - 230 + 8 * math.sin(t * 2.5), .55, 0.0, t, face=1.0, sad=1.0, seed=4))
    o.append(PR.sparkles(clip_at[0], clip_at[1] - 60, 1.0, bump(t, W(61), .05, .4), t, seed=13, n=4, r=100))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(60), 6)
    return view("".join(o), 500 + dx, 950 + dy - 20 * u, 1.05 + .15 * u, 0, bg=OFFICE)


def frame_s14(t):
    """«с этого начинают даже лечение депрессии»: клиент поднялся и поливает из кружки цветок — цветок выпрямляется,
    серое облачко над ним светлеет и улыбается; психолог кивает."""
    a, b = T0("s14"), T1("s14")
    k = .5
    o = [office_room(t)]
    pour = ramp(t, W(63) - .1, .25)
    perk = ease_io(ramp(t, W(64), 1.0))
    light = ease_io(ramp(t, W(65), WE(67) - W(65)))
    o.append(PR.houseplant(640, FL, 1.1, droop=1 - perk, perk=perk, t=t))
    hip = stand_hip(k)
    hold = (520, hip - 280)
    c = people.subject82(380, hip, k, "rest", t=t, expr="focus", feet="stand",
                         arms={"n": ("ik", hold, -1)}, hands={"n": {"dir": (1, .1), "curl": (.8, .8, .8, .8), "thumb": .6}})
    o.append(c["svg"])
    rot = 70 * pour
    o.append(PR.mug(hold[0] + 30, hold[1] + 30, .9, rot=rot, col="blue", coffee=False))
    if pour > .5:
        o.append(PR.pour_stream(hold[0] + 75, hold[1] + 10, 640, FL - 200, t=t, w=12, col="#7fb8e6", seed=2))
    hx, hy = c["head"]
    o.append(mot(hx, hy - 230 + 8 * math.sin(t * 2.5), .55, light, t, face=1.0, sad=1.0 if light < .5 else 0.0, seed=4))
    o.append(PR.sparkles(640, FL - 400, 1.4, bump(t, W(66), .05, .5), t, seed=14, n=5, r=160))
    nod = .1 * math.sin(t * 9) * bump(t, W(66), .1, .6)
    sci = people.scientist82("a", 900, stand_hip(k), k, "rest", t=t, expr="smile", feet="stand", flip=True, head_add=nod,
                             arms={"n": ("ik", (900 - 120, stand_hip(k) - 230), 1)},
                             hands={"n": {"dir": (-.3, -1), "curl": (.8, .8, .8, .8), "thumb": .6}})
    o.append(sci["svg"])
    o.append(clipboard(900 - 140, stand_hip(k) - 300, .7, 10, 1.0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(67), 7)
    return view("".join(o), 580 + dx, 900 + dy - 30 * u, 1.15 + .15 * u, 0, bg=OFFICE)


# ═════════════════════════ s15–s16: не жди, открой файл ═════════════════════════
def frame_s15(t):
    """«Поэтому не жди настроения»: Дима у стола держит табличку-облачко на палке, на «жди» отшвыривает её — она улетает
    за кадр, кружась, и он открывает ноутбук."""
    a, b = T0("s15"), T1("s15")
    k = .5
    toss = W(70)
    o = [room(t)]
    o.append(chair(DX - 40, FL - 240, 1.0))
    o.append(PR.desk(DESK[0], DESK[1], w=520, depth=100, leg_h=260, seed=7))
    lid = .1 + .9 * ease_io(ramp(t, W(71) + .2, .4))
    if t < toss:
        hand = (DX + 60, DHIP - 330 - 30 * bump(t, W(69), .1, .3))
        f = dima_sit(DX, DHIP, k, "frowny", t, pose="d82_rest", arms={"n": ("ik", hand, -1)},
                     hands={"n": {"dir": (.1, -1), "curl": (.8, .85, .85, .85), "thumb": .6}})
        o.append(f["svg"])
        o.append(sign_stick(hand[0], hand[1], hand[1] - 330, .72, 0.0, t, rot=-6 * ramp(t, W(69), .3), seed=2))
    else:
        u = ramp(t, toss, .55)
        typ = ramp(t, W(71) + .2, .3)
        f = dima_sit(DX, DHIP, k, "sure82" if typ > .5 else "squint82", t, pose=("d82_shrug", "sit_desk"), u=ease_io(clamp(u * 1.6)))
        o.append(f["svg"])
        sx, sy = DX + 60 - 900 * u, DHIP - 500 - 500 * math.sin(math.pi * min(u, .9)) + 300 * u
        o.append(tf(sign_stick(0, 0, -330, .72, 0.0, t, seed=2), sx, sy, 1.0, -540 * u))
        o.append(PR.speed_arcs(sx + 150, sy - 300, 1.2, 1 - u, t, seed=15, n=3, ang=0))
    o.append(PR.laptop(LAP[0], LAP[1], .5, open_=lid, screen="dark", t=t))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, toss, 10)
    return view("".join(o), 520 + dx, 900 + dy, 1.4 + .15 * u, 1 - 2 * u)


def finger(x, y, k=1.0):
    """Палец сверху-справа жмёт клавишу: (x, y) — кончик указательного."""
    return people.hand_svg("dima", (x + 120 * k, y - 170 * k), (-.55, .85), 1.6 * k, curl=(0, .9, .9, .9), spread=.05, thumb=.75, seed=780)


def frame_s16(t):
    """«открой файл, напиши одно слово»: крупно ноутбук; на «открой» на пустом экране раскрывается лист-файл, мигает курсор;
    палец жмёт клавишу на «напиши» и «одно», на «слово» на листе встаёт одна чёрточка-слово с искрой."""
    a, b = T0("s16"), T1("s16")
    o = [room(t)]
    o.append(PR.desk(560, FL - 300, w=900, depth=140, leg_h=260, seed=8))
    o.append(PR.laptop(560, FL - 340, 1.0, open_=1.0, screen="dark", t=t))
    sx0, sy0, sx1, sy1 = 560 - 215, FL - 340 - 445, 560 + 215, FL - 340 - 120
    op = ease_out(ramp(t, W(73) - .05, .35))
    if op > .01:
        cx, cy = (sx0 + sx1) / 2, (sy0 + sy1) / 2
        w2, h2 = (sx1 - sx0) / 2 * .82 * op, (sy1 - sy0) / 2 * .86 * op
        o.append(shape(lib.rect_pts(cx - w2, cy - h2, cx + w2, cy + h2), "#ffffff", "", w=3.4, seed=9760))
        word = ease_out(ramp(t, W(76), .25))
        lx = cx - w2 + 40
        if word > .01:
            o.append(line([(lx, cy - h2 + 60), (lx + 110 * word, cy - h2 + 60)], 12, INK, taper=0, wmin=1, seed=9761))
        cur_x = lx + 110 * word + 18
        if int(t * 3.2) % 2 == 0:
            o.append(line([(cur_x, cy - h2 + 38), (cur_x, cy - h2 + 82)], 5, INK, taper=0, wmin=1, seed=9762))
        o.append(PR.sparkles(lx + 60, cy - h2 + 60, 1.0, bump(t, W(76) + .1, .05, .45), t, seed=16, n=4, r=90))
    presses = (stress(74, .2), stress(75, .2), stress(76, .15))
    pr = max(bump(t, q - .06, .06, .12) for q in presses)
    keyx, keyy = 640, FL - 400
    show = ramp(t, W(74) - .4, .25)
    if show > .01:
        o.append(finger(keyx + 200 * (1 - show), keyy - 60 * (1 - pr) - 200 * (1 - show), 1.0))
        o.append(PR.tap_rings(keyx, keyy, 1.0, pr, t) if hasattr(PR, "tap_rings") else "")
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(76), 8)
    cy_ = 820 + 120 * ease_io(ramp(t, W(74) - .5, .5)) - 140 * ease_io(ramp(t, W(76) - .1, .3))
    return view("".join(o), 560 + dx, cy_ + dy, 1.35 + .15 * u, 0)


# ═════════════════════════ s17–s18: желание догоняет на третьей минуте ═════════════════════════
def minute_dial(x, y, k, prog, t, click=0.0, lit_n=0):
    """Секундомер: сектор бежит по кругу (prog 0…1 — три минуты), три точки-минуты сверху загораются по одной."""
    o = [PR.stopwatch(0, 0, 1.0, hand_a=360 * prog, sector_a=360 * prog, click=click, t=t)]
    for j in range(3):
        on = j < lit_n
        o.append(shape(ellipse_pts(-70 + 70 * j, -260, 22, 22, 12), "#7cc46a" if on else "#e9e2d2", "", w=3.6, seed=9770 + j))
    return tf("".join(o), x, y, k)


def frame_s17(t):
    """«Желание догонит тебя на»: Дима печатает за столом, на стене секундомер — сектор бежит, загораются две минуты;
    слева вприпрыжку несётся облачко-мотивация и догоняет его."""
    a, b = T0("s17"), T1("s17")
    o = [room(t, x0=-1400, x1=2400)]
    prog = ease_io(ramp(t, a - .3, W(81) - a + .3)) * (2.9 / 3)
    o.append(PR.glow(760, 520, 220, .4, "#d8f0c8"))
    o.append(minute_dial(760, 540, .7, prog, t, lit_n=1 + (t > W(78)) + 0))
    o.append(chair(DX - 40, FL - 240, 1.0))
    o.append(PR.desk(DESK[0], DESK[1], w=520, depth=100, leg_h=260, seed=7))
    f = dima_sit(DX, DHIP, DK, "type73", t, pose="sit_desk", lean=.12 + .03 * math.sin(t * 9))
    o.append(f["svg"])
    o.append(PR.laptop(LAP[0], LAP[1], .5, open_=1.0, screen="on", lines=ramp(t, a, b - a), t=t))
    o.append(run_cloud(t, a - .5, lambda tt: -300 + 420 * (tt - a), FL, .5, 1.0, seed=3))
    o.append(PR.speed_arcs(-300 + 420 * (t - a) - 140, FL - 200, 1.0, 1.0, t, seed=17, n=3, ang=180))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(78), 7)
    return view("".join(o), 380 + 80 * u + dx, 880 + dy, 1.2 + .1 * u, 0)


def frame_s18(t):
    """«третьей минуте»: третья точка загорается, облачко прыгает Диме на плечо и светится; он улыбается и печатает;
    камера отходит к ракурсу хука — часы спокойны, табличка больше не висит."""
    a, b = T0("s18"), T1("s18")
    jump = ease_io(ramp(t, a - .1, .45))
    hx_, hy_ = DX - 30, DHIP - 330
    x0, y0 = 110, FL - 180
    mx = x0 + (hx_ - x0) * jump
    my = y0 + (hy_ - y0) * jump - 260 * math.sin(math.pi * jump)
    land = bump(t, a + .35, .04, .2)
    cl = mot(mx, my, .42, 1.0, t, face=1.0, legs=1.0 - jump, squash=.6 * land, rot=-8 * math.sin(math.pi * jump), seed=3)
    body, f = desk_world(t, typing=True, screen="on", lines=.6 + .4 * ramp(t, a, b - a), clock_calm=1.0, mot_on=cl)
    o = [body]
    o.append(minute_dial(560, 560, .42, 1.0, t, lit_n=2 + (t > W(81)), click=bump(t, W(81), .04, .2)))
    o.append(PR.sparkles(hx_, hy_, 1.4, bump(t, a + .35, .05, .5), t, seed=18, n=5, r=150))
    u = ease_io(ramp(t, a + .3, b - a - .3))
    dx, dy = shake(t, a + .35, 7)
    cx = 470 + (530 - 470) * u
    cy = 760 + (770 - 760) * u
    return view(o[0] + "".join(o[1:]), cx + dx, cy + dy, 1.9 - .18 * u, 0)
