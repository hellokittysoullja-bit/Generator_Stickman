"""Рилс 76 «Рассказал о цели», группа A: графика, факт, предметы — s03, s06, s12, s13, s14, s15, s16.
Время — ТОЛЬКО из shots.json (t0/t1 плана) и voice/words.json (слово по индексу wN); числа в коде — длительности движений.
(Проверка сдвига: переменные окружения A76_WORDS / A76_SHOTS подменяют файлы.)
s03 средне-крупно: Дима на матрасе, кубок на груди тяжелеет с «И» (w9), «этого» (w13) — вдавливает, матрас проседает, чипсы выскальзывают.
s06 (whip) бумага: «пять» (w25) пять конвертов выпрыгивают дугой, «нельзя» (w29) сургуч по очереди, «говорить» (w30) лапа кота прижимает.
s12 (whip) голова-контур: «хвалят» (w59) искорки летят в ухо, «цель» (w61) чистый лист на полочке вспыхивает золотом.
s13 та же голова: печать опускается, «засчитывает» (w63) — шмяк, галочка; «будто…дело» (w65–w66) наезд на пустой лист;
    «сделано» (w68) лист уезжает в картотеку, ящик захлопывается, звёздочка.
s14 (whip) город на закате в окне аудитории (w70), «студенты» (w71) — отъезд в аудиторию: два стола по трое, «рассказали» (w73)
    левые рассказывают преподавателю, правые молча пишут.
s15 та же аудитория: «одобрение» (w78) преподаватель хлопает, левые откидываются и закрывают тетради; «потом…ею» (w79–w81) тени
    ползут по полу, лампа левых гаснет, правые пишут.
s16 «меньше» (w82) левый стол пуст, блокнот; переезд вправо: «промолчал» (w85) правые пишут, студентка подносит палец к губам.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Люди и кот — common/people.py, cat.py; предметы — common/props.py."""
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
import people as PP  # noqa: E402
import props as P  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, rect_pts, shape, svg  # noqa: E402

INK = lib.INK
WORDS = json.load(open(os.environ.get("A76_WORDS") or os.path.join(STORY, "voice", "words.json")))
SHOTS = {s["id"]: s for s in json.load(open(os.environ.get("A76_SHOTS") or os.path.join(STORY, "shots.json")))["shots"]}


def ws(i):
    return WORDS[i]["start"]


def we(i):
    return WORDS[i]["end"]


def T0(sid):
    return SHOTS[sid]["t0"]


def T1(sid):
    return SHOTS[sid]["t1"]


def A(sid):
    return max(0.0, T0(sid) - .2)


def lerp(a, b, u):
    return a + (b - a) * u


def ramp(t, a, d):
    return clamp((t - a) / d)


def paper_bg(col=None, grid="#E3D9BE"):
    d = "".join(f"M-900 {i * 64}H2600" for i in range(-14, 80)) + "".join(f"M{i * 64} -900V5000" for i in range(-14, 42))
    return (f'<path d="M-900 -900H2600V5000H-900Z" fill="{col or P.C_PAGE}"/>'
            f'<path d="{d}" stroke="{grid}" stroke-width="2" fill="none"/>')


def frame_svg(body, cx, cy, s, rot, bg=None, over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg or P.C_PAGE}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def shadow(x, y, rx, op=.13, col="#6B5B3A"):
    return blob(ellipse_pts(x, y, rx, rx * .14, 18), col, op)


def whip_in(t, t0, amp=380.0, dur=.28):
    """Хвост хлёста внутри клипа: камера влетает со стороны и тормозит без остановки (ease out)."""
    u = clamp((t - t0 + .06) / dur)
    return amp * (1 - ease_out(u, 3))


def impact(x, y, u, r0=60.0, n=6, a0=-170.0, span=160.0, w=7.0, sd=0, sy=.6, col=None):
    if u <= 0 or u >= 1:
        return ""
    o = []
    for j in range(n):
        a = math.radians(a0 + span * j / max(1, n - 1))
        r1 = r0 + 60 * ease_out(u, 2)
        o.append(line([(x + math.cos(a) * r1, y + math.sin(a) * r1 * sy), (x + math.cos(a) * (r1 + 50 * (1 - u)), y + math.sin(a) * (r1 + 50 * (1 - u)) * sy)],
                      w * (1 - u), col or INK, taper=.6, wmin=.1, seed=sd + j))
    return "".join(o)


def shake_sum(t, times, amp, dur=.25):
    dx = dy = 0.0
    for i, c in enumerate(times):
        a, b = P.shake(t, c, amp, dur, seed=i)
        dx += a
        dy += b
    return dx, dy


# ═══════════════════════════════ s06: пять конвертов ═══════════════════════════════
ENV_K = 1.18


def env_pos(i):
    a = math.radians(-160 + 35 * i)
    return 540 + 380 * math.cos(a), 1060 + 520 * math.sin(a), (-160 + 35 * i + 90) * .3


def s06(t):
    lib.dyn_begin()
    sid = "s06"
    a = A(sid)
    t_five = ws(25)
    step = min(.2, (ws(27) - t_five) / 5)
    pops = [t_five - .05 + step * i for i in range(5)]
    sa, sb = ws(29), ws(30)
    seals = [sa + (sb - sa) * i / 5 for i in range(5)]
    t_paw = ws(30)
    o = [paper_bg()]
    land = []
    for i in range(5):
        x, y, r = env_pos(i)
        tp = pops[i]
        if t < tp:
            continue
        sx, sy = P.pop(t, tp, .32, .35, 2.2, 6.0)
        hop = -170 * math.sin(math.pi * clamp((t - tp) / .32)) if t - tp < .32 else 0.0
        bob = 6 * math.sin((t - tp) * 5 + i) * clamp((t - tp - .3) / .3)
        su = ramp(t, seals[i] - .1, .2)
        sq = P.squash(t, seals[i], .14, 3.0, 8.0)
        press = 0.0
        if i == 4:
            press = ease_out(ramp(t, t_paw + .12, .1), 2)
            sq = (sq[0] * (1 + .05 * press), sq[1] * (1 - .07 * press))
        shiver = ramp(t, t_paw, .2) * (.6 if i == 4 else 1.0)
        o.append(shadow(x, y + 66 * ENV_K + 10, 110 * (1 - .3 * clamp(-hop / 150)), .14))
        env = P.sealed_envelope(0, 0, ENV_K, su, shiver, t, seed=i, rot=r + 4 * math.sin((t - tp) * 3 + i) * (1 - su))
        o.append(f'<g transform="translate({x:.1f} {y + hop + bob:.1f}) scale({sx * sq[0]:.4f} {sy * sq[1]:.4f})">{env}</g>')
        o.append(impact(x, y - 20, (t - tp) / .3, 90, 6, -160, 140, 7, sd=60 + i * 7))
        o.append(impact(x, y - 10, (t - seals[i] + .02) / .28, 70, 5, -150, 120, 6, sd=120 + i * 7, col=P.C_WAX_SH))
        land.append(seals[i])
    # лапа кота справа: входит к «говорить», прижимает последний конверт
    pin = ease_out(ramp(t, t_paw - .2, .32), 3)
    if pin > 0:
        x4, y4, _ = env_pos(4)
        tip = (lerp(1320, x4 + 40, pin), lerp(560, y4 - 40, pin) + 14 * ease_out(ramp(t, t_paw + .12, .1), 2))
        o.append(PP.cat_forearm((1380, 420), tip, 1.7, 0.0, seed=6))
    wx = whip_in(t, T0(sid), 420)
    dx, dy = shake_sum(t, seals, 7, .22)
    pdx, pdy = P.shake(t, t_paw + .12, 9, .25, 3)
    pu = ease_io(ramp(t, a, T1(sid) + .2 - a))
    s = 1.02 + .05 * pu
    cx = 520 + 40 * pu - wx + dx + pdx
    cy = 900 - 20 * pu + dy + pdy
    return frame_svg("".join(o), cx, cy, s, -.8 + 1.3 * pu)


# ═══════════════════════════════ голова-контур: s12, s13 ═══════════════════════════════
HX, HY, HK = 540.0, 720.0, 1.22


def gold_sheet(x, y, k, glow_u, t, seed=0, rot=0.0, seal_u=0.0, hop=0.0):
    """Чистый лист стоя на полочке (x, y — центр низа листа), может вспыхнуть золотом и нести оттиск печати."""
    col = lib.mix(P.C_PAGE, "#FFE07A", .55 * glow_u)
    o = []
    if glow_u > .01:
        o.append(P.glow(x, y - 100 * k, 190 * k, .9 * glow_u, "#FFD45A"))
    o.append(P.paper(x, y - 100 * k + hop, k, rot, 150, 200, seed, "blank", col=col))
    if seal_u > 0:
        o.append(P.check_seal(x, y - 104 * k + hop, k * .78, seal_u, seed))
    return "".join(o)


def gold_star(x, y, r, rot=0.0, col="#F2B632"):
    """Золотая четырёхлучевая искра с контуром тушью (видна на кремовой бумаге)."""
    if r < 1:
        return ""
    pts = []
    for j in range(8):
        a = math.radians(rot + 45 * j)
        rr = r if j % 2 == 0 else r * .3
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)) + ((1,) if j % 2 == 0 else ()))
    return shape(pts, col, blob(ellipse_pts(x - r * .08, y - r * .08, r * .14, r * .14, 8), "#FFF3C4"), w=max(1.6, r * .09), seed=int(x + y) % 997)


def sparks_to(x0, y0, x1, y1, t, t_a, n=9, dur=.55, spread=.42, seed=0, k=1.0):
    """Золотые искорки и мелкое конфетти летят по дуге из (x0, y0) в (x1, y1), каждая со своей задержкой."""
    rs = P._rs(76000 + seed)
    o = []
    for j in range(n):
        d0 = t_a + j * spread / n
        u = (t - d0) / dur
        if u <= 0 or u >= 1.08:
            continue
        u = clamp(u)
        e = ease_in(u, 1.6)
        bx = rs.uniform(-160, 160) * k
        by = rs.uniform(-120, 120) * k
        px = lerp(x0 + bx, x1, e) + math.sin(math.pi * u) * rs.uniform(-60, 60) * k
        py = lerp(y0 + by, y1, e) - math.sin(math.pi * u) * rs.uniform(30, 110) * k
        sc = (1 - .7 * e)
        if j % 3 == 2:
            col = P.CONFETTI_COLS[j % len(P.CONFETTI_COLS)]
            ang = t * 9 + j
            hw, hh = 14 * k * sc, 9 * k * sc * max(.15, abs(math.cos(t * 11 + j)))
            ca, sa = math.cos(ang), math.sin(ang)
            pts = [(px + dx_ * ca - dy_ * sa, py + dx_ * sa + dy_ * ca) for dx_, dy_ in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]
            o.append(blob([p + (1,) for p in pts], col))
        else:
            o.append(gold_star(px, py, 34 * k * sc * (.8 + .2 * math.sin(t * 20 + j)), t * 160 + j * 30))
    return "".join(o)


def s12(t):
    lib.dyn_begin()
    sid = "s12"
    a = A(sid)
    t_praise, t_goal = ws(59), ws(61)
    an = P.head_anchor(HX, HY, HK)
    ex, ey = an["ear"]
    sh0, sh1, shy = an["shelf"]
    sxp = (sh0 + sh1) / 2 + 30 * HK
    o = [paper_bg()]
    du = lerp(.45, 1.0, ease_out(ramp(t, a, .5), 2))
    o.append(P.head_outline(HX, HY, HK, du, seed=12, t=t))
    gu = ease_out(ramp(t, t_goal, .18), 2) * (1 - .25 * ramp(t, t_goal + .45, .4))
    hop = -18 * math.sin(math.pi * ramp(t, t_goal, .22))
    sway = 3 * math.sin(t * 4)
    o.append(gold_sheet(sxp, shy, HK * .8, gu, t, 12, sway, hop=hop))
    if gu > .05:
        o.append(P.sparkles(sxp, shy - 100 * HK, HK * 1.3, gu, t, seed=12, n=6, r=150))
    # искорки-хлопки снаружи летят в ухо: с самого начала плана редкие, на «хвалят» — густо
    o.append(sparks_to(ex - 520, ey - 520, ex - 10, ey + 6, t, a - .3, 6, 1.2, .5, seed=1, k=1.8))
    o.append(sparks_to(ex - 560, ey - 420, ex - 10, ey + 6, t, t_praise - .12, 16, .45, .5, seed=2, k=1.9))
    # мелкие «хлопки» у входа в ухо
    for j in range(3):
        o.append(P.click(ex - 30, ey, 1.3, ramp(t, t_praise + .3 + j * .12, .2), seed=j))
    wx = whip_in(t, T0(sid), 420)
    pu = ease_io(ramp(t, t_praise - .1, t_goal - t_praise + .2))
    back = ease_io(ramp(t, t_goal, .4))
    fx, fy = lerp(HX + 10, lerp(ex - 40, sxp - 60, back), pu), lerp(HY + 170, lerp(ey + 60, shy - 30, back), pu)
    s = lerp(1.16, 1.5, pu) - .1 * back + .03 * ease_io(ramp(t, a, .8))
    dx, dy = P.shake(t, t_goal, 8, .25, 2)
    return frame_svg("".join(o), fx - wx + dx, fy + dy, s, lerp(-1.2, .6, pu))


HK13 = 1.22


def s13(t):
    lib.dyn_begin()
    sid = "s13"
    a = A(sid)
    t_slam = lerp(ws(63), ws(64), .42)
    t_zoom0, t_zoom1 = ws(65), ws(66)
    t_done = ws(68)
    hx, hy = 540.0, 760.0
    an = P.head_anchor(hx, hy, HK13)
    sh0, sh1, shy = an["shelf"]
    sxp = (sh0 + sh1) / 2 + 30 * HK13
    sk = HK13 * .8
    o = [paper_bg()]
    o.append(P.head_outline(hx, hy, HK13, 1.0, seed=12, t=t))
    # картотека внутри головы (низ, у затылка)
    cfx, cfy = an["cab"]
    cf_k = .62 * HK13
    t_open = t_done - .45
    out = ease_out(ramp(t, t_open, .2), 2) * (1 - ease_in(ramp(t, t_done, .08), 2))
    o.append(P.card_file(cfx, cfy, cf_k, out, seed=13))
    # лист: стоит на полочке → уезжает в ящик
    seal_u = ramp(t, t_slam, .25)
    hop = -26 * math.sin(math.pi * ramp(t, t_slam, .25))
    glow_u = .35 * (1 - ramp(t, t_slam + .3, .5)) + .25 * math.exp(-max(0.0, t - t_slam) * 4) * (t >= t_slam)
    fly = ease_in(ramp(t, t_done - .3, .3), 2)
    if fly < 1:
        slot = P.card_file_slot(cfx, cfy, cf_k, max(out, .6))
        px = lerp(sxp, slot[0], fly)
        py = lerp(shy, slot[1] + 40, fly) - 120 * math.sin(math.pi * fly)
        sheet = gold_sheet(0, 0, sk, glow_u, t, 13, 3 * math.sin(t * 3) + 70 * fly, seal_u, hop)
        sc = 1 - .45 * fly
        o.append(f'<g transform="translate({px:.1f} {py:.1f}) scale({sc:.4f} {sc * (1 - .5 * fly):.4f})">{sheet}</g>')
    o.append(impact(sxp, shy - 100 * sk, (t - t_slam) / .3, 120, 8, -180, 360, 7, sd=130, sy=1.0, col="#2FA45A"))
    if t_slam <= t < t_slam + .5:
        o.append(P.sparkles(sxp, shy - 100 * sk, HK13 * 1.4, 1 - ramp(t, t_slam, .5), t, seed=13, n=6, r=170))
    # печать: опускается сверху с первого кадра, шмяк, уходит вверх
    if t < t_slam + .7:
        if t < t_slam:
            dn = ease_in(ramp(t, a, t_slam - a), 2.2)
            sy_ = lerp(shy - 900, shy - 100 * sk - 64 * sk, dn)
            down = 0.0
        else:
            up = ease_in(ramp(t, t_slam + .18, .45), 2)
            sy_ = shy - 100 * sk - 64 * sk - 950 * up
            down = 1 - ramp(t, t_slam, .12)
        o.append(P.rubber_stamp(sxp, sy_ + 64 * sk * 0, sk * 1.3, down, seed=13))
    # звёздочка над захлопнутым ящиком
    su = ramp(t, t_done + .05, .5)
    if 0 < su < 1:
        sx_, sy_ = P.pop(t, t_done + .05, .3)
        o.append(P.star4(cfx, cfy - 150 * cf_k - 60 * su, 46 * sx_, 1.0))
        o.append(P.sparkles(cfx, cfy - 150 * cf_k - 60 * su, 1.2, 1 - su, t, seed=31, n=4, r=80))
    o.append(impact(cfx, cfy - 70 * cf_k, (t - t_done) / .25, 90, 6, -170, 160, 6, sd=140))
    # камера: тряска на печати, наезд на пустой лист, отъезд к ящику, толчок
    zin = ease_io(ramp(t, t_zoom0 - .1, t_zoom1 - t_zoom0 + .35))
    zout = ease_io(ramp(t, t_open - .15, .35))
    f0x, f0y = hx + 10, hy + 120
    fx = lerp(f0x, sxp, zin * (1 - zout)) + (cfx + 60 - f0x) * .45 * zout
    fy = lerp(f0y, shy - 100 * sk, zin * (1 - zout)) + (cfy - 60 - f0y) * .45 * zout
    s = 1.0 + .75 * zin * (1 - zout) + .2 * zout + .05 * ease_io(ramp(t, a, t_slam - a))
    dx, dy = P.shake(t, t_slam, 16, .3, 1)
    bx, by = P.shake(t, t_done, 9, .22, 4)
    return frame_svg("".join(o), fx + dx + bx, fy + dy + by, s, .8 * math.sin(t * 1.3))


# ═══════════════════════════════ s03: кубок тяжелеет на груди ═══════════════════════════════
D3 = (330.0, 1050.0)
D3_SC = .85
WALL_DAY = "#EADBB9"
FLOOR_DAY = "#C9A57A"


def day_room_bg(t, beam_x=520.0):
    o = [f'<path d="M-900 -900H2600V1180H-900Z" fill="{WALL_DAY}"/>']
    o.append(line([(-900, 1060), (2600, 1060)], 5, "#B79E78", taper=0, seed=301))
    o.append(blob(rect_pts(-900, 1060, 2600, 1180), "#DCC9A3"))
    o.append(blob(rect_pts(-900, 1180, 2600, 3000), FLOOR_DAY))
    for j in range(12):
        o.append(line([(-900, 1230 + j * 70), (2600, 1230 + j * 70)], 3, "#B08A5E", taper=0, seed=310 + j, op=.6))
    # золотой луч сверху (тот же прожектор хука), край чёткий
    br = .55 + .08 * math.sin(t * 5)
    o.append(blob([(beam_x - 120, -900, 1), (beam_x + 120, -900, 1), (beam_x + 380, 1200, 1), (beam_x - 380, 1200, 1)], "#FFE08A", .28 * br))
    o.append(blob([(beam_x - 60, -900, 1), (beam_x + 60, -900, 1), (beam_x + 220, 1200, 1), (beam_x - 220, 1200, 1)], "#FFF1B8", .22 * br))
    return "".join(o)


def s03(t):
    lib.dyn_begin()
    sid = "s03"
    a = A(sid)
    t_and, t_this = ws(9), ws(13)
    heavy = ease_in(ramp(t, t_and, t_this - t_and), 1.5)
    press = ease_out(ramp(t, t_this, .14), 2)
    x, y = D3
    sc = D3_SC
    sink = 24 * heavy + 26 * press + 4 * math.sin(t * 9) * (1 - heavy)
    yb = y + sink
    sag = .35 + .4 * heavy + .3 * press
    worry = t >= t_this - .05
    expr = "pinned76" if worry else ("glance76" if t >= t_and + .15 else "bored76")
    o = [day_room_bg(t, 560)]
    mx, my = 560, y + 150
    o.append(P.floor_mattress(mx, my, 1.25, sag=sag, sink=0, layer="back", sag_x=x + 120, seed=3))
    breath = .015 * math.sin(t * 5)
    fig = PP.dima_pj(x, yb, sc, expr, "pinned76", lean_add=breath + .04 * press, shrug=.3 + .4 * press,
                     arms={"n": ("ik", (x + 170 * sc, yb - 40 * sc), -1), "f": ("ik", (x - 90 * sc, yb - 50 * sc), 1)}, **PP.mattress_kw(x, yb, sc))
    # пакет чипсов в ближней руке, лежит на матрасе; на «этого» чипсы выскальзывают
    wx_, wy_ = fig["wrist"]["n"]
    bag_rot = -70 - 25 * press
    o.append(fig["svg"])
    o.append(P.chips_bag(wx_ + 60, wy_ - 10, .8, bag_rot, crunch=.3 + .5 * press, seed=3))
    o.append(P.chip_crumbs(wx_ + 150, wy_ + 10, 1.0, ramp(t, t_this + .02, .7), seed=3, n=6))
    # кубок на животе: блик бежит с «И», тяжелеет, толчок вниз на «этого»
    tx = x + 250 * sc
    ty = yb - 140 * sc + 18 * press
    gl = ramp(t, t_and - .05, .5)
    rock = 3 * math.sin(t * 6) * (1 - heavy) - 2 * press
    o.append(shadow(tx, ty + 4, 120, .2 * heavy))
    o.append(P.trophy(tx, ty, 1.1, glint=gl, heavy=heavy, rot=rock, seed=3))
    o.append(impact(tx, ty - 30, (t - t_this) / .3, 150, 6, 20, 140, 8, sd=330, sy=.5))
    # тяжесть: штрихи-«вес» над кубком
    if heavy > .2:
        for j in range(3):
            yy = ty - 420 - 40 * j + 30 * ((t * 2 + j * .33) % 1)
            o.append(line([(tx - 50 + 50 * j, yy), (tx - 50 + 50 * j, yy + 50)], 6, INK, taper=.6, seed=340 + j, op=.5 * heavy))
    o.append(P.floor_mattress(mx, my, 1.25, sag=sag, sink=0, layer="front", sag_x=x + 120, seed=3))
    # камера: медленный наезд сверху вниз за проседанием, толчок на «этого»
    pu = ease_io(ramp(t, a, T1(sid) + .2 - a))
    dx, dy = P.shake(t, t_this, 14, .3, 5)
    cx = 360 + 30 * pu + dx
    cy = 760 + 60 * pu + .5 * sink + dy
    s = 1.42 + .12 * pu + .05 * press
    return frame_svg("".join(o), cx, cy, s, -1.0 + 1.6 * pu)


# ═══════════════════════════════ аудитория: s14, s15, s16 ═══════════════════════════════
AUD_FLOOR = 1150.0
ST_SC = .55
ST_HIP = 1000.0
LEFT_X = (310.0, 520.0, 730.0)
RIGHT_X = (1250.0, 1470.0, 1690.0)
TEACH = (975.0, 1000.0)
DESK_Y = 912.0
WIN = (700.0, -260.0, 1300.0, 470.0)
C_AUD_WALL = "#E3C9A4"
C_AUD_WALL_SH = "#C9A982"
C_AUD_FLOOR = "#9C6B45"


def sky_city(t, dusk):
    x0, y0, x1, y1 = WIN
    g = lib.lin_grad([(0, lib.mix("#5B6FB5", "#3B4C8C", dusk), 1), (.55, lib.mix("#E59A86", "#B97A9A", dusk), 1), (1, lib.mix("#F7C47A", "#E99A6A", dusk), 1)])
    o = [f'<path d="M{x0 - 400} {y0 - 400}H{x1 + 400}V{y1 + 40}H{x0 - 400}Z" fill="url(#{g})"/>']
    o.append(P.glow((x0 + x1) / 2 + 140, y1 - 70, 220, .7, "#FFD27A"))
    o.append(blob(ellipse_pts((x0 + x1) / 2 + 140, y1 - 60, 60, 60, 24), "#FFD98A", .9))
    o.append(P.city_skyline((x0 + x1) / 2, y1 - 30, 900, t, dusk, seed=14))
    return "".join(o)


def aud_window(t, dusk):
    x0, y0, x1, y1 = WIN
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    o = [f'<g clip-path="url(#{c})">{sky_city(t, dusk)}</g>']
    fr = "#8A5B32"
    for (a, b, cc, d) in ((x0 - 22, y0 - 22, x1 + 22, y0), (x0 - 22, y1, x1 + 22, y1 + 30), (x0 - 22, y0, x0, y1), (x1, y0, x1 + 22, y1)):
        o.append(shape(rect_pts(a, b, cc, d), fr, "", w=4, seed=int(a)))
    o.append(shape(rect_pts((x0 + x1) / 2 - 9, y0, (x0 + x1) / 2 + 9, y1), fr, "", w=3.4, seed=1401))
    o.append(shape(rect_pts(x0, (y0 + y1) / 2 - 8, x1, (y0 + y1) / 2 + 8), fr, "", w=3.4, seed=1402))
    return "".join(o)


def aud_back(t, dusk, shadow_u):
    o = [f'<path d="M-900 -900H3200V{AUD_FLOOR}H-900Z" fill="{C_AUD_WALL}"/>']
    o.append(blob(rect_pts(-900, AUD_FLOOR - 70, 3200, AUD_FLOOR), C_AUD_WALL_SH))
    o.append(line([(-900, AUD_FLOOR - 70), (3200, AUD_FLOOR - 70)], 4, INK, taper=0, seed=1403, op=.5))
    o.append(blob(rect_pts(-900, AUD_FLOOR, 3200, 3200), C_AUD_FLOOR))
    for j in range(10):
        o.append(line([(-900, AUD_FLOOR + 40 + j * 60 + j * j * 4), (3200, AUD_FLOOR + 40 + j * 60 + j * j * 4)], 3, "#7C5233", taper=0, seed=1410 + j, op=.7))
    o.append(line([(-900, AUD_FLOOR), (3200, AUD_FLOOR)], 5, INK, taper=0, seed=1404))
    # свет окна на стене и на полу — ползёт с shadow_u (время идёт)
    x0, y0, x1, y1 = WIN
    sh = 900 * shadow_u
    o.append(blob([(x0 + 60 + sh * .3, y0 + 20, 1), (x1 + 60 + sh * .3, y0 + 20, 1), (x1 + 160 + sh * .45, y1 + 40, 1), (x0 + 160 + sh * .45, y1 + 40, 1)], "#FFE2A6", .0))
    flo = [(x0 - 60 + sh, AUD_FLOOR + 30, 1), (x1 - 60 + sh, AUD_FLOOR + 30, 1), (x1 + 420 + sh * 1.6, 2100, 1), (x0 + 120 + sh * 1.6, 2100, 1)]
    o.append(blob(flo, "#F2B36A", .38))
    o.append(aud_window(t, dusk))
    # доска-полка без надписей между окном и краями: пустая зелёная доска слева
    o.append(shape(rect_pts(-560, 260, 380, 700), "#3E5E4E", line([(-520, 640), (340, 640)], 3, "#5C7E6C", taper=0, seed=1405), w=5, seed=1406))
    o.append(shape(rect_pts(-580, 700, 400, 724), C_WOOD_A, "", w=3.6, seed=1407))
    o.append(shape(rect_pts(1620, 300, 2400, 640), "#E9DCC4", "", w=4.4, seed=1408))
    return "".join(o)


C_WOOD_A = "#B27C4C"


def aud_desk(x0, x1, layer, seed=0):
    """Длинный стол: layer "top" — столешница (рисовать ДО рук на столе, ПОСЛЕ фигур), "front" — передняя панель (после фигур)."""
    if layer == "top":
        return shape([(x0 + 20, DESK_Y - 40, 1), (x1 - 20, DESK_Y - 40, 1), (x1, DESK_Y, 1), (x0, DESK_Y, 1)], "#C8915C",
                     line([(x0 + 40, DESK_Y - 30), (x1 - 60, DESK_Y - 30)], 3, "#E0AE78", taper=.3, seed=seed + 1), w=4.2, seed=seed + 2)
    return shape(rect_pts(x0, DESK_Y, x1, AUD_FLOOR + 90), "#A86F42", blob(rect_pts(x0, DESK_Y, x1, DESK_Y + 22), "#7E4E2A", .9) +
                 line([(x0 + 30, DESK_Y + 120), (x1 - 30, DESK_Y + 120)], 3, "#8E5A33", taper=.2, seed=seed + 3), w=4.6, seed=seed + 4)


def lamp_pool(x, y, u, w=220.0):
    if u <= .01:
        return ""
    return blob(ellipse_pts(x, y, w, w * .16, 24), "#FFE7A3", .55 * u)


def pencil_in(fig, t, write, seed):
    wx, wy = fig["wrist"]["n"]
    jig = 6 * math.sin(t * 31 + seed) * write
    return P.pencil(wx + 26 + jig, wy + 4, .7, 35 + 8 * math.sin(t * 23 + seed) * write)


def student_left(i, t, mode, u=0.0, seed=0):
    """Студент слева: mode "tell" — рассказывает (руки показывают «вот такое»), "relax" — откинулся."""
    who = PP.STUDENTS76[i]
    x = LEFT_X[i]
    ph = t * 2.6 + i * 1.9
    if mode == "tell":
        w = .5 + .5 * math.sin(ph)
        arms = {"n": ("ik", (x + (300 + 60 * w) * ST_SC, ST_HIP - (330 + 120 * w + 40 * i) * ST_SC), -1),
                "f": ("ik", (x + (200 - 40 * w) * ST_SC, ST_HIP - (300 + 90 * (1 - w)) * ST_SC), -1)}
        return PP.person(who, x, ST_HIP, ST_SC, "tell_s76", "gesture76", arms=arms, lean_add=.05 * math.sin(ph * .7), head_add=.04 * math.sin(ph),
                         **PP.sit_kw(x, ST_HIP, ST_SC, who))
    e = ease_io(u)
    return PP.person(who, x, ST_HIP, ST_SC, "smug_s76" if e > .3 else "tell_s76", "gesture76", u_pose=(RELAX_POSE, e),
                     lean_add=-.1 * e + .03 * math.sin(ph * .5), head_add=.05 * math.sin(ph * .6) - .06 * e, **PP.sit_kw(x, ST_HIP, ST_SC, who))


RELAX_POSE = "cross"


def student_right(i, t, shh=0.0):
    who = PP.STUDENTS76[3 + i]
    x = RIGHT_X[i]
    ph = t * 3 + i * 2.3
    if shh > 0:
        e = ease_io(shh)
        tgt = PP.lips76(x, ST_HIP, ST_SC, .42 * (1 - e), 0.0, who)
        fig = PP.person(who, x, ST_HIP, ST_SC, "shh_s76" if e > .5 else "write_s76", "write76", lean_add=-.4 * e,
                        arms={"n": ("ik", (lerp(x + 330 * ST_SC, tgt[0], e), lerp(ST_HIP - 160 * ST_SC, tgt[1], e)), -1)},
                        hands={"n": {"dir": (.1, -1), "curl": (0, .88, .92, .92), "spread": .03, "thumb": .75}} if e > .6 else None,
                        **PP.sit_kw(x, ST_HIP, ST_SC, who))
        return fig, 1 - e
    fig = PP.person(who, x, ST_HIP, ST_SC, "write_s76", "write76", lean_add=.02 * math.sin(ph), head_add=.03 * math.sin(ph * 1.3),
                    arms={"n": ("ik", (x + (330 + 18 * math.sin(ph * 2.2)) * ST_SC, ST_HIP - (160 + 6 * math.sin(ph * 3.1)) * ST_SC), -1)},
                    **PP.sit_kw(x, ST_HIP, ST_SC, who))
    return fig, 1.0


def teacher_fig(t, mode, u=0.0):
    x, y = TEACH
    ph = t * 2.2
    if mode == "listen":
        return PP.person("psych", x, y - 300 * ST_SC, ST_SC, "listen76", None, flip=True, head_add=.05 * math.sin(ph),
                         **PP.stand_kw(x, y - 300 * ST_SC, ST_SC, "psych"))
    if mode == "clap":
        cu = .5 + .5 * math.cos(t * 2 * math.pi * 3.2)
        arms, hands = PP.clap_arms(cu, x, y - 300 * ST_SC, ST_SC, "psych")
        return PP.person("psych", x, y - 300 * ST_SC, ST_SC, "cheer76", None, flip=True, arms=arms, hands=hands,
                         **PP.stand_kw(x, y - 300 * ST_SC, ST_SC, "psych"))
    return PP.person("psych", x, y - 300 * ST_SC, ST_SC, "proud76", "thumb76", flip=True, lean_add=.03 * math.sin(ph),
                     **PP.stand_kw(x, y - 300 * ST_SC, ST_SC, "psych"))


def aud_scene(t, left_mode="tell", relax_u=0.0, teach="listen", lamp_l=1.0, shadow_u=0.0, dusk=.3, close_u=0.0, shh=0.0,
              left_gone=0.0, write_u=0.0):
    o = [aud_back(t, dusk, shadow_u)]
    # левый стол
    o.append(lamp_pool(150, DESK_Y + 60, 0))
    if left_gone < 1:
        for i in range(3):
            f = student_left(i, t, left_mode, clamp(relax_u * 1.3 - i * .15), seed=i)
            o.append(f["svg"])
    if left_gone >= 1:
        for i, x in enumerate(LEFT_X):
            o.append(shape(lib.rrect(x - 70, DESK_Y - 150 + 8 * i, x + 10, DESK_Y + 10, 10), "#8E5A33", "", w=4, seed=1460 + i))
    tf = teacher_fig(t, teach) if teach else None
    if tf and left_gone < 1:
        o.append(tf["svg"])
    o.append(aud_desk(110, 920, "top", 1420))
    # тетради левых: открыты → закрываются по очереди
    for i, x in enumerate(LEFT_X):
        if left_gone >= 1 and i != 1:
            continue
        cu = clamp(close_u * 1.4 - i * .2)
        bx = x + 300 * ST_SC
        if cu < .5:
            o.append(P.book_open(bx, DESK_Y - 16, .55, 0, flip=cu * 2, seed=40 + i))
        else:
            o.append(P.book_closed(bx, DESK_Y - 16, .55 * (1.5 if left_gone >= 1 else 1), 0, cover=P.C_BLUE_COVER if i % 2 else P.C_RED_COVER))
    o.append(P.lamp_desk(185, DESK_Y - 18, .9, lamp_l, seed=41))
    o.append(P.glow(199, DESK_Y - 110, 170, .7 * lamp_l, "#FFE7A3"))
    o.append(lamp_pool(270, DESK_Y - 18, lamp_l, 200))
    o.append(aud_desk(110, 920, "front", 1430))
    dark = .28 * left_gone + .18 * (1 - lamp_l) * (1 - left_gone)
    if dark > .01:
        g = lib.lin_grad([(0, "#1E1A30", 1), (.75, "#1E1A30", 1), (1, "#1E1A30", 0)], 0, 0, 1, 0)
        o.append(f'<path d="M-900 -900H1060V3200H-900Z" fill="url(#{g})" opacity="{dark:.3f}"/>')
    # правый стол
    figs = []
    for i in range(3):
        f, wr = student_right(i, t, shh if i == 1 else 0.0)
        figs.append((f, wr))
        o.append(f["svg"])
    o.append(aud_desk(1130, 1990, "top", 1440))
    for i, x in enumerate(RIGHT_X):
        wu = clamp(write_u + .25 * i + .08 * t) % 1.0 if write_u >= 0 else 0
        o.append(P.letter(x + 320 * ST_SC, DESK_Y - 20, .55, -6, 230, 230, write=.25 + .7 * clamp(write_u * (1.1 - .15 * i) + .1), seed=50 + i, sy=.45))
        f, wr = figs[i]
        if wr > .2:
            o.append(pencil_in(f, t, wr, i))
    o.append(P.lamp_desk(1930, DESK_Y - 18, .9, 1.0, seed=42))
    o.append(P.glow(1944, DESK_Y - 110, 170, .7, "#FFE7A3"))
    o.append(lamp_pool(1820, DESK_Y - 18, 1.0, 200))
    o.append(aud_desk(1130, 1990, "front", 1450))
    return "".join(o)


def s14(t):
    lib.dyn_begin()
    sid = "s14"
    a = A(sid)
    t_ny, t_st, t_tell = ws(70), ws(71), ws(73)
    body = aud_scene(t, "tell", teach="listen", lamp_l=1.0, shadow_u=0.0, dusk=.15 + .1 * ramp(t, a, 3), write_u=ramp(t, a, 3) * .4)
    x0, y0, x1, y1 = WIN
    out = ease_io(ramp(t, t_st - .25, .7))
    wx = whip_in(t, T0(sid), 420)
    cx = lerp((x0 + x1) / 2 + 20 * ramp(t, a, 1), 600, out)
    cy = lerp((y0 + y1) / 2 + 30 - 60 * ramp(t, a, 1), 800, out)
    s = lerp(1.95 + .1 * ramp(t, a, 1), 1.42, out)
    drift = ease_io(ramp(t, t_tell - .2, T1(sid) - t_tell + .4))
    cx += -40 * drift
    s += .06 * drift
    return frame_svg(body, cx - wx, cy, s, lerp(-1.5, .4, out))


def s15(t):
    lib.dyn_begin()
    sid = "s15"
    a = A(sid)
    t_heard, t_ok, t_then, t_it = ws(77), ws(78), ws(79), ws(81)
    teach = "clap" if t < t_ok + .55 else "thumb"
    relax = ease_io(ramp(t, t_ok, .6))
    close = ramp(t, t_ok + .2, .7)
    time_u = ease_io(ramp(t, t_then - .1, T1(sid) + .2 - t_then))
    lamp = 1 - ease_in(ramp(t, lerp(t_then, t_it, .55), .35), 2)
    lamp *= 1 - .3 * (P.flicker(t, lerp(t_then, t_it, .3), lerp(t_then, t_it, .55), 7) if hasattr(P, "flicker") else 0)
    body = aud_scene(t, "relax", relax, teach, lamp, .1 + .5 * time_u, .3 + .5 * time_u, close, write_u=.3 + .6 * time_u)
    pu = ease_io(ramp(t, a, T1(sid) + .2 - a))
    dx, dy = P.shake(t, t_ok, 6, .25, 2)
    s = 1.12 - .06 * pu
    return frame_svg(body, 600 + 90 * pu + dx, 790 + dy, s, -.5 + .9 * pu)


def s16(t):
    lib.dyn_begin()
    sid = "s16"
    a = A(sid)
    t_less, t_who, t_quiet = ws(82), ws(84), ws(85)
    shh = ease_io(ramp(t, t_quiet + .1, .5))
    body = aud_scene(t, "relax", 1.0, None, 0.0, .65 + .1 * ramp(t, a, 2), .85, 1.0, shh=shh, left_gone=1.0, write_u=.6 + .4 * ramp(t, a, 2))
    mv = ease_io(ramp(t, lerp(t_less, t_who, .5), t_who - lerp(t_less, t_who, .5) + .25))
    zoom = ease_io(ramp(t, t_quiet, .7))
    cx = lerp(520, 1480, mv) + 20 * zoom
    cy = lerp(820, 800, mv) - 50 * zoom
    s = lerp(1.35, 1.4, mv) + .3 * zoom + .04 * ramp(t, a, .6)
    return frame_svg(body, cx, cy, s, lerp(.6, -.4, mv))


SCENES = {"s03": s03, "s06": s06, "s12": s12, "s13": s13, "s14": s14, "s15": s15, "s16": s16}


def frame(sid, t):
    return SCENES[sid](t)
