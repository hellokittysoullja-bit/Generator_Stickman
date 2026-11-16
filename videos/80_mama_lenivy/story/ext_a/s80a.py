"""Рилс 80 «Мама была права», группа A: s06, s09, s11, s13, s14, s17.
Время — ТОЛЬКО из shots.json (t0/t1 плана) и voice/words.json (слово по индексу wN); числа в коде — длительности движений.
s06 веер раскадровки: кот лапой раскидывает карточки тремя рывками «такие» (w24), «истории» (w25), «про» (w26);
    «Диму» (w27) — карточка с Димой подлетает к камере и заполняет кадр. Камера: хвост хлёста на входе, наезд в карточку.
s09 чувство: Дима за столом днём; «сразу» (w44) над головой набухает серое облачко; «тоскливо» (w46) морось, стол и окно
    выцветают, плечи опускаются; «тревожно» (w48) молнии, стол дрожит, ручка катится. Камера: дрейф вверх, мини-тряска.
s11 купол: Дима в тёплом куполе телефона; облако внутри тает «чувство»–«пропало» (w56–w57), он выдыхает; «хоть» (w58) облако
    снаружи у края купола ждёт; «минуту» (w60) заглядывает краешком внутрь. Камера: медленный отъезд.
s13 схема на бумаге: «дела» (w67) коробка дела; «откладывают» (w68) фигурка отходит; «сбежать» (w70) убегает, за ней катится
    облачко. Камера: дрейф за фигуркой.
s14 бирка раскалывается: «плохого»–«чувства» (w72–w73) облако обвивает бирку; «лень» (w75) трещина; «ни» … «чём» (w77–w79)
    бирка оказывается картоном и лёгкими кусками падает, Дима выпрямляется и трогает шею. Камера: наезд, толчок и тряска.
s17 две минуты: «делает» (w88) ручка бежит по листу; «первые» (w89) лист отложен; «две» (w90) второй лист, клубок бледнеет.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика."""
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
import people  # noqa: E402
import props as P  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, svg  # noqa: E402

INK = lib.INK
WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SHOTS = {s["id"]: s for s in json.load(open(os.path.join(STORY, "shots.json")))["shots"]}


def ws(i):
    return WORDS[i]["start"]


def we(i):
    return WORDS[i]["end"]


def T0(sid):
    return SHOTS[sid]["t0"]


def T1(sid):
    return SHOTS[sid]["t1"]


def lerp(a, b, u):
    return a + (b - a) * u


def ramp(t, a, d):
    return clamp((t - a) / d)


C_WALL = "#F2E1BF"
C_WALL2 = "#E6CC9C"
C_WALL_EVE = "#D9B98A"
C_WALL_EVE2 = "#B88E62"


def frame_svg(body, cx, cy, s, rot, bg=None, over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg or P.C_PAGE}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def shadow(x, y, rx, op=.13, col="#6B5B3A"):
    return blob(ellipse_pts(x, y, rx, rx * .14, 18), col, op)


def whip_in(t, t0, amp=380.0, dur=.28):
    u = clamp((t - t0 + .06) / dur)
    return amp * (1 - ease_out(u, 3))


def jerk(t, times, dur=.22):
    """Ступени 0 → 1/n → … → 1 рывками на моменты times (с перелётом)."""
    n = len(times)
    v = 0.0
    for c in times:
        u = (t - c) / dur
        if u > 0:
            v += (lib.back_out(min(u, 1.0), 2.2) if u < 1 else 1.0) / n
    return v


def wall(top=-900, bot=3000, c1=C_WALL, c2=C_WALL2):
    g = lib.lin_grad([(0, c1, 1), (1, c2, 1)], 0, 0, 0, 1)
    return f'<path d="M-900 {top}H2600V{bot}H-900Z" fill="url(#{g})"/>'


def floor_band(y, col="#C99A63", col2="#B0824F"):
    g = lib.lin_grad([(0, col, 1), (1, col2, 1)], 0, 0, 0, 1)
    return (f'<path d="M-900 {y:.0f}H2600V3200H-900Z" fill="url(#{g})"/>' +
            line([(-900, y), (2600, y)], 5, INK, taper=.02, wmin=.8, seed=901))


# ═══════════════════════════════ стол Димы (s09, s11, s17) ═══════════════════════════════
DESK_X, DESK_Y, DESK_W = 760.0, 1110.0, 760.0
HIP = (330.0, 1270.0)
SC = .8
FLOOR = 1600.0


def desk_room(t, mode="day", grey=0.0, shake=(0.0, 0.0)):
    """Стена, окно, пол (под фильтром выцветания), возвращает (фон, стол)."""
    o = [wall(c1=C_WALL if mode == "day" else C_WALL_EVE, c2=C_WALL2 if mode == "day" else C_WALL_EVE2)]
    o.append(P.window(250, 860, 380, 520, "day" if mode == "day" else "evening", t, seed=80))
    if mode == "day":
        o.append(P.glow(250, 640, 330, .35, "#FFF4D0"))
    o.append(floor_band(FLOOR))
    bg = "".join(o)
    desk = P.desk(DESK_X + shake[0], DESK_Y + shake[1], DESK_W, 1.0, 150, legs=True, seed=80, leg_h=FLOOR - DESK_Y - 20)
    return bg, desk


def seated(t, expr, pose, lean=0.0, head=0.0, arms=None, hands=None, layers=None, shrug=0.0, x=None, y=None):
    hx, hy = (x if x is not None else HIP[0]), (y if y is not None else HIP[1])
    br = 3 * math.sin(t * 2.3)
    kw = dict(feet=people.sit_kw(hx, hy + br, SC)["feet"], lean_add=lean, head_add=head, shrug=shrug)
    if arms:
        kw["arms"] = arms
    if hands:
        kw["hands"] = hands
    if layers:
        kw["layers"] = layers
    return people.dima(hx, hy + br, SC, expr, pose, **kw)


def chair(x, y, k=1.0):
    o = [P.shape(lib.rrect(x - 110 * k, y - 10 * k, x + 70 * k, y + 22 * k, 8), P.C_WOOD_SH, "", w=3.6, seed=8101)]
    o.append(P.shape(lib.rrect(x - 130 * k, y - 330 * k, x - 96 * k, y + 10 * k, 10), P.C_WOOD, "", w=3.6, seed=8102))
    for lx in (x - 100 * k, x + 50 * k):
        o.append(P.shape(P.rect_pts(lx - 9 * k, y + 20 * k, lx + 9 * k, FLOOR), P.C_WOOD_SH, "", w=3.2, seed=8103 + int(lx)))
    return "".join(o)


EX = people.EXPR["dima"]


def ex(base, **kw):
    d = dict(EX[base]) if isinstance(base, str) else dict(base)
    d.update(kw)
    return d


# ═══════════════════════════════ s09: чувство над головой ═══════════════════════════════
def s09(t):
    lib.dyn_begin()
    a = max(0.0, T0("s09") - .2)
    t_now, t_sad, t_anx = ws(44), ws(46), ws(48)
    grow = ease_out(ramp(t, t_now - .05, .45), 2)
    sad = ease_io(ramp(t, t_sad - .1, .6))
    anx = ramp(t, t_anx - .02, .12)
    sh = P.shake(t, t_anx, 9, .5, 2) if t > t_anx else (0.0, 0.0)
    tremble = (2.5 * anx * math.sin(t * 61), 1.5 * anx * math.cos(t * 53))
    dsh = (sh[0] * .6 + tremble[0], sh[1] * .3 + tremble[1])
    bg, desk = desk_room(t, "day", 0, dsh)
    o = []
    flt = P.desat(.75 * sad)
    # Дима: пишет (ручка в ближней руке), на «тоскливо» плечи опускаются, взгляд вниз; на «тревожно» вздрагивает
    lean = .02 + .05 * math.sin(t * 1.7) * (1 - sad) + .16 * sad - .05 * anx * math.exp(-max(0.0, t - t_anx) * 3)
    expr = ex("focus") if t < t_now else (ex("focus", brows="worry", look=(.1, -.6)) if t < t_sad - .1 else ex("gloom", look=(.2, .6)))
    if t > t_anx:
        expr = ex("gloom", brows="worry", lid=.75, look=(-.2, -.5))
    write = 1 - ease_io(ramp(t, t_now, .3))
    pen_ph = math.sin(t * 9) * write
    fig_b = seated(t, expr, "write", lean, .05 * sad, layers=("legs", "pelvis"), shrug=.5 * sad)
    fig = seated(t, expr, "write", lean, .05 * sad + .02 * pen_ph, layers=("arm_f", "body", "arm_n"), shrug=.5 * sad)
    sheet_x, sheet_y = DESK_X - 140 + dsh[0], DESK_Y - 70 + dsh[1]
    o.append(f'<g {flt}>{bg}{chair(HIP[0], HIP[1] + 20)}{fig_b["svg"]}{desk}'
             f'{P.paper(sheet_x, sheet_y, 1.15, -4, 220, 280, seed=9, kind="lines", sy=.42)}'
             f'{P.mug(DESK_X + 250 + dsh[0], DESK_Y - 60 + dsh[1], .8, col="blue", coffee=True, steam=.6 * (1 - sad), t=t, seed=9)}'
             f'{P.lamp_desk(DESK_X + 150 + dsh[0], DESK_Y - 110 + dsh[1], .9, on=0.0, seed=9)}'
             f'{fig["svg"]}</g>')
    # ручка: в руке, пока пишет; на «тревожно» выпадает и катится по столу
    wr = fig["wrist"]["n"]
    if t < t_anx:
        o.append(f'<g {flt}>{P.pen(wr[0] + 16, wr[1] + 30, .55, 28 + 6 * pen_ph, seed=9)}</g>')
    else:
        u = t - t_anx
        px = wr[0] + 16 + 150 * (1 - math.exp(-u * 2.2))
        fall = ease_in(clamp(u / .12), 2)
        rr = lerp(28, 86 + 7 * math.sin(u * 15) * math.exp(-u * 2), fall)
        o.append(f'<g {flt}>{P.pen(px, lerp(wr[1] + 30, DESK_Y - 46 + dsh[1], fall), .55, rr, seed=9)}</g>')
    # облачко: над головой, набухает на «сразу», моросит на «тоскливо», трещит на «тревожно»
    hx, hy = fig["head"]
    cx, cy = hx + 30 + 10 * math.sin(t * 1.3), hy - 270 + 8 * math.sin(t * 1.9)
    o.append(P.gloom_cloud(cx, cy, 1.15, t, rain=sad, zap=anx, grow=grow, seed=9))
    # камера: дрейф вверх к облаку, мини-тряска на «тревожно»
    pu = ease_io(ramp(t, a, T1("s09") + .2 - a))
    s = lerp(1.36, 1.46, pu)
    ccx = lerp(560, 520, pu) + sh[0]
    ccy = lerp(930, 850, pu) + sh[1]
    return frame_svg("".join(o), ccx, ccy, s, .4 * math.sin(t * 1.1))


# ═══════════════════════════════ s11: купол телефона, облако ждёт снаружи ═══════════════════════════════
DOME = (360.0, FLOOR)
DOME_K = 2.75


def s11(t):
    lib.dyn_begin()
    a = max(0.0, T0("s11") - .2)
    t_feel, t_gone, t_wait, t_min = ws(56), ws(57), ws(58), ws(60)
    melt = ease_io(ramp(t, t_feel, t_gone - t_feel + .25))
    bg, desk = desk_room(t, "day")
    hx, hy = 300.0, HIP[1]
    br = 3 * math.sin(t * 2.3)
    exh = ramp(t, t_gone, .5)
    expr = ex("screen74", lid=.55 + .2 * exh, mouth="o" if 0 < exh < 1 else ("smile" if exh >= 1 else "flat"), open=.2, smile=.5,
              look=(.45, .5), bags=True)
    lean = .04 + .06 * math.sin(math.pi * exh) * -1 + .02 * math.sin(t * 1.4)
    fig = people.dima_phone(hx, hy + br, SC, expr, "phone_chest74", thumb=.6, t=t,
                            feet=people.sit_kw(hx, hy + br, SC)["feet"], lean_add=lean, shrug=.35 * (1 - exh))
    scene = bg + chair(hx, hy + 20) + desk + P.mug(DESK_X + 250, DESK_Y - 60, .8, col="blue", coffee=True, seed=9) + fig["svg"]
    # снаружи купола мир серый, внутри — тёплый: одна сцена дважды, внутренняя под клипом купола
    R = P.dome_r(DOME_K, 1.0) * (1 + .02 * math.sin(t * 5.3))
    dpts = [(DOME[0] + R * math.cos(math.radians(q)), DOME[1] - R * .95 * math.sin(math.radians(q))) for q in range(0, 181, 6)]
    cid = lib.clip_of(dpts)
    o = [f'<g {P.desat(.7)}>{scene}</g>', f'<g clip-path="url(#{cid})">{scene}</g>']
    o.append(P.phone_dome(DOME[0], DOME[1], DOME_K, 1.0, t, seed=11))
    # свет экрана на лице
    w = fig["wrist"]["n"]
    o.append(P.glow(w[0] - 10, w[1] - 90, 130, .45, "#FFE7A3"))
    # облако внутри купола над головой тает (бледнеет, сжимается, клочья вверх)
    hd = fig["head"]
    if melt < 1:
        o.append(P.gloom_cloud(hd[0] + 20, hd[1] - 190 - 40 * melt, .8 * (1 - .5 * melt), t, rain=.3 * (1 - melt), pale=melt,
                               grow=1 - ease_in(ramp(t, t_gone, .35), 2), seed=11))
    # снаружи: облако садится у края купола справа и ждёт; на «минуту» заглядывает краешком внутрь
    q = math.radians(65)
    ox, oy = DOME[0] + (R + 150) * math.cos(q), DOME[1] - (R + 120) * .95 * math.sin(q)
    app = ease_out(ramp(t, t_gone - .1, t_wait - t_gone + .1), 2)
    peek = math.sin(math.pi * clamp((t - t_min) / .9)) if t > t_min else 0.0
    peek = max(peek, ramp(t, t_min, .25) * (1 - ramp(t, t_min + .9, .3)))
    ox += lerp(300, 0, app) - 95 * peek
    oy += lerp(-160, 0, app) + 85 * peek + 10 * math.sin(t * 2.1)
    o.append(P.gloom_cloud(ox, oy, 1.05, t, rain=.5, grow=ease_out(ramp(t, t_gone - .15, .5), 2), seed=12))
    # камера: медленный отъезд, в конце виден край купола и ждущее облако
    pu = ease_io(ramp(t, a, T1("s11") + .2 - a))
    s = lerp(1.5, 1.0, pu)
    cx = lerp(390, 600, pu)
    cy = lerp(1000, 900, pu)
    return frame_svg("".join(o), cx, cy, s, .3 * math.sin(t * 1.2))


# ═══════════════════════════════ s14: бирка была картонной ═══════════════════════════════
HIP14 = (450.0, 1500.0)
SC14 = 1.15


def neck_of(fig, sc):
    hx, hy = fig["head"]
    return hx - 18 * sc, hy + 150 * sc


def s14(t):
    lib.dyn_begin()
    a = max(0.0, T0("s14") - .2)
    t_bad, t_feel, t_lazy, t_ni, t_chem = ws(72), ws(73), ws(75), ws(77), ws(79)
    wrap = ease_io(ramp(t, t_bad - .1, t_feel - t_bad + .35))
    crack = ease_out(ramp(t, t_lazy, .3), 2) * .75 + .25 * ease_out(ramp(t, t_ni - .05, .1), 2)
    brk = ramp(t, t_ni + .02, .85)
    up = ease_out(ramp(t, t_ni + .05, .5), 2)
    touch = ease_io(ramp(t, t_chem - .05, .4))
    o = [wall(c1="#F3E2C2", c2="#E2C795")]
    o.append(P.window(860, 1020, 360, 520, "day", t, seed=14))
    o.append(P.glow(860, 780, 320, .3, "#FFF4D0"))
    o.append(floor_band(HIP14[1] + 590 * SC14))
    # Дима крупно (ноги уходят за низ кадра): под биркой согнут, голова вниз; после раскола выпрямляется, ближняя рука к шее
    bend = (.24 + .03 * math.sin(t * 2.6)) * (1 - up) + .02 * wrap * (1 - up)
    hx, hy = HIP14
    expr = ex("gloom", look=(.2, .7)) if t < t_ni else ex("surprise", look=(.1, .55), open=.3)
    if t > t_chem + .2:
        expr = ex("relief78", look=(.2, .5))
    feet = people.stand_kw(hx, hy, SC14)["feet"]
    pre = people.dima(hx, hy, SC14, expr, None, lean_add=bend, head_add=.16 * (1 - up), shrug=.45 * (1 - up), feet=feet)
    nk = neck_of(pre, SC14)
    arms = {"f": ("ang", .22 + .05 * math.sin(t * 2), .25), "n": ("ang", -.05, .3)}
    hands = {}
    if touch > 0:
        tgt = (nk[0] + 45, nk[1] + 85)
        rest = (hx + 120 * SC14, hy - 40 * SC14)
        arms["n"] = ("ik", (lerp(rest[0], tgt[0], touch), lerp(rest[1], tgt[1], touch)), -1)
        hands = {"n": {"dir": (-.3, -1), "curl": (.15, .2, .25, .3), "spread": .12, "thumb": .2}}
    fig = people.dima(hx, hy, SC14, expr, None, lean_add=bend, head_add=.16 * (1 - up), shrug=.45 * (1 - up), arms=arms, hands=hands,
                      layers=("legs", "pelvis", "arm_f", "body") if touch > 0 else None, feet=feet)
    arm = people.dima(hx, hy, SC14, expr, None, lean_add=bend, head_add=.16 * (1 - up), shrug=.45 * (1 - up), arms=arms, hands=hands,
                      layers=("arm_n",), feet=feet) if touch > 0 else {"svg": ""}
    nk = neck_of(fig, SC14)
    o.append(fig["svg"])
    # бирка: висит на шее, тянет вниз (качается тяжело); облако обвивает; трещина на «лень»; на «ни при чём» — картон
    sw = 5 * math.sin(t * 1.9) * (1 - wrap * .6) + 3 * math.sin(t * 7) * crack * (1 - brk)
    k_tag = 1.3
    tc = P.iron_tag_center(nk[0], nk[1], k_tag, sw, 95)
    if wrap > 0 and brk < 1:   # облако позади бирки
        cloud_k = lerp(1.2, 1.15, wrap) * (1 - .6 * ease_in(brk, 2))
        cx_ = lerp(tc[0] - 320, tc[0], wrap)
        cy_ = lerp(tc[1] - 420, tc[1] + 10, wrap)
        o.append(P.gloom_cloud(cx_, cy_, cloud_k, t, zap=.3 * wrap * (1 - brk), pale=brk, grow=1 - ease_in(clamp(brk * 2.2), 2), seed=14))
    o.append(P.iron_tag(nk[0], nk[1], k_tag, sw, crack, seed=14, cord=95, break_u=brk, card=ease_in(brk * 3, 1), fall=700, t=t))
    if wrap > .3 and brk < .4:   # клуб облака спереди, обнимает низ бирки
        fu = clamp((wrap - .3) / .7) * (1 - brk / .4)
        o.append(P.gloom_cloud(tc[0] - 60, tc[1] + 105, .5 * fu, t, seed=15))
        o.append(P.gloom_cloud(tc[0] + 95, tc[1] - 40, .38 * fu, t, seed=16))
    o.append(arm["svg"])
    # штрихи удара на «ни»
    u = ramp(t, t_ni, .35)
    if 0 < u < 1:
        for j in range(7):
            ang = math.radians(-180 + 360 * j / 7 + 12)
            r1 = 150 + 110 * ease_out(u, 2)
            o.append(line([(tc[0] + math.cos(ang) * r1, tc[1] + math.sin(ang) * r1),
                           (tc[0] + math.cos(ang) * (r1 + 70 * (1 - u)), tc[1] + math.sin(ang) * (r1 + 70 * (1 - u)))],
                          8 * (1 - u), INK, taper=.6, wmin=.1, seed=1400 + j))
    # камера: наезд к бирке; толчок и тряска на «ни при чём», потом чуть шире — видно, как он выпрямился
    pu = ease_io(ramp(t, a, t_ni - a))
    back = ease_io(ramp(t, t_ni + .1, .8))
    punch = .09 * math.exp(-max(0.0, t - t_ni) * 5) * ease_out(ramp(t, t_ni, .06), 2)
    sh = P.shake(t, t_ni, 12, .4, 4)
    s = lerp(1.0, 1.2, pu) - .12 * back + punch
    cx = lerp(540, tc[0] + 60, pu) * (1 - back) + 560 * back + sh[0]
    cy = lerp(1080, tc[1] + 60, pu) * (1 - back) + 1080 * back + sh[1]
    return frame_svg("".join(o), cx, cy, s, .3 * math.sin(t * 1.3), bg="#F3E2C2")


# ═══════════════════════════════ s06: веер раскадровки ═══════════════════════════════
PIV6 = (470.0, 1240.0)
K6 = 2.45
R6 = 330.0
N6 = 5
HERO6 = 2


def table_top(t, seed=6):
    """Стол сверху: тёплые доски вдоль кадра, мягкий свет лампы."""
    o = [f'<path d="M-900 -900H2600V3200H-900Z" fill="{P.C_WOOD}"/>']
    for j in range(-6, 22):
        x = j * 170 + 30 * math.sin(j * 1.7)
        o.append(line([(x, -900), (x + 8, 3200)], 4, P.C_WOOD_SH, taper=.02, wmin=.8, seed=600 + j + seed, op=.8))
        for m in range(3):
            y0 = -400 + ((j * 397 + m * 811) % 2600)
            o.append(line(P._wavy(x + 40, x + 120, y0, 610 + j * 3 + m, amp=5, per=60) if hasattr(P, "_wavy") else
                          [(x + 40, y0), (x + 120, y0 + 4)], 2.4, P.C_WOOD_HI, taper=.4, wmin=.3, seed=620 + j * 3 + m, op=.7))
    o.append(P.glow(560, 760, 760, .35, "#FFE7A3"))
    # кружка сверху и карандаш — стол живой, верх кадра не пустой
    mx, my = 820.0, 560.0
    o.append(blob(ellipse_pts(mx + 18, my + 22, 108, 104, 24), "#3A2A18", .22))
    o.append(P.shape(lib.T(lib.rrect(-26, -16, 26, 16, 12), mx + 118, my + 6, 1.0, 10), "#D0553F", "", w=4.0, seed=631))
    o.append(P.shape(ellipse_pts(mx, my, 100, 100, 28), "#D0553F", blob(ellipse_pts(mx + 20, my + 18, 86, 86, 24), "#9E3A2A", .6), w=4.4, seed=632))
    o.append(P.shape(ellipse_pts(mx, my, 80, 80, 26), P.C_COFFEE, blob(ellipse_pts(mx - 26, my - 24, 22, 14, 12), "#8A5E40", .8), w=3.0, seed=633))
    o.append(P.pencil(250, 520, 1.6, 28))
    return "".join(o)


def card6_pose(t, u, j):
    a = -48 + (j / (N6 - 1)) * 112 * u + 1.2 * math.sin(t * 3 + j)
    ar = math.radians(a)
    return PIV6[0] + math.sin(ar) * R6, PIV6[1] - math.cos(ar) * R6, a


def s06(t):
    lib.dyn_begin()
    a = max(0.0, T0("s06") - .2)
    jerks = [ws(24), ws(25), ws(26)]
    t_d = ws(27)
    u = .08 + .92 * jerk(t, jerks, .26)
    u += .03 * math.sin(t * 7) * (1 - ramp(t, jerks[0], .1))
    lift = ease_io(ramp(t, t_d - .02, .34))
    o = [table_top(t)]
    # тени и карточки (кроме подлетающей)
    for j in range(N6):
        if j == HERO6 and lift > 0:
            continue
        cx, cy, ang = card6_pose(t, u, j)
        o.append(P.story_card(cx, cy, K6, ang, i=j, seed=6))
    # лапа кота справа: подушечка на верхней карточке, тянет её на каждом рывке
    cx, cy, ang = card6_pose(t, u, N6 - 1)
    ar = math.radians(ang)
    tip = (cx + (40 * math.cos(ar) - (-60) * math.sin(ar)) * K6, cy + (40 * math.sin(ar) + (-60) * math.cos(ar)) * K6)
    pr = sum(math.sin(math.pi * clamp((t - c + .05) / .3)) for c in jerks if 0 < t - c + .05 < .3)
    away = ease_in(ramp(t, t_d - .1, .3), 2)
    tip = (tip[0] + 120 * away, tip[1] - 40 * pr * 0 - 60 * away)
    base = (tip[0] + 360 + 30 * pr, tip[1] + 470 + 30 * math.sin(t * 2))
    o.append(blob(ellipse_pts(tip[0] + 20, tip[1] + 30, 70, 40, 14), "#3A2A18", .18))
    o.append(people.cat_forearm(base, tip, 2.4, claw=0.0, seed=6))
    # карточка «Диму»: подлетает к камере и заполняет кадр
    if lift > 0:
        c0 = card6_pose(t, u, HERO6)
        cam_c = (560.0, 900.0)
        bx = lerp(c0[0], cam_c[0], lift)
        by = lerp(c0[1], cam_c[1], lift) - 60 * math.sin(math.pi * lift)
        kk = K6 * lerp(1.0, 2.15, lift)
        rr = lerp(c0[2], 0, lift) + 4 * math.sin(math.pi * lift)
        o.append(P.story_card(bx, by, kk, rr, i=HERO6, seed=6, lift=lift))
    # камера: хвост хлёста на входе, лёгкий наезд, на «Диму» — толчок
    wx = whip_in(t, T0("s06"), 230, .3)
    pu = ease_io(ramp(t, a, T1("s06") + .2 - a))
    punch = .06 * math.exp(-max(0.0, t - t_d - .3) * 4) * ease_out(ramp(t, t_d + .25, .08), 2)
    s = lerp(1.0, 1.06, pu) + punch
    return frame_svg("".join(o), 560 + wx + 10 * math.sin(t * 1.4), 1000 - 40 * pu, s * 1.08, -1.2 + .6 * pu)


# ═══════════════════════════════ s13: схема «бежит от облака» ═══════════════════════════════
GROUND13 = 1180.0
BOX13 = (330.0, GROUND13)
SC13 = .55


def grid_paper(col="#F8F0D8", grid="#C9D6E6"):
    d = "".join(f"M-900 {i * 60}H2600" for i in range(-16, 60)) + "".join(f"M{i * 60} -900V3400" for i in range(-16, 50))
    return (f'<path d="M-900 -900H2600V3400H-900Z" fill="{col}"/>'
            f'<path d="{d}" stroke="{grid}" stroke-width="2" fill="none"/>' +
            line([(-900, 0), (2600, 0)], 0.1, col))


def ink_box(x, y, k=1.0, u=1.0, seed=0):
    """Коробка дела тушью (x, y — середина дна), рисуется штрихами по u."""
    if u <= 0:
        return ""
    w, h, d = 200 * k, 170 * k, 70 * k
    o = []
    fr = [(x - w / 2, y, 1), (x + w / 2, y, 1), (x + w / 2, y - h, 1), (x - w / 2, y - h, 1)]
    o.append(P.shape(fr, "#F2DDB0", blob([(x + w / 2 - 50 * k, y, 1), (x + w / 2, y, 1), (x + w / 2, y - h, 1), (x + w / 2 - 50 * k, y - h, 1)], "#E3C690"),
                     w=5 * k, seed=1300 + seed))
    top = [(x - w / 2, y - h, 1), (x + w / 2, y - h, 1), (x + w / 2 + d, y - h - d * .7, 1), (x - w / 2 + d, y - h - d * .7, 1)]
    o.append(P.shape(top, "#F7E7C2", "", w=5 * k, seed=1301 + seed))
    side = [(x + w / 2, y, 1), (x + w / 2 + d, y - d * .7, 1), (x + w / 2 + d, y - h - d * .7, 1), (x + w / 2, y - h, 1)]
    o.append(P.shape(side, "#D9B87E", "", w=5 * k, seed=1302 + seed))
    o.append(line([(x - 30 * k, y - h), (x + d - 30 * k, y - h - d * .7)], 3.4 * k, "#9C7A48", seed=1303 + seed))
    o.append(line([(x - w / 2 + 20 * k, y - h * .55), (x + w / 2 - 20 * k, y - h * .55)], 3.4 * k, "#9C7A48", taper=.3, wmin=.4, seed=1304 + seed))
    g = lib.back_out(clamp(u), 1.8)
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({g:.4f}) translate({-x:.1f} {-y:.1f})">{"".join(o)}</g>'


def silhouette(svg_):
    i = "sil80"
    if not any(f'id="{i}"' in x for x in lib.DEFS):
        lib.DEFS.append(f'<filter id="{i}" x="-20%" y="-20%" width="140%" height="140%"><feColorMatrix type="matrix" '
                        f'values="0 0 0 0 .18 0 0 0 0 .22 0 0 0 0 .34 0 0 0 1 0"/></filter>')
    return f'<g filter="url(#{i})">{svg_}</g>'


def fig13_x(t):
    t_off, t_run = ws(68), ws(70)
    x0 = 660.0
    if t < t_off:
        return x0, 0.0, 0.0
    if t < t_run:
        d = 240 * (t - t_off) - 80 * (1 - math.exp(-(t - t_off) * 3)) / 3 * 3
        return x0 + d, d, 1.0
    d1 = 240 * (t_run - t_off) - 80 * (1 - math.exp(-(t_run - t_off) * 3))
    u = t - t_run
    d = d1 + 760 * u - 520 * (1 - math.exp(-u * 4)) / 4
    return x0 + d, d, 2.0


def s13(t):
    lib.dyn_begin()
    a = max(0.0, T0("s13") - .2)
    t_task, t_off, t_run = ws(67), ws(68), ws(70)
    o = [grid_paper()]
    o.append(line([(-900, GROUND13), (2600, GROUND13 + 4)], 5, "#2E3A5C", taper=.02, wmin=.8, seed=1310))
    for j in range(-6, 30):   # штриховка земли
        x = j * 90
        o.append(line([(x, GROUND13 + 8), (x - 30, GROUND13 + 40)], 3, "#2E3A5C", taper=.3, wmin=.4, seed=1320 + j, op=.55))
    # коробка дела: проявляется на «дела» (до него — контур тонким карандашом)
    bu = ease_out(ramp(t, t_task - .08, .3), 2)
    o.append(ink_box(BOX13[0], BOX13[1], 1.35, .35 + .65 * bu, seed=13))
    fx, dist, mode = fig13_x(t)
    # след: штрих-пунктир от коробки к фигурке
    if dist > 20:
        o.append(P.dash_path([(BOX13[0] + 200, GROUND13 + 22), (fx - 40, GROUND13 + 22)], 1.0, w=5, col="#2E3A5C", gap=24, dash=14, seed=1330))
    # фигурка Димы силуэтом: стоит у коробки лицом к ней; «откладывают» — разворачивается и уходит; «сбежать» — бежит
    hip_y = GROUND13 - 586 * SC13
    if mode == 0:
        feet = people.stand_kw(fx, hip_y, SC13)["feet"]
        fig = people.dima(fx, hip_y + 2 * math.sin(t * 3), SC13, ex("gloom"), None, feet=feet, flip=True,
                          lean_add=.04 * math.sin(t * 2.4), arms={"f": ("ang", .15, .2), "n": ("ang", -.25 + .2 * bu, .4)})
    else:
        stride = 230.0 if mode == 1 else 330.0
        ph = dist / (stride * SC13 * 2) + .1
        wk = people.walk_kw(fx, hip_y, SC13, ph, stride=stride, lift=60 if mode == 1 else 95)
        sw = math.sin(2 * math.pi * ph)
        amp = .3 if mode == 1 else .55
        el = .35 if mode == 1 else 1.2
        arms = {"f": ("ang", .1 + amp * sw, el), "n": ("ang", -.05 - amp * sw, el)}
        fig = people.dima(fx, wk["hip"][1], SC13, ex("gloom") if mode == 1 else ex("scared"), None, feet=wk["feet"],
                          lean_add=.08 if mode == 1 else .26, arms=arms)
    o.append(silhouette(fig["svg"]))
    # облачко: сидит над коробкой с «дела»; на «сбежать» катится за фигуркой (коробка остаётся на месте)
    cg = ease_out(ramp(t, t_task + .05, .35), 2)
    roll = ease_io(ramp(t, t_run - .25, .5))
    cx = lerp(BOX13[0] + 40, fx - 290, roll)
    cy = lerp(BOX13[1] - 420, GROUND13 - 140, roll) + 10 * math.sin(t * 4)
    rot = -40 * roll * math.sin(t * 6) * .3 - 60 * (t - t_run) * roll
    cl = P.gloom_cloud(cx, cy, 1.05 - .2 * roll, t, rain=.4 * (1 - roll), zap=.5 * roll, grow=cg, seed=13)
    o.append(f'<g transform="rotate({rot:.2f} {cx:.1f} {cy:.1f})">{cl}</g>')
    if roll > .2:   # штрихи скорости за облаком
        o.append(P.speed_arcs(cx - 170, cy, 1.0, roll, t, seed=13, n=3, ang=180.0))
        o.append(P.speed_arcs(fx - 120, hip_y - 60, .8, roll, t, seed=14, n=3, ang=180.0))
    # камера: дрейф за фигуркой
    pu = ease_io(ramp(t, a, T1("s13") + .2 - a))
    ccx = max(560.0, lerp(560, fx - 170 + 110 * ramp(t, t_run - .2, .5), ramp(t, t_off, .6)))
    return frame_svg("".join(o), ccx, 960 - 20 * pu, 1.3 + .05 * pu, .3 * math.sin(t * 1.3))


# ═══════════════════════════════ s17: первые две минуты ═══════════════════════════════
def s17(t):
    lib.dyn_begin()
    a = max(0.0, T0("s17") - .2)
    t_do, t_first, t_two = ws(88), ws(89), ws(90)
    bg, desk = desk_room(t, "evening")
    o = [bg, chair(HIP[0], HIP[1] + 20)]
    # лампа горит тёплым кругом
    lamp = P.lamp_desk(DESK_X + 300, DESK_Y - 130, 1.0, on=1.0, seed=17)
    # лист 1 пишется с «делает» до «первые», потом уезжает влево-вверх на стопку; лист 2 — с «две»
    w1 = .12 + .88 * ease_io(ramp(t, t_do, t_first - t_do + .02))
    w1 += .05 * math.sin(t * 9) * 0
    slide = ease_io(ramp(t, t_first, .3))
    w2 = .25 * ease_out(ramp(t, t_two - .05, (T1("s17") + .2) - t_two), 1.4) if t > t_two - .05 else 0.0
    SX, SY = DESK_X - 120, DESK_Y - 72
    s1 = (lerp(SX, SX - 40, slide), lerp(SY, SY - 60, slide), lerp(-4, -14, slide))
    sheets = P.scribble_sheet(SX + 20 - 40 * slide, SY - 70, 1.2, 1.0, -16, seed=170, w=240, h=320, sy=.6) if slide > .0 else ""
    if slide > .6:   # второй лист лёг на место первого
        new_in = ease_out(ramp(t, t_first + .18, .25), 2)
        sheets += P.scribble_sheet(SX + 60 * (1 - new_in), SY + 10 * (1 - new_in), 1.2, w2, -4, seed=171, w=240, h=320, sy=.6)
        tip = P.scribble_tip(SX + 60 * (1 - new_in), SY + 10 * (1 - new_in), 1.2, w2, -4, w=240, h=320, sy=.6)
    else:
        sheets += P.scribble_sheet(s1[0], s1[1], 1.2, w1, s1[2], seed=172, w=240, h=320, sy=.6)
        tip = P.scribble_tip(s1[0], s1[1], 1.2, w1, s1[2], w=240, h=320, sy=.6)
    if slide > 0 and slide < 1:
        tip = (tip[0] + 30 * math.sin(math.pi * slide), tip[1] - 40 * math.sin(math.pi * slide))
    # клубок-облачко на углу стола: на «две» бледнеет
    pale = ease_io(ramp(t, t_two, .6))
    ball = P.gloom_cloud(DESK_X + 105, DESK_Y - 100 + 4 * math.sin(t * 2), 1.15, t, shrink=1.0, pale=pale, seed=17,
                         grow=1 - .35 * pale)
    # Дима пишет: ближняя кисть держит ручку у кончика
    jit = 3 * math.sin(t * 23)
    wr = (tip[0] - 52, tip[1] - 28 + jit * .3)
    arms = {"n": ("ik", wr, -1), "f": ("ik", (SX + 70 + 4 * math.sin(t * 2), SY - 105), -1)}
    hands = {"n": {"curl": (.55, .6, .7, .75), "thumb": .5, "dir": (.85, .5)}, "f": {"curl": (.35, .4, .45, .5), "thumb": .35, "dir": (.9, .55)}}
    expr = ex("focus", look=(.6, .7), bags=False)
    if t > t_two:
        expr = ex("focus", look=(.6, .7), bags=False, brows="calm")
    fig_b = seated(t, expr, "write", .1, .08, layers=("legs", "pelvis"))
    fig = seated(t, expr, "write", .1, .08, arms=arms, hands=hands, layers=("arm_f", "body"))
    arm = seated(t, expr, "write", .1, .08, arms=arms, hands=hands, layers=("arm_n",))
    o.append(fig_b["svg"])
    o.append(desk)
    o.append(lamp)
    o.append(sheets)
    o.append(ball)
    o.append(fig["svg"])
    # ручка: кончик на строке, наклон к руке
    o.append(P.pen(tip[0] - 26, tip[1] - 62, .62, 25 + 4 * math.sin(t * 9), seed=17))
    o.append(arm["svg"])
    o.append(P.glow(DESK_X + 160, DESK_Y - 90, 420, .55, "#FFD98A"))
    # камера: дрейф вдоль строк
    pu = ease_io(ramp(t, a, T1("s17") + .2 - a))
    return frame_svg("".join(o), lerp(620, 680, pu), lerp(1060, 1040, pu), lerp(1.74, 1.82, pu), .3 * math.sin(t * 1.2))


SCENES = {"s17": s17, "s13": s13, "s06": s06, "s14": s14, "s09": s09, "s11": s11}


def frame(sid, t):
    return SCENES[sid](t)
