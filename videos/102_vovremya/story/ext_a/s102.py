"""Рилс 102 «30 дней без опозданий», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу); числа в коде — длительности движений.
Говорит Дима от первого лица (имя не звучит и не пишется). Сквозные места: день рождения (торт, гости, дверь), прихожая,
улица, ванная с таймером, телефон с пузырём «буду через 5 минут», схема «назад от двери», призыв «КОТ».
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
import hand_kot  # noqa: E402
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


def title(t):
    if NOCAM:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, text=SH["title"]["text"], t_in=SH["title"]["t_in"], t_out=SH["title"]["t_out"], hits=hits)


def changed_label(t):
    """Маленькая надпись «ВОТ ЧТО Я ПОМЕНЯЛ» — только на фразах 5–6 (с «Вот» до конца «будильника»), вверху кадра."""
    if NOCAM:
        return ""
    a, b = T0("s10"), T1("s13")
    if t < a or t > b + .15:
        return ""
    u = ease_out(ramp(t, a + .02, .2))
    op = 1.0 - ramp(t, b, .15)
    s = .6 + .4 * lib.back_out(u, 2.0) if u < 1 else 1.0
    body = (f'<rect x="-330" y="-62" width="660" height="104" rx="22" fill="#FFD23F" stroke="#111" stroke-width="6"/>'
            + text("ВОТ ЧТО Я ПОМЕНЯЛ", 0, 18, 58, fill="#111", stroke="#111", sw=0.01))
    return f'<g opacity="{op:.3f}" transform="translate(540 220) rotate(-2) scale({s:.4f})">{body}</g>'


BG = "#efe2c8"


def view(body, cx, cy, s, rot=0.0, over="", bg=BG):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


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
            blur += (f'<use href="#hk102" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk102">{body}</g></g>{blur}'


def cat(x, y, k, t, st=None):
    st = dict(dict(look=(-.4, -.2), tail=8 * math.sin(t * 1.7), flame_e=1.0), **(st or {}))
    return CT.draw(x, y, k, st, t)


FL = 1500.0


def stand_hip(k, fl=FL):
    return fl - (people.LEG_LEN - 12) * k - 6


# ═════════════════════════ день рождения ═════════════════════════
C_CREAM, C_SPONGE, C_PINK, C_FLAME = "#FFF1DC", "#E9B98A", "#E98FA6", "#FFB22E"
PARTY_WALL, PARTY_WALL_SH = "#cfe3ee", "#bcd5e4"
DOOR_X, DOOR_K = 150.0, .8
TABLE_X, TABLE_Y = 700.0, FL - 330      # верх столешницы


def door_open(x, y, k, u, t=0.0, out_col="#fff4d6", seed=1):
    """Дверь в проёме, u 0…1 — распахивается к нам (полотно поворачивается на петлях слева, сужается и темнеет);
    в проёме — светлая лестничная площадка."""
    o = [shape([(-236, 0, 1), (-236, -960, 1), (236, -960, 1), (236, 0, 1), (210, 0, 1), (210, -936, 1), (-210, -936, 1), (-210, 0, 1)],
               "#EEE6D6", "", w=4.2, seed=71400 + seed)]
    if u > .01:
        g = lib.lin_grad([(0, out_col, 1), (1, lib.mix(out_col, "#c9b28a", .5), 1)], 0, 0, 0, 1)
        o.append(f'<rect x="-210" y="-936" width="420" height="936" fill="url(#{g})"/>')
        o.append(blob([(-210, -40), (210, -40), (210, 0), (-210, 0)], "#d9c49c"))
        o.append(PR.glow(0, -500, 380, .6 * u, "#fff6d0"))
    leaf = PR.door(0, 0, 1.0, seed=seed)
    c = lib.clip_rect(-212, -940, 424, 952)
    sx = 1 - 1.55 * ease_io(clamp(u))          # < 0 — полотно перевернулось к нам и ушло влево от петель
    shade = .35 * clamp(u)
    leaf_g = f'<g clip-path="url(#{c})">{leaf}</g>'
    if shade > .01:
        leaf_g += f'<rect x="-210" y="-936" width="420" height="936" fill="#000" opacity="{shade:.3f}" clip-path="url(#{c})"/>'
    o.append(f'<g transform="translate(-210 0) scale({sx:.4f} 1) translate(210 0)">{leaf_g}</g>')
    return tf("".join(o), x, y, k)
CANDLES = (-52, -18, 18, 52)


def candle_len(t, burnt=0.0):
    return 48 * (1 - .78 * burnt)


def cake(x, y, k, t, burnt=0.0, out=(), smoke_t=None):
    """Двухъярусный торт с четырьмя свечами (дно в (x, y)); burnt 0…1 — свечи догорели (короче, оплыли воском);
    out — индексы погасших свечей; smoke_t — время, когда гаснет последняя (дымок)."""
    sd = 8300
    o = [shape(ellipse_pts(0, -4, 112, 14, 24), "#F4EEE4", blob(ellipse_pts(0, -2, 92, 8, 20), "#E2D9C8"), w=3.0, seed=sd)]
    b1 = [(-86, -6, 1), (86, -6, 1), (87, -70), (-87, -70)]
    i1 = blob(lib.rect_pts(34, -70, 90, -4), lib.mix(C_SPONGE, "#000000", .12)) + blob(lib.rect_pts(-90, -40, 90, -33), C_CREAM)
    o.append(shape(b1, C_SPONGE, i1, w=3.6, seed=sd + 1))
    o.append(shape(ellipse_pts(0, -70, 87, 15, 22), C_PINK, blob(ellipse_pts(-4, -68, 66, 8, 18), lib.mix(C_PINK, "#ffffff", .3)), w=3.4, seed=sd + 2))
    for j, (dx, h) in enumerate(((-66, 16), (-34, 24), (-4, 14), (28, 22), (60, 15))):
        o.append(shape([(dx - 11, -70, 1), (dx + 11, -70, 1), (dx + 9, -70 + h * .7), (dx, -70 + h), (dx - 9, -70 + h * .7)], C_PINK, "", w=2.8,
                       seed=sd + 20 + j))
    b2 = [(-58, -70, 1), (58, -70, 1), (59, -122), (-59, -122)]
    i2 = blob(lib.rect_pts(22, -122, 60, -70), lib.mix(C_SPONGE, "#000000", .12)) + blob(lib.rect_pts(-60, -98, 60, -91), C_CREAM)
    o.append(shape(b2, C_SPONGE, i2, w=3.4, seed=sd + 3))
    o.append(shape(ellipse_pts(0, -122, 59, 11, 20), C_CREAM, blob(ellipse_pts(-3, -121, 44, 5, 16), "#FFFFFF"), w=3.2, seed=sd + 4))
    ch = candle_len(t, burnt)
    for j, dx in enumerate(CANDLES):
        col = ("#7FC1E6", "#F7A6C0", "#9AD98A", "#FFD36A")[j]
        top = -124 - ch
        o.append(shape([(dx - 6, -124, 1), (dx + 6, -124, 1), (dx + 6, top, 1), (dx - 6, top, 1)], col,
                       "".join(line([(dx - 6, top + ch * (.25 + .3 * q)), (dx + 6, top + ch * (.15 + .3 * q))], 3, "#FFFFFF", taper=0, wmin=1,
                                     seed=sd + 40 + q + 5 * j) for q in range(2)), w=2.6, seed=sd + 50 + j))
        if burnt > .2:      # оплывший воск
            o.append(blob(ellipse_pts(dx, -125, 11 * burnt, 4, 10), col))
            o.append(blob([(dx + 4, -126), (dx + 9, -126), (dx + 8, -112 + 6 * j % 3), (dx + 5, -112)], col))
        o.append(line([(dx, top), (dx + 1, top - 7)], 2.4, INK, taper=0, wmin=1, seed=sd + 60 + j))
        lit = j not in out
        if lit:
            fl = (26 - 8 * burnt) * (1 + .14 * math.sin(t * 21 + j * 1.9))
            sw = 4 * math.sin(t * 15 + j * 2.3)
            fy = top - 6
            o.append(PR.glow(dx, fy - 10, 46, .5, "#ffd36a"))
            o.append(shape([(dx + sw * .4, fy - fl, 1), (dx + 9, fy - fl * .35), (dx + 6, fy + 2), (dx - 6, fy + 2), (dx - 9, fy - fl * .35)], C_FLAME,
                           blob(ellipse_pts(dx, fy - 5, 3.8, 7, 10), "#FFF3B0"), w=2.2, seed=sd + 70 + j))
        elif smoke_t is not None and t > smoke_t:
            o.append(PR.smoke_curls(dx, top - 10, .5, 1 - ramp(t, smoke_t + 1.0, .8), t, seed=j, n=2))
    return tf("".join(o), x, y, k)


def garland(x0, x1, y, t, sag=70.0):
    cols = ("#E9576A", "#FFD23F", "#5BA7E0", "#7CC46A", "#F59A3C")
    o = []
    n = 9
    pts = [(x0 + (x1 - x0) * i / 20, y + sag * math.sin(math.pi * i / 20)) for i in range(21)]
    o.append(line(pts, 3.2, "#7a5a3c", taper=0, wmin=1, seed=1201))
    for i in range(n):
        u = (i + .5) / n
        px, py = x0 + (x1 - x0) * u, y + sag * math.sin(math.pi * u)
        sw = 5 * math.sin(t * 2.4 + i)
        tri = [(-30, 0, 1), (30, 0, 1), (0, 66, 1)]
        o.append(tf(shape(tri, cols[i % 5], "", w=3.0, seed=1210 + i), px, py, 1.0, sw))
    return "".join(o)


def table(x, y, w=560.0):
    o = [shape(lib.rect_pts(x - w / 2, y, x + w / 2, y + 26), "#f4f1ea", blob(lib.rect_pts(x - w / 2, y + 18, x + w / 2, y + 26), "#d9d2c4"), w=4,
               seed=1301)]
    # скатерть свисает
    o.append(shape([(x - w / 2 - 6, y + 20, 1), (x + w / 2 + 6, y + 20, 1), (x + w / 2 + 14, y + 150), (x - w / 2 - 14, y + 150)], "#f7d6de",
                   "".join(blob(lib.rect_pts(x - w / 2 + 40 + 90 * j, y + 20, x - w / 2 + 70 + 90 * j, y + 150), "#f2bfcc", .7) for j in range(6)),
                   w=4, seed=1302))
    for s in (-1, 1):
        o.append(shape(lib.rect_pts(x + s * (w / 2 - 50) - 10, y + 150, x + s * (w / 2 - 50) + 10, FL), "#a8774a", "", w=3.4, seed=1303 + s))
    return "".join(o)


def party_room(t, x0=-900.0, x1=2100.0):
    o = [rect(x0, -1400, x1, FL, PARTY_WALL)]
    for i in range(int(x0 // 140), int(x1 // 140) + 1):
        o.append(rect(i * 140, -1400, i * 140 + 50, FL, PARTY_WALL_SH, .5))
    o.append(rect(x0, FL - 40, x1, FL, "#f4ead8"))
    o.append(line([(x0, FL - 40), (x1, FL - 40)], 3, seed=7))
    o.append(rect(x0, FL, x1, FL + 1400, "#c9a77c"))
    o.append(line([(x0, FL), (x1, FL)], 5, seed=11))
    for i in range(int(x0 // 260), int(x1 // 260) + 1):
        xa = i * 260
        o.append(line([(xa, FL + 20), (xa + (xa - 600) * .9, FL + 900)], 2.4, "#a98a62", seed=20 + i % 9, op=.8))
    o.append(garland(320, 1000, 560, t))
    for j, (bx, by, col) in enumerate(((330, 700, "red"), (980, 690, "blue"), (1060, 760, "yellow"))):
        o.append(PR.balloon(bx, by + 10 * math.sin(t * 1.7 + j), .9, col=col, t=t, seed=j, string=260))
    return "".join(o)


def guest(kind, x, t, expr="calm", sleep=0.0, look_door=1.0, tap=0.0):
    """Гость у стола смотрит на дверь (влево); sleep 0…1 — клюёт носом; tap — стучит ногой (нетерпение)."""
    k = .5
    hip = stand_hip(k) + 6 * sleep
    f = people.townsman82(kind, x, hip, k, "rest", t=t, expr=expr, feet="stand", flip=look_door > .5,
                          head_add=.25 * sleep + .05 * math.sin(t * 2.6) * (1 - sleep), lean_add=.06 * sleep)
    o = f["svg"]
    if sleep > .3:
        hx, hy = f["head"]
        o += PR.zzz(hx + 40, hy - 120, .8, t, sleep)
    return o, f


def party_world(t, door=0.0, dima=None, burnt=0.0, out=(), smoke_t=None, sleep=0.0, guests_turn=0.0, cat_st=None):
    o = [party_room(t)]
    o.append(door_open(DOOR_X, FL, DOOR_K, door, t))
    g1, _ = guest("student", TABLE_X - 80, t, "calm", sleep=sleep)
    g2, _ = guest("mom", TABLE_X + 170, t, "calm", sleep=sleep)
    o.append(g2)
    o.append(g1)
    o.append(table(TABLE_X, TABLE_Y))
    o.append(cake(TABLE_X - 10, TABLE_Y + 4, 1.3, t, burnt, out, smoke_t))
    o.append(cat(TABLE_X + 225, TABLE_Y + 4, .45, t, cat_st or dict(look=(-.8, -.1))))
    if dima:
        o.append(dima)
    return "".join(o)


# ═════════════════════════ s01 хук, s03 опоздал на свой праздник, s16 петля ═════════════════════════
HIT01 = stress(2, .45)                    # «подРЯД»: дверь распахнута, Дима влетает


def dima_burst(t, t_open, k=.5, expr="panic82", x_from=None, x_to=None, dur=.7, hat=True):
    """Дима влетает в дверь бегом: до t_open стоит за дверью (не виден), затем бежит от двери к столу и тормозит."""
    x_from = DOOR_X - 40 if x_from is None else x_from
    x_to = DOOR_X + 80 if x_to is None else x_to
    u = clamp((t - t_open) / dur)
    if t < t_open - .02:
        return ""
    x = x_from + (x_to - x_from) * ease_out(u)
    hip = stand_hip(k)
    if u < .85:
        f = people.dima82_run(x, hip, k, (t - t_open) / .34, t=t, expr=expr, boot=False, socks=("shoe", "shoe"), sandwich=False,
                              lean=.35 - .25 * u)
    else:
        f = people.dima82(x, hip, k, expr, "d82_rest", t=t, feet="stand", lean_add=.12 * (1 - ramp(t, t_open + dur, .3)) + .03 * math.sin(t * 9))
    o = f["svg"]
    hx, hy = f["head"]
    o += PR.sweat(hx - 60, hy - 30, .8, -20)
    o += PR.speed_arcs(x - 170, hip - 120, 1.0, 1 - u, t, seed=3, n=3, ang=180)
    return o


def hook_cam_scene(t):
    u = ease_io(clamp((t + .2) / 1.5))
    s = 1.12 + .08 * u
    return 560 - 40 * u, FL - 540 / s + 30, s


def frame_s01(t):
    """ХУК: праздник, все ждут, дверь распахивается на «подряд», Дима влетает."""
    op = ease_out(ramp(t, -.12, .2))
    body = party_world(t, door=op, dima=dima_burst(t, -.02, dur=.85), guests_turn=1.0,
                       cat_st=dict(look=(-.9, -.1), perk=bump(t, HIT01, .05, .4)))
    cx, cy, s = hook_cam_scene(t)
    dx, dy = shake(t, HIT01, 14)
    v = f'<g transform="{lib.cam(cx + dx, cy + dy, s, 0)}">{body}</g>'
    if NOCAM:
        return lib.svg(f'<rect width="1080" height="1920" fill="{BG}"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT01) + title(t))


def frame_s03(t):
    """«Раньше опаздывал даже на свой день рождения»: свечи догорели, гости спят; Дима влетает на «опаздывал»; на «рождения»
    последняя свеча гаснет дымком."""
    a, b = T0("s03"), T1("s03")
    t_open = W(7) - .1
    op = ease_out(ramp(t, t_open - .08, .14))
    t_out = stress(12, .4)
    outs = (0, 2) if t < t_out else (0, 1, 2, 3)
    wake = bump(t, t_open + .1, .1, .8)
    body = party_world(t, door=op, dima=dima_burst(t, t_open, dur=.8), burnt=1.0, out=outs, smoke_t=t_out, sleep=1 - .6 * wake,
                       cat_st=dict(look=(-.9, -.1), smug=.6, squint=.4))
    u = ease_io(ramp(t, a, b - a))
    push = ease_io(ramp(t, t_out - .3, .5))
    dx, dy = shake(t, t_open + .05, 9)
    cx = 520 + 120 * push
    cy = 1100 - 20 * u + 30 * push
    return view(body, cx + dx, cy + dy, .95 + .1 * u + .55 * push, 1 - 2 * u, over=title(t))


def frame_s16(t):
    """Петля: тот же праздник, что в первом кадре: все ждут, дверь закрыта и вот-вот откроется."""
    a = T0("s16")
    body = party_world(t, door=.6 * lib.ease_in(ramp(t, T1("s16") - .4, .4)), cat_st=dict(look=(-.9, -.1)))
    u = ease_io(ramp(t, a, T1("s16") - a))
    c0 = hook_cam_scene(0.0)
    import anim
    hc = anim.hook_cam(0.0, hit=HIT01)
    z0 = hc["zoom"]
    s = c0[2] * (1 + (z0 - 1) * u)
    return view(body, c0[0], c0[1], s, hc["rot"] * u)




# ═════════════════════════ s02: календарь, 30 галочек ═════════════════════════
def calendar30(x, y, t, t0, t1, glow_u=0.0):
    """Настенный календарь 6×5 = 30 клеток; галочки появляются по одной от t0 до t1."""
    w, h = 620.0, 640.0
    o = []
    if glow_u > .01:
        o.append(PR.glow(x, y, 520, .55 * glow_u, "#d8f5c0"))
    o.append(shape(lib.rrect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 18), "#fffdf6",
                   blob(lib.rect_pts(x - w / 2, y - h / 2, x + w / 2, y - h / 2 + 110), "#E9576A"), w=5, seed=2001))
    for j in range(5):       # кольца
        rx = x - w / 2 + 90 + j * (w - 180) / 4
        o.append(line([(rx, y - h / 2 - 34), (rx, y - h / 2 + 24)], 12, "#8a8f99", taper=0, wmin=1, seed=2002 + j))
    cw, ch = (w - 60) / 6, (h - 160) / 5
    n = 0
    for r in range(5):
        for c in range(6):
            cx = x - w / 2 + 30 + cw * (c + .5)
            cy = y - h / 2 + 130 + ch * (r + .5)
            o.append(shape(lib.rrect(cx - cw / 2 + 6, cy - ch / 2 + 6, cx + cw / 2 - 6, cy + ch / 2 - 6, 8), "#f3eee2", "", w=2.6, seed=2010 + n))
            ta = t0 + (t1 - t0) * n / 29
            if t >= ta:
                u = clamp((t - ta) / .12)
                o.append(PR.check_mark(cx - 4, cy + 4, .62 * (1 + .25 * bump(t, ta, .04, .12)), u, col="#2f9a4a", seed=n))
            n += 1
    return "".join(o)


def frame_s02(t):
    """«я прихожу вовремя»: 30 клеток календаря получают галочки одна за другой; Дима гордо кивает, кот трётся рядом."""
    a, b = T0("s02"), T1("s02")
    t_ok = W(5)
    o = [rect(-1000, -1400, 2200, FL, "#f1e4c9")]
    for i in range(-8, 18):
        o.append(rect(i * 120, -1400, i * 120 + 44, FL, "#e6d6b6", .55))
    o.append(rect(-1000, FL - 40, 2200, FL, "#f4ead8"))
    o.append(rect(-1000, FL, 2200, FL + 1400, "#c9a77c"))
    o.append(line([(-1000, FL), (2200, FL)], 5, seed=11))
    o.append(calendar30(420, 930, t, a - .05, t_ok + .05, glow_u=ease_out(ramp(t, t_ok, .3))))
    k = .5
    nod = bump(t, t_ok + .05, .1, .3)
    f = people.dima82(850, stand_hip(k), k, "proud82", "d82_one", t=t, feet="stand", flip=True, head_add=.1 * nod)
    o.append(f["svg"])
    o.append(cat(640, FL, .7, t, dict(look=(.6, -.4), smile=1.0, tail=14 * math.sin(t * 4))))
    o.append(PR.sparkles(420, 930, 2.4, bump(t, t_ok + .05, .05, .5), t, seed=21, n=6, r=360))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_ok, 8)
    return view("".join(o), 560 + dx, 1010 + dy - 20 * u, 1.05 + .1 * u, -1 + 2 * u, over=title(t))


# ═════════════════════════ прихожая: s04, s10, s11 ═════════════════════════
FL82 = RM.FL82
HDX, HK = 560.0, .85
HHIP = FL82 - 598 * HK


def hall_clock(t, spin=0.0, x=900.0, y=180.0, r=88.0):
    return PR.clock(x, y, r, angle_h=250 + t * 30 * spin, angle_m=120 + t * 360 * spin, seed=4)


def frame_s04(t):
    """«Выйти вовремя для меня значило выйти»: прихожая утром, Дима со щёткой во рту и в одном носке; на «Выйти» глядит на
    часы над дверью, стрелки летят; на втором «выйти» распахивает дверь и рвётся к ней."""
    a, b = T0("s04"), T1("s04")
    h = RM.hall82(t, "morning")
    t_go = W(18)
    ajar = ease_out(ramp(t, t_go - .05, .25))
    look = ramp(t, W(13) - .1, .2)
    o = [h["bg"], h["door"](ajar), hall_clock(t, 3.0 * look)]
    if look > .01:
        o.append(PR.speed_arcs(1000, 180, .8, look, t, seed=4, n=3, ang=0))
    if t < t_go:
        f = people.dima82(HDX, HHIP, HK, "panic82" if look > .5 else "squint82", "d82_look_up" if look > .5 else "d82_rest", t=t,
                          feet="stand", brush=True, socks=("sock", "bare"), head_add=-.05 * look)
    else:
        u = t - t_go
        x = HDX + 380 * ease_out(clamp(u / .7))
        f = people.dima82_run(x, HHIP, HK, u / .34, t=t, expr="rush82", boot=True, socks=("sock", "bare"), sandwich=False, lean=.3)
        o.append(PR.speed_arcs(x - 300, HHIP - 200, 1.4, 1.0, t, seed=5, n=3, ang=180))
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.sweat(hx - 70, hy - 40, 1.2, -20) if look > .5 else "")
    u = ease_io(ramp(t, a, b - a))
    up = look * (1 - ramp(t, t_go - .3, .3))
    dx, dy = shake(t, t_go, 12)
    cx = 700 + 120 * ease_io(ramp(t, t_go, .5))
    cy = 1100 - 260 * up
    return view("".join(o), cx + dx, cy + dy, .82 + .12 * u + .1 * up, 0)


def stopwatch_held(x, y, k, t, prog, click=0.0, badge=0.0, label="40 МИН"):
    """Секундомер (prog 0…1 — оборот сектора) + плашка с итогом над ним (badge 0…1 — выскакивает)."""
    o = [PR.stopwatch(x, y, k, hand_a=360 * prog, sector_a=360 * prog, click=click, t=t)]
    if badge > .01:
        s = lib.back_out(clamp(badge), 2.4) if badge < 1 else 1.0
        bd = (f'<rect x="-190" y="-70" width="380" height="120" rx="26" fill="#FFD23F" stroke="#111" stroke-width="7"/>'
              + text(label, 0, 22, 78, fill="#111", stroke="#111", sw=.01))
        o.append(tf(bd, x, y - 330 * k, s * k * 1.6, -3))
        o.append(PR.sparkles(x, y - 330 * k, 1.6 * k, bump(t, 0, 1, 1) * 0 + badge * (1 - clamp(badge - 1)), t, seed=31, n=5, r=200 * k))
    return "".join(o)


def cat_on_stool(t, st=None, jump=1.0):
    """Кот на табурете прихожей (HALL82 stool — центр сиденья); jump 0…1 — запрыгивает с пола."""
    sx, sy = RM.HALL82["stool"]
    x0, y0 = sx - 260, FL82
    x = x0 + (sx - x0) * jump
    y = y0 + (sy - y0) * jump - 260 * math.sin(math.pi * jump)
    st = dict(dict(look=(.5, -.4), legs=1.0 - jump if jump < 1 else 0.0), **(st or {}))
    return cat(x, y, .8, t, st), (x, y)


def frame_s10(t):
    """«Вот что я поменял»: прихожая вечером, Дима поднимает палец, над ним загорается лампочка-идея; кот запрыгивает на
    табурет и тянет лапу к секундомеру."""
    a, b = T0("s10"), T1("s10")
    h = RM.hall82(t, "evening")
    o = [h["bg"], h["door"](0.0), hall_clock(t, .02)]
    t_idea = W(44) + .1
    f = people.dima82(HDX + 140, HHIP, HK, "wow82" if t > t_idea else "puzzled82", "d82_one", t=t, feet="stand", flip=True,
                      head_add=.08 * bump(t, t_idea, .08, .3))
    o.append(f["svg"])
    hx, hy = f["head"]
    bu = pop(t, t_idea, .25)
    if t > t_idea:
        o.append(PR.glow(hx, hy - 330, 260, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx, hy - 330 + 8 * math.sin(t * 5), 1.2 * bu, on=1.0, t=t))
        o.append(PR.sparkles(hx, hy - 330, 2.0, bump(t, t_idea, .05, .5), t, seed=41, n=5, r=220))
    jump = ease_io(ramp(t, W(46) - .1, .4))
    c, (cx_, cy_) = cat_on_stool(t, dict(look=(.8, -.6), perk=1.0, paw=ease_out(ramp(t, W(47), .3))), jump)
    o.append(PR.stool(*RM.HALL82["stool"], 1.0, seed=3))
    o.append(c)
    if jump > .95:
        o.append(stopwatch_held(cx_ + 200, cy_ - 260, .45 * pop(t, W(47), .25), t, 0.0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_idea, 10)
    return view("".join(o), 560 + dx, 1080 + dy, .9 + .14 * u, 1 - 2 * u, over=changed_label(t))


T11_POSES = ("brush", "sock", "keys", "jacket")


def frame_s11(t):
    """«Один раз засёк, сколько на самом деле идут сборы»: кот на табурете жмёт секундомер на «засёк»; Дима ускоренно
    собирается — щётка, носок, ключи, куртка (смена поз со смазом), сектор бежит; на «сборы» стоп и плашка «40 МИН»."""
    a, b = T0("s11"), T1("s11")
    h = RM.hall82(t, "morning")
    t_go, t_stop = W(50), W(56) + .05
    run = ramp(t, t_go, t_stop - t_go)
    o = [h["bg"], h["door"](0.0), hall_clock(t, 2.5 if t_go < t < t_stop else .02)]
    st_ph = min(3, int(run * 4)) if t_go < t < t_stop else (0 if t <= t_go else 3)
    kind = T11_POSES[st_ph]
    xs = (480, 700, 600, 760)
    x = xs[st_ph] + (25 * math.sin(t * 30) if t_go < t < t_stop else 0)
    if kind == "brush":
        f = people.dima82(x, HHIP, HK, "squint82", "d82_rest", t=t, feet="stand", brush=True, socks=("bare", "bare"))
    elif kind == "sock":
        f = people.dima82(x, HHIP, HK, "rush82", "d82_shoe", t=t, feet="stand", socks=("sock", "bare"))
    elif kind == "keys":
        f = people.dima82(x, HHIP, HK, "rush82", "d82_pocket", t=t, feet="stand", socks=("sock", "sock"))
    else:
        f = people.dima82(x, HHIP, HK, "proud82" if t > t_stop else "rush82", "d82_rest", t=t, feet="stand", flip=True)
    if t_go < t < t_stop:      # смаз ускоренной съёмки: два бледных следа позади
        for j, dxo in enumerate((-70, -140)):
            o.append(f'<g opacity="{.22 - .08 * j:.2f}" transform="translate({dxo} 0)">{f["svg"]}</g>')
        o.append(PR.speed_arcs(x - 220, HHIP - 160, 1.3, 1.0, t, seed=6 + st_ph, n=3, ang=180))
    o.append(f["svg"])
    o.append(PR.stool(*RM.HALL82["stool"], 1.0, seed=3))
    c, (cx_, cy_) = cat_on_stool(t, dict(look=(.9, -.7), perk=1.0, paw=1.0, squint=.3 * run))
    o.append(c)
    prog = run * .92
    click = max(bump(t, t_go - .03, .04, .15), bump(t, t_stop - .03, .04, .15))
    badge = ramp(t, t_stop + .05, .3)
    o.append(stopwatch_held(cx_ + 200, cy_ - 260, .45, t, prog, click, badge))
    if t_go < t < t_stop:
        o.append(PR.tap_rings(cx_ + 200, cy_ - 360, ramp(t, t_go, .4), 1.0, col="#FFD23F"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_stop, 10)
    zoom = ease_io(ramp(t, t_stop, .4))
    return view("".join(o), 560 - 120 * zoom + dx, 1080 - 120 * zoom + dy, .9 + .08 * u + .35 * zoom, 0, over=changed_label(t))


# ═════════════════════════ s05: улица, бежит, когда уже пора быть там ═════════════════════════
GROUND = 1560.0


def street_bg(t, x0=-800.0, x1=3600.0):
    o = []
    g = lib.lin_grad([(0, "#8fd0f4", 1), (1, "#d9f1fb", 1)], 0, 0, 0, 1)
    o.append(f'<rect x="{x0}" y="-1400" width="{x1 - x0}" height="{GROUND + 1400}" fill="url(#{g})"/>')
    cols = ("#e9a77c", "#f0d08a", "#b8c9e6", "#e7b4c0", "#c8dca0")
    for i, xa in enumerate(range(int(x0), int(x1), 420)):
        hgt = 900 + 160 * ((i * 7) % 3)
        c = cols[i % 5]
        win = "".join(blob(lib.rect_pts(xa + 60 + 110 * cc, GROUND - hgt + 80 + 170 * r, xa + 130 + 110 * cc, GROUND - hgt + 190 + 170 * r),
                           "#8fb7d6") for r in range(int(hgt // 170) - 1) for cc in range(3))
        o.append(shape(lib.rect_pts(xa, GROUND - hgt, xa + 400, GROUND - 20), c, win, w=4.2, seed=3000 + i))
    o.append(rect(x0, GROUND - 20, x1, GROUND + 1400, "#c7c2b8"))
    o.append(line([(x0, GROUND - 20), (x1, GROUND - 20)], 5, seed=3100))
    for i, xa in enumerate(range(int(x0), int(x1), 240)):
        o.append(line([(xa, GROUND + 10), (xa - 160, GROUND + 700)], 2.5, "#a39e94", seed=3110 + i % 7))
    return "".join(o)


def frame_s05(t):
    """«когда уже пора быть там»: улица, Дима несётся вправо с кедом в руке, камера едет за ним; впереди уличные часы — на
    «пора» стрелка прыгает на срок, часы трясутся."""
    a, b = T0("s05"), T1("s05")
    k = .75
    x = 300 + 640 * (t - a)
    hip = GROUND - 598 * k
    o = [street_bg(t)]
    clk_x = 1500.0
    jump = ease_out(ramp(t, W(21), .15))
    o.append(PR.street_clock(clk_x, GROUND - 20, 1.0, hand_a=300 + 60 * jump, jump_u=bump(t, W(21), .05, .4), t=t, seed=1))
    o.append(PR.sparkles(clk_x, GROUND - 900, 2.0, bump(t, W(21), .05, .5), t, seed=51, n=5, r=200))
    f = people.dima82_run(x, hip, k, (t - a) / .32, t=t, expr="rush82" if t < W(21) else "panic82", boot=True, socks=("sock", "bare"),
                          sandwich=True, lean=.35)
    o.append(PR.speed_arcs(x - 260, hip - 150, 1.4, 1.0, t, seed=52, n=3, ang=180))
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.sweat(hx - 70, hy - 40, 1.1, -20))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(21), 10)
    cx = x + 220 + 120 * ease_io(ramp(t, W(21) - .2, .5))
    sc = 1.0 + .06 * u
    return view("".join(o), cx + dx, GROUND - 480 / sc + dy, sc, -1.5 + 3 * u)


# ═════════════════════════ s06–s07: душ на 5 минут шёл 25 ═════════════════════════
BATH = "#d9eef2"


def bath_timer(x, y, k, t, num="5", hot=0.0, jolt=0.0):
    """Кухонный таймер на кафеле: круглый, с окошком; число минут крупно; hot — краснеет."""
    face = lib.mix("#ffffff", "#ffd6cf", hot)
    o = [shape(ellipse_pts(0, 0, 170, 170, 34), lib.mix("#4FB0C6", "#E9576A", hot), "", w=6, seed=4001)]
    o.append(shape(ellipse_pts(0, 0, 135, 135, 30), face, "", w=4, seed=4002))
    for j in range(12):
        a = math.radians(j * 30)
        o.append(line([(118 * math.sin(a), -118 * math.cos(a)), (132 * math.sin(a), -132 * math.cos(a))], 5, INK, taper=0, wmin=1, seed=4010 + j))
    o.append(text(num, 0, 38 if len(num) == 1 else 34, 120 if len(num) == 1 else 104, fill=lib.mix("#1d2448", "#c0392b", hot), stroke="#ffffff",
                  sw=8))
    o.append(text("МИН", 0, 98, 38, fill="#1d2448", stroke="#ffffff", sw=5))
    o.append(shape(lib.rrect(-26, -205, 26, -165, 8), "#3c3f46", "", w=3, seed=4003))
    return tf("".join(o), x, y, k * (1 + .18 * jolt), 8 * jolt * math.sin(t * 50))


def steam_puffs(t, u, box=(0, 300, 1080, 1500), n=10, seed=0):
    if u <= .01:
        return ""
    x0, y0, x1, y1 = box
    o = []
    for j in range(n):
        ph = (t * .25 + j / n + seed * .1) % 1.0
        px = x0 + (x1 - x0) * ((j * .37 + .1) % 1.0) + 40 * math.sin(t * .9 + j)
        py = y1 - (y1 - y0) * ph
        r = (90 + 60 * ((j * 3) % 4)) * (.6 + .6 * ph)
        o.append(blob(ellipse_pts(px, py, r, r * .7, 16), "#ffffff", .35 * u * math.sin(math.pi * ph)))
    return "".join(o)


def shower_world(t, num="5", hot=0.0, jolt=0.0, expr="calm82", steam=.4, foam=1.0):
    o = [rect(-900, -1400, 2200, 2400, BATH)]
    o.append(RM._tiles(-900, -1400, 2200, 1700, 120, "#c4e1e7", seed=1))
    # штанга и шторка
    k = 1.0
    hip = 1900 - 598 * k
    f = people.dima82(420, hip, k, expr, "d82_rest", t=t, feet="stand", head_add=.05 * math.sin(t * 3))
    o.append(f["svg"])
    hx, hy = f["head"]
    if foam > .01:       # пена на голове
        for j, (dx, dy, r) in enumerate(((-60, -110, 46), (-10, -140, 56), (50, -118, 48), (90, -80, 34), (-100, -70, 30))):
            o.append(shape(ellipse_pts(hx + dx + 4 * math.sin(t * 6 + j), hy + dy, r, r * .85, 14), "#ffffff", "", w=2.6, seed=4110 + j))
    # шторка: от плеч вниз
    top = hy + 120
    pts = [(-400, top)] + [(-400 + 170 * i, top + 14 * math.sin(i * 1.3 + t * 3)) for i in range(13)] + [(1800, 2600), (-400, 2600)]
    stripes = "".join(blob(lib.rect_pts(-400 + 170 * i, top, -330 + 170 * i, 2600), "#f0c25a", .9) for i in range(13))
    dots = "".join(shape(ellipse_pts(-330 + 170 * (i % 13) + 85 * ((i // 13) % 2), top + 200 + 230 * (i // 13), 34, 34, 14), "#ffffff", "", w=3,
                         seed=4160 + i) for i in range(52))
    o.append(shape(pts, "#ffe08a", stripes + dots, w=4.6, seed=4120))
    bar = hy - 330
    o.append(line([(-400, bar), (1800, bar)], 14, "#9aa3ad", taper=0, wmin=1, seed=4101))
    for i in range(13):
        o.append(shape(ellipse_pts(-360 + 170 * i, bar, 14, 18, 10), "#c9ced6", "", w=2.4, seed=4130 + i))
        o.append(line([(-360 + 170 * i, bar + 16), (-360 + 170 * i, top + 6)], 3, "#9aa3ad", taper=0, wmin=1, seed=4140 + i))
    # капли душа
    for j in range(14):
        ph = (t * 2.2 + j * .137) % 1.0
        o.append(PR.drop(hx - 220 + 30 * j, hy - 420 + 600 * ph, .5, 0))
    o.append(shape(lib.rrect(hx - 160, hy - 560, hx + 160, hy - 520, 30), "#b9c2cc", "", w=4, seed=4150))     # лейка
    o.append(bath_timer(hx + 430, hy - 230, 1.0, t, num, hot, jolt))
    o.append(steam_puffs(t, steam, (-200, 200, 1300, 1500)))
    return "".join(o), f


def frame_s06(t):
    """«Душ на пять минут»: ванная, Дима в пене за шторкой, на кафеле таймер «5 МИН»; на «пять» таймер подпрыгивает."""
    a, b = T0("s06"), T1("s06")
    body, f = shower_world(t, "5", jolt=bump(t, W(26), .05, .3), expr="calm82", steam=.3)
    hx, hy = f["head"]
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(26), 7)
    return view(body, hx + 230 + dx, hy - 140 + dy, 1.15 + .12 * u, 0, bg=BATH)


def frame_s07(t):
    """«почему-то шёл двадцать пять»: крупно таймер и Дима; пар густеет, на «двадцать» число прыгает 5 → 25 и краснеет,
    Дима в панике."""
    a, b = T0("s07"), T1("s07")
    tj = W(30)
    num = "5" if t < tj else "25"
    hot = ease_out(ramp(t, tj, .3))
    jolt = bump(t, tj, .05, .35) + .4 * bump(t, W(31), .05, .3)
    body, f = shower_world(t, num, hot, jolt, "panic82" if t > tj else "puzzled82", steam=.5 + .5 * ramp(t, a, b - a))
    o = [body]
    hx, hy = f["head"]
    o.append(PR.sparkles(hx + 430, hy - 230, 2.0, bump(t, tj, .05, .5), t, seed=71, n=6, r=230))
    o.append(PR.sweat(hx - 80, hy - 20, 1.3, -20) if t > tj else "")
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tj, 14)
    z = 1.6 + .1 * u + .15 * bump(t, tj, .05, .4)
    return view("".join(o), hx + 230 + dx, hy - 170 + dy, z, 2 - 3 * u, bg=BATH)


# ═════════════════════════ s08–s09: телефон, «буду через 5 минут» ═════════════════════════
MSG = "буду через 5 минут"


def msg_bubble(x, y, s=1.0, ticks=True, op=1.0, tm="8:55"):
    """Исходящий пузырь чата (правый край в x): зелёный, текст, время и галочки."""
    w, hgt = 560.0, 118.0
    body = (f'<rect x="{-w}" y="{-hgt / 2}" width="{w}" height="{hgt}" rx="34" fill="#DCF8C6" stroke="#2a2a30" stroke-width="4"/>'
            f'<text x="{-w + 34}" y="14" font-family="IDB" font-size="44" fill="#1d2448" style="font-kerning:none">{MSG}</text>'
            f'<text x="-80" y="44" font-family="IDB" font-size="24" fill="#6a7a6a" style="font-kerning:none">{tm}</text>')
    if ticks:
        body += line([(-34, 34), (-26, 42), (-12, 24)], 4, "#4FB0E6", taper=0, wmin=1, seed=5001)
    return f'<g opacity="{op:.3f}" transform="translate({x:.1f} {y:.1f}) scale({s:.4f})">{body}</g>'


def phone_chat(t, bubbles, typing=0.0, shake_u=0.0, typed=0.0):
    """Телефон в руке, экран — чат; bubbles — список (y_off, s, op, время) снизу вверх; typed 0…1 — текст в поле ввода."""
    cx, cy = 540.0, 980.0
    o = [rect(-900, -1400, 2200, 2600, "#3b3552")]
    o.append(PR.glow(cx, cy, 900, .35, "#8fb7ff"))
    o.append(PR.phone_frame(cx, cy, 1.0, 1.0, glow_=.4, seed=1))
    x0, y0, x1, y1 = PR.phone_frame_rect(cx, cy, 1.0)
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    scr = [rect(x0, y0, x1, y1, "#ECE5DD")]
    tops = [y1 - 190 - yo - 59 * s for (yo, s, op, tm) in bubbles]
    lift = max(0.0, (y0 + 406) - min(tops)) if tops else 0.0       # входящие уезжают вверх, а не прячутся под исходящими
    for j, (txt, yy) in enumerate((("ты где?", 220), ("мы уже все тут", 340))):
        w_ = 40 + 25 * len(txt)
        yy -= lift
        scr.append(f'<rect x="{x0 + 24}" y="{y0 + yy - 50}" width="{w_}" height="96" rx="30" fill="#ffffff" stroke="#2a2a30" stroke-width="4"/>'
                   f'<text x="{x0 + 52}" y="{y0 + yy + 12}" font-family="IDB" font-size="42" fill="#1d2448">{txt}</text>')
    for (yo, s, op, tm) in bubbles:
        scr.append(msg_bubble(x1 - 24, y1 - 190 - yo, s, op=op, tm=tm))
    scr.append(rect(x0, y0, x1, y0 + 120, "#2f7d6a"))
    scr.append(shape(ellipse_pts(x0 + 70, y0 + 60, 34, 34, 16), "#f2c5a0", "", w=3, seed=5010))
    scr.append(f'<text x="{x0 + 124}" y="{y0 + 74}" font-family="IDB" font-size="40" fill="#ffffff">Друзья</text>')
    scr.append(rect(x0, y1 - 110, x1, y1, "#f7f7f7"))
    scr.append(f'<rect x="{x0 + 20}" y="{y1 - 92}" width="{x1 - x0 - 130}" height="74" rx="37" fill="#ffffff" stroke="#c9c9c9" stroke-width="3"/>')
    if typed > .01:
        n = int(len(MSG) * clamp(typed))
        scr.append(f'<text x="{x0 + 46}" y="{y1 - 42}" font-family="IDB" font-size="38" fill="#1d2448">{MSG[:n]}</text>')
    scr.append(shape(ellipse_pts(x1 - 58, y1 - 55, 38, 38, 16), "#2f7d6a", "", w=3, seed=5011))
    o.append(f'<g clip-path="url(#{c})">{"".join(scr)}</g>')
    # ладонь снизу и большой палец (печатает — палец прыгает по клавишам)
    o.append(shape([(x0 - 70, y1 - 160), (x0 + 40, y1 + 40), (x1 + 20, y1 + 120), (x1 + 160, y1 + 700), (x0 - 140, y1 + 700)], "#ecc4a2",
                   blob([(x0 - 70, y1 + 200), (x1 + 100, y1 + 300), (x1 + 160, y1 + 700), (x0 - 140, y1 + 700)], "#d9a984", .7), w=5, seed=5020))
    tx = x0 + 160 + 200 * (.5 + .5 * math.sin(t * 9)) * typing
    ty = y1 - 70 - 40 * abs(math.sin(t * 22)) * typing
    o.append(shape(lib.band([(x1 + 110, y1 + 420), (tx + 30, ty + 40)], 120, 92), "#ecc4a2", "", w=5, seed=5021))
    o.append(shape(ellipse_pts(tx + 22, ty + 18, 30, 38, 14), "#f7ddd0", "", w=3, seed=5022))
    sx = 14 * shake_u * math.sin(t * 60)
    return f'<g transform="translate({sx:.2f} 0)">{"".join(o)}</g>'


def frame_s08(t):
    """«И каждый раз одно и то же сообщение»: палец набирает «буду через 5 минут»; на «сообщение» пузырь улетает в чат."""
    a, b = T0("s08"), T1("s08")
    send = W(39)
    typed = ramp(t, a, send - a - .1)
    if t < send:
        bubbles = [(0, 1.0, 1.0, "8:55")] if False else []
    else:
        u = ease_out(ramp(t, send, .2))
        bubbles = [(-60 * (1 - u), .6 + .4 * lib.back_out(u, 2), 1.0, "8:55")]
    body = phone_chat(t, bubbles, typing=1.0 if t < send else 0.0, typed=typed if t < send else 0.0)
    o = [body, PR.tap_rings(780, 1490, ramp(t, send - .05, .3), 1.4, col="#FFD23F") if t > send - .05 else ""]
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, send, 8)
    return view("".join(o), 560 + dx, 1060 + dy - 60 * u, 1.05 + .1 * u, -2 + 3 * u, bg="#3b3552")


def frame_s09(t):
    """«буду через пять минут»: тот же пузырь приходит снова и снова (новое время), лента ползёт вверх, телефон дрожит."""
    a, b = T0("s09"), T1("s09")
    times = [a - .3, W(40), W(41), W(42), W(43), stress(43, .6)]
    labels = ["8:55", "9:20", "9:41", "10:05", "10:32", "11:03"]
    bubbles = []
    n = sum(1 for q in times if t >= q)
    for i in range(n):
        u = ease_out(ramp(t, times[i], .18)) if i else 1.0
        age = n - 1 - i
        yo = age * 140 + (140 * (1 - ease_out(ramp(t, times[n - 1], .18))) * -1 if age else -60 * (1 - u))
        bubbles.append((yo, .6 + .4 * lib.back_out(u, 2) if u < 1 else 1.0, 1.0, labels[i]))
    sh = max([bump(t, q, .03, .12) for q in times[1:]] + [0])
    body = phone_chat(t, bubbles, typing=0.0, shake_u=sh)
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(43), 10)
    return view(body, 560 + dx, 900 + dy, 1.2 + .15 * u, 2 - 4 * u, bg="#3b3552")


# ═════════════════════════ s12–s13: схема «назад от двери» ═════════════════════════
PAPER = "#f6efdf"
LINE_Y = 1250.0


def scheme_bg():
    return rect(-2000, -2000, 3500, 4000, PAPER) + "".join(
        line([(-1200, 200 + 90 * j), (2600, 200 + 90 * j)], 2, "#e3d6bb", taper=0, wmin=1, seed=6000 + j) for j in range(24))


def timeline(x0, x1, y, labels):
    o = [line([(x0, y), (x1, y)], 12, INK, taper=0, wmin=1, seed=6100)]
    for j, (x, lab) in enumerate(labels):
        o.append(line([(x, y - 30), (x, y + 30)], 8, INK, taper=0, wmin=1, seed=6110 + j))
        o.append(text(lab, x, y - 56, 60, fill="#1d2448", stroke=PAPER, sw=6))
    return "".join(o)


def red_arrow(x0, x1, y, u, w=48.0, col="#e2574c"):
    if u <= .01:
        return ""
    xe = x0 + (x1 - x0) * u
    d = 1 if x1 >= x0 else -1
    h = w
    pts = [(x0, y - h / 2, 1), (xe - d * 80, y - h / 2, 1), (xe - d * 80, y - h * 1.3, 1), (xe, y, 1), (xe - d * 80, y + h * 1.3, 1),
           (xe - d * 80, y + h / 2, 1), (x0, y + h / 2, 1)]
    return shape(pts, col, "", w=5, seed=6200 + int(x0) % 50)


TICKS = [(-380, "7:40"), (-80, "7:50"), (220, "8:00"), (520, "8:10")]
DOOR_S = (840.0, LINE_Y)
ALARM = (-560.0, 820.0)


def alarm_clock(x, y, k, t, ring=0.0, sad=0.0):
    o = []
    for s_ in (-1, 1):
        o.append(shape(ellipse_pts(s_ * 90, -150, 56, 44, 16), "#c9ced6", "", w=4, seed=6300 + s_))
        o.append(line([(s_ * 80, 130), (s_ * 110, 190)], 12, INK, taper=0, wmin=1, seed=6302 + s_))
    o.append(PR.clock(0, 0, 160, angle_h=200, angle_m=0, seed=7, rim="#E9576A"))
    if sad > .01:
        o.append(line([(-40, 80), (0, 64), (40, 80)], 7, INK, taper=.2, wmin=.6, seed=6310))
    wob = 9 * ring * math.sin(t * 55)
    o2 = tf("".join(o), x, y, k, wob)
    if ring > .05:
        o2 += PR.speed_arcs(x + 220 * k, y - 120 * k, 1.0 * k, ring, t, seed=63, n=3, ang=0)
        o2 += PR.speed_arcs(x - 220 * k, y - 120 * k, 1.0 * k, ring, t, seed=64, n=3, ang=180)
    return o2


def scheme_world(t, back_u=0.0, fwd_u=0.0, cross_u=0.0, ring=0.0, cat_st=None, sad=0.0):
    o = [scheme_bg()]
    o.append(timeline(-560, 980, LINE_Y, TICKS))
    o.append(door_open(DOOR_S[0], LINE_Y, .62, .0, t))
    o.append(text("ВЫХОД 8:20", DOOR_S[0] - 60, LINE_Y - 640, 52, fill="#e2574c", stroke=PAPER, sw=6))
    o.append(red_arrow(DOOR_S[0] - 160, -380, 500, back_u))
    if back_u > .9:
        s_ = pop(t, 0, 1) if False else 1.0
        o.append(text("40 МИН НАЗАД", 20, 640, 60, fill="#e2574c", stroke=PAPER, sw=8))
    c_st = dict(dict(look=(.6, -.5), paw=1.0, smile=.6), **(cat_st or {}))
    o.append(cat(430, LINE_Y - 10, 1.05, t, c_st))
    o.append(stopwatch_held(640, 820, .55, t, .92))
    o.append(alarm_clock(ALARM[0], ALARM[1], 1.0, t, ring, sad))
    o.append(red_arrow(-440, 220, 340, fwd_u, col="#7c8794"))
    if cross_u > .01:
        o.append(PR.cross_stroke((-480, 230), (260, 450), (-480, 450), (260, 230), cross_u, w=40, seed=1))
    return "".join(o)


def frame_s12(t):
    """«и считаю время назад от двери»: шкала времени, справа дверь «8:20 ВЫХОД», кот держит секундомер; на «назад»
    красная стрелка растёт от двери влево на 40 минут."""
    a, b = T0("s12"), T1("s12")
    back = ease_out(ramp(t, W(60) - .05, WE(62) - W(60)))
    o = scheme_world(t, back_u=back, cat_st=dict(perk=bump(t, W(62), .05, .4)))
    o += PR.sparkles(-380, 560, 1.8, bump(t, WE(62), .05, .5), t, seed=81, n=5, r=180)
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(62), 8)
    return view(o, 470 - 100 * u + dx, 880 + dy, .92 - .04 * u, 0, over=changed_label(t), bg=PAPER)


def frame_s13(t):
    """«а не вперёд от будильника»: камера уходит влево к будильнику; серая стрелка вперёд от него растёт и на «вперёд»
    перечёркивается красным крестом, будильник обиженно трясётся."""
    a, b = T0("s13"), T1("s13")
    fwd = ease_out(ramp(t, a, W(65) - a + .1))
    cross = ease_out(ramp(t, W(65) + .15, .3))
    ring = bump(t, W(67), .06, .5) + .5 * bump(t, W(65) + .2, .05, .3)
    o = scheme_world(t, back_u=1.0, fwd_u=fwd, cross_u=cross, ring=min(1.0, ring), sad=ramp(t, W(67), .2))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(65) + .2, 10)
    return view(o, -200 + 40 * u + dx, 860 + dy, .92 + .06 * u, 0, over=changed_label(t), bg=PAPER)


# ═════════════════════════ s14–s15: призыв «КОТ» ═════════════════════════
def kot_print(t, t0, x, y, size):
    """Кодовое слово печатными: жирный IDB, жёлтый с чёрной обводкой и тенью (как «КОТ» в рилсе 101); буквы выскакивают по одной
    с t0 (по 0.09 с), y — базовая линия, x — центр слова."""
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



def frame_s14(t):
    """«Напиши «КОТ»»: на бумаге крупно пишется КОТ, кот рядом показывает на слово лапой."""
    a, b = T0("s14"), T1("s14")
    o = [scheme_bg()]
    o.append(PR.glow(540, 820, 420, .5 * ramp(t, W(69), .3), "#ffe9a8"))
    o.append(kot_print(t, W(68) - .02, 540, 820, 300))
    o.append(PR.sparkles(540, 800, 2.4, bump(t, W(68) + .75, .05, .5), t, seed=91, n=6, r=380))
    o.append(cat(760, 1560, 1.25, t, dict(look=(-.6, -.6), paw=ease_out(ramp(t, W(69) - .2, .3)), smile=1.0, tail=10 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(69), 8)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .08 * u, 0, bg=PAPER)


def frame_s15(t):
    """«если через пять минут тоже твоя фраза»: прилетает пузырь «буду через 5 минут», кот тянется и лопает его лапой;
    КОТ крупно сверху."""
    a, b = T0("s15"), T1("s15")
    o = [scheme_bg()]
    o.append(PR.glow(540, 820, 420, .5, "#ffe9a8"))
    mv = ease_io(ramp(t, T0("s15"), .4))
    o.append(kot_print(t, -9.0, 540, 820 - 240 * mv, 300 - 70 * mv))
    t_in, t_pop = W(71) - .1, W(74) + .05
    fly = ease_out(ramp(t, t_in, .35))
    if t < t_pop:
        bx = 1500 - 520 * fly + 10 * math.sin(t * 4)
        by = 900 - 30 * math.sin(t * 3)
        o.append(msg_bubble(bx, by, 1.6 + .08 * math.sin(t * 5), tm="8:55"))
    else:
        pu = ramp(t, t_pop, .35)
        o.append(PR.sparkles(530, 900, 2.6, 1 - pu, t, seed=95, n=7, r=320))
        for j in range(8):
            ang = j * 45
            r = 120 + 260 * pu
            o.append(blob(ellipse_pts(530 + r * math.cos(math.radians(ang)), 900 + r * math.sin(math.radians(ang)), 22 * (1 - pu), 22 * (1 - pu), 10),
                          "#DCF8C6"))
    reach = ease_io(ramp(t, t_pop - .35, .3)) * (1 - ease_io(ramp(t, t_pop + .2, .4)))
    o.append(cat(780, 1560, 1.25, t, dict(look=(-.8, -.4), paw=reach, perk=1.0, smile=1.0 if t > t_pop else 0.0, tail=10 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_pop, 12)
    return view("".join(o), 560 + dx, 1020 + dy, 1.0 + .08 * u, 0, bg=PAPER)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
