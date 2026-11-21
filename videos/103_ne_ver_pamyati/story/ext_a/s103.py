"""Рилс 103 «Не верь памяти», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу); числа в коде — длительности движений.
Говорит Дима от первого лица (имя не звучит и не пишется). Сквозные места: лестничная площадка у двери квартиры (хук, петля),
прихожая рилса 82 (тумбочка, крючки, дверь), телефон, календарь, квитанция, комната, диван.
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
    """Кодовое слово печатными: жирный IDB, жёлтый с чёрной обводкой и тенью (как «КОТ» в рилсах 101, 102); буквы выскакивают по
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
    """«КОТ» держится маленьким вверху до конца призыва (планы s13–s15)."""
    if NOCAM:
        return ""
    k = SH["kot"]
    if t < k["t_in"] - .01 or t > k["t_out"]:
        return ""
    return kot_print(t, -9.0, 540, 330, 150)


def over(t):
    return title(t) + plate(t, SH["label"]) + plate(t, SH["label2"], w=600) + kot_small(t)


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
            blur += (f'<use href="#hk103" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk103">{body}</g></g>{blur}'


def cat(x, y, k, t, st=None):
    st = dict(dict(look=(-.4, -.2), tail=8 * math.sin(t * 1.7), flame_e=1.0), **(st or {}))
    return CT.draw(x, y, k, st, t)


# ═════════════════════════ предметы ═════════════════════════
def keys(x, y, k, t, rot=0.0, seed=0):
    """Связка ключей: (x, y) — кольцо (точка подвеса), ключи висят вниз; rot — поворот вокруг кольца."""
    return tf(f'<g transform="translate(0 -40)">{PR.thief_keys(0, 0, 1.0, 0.0, t, seed)}</g>', x, y, k, rot)


def cabinet(x, y, k=1.0, seed=0):
    """Тумбочка в прихожей: (x, y) — центр низа; верх на y − 410·k."""
    o = [blob(ellipse_pts(x + 8, y + 6, 200 * k, 16 * k, 16), "#000000", .16)]
    w, h = 170 * k, 410 * k
    inner = blob(lib.rect_pts(x + w - 34 * k, y - h + 40 * k, x + w, y), RM.WOOD_SH, .8)
    for j, (a, b) in enumerate(((y - h + 60 * k, y - h + 200 * k), (y - h + 220 * k, y - 30 * k))):
        inner += shape(lib.rrect(x - w + 24 * k, a, x + w - 24 * k, b, 10 * k), RM.WOOD_HI, blob(lib.rect_pts(x - w + 24 * k, b - 18 * k, x + w - 24 * k, b),
                       RM.WOOD_SH, .6), w=3.2 * k, seed=9300 + seed + j)
        inner += shape(ellipse_pts(x, (a + b) / 2, 18 * k, 14 * k, 12), "#c9ced6", "", w=2.6 * k, seed=9310 + seed + j)
    o.append(shape(lib.rect_pts(x - w, y - h + 30 * k, x + w, y), RM.WOOD, inner, w=4.0 * k, seed=9320 + seed))
    o.append(shape(lib.rrect(x - w - 18 * k, y - h, x + w + 18 * k, y - h + 34 * k, 8 * k), RM.WOOD_HI,
                   blob(lib.rect_pts(x - w - 18 * k, y - h + 22 * k, x + w + 18 * k, y - h + 34 * k), RM.WOOD_SH, .8), w=3.8 * k, seed=9330 + seed))
    return "".join(o)


def earbuds(x, y, k=1.0, seed=0):
    """Футляр наушников с двумя наушниками (центр)."""
    o = [shape(lib.rrect(-90, -50, 90, 70, 44), "#f7f7f4", blob(lib.rrect(-90, 30, 90, 70, 30), "#d9dbd6", .8)
               + line([(-88, -6), (88, -6)], 3, "#9aa0a6", taper=0, wmin=1, seed=9401), w=4, seed=9400 + seed)]
    o.append(shape(ellipse_pts(0, 30, 10, 6, 10), "#7fc1e6", "", w=2, seed=9402))
    for s in (-1, 1):
        o.append(shape(ellipse_pts(s * 46, -88, 30, 26, 14), "#ffffff", blob(ellipse_pts(s * 50, -82, 14, 10, 10), "#d9dbd6"), w=3.4, seed=9403 + s))
        o.append(shape(lib.rrect(s * 46 - 10, -76, s * 46 + 10, -18, 8), "#ffffff", "", w=3.0, seed=9406 + s))
    return tf("".join(o), x, y, k)


def pass_card(x, y, k=1.0, rot=0.0, seed=0):
    """Пропуск на ленте: синяя карточка с фото и словом «ПРОПУСК» (центр карточки)."""
    o = [line([(-60, -150), (0, -260), (60, -150)], 10, "#d9483b", taper=0, wmin=1, seed=9500)]
    o.append(shape(lib.rrect(-150, -150, 150, 100, 18), "#5BA7E0", blob(lib.rrect(-150, -150, 150, -90, 18), "#3d82c0"), w=4.4, seed=9501 + seed))
    o.append(shape(lib.rrect(-24, -140, 24, -116, 6), "#e9eef3", "", w=2.4, seed=9502))
    o.append(shape(lib.rrect(-126, -70, -30, 60, 10), "#f2d1b3", blob(ellipse_pts(-78, -20, 26, 30, 14), "#e0b892")
                   + blob(ellipse_pts(-78, 52, 44, 30, 14), "#3d5277"), w=3.0, seed=9503))
    o.append(text("ПРОПУСК", 50, -36, 36, fill="#ffffff", stroke="#1d2448", sw=5))
    for j in range(2):
        o.append(line([(-14, 4 + 34 * j), (126, 4 + 34 * j)], 6, "#e9eef3", taper=0, wmin=1, seed=9510 + j))
    return tf("".join(o), x, y, k, rot)


def badge(x, y, k, t, ta, inner, seed=0):
    """Предмет в белом круге выскакивает на своём слове ta и чуть покачивается."""
    if t < ta:
        return ""
    s = pop(t, ta, .26)
    o = [shape(ellipse_pts(0, 0, 150, 150, 30), "#ffffff", "", w=6, seed=9600 + seed)]
    o.append(inner)
    return tf("".join(o), x, y + 6 * math.sin(t * 4 + seed), k * s, 5 * math.sin(t * 3 + seed))


def mini_phone(x, y, k, rot=0.0, screen="#2f3a55", inner=""):
    """Телефон в руке (центр), экран 120×220 в своих координатах."""
    o = [shape(lib.rrect(-72, -128, 72, 128, 22), "#2a2d36", "", w=4, seed=9700)]
    o.append(shape(lib.rrect(-60, -112, 60, 112, 12), screen, inner, w=2.4, seed=9701))
    return tf("".join(o), x, y, k, rot)


# ═════════════════════════ лестничная площадка (хук s01, s04, петля s22) ═════════════════════════
FLL = 1560.0
LDOOR = (500.0, FLL)
LDOOR_K = 1.25
L_WALL, L_WALL2, L_TILE = "#cfdcc6", "#8fae94", "#b9b2a4"


def door_open(x, y, k, u, t=0.0, out_col="#fff4d6", seed=1, col="#9a5b3a"):
    """Дверь квартиры в проёме, u 0…1 — открыта к нам (полотно поворачивается на петлях слева, сужается и темнеет); в проёме —
    тёплый свет прихожей."""
    o = [shape([(-236, 0, 1), (-236, -960, 1), (236, -960, 1), (236, 0, 1), (210, 0, 1), (210, -936, 1), (-210, -936, 1), (-210, 0, 1)],
               "#E8DFCF", "", w=4.2, seed=71400 + seed)]
    if u > .01:
        g = lib.lin_grad([(0, out_col, 1), (1, lib.mix(out_col, "#c9b28a", .5), 1)], 0, 0, 0, 1)
        o.append(f'<rect x="-210" y="-936" width="420" height="936" fill="url(#{g})"/>')
        o.append(blob([(-210, -40), (210, -40), (210, 0), (-210, 0)], "#d9c49c"))
        o.append(PR.glow(0, -500, 380, .6 * u, "#fff6d0"))
    leaf = PR.door(0, 0, 1.0, seed=seed, col=col)
    leaf += shape(lib.rrect(-40, -820, 40, -770, 8), "#d8b24a", "", w=3, seed=71460) + text("47", 0, -782, 34, fill="#3a2a1a", stroke="#d8b24a", sw=1)
    leaf += shape(ellipse_pts(0, -640, 11, 11, 10), "#c9ced6", blob(ellipse_pts(0, -640, 5, 5, 8), "#3a3d46"), w=2.4, seed=71461)
    c = lib.clip_rect(-212, -940, 424, 952)
    sx = 1 - 1.55 * ease_io(clamp(u))
    shade = .35 * clamp(u)
    leaf_g = f'<g clip-path="url(#{c})">{leaf}</g>'
    if shade > .01:
        leaf_g += f'<rect x="-210" y="-936" width="420" height="936" fill="#000" opacity="{shade:.3f}" clip-path="url(#{c})"/>'
    o.append(f'<g transform="translate(-210 0) scale({sx:.4f} 1) translate(210 0)">{leaf_g}</g>')
    return tf("".join(o), x, y, k)


def landing(t, door=0.0):
    o = [rect(-1200, -1400, 2400, FLL, L_WALL)]
    o.append(rect(-1200, 900, 2400, FLL, L_WALL2))
    o.append(line([(-1200, 900), (2400, 900)], 5, "#5d7a62", taper=0, wmin=1, seed=31))
    o.append(rect(-1200, FLL, 2400, FLL + 1400, L_TILE))
    for i in range(-8, 20):
        o.append(line([(i * 160, FLL + 4), (i * 160 - (i * 160 - 540) * .6, FLL + 700)], 2.4, "#9a9384", seed=40 + i % 9, op=.8))
    for j, yy in enumerate((FLL + 60, FLL + 150, FLL + 280)):
        o.append(line([(-1200, yy), (2400, yy)], 2.4, "#9a9384", taper=0, wmin=1, seed=60 + j, op=.7))
    o.append(line([(-1200, FLL), (2400, FLL)], 5, seed=33))
    # перила лестницы справа и щиток слева
    for j in range(5):
        x = 1220 + 110 * j
        o.append(line([(x, FLL), (x - 40, 1050)], 9, "#5a4a3a", taper=0, wmin=1, seed=70 + j))
    o.append(line([(1180, 1060), (1800, 990)], 18, "#7a5a40", taper=0, wmin=1, seed=79))
    o.append(shape(lib.rrect(-120, 420, 80, 760, 10), "#c9ced6", blob(lib.rect_pts(40, 420, 80, 760), "#a9aeb6", .8), w=4, seed=81))
    # лампа под потолком
    o.append(PR.glow(500, 180, 360, .35, "#fff3c8"))
    o.append(shape(ellipse_pts(500, 170, 90, 34, 18), "#f6efd8", "", w=3.6, seed=82))
    # коврик
    o.append(shape(lib.rrect(LDOOR[0] - 260, FLL + 10, LDOOR[0] + 260, FLL + 80, 14), "#7c5a8a", blob(lib.rrect(LDOOR[0] - 230, FLL + 24, LDOOR[0] + 230,
                   FLL + 66, 10), "#9a78a8"), w=3.4, seed=83))
    o.append(door_open(LDOOR[0], LDOOR[1], LDOOR_K, door, t))
    return "".join(o)


HIT01 = stress(2, .4)                       # «памЯти»: карманы пустые
DOOR_C = (LDOOR[0], LDOOR[1] - 600 * LDOOR_K)


def slam_u(t, t_slam):
    """Дверь приоткрыта и захлопывается к t_slam."""
    return .42 * (1 - lib.ease_in(ramp(t, t_slam - .2, .2)))


def dima_pockets(x, hip, k, t, expr, rate=6.0, on=1.0):
    """Дима хлопает себя по карманам: руки то в карманах, то хлопают по бокам."""
    u = on * (.5 + .5 * math.sin(t * rate * 2 * math.pi))
    return people.dima82(x, hip, k, expr, ("d82_rest", "d82_pocket"), u=u, t=t, feet="stand", flip=True,
                         head_add=-.08 * on + .03 * math.sin(t * 13))


def hook_cam_scene(t):
    u = ease_io(clamp((t + .2) / 1.5))
    return 650 - 30 * u, 962 + 10 * u, .82 + .05 * u


def frame_s01(t):
    """ХУК: площадка, дверь захлопывается с кадра 0; Дима хлопает по пустым карманам; на «памяти» паника; в конце камера влетает
    в дверь (к глазку)."""
    door = slam_u(t, .07)
    o = [landing(t, door)]
    hip = FLL - (people.LEG_LEN - 12) * .66 - 6
    panic = ramp(t, HIT01 - .25, .15)
    f = dima_pockets(840, hip, .66, t, "panic82" if panic > .5 else "puzzled82", on=ramp(t, .12, .1))
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.speed_arcs(LDOOR[0] + 300, LDOOR[1] - 700, 1.3, 1 - ramp(t, .1, .35), t, seed=3, n=3, ang=180))
    for j, dx in enumerate((-260, 260)):
        o.append(PR.dust_puff(LDOOR[0] + dx, LDOOR[1] - 20, 1.0, ramp(t, .07, .5), seed=j) if hasattr(PR, "dust_puff") else "")
    if t > HIT01 - .1:
        o.append(PR.question_mark(hx - 190, hy - 40, 1.0 * pop(t, HIT01 - .1, .25), 1.0, col="#e2574c"))
        o.append(PR.sweat(hx - 70, hy - 40, 1.1, -20))
    cx, cy, s = hook_cam_scene(t)
    dive = lib.ease_in(ramp(t, 1.02, T1("s01") - 1.02), 3)
    cx += (DOOR_C[0] - cx) * dive
    cy += (DOOR_C[1] - 160 - cy) * dive
    s *= 1 + 7.0 * dive
    dx, dy = shake(t, .07, 16)
    dx2, dy2 = shake(t, HIT01, 10)
    v = f'<g transform="{lib.cam(cx + dx + dx2, cy + dy + dy2, s, 0)}">{"".join(o)}</g>'
    if NOCAM:
        return lib.svg(f'<rect width="1080" height="1920" fill="{BG}"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT01) + over(t))


def frame_s22(t):
    """Петля: тот же кадр хука — площадка, дверь приоткрыта и вот-вот захлопнется, Дима тянет её."""
    a, b = T0("s22"), T1("s22")
    door = slam_u(t, b + .07)
    o = [landing(t, door)]
    hip = FLL - (people.LEG_LEN - 12) * .78 - 6
    f = people.dima82(860, hip, .78, "calm82", "d82_rest", t=t, feet="stand", flip=True)
    o.append(f["svg"])
    u = ease_io(ramp(t, a, b - a))
    c0 = hook_cam_scene(0.0)
    import anim
    hc = anim.hook_cam(0.0, hit=HIT01)
    s = c0[2] * (1 + (hc["zoom"] - 1) * u)
    return view("".join(o), c0[0], c0[1], s, hc["rot"] * u, t=t)


def frame_s04(t):
    """«Покажу, что поменял»: та же площадка, дверь закрыта, Дима спокойно поднимает палец, кот садится рядом на коврик; на «поменял»
    над Димой загорается лампочка."""
    a, b = T0("s04"), T1("s04")
    o = [landing(t, 0.0)]
    hip = FLL - (people.LEG_LEN - 12) * .78 - 6
    t_idea = W(12)
    f = people.dima82(820, hip, .78, "sure82" if t < t_idea else "proud82", "d82_one", t=t, feet="stand", flip=True,
                      head_add=.08 * bump(t, t_idea, .08, .3))
    o.append(f["svg"])
    hx, hy = f["head"]
    walk = ease_out(ramp(t, a, .5))
    o.append(cat(380 + 140 * walk, FLL + 40, .7, t, dict(look=(.7, -.5), walk=(t * 3) if walk < 1 else None, smile=.8,
                                                         tail=12 * math.sin(t * 3))))
    if t > t_idea:
        o.append(PR.glow(hx, hy - 300, 240, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx, hy - 300 + 8 * math.sin(t * 5), 1.2 * pop(t, t_idea, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx, hy - 300, 2.0, bump(t, t_idea, .05, .5), t, seed=41, n=5, r=220))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_idea, 9)
    return view("".join(o), 650 + dx, 1080 + dy - 30 * u, 1.0 + .1 * u, -1 + 2 * u, t=t)


# ═════════════════════════ прихожая (рилс 82): тумбочка, крючки, дверь ═════════════════════════
FL82 = RM.FL82
HK = .85
HHIP = FL82 - 598 * HK
CAB = (360.0, FL82)
CAB_TOP = FL82 - 410
KEYS_ON_CAB = (330.0, CAB_TOP + 4)
HOOK = (RM.HALL82["keys"][0], RM.HALL82["keys"][1] - 14)    # крючок среднего
HDOOR = RM.HALL82["door"]
HDOOR_C = (HDOOR[0], HDOOR[1] - 624)


def keys_lying(t, jump=0.0):
    x, y = KEYS_ON_CAB
    return keys(x, y - 40 * jump, .5, t, rot=-78 + 10 * jump)


def frame_s02(t):
    """Камера вылетает из двери внутрь прихожей: на тумбочке лежит связка ключей, кот сидит рядом и смотрит на неё; трогает лапой —
    связка подпрыгивает («звяк»)."""
    a, b = T0("s02"), T1("s02")
    h = RM.hall82(t, "evening")
    o = [h["bg"], cabinet(*CAB), h["door"](0.0)]
    t_tap = W(4) + .05
    jump = bump(t, t_tap, .05, .18)
    o.append(PR.glow(KEYS_ON_CAB[0], KEYS_ON_CAB[1] - 20, 200, .5, "#fff1b0"))
    o.append(keys_lying(t, jump))
    o.append(PR.sparkles(KEYS_ON_CAB[0], KEYS_ON_CAB[1] - 60, 1.4, bump(t, t_tap, .05, .45), t, seed=11, n=5, r=150))
    paw = ease_out(ramp(t, t_tap - .2, .2)) * (1 - ease_io(ramp(t, t_tap + .2, .3)))
    o.append(cat(620, FL82, .85, t, dict(look=(-.9, -.6), paw_l=paw, perk=.6 + .4 * paw, tail=14 * math.sin(t * 4), turn=-.3)))
    u = ease_out(ramp(t, a, .45))
    s = 5.5 + (1.15 - 5.5) * u
    cx = HDOOR_C[0] + (480 - HDOOR_C[0]) * u
    cy = HDOOR_C[1] - 160 + (1180 - HDOOR_C[1] + 160) * u
    drift = ease_io(ramp(t, a + .45, b - a))
    dx, dy = shake(t, t_tap, 8)
    return view("".join(o), cx - 20 * drift + dx, cy + dy, s + .06 * drift, t=t)


def frame_s03(t):
    """«не возвращался за ключами»: дверь открыта, Дима крутит связку на пальце и уходит к выходу; на «ключами» связка звякает."""
    a, b = T0("s03"), T1("s03")
    h = RM.hall82(t, "morning")
    o = [h["bg"], cabinet(*CAB), h["door"](.85)]
    x = 600 + 120 * ease_io(ramp(t, a, b - a))
    f = people.dima82(x, HHIP, HK, "proud82", "d82_one", t=t, feet="stand", head_add=.04 * math.sin(t * 6))
    o.append(f["svg"])
    hx_, hy_ = f["hold"]
    spin = 540 * (t - a) + 200 * bump(t, W(9), .05, .3)
    o.append(keys(hx_ + 6, hy_ - 92 * HK, .42, t, rot=spin))
    o.append(PR.speed_arcs(hx_ + 80, hy_ - 120, .8, .8, t, seed=4, n=3, ang=0))
    o.append(PR.sparkles(hx_, hy_ - 80, 1.4, bump(t, W(9), .05, .45), t, seed=12, n=5, r=160))
    o.append(cat(330, CAB_TOP, .62, t, dict(look=(.8, -.3), smile=1.0, tail=18 * math.sin(t * 5))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(9), 8)
    return view("".join(o), 700 + 60 * u + dx, 1040 + dy, .9 + .08 * u, 1 - 2 * u, t=t)


def frame_s05(t):
    """«Раньше выходил и через минуту»: утро, Дима идёт к двери и выходит, дверь закрывается; камера едет к тумбочке: ключи остались
    лежать, кот смотрит на них, потом на дверь."""
    a, b = T0("s05"), T1("s05")
    h = RM.hall82(t, "morning")
    t_open, t_close = W(14), W(16) + .05
    ajar = ease_out(ramp(t, t_open - .05, .25)) * (1 - lib.ease_in(ramp(t, t_close - .2, .2)))
    o = [h["bg"], cabinet(*CAB), h["door"](ajar)]
    o.append(keys_lying(t))
    out = ramp(t, t_open + .1, t_close - t_open - .25)
    if out < 1:
        x = 520 + (HDOOR[0] + 60 - 520) * ease_io(ramp(t, a, t_open + .35 - a))
        f = people.dima82_walk(x, HHIP, HK * (1 - .12 * out), (t - a) / .55, t=t, expr="calm82", mug=False)
        o.append(f'<g opacity="{1 - out:.3f}">{f["svg"]}</g>')
    look_keys = ramp(t, t_close, .2)
    o.append(cat(600, FL82, .8, t, dict(look=(-.9, -.6) if look_keys > .5 else (.9, -.3), perk=look_keys, tail=10 * math.sin(t * 3))))
    if t > W(17) + .1:
        o.append(PR.question_mark(KEYS_ON_CAB[0] + 40, KEYS_ON_CAB[1] - 210, 1.0 * pop(t, W(17) + .1, .25), 1.0, col="#e2574c"))
        o.append(PR.glow(KEYS_ON_CAB[0], KEYS_ON_CAB[1] - 20, 220, .6 * ramp(t, W(17), .2), "#fff1b0"))
    dx, dy = shake(t, t_close, 10)
    push = ease_io(ramp(t, t_close, .45))
    cx = 760 - 330 * push
    cy = 1060 + 120 * push
    return view("".join(o), cx + dx, cy + dy, .78 + .62 * push, 0, t=t)


def frame_s06(t):
    """«бежал обратно»: дверь распахивается, Дима влетает бегом обратно влево, в панике."""
    a, b = T0("s06"), T1("s06")
    h = RM.hall82(t, "morning")
    ajar = ease_out(ramp(t, a - .05, .18))
    o = [h["bg"], cabinet(*CAB), h["door"](ajar), keys_lying(t)]
    u = t - a
    x = HDOOR[0] + 40 - 440 * ease_out(clamp(u / .9))
    f = people.dima82_run(x, HHIP, HK, u / .33, t=t, expr="panic82", boot=False, socks=None, sandwich=False, lean=.35, flip=True)
    o.append(f["svg"])
    o.append(PR.speed_arcs(x + 260, HHIP - 200, 1.4, 1.0, t, seed=5, n=3, ang=0))
    hx, hy = f["head"]
    o.append(PR.sweat(hx + 70, hy - 40, 1.2, 20))
    o.append(cat(140, FL82, .8, t, dict(look=(.9, -.4), perk=1.0, tail=20 * math.sin(t * 6))))
    dx, dy = shake(t, a + .02, 14)
    return view("".join(o), 640 - 100 * ease_io(ramp(t, a, b - a)) + dx, 1040 + dy, .86, -1, t=t)


def frame_s07(t):
    """«ключи, наушники, пропуск»: Дима в панике, над ним по очереди выскакивают три забытых предмета на своих словах."""
    a, b = T0("s07"), T1("s07")
    h = RM.hall82(t, "morning")
    o = [h["bg"], cabinet(*CAB), h["door"](1.0)]
    f = people.dima82(560, HHIP, HK, "panic82", "d82_shrug", t=t, feet="stand", head_add=.05 * math.sin(t * 7))
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.sweat(hx - 70, hy - 40, 1.2, -20))
    row_y = hy - 380
    o.append(badge(hx - 310, row_y + 40, .95, t, W(20), keys(0, -70, .95, t, rot=8 * math.sin(t * 5)), seed=1))
    o.append(badge(hx, row_y - 60, .95, t, W(21), earbuds(0, 30, 1.0), seed=2))
    o.append(badge(hx + 310, row_y + 40, .95, t, W(22), pass_card(0, 50, .7, -6), seed=3))
    for j, w in enumerate((20, 21, 22)):
        o.append(PR.sparkles(hx - 300 + 300 * j, row_y + 20, 1.2, bump(t, W(w), .05, .4), t, seed=30 + j, n=4, r=150))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = 0.0, 0.0
    for w in (20, 21, 22):
        sx, sy = shake(t, W(w), 7)
        dx += sx
        dy += sy
    return view("".join(o), hx + dx, hy - 200 + dy, 1.0 + .08 * u, -1 + 2 * u, t=t)


# ═════════════════════════ телефон крупно (s08, s18) ═════════════════════════
PH_C = (540.0, 980.0)


def phone_hand(t, screen, typing=0.0, shake_u=0.0, thumb_to=None, bg="#3b3552"):
    """Телефон в руке крупно, экран — SVG screen(x0, y0, x1, y1); большой палец печатает (typing) или тянется к thumb_to."""
    cx, cy = PH_C
    o = [rect(-900, -1400, 2200, 2600, bg)]
    o.append(PR.glow(cx, cy, 900, .35, "#8fb7ff"))
    o.append(PR.phone_frame(cx, cy, 1.0, 1.0, glow_=.4, seed=1))
    x0, y0, x1, y1 = PR.phone_frame_rect(cx, cy, 1.0)
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    o.append(f'<g clip-path="url(#{c})">{screen(x0, y0, x1, y1)}</g>')
    o.append(shape([(x0 - 70, y1 - 160), (x0 + 40, y1 + 40), (x1 + 20, y1 + 120), (x1 + 160, y1 + 700), (x0 - 140, y1 + 700)], "#ecc4a2",
                   blob([(x0 - 70, y1 + 200), (x1 + 100, y1 + 300), (x1 + 160, y1 + 700), (x0 - 140, y1 + 700)], "#d9a984", .7), w=5, seed=5020))
    if thumb_to is not None:
        tx, ty = thumb_to
    else:
        tx = x0 + 160 + 200 * (.5 + .5 * math.sin(t * 9)) * typing
        ty = y1 - 70 - 40 * abs(math.sin(t * 22)) * typing
    o.append(shape(lib.band([(x1 + 110, y1 + 420), (tx + 30, ty + 40)], 120, 92), "#ecc4a2", "", w=5, seed=5021))
    o.append(shape(ellipse_pts(tx + 22, ty + 18, 30, 38, 14), "#f7ddd0", "", w=3, seed=5022))
    sx = 14 * shake_u * math.sin(t * 60)
    return f'<g transform="translate({sx:.2f} 0)">{"".join(o)}</g>', (x0, y0, x1, y1)


def mom_face(x, y, r):
    o = [shape(ellipse_pts(x, y, r, r, 24), "#f7c9d4", "", w=4, seed=5101)]
    o.append(blob(ellipse_pts(x, y - r * .25, r * .62, r * .55, 18), "#7a4a3a"))
    o.append(shape(ellipse_pts(x, y + r * .05, r * .44, r * .5, 18), "#f2d1b3", "", w=3, seed=5102))
    for s in (-1, 1):
        o.append(blob(ellipse_pts(x + s * r * .17, y, r * .05, r * .07, 8), INK))
    o.append(line([(x - r * .14, y + r * .22), (x, y + r * .3), (x + r * .14, y + r * .22)], 4, INK, taper=.2, wmin=.6, seed=5103))
    return "".join(o)


def call_screen(t, declined_at):
    def scr(x0, y0, x1, y1):
        g = lib.lin_grad([(0, "#3a4a7a", 1), (1, "#1d2448", 1)], 0, 0, 0, 1)
        o = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>']
        cx = (x0 + x1) / 2
        ring = 0.0 if t > declined_at else .5 + .5 * math.sin(t * 14)
        for j in range(2):
            rr = 120 + 40 * j + 20 * ring
            o.append(f'<circle cx="{cx}" cy="{y0 + 300}" r="{rr:.1f}" fill="none" stroke="#9fc3ff" stroke-width="4" opacity="{.35 - .15 * j:.2f}"/>')
        o.append(mom_face(cx, y0 + 300, 105))
        o.append(text("Мама", cx, y0 + 500, 86, fill="#ffffff", stroke="#1d2448", sw=4))
        if t < declined_at:
            o.append(text("входящий звонок", cx, y0 + 560, 36, fill="#c9d6ff", stroke="#1d2448", sw=1))
            for j, (bx, col, lab) in enumerate(((cx - 140, "#e2574c", "позже"), (cx + 140, "#3fb26a", "ответить"))):
                o.append(shape(ellipse_pts(bx, y1 - 220, 64, 64, 24), col, "", w=4, seed=5110 + j))
                o.append(line([(bx - 26, y1 - 210), (bx - 10, y1 - 232), (bx + 10, y1 - 232), (bx + 26, y1 - 210)], 9, "#ffffff", taper=0, wmin=1,
                              seed=5112 + j))
                o.append(text(lab, bx, y1 - 120, 34, fill="#ffffff", stroke="#1d2448", sw=1))
        else:
            o.append(text("звонок отклонён", cx, y0 + 560, 36, fill="#ffb3a8", stroke="#1d2448", sw=1))
            u = ease_out(ramp(t, W(25), .25))
            if u > 0:
                s = .5 + .5 * lib.back_out(u, 2.0) if u < 1 else 1.0
                bub = (f'<rect x="-230" y="-60" width="460" height="120" rx="34" fill="#DCF8C6" stroke="#2a2a30" stroke-width="4"/>'
                       + plain("перезвоню!", 0, 18, 56, anchor="middle"))
                o.append(f'<g transform="translate({cx:.1f} {y1 - 230 - 40 * u:.1f}) scale({s:.4f})">{bub}</g>')
        return "".join(o)
    return scr


def frame_s08(t):
    """«Обещал перезвонить маме»: звонит «Мама», телефон вибрирует; палец жмёт «позже»; на «маме» уходит «перезвоню!»."""
    a, b = T0("s08"), T1("s08")
    t_dec = W(24) + .3
    x0, y0, x1, y1 = PR.phone_frame_rect(*PH_C, 1.0)
    reach = ease_io(ramp(t, t_dec - .35, .3)) * (1 - ease_io(ramp(t, t_dec + .1, .3)))
    rest = (x1 + 60, y1 + 60)
    tgt = ((x0 + x1) / 2 - 140 - 22, y1 - 220 - 18)
    thumb = (rest[0] + (tgt[0] - rest[0]) * reach, rest[1] + (tgt[1] - rest[1]) * reach)
    body, _ = phone_hand(t, call_screen(t, t_dec), shake_u=1.0 if t < t_dec else 0.0, thumb_to=thumb)
    o = [body, PR.tap_rings(tgt[0] + 22, tgt[1] + 18, ramp(t, t_dec, .3), 1.2, col="#FFD23F") if t > t_dec else ""]
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_dec, 8)
    return view("".join(o), 560 + dx, 1000 + dy - 40 * u, 1.0 + .1 * u, -2 + 3 * u, bg="#3b3552", t=t)


def note_screen(t, lines):
    """Экран заметки: жёлтая шапка «Заметка», строки с квадратиками появляются по времени (t_in)."""
    def scr(x0, y0, x1, y1):
        o = [rect(x0, y0, x1, y1, "#fffbea")]
        o.append(rect(x0, y0, x1, y0 + 130, "#FFD23F"))
        o.append(plain("Заметка", x0 + 40, y0 + 88, 56, fill="#1d2448"))
        for j in range(9):
            o.append(line([(x0 + 30, y0 + 250 + 110 * j), (x1 - 30, y0 + 250 + 110 * j)], 2, "#eadfb8", taper=0, wmin=1, seed=5200 + j))
        for j, (s, ta) in enumerate(lines):
            if t < ta:
                continue
            yy = y0 + 230 + 110 * j
            n = int(len(s) * clamp((t - ta) / .3))
            o.append(shape(lib.rrect(x0 + 34, yy - 40, x0 + 84, yy + 10, 8), "#ffffff", "", w=3.4, seed=5210 + j))
            o.append(plain(s[:n], x0 + 106, yy, 50))
        return "".join(o)
    return scr


NOTE_LINES = ("позвонить маме", "оплатить свет", "пропуск в рюкзак")


def frame_s18(t):
    """«сразу пишу в одну заметку»: облачка мыслей влетают в телефон, строки заметки печатаются; на «заметку» экран светится."""
    a, b = T0("s18"), T1("s18")
    times = (a + .05, W(74), W(75) + .05)
    typing = 1.0 if t < W(76) + .3 else 0.0
    body, (x0, y0, x1, y1) = phone_hand(t, note_screen(t, list(zip(NOTE_LINES, times))), typing=typing)
    o = [body]
    for j, ta in enumerate(times):           # облачко прилетает сверху в свою строку
        u = ramp(t, ta - .35, .35)
        if 0 < u < 1:
            yy = y0 + 230 + 110 * j
            px = 540 + (x0 + 300 - 540) * u
            py = -100 + (yy - (-100)) * ease_io(u)
            o.append(PR.thought_cloud(px, py, .8 * (1 - .7 * u), 200, 130, 1.0, seed=60 + j, dots=0))
    glow = bump(t, W(76) + .15, .08, .5)
    if glow > .01:
        o.append(PR.glow(540, 980, 600, .5 * glow, "#fff1b0"))
        o.append(PR.sparkles(540, 700, 2.4, glow, t, seed=61, n=6, r=380))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(76) + .15, 8)
    return view("".join(o), 560 + dx, 1000 + dy - 50 * u, 1.0 + .1 * u, 2 - 3 * u, bg="#3b3552", t=t)


# ═════════════════════════ s09: неделя на отрывном календаре ═════════════════════════
ROOM_FL = 1560.0
WALL, WALL_SH, FLOOR_C = "#efe2c8", "#e3d2b2", "#cdb48c"


def room(t, x0=-1400.0, x1=2600.0, dusk=0.0, wall=None):
    wc = lib.mix(wall or WALL, "#c9b6a8", dusk)
    o = [rect(x0, -1400, x1, ROOM_FL, wc)]
    for i in range(int(x0 // 120), int(x1 // 120) + 1):
        xa = i * 120
        o.append(rect(xa, -1400, xa + 46, ROOM_FL, lib.mix(WALL_SH, "#b9a698", dusk), .55))
    o.append(rect(x0, ROOM_FL - 46, x1, ROOM_FL, "#d8c3a0"))
    o.append(line([(x0, ROOM_FL - 46), (x1, ROOM_FL - 46)], 3, seed=7))
    o.append(rect(x0, ROOM_FL, x1, ROOM_FL + 1400, lib.mix(FLOOR_C, "#8c7a66", dusk)))
    o.append(line([(x0, ROOM_FL), (x1, ROOM_FL)], 5, seed=11))
    for i in range(int(x0 // 300), int(x1 // 300) + 1):
        xa = i * 300
        o.append(line([(xa, ROOM_FL + 20), (xa + (xa - 540) * .9, ROOM_FL + 900)], 2.4, "#b0966c", seed=20 + i % 9, op=.8))
    return "".join(o)


def tear_sheet(n, x, y, k=1.0, rot=0.0):
    o = [shape(lib.rrect(-200, -150, 200, 230, 8), "#fffdf6", "", w=4, seed=6000 + n % 5)]
    o.append(text(str(n), 0, 120, 230, fill="#1d2448" if n % 7 else "#d8453a", stroke="#fffdf6", sw=2))
    o.append(text("ноябрь", 0, -80, 44, fill="#6a6f7a", stroke="#fffdf6", sw=1))
    return tf("".join(o), x, y, k, rot)


def tear_calendar(x, y, t, times, first=14):
    """Отрывной календарь: красная шапка, стопка листов; листы слетают в моменты times (каждый уносит день)."""
    o = [shape(lib.rrect(x - 230, y - 290, x + 230, y + 260, 14), "#c9b28a", "", w=4, seed=6100)]
    o.append(shape(lib.rrect(x - 230, y - 290, x + 230, y - 180, 14), "#d8453a", "", w=4, seed=6101))
    for j in (-90, 90):
        o.append(shape(ellipse_pts(x + j, y - 290, 12, 18, 10), "#9aa0aa", "", w=3, seed=6102 + (j > 0)))
    n_off = sum(1 for q in times if t >= q)
    o.append(tear_sheet(first + n_off, x, y - 10))
    for j, q in enumerate(times):
        u = (t - q) / .55
        if 0 <= u < 1:
            fx = x + (160 + 90 * (j % 3)) * u * (1 if j % 2 else -1)
            fy = y - 10 - 260 * u + 900 * u * u
            o.append(f'<g opacity="{1 - u:.3f}">{tear_sheet(first + j, fx, fy, 1 - .3 * u, (40 if j % 2 else -40) * u)}</g>')
    return "".join(o)


def notice(x, y, s, t):
    """Уведомление «Пропущенный: Мама» (центр)."""
    o = [shape(lib.rrect(-300, -76, 300, 76, 30), "#ffffff", "", w=5, seed=6200)]
    o.append(shape(ellipse_pts(-226, 0, 46, 46, 18), "#e2574c", line([(-252, 10), (-236, -12), (-216, -12), (-200, 10)], 8, "#ffffff", taper=0,
                                                                     wmin=1, seed=6202), w=3, seed=6201))
    o.append(plain("Пропущенный", -160, -10, 42, fill="#e2574c"))
    o.append(plain("Мама · 7 дней назад", -160, 44, 36, fill="#1d2448"))
    return tf("".join(o), x, y, s, -2)


def frame_s09(t):
    """«и вспоминал через неделю»: листы отрывного календаря слетают один за другим (14 → 21); на «неделю» уведомление
    «Пропущенный: Мама» и Дима хватается за голову."""
    a, b = T0("s09"), T1("s09")
    o = [room(t)]
    times = [a + .05 + j * (W(29) - a - .05) / 7 for j in range(7)]
    o.append(tear_calendar(400, 760, t, times))
    k = .62
    hip = ROOM_FL - (people.LEG_LEN - 12) * k - 6
    t_n = W(29) + .1
    f = people.dima82(820, hip, k, "panic82" if t > t_n else "puzzled82", "d82_look_up" if t < t_n else "d82_shrug", t=t, feet="stand", flip=True,
                      head_add=.05 * math.sin(t * 6))
    o.append(f["svg"])
    hx, hy = f["head"]
    if t > t_n:
        o.append(PR.sweat(hx + 70, hy - 40, 1.1, 20))
        o.append(notice(470, 360, .9 * pop(t, t_n, .28), t))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_n, 10)
    return view("".join(o), 560 + dx, 900 + dy, 1.0 + .06 * u, 0, t=t)


# ═════════════════════════ s10: квитанция и штамп ПЕНИ ═════════════════════════
def receipt(x, y, t, stamp_t):
    o = [blob(lib.rect_pts(x - 330, y - 520, x + 350, y + 540), "#000000", .12)]
    edge = [(x - 340, y - 540, 1), (x + 340, y - 540, 1)] + [(x + 340 - 680 * j / 16, y + 520 + (14 if j % 2 else 0)) for j in range(17)]
    o.append(shape(edge, "#fffdf6", "", w=4.6, seed=6300))
    o.append(text("КВИТАНЦИЯ", x, y - 430, 70, fill="#1d2448", stroke="#fffdf6", sw=2))
    o.append(PR.idea_bulb(x - 200, y - 250, 1.1, on=.8, t=t, rays=False))
    o.append(plain("за свет", x - 120, y - 230, 64))
    for j in range(5):
        o.append(line([(x - 270, y - 90 + 70 * j), (x + 270 - 120 * (j % 2), y - 90 + 70 * j)], 6, "#c9c2b0", taper=0, wmin=1, seed=6310 + j))
    late = t > stamp_t
    o.append(plain("Итого:", x - 270, y + 330, 58))
    amt = "1240 руб" if not late else "1390 руб"
    o.append(plain(amt, x + 270, y + 330, 64, fill="#c0392b" if late else "#1d2448", anchor="end"))
    if late:
        u = clamp((t - stamp_t) / .12)
        s = 1.8 - .8 * ease_out(u)
        st = (f'<rect x="-210" y="-90" width="420" height="180" rx="16" fill="none" stroke="#d8453a" stroke-width="16"/>'
              + text("ПЕНИ", 0, 50, 140, fill="#d8453a", stroke="#d8453a", sw=.01))
        o.append(f'<g opacity="{.4 + .55 * u:.3f}" transform="translate({x + 60} {y + 90}) rotate(-14) scale({s:.4f})">{st}</g>')
        for j in range(6):
            ang = math.radians(j * 60 + 20)
            r = 260 + 80 * ramp(t, stamp_t, .3)
            o.append(blob(ellipse_pts(x + 60 + r * math.cos(ang), y + 90 + r * .6 * math.sin(ang), 12, 10, 8), "#d8453a", 1 - ramp(t, stamp_t + .2, .5)))
    return "".join(o)


def frame_s10(t):
    """«А за свет платил с пенями»: квитанция за свет на столе крупно; на «пенями» сверху бьёт красный штамп «ПЕНИ», сумма краснеет."""
    a, b = T0("s10"), T1("s10")
    t_st = W(35) + .05
    o = [rect(-800, -800, 1900, 2800, "#c9a77c")]
    for j in range(10):
        o.append(line([(-800, 200 * j), (1900, 200 * j + 40)], 3, "#b08d64", taper=0, wmin=1, seed=6400 + j, op=.7))
    o.append(receipt(540, 800, t, t_st))
    k = .9
    hip = 2200
    f = people.dima82(880, hip, k, "panic82" if t > t_st else "squint82", "d82_rest", t=t, feet=None, flip=True)
    o.append(f["svg"] if t > t_st - .3 else "")
    u = ease_io(ramp(t, a, t_st - a))
    dx, dy = shake(t, t_st, 16)
    cy = 820 + 110 * u
    return view("".join(o), 540 + dx, cy + dy, 1.12 - .08 * u + .1 * bump(t, t_st, .05, .3), -1 + 2 * u, bg="#c9a77c", t=t)


# ═════════════════════════ s11: «точно помнил», свет гаснет ═════════════════════════
def ceiling_lamp(x, y, on):
    o = [line([(x, -800), (x, y - 40)], 4, "#3a3d46", taper=0, wmin=1, seed=6500)]
    if on > .01:
        o.append(PR.glow(x, y + 30, 420, .55 * on, "#fff1c0"))
    o.append(shape([(x - 110, y + 30, 1), (x - 60, y - 40, 1), (x + 60, y - 40, 1), (x + 110, y + 30, 1)], lib.mix("#8a8f99", "#f0d27a", on), "",
                   w=4, seed=6501))
    o.append(shape(ellipse_pts(x, y + 34, 34, 22, 12), lib.mix("#c9ced6", "#fff6c8", on), "", w=3, seed=6502))
    return "".join(o)


def frame_s11(t):
    """«потому что „точно помнил“»: Дима уверенно стучит пальцем по виску; на «помнил» щёлк — свет гаснет, комната в темноте."""
    a, b = T0("s11"), T1("s11")
    t_off = W(39) + .1
    on = 0.0 if t > t_off else 1.0
    o = [room(t)]
    o.append(ceiling_lamp(540, 420, on))
    o.append(RM.wall_picture(200, 760, 220, 170, "day", seed=3) if hasattr(RM, "wall_picture") else "")
    k = .7
    hip = ROOM_FL - (people.LEG_LEN - 12) * k - 6
    tap = .5 + .5 * math.cos((t - W(38)) * 2 * math.pi * 2.5) if W(38) - .1 < t < t_off else 1.0
    f = people.dima82_temple(560, hip, k, tap, t=t, expr="sure82" if t < t_off else "panic82", feet="stand",
                             head_add=.05 * bump(t, W(38), .08, .3))
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.sparkles(hx - 60, hy - 60, 1.0, bump(t, W(38), .05, .35) * (1 - on * 0), t, seed=70, n=4, r=110))
    dark = ""
    if t > t_off:
        u = ease_out(ramp(t, t_off, .08))
        dark = f'<rect x="-1400" y="-1400" width="4000" height="4000" fill="#0A0E26" opacity="{.72 * u:.3f}"/>'
        dark += PR.glow(hx, hy, 260, .25, "#8fa6ff")
        dark += PR.question_mark(hx + 40, hy - 230, 1.1 * pop(t, t_off + .05, .25), 1.0, col="#ffd23f")
        dark += PR.sparkles(540, 470, 1.2, bump(t, t_off, .03, .25), t, seed=71, n=5, r=120)
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_off, 12)
    return view("".join(o) + dark, 560 + dx, hy + 260 + dy, 1.05 + .12 * u, 0, t=t)


# ═════════════════════════ s12: призыв «КОТ» ═════════════════════════
PAPER = "#f6efdf"


def paper_bg():
    return rect(-2000, -2000, 3500, 4000, PAPER) + "".join(
        line([(-1200, 200 + 90 * j), (2600, 200 + 90 * j)], 2, "#e3d6bb", taper=0, wmin=1, seed=6000 + j) for j in range(24))


def frame_s12(t):
    """«Напиши «КОТ»»: на бумаге крупно печатается жёлтое «КОТ»; Дима внизу слева, кот прыгает и садится рядом с ним."""
    a, b = T0("s12"), T1("s12")
    o = [paper_bg()]
    o.append(PR.glow(540, 700, 420, .5 * ramp(t, W(41), .3), "#ffe9a8"))
    o.append(kot_print(t, W(40) + .05, 540, 760, 300))
    o.append(PR.sparkles(540, 700, 2.4, bump(t, W(41) + .1, .05, .5), t, seed=91, n=6, r=380))
    k = .62
    hip = 1640 - (people.LEG_LEN - 12) * k - 6
    f = people.dima82(330, hip, k, "proud82", "d82_rest", t=t, feet="stand", head_add=.05 * math.sin(t * 3))
    o.append(f["svg"])
    t_j = W(42) - .05
    j = ease_io(ramp(t, t_j, .4))
    x = 1180 + (620 - 1180) * j
    y = 1640 - 260 * math.sin(math.pi * j)
    o.append(cat(x, y, .9, t, dict(look=(-.7, -.4), legs=1.0 - j if j < 1 else 0.0, smile=1.0 if j >= 1 else .4, tail=10 * math.sin(t * 3))))
    if j >= 1:
        o.append(PR.heart(480, 1060 - 30 * ramp(t, t_j + .4, .8), .6 * pop(t, t_j + .4, .25), beat=bump(t, t_j + .4, .05, .3)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(41), 8)
    return view("".join(o), 540 + dx, 1020 + dy, 1.0 + .06 * u, 0, bg=PAPER, t=t)


# ═════════════════════════ s13–s14: «потом вспомню» → один шаг на две минуты ═════════════════════════
def step_card(x, y, k, t, ring=0.0, done=0.0, rot=0.0):
    """Жёлтая карточка шага: «ОДИН ШАГ», «оплатить свет», кольцо таймера «2 МИН»."""
    o = [blob(lib.rrect(-290, -230, 310, 250, 26), "#000000", .14)]
    o.append(shape(lib.rrect(-300, -240, 300, 240, 26), "#FFE58A", "", w=5, seed=6600))
    o.append(text("ОДИН ШАГ", 0, -150, 72, fill="#1d2448", stroke="#FFE58A", sw=2))
    o.append(plain("оплатить свет", -250, -40, 58))
    cx, cy, r = 150, 110, 82
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#ffffff" stroke="#1d2448" stroke-width="6"/>')
    if ring > .01:
        a1 = -90 + 360 * clamp(ring)
        large = 1 if a1 + 90 > 180 else 0
        ex, ey = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
        if ring < .999:
            o.append(f'<path d="M{cx} {cy} L{cx} {cy - r} A{r} {r} 0 {large} 1 {ex:.1f} {ey:.1f} Z" fill="#7cc46a" opacity=".85"/>')
        else:
            o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#7cc46a" opacity=".85"/>')
    o.append(text("2", cx, cy + 22, 64, fill="#1d2448", stroke="#ffffff", sw=6))
    o.append(plain("МИН", cx, cy + 128, 34, anchor="middle"))
    o.append(shape(lib.rrect(-250, 60, -110, 160, 14), "#ffffff", "", w=4, seed=6601))
    if done > .01:
        o.append(PR.check_mark(-180, 112, 1.1, done, col="#2f9a4a", seed=1))
    return tf("".join(o), x, y, k, rot)


def frame_s13(t):
    """«„потом вспомню“ сразу становилось»: облачко «потом вспомню» над Димой; на «сразу» оно сжимается и становится карточкой шага."""
    a, b = T0("s13"), T1("s13")
    o = [room(t)]
    k = 1.15
    hip = 2050
    t_m = W(46) - .05
    f = people.dima82(760, hip, k, "puzzled82" if t < t_m else "wow82", "d82_rest", t=t, feet=None, flip=True, head_add=-.06)
    o.append(f["svg"])
    cu = pop(t, a, .25) * (1 - ease_io(ramp(t, t_m, .18)))
    if cu > .01:
        inner = plain("потом", 0, -20, 66, anchor="middle") + plain("вспомню", 0, 56, 66, anchor="middle")
        o.append(PR.thought_cloud(420, 900 + 10 * math.sin(t * 4), 1.0, 380, 250, cu, seed=81, dots=2, inner=inner))
    if t > t_m:
        cu2 = pop(t, t_m + .05, .3)
        o.append(step_card(420, 900, .82 * cu2, t, rot=-4))
        o.append(PR.sparkles(420, 900, 2.2, bump(t, t_m, .05, .45), t, seed=82, n=6, r=330))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_m, 10)
    return view("".join(o), 540 + dx, 1060 + dy, 1.0 + .05 * u, 0, t=t)


def frame_s14(t):
    """«одним шагом на две минуты»: карточка шага крупно, на «две» кольцо таймера начинает заполняться, на «минуты» галочка."""
    a, b = T0("s14"), T1("s14")
    o = [paper_bg()]
    ring = ease_io(ramp(t, W(51), WE(52) + .3 - W(51)))
    done = ease_out(ramp(t, W(52) + .3, .25))
    o.append(step_card(540, 1000, 1.45, t, ring, done, rot=-3 + 2 * math.sin(t * 1.3)))
    o.append(PR.sparkles(540, 1000, 2.6, bump(t, W(52) + .3, .05, .5), t, seed=83, n=6, r=430))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(52) + .3, 9)
    return view("".join(o), 540 + dx, 1000 + dy, .95 + .1 * u, 0, bg=PAPER, t=t)


# ═════════════════════════ s15: кот сидит рядом, пока делаешь ═════════════════════════
def chair(x, y, k=1.0):
    o = [shape(lib.rrect(-100, -16, 110, 10, 6), "#a8774a", "", w=4, seed=1011)]
    o.append(shape([(-100, -16, 1), (-80, -16, 1), (-70, -330, 1), (-92, -330, 1)], "#a8774a", "", w=4, seed=1012))
    for s in (-1, 1):
        o.append(shape([(s * 80 - 9, 8, 1), (s * 80 + 9, 8, 1), (s * 86 + 9, 240, 1), (s * 86 - 9, 240, 1)], "#8a6038", "", w=3.4, seed=1013 + s))
    return tf("".join(o), x, y, k)


def frame_s15(t):
    """«и кот сидел рядом, пока ты его делаешь»: Дима за столом жмёт «оплатить» в телефоне, кот запрыгивает на стол и садится рядом,
    мурчит; на «делаешь» на экране галочка."""
    a, b = T0("s15"), T1("s15")
    fl = 1300.0
    o = [rect(-1400, -1400, 2600, fl, WALL)]
    for i in range(-12, 22):
        o.append(rect(i * 120, -1400, i * 120 + 46, fl, WALL_SH, .55))
    o.append(rect(-1400, fl, 2600, fl + 1400, FLOOR_C))
    o.append(line([(-1400, fl), (2600, fl)], 5, seed=11))
    o.append(PR.window(160, 640, 300, 400, mode="day", t=t, seed=3, curtain=False))
    o.append(chair(320, fl - 240, 1.0))
    desk_y = fl - 300
    o.append(PR.desk(680, desk_y, w=660, depth=100, leg_h=260, seed=7))
    hip = fl - 290
    feet = people.sit_kw(360, hip, .5)["feet"]
    f = people.dima82(360, hip, .5, "calm82" if t < W(60) else "proud82", "sit_desk", t=t, feet=feet, lean_add=.1)
    o.append(f["svg"])
    done = ease_out(ramp(t, W(60), .25))
    scr = rect(-60, -112, 60, 112, "#2f3a55")
    scr += plain("свет", 0, -40, 30, fill="#ffffff", anchor="middle")
    if done > .01:
        scr += PR.check_mark(0, 30, .6, done, col="#7cc46a", seed=2)
    else:
        scr += shape(lib.rrect(-44, 10, 44, 60, 10), "#3fb26a", "", w=2, seed=9711)
    o.append(mini_phone(600, desk_y - 70, .55, -70, inner=scr))
    t_j = W(54) - .1
    j = ease_io(ramp(t, t_j, .4))
    cx_ = 1100 + (850 - 1100) * j
    cy_ = fl + (desk_y - fl) * j - 220 * math.sin(math.pi * j)
    o.append(cat(cx_, cy_, .45, t, dict(look=(-.8, .2), legs=1.0 - j if j < 1 else 0.0, smile=1.0 if j >= 1 else .3,
                                        tail=10 * math.sin(t * 2.5), blink=1.0 if 23.6 < t < 23.75 else 0.0)))
    if j >= 1:
        o.append(PR.purr(cx_ - 60, cy_ - 220, 1.0, t, ramp(t, W(56), .2), seed=1))
    o.append(PR.sparkles(600, desk_y - 90, 1.4, bump(t, W(60), .05, .5), t, seed=84, n=5, r=160))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(56), 6)
    return view("".join(o), 620 + dx, 1000 + dy, 1.55 + .1 * u, 0, t=t)


# ═════════════════════════ s16–s17: решение ═════════════════════════
def frame_s16(t):
    """«Вот что я поменял»: вечерняя прихожая, Дима показывает телефон с заметкой, над ним загорается лампочка; кот на тумбочке."""
    a, b = T0("s16"), T1("s16")
    h = RM.hall82(t, "evening")
    o = [h["bg"], cabinet(*CAB), h["door"](0.0)]
    t_idea = W(61) + .1
    f = people.dima82(700, HHIP, HK, "wow82" if t > t_idea else "sure82", "d82_mug", t=t, feet="stand", flip=True,
                      head_add=.08 * bump(t, t_idea, .08, .3))
    o.append(f["svg"])
    px, py = f["hold"]
    scr = rect(-60, -112, 60, 112, "#fffbea") + rect(-60, -112, 60, -70, "#FFD23F")
    for j in range(4):
        scr += line([(-44, -40 + 40 * j), (44 - 20 * (j % 2), -40 + 40 * j)], 6, "#9aa0a6", taper=0, wmin=1, seed=9720 + j)
    o.append(mini_phone(px - 20, py - 60, .7, 8, inner=scr))
    hx, hy = f["head"]
    if t > t_idea:
        o.append(PR.glow(hx, hy - 300, 240, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx, hy - 300 + 8 * math.sin(t * 5), 1.1 * pop(t, t_idea, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx, hy - 300, 2.0, bump(t, t_idea, .05, .5), t, seed=41, n=5, r=220))
    o.append(cat(360, CAB_TOP, .6, t, dict(look=(.8, -.4), perk=1.0, tail=10 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_idea, 10)
    return view("".join(o), 560 + dx, 1000 + dy, .95 + .12 * u, 1 - 2 * u, t=t)


def frame_s17(t):
    """«Всё, что держу в голове дольше минуты»: над головой Димы кружат облачка с делами (ключи, мама, свет, пропуск); на «минуты»
    выскакивает таймер, облачка дрожат, Дима напрягается."""
    a, b = T0("s17"), T1("s17")
    o = [room(t, dusk=.3)]
    k = 1.2
    hip = 2150
    strain = ramp(t, W(70), .3)
    f = people.dima82(540, hip, k, "squint82" if strain > .5 else "puzzled82", "d82_rest", t=t, feet=None,
                      head_add=.04 * math.sin(t * 5) + .03 * strain * math.sin(t * 40))
    o.append(f["svg"])
    hx, hy = f["head"]
    icons = [keys(0, -50, .42, t), mom_face(0, 0, 60), PR.idea_bulb(0, 0, .9, on=.3, t=t, rays=False), pass_card(0, 20, .35)]
    starts = [a, a + .15, W(68), W(70)]
    for j, (ic, ta) in enumerate(zip(icons, starts)):
        if t < ta:
            continue
        ang = j * 90 + 70 * (t - a) + (8 * strain * math.sin(t * 30 + j))
        r = 360 + 20 * math.sin(t * 3 + j)
        px = hx + r * math.cos(math.radians(ang))
        py = hy - 420 + 170 * math.sin(math.radians(ang))
        o.append(PR.thought_cloud(px, py, .95, 240, 180, pop(t, ta, .25), seed=90 + j, dots=0, inner=ic))
    if t > W(71) - .05:
        o.append(PR.stopwatch(hx + 330, hy + 120, .45 * pop(t, W(71) - .05, .25), hand_a=360 * ramp(t, W(71), 1.2), sector_a=360 * ramp(t, W(71), 1.2),
                              t=t))
        o.append(PR.sweat(hx - 90, hy - 30, 1.3, -20))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(71), 10)
    return view("".join(o), 540 + dx, hy - 120 + dy, .95 + .08 * u, 0, t=t)


# ═════════════════════════ s19–s20: крючок у двери ═════════════════════════
def frame_s19(t):
    """«А ключи живут на одном крючке у двери»: Дима вешает связку на средний крючок, она качается со звяком; на «двери» камера
    отъезжает: крючок у двери, кот сторожит на тумбочке."""
    a, b = T0("s19"), T1("s19")
    h = RM.hall82(t, "evening")
    o = [h["bg"], cabinet(*CAB), h["door"](0.0)]
    t_hang = W(78) + .35
    reach = ease_io(ramp(t, a, t_hang - a))
    away = ease_io(ramp(t, t_hang + .25, .5))
    hx_, hy_ = HOOK
    tgt = (hx_ + 30 + 140 * away, hy_ + 60 + 260 * away + 140 * (1 - reach))
    tgt = (2 * 760 - tgt[0], tgt[1])                 # flip: цель руки зеркалится вокруг таза (как в dima82_temple)
    arms = {"f": ("ang", 0.16, 0.16), "n": ("ik", tgt, 1)}
    hands = {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"dir": (-.6, -1), "curl": (.6, .65, .7, .7), "thumb": .5}}
    f = people.dima82(760, HHIP, HK, "calm82" if t < t_hang else "proud82", "d82_rest", t=t, feet="stand", flip=True, arms=arms, hands=hands)
    o.append(f["svg"])
    if t < t_hang:
        wx, wy = f["hold"]
        o.append(keys(wx, wy - 20, .5, t, rot=10 * math.sin(t * 6)))
    else:
        u = t - t_hang
        sw = 22 * math.exp(-u * 2.2) * math.sin(u * 11)
        o.append(keys(hx_, hy_ + 4, .5, t, rot=sw))
    o.append(PR.sparkles(hx_, hy_ + 80, 1.4, bump(t, W(82), .05, .5), t, seed=50, n=5, r=160))
    guard = ramp(t, W(84) - .2, .3)
    o.append(cat(360, CAB_TOP, .6, t, dict(look=(.7, -.9) if guard < .5 else (.4, -.2), perk=1.0, smug=guard, tail=8 * math.sin(t * 2.5))))
    pull = ease_io(ramp(t, W(84) - .1, .5))
    cx = 560 + (720 - 560) * pull
    cy = 900 + (1060 - 900) * pull
    s = 1.1 + (.72 - 1.1) * pull
    dx, dy = shake(t, t_hang, 8)
    return view("".join(o), cx + dx, cy + dy, s, 0, t=t)


def frame_s20(t):
    """«Сегодня вышел с первого раза»: утро, Дима снимает ключи с крючка и уходит, дверь спокойно закрывается; надпись
    «С ПЕРВОГО РАЗА»; кот на тумбочке машет хвостом."""
    a, b = T0("s20"), T1("s20")
    h = RM.hall82(t, "morning")
    t_grab = W(86) - .3
    t_open, t_close = t_grab + .45, b - .45
    ajar = ease_out(ramp(t, t_open, .35)) * (1 - ease_io(ramp(t, t_close, .35)))
    o = [h["bg"], cabinet(*CAB), h["door"](ajar)]
    hx_, hy_ = HOOK
    out = ramp(t, t_open + .25, t_close - t_open - .25)
    if t < t_grab:
        o.append(keys(hx_, hy_ + 4, .5, t, rot=3 * math.sin(t * 2)))
    if out < 1:
        if t < t_grab + .3:
            reach = ease_io(ramp(t, a, t_grab - a))
            tgt = (2 * 760 - hx_ - 30, hy_ + 60 + 160 * (1 - reach))
            arms = {"f": ("ang", 0.16, 0.16), "n": ("ik", tgt, 1)}
            hands = {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"dir": (-.6, -1), "curl": (.6, .65, .7, .7), "thumb": .5}}
            f = people.dima82(760, HHIP, HK, "calm82", "d82_rest", t=t, feet="stand", flip=True, arms=arms, hands=hands)
        else:
            x = 640 + (HDOOR[0] + 40 - 640) * ease_io(ramp(t, t_grab + .3, t_open + .3 - t_grab))
            f = people.dima82_walk(x, HHIP, HK * (1 - .12 * out), (t - a) / .55, t=t, expr="proud82", mug=False)
        o.append(f'<g opacity="{1 - out:.3f}">{f["svg"]}</g>')
        if t >= t_grab:
            wx, wy = f["hold"]
            o.append(f'<g opacity="{1 - out:.3f}">{keys(wx, wy - 20, .45, t, rot=14 * math.sin(t * 7))}</g>')
    o.append(cat(360, CAB_TOP, .6, t, dict(look=(.8, -.3), smile=1.0, tail=18 * math.sin(t * 4))))
    o.append(PR.sparkles(HDOOR[0], HDOOR[1] - 700, 2.0, bump(t, t_close + .3, .05, .5), t, seed=51, n=5, r=260))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(88), 6)
    return view("".join(o), 700 + 40 * u + dx, 1080 + dy, .78 + .06 * u, 0, t=t)


# ═════════════════════════ s21: вечер, «Мама ❤ 12 мин» ═════════════════════════
def call_card(x, y, s, t, beat):
    o = [blob(lib.rrect(-286, -150, 300, 170, 36), "#000000", .2)]
    o.append(shape(lib.rrect(-300, -160, 300, 160, 36), "#1d2448", "", w=5, seed=6700))
    o.append(mom_face(-190, -20, 74))
    o.append(text("Мама", -70, -30, 76, fill="#ffffff", stroke="#1d2448", sw=2, anchor="start"))
    o.append(PR.heart(170, -54, .55, beat=beat, seed=3))
    o.append(plain("12 мин", -70, 70, 60, fill="#7cc46a"))
    o.append(line([(200, 46), (214, 32), (232, 32), (246, 46)], 8, "#7cc46a", taper=0, wmin=1, seed=6701))
    return tf("".join(o), x, y, s, -2)


def frame_s21(t):
    """«и маме позвонил в тот же вечер»: вечерняя комната, Дима на диване с телефоном, кот рядом; над ним выскакивает экран звонка
    «Мама ❤ 12 мин»."""
    a, b = T0("s21"), T1("s21")
    sc = RM.sofa_scene(t, "evening")
    o = [sc["bg"], sc["sofa"]]
    bs = 1.0
    hx0, hip = RM.SOFA_DIMA
    feet = people.sit_kw(hx0, hip, .5 * bs)["feet"]
    f = people.dima82(hx0, hip, .5, "proud82", "d82_mug", t=t, feet=feet, head_add=.04 * math.sin(t * 2))
    o.append(f["svg"])
    px, py = f["hold"]
    scr = rect(-60, -112, 60, 112, "#1d2448") + shape(ellipse_pts(0, -40, 30, 30, 14), "#f7c9d4", "", w=2, seed=9730)
    o.append(mini_phone(px + 10, py - 40, .45, -8, inner=scr))
    o.append(sc["front"])
    o.append(cat(2440, RM.SOFA_SEAT + 10, .42, t, dict(look=(-.8, -.2), smile=1.0, tail=10 * math.sin(t * 2), blink=1.0 if 35.9 < t < 36.05 else 0.0)))
    o.append(PR.purr(2400, RM.SOFA_SEAT - 200, .8, t, 1.0, seed=2))
    t_c = W(92) - .05
    if t > t_c:
        hx, hy = f["head"]
        o.append(call_card(hx + 120, hy - 400, .62 * pop(t, t_c, .28), t, bump(t, W(96), .05, .3)))
        o.append(PR.sparkles(hx + 120, hy - 400, 1.4, bump(t, W(96), .05, .5), t, seed=52, n=5, r=230))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(96), 6)
    return view("".join(o), 2250 + dx, 950 + dy, 1.2 + .08 * u, 0, t=t)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
