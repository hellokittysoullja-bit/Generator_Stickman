"""Рилс 61 «стол», группа C — эксперимент в Миннесоте: s08 (аккуратная комната, участница садится, листы выравниваются щелчком),
s09 (захламлённая комната, падают лист и кружка, бородач садится, подъезжает лист с карандашом, чешет затылок),
s12 (участница крупнее, облачко-квадрат, кивок и очки, поднос с яблоком и шоколадкой, рука тянется).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Комната — ext_c/lab.py (одна комната и один стол на оба варианта),
люди — common/people.py, предметы — common/props.py."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import lab as L  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, smooth, spring  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


T_SAZHALI, T_AKK = wt(33), wt(35)
T_ZAHL, T_PROSILI, T_PRIDUMAT = wt(37), wt(40), wt(41)
T_PORYADKE, T_VYBIRALI, T_POLEZ = wt(50), wt(53), wt(54)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if (u <= 0 or u >= 1) else math.sin(math.pi * u) ** 2


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def lerp(a, b, u):
    return a + (b - a) * u


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


import people as P  # noqa: E402
import props as PR  # noqa: E402

PS = 0.70                 # масштаб участников (голова ≈ 300·PS)
SIT_Y = 1195.0            # таз сидящего (под крышкой стола)
STAND_Y = 1040.0          # таз стоящего за столом


def room(t, kind, people_svg="", items=None, extra=""):
    o = [L.back(t, kind), people_svg, L.desk_top(kind)]
    o.append(items if items is not None else (L.desk_items_tidy(t) if kind == "tidy" else L.desk_items_messy(t)))
    o.append(extra)
    o.append(L.under_desk())
    o.append(L.desk_front())
    if kind == "messy":
        o.append(L.clutter_front(t))
    return "".join(o)


FOOT_Y = L.WALL_Y + 42


def feet_for(x, y, walk=None):
    """Ноги: сидя — колени вперёд, стопы на полу под столом; стоя/шагая (walk — фаза) — стопы под тазом попеременно."""
    if walk is None:
        sit = clamp((y - (STAND_Y + 10)) / (SIT_Y - STAND_Y - 10))
        dx = lerp(30, 215, sit)
        return {"n": ((x + dx, FOOT_Y), 0.0), "f": ((x + dx - 40, FOOT_Y - 4), 0.0)}
    a = 46 * math.sin(walk)
    return {"n": ((x + 20 + a, FOOT_Y - 14 * max(0, math.cos(walk))), 0.0), "f": ((x - 10 - a, FOOT_Y - 4 - 14 * max(0, -math.cos(walk))), 0.0)}


def seated(who, x, y, t, expr, pose="sit_desk", lean_add=0.0, head_add=0.0, arms=None, hands=None, flip=False, chair=True, walk=None):
    kw = P.pose_kw(pose, x, y, PS, who)
    kw["feet"] = feet_for(x, y, walk)
    if arms:
        kw["arms"].update(arms)
    if hands:
        kw["hands"].update(hands)
    kw["lean"] += lean_add
    kw["head_ang"] += head_add
    fig = P.figure(who, x, y, PS, expr, flip=flip, **kw)
    ch = L.chair_back(x - (14 if not flip else -14), max(y, SIT_Y) + 10, 0, .78) if chair else ""
    return ch + fig["svg"], fig


def sit_curve(t, t_sit, dur=.42):
    """0 — стоит, 1 — сидит; опускается с лёгким отскоком сиденья."""
    u = (t - (t_sit - dur * .6)) / dur
    if u <= 0:
        return 0.0
    if u < 1:
        return ease_in(u, 1.6)
    return 1.0 + .06 * math.exp(-(u - 1) * 3.2) * math.sin((u - 1) * 9)


def frame_debug(kind, t):
    s = 1.0
    set_ink(s)
    return f'<g transform="{lib.cam(540, 960, s)}">{room(t, kind)}</g>'


def frame(sid, t):
    lib.dyn_begin()
    if sid in ("dtidy", "dmessy"):
        body = frame_debug(sid[1:], t)
    else:
        body = {"s08": frame08, "s09": frame09, "s12": frame12}[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="#cfdad8"/>{body}')


# ═══════════════════════════ s08: аккуратная комната, участница садится, щелчок ═══════════════════════════
def frame08(t):
    a = 17.6
    u = clamp((t - a) / 2.9)
    s = 1.42 + .16 * ease_io(u)
    cx = lerp(350, 600, ease_io(u))
    cy = lerp(860, 900, u) + 4 * math.sin(t * 1.7)
    rot = lerp(-1.0, .6, ease_io(u))
    set_ink(s)
    # участница: входит справа (x 760 → 500), шаги — покачивание таза, на «сажали» садится
    w = clamp((t - a) / (T_SAZHALI - .35 - a))
    x = lerp(800, 500, ease_out(w, 2))
    step = abs(math.sin((t - a) * 7.5)) * 8 * (1 - w ** 3)
    sc = sit_curve(t, T_SAZHALI)
    y = lerp(STAND_Y - step, SIT_Y, min(1.0, sc)) + (sc - 1) * 60 if sc > 1 else lerp(STAND_Y - step, SIT_Y, sc)
    snap = t > T_AKK
    mis = 1.0 if t < T_AKK else max(0.0, 1 - ease_out(clamp((t - T_AKK) / .12), 2) * 1.08 + .08 * math.exp(-(t - T_AKK) * 9) * math.sin((t - T_AKK) * 40))
    mis = clamp(mis)
    look = (.5, .1) if sc < .5 else (.55, .55)
    ex = dict(P.EXPR["bob"]["calm"], look=look)
    if snap:
        k = smooth(T_AKK, T_AKK + .2, t)
        ex = dict(P.EXPR["bob"]["pleased"], look=(.55, .45), lid=.6 + .25 * bump(t, T_AKK, .25), smile=.4 + .6 * k)
    ex["closed"] = max(bump(t, 17.95, .16), bump(t, 19.95, .16))
    if sc < .6:
        pose_arms = {"f": ("ang", 0.25 + .1 * math.sin((t - a) * 7.5), .3), "n": ("ang", -0.15 - .1 * math.sin((t - a) * 7.5), .35)}
        hands = {"f": {"curl": (.35, .35, .4, .45), "thumb": .3}, "n": {"curl": (.35, .35, .4, .45), "thumb": .3}}
    else:
        pose_arms, hands = None, None
    fig, info = seated("bob", x, y, t, ex, lean_add=-.08 * (1 - min(1, sc)) - .04 * bump(t, T_SAZHALI, .4),
                       head_add=.06 * bump(t, T_AKK + .05, .35), arms=pose_arms, hands=hands, walk=(t - a) * 7.5 if w < 1 else None)
    shine = clamp((t - T_AKK) / .5) if snap else 0.0
    items = L.desk_items_tidy(t, misalign=mis, shine=shine if 0 < shine < 1 else 0.0)
    extra = ""
    if snap and t < T_AKK + .4:
        extra += PR.clink(L.SX + 120, L.TOP_BACK - 10, 1.1, clamp((t - T_AKK) / .4), 3)
    body = room(t, "tidy", fig, items, extra)
    dx, dy = PR.shake(t, T_AKK, 5, .25, 2)
    return f'<g transform="translate({dx:.2f} {dy:.2f})"><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g></g>'


# ═══════════════════════════ s09: захламлённая комната ═══════════════════════════
def frame09(t):
    a = 20.1
    back = sm(t, T_ZAHL - .05, T_ZAHL + .55)
    s = lerp(1.55, 1.13, back) + .03 * sm(t, 21.5, 23.4)
    cx = lerp(560, 560, back) + 14 * math.sin(t * .9) + lerp(0, 40, sm(t, 21.5, 23.4))
    cy = lerp(1000, 920, back) + 5 * math.sin(t * 1.3)
    rot = lerp(1.6, -.4, back)
    set_ink(s)
    X = 640.0
    sc = sit_curve(t, 21.05, .5)
    y = SIT_Y + (sc - 1) * 70 if sc > 1 else lerp(STAND_Y, SIT_Y, sc)
    sway = 6 * math.sin(t * 2.2) * (1 - min(1, sc))
    ex = dict(P.EXPR["beard"]["calm"], look=(.2, .4))
    if t > T_PROSILI - .1:
        ex = dict(P.EXPR["beard"]["calm"], look=(.35, .7), brows="up")
    if t > T_PRIDUMAT - .05:
        ex = dict(P.EXPR["beard"]["think"])
        ex["look"] = (.3, -.7)
    ex["closed"] = max(bump(t, 20.6, .16), bump(t, 22.15, .16))
    arms, hands = None, None
    if sc < .6:
        arms = {"f": ("ang", 0.2, .25), "n": ("ang", -0.1, .3)}
        hands = {"f": {"curl": (.35, .35, .4, .45), "thumb": .3}, "n": {"curl": (.35, .35, .4, .45), "thumb": .3}}
    head_add = 0.0
    scr = smooth(T_PRIDUMAT - .12, T_PRIDUMAT + .15, t)
    if scr > 0:
        # чешет затылок ближней рукой: цель — за головой (в неотражённой системе героя затылок слева)
        hd = P.figure("beard", X, y, PS, ex, flip=True, **P.pose_kw("sit_desk", X, y, PS, "beard"))["head"]
        hx_un = 2 * X - hd[0]
        wig = 9 * math.sin(t * 34)
        tgt = (lerp(X + 240 * PS * 1.05, hx_un - 95 * PS + wig * .5, scr), lerp(y - 200 * PS, hd[1] - 120 * PS + wig, scr))
        arms = {"n": ("ik", tgt, +1)}
        hands = {"n": {"dir": (-.3, -1), "curl": (.45 + .15 * math.sin(t * 34), .45, .5, .55), "thumb": .35, "flip": 1}}
        head_add = .08 * scr
    fig, info = seated("beard", X + sway, y, t, ex, lean_add=-.06 * (1 - min(1, sc)), head_add=head_add, arms=arms, hands=hands, flip=True)
    # падающий лист и кружка, звяк
    extra = ""
    land = T_ZAHL + .42
    if t < land:
        u = clamp((t - (T_ZAHL - .25)) / (land - (T_ZAHL - .25)))
        fy = lerp(150, L.TOP_FRONT - 40, u ** 1.6)
        fx = 470 + 60 * math.sin(u * 5)
        extra += PR.flying_sheet(fx, fy, .9, -20 + 30 * u, 41, "sketch", flap=t * 9)
    else:
        extra += PR.paper(470, L.TOP_FRONT - 34, .9, -14, 120, 160, 41, "sketch", .45)
    mug_land = T_ZAHL + .3
    mx, my = 560.0, L.TOP_BACK + 48
    if t < mug_land:
        u = clamp((t - (T_ZAHL - .15)) / .45)
        extra_mug = L.mug(mx, lerp(-200, my, u * u), 1.0, "green", 12 * (1 - u), 77)
    else:
        e = math.exp(-(t - mug_land) * 6) * math.sin((t - mug_land) * 38)
        extra_mug = L.mug(mx, my, 1.0, "green", 9 * e, 77)
    extra = extra_mug + extra
    if mug_land < t < mug_land + .4:
        extra += PR.clink(mx, my - 50, 1.1, clamp((t - mug_land) / .4), 7)
    # «просили»: к нему подъезжает лист и карандаш
    if t > T_PROSILI - .25:
        u = ease_out(clamp((t - (T_PROSILI - .25)) / .5), 3)
        px = lerp(100, 600, u)
        extra += PR.paper(px, L.TOP_FRONT - 20, 1.0, lerp(-30, -4, u), 130, 170, 52, "blank", .45)
        extra += PR.pencil(px + 30, L.TOP_FRONT - 22, .8, lerp(-80, -12, u))
    body = room(t, "messy", fig, None, extra)
    dx, dy = PR.shake(t, mug_land, 6, .3, 4)
    return f'<g transform="translate({dx:.2f} {dy:.2f})"><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g></g>'


def square_cloud(x, y, u, t):
    """Простое ровное облачко-квадрат: скруглённый квадрат, внутри одна серая ровная плитка (без букв), хвост кружочками вниз-влево."""
    if u <= .01:
        return ""
    k = lib.back_out(clamp(u), 2.0) if u < 1 else 1.0
    o = []
    for j, (dx, dy, r) in enumerate(((-70, 150, 16), (-100, 190, 10), (-122, 222, 6))):
        o.append(lib.shape(ellipse_pts(dx, dy, r, r, 10), "#ffffff", w=3, seed=760 + j))
    o.append(lib.shape(lib.rrect(-120, -110, 120, 120, 26), "#ffffff", blob(lib.rrect(-20, -100, 110, 110, 20), "#eef1f2"), w=4.2, seed=770))
    o.append(lib.shape(lib.rrect(-56, -46, 56, 56, 6), "#b9c2c8", blob(lib.rrect(10, -46, 56, 56, 4), "#a3adb4"), w=3.4, seed=771))
    return f'<g transform="translate({x:.1f} {y + 3 * math.sin(t * 2):.1f}) scale({k:.4f})">{"".join(o)}</g>'


# ═══════════════════════════ s12: участница крупнее, облачко-квадрат, поднос ═══════════════════════════
def frame12(t):
    a = 27.6
    X, y = 470.0, SIT_Y
    push = sm(t, T_VYBIRALI - .1, 30.2)
    s = lerp(1.66, 1.76, clamp((t - a) / 1.6)) + .3 * push
    cx = lerp(560, 590, clamp((t - a) / 1.6)) + 80 * push + 5 * math.sin(t * 1.3)
    cy = lerp(870, 885, clamp((t - a) / 1.6)) + 120 * push + 4 * math.sin(t * 1.7)
    rot = lerp(.8, -.6, clamp((t - a) / 2.6))
    set_ink(s)
    nod = .1 * bump(t, T_PORYADKE, .32) + .07 * bump(t, T_PORYADKE + .3, .3)
    # поправляет очки ближней рукой (28.15–28.85)
    g = bump(t, 28.2, .6)
    ex = dict(P.EXPR["bob"]["calm"], look=(.5, .05))
    ex["closed"] = max(bump(t, 27.75, .16), bump(t, 29.05, .16))
    if t > T_PORYADKE:
        ex = dict(ex, smile=.65, lid=.7)
    tray_u = ease_out(clamp((t - (T_VYBIRALI - .2)) / .55), 3)
    TX = lerp(1250, 700, tray_u)
    TY = L.TOP_FRONT - 4
    if t > T_VYBIRALI - .05:
        ex = dict(P.EXPR["bob"]["think"], look=(.75, .75))
    if t > T_POLEZ - .1:
        ex = dict(P.EXPR["bob"]["calm"], look=(.75, .7), smile=.6)
    arms, hands = {}, {}
    fig0 = P.figure("bob", X, y, PS, ex, **P.pose_kw("sit_desk", X, y, PS, "bob"))
    hd = fig0["head"]
    if g > 0:
        tgt = (lerp(X + 240 * PS * .95, hd[0] + 55 * PS, g), lerp(y - 195 * PS, hd[1] + 100 * PS, g))
        arms["n"] = ("ik", tgt, -1)
        hands["n"] = {"dir": (-.15, -1), "curl": (.0, .75, .85, .85), "spread": .05, "thumb": .5}
    reach = smooth(T_POLEZ - .08, T_POLEZ + .35, t)
    ax, ay = TX - 80, TY - 40
    if reach > 0:
        tgt = (lerp(X + 240 * PS * .95, ax - 55, reach), lerp(y - 195 * PS, ay + 6, reach))
        arms["n"] = ("ik", tgt, -1)
        hands["n"] = {"dir": (1, .15), "curl": (.15 + .25 * reach, .2 + .25 * reach, .25 + .25 * reach, .3 + .25 * reach), "spread": .25, "thumb": .4 * reach}
    fig, info = seated("bob", X, y, t, ex, head_add=nod, arms=arms, hands=hands)
    items = L.desk_items_tidy(t)
    tr = ""
    if tray_u > 0:
        tr = PR.tray(TX, TY, 1.0, 330) + PR.apple(TX - 80, TY - 30, 1.15, -6, 0, 1) + PR.chocolate(TX + 70, TY - 50, .95, 6, 1)
    cu = clamp((t - a) / .3)
    cloud = square_cloud(hd[0] + 210, hd[1] - 240, cu, t)
    body = room(t, "tidy", fig, items + tr, "") + cloud
    return f'<g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>'
