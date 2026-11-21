"""Рилс 101 «Встреча в шесть вечера больше не съедает мне весь день», все планы (одна группа ext_a).
frame(sid, t) -> SVG 1080×1920, t — время ролика. Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу);
числа в коде — длительности движений. Сквозной образ: настенные часы, которые Дима сторожит весь день; в решении их
сторожит красный будильник в фуражке. NOCAM=1 — без влёта, тряски и надписей."""
import importlib.util
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

_sp = importlib.util.spec_from_file_location("alarm101", os.path.join(STORY, "common", "alarm.py"))
AL = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(AL)

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
SID = {s["id"]: s["scene"] for s in SH["shots"]}
SCN = {s["scene"]: s for s in SH["shots"]}
END = SH["end"]
NOCAM = bool(os.environ.get("NOCAM"))


def W(i):
    return WORDS[i]["start"]


def WE(i):
    return WORDS[i]["end"]


def stress(i, u):
    return W(i) + (WE(i) - W(i)) * u


def T0(sc):
    return SCN[sc]["t0"]


def T1(sc):
    return SCN[sc]["t1"]


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


def txt(s, x, y, size, fill="#FFFFFF", stroke="#111", sw=None, anchor="middle", op=1.0):
    sw = size * .09 if sw is None else sw
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="IDB" font-size="{size:.1f}" text-anchor="{anchor}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw:.1f}" stroke-linejoin="round" paint-order="stroke" opacity="{op:.3f}" '
            f'style="font-kerning:none">{s}</text>')


# ═════════════════════════ экранные надписи ═════════════════════════
def title(t):
    if NOCAM:
        return ""
    ti = SH["title"]
    return big_title.layer(t, text=ti["text"], t_in=ti["t_in"], t_out=ti["t_out"], hits=[W(i) for i in ti["hits"]])


def label(t):
    """«ВОТ ЧТО Я ПОМЕНЯЛ» — маленькая надпись сверху, только на фразах 5–6."""
    lb = SH["label"]
    a, b = lb["t_in"], lb["t_out"]
    if NOCAM or t < a or t > b + .2:
        return ""
    k = pop(t, a, .25)
    op = 1 - ramp(t, b, .2)
    k *= 1 - .15 * ramp(t, b, .2)
    body = (f'<rect x="-330" y="-62" width="660" height="92" rx="22" fill="#FFD23F" stroke="#111" stroke-width="6"/>'
            + txt(lb["text"], 0, 8, 58, "#111", "#111", 0))
    return f'<g transform="translate(540 236) rotate(-2) scale({max(.01, k):.3f})" opacity="{op:.3f}">{body}</g>'


def kot_title(t):
    kt = SH["kot"]
    if NOCAM:
        return ""
    return big_title.layer(t, text=kt["text"], t_in=kt["t_in"], t_out=kt["t_out"], hits=[W(64), W(67), W(69)], style="yellow")


def over(t):
    return title(t) + label(t) + kot_title(t)


BG = "#efe2c8"


def view(body, cx, cy, s, rot=0.0, bg=BG, t=0.0):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over(t)}')


# ═════════════════════════ комната ═════════════════════════
FL = 1300.0
WALL, WALL_SH, FLOOR_C = "#efe2c8", "#e3d2b2", "#cdb48c"


def room(t, x0=-1400.0, x1=2600.0, dusk=0.0, wall=None):
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


def sofa(x, y, k=1.0):
    o = shape(lib.rrect(-260, -300, 260, -120, 40), "#8aa0c8", "", w=4.4, seed=9750)
    o += shape(lib.rrect(-300, -170, 300, -40, 30), "#9db2d8", "", w=4.4, seed=9751)
    for s in (-1, 1):
        o += shape(lib.rrect(s * 300 - 50, -230, s * 300 + 50, -30, 30), "#7d93bb", "", w=4.4, seed=9752 + s)
        o += line([(s * 240, -30), (s * 250, 0)], 10, INK, taper=0, wmin=1, seed=9754 + s)
    return tf(o, x, y, k)


def wall_clock(x, y, r, hh, mm, seed=0, wob=0.0):
    ah, am = PR.clock_hm(hh, mm)
    c = PR.clock(x, y, r, angle_h=ah, angle_m=am, seed=seed)
    if abs(wob) > .01:
        c = f'<g transform="rotate({wob:.2f} {x:.1f} {y - r:.1f})">{c}</g>'
    return c


def spin_time(t, speed):
    """Время на часах, которые бешено крутятся: speed часов в секунду."""
    m = (t * speed * 60) % 720
    return m / 60.0, m % 60


def stand_hip(k):
    return FL - (people.LEG_LEN - 12) * k - 6


def cat(x, y, k, t, st=None):
    st = dict(dict(look=(-.6, -.3), tail=8 * math.sin(t * 1.7), flame_e=1.0), **(st or {}))
    return CT.draw(x, y, k, st, t)


# Дима за столом (как рилс 96): таз, масштаб, стол, ноутбук; часы на стене; кот на столе справа; окно слева.
DX, DHIP, DK = 360.0, FL - 290, .5
DESK = (680.0, FL - 300)
LAP = (640.0, FL - 330)
CLOCK = (735.0, 470.0)
CAT_AT = (950.0, DESK[1] - 100)
ALARM_AT = (822.0, DESK[1] - 128)
WIN = (165.0, 860.0)
CAL = (500.0, 540.0)


def dima_sit(x, hip, k, expr, t, pose="sit_desk", lean=0.0, head_add=0.0, flip=False, **kw):
    feet = people.sit_kw(x, hip, k)["feet"]
    return people.dima82(x, hip, k, expr, pose, t=t, feet=feet, lean_add=lean, head_add=head_add, flip=flip, **kw)


def alarm(x, y, size, hh, mm, t, ring=0.0, press=0.0, rot=0.0, uid="al", cap=0.0, look=0.0):
    o = AL.shadow(x, y + 1.27 * size, size, .3)
    o += AL.alarm(x, y, size, hh=hh, mm=mm, ring=ring, t=t, press=press, rot=rot, uid=uid)
    if ring > .05:
        o += AL.ring_marks(x, y, size, t, ring)
    if cap > .01:
        o += guard_cap(x, y - 1.32 * size, size / 120 * cap, rot)
    return o


def guard_cap(x, y, k, rot=0.0):
    """Фуражка сторожа на будильнике: тёмно-синяя тулья, чёрный козырёк, золотая кокарда."""
    o = shape([(-92, 0, 1), (-104, -46), (-60, -78), (40, -84), (108, -58), (96, 0, 1)], "#2f3f6e",
              blob([(-80, -10), (90, -10), (96, -30), (-90, -30)], "#22305a", .8), w=4.4, seed=10100)
    o += shape([(-96, -4, 1), (96, -4, 1), (120, 18), (-40, 26)], "#1b1b22", "", w=4.0, seed=10101)
    o += shape(ellipse_pts(4, -46, 18, 15, 12), "#FFD23F", "", w=3.0, seed=10102)
    return tf(o, x, y, k, rot)


def desk_world(t, dima=None, clock=None, cat_st=None, cat_dy=0.0, alarm_on=None, win="day", sun_u=.6, lap_screen="dark",
               lap_lines=0.0, lap_open=1.0, calendar=True, cal_sheet=True, speed=0.0):
    """Комната со столом. dima — готовая фигура (dict) или None (печатает); clock — (hh, mm, wob) или None (бешено крутятся)."""
    o = [room(t)]
    o.append(PR.window(WIN[0], WIN[1], 300, 400, mode=win, t=t, seed=3, curtain=False))
    if win == "day":
        o.append(PR.sun(WIN[0] + 40, WIN[1] - 320 + 80 * (1 - sun_u), 46, 1.0, t, seed=2))
    if calendar:
        o.append(day_sheet(*CAL, .5, t, sheet=cal_sheet))
    if clock is None:
        hh, mm = spin_time(t, 2.2)
        o.append(wall_clock(*CLOCK, 82, hh, mm, seed=1, wob=3 * math.sin(t * 13)))
        o.append(PR.speed_arcs(CLOCK[0] + 115, CLOCK[1], .9, 1.0, t, seed=2, n=3, ang=0))
    else:
        o.append(wall_clock(*CLOCK, 82, clock[0], clock[1], seed=1, wob=clock[2] if len(clock) > 2 else 0.0))
    o.append(chair(DX - 40, FL - 240, 1.0))
    o.append(PR.desk(DESK[0], DESK[1], w=660, depth=100, leg_h=260, seed=7))
    f = dima or dima_sit(DX, DHIP, DK, "type73", t, pose="sit_desk", lean=.12 + .03 * math.sin(t * 9))
    o.append(f["svg"])
    o.append(PR.laptop(LAP[0], LAP[1], .5, open_=lap_open, screen=lap_screen, lines=lap_lines, t=t))
    if alarm_on is not None:
        o.append(alarm_on)
    o.append(cat(CAT_AT[0], CAT_AT[1] - cat_dy, .38, t, cat_st))
    return "".join(o), f


def day_sheet(x, y, k, t, sheet=True, sun=1.0, rot=0.0, crumple=0.0):
    """Отрывной календарь на стене: красная шапка, лист с солнышком (день). sheet=False — лист оторван (под ним следующий)."""
    o = [shape(lib.rrect(-110, -150, 110, 140, 10), "#f4ecdc", "", w=4, seed=10200)]
    o.append(shape(lib.rrect(-110, -150, 110, -96, 10), "#d8453a", "", w=4, seed=10201))
    for j in (-50, 50):
        o.append(shape(ellipse_pts(j, -150, 9, 14, 10), "#9aa0aa", "", w=3, seed=10202 + (j > 0)))
    if sheet:
        o.append(day_leaf(0, 20, 1.0, t, sun))
    return tf("".join(o), x, y, k, rot)


def day_leaf(x, y, k, t, sun=1.0, rot=0.0, crumple=0.0):
    """Лист «день»: белый листок с солнцем (центр)."""
    c = clamp(crumple)
    pts = [(-100, -110), (100, -110), (100, 110), (-100, 110)]
    if c > 0:
        pts = [(px * (1 - .45 * c) + 14 * c * math.sin(i * 2.3), py * (1 - .45 * c) + 12 * c * math.cos(i * 1.7)) for i, (px, py) in enumerate(pts)]
    o = shape(pts, "#fffdf6", "", w=4, seed=10210)
    o += PR.sun(0, 0, 44 * (1 - .4 * c), sun, t, seed=5)
    return tf(o, x, y, k, rot)


def hook_cam_scene(t):
    u = ease_io(clamp((t + .2) / 1.6))
    return 660 - 30 * u, 800 + 20 * u + 8 * math.sin(t * 6), 1.32 + .1 * u


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
            blur += (f'<use href="#hk101" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk101">{body}</g></g>{blur}'


# ═════════════════════════ s01 хук, s17 петля ═════════════════════════
HIT = stress(2, .45)          # «шЕсть»: стрелки встают на шесть


def hook_world(t, tt):
    """Хук: часы несутся и на «шесть» встают на 18:00 с отскоком; Дима спокойно печатает; кот бьёт хвостом; будильник на столе."""
    if tt < HIT:
        hh, mm = spin_time(tt, 2.6)
        clk = None
    else:
        u = tt - HIT
        hh, mm = 6.0, 0.0
        clk = (hh, mm + 9 * math.exp(-u * 7) * math.cos(u * 30), 4 * math.exp(-u * 5) * math.sin(u * 25))
    o = []
    if clk is None:
        body, f = desk_world(t, clock=(hh, mm, 3 * math.sin(tt * 13)), lap_screen="lines", lap_lines=.5 + .1 * math.sin(tt * 3), cat_st=dict(tail=20 * math.sin(tt * 6), look=(.5, -.6)))
    else:
        body, f = desk_world(t, clock=clk, lap_screen="lines", lap_lines=.55, cat_st=dict(tail=20 * math.sin(tt * 6), look=(-.4, -.6), perk=1.0),
                             cat_dy=26 * bump(tt, HIT, .06, .18))
    o.append(body)
    if clk is None:
        o.append(PR.speed_arcs(CLOCK[0] + 115, CLOCK[1], .9, 1.0, tt, seed=2, n=3, ang=0))
    o.append(alarm(ALARM_AT[0], ALARM_AT[1], 34, 17, 30, t, uid="ah"))
    o.append(PR.sparkles(CLOCK[0], CLOCK[1], 1.2, bump(tt, HIT, .05, .4), tt, seed=1, n=5, r=130))
    return "".join(o)


def frame_hook(t):
    cx, cy, s = hook_cam_scene(t)
    body = hook_world(t, t)
    dx, dy = shake(t, HIT, 14)
    v = f'<g transform="{lib.cam(cx + dx, cy + dy, s, 0)}">{body}</g>'
    if NOCAM:
        return lib.svg(f'<rect width="1080" height="1920" fill="{BG}"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT) + over(t))


def frame_loop(t):
    """Петля: тот же мир, что на кадре 0 (часы и кот в той же фазе в конце), камера едет к виду хука."""
    a, b = T0("loop"), T1("loop")
    tt = t - END
    body = hook_world(t, tt)
    import anim
    cx, cy, s = hook_cam_scene(tt)
    u = ease_io(ramp(t, a, b - a))
    h0 = anim.hook_cam(0.0, hit=HIT)
    z = 1.15 + (h0["zoom"] - 1.15) * u
    r = 2 * (1 - u) + h0["rot"] * u
    v = f'<g transform="{lib.cam(cx, cy, s, 0)}">{body}</g>'
    piv = 960.0
    tr = f"translate({540 + h0['dx'] * u:.2f} {piv + h0['dy'] * u:.2f}) rotate({r:.3f}) scale({z:.5f}) translate(-540 {-piv})"
    return lib.svg(f'<rect width="1080" height="1920" fill="{BG}"/><g transform="{tr}">{v}</g>' + over(t))


# ═════════════════════════ s02: день летит в мусорку, Дима его ловит ═════════════════════════
BIN = (120.0, FL)


def frame_save_day(t):
    a, b = T0("save_day"), T1("save_day")
    catch = stress(8, .3)
    src = (CAL[0], CAL[1] + 10)
    tgt = (BIN[0], BIN[1] - 150)

    def arc(u):
        return (src[0] + (tgt[0] - src[0]) * u, src[1] + (tgt[1] - src[1]) * u * u - 90 * math.sin(math.pi * u))
    fl = ease_in(ramp(t, a - .15, catch - a + .15)) * .62
    caught = t >= catch
    lx, ly = arc(fl) if not caught else arc(.62)
    lift = ease_out(ramp(t, catch, .3))
    reach = ease_io(ramp(t, catch - .35, .35))
    rest = (DX + 40, DHIP - 180)
    if caught:
        hold = (lx + 60 * lift, ly - 170 * lift)
    else:
        hold = (rest[0] + (lx - rest[0]) * reach, rest[1] + (ly - rest[1]) * reach)
    f = dima_sit(DX, DHIP, DK, "surprise" if not caught else "relief", t, pose="sit_desk", lean=.05 - .1 * reach,
                 arms={"n": ("ik", hold, -1)}, hands={"n": {"dir": (-.3, -1), "curl": (.6, .7, .7, .7), "thumb": .5}})
    cat_jump = bump(t, catch, .08, .25)
    body, _ = desk_world(t, dima=f, clock=(17, 10 + 30 * (t - a)), cal_sheet=False,
                         cat_st=dict(look=(-.9, -.4), perk=1.0, legs=cat_jump), cat_dy=60 * cat_jump)
    o = [body]
    o.append(PR.basket(BIN[0], BIN[1], .75, seed=1))
    if caught:
        o.append(PR.glow(hold[0], hold[1] - 60, 200, .6 * ease_out(ramp(t, W(9) - .1, .3)), "#ffe58a"))
        o.append(day_leaf(hold[0], hold[1] - 60, .55 + .1 * bump(t, W(9), .06, .3), t, 1.0, rot=-6 + 4 * math.sin(t * 5)))
        o.append(PR.sparkles(hold[0], hold[1] - 60, 1.3, bump(t, W(9), .05, .5), t, seed=21, n=5, r=130))
    else:
        o.append(day_leaf(lx, ly, .5, t, .5, rot=-260 * fl, crumple=.8 * fl))
        o.append(PR.speed_arcs(lx + 70, ly - 30, .9, min(1.0, fl * 3), t, seed=22, n=3, ang=20))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, catch, 12)
    return view("".join(o), 430 + 40 * u + dx, 860 + dy, 1.45 + .1 * u, 1 - 2 * u, t=t)

# ═════════════════════════ s03: утро, стикер «18:00» ═════════════════════════
def sticker_1800(x, y, k, circle=0.0, t=0.0):
    o = PR.sticky(0, 0, 2.4, -4, "yellow", seed=3, mark="none") if True else ""
    o += txt("18:00", 0, 26, 64, "#c3291e", "#c3291e", 0)
    if circle > .01:
        n = 40
        pts = [(118 * math.cos(-1.9 + 2 * math.pi * 1.08 * j / n * circle), 86 * math.sin(-1.9 + 2 * math.pi * 1.08 * j / n * circle)) for j in range(n + 1)]
        o += line(pts, 9, "#e0322a", taper=.3, wmin=.5, seed=301)
    return tf(o, x, y, k)


def frame_morning(t):
    a, b = T0("morning"), T1("morning")
    rise = ease_io(ramp(t, a, b - a))
    o = [room(t)]
    o.append(PR.window(260, 900, 360, 480, mode="day", t=t, seed=4, curtain=False))
    o.append(PR.sun(260, 700 - 120 * rise, 60, ramp(t, a, .6), t, seed=3))
    o.append(PR.glow(260, 700 - 120 * rise, 260, .5, "#ffe8a0"))
    circ = ease_out(ramp(t, W(12), .45))
    o.append(sticker_1800(760, 560, 1.0 + .15 * bump(t, W(12), .06, .3), circ, t))
    o.append(sofa(560, FL, .9))
    hip = FL - 150
    f = people.dima82(560, hip, .5, "nervous" if t < W(12) else "dread81", "d82_rest", t=t, feet=people.sit_kw(560, hip, .5)["feet"],
                      head_add=-.12 * ease_io(ramp(t, W(12), .3)))
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(people.strain_marks((hx, hy), .5, t, ramp(t, W(12), .3)))
    o.append(cat(830, FL - 120, .42, t, dict(look=(-.7, -.2), tail=10 * math.sin(t * 3))))
    dx, dy = shake(t, W(12), 9)
    cx = 470 + 220 * ease_io(ramp(t, W(11), .6))
    return view("".join(o), cx + dx, 820 + dy, 1.25 + .12 * rise, 0, t=t)


# ═════════════════════════ s04: с утра не мог начать ничего ═════════════════════════
def frame_no_start(t):
    a, b = T0("no_start"), T1("no_start")
    jabs = [stress(18, .3), stress(19, .4)]
    jab = max(bump(t, q, .12, .2) for q in jabs)
    drop = ease_out(ramp(t, stress(20, .2), .25))
    if drop < .01:
        f = dima_sit(DX, DHIP, DK, "squint82" if jab < .3 else "wince", t, pose=("sit_desk", "d82_press"), u=.9 * jab, lean=.12)
    else:
        f = dima_sit(DX, DHIP, DK, "glum", t, pose="sit_desk", lean=.12 + .3 * drop, head_add=.22 * drop)
    yawn = bump(t, W(16), .2, .5)
    body, _ = desk_world(t, dima=f, clock=(9, 5 + 40 * (t - a)), lap_screen="lines", lap_lines=0.0,
                         cat_st=dict(look=(-.4, .2), blink=.7 * yawn, tilt=-10 * yawn, sleep=.3 * yawn))
    o = [body]
    if drop > .01:
        hx, hy = f["head"]
        o.append(PR.sparkles(hx + 40, hy - 40, .9, bump(t, stress(20, .2) + .2, .05, .3), t, seed=41, n=3, r=70))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, stress(20, .2) + .2, 10)
    return view("".join(o), 560 + dx, 880 + dy - 30 * u, 1.55 + .2 * u, 1.5 - 3 * u, t=t)


# ═════════════════════════ s05: смотрел на часы каждые десять минут ═════════════════════════
def frame_stare_clock(t):
    a, b = T0("stare_clock"), T1("stare_clock")
    ticks = [W(22), W(23), W(24), W(25), W(26), stress(26, .7)]
    n = sum(1 for q in ticks if t >= q)
    last = max([q for q in ticks if t >= q], default=None)
    mm = 10 * n + (10 * ease_out(ramp(t, last, .08)) - 10 if last is not None else 0)
    jolt = bump(t, last, .04, .15) if last is not None else 0.0
    o = [room(t)]
    o.append(wall_clock(540, 560, 280, 10 + mm / 60, mm % 60 + 20, seed=5, wob=4 * jolt))
    o.append(PR.glow(540, 560, 400, .25, "#fff1c4"))
    look = .25 * math.sin(t * 2.5)
    f = people.dima82(540, 1930, 1.55, "stare73", "d82_rest", t=t, feet="stand", head_add=-.06 * jolt + .05 * look)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.speed_arcs(hx - 230, hy - 80, 1.2, jolt, t, seed=51, n=2, ang=150))
    o.append(PR.speed_arcs(hx + 230, hy - 80, 1.2, jolt, t, seed=52, n=2, ang=30))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, last, 6)
    return view("".join(o), 540 + dx, 900 + dy + 40 * u, 1.0 + .08 * u + .03 * jolt, 0, t=t)


# ═════════════════════════ s06: будто охраняю их ═════════════════════════
def frame_guard(t):
    a, b = T0("guard"), T1("guard")
    on = ease_out(ramp(t, W(28), .12))
    k = .5
    hip = stand_hip(k)
    gx = 380.0
    hand = (gx + 150, hip - 300)
    f = people.dima82(gx, hip, k, "det80", "d82_rest", t=t, feet="stand", head_add=-.08 + .05 * math.sin(t * 3),
                      arms={"n": ("ik", hand, -1)}, hands={"n": {"dir": (1, -.4), "curl": (.85, .85, .85, .85), "thumb": .6}})
    o = [room(t)]
    o.append(wall_clock(760, 520, 110, 11, 40 + 6 * (t - a), seed=1))
    o.append(f["svg"])
    ang = math.degrees(math.atan2(520 - hand[1], 760 - hand[0]))
    o.append(PR.flashlight(hand[0] + 20, hand[1] - 6, 1.1, ang, on))
    o.append(PR.beam(hand[0] + 70, hand[1] - 30, ang, 420, 26, .8 * on))
    o.append(PR.glow(760, 520, 200, .5 * on, "#fff4b0"))
    o.append(PR.sparkles(760, 520, 1.3, bump(t, W(28), .05, .35), t, seed=61, n=4, r=150))
    o.append(CT.curl(215, FL - 4, .55, dict(breath=1.2), t))
    o.append(PR.z_mark(300, FL - 250 - 20 * math.sin(t * 3), 1.0, .6 + .4 * math.sin(t * 4)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(28), 8)
    return view("".join(o), 540 + dx, 820 + dy, 1.5 + .12 * u, -1 + 2 * u, t=t)


# ═════════════════════════ s07: стрелки срываются к шести ═════════════════════════
def frame_rush_hands(t):
    a, b = T0("rush_hands"), T1("rush_hands")
    run = ease_in(ramp(t, a, b - a + .1))
    mm = 17 * 60 + 10 + 48 * run
    jump = bump(t, W(33), .1, .35)
    f = dima_sit(DX, DHIP - 120 * jump, DK, "panic82", t, pose=("sit_desk", "d82_shrug"), u=ease_io(ramp(t, W(33) - .1, .2)), lean=-.05)
    body, _ = desk_world(t, dima=f, clock=(mm // 60, mm % 60, 5 * math.sin(t * 30) * run), win="evening",
                         cat_st=dict(look=(-.9, -.6), perk=1.0, legs=jump), cat_dy=50 * jump)
    o = [body]
    o.append(PR.speed_arcs(CLOCK[0] + 115, CLOCK[1], .9, run, t, seed=71, n=3, ang=0))
    hx, hy = f["head"]
    o.append(PR.sweat(hx + 50, hy - 20, .8) if hasattr(PR, "sweat") else "")
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(33), 12)
    cx = 560 + 30 * u
    return view("".join(o), cx + dx, 780 + dy, 1.45 + .2 * u, 0, t=t)


def ease_in(u):
    return lib.ease_in(u, 2)


# ═════════════════════════ s08: выбегал впритык ═════════════════════════
def frame_door_out(t):
    a, b = T0("door_out"), T1("door_out")
    op = ease_out(ramp(t, a - .1, .18))
    k = .5
    run_u = ramp(t, a + .05, b - a)
    x = 430 + 760 * run_u
    o = [room(t, wall="#e6d6be")]
    o.append(PR.door(420, FL, .95, op, seed=2))
    o.append(wall_clock(420, 260, 60, 5, 57 + 2 * run_u, seed=3))
    if t > a + .02:
        f = people.dima82_run(x, stand_hip(k), k, (t - a) / .34, t=t, expr="rush82", boot=False, socks=None, sandwich=False)
        o.append(f["svg"])
        o.append(PR.speed_arcs(x - 170, stand_hip(k) - 120, 1.3, 1.0, t, seed=81, n=4, ang=180))
    o.append(PR.wind_lines(560, 700, 1.2, op, t, seed=82, n=4))
    dx, dy = shake(t, a + .05, 14)
    return view("".join(o), 600 + 160 * run_u + dx, 860 + dy, 1.45, -2 + 3 * run_u, t=t)


# ═════════════════════════ s09: и опаздывал, 18:07 ═════════════════════════
def street(t, x0=-1400, x1=2600):
    o = [rect(x0, -1400, x1, FL + 1400, "#cfe0ea")]
    o.append(rect(x0, FL - 40, x1, FL + 1400, "#b8b2a6"))
    o.append(line([(x0, FL - 40), (x1, FL - 40)], 4, seed=91))
    for i in range(-3, 8):
        bx = i * 360
        h = 520 + 140 * ((i * 37) % 3)
        o.append(shape(lib.rect_pts(bx, FL - 40 - h, bx + 320, FL - 40), ["#d9b99a", "#c9a7a0", "#b9c3a2"][i % 3], "", w=4, seed=920 + i))
        for r in range(2):
            for c in range(2):
                o.append(shape(lib.rect_pts(bx + 50 + 130 * c, FL - 40 - h + 70 + 160 * r, bx + 140 + 130 * c, FL - 40 - h + 170 + 160 * r),
                               "#eaf2f6", "", w=3, seed=940 + i * 4 + r * 2 + c))
    return "".join(o)


def board(x, y, k, t, flash=0.0):
    o = shape(lib.rrect(-190, -80, 190, 80, 14), "#22232b", "", w=5, seed=950)
    o += line([(0, 80), (0, 420)], 14, "#55595f", taper=0, wmin=1, seed=951)
    col = lib.mix("#ff5a3c", "#ffe14a", flash)
    o += f'<rect x="-170" y="-62" width="340" height="124" rx="8" fill="{col}" opacity="{.10 + .15 * flash:.3f}"/>'
    o += txt("18:07", 0, 44, 120, col, "#22232b", 0)
    return tf(o, x, y, k)


def frame_late(t):
    a, b = T0("late"), T1("late")
    k = .5
    x = 120 + 820 * ramp(t, a - .1, b - a + .2)
    o = [street(t)]
    fl = bump(t, stress(38, .25), .05, .35)
    o.append(board(760, FL - 900, 1.0 + .12 * fl, t, max(fl, .5 + .5 * math.sin(t * 16) * (t > W(38)))))
    f = people.dima82_run(x, stand_hip(k), k, (t - a) / .32, t=t, expr="panic82", boot=False, socks=None, sandwich=False)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.sweat(hx - 40, hy - 30, .9) if hasattr(PR, "sweat") else "")
    o.append(PR.speed_arcs(x - 160, stand_hip(k) - 100, 1.3, 1.0, t, seed=93, n=4, ang=180))
    dx, dy = shake(t, stress(38, .25), 14)
    return view("".join(o), 560 + 120 * ramp(t, a, b - a) + dx, 880 + dy, 1.25 + .06 * fl, 0, bg="#cfe0ea", t=t)


# ═════════════════════════ s10: вот что я поменял ═════════════════════════
def frame_change(t):
    """«Вот что я поменял»: красный будильник падает сверху на стол на «поменял» (сплющивается и отскакивает), Дима кивает,
    кот смотрит на будильник."""
    a, b = T0("change"), T1("change")
    land = stress(42, .35)
    fall = ease_in(ramp(t, land - .35, .35))
    y = ALARM_AT[1] - 10 - 700 * (1 - fall)
    sq = bump(t, land, .03, .18)
    al = alarm(ALARM_AT[0], y, 44, 7, 0, t, rot=8 * (1 - fall) + 5 * sq, uid="ac")
    nod = .12 * math.sin((t - land) * 14) * bump(t, land, .05, .4)
    f = dima_sit(DX, DHIP, DK, "resolve" if t < land else "sure82", t, pose="sit_desk", lean=.08, head_add=nod)
    look = ease_io(ramp(t, land - .3, .3))
    body, _ = desk_world(t, dima=f, clock=(8, 30 + 10 * (t - a)), alarm_on=al,
                         cat_st=dict(look=(-.9, -.6 + .6 * look), perk=look, tilt=-10 * look), cat_dy=30 * bump(t, land, .06, .2))
    o = [body, PR.sparkles(ALARM_AT[0], ALARM_AT[1] - 40, 1.3, bump(t, land, .05, .4), t, seed=101, n=5, r=130)]
    o.append(PR.speed_arcs(ALARM_AT[0], y - 90, 1.0, (1 - fall) * (t > land - .35), t, seed=102, n=3, ang=270))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, land, 10)
    return view("".join(o), 640 + 40 * u + dx, 860 + dy, 1.45 + .2 * u, 0, t=t)

# ═════════════════════════ s11: ставлю будильник на время выхода ═════════════════════════
def finger(x, y, k=1.0):
    """Палец сверху-справа жмёт: (x, y) — кончик указательного (рукав худи уходит за кадр)."""
    wx, wy = x + 120 * k, y - 170 * k
    ex, ey = wx + .55 * 900 * k, wy - .85 * 900 * k
    sleeve = (line([(wx + 20 * k, wy - 30 * k), (ex, ey)], 118 * k, INK, taper=0, wmin=1, seed=781)
              + line([(wx + 20 * k, wy - 30 * k), (ex, ey)], 104 * k, "#d4a23e", taper=0, wmin=1, seed=782))
    return sleeve + people.hand_svg("dima", (wx, wy), (-.55, .85), 1.6 * k, curl=(0, .9, .9, .9), spread=.05, thumb=.75, seed=780)


def door_note(x, y, k, u, t):
    if u <= .01:
        return ""
    o = PR.sticky(0, 0, 2.2, 5, "blue" if "blue" in getattr(PR, "_STICKY", {}) else "yellow", seed=7, mark="none")
    o += shape(lib.rect_pts(-36, -50, 36, 50), "#C99A6B", "", w=4, seed=1110)
    o += shape(ellipse_pts(22, 4, 6, 6, 8), "#f4d35e", "", w=2.5, seed=1111)
    o += line([(44, 30), (82, 30), (70, 18)], 6, "#2f9a4a", taper=0, wmin=1, seed=1112) + line([(82, 30), (70, 42)], 6, "#2f9a4a", taper=0, wmin=1, seed=1113)
    return tf(o, x, y, k * lib.back_out(clamp(u), 2.0))


def frame_set_alarm(t):
    a, b = T0("set_alarm"), T1("set_alarm")
    press = bump(t, stress(43, .3), .06, .2)
    turn = ease_io(ramp(t, W(44), WE(47) - W(44)))
    mm = 7 * 60 + (17 * 60 + 30 - 7 * 60) * turn
    o = [room(t), PR.desk(540, FL + 200, w=1300, depth=600, legs=False, seed=9)]
    cx, cy, size = 620.0, 980.0, 210.0
    o.append(alarm(cx, cy, size, mm // 60, mm % 60, t, press=press, rot=2 * math.sin(t * 2), uid="as"))
    o.append(PR.glow(cx, cy, 330, .3 + .3 * bump(t, WE(47) - .1, .05, .4), "#fff1c4"))
    o.append(door_note(230, 700, 1.5, ramp(t, W(47), .3), t))
    tip_y = cy - 1.4 * size - 18 + 30 * press - 260 * (1 - ramp(t, a - .2, .3))
    o.append(finger(cx + 4, tip_y, 1.0) if t < W(44) + .2 else
             finger(cx + 1.2 * size + 30, cy - .6 * size + 20 * math.sin(t * 20) * (turn < 1), .9))
    o.append(PR.sparkles(cx, cy, 2.0, bump(t, WE(47) - .1, .05, .45), t, seed=111, n=5, r=280))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, stress(43, .3), 8)
    return view("".join(o), 600 + dx, 900 + dy, 1.05 + .1 * u, 0, t=t)


# ═════════════════════════ s12: часы караулит он, а не я ═════════════════════════
def frame_alarm_guard(t):
    a, b = T0("alarm_guard"), T1("alarm_guard")
    cap = ease_out(ramp(t, W(50) - .05, .25))
    away = ease_io(ramp(t, W(53), .35))
    patrol = 5 * math.sin(t * 5) * cap
    if away < .5:
        f = dima_sit(DX, DHIP, DK, "stare73", t, pose="sit_desk", lean=.05, head_add=-.18 * (1 - away))
    else:
        f = dima_sit(DX, DHIP, DK, "calm82", t, pose="sit_desk", lean=.12 + .03 * math.sin(t * 9))
    al = alarm(ALARM_AT[0], ALARM_AT[1] - 10, 44, 17, 30, t, rot=patrol, uid="ag", cap=cap)
    body, _ = desk_world(t, dima=f if away < .5 else None, clock=(9, 40 + 8 * (t - a)), alarm_on=al,
                         cat_st=dict(look=(-.6, -.4), tail=8 * math.sin(t * 2)))
    o = [body, PR.sparkles(ALARM_AT[0], ALARM_AT[1] - 70, 1.0, bump(t, W(50), .05, .4), t, seed=121, n=4, r=90)]
    o.append(PR.dash_path([(ALARM_AT[0] + 20, ALARM_AT[1] - 60), (650, 600), (CLOCK[0] - 60, CLOCK[1] + 50)], cap * (1 - away * .7), w=5,
                          col="#e0322a", seed=122))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(50), 8)
    cx = 600 + 40 * u
    return view("".join(o), cx + dx, 780 + dy + 60 * u, 1.55 + .1 * u, 0, t=t)


# ═════════════════════════ s13: одно дело до звонка ═════════════════════════
def frame_one_task(t):
    a, b = T0("one_task"), T1("one_task")
    lines = ease_io(ramp(t, a, b - a))
    tick = ease_out(ramp(t, stress(59, .2), .3))
    al = alarm(ALARM_AT[0], ALARM_AT[1] - 10, 44, 17, 30, t, uid="ao", cap=1.0, rot=2 * math.sin(t * 3))
    body, f = desk_world(t, clock=(11, 20 + 8 * (t - a)), alarm_on=al, lap_screen="lines", lap_lines=lines,
                         cat_st=dict(look=(-.7, .1), tail=10 * math.sin(t * 2.5)))
    o = [body]
    o.append(PR.check_mark(LAP[0] - 10, LAP[1] - 240, 1.6 * pop(t, stress(59, .2), .3) if tick > 0 else 0, tick, col="#2f9a4a"))
    o.append(PR.sparkles(LAP[0], LAP[1] - 240, 1.3, bump(t, stress(59, .2) + .1, .05, .45), t, seed=131, n=5, r=120))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, stress(59, .2) + .05, 7)
    return view("".join(o), 610 + dx, 860 + dy, 1.7 + .15 * u, -1 + 2 * u, t=t)


# ═════════════════════════ s14: кот сидит рядом ═════════════════════════
def frame_cat_near(t):
    """«кот сидит рядом»: Дима печатает и улыбается коту, кот жмурится и мурлычет, сердечко."""
    a, b = T0("cat_near"), T1("cat_near")
    glance = ease_io(ramp(t, a, .3)) * (1 - ease_io(ramp(t, b - .3, .3)))
    f = dima_sit(DX, DHIP, DK, "smile73", t, pose="sit_desk", lean=.12 + .03 * math.sin(t * 9), head_add=-.08 * glance)
    al = alarm(ALARM_AT[0], ALARM_AT[1] - 10, 44, 17, 30, t, uid="an", cap=1.0)
    body, _ = desk_world(t, dima=f, clock=(13, 10 + 8 * (t - a)), alarm_on=al, lap_screen="lines", lap_lines=1.0,
                         cat_st=dict(look=(-.8, -.2), blink=.85, smile=1.0, tilt=-8 * math.sin(t * 3), tail=16 * math.sin(t * 3)))
    o = [body, PR.purr(CAT_AT[0] + 40, CAT_AT[1] - 190, 1.2, t, 1.0, seed=141)]
    o.append(PR.heart(CAT_AT[0] - 30, CAT_AT[1] - 250 - 60 * ramp(t, W(61), .8), .9 * pop(t, W(61), .3), bump(t, W(62), .05, .3)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(60), 6)
    return view("".join(o), 690 + 40 * u + dx, 860 + dy, 1.5 + .12 * u, 0, t=t)

# ═════════════════════════ s15: напиши «КОТ» ═════════════════════════
def tap_finger(x, y, k=1.0):
    """Палец снизу-справа жмёт по экрану телефона: (x, y) — кончик; рукав уходит вниз за кадр."""
    wx, wy = x + 110 * k, y + 160 * k
    ex, ey = wx + .45 * 900 * k, wy + .9 * 900 * k
    sleeve = (line([(wx + 20 * k, wy + 30 * k), (ex, ey)], 118 * k, INK, taper=0, wmin=1, seed=791)
              + line([(wx + 20 * k, wy + 30 * k), (ex, ey)], 104 * k, "#d4a23e", taper=0, wmin=1, seed=792))
    return sleeve + people.hand_svg("dima", (wx, wy), (-.55, -.85), 1.6 * k, curl=(0, .9, .9, .9), spread=.05, thumb=.75, seed=790)


def comment_screen(x0, y0, x1, y1, t, typed, send, posted, caret):
    w, h = x1 - x0, y1 - y0
    o = [rect(x0, y0, x1, y1, "#ffffff")]
    o.append(rect(x0, y0, x1, y0 + h * .32, "#3a3550"))
    o.append(PR.sun(x0 + w * .3, y0 + h * .16, 30, 1.0, t, seed=9))
    o.append(rect(x0 + w / 2 - 34, y0 + h * .32 + 14, x0 + w / 2 + 34, y0 + h * .32 + 22, "#d6d6de"))
    sh = 104 * ease_out(clamp(posted), 3)
    cols = ["#7cc46a", "#6aa6e8", "#e88a6a", "#b48ae8"]
    for j in range(4):
        yy = y0 + h * .32 + 50 + j * 104 + sh
        if yy > y1 - 170:
            continue
        o.append(f'<circle cx="{x0 + 50:.1f}" cy="{yy + 24:.1f}" r="24" fill="{cols[j]}"/>')
        o.append(rect(x0 + 90, yy + 6, x0 + 180, yy + 18, "#b9b9c6"))
        o.append(rect(x0 + 90, yy + 28, x0 + 90 + [220, 150, 260, 180][j], yy + 40, "#dedee6"))
    if posted > 0:
        yy = y0 + h * .32 + 50
        op = clamp(posted * 3)
        o.append(f'<g opacity="{op:.3f}"><rect x="{x0 + 10:.1f}" y="{yy - 10:.1f}" width="{w - 20:.1f}" height="90" rx="18" fill="#fff4d6"/>'
                 f'<circle cx="{x0 + 50:.1f}" cy="{yy + 30:.1f}" r="24" fill="#d4a23e"/>' + txt("КОТ", x0 + 90, yy + 50, 46, "#1d2030", "#1d2030", 0, "start") + "</g>")
    fy = y1 - 120
    o.append(rect(x0, fy - 16, x1, y1, "#ffffff"))
    o.append(f'<rect x="{x0 + 20:.1f}" y="{fy:.1f}" width="{w - 110:.1f}" height="76" rx="38" fill="#f2f2f6" stroke="#dcdce4" stroke-width="3"/>')
    if typed:
        o.append(txt(typed, x0 + 48, fy + 56, 52, "#1d2030", "#1d2030", 0, "start"))
    if caret and not posted and int(t * 4) % 2 == 0:
        cw = big_title.text_w(typed, 52) if typed else 0
        o.append(rect(x0 + 52 + cw, fy + 14, x0 + 56 + cw, fy + 62, "#2f8cff"))
    sc = 1 - .2 * clamp(send * 2) if send > 0 else 1
    o.append(f'<g transform="translate({x1 - 50:.1f} {fy + 38:.1f}) scale({sc:.3f})"><circle r="30" fill="#2f8cff"/>'
             f'<path d="M-11 0 L11 0 M2 -9 L11 0 L2 9" stroke="#ffffff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>')
    return "".join(o)


def frame_cta_type(t):
    a, b = T0("cta_type"), T1("cta_type")
    t0, st = W(64) + .02, .1
    word = "КОТ"
    nch = int(clamp((t - t0) / st, 0, len(word)))
    send_t = t0 + st * len(word) + .12
    sent = t >= send_t + .05
    typed = word[:nch] if not sent else ""
    posted = ramp(t, send_t + .1, .3)
    k = .78
    px, py = 540.0, 980.0
    x0, y0, x1, y1 = PR.phone_frame_rect(px, py, k)
    o = [room(t, wall="#e6d6be")]
    o.append(comment_screen(x0, y0, x1, y1, t, typed, ramp(t, send_t, .12), posted, True))
    o.append(PR.phone_frame(px, py, k, glow_=.6))
    o.append(people.hand_svg("dima", (x0 - 30, y0 + 520), (.6, -.6), 1.7, curl=(.75, .8, .8, .8), thumb=.2, seed=1500))
    tap = (x1 - 50, y1 - 82) if t >= send_t - .15 else (x0 + 110 + 40 * nch, y1 - 82)
    pr = max(bump(t, t0 + st * j, .03, .07) for j in range(3)) if t < send_t - .15 else bump(t, send_t, .04, .1)
    o.append(tap_finger(tap[0], tap[1] + 40 * (1 - pr), .8))
    o.append(cat(940, FL - 60, .55, t, dict(look=(-.8, -.6), perk=1.0, tail=14 * math.sin(t * 4))))
    zin = ease_out(ramp(t, a, .3), 3)
    s = 1.0 + .25 * zin
    dx, dy = shake(t, send_t, 7)
    return view("".join(o), 540 + dx, 1060 - 60 * zin + dy, s, 0, bg="#e6d6be", t=t)


# ═════════════════════════ s16: если одна встреча тоже съедает тебе целый день ═════════════════════════
def frame_cta_calm(t):
    a, b = T0("cta_calm"), T1("cta_calm")
    ring_t = stress(67, .1)
    stop_t = stress(69, .2)
    ring = ramp(t, ring_t, .05) * (1 - ramp(t, stop_t, .08))
    press = bump(t, stop_t, .05, .2)
    close = ease_io(ramp(t, stop_t + .25, .4))
    if t < stop_t - .25:
        f = dima_sit(DX, DHIP, DK, "type73" if t < ring_t else "calm82", t, pose="sit_desk", lean=.12)
    else:
        hand = (LAP[0] - 70, LAP[1] - 150 + 90 * close)
        f = dima_sit(DX, DHIP, DK, "smile73", t, pose="sit_desk", lean=.15, arms={"n": ("ik", hand, -1)},
                     hands={"n": {"dir": (.3, 1), "curl": (.1, .1, .1, .1), "thumb": .3}})
    al = alarm(ALARM_AT[0], ALARM_AT[1] - 10, 44, 17, 30, t, ring=ring, press=press, uid="az", cap=1.0)
    body, _ = desk_world(t, dima=f, clock=(5, 30, 0), win="evening", alarm_on=al, lap_screen="lines", lap_lines=1.0, lap_open=1 - .85 * close,
                         cat_st=dict(look=(-.9, .2), smile=ramp(t, stop_t, .3), tail=14 * math.sin(t * 3), paw=ease_io(ramp(t, stop_t - .2, .2)) * (1 - ease_io(ramp(t, stop_t + .35, .3))), paw_dx=-120))
    o = [body, PR.sparkles(DX + 40, DHIP - 420, 1.3, bump(t, W(72), .05, .45), t, seed=161, n=5, r=140)]
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ring_t, 9)
    return view("".join(o), 700 - 20 * u + dx, 860 + dy + 30 * u, 1.45 - .08 * u, 0, t=t)


FRAMES = {k[6:]: v for k, v in dict(globals()).items() if k.startswith("frame_")}


def frame(sid, t):
    lib.DEFS.clear()
    return FRAMES[SID[sid]](t)
