"""Рилс 75 «Ток или скука», группа A: графика на бумаге — опыт в Вирджинии и Англия.
Все времена — из shots.json (t0/t1 плана) и voice/words.json (W(i) — начало слова i, WE(i) — конец) при рендере; секунд в коде нет.
s03 (whip): разрез кукольного дома 2×2 — в трёх комнатках участники ёрзают, кнопки мигают; «ты» (W11) камера ныряет к пустой комнатке,
    её кнопка разгорается; «скорее» (W13) трое жмут по очереди — вспышка, волосы дыбом.
s08: здание с колоннами и куполом встаёт штампом на «Вирджинии» (W39), окна загораются; «людей» (W40) крошечные люди заходят в двери;
    «оставляли» (W41) камера ныряет в окно — человек один на стуле, дверь за ним захлопывается.
s10 (whip): трое мужчин в ряд с кнопками; «Две» (W51) первый жмёт, «трети» (W52) второй, третий спокоен (руки скрещены, косится);
    «ударили» (W55) оба ещё раз — две вспышки, дымок.
s11: бородач один; «нажал» (W58) жмёт, «сто девяносто» (W59–W60) — пулемёт нажатий, кнопка раскаляется, искры, вспышка на «раз» (W61).
s14 (whip): дождь, красный двухэтажный автобус на «Англии» (W75), камера в окно — человек переписывает справочник; «пятнадцати» (W77)
    страница перелистывается; «скучного» (W79) зевок; «дела» (W80) голова на справочник.
s15: «люди» (W81) поднимает голову, стаканчики; «придумывали» (W82) становятся шляпой, телефоном-банкой, горшком, башенкой;
    «больше идей» (W83–W84) фонтан стаканчиков вокруг большой искры.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Люди — common/people.py, предметы — common/props.py."""
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
WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SHOTS = {s["id"]: s for s in json.load(open(os.path.join(STORY, "shots.json")))["shots"]}


def W(i):
    return WORDS[i]["start"]


def WE(i):
    return WORDS[i]["end"]


def T0(sid):
    return SHOTS[sid]["t0"]


def T1(sid):
    return SHOTS[sid]["t1"]


def lerp(a, b, u):
    return a + (b - a) * u


def paper_bg(col=None, grid="#E3D9BE"):
    d = "".join(f"M-900 {i * 64}H2600" for i in range(-14, 46)) + "".join(f"M{i * 64} -900V2800" for i in range(-14, 42))
    return (f'<path d="M-900 -900H2600V2800H-900Z" fill="{col or P.C_PAGE}"/>'
            f'<path d="{d}" stroke="{grid}" stroke-width="2" fill="none"/>')


def frame_svg(body, cx, cy, s, rot, over=""):
    return svg(f'<rect width="1080" height="1920" fill="{P.C_PAGE}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def shadow(x, y, rx, op=.13):
    return blob(ellipse_pts(x, y, rx, rx * .14, 18), "#6B5B3A", op)


def glow_disc(x, y, r, col, op):
    if op <= .01:
        return ""
    g = lib.rad_grad([(0, col, op), (1, col, 0)], x, y, r)
    return f'<circle cx="{lib.f(x)}" cy="{lib.f(y)}" r="{lib.f(r)}" fill="url(#{g})"/>'


# ─────────────────────────── мебель на бумаге (люди — только people.py) ───────────────────────────
CH = dict(c="#8e98a0", sh="#6d767e", hi="#b2bac0", leg="#5d646b")


def chair_side(px, py, s, floor, seed=0, rattle=0.0):
    """Стул сбоку под человеком, сидящим лицом вправо: (px, py) — его таз, s — масштаб figure. dict(back, seat)."""
    sd = 30000 + seed
    k = s / .3
    seat = py + 26 * k
    x0, x1 = px - 70 * k, px + 120 * k
    bx = x0 + 6 * k
    back = shape([(bx - 4 * k, seat, 1), (bx + 6 * k, seat, 1), (bx - 2 * k, seat - 215 * k, 1), (bx - 12 * k, seat - 214 * k, 1)], CH["leg"], w=2.4, seed=sd)
    back += shape(lib.rrect(bx - 28 * k, seat - 235 * k, bx + 16 * k, seat - 70 * k, 14 * k), CH["hi"],
                  blob(rect_pts(bx - 2 * k, seat - 235 * k, bx + 16 * k, seat - 70 * k), CH["c"], .8), w=2.8, seed=sd + 1)
    front = shape(lib.rrect(x0 - 10 * k, seat - 6 * k, x1, seat + 14 * k, 7 * k), CH["c"], blob(rect_pts(x0 - 10 * k, seat + 6 * k, x1, seat + 14 * k), CH["sh"]),
                  w=2.8, seed=sd + 2)
    for i, lx in enumerate((x0 + 4 * k, x1 - 12 * k)):
        j = rattle * math.sin(i * 2 + seed)
        front += shape([(lx - 4 * k, seat + 14 * k, 1), (lx + 4 * k, seat + 14 * k, 1), (lx + 6 * k + j, floor, 1), (lx - 2 * k + j, floor, 1)], CH["leg"], w=2.4,
                       seed=sd + 3 + i)
    return dict(back=back, seat=front, shadow=shadow((x0 + x1) / 2, floor + 3, (x1 - x0) * .7, .16))


def small_table(x0, x1, top, floor, seed=0, col="#dfe3e2", sh="#b5bcbb"):
    sd = 30100 + seed
    th = 14.0 * (x1 - x0) / 200
    o = shadow((x0 + x1) / 2, floor + 3, (x1 - x0) * .62, .15)
    o += shape([(x0 + 10, top - th * .9, 1), (x1 - 10, top - th * .9, 1), (x1, top, 1), (x0, top, 1)], "#f2f4f3", "", w=2.6, seed=sd)
    o += shape(rect_pts(x0, top, x1, top + th), col, blob(rect_pts(x0, top + th * .6, x1, top + th), sh), w=2.6, seed=sd + 1)
    for i, lx in enumerate((x0 + (x1 - x0) * .12, x1 - (x1 - x0) * .12)):
        w_ = (x1 - x0) * .035
        o += shape([(lx - w_, top + th, 1), (lx + w_, top + th, 1), (lx + w_ * .7, floor, 1), (lx - w_ * .7, floor, 1)], col,
                   blob(rect_pts(lx, top + th, lx + w_, floor), sh, .8), w=2.4, seed=sd + 2 + i)
    return o


def pedestal(x, top, floor, k=1.0, seed=0):
    """Узкая стойка под коробку с кнопкой: площадка, трубка, круглое основание."""
    sd = 30200 + seed
    o = shadow(x, floor + 3, 70 * k, .16)
    o += shape(rect_pts(x - 9 * k, top, x + 9 * k, floor - 8 * k), "#8e98a0", blob(rect_pts(x + 2 * k, top, x + 9 * k, floor - 8 * k), "#6d767e"), w=2.4, seed=sd)
    o += shape(ellipse_pts(x, floor - 6 * k, 55 * k, 10 * k, 14), "#b2bac0", "", w=2.6, seed=sd + 1)
    o += shape(lib.rrect(x - 80 * k, top - 4 * k, x + 80 * k, top + 10 * k, 4 * k), "#b2bac0", "", w=2.6, seed=sd + 2)
    return o


def lab_wall(y0, floor, x0=-300, x1=1380, seed=0, bottom=True):
    """Белая стена опыта со штриховкой, плинтус и пол — фон графики (не пустая бумага)."""
    sd = 30300 + seed
    o = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{floor - y0}" fill="{WALL}"/>']
    for j in range(int((x1 - x0) / 70)):
        xx = x0 + 30 + j * 70
        o.append(line([(xx, y0 + 30), (xx - 70, y0 + 260)], 2.6, WALL_SH, taper=.5, wmin=.2, seed=sd + j))
    o.append(blob(rect_pts(x0, floor - 26, x1, floor), "#E7E1D4"))
    o.append(line([(x0, floor - 26), (x1, floor - 26)], 3, "#C9C0AE", taper=.1, seed=sd + 90))
    o.append(blob(rect_pts(x0, floor, x1, floor + 260), FLOOR))
    o.append(line([(x0, floor), (x1, floor)], 4, "#B9AE98", taper=.1, seed=sd + 91))
    o.append(line([(x0, y0), (x1, y0)], 5, INK, taper=0, seed=sd + 92))
    if bottom:
        o.append(line([(x0, floor + 260), (x1, floor + 260)], 5, INK, taper=0, seed=sd + 93))
    return "".join(o)


def zap_burst(x, y, r, t, seed, u):
    """Вспышка разряда: светлый диск, молнии-лучи наружу."""
    if u <= .01:
        return ""
    o = [glow_disc(x, y, r * 1.6, "#FFF4B8", .85 * u)]
    o.append(P.star4(x, y - r * .2, r * .55 * u, 1.0))
    return "".join(o)


def seated(who, px, py, s, floor, t, btn_x, btn_y, btn_k, reach=0.0, press=0.0, expr=None, zap_u=0.0, hair=0.0, smoke=0.0, seed=0,
           heat=0.0, glow=0.3, arc=0.0, fidget=1.0, rattle=0.0, pose=None, far_hand=None, fan=0.0, stand=False):
    """Участник на стуле у столика (stand=True — у узкой стойки) с кнопкой (лицом вправо). Возвращает svg и голову."""
    fl, fh, fs = PP.fidget(t, fidget, seed)
    ch = chair_side(px, py, s, floor, seed, rattle)
    k = s / .3
    tb = pedestal(btn_x, btn_y, floor, k, seed) if stand else small_table(btn_x - 95 * k, btn_x + 95 * k, btn_y, floor, seed)
    tgt = P.shock_button_top(btn_x, btn_y, btn_k, 0, "top", press)
    o = [ch["shadow"], ch["back"], tb]
    if pose:
        fig = PP.person(who, px, py, s, expr or "serious", pose, lean_add=fl * .5, head_add=fh, shrug=fs * .5, **PP.sit_kw(px, py, s, who))
        fig["tip"] = fig["wrist"]["n"]
    else:
        fig = PP.press_at(who, px, py, s, tgt, reach=reach, press=press, expr=expr, t=t, lean_add=fl * (1 - reach), head_add=fh * (1 - .5 * reach),
                          shrug=fs * (1 - reach), far_hand=far_hand)
    btn = P.shock_button(btn_x, btn_y, btn_k, 0, press, glow, arc, heat, t, "top", seed)
    o += [ch["seat"], btn, fig["svg"]]
    if fan > 0:
        o.append(PP.finger_fan(fig["tip"], s, t, fan) + PP.finger_fan(fig["tip"], s, t + .033, fan))
    if hair > 0:
        o.append(PP.hair_spikes(fig["head"], fig["scale"], hair, t, seed=seed))
    if smoke > 0:
        o.append(PP.head_smoke(fig["head"], fig["scale"], t, smoke, seed))
    if zap_u > 0:
        hx, hy = fig["head"]
        el = fig["elbow"]["n"]
        o.append(P.zap(tgt, el, t, seed + 1, zap_u, 20 * k, 1))
        o.append(P.zap(el, (hx - 25 * k, hy + 115 * k), t, seed + 2, zap_u, 16 * k, 0))
        o.append(zap_burst(tgt[0], tgt[1], 90 * k, t, seed + 7, zap_u))
    return "".join(o), fig


def press_curve(t, tp, pre=.12, hold=.12, rel=.18):
    """(reach, press) вокруг нажатия в tp: рука тянется за pre, давит hold, отпускает за rel."""
    if t < tp - pre - .25:
        return 0.0, 0.0
    if t < tp - pre:
        return .55 * ease_io((t - (tp - pre - .25)) / .25), 0.0
    if t < tp:
        return .55 + .45 * ease_out((t - (tp - pre)) / pre, 2), 0.0
    if t < tp + hold:
        return 1.0, ease_out((t - tp) / .05, 2)
    u = clamp((t - tp - hold) / rel)
    return 1 - .35 * ease_io(u), 1 - ease_out(u, 2)


def zap_env(t, tp, dur=.32):
    u = t - tp
    if u < 0 or u > dur:
        return 0.0
    return (1 - u / dur) ** .7 * (.75 + .25 * math.sin(u * 90))


def hair_env(t, tp, rest=.55):
    u = t - tp
    if u < 0:
        return 0.0
    return min(1.0, u / .05) * (rest + (1 - rest) * math.exp(-u * 4))


# ═══════════════════════════════ s03: кукольный дом ═══════════════════════════════
HOUSE = (40.0, 1040.0)
ROOMS = [(60.0, 330.0), (550.0, 330.0), (60.0, 820.0), (550.0, 820.0)]   # левый верх (x0, y0) каждой комнатки
RW, RH = 470.0, 470.0
WALL = "#F7F4ED"
WALL_SH = "#E4DFD3"
FLOOR = "#DCD3C2"


def room_box(x0, y0, seed, light=0.0):
    sd = 31000 + seed
    o = [f'<rect x="{x0}" y="{y0}" width="{RW}" height="{RH}" fill="{WALL}"/>']
    # штриховка стен и тень в углу
    for j in range(9):
        xx = x0 + 18 + j * 22
        o.append(line([(xx, y0 + 14), (xx - 40, y0 + 120)], 2.2, WALL_SH, taper=.5, wmin=.2, seed=sd + j))
    o.append(blob(rect_pts(x0, y0, x0 + 30, y0 + RH), WALL_SH, .6))
    o.append(blob(rect_pts(x0, y0 + RH - 70, x0 + RW, y0 + RH), FLOOR))
    o.append(line([(x0, y0 + RH - 70), (x0 + RW, y0 + RH - 72)], 3, "#B9AE98", taper=.1, seed=sd + 20))
    o.append(line([(x0, y0 + RH - 92), (x0 + RW, y0 + RH - 94)], 2.4, "#CFC6B3", taper=.1, seed=sd + 21))
    if light > 0:
        o.append(f'<rect x="{x0}" y="{y0}" width="{RW}" height="{RH}" fill="#FFF3B0" opacity="{clamp(light) * .55:.3f}"/>')
    return "".join(o)


def s03(t):
    lib.dyn_begin()
    o = [paper_bg()]
    t_you, t_sk = W(11), W(13)
    # дом стоит на деревянном столе (низ кадра не пустой)
    o.append(blob(rect_pts(-400, 1300, 1480, 2600), "#C99A6B"))
    o.append(blob(rect_pts(-400, 1300, 1480, 1330), "#E0B888"))
    o.append(line([(-400, 1300), (1480, 1300)], 5, INK, taper=0, seed=31490))
    for j in range(7):
        o.append(line([(-300 + j * 90, 1380 + j * 70), (1400 - j * 40, 1400 + j * 74)], 3, "#A87C52", taper=.6, wmin=.2, seed=31491 + j))
    presses = [t_sk, t_sk + .06, t_sk + .12]
    # дом: крыша, наружные стены
    x0, x1 = HOUSE
    o.append(shadow(540, 1312, 560, .16))
    o.append(shape([(x0 - 30, 332, 1), (540, 120, 1), (x1 + 30, 332, 1)], "#C9634E", blob([(540, 150), (x1 - 10, 322), (x1 + 30, 332), (540, 120)], "#A44A39", .7),
                   w=5, seed=31500))
    o.append(shape(rect_pts(x0, 310, x1, 1310), "#E2D6BE", "", w=5, seed=31501))
    flashes = 0.0
    for i, (rx, ry) in enumerate(ROOMS):
        light = 0.0
        if i < 3:
            light = zap_env(t, presses[i], .3)
            flashes = max(flashes, light)
        o.append(room_box(rx, ry, i, light * .8))
    # люди и кнопки
    S = .3
    who = ["curly", "beard", "youth"]
    for i, (rx, ry) in enumerate(ROOMS):
        floor = ry + RH - 30
        px, py = rx + 110, floor - 300 * S * PP.HEIGHT.get(who[i] if i < 3 else "youth", 1.0) + 4
        bx, by = rx + 120 + 520 * S, py + 135 * S
        cid = lib.clip_rect(rx, ry, RW, RH)
        if i < 3:
            tp = presses[i]
            rc, pr = press_curve(t, tp, .1, .1, .2)
            if t < tp - .35:     # до нажатия — рука ходит над коленом, кнопка зовёт
                rc = .18 + .14 * math.sin(t * 6 + i * 2)
            hz = hair_env(t, tp)
            body, fig = seated(who[i], px, py, S, floor, t, bx, by, S * 1.7, rc, pr, "zap75" if t >= tp else ("eye_btn75" if i != 1 else "bored75"),
                               zap_env(t, tp, .28), hz, clamp((t - tp - .15) / .2) if t > tp else 0.0, seed=10 + i * 7,
                               glow=.25 + .25 * (.5 + .5 * math.sin(t * 9 + i * 1.7)), fidget=1.3)
        else:
            # пустая комнатка: стул и кнопка; кнопка разгорается на «ты»
            ch = chair_side(px, py, S, floor, 40)
            g = .35 + .25 * (.5 + .5 * math.sin(t * 7)) + .6 * ease_out(clamp((t - t_you) / .25))
            body = ch["shadow"] + ch["back"] + ch["seat"] + small_table(bx - 95 * S / .3, bx + 95 * S / .3, by, floor, 40)
            body += glow_disc(bx + 10, by - 60, 170 * clamp(g), "#FF6B5A", .5 * clamp(g))
            body += P.cuff_wire(P.shock_button_wire(bx, by, S * 1.7), (px + 30, floor - 6), 8, t, .6, seed=3, cuff=True, cuff_rot=90)
            body += P.shock_button(bx, by, S * 1.7, 0, 0, clamp(g), 0, 0, t, "top", 44)
        o.append(f'<g clip-path="url(#{cid})">{body}</g>')
    # перегородки
    o.append(shape(rect_pts(530, 330, 550, 1290), "#E2D6BE", "", w=4, seed=31510))
    o.append(shape(rect_pts(60, 800, 1020, 820), "#E2D6BE", "", w=4, seed=31511))
    o.append(line([(x0, 310), (x1, 310)], 5, INK, taper=0, seed=31512))
    # камера: дрейф с кадра 0, на «ты» нырок к пустой комнатке, на нажатиях — толчки
    d = ease_out(clamp((t - t_you) / .3), 3)
    cx = lerp(540, 615, d) + 6 * math.sin(t * 2.3)
    cy = lerp(970, 1060, d)
    s = lerp(1.0 + .05 * clamp((t - T0("s03") + .2) / 1.0), 1.24, d)
    rot = lerp(-.8, .6, d) + .3 * math.sin(t * 1.7)
    for tp in presses:
        sh = P.shake(t, tp, 9, .22, int(tp * 100))
        cx += sh[0] / s
        cy += sh[1] / s
    return frame_svg("".join(o), cx, cy, s, rot)


# ═══════════════════════════════ s08: здание с куполом ═══════════════════════════════
B8 = (540.0, 1270.0, 1.22)      # центр дна, масштаб здания


def tree_autumn(x, y, k, t, seed):
    sd = 32000 + seed
    sw = 3 * math.sin(t * 2.1 + seed)
    o = [shadow(x, y + 2, 90 * k, .14)]
    o.append(shape([(x - 12 * k, y, 1), (x + 12 * k, y, 1), (x + 8 * k, y - 170 * k, 1), (x - 8 * k, y - 170 * k, 1)], "#7A5232", "", w=3, seed=sd))
    cols = ["#E08A2E", "#D2552F", "#E8B83A"]
    for j, (dx, dy, r) in enumerate(((0, -250, 95), (-60, -200, 70), (62, -205, 72), (0, -170, 60))):
        o.append(shape(ellipse_pts(x + (dx + sw * (1 + j * .3)) * k, y + dy * k, r * k, r * .85 * k, 14), cols[(j + seed) % 3],
                       blob(ellipse_pts(x + (dx + 20 + sw) * k, y + (dy + 18) * k, r * .6 * k, r * .45 * k, 12), "#B4472A", .35), w=3.4, seed=sd + 1 + j))
    return "".join(o)


def falling_leaves(x, y, t, seed, n=5, k=1.0):
    rs = P._rs(32100 + seed)
    o = []
    for j in range(n):
        ph = (t * rs.uniform(.25, .4) + rs.uniform(0, 1)) % 1.0
        lx = x + rs.uniform(-140, 140) * k + 30 * math.sin(ph * 9 + j) * k
        ly = y + ph * 300 * k
        a = 40 * math.sin(ph * 12 + j)
        col = ["#E08A2E", "#D2552F", "#E8B83A"][j % 3]
        leaf = [(0, -10, 1), (7, -2), (0, 10, 1), (-7, -2)]
        o.append(P._tf(shape(leaf, col, "", w=2.2, seed=32110 + j), lx, ly, k * 1.3, a))
    return "".join(o)


def interior8(t, t_in, t_slam):
    """Комната внутри окна (мир 1080×1920 до масштаба): человек один на стуле, дверь слева захлопывается."""
    o = [f'<rect x="-200" y="-200" width="1480" height="2320" fill="{WALL}"/>']
    for j in range(14):
        xx = 40 + j * 80
        o.append(line([(xx, 120), (xx - 90, 520)], 3, WALL_SH, taper=.5, wmin=.2, seed=32200 + j))
    floor = 1500.0
    o.append(blob(rect_pts(-200, floor - 120, 1280, 2120), FLOOR))
    o.append(line([(-200, floor - 120), (1280, floor - 122)], 5, "#B9AE98", taper=.1, seed=32220))
    o.append(blob(rect_pts(-200, -200, 60, 2120), WALL_SH, .55))
    # дверь слева: от приоткрытой к закрытой
    slam = ease_in(clamp((t - t_slam + .12) / .12), 2)
    open_w = 230 * (1 - slam)
    dx0, dx1, dy0, dy1 = 90, 400, 520, floor - 120
    o.append(shape(rect_pts(dx0 - 14, dy0 - 14, dx1 + 14, dy1), "#E2D6BE", "", w=4, seed=32230))
    o.append(blob(rect_pts(dx0, dy0, dx1, dy1), "#3A3530"))
    leaf_x1 = dx1 - open_w
    o.append(shape([(dx0, dy0, 1), (leaf_x1, dy0 - 40 * (1 - slam), 1), (leaf_x1, dy1 + 30 * (1 - slam), 1), (dx0, dy1, 1)], "#C99A6B",
                   line([(dx0 + 30, dy0 + 40), (dx0 + 30, dy1 - 40)], 3, "#A87C52", seed=32231), w=4.4, seed=32232))
    if slam > .9:
        o.append(shape(ellipse_pts(leaf_x1 - 40, (dy0 + dy1) / 2, 14, 14, 10), "#8A8F98", "", w=3, seed=32233))
        u = clamp((t - t_slam) / .3)
        o.append(P.clink(leaf_x1, (dy0 + dy1) / 2, 2.4, u, 5, INK) if u < 1 else "")
    # человек на стуле, руки на коленях, ёрзает
    s = .62
    px, py = 560, floor - 300 * s * PP.HEIGHT["youth"] - 40
    ch = chair_side(px, py, s, floor - 40, 50)
    fl, fh, fs = PP.fidget(t, .8, 3)
    fig = PP.person("youth", px, py, s, "bored75" if t < t_slam else "ceiling75", lean_add=fl, head_add=fh, shrug=fs,
                    hands={"n": PP.knee_tap(t), "f": {"curl": (.35, .4, .45, .5), "thumb": .3}}, **PP.sit_kw(px, py, s, "youth"))
    bx, by = px + 520 * s, py + 135 * s
    tb = small_table(bx - 95 * s / .3, bx + 95 * s / .3, by, floor - 40, 51)
    btn = P.shock_button(bx, by, s * 1.7, 0, 0, .25 + .2 * math.sin(t * 6), 0, 0, t, "top", 52)
    # высокое окошко со светом
    o.append(shape(rect_pts(700, 300, 900, 520), "#DCEBF2", line([(800, 300), (800, 520)], 6, "#F2EEE4", taper=0, seed=32240), w=4, seed=32241))
    o += [ch["shadow"], ch["back"], tb, ch["seat"], btn, fig["svg"]]
    return "".join(o)


def s08(t):
    lib.dyn_begin()
    o = [paper_bg()]
    t_st, t_pe, t_in = W(39), W(40), W(41)
    t_slam = t_in + .35
    bx, by, bk = B8
    # деревья качаются с кадра 0, листья летят
    for i, (tx, tk) in enumerate(((-40, 1.25), (1120, 1.3), (60, 1.6), (1000, 1.55))):
        o.append(tree_autumn(tx, by + 6, tk, t, i))
    o.append(blob(rect_pts(-300, by + 4, 1380, by + 900), "#C7C98A"))
    o.append(blob([(bx - 120, by + 4), (bx + 120, by + 4), (bx + 330, by + 900), (bx - 330, by + 900)], "#E9DFC6"))
    for j in range(16):
        gx = -200 + (j * 137) % 1500
        gy = by + 80 + (j * 53) % 420
        if abs(gx - bx) > 200 + (gy - by) * .25:
            o.append(line([(gx, gy), (gx + 8, gy - 22)], 3, "#8E9A55", taper=.6, seed=32310 + j) + line([(gx + 14, gy), (gx + 20, gy - 18)], 3, "#8E9A55",
                                                                                                         taper=.6, seed=32330 + j))
    o.append(line([(-300, by + 4), (1380, by + 4)], 4, "#7F8A4A", taper=.1, seed=32300))
    # штамп: тень растёт до удара, здание падает и пружинит
    if t < t_st:
        u = clamp((t - (t_st - .45)) / .45)
        o.append(blob(ellipse_pts(bx, by + 4, 420 * bk * (.4 + .6 * u), 30 * bk * (.4 + .6 * u), 18), "#6B5B3A", .08 + .16 * u))
        dropy = -900 * (1 - ease_in(u, 2))
        sq = (1.0, 1.0)
    else:
        dropy = 0.0
        sq = P.squash(t, t_st, .22, 3.2, 7)
    lights = clamp((t - t_st - .15) / .35)
    door = clamp((t_pe - .1 - t + .5) / .5) if False else clamp((t - (t_pe - .1)) / .2)
    bld = P.rotunda(0, 0, bk, lights, door, 0)
    if t >= t_st - .45:
        o.append(f'<g transform="translate({bx:.1f} {by + dropy:.1f}) scale({sq[0]:.4f} {sq[1]:.4f})">{bld}</g>')
    if t >= t_st and t < t_st + .3:
        o.append(P.dust_puff(bx - 300 * bk, by, 1.2, (t - t_st) / .3, 3) + P.dust_puff(bx + 300 * bk, by, 1.2, (t - t_st) / .3, 4))
    # человечки заходят в двери
    dxw, dyw = P.rotunda_door(bx, by, bk)
    for j in range(4):
        ts = t_pe - .1 + j * .12
        u = clamp((t - ts) / .55)
        if t < ts - .6 or u >= 1:
            continue
        side = -1 if j % 2 == 0 else 1
        sx = bx + side * (520 + 60 * j)
        xx = lerp(sx, dxw, ease_io(u))
        yy = by - 6 - lerp(0, 60 * bk, clamp((u - .6) / .4))
        sc = .15
        wk = PP.walk_kw(xx, yy - 300 * sc * .97, sc, t * 2.2 + j * .3, ["youth", "curly", "beard", "bald"][j])
        fig = PP.person(["youth", "curly", "beard", "bald"][j], wk["hip"][0], wk["hip"][1], sc, "", feet=wk["feet"], flip=(side > 0))
        op = 1 - clamp((u - .85) / .15)
        o.append(f'<g opacity="{op:.3f}">{fig["svg"]}</g>')
    o.append(falling_leaves(540, 600, t, 1, 7, 1.0))
    # камера: дрейф; на «оставляли» нырок в окно
    wx, wy = P.rotunda_window(bx, by, bk, 3)
    dive = clamp((t - t_in) / .32)
    dv = ease_in(dive, 2.4)
    win_w = 52 * bk                    # ширина окна в мире
    s_end = 1080 / win_w * 1.15
    s = lerp(1.0 + .04 * clamp((t - T0("s08")) / 2.4), s_end, dv) if dive > 0 else 1.0 + .04 * clamp((t - T0("s08")) / 2.4)
    cx = lerp(540 + 8 * math.sin(t * 1.3), wx, ease_out(dive, 2))
    cy = lerp(900, wy, ease_out(dive, 2))
    sh = P.shake(t, t_st, 12, .3, 3)
    cx += sh[0] / s
    cy += sh[1] / s
    rot = .5 * math.sin(t * 1.2)
    if dive > 0:
        # внутри окна — комната (рисуется в окне, растёт вместе с камерой)
        ww, wh = win_w, 120 * bk
        kk = ww / 1080 * 1.0
        inner = interior8(t, t_in, t_slam)
        cid = lib.clip_rect(wx - ww / 2 + 2, wy - wh / 2 + 2, ww - 4, wh - 4, 8 * bk)
        o.append(f'<g clip-path="url(#{cid})"><g transform="translate({wx - 540 * kk:.3f} {wy - 1100 * kk:.3f}) scale({kk:.6f})">{inner}</g></g>')
    if dive >= 1:
        sh2 = P.shake(t, t_slam, 14, .3, 9)
        return svg(f'<rect width="1080" height="1920" fill="{WALL}"/><g transform="translate({sh2[0]:.1f} {sh2[1] + 140:.1f}) '
                   f'scale(1.15) translate({-540 * .15 / 1.15:.1f} {-1100 + 960 / 1.15:.1f})">{interior8(t, t_in, t_slam)}</g>')
    return frame_svg("".join(o), cx, cy, s, rot * (1 - dive))


# ═══════════════════════════════ s10: трое в ряд ═══════════════════════════════
def s10(t):
    lib.dyn_begin()
    o = [paper_bg()]
    t2, t3, tu = W(51), W(52), W(55)
    o.append(lab_wall(330, 760, seed=1, bottom=False))
    o.append(blob(rect_pts(-300, 1020, 1380, 2600), FLOOR))
    o.append(line([(-300, 2400), (1380, 2400)], 5, INK, taper=0, seed=33001))
    # лампа под потолком качается
    la = 6 * math.sin(t * 2.2)
    o.append(P._tf(line([(0, 0), (0, 130)], 4, INK, taper=0, seed=33010) + shape([(-60, 170, 1), (-30, 130, 1), (30, 130, 1), (60, 170, 1)], "#b2bac0", "", w=3.4,
                                                                                    seed=33011), 300, 330, 1.0, la))
    # ряд уходит вглубь: первый дальше всех, третий ближе всех
    rows = [("beard", 670, 900.0, .4, [t2, tu]), ("youth", 410, 1200.0, .48, [t3, tu + .07]), ("bald", 185, 1540.0, .56, [])]
    for i, (who, px, floor, S, tps) in enumerate(rows):
        py = floor - 300 * S * PP.HEIGHT.get(who, 1.0) + 4
        bx, by = px + 470 * S, py + 120 * S
        if not tps:
            # третий: руки скрещены, косится на соседей
            look = (.75, -.7) if (t2 < t < t2 + .7 or t > tu - .1) else (-.25, .05)
            ex = {"brows": "skeptic", "mouth": "flat", "lid": .55, "look": look}
            ch = chair_side(px, py, S, floor, 70)
            fl, fh, fs = PP.fidget(t, .4, 5)
            fig = PP.person(who, px, py, S, ex, "cross", lean_add=-.04 + fl * .3, head_add=fh * .5 - .08 * (look[1] < 0), **PP.sit_kw(px, py, S, who))
            o += [ch["shadow"], ch["back"], pedestal(bx, by, floor, S / .3, 70), ch["seat"],
                  P.shock_button(bx, by, S * 1.5, 0, 0, .2 + .15 * math.sin(t * 6), 0, 0, t, "top", 72), fig["svg"]]
            continue
        rc, pr = 0.0, 0.0
        for tp in tps:
            r_, p_ = press_curve(t, tp, .14, .14, .25)
            rc, pr = max(rc, r_), max(pr, p_)
        if t < tps[0] - .4:
            rc = .2 + .2 * (.5 + .5 * math.sin(t * 5 + i * 2))   # рука уже тянется с кадра 0
        zu = max(zap_env(t, tp, .32) for tp in tps)
        hz = max(hair_env(t, tp) for tp in tps)
        sm = clamp((t - tps[0] - .2) / .3) if t > tps[0] else 0.0
        ex = "zap75" if zu > .05 else ("eye_btn75" if t < tps[0] else "manic75")
        body, fig = seated(who, px, py, S, floor, t, bx, by, S * 1.5, rc, pr, ex, zu, hz, sm, seed=60 + i * 9, fidget=1.0, stand=True)
        o.append(body)
    # камера: лёгкий наезд, тряска на каждой вспышке
    s = 1.0 + .05 * clamp((t - T0("s10") + .2) / 2.4)
    cx, cy = 540 + 6 * math.sin(t * 1.9), 1000
    for tp in (t2, t3, tu, tu + .07):
        sh = P.shake(t, tp, 14, .28, int(tp * 10))
        cx += sh[0] / s
        cy += sh[1] / s
    return frame_svg("".join(o), cx, cy, s, .4 * math.sin(t * 1.3))


# ═══════════════════════════════ s11: пулемёт нажатий ═══════════════════════════════
def s11(t):
    lib.dyn_begin()
    o = [paper_bg()]
    t_one, t_n, t_100, t_190, t_raz = W(57), W(58), W(59), W(60), W(61)
    floor = 1380.0
    S = .66
    o.append(lab_wall(-300, floor, seed=2, bottom=False))
    o.append(blob(rect_pts(-300, floor + 250, 1380, 2600), FLOOR))
    who = "beard"
    py = floor - 300 * S * PP.HEIGHT[who] + 4
    px = 250.0
    bx, by = px + 470 * S, py + 120 * S
    # нажатие на «нажал», потом пулемёт до «раз»
    mg = clamp((t - t_100) / .15) * (1 - clamp((t - WE(61)) / .2))
    if t < t_100:
        rc, pr = press_curve(t, t_n, .16, .16, .3)
        if t < t_n - .45:
            rc = .25 + .2 * (.5 + .5 * math.sin(t * 6))
    else:
        ph = (t * 14) % 1.0
        rc, pr = 1.0, (1 - abs(ph * 2 - 1)) ** .5 * mg + (1 - mg) * .2
    heat = ease_in(clamp((t - t_100) / (t_raz - t_100)), 1.4)
    zu = max(zap_env(t, t_n, .3), mg * (.6 + .4 * math.sin(t * 61)))
    hz = max(hair_env(t, t_n, .7), mg)
    rat = 6 * mg * (1 + heat)
    jx, jy = rat * math.sin(t * 67), rat * .5 * math.cos(t * 53)
    ex = "zap75" if t < t_100 and t > t_n else ("manic75" if t >= t_100 else "eye_btn75")
    body, fig = seated(who, px + jx, py + jy, S, floor, t, bx, by, S * 1.5, rc, pr, ex, zu, hz, clamp((t - t_n - .25) / .3) if t > t_n else 0.0,
                       seed=90, heat=heat, glow=.3 + .7 * heat, arc=mg, fidget=1.0 - mg, rattle=rat, fan=mg, stand=True)
    o.append(body)
    tgt = P.shock_button_top(bx, by, S * 1.5, 0, "top", pr)
    # молнии роятся вокруг (по кругу, лицо не пересекают), фонтан искр
    if mg > 0:
        hx, hy = fig["head"]
        R = 300 * S / .42 * .62
        for j in range(4):
            a = t * 4 + j * math.pi / 2
            p0 = (hx + R * math.cos(a), hy - 30 + R * .85 * math.sin(a))
            p1 = (hx + R * 1.15 * math.cos(a + .55), hy - 30 + R * .95 * math.sin(a + .55))
            o.append(P.zap(p0, p1, t, 300 + j, mg * .8, 12, 0))
        rs = P._rs(int(t * 30) + 7)
        for j in range(10):
            a = math.radians(rs.uniform(-160, -20))
            d = rs.uniform(40, 220)
            sx, sy = tgt[0] + math.cos(a) * d, tgt[1] + math.sin(a) * d
            o.append(line([(sx, sy), (sx + math.cos(a) * 22, sy + math.sin(a) * 22)], 7, "#FFD34A", taper=.5, wmin=.3, seed=330 + j, op=mg))
    flash = clamp(1 - abs(t - t_raz - .06) / .14) if t > t_raz - .08 else 0.0
    # камера: наезд с разгоном, нарастающая тряска
    u = clamp((t - (T0("s11") - .2)) / (t_raz - T0("s11") + .2))
    s = 1.0 + .32 * ease_in(u, 1.6)
    cx = lerp(560, (fig["head"][0] + tgt[0]) / 2, ease_io(u))
    cy = lerp(960, (fig["head"][1] + tgt[1]) / 2 + 40, ease_io(u))
    amp = 3 + 22 * mg * (.4 + .6 * heat)
    cx += amp * math.sin(t * 71) / s
    cy += amp * math.cos(t * 59) / s
    sh = P.shake(t, t_n, 14, .3, 4)
    cx += sh[0] / s
    cy += sh[1] / s
    return frame_svg("".join(o), cx, cy, s, .5 * math.sin(t * 1.4) + amp * .05 * math.sin(t * 37), P.flash_screen(flash * .85))


# ═══════════════════════════════ s14: Англия, автобус и справочник ═══════════════════════════════
WIN14 = (540.0, 760.0, 500.0, 560.0)    # окно на фасаде: центр, ширина, высота (мир)


def desk_scene(t, mode, head_u=0.0, yawn=0.0, flip=0.0, write=0.0, cups_u=None, sd=0):
    """Комната за окном (мир 1080×1920): человек (curly) за столом у справочника. mode "copy" — пишет; "rise" — поднимает голову.
    Возвращает (svg, fig, desk_top)."""
    o = [f'<rect x="-400" y="-400" width="1880" height="2720" fill="#EFE9DC"/>']
    for j in range(16):
        xx = -100 + j * 90
        o.append(line([(xx, 160), (xx - 70, 460)], 3, "#DED6C4", taper=.5, wmin=.2, seed=34000 + j))
    floor = 1640.0
    # окно на задней стене: серое небо и дождь
    wx0, wy0, wx1, wy1 = 470, 560, 900, 1000
    cid = lib.clip_rect(wx0, wy0, wx1 - wx0, wy1 - wy0)
    o.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="#AEB9C4"/>')
    o.append(f'<g clip-path="url(#{cid})">' + blob(rect_pts(wx0, wy0 + 260, wx1, wy1), "#8E7F78") +
             "".join(blob(rect_pts(wx0 + 20 + i * 110, wy0 + 200 + (i % 2) * 40, wx0 + 90 + i * 110, wy1), "#7A6C66") for i in range(4)) +
             P.rain_streaks(wx0, wy0, wx1, wy1, t, 9, 26, .9, .2, "#E8EEF3") + '</g>')
    o.append(shape(rect_pts(wx0, wy0, wx1, wy1), "none", "", w=5, seed=34030))
    o.append(line([(wx0, (wy0 + wy1) / 2 - 60), (wx1, (wy0 + wy1) / 2 - 60)], 12, "#F2EEE4", taper=0, wmin=1, seed=34031))
    o.append(shape(rect_pts(wx0 - 30, wy1, wx1 + 30, wy1 + 24), "#F2EEE4", "", w=3.4, seed=34032))
    o.append(blob(rect_pts(-400, floor, 1480, 2320), "#D6CCB8"))
    o.append(line([(-400, floor), (1480, floor)], 5, "#B9AE98", taper=.1, seed=34020))
    s = .62
    who = "curly"
    px = 300.0
    py = floor - 300 * s * PP.HEIGHT.get(who, 1.0) + 4
    top = py - 40
    ch = chair_side(px, py, s, floor, 80)
    o += [ch["shadow"], ch["back"]]
    # стол: столешница справа от человека
    tx0, tx1 = px + 110, px + 760
    o.append(small_table(tx0, tx1, top, floor, 81, "#C99A6B", "#A87C52"))
    if mode == "copy":
        pz = "head_arms" if head_u > 0 else "write"
        ex = "yawn75" if yawn > 0 and head_u < .5 else ("bored75" if head_u <= 0 else "sigh75")
        fl, fh, fs = PP.fidget(t, .5, 2)
        if head_u > 0:
            fig = PP.person(who, px, py, s, ex, "write", u_pose=("head_arms", ease_io(head_u)), head_add=fh * .3, **PP.sit_kw(px, py, s, who))
        else:
            fig = PP.person(who, px, py, s, ex, pz, lean_add=fl * .5, head_add=fh * .6 - .25 * yawn, **PP.sit_kw(px, py, s, who))
    else:
        fig = PP.person(who, px, py, s, "idea75" if head_u > .5 else "sigh75", "head_arms", u_pose=("lift_head", ease_io(head_u)), **PP.sit_kw(px, py, s, who))
    # справочник и лист на столе (под руками, перед телом)
    book = P.phone_book(px + 470, top - 95, .85, 0, flip, 5)
    sheet = P.sheet_lines(px + 240, top - 48, .7, 240, 150, write, 6, -4) if mode == "copy" else ""
    o += [ch["seat"]]
    if cups_u is None:
        o += [book, sheet]
    o.append(fig["svg"])
    if mode == "copy" and head_u <= 0:
        # ручка в пишущей руке
        wx, wy = fig["wrist"]["n"]
        o.append(P.pen(wx + 34, wy + 10, .45, 25 + 6 * math.sin(t * 13), 0, 7) if hasattr(P, "pen") else "")
    return "".join(o), fig, (tx0, tx1, top, px, py, s)


def facade(t, seed=0):
    o = []
    # кирпичный дом с большим окном
    o.append(shape(rect_pts(-160, 120, 1240, 1240), "#B5654A", "".join(
        line([(-160, 150 + j * 46), (1240, 150 + j * 46)], 2.2, "#8E4A34", taper=0, seed=34100 + j) for j in range(24)) +
        "".join(line([(-130 + (j % 2) * 60 + i * 120, 150 + j * 46), (-130 + (j % 2) * 60 + i * 120, 196 + j * 46)], 2.2, "#8E4A34", taper=0, seed=34400 + j * 13 + i)
                for j in range(24) for i in range(12)), w=5, seed=34120))
    for wx in (-90, 1170):      # соседние окна по краям
        o.append(shape(rect_pts(wx - 90, 520, wx + 90, 1000), "#3E4A5E", line([(wx, 520), (wx, 1000)], 8, "#F2EEE4", taper=0, seed=34125), w=4, seed=34126 + wx))
    x, y, w, h = WIN14
    o.append(shape(rect_pts(x - w / 2 - 26, y - h / 2 - 26, x + w / 2 + 26, y + h / 2 + 26), "#F2EEE4", "", w=4.4, seed=34121))
    o.append(shape(rect_pts(x - w / 2 - 50, y + h / 2 + 20, x + w / 2 + 50, y + h / 2 + 50), "#F2EEE4", "", w=4, seed=34122))
    return "".join(o)


def window_over(t, seed=0, rain_k=1.0):
    """Рама окна, стекло и капли поверх комнаты (в мире)."""
    x, y, w, h = WIN14
    o = [f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" fill="#BFDCEB" opacity=".22"/>']
    o.append(line([(x - w / 2 + 40, y - h / 2 + 60), (x - w / 2 + 120, y - h / 2 + 20)], 8, "#FFFFFF", taper=.4, seed=34130, op=.6))
    rs = P._rs(34140 + seed)
    for j in range(14):     # капли текут по стеклу
        ph = (t * rs.uniform(.3, .6) + rs.uniform(0, 1)) % 1.0
        dx = x - w / 2 + rs.uniform(20, w - 20)
        dy = y - h / 2 + ph * h
        o.append(line([(dx, dy - 30 * rain_k), (dx + 2, dy)], 4, "#9CC3DA", taper=.6, wmin=.3, seed=34150 + j, op=.8))
        o.append(blob(ellipse_pts(dx + 2, dy + 3, 5, 6, 8), "#9CC3DA", .85))
    o.append(shape([(x - w / 2, y - h / 2, 1), (x + w / 2, y - h / 2, 1), (x + w / 2, y + h / 2, 1), (x - w / 2, y + h / 2, 1)], "none", "", w=6, seed=34160)
             .replace('fill="none"', 'fill="none"'))
    ty = y - h * .3
    o.append(line([(x - w / 2, ty), (x + w / 2, ty)], 14, "#F2EEE4", taper=0, wmin=1, seed=34162))
    o.append(line([(x - w / 2, ty), (x + w / 2, ty)], 3, INK, taper=0, wmin=1, seed=34164, op=.6))
    return "".join(o)


def s14(t):
    lib.dyn_begin()
    t_en, t_15, t_sk, t_de = W(75), W(77), W(79), W(80)
    o = [f'<rect x="-600" y="-600" width="2280" height="3120" fill="#C9D2DA"/>']
    o.append(f'<rect x="-600" y="1240" width="2280" height="1200" fill="#7D8590"/>')
    o.append(line([(-600, 1240), (1680, 1240)], 5, INK, taper=0, seed=34200))
    o.append(blob(rect_pts(-600, 1240, 1680, 1290), "#A9B0B8"))
    for j in range(8):
        o.append(blob(rect_pts(-560 + j * 300, 1430, -420 + j * 300, 1446), "#F2EEE4", .8))
    o.append(facade(t))
    # комната в окне
    x, y, w, h = WIN14
    kk = w / 1080 * 1.18
    head_u = ease_io(clamp((t - t_de) / .35))
    yawn = clamp(1 - abs(t - (t_sk + .3)) / .45) if t > t_sk - .15 else 0.0
    flip = clamp((t - t_15) / .45)
    write = .2 + .5 * clamp((t - T0("s14") + .2) / 2.8)
    inner, fig, _ = desk_scene(t, "copy", head_u, yawn, flip, write)
    cid = lib.clip_rect(x - w / 2, y - h / 2, w, h)
    o.append(f'<g clip-path="url(#{cid})"><g transform="translate({x - 540 * kk:.3f} {y - 1250 * kk:.3f}) scale({kk:.5f})">{inner}</g></g>')
    o.append(window_over(t))
    # автобус проезжает на «Англии»
    ub = (t - (t_en - .55)) / 1.2
    if -0.1 < ub < 1.1:
        bxx = lerp(-560, 1680, ub)
        o.append(P.bus_red(bxx, 1440, 1.45, t, 0, 1.4))
        o.append(P.wind_lines(bxx - 420, 1200, 1.2, 1.0, t, 3, 4) if hasattr(P, "wind_lines") else "")
    o.append(P.rain_streaks(-200, -200, 1300, 2100, t, 4, 70, 1.3, .22))
    # камера: с улицы панорамой за автобусом и вверх в окно
    u = ease_io(clamp((t - (t_en + .2)) / .8))
    s = lerp(.92, 1080 / (w * 1.02), u)
    cx = lerp(540 + 60 * clamp((t - T0("s14")) / .8), x, u) + 5 * math.sin(t * 1.7)
    cy = lerp(1060, y + 30, u)
    if t > t_sk:
        s *= 1 + .05 * ease_out(clamp((t - t_sk) / .5))
    return frame_svg("".join(o), cx, cy, s, .4 * math.sin(t * 1.1))


# ═══════════════════════════════ s15: стаканчики становятся идеями ═══════════════════════════════
def s15(t):
    lib.dyn_begin()
    t_l, t_p, t_b, t_i = W(81), W(82), W(83), W(84)
    head_u = clamp((t - (t_l - .15)) / .35)
    inner, fig, (tx0, tx1, top, px, py, s) = desk_scene(t, "rise", head_u, cups_u=1)
    o = [inner]
    hx, hy = fig["head"]
    hs = fig["scale"]
    # исходная стопка перед ней на столе
    sx, sy = px + 380, top - 30
    tr = ease_io(clamp((t - t_p) / .35))
    fo = clamp((t - t_b) / (t_i + .3 - t_b))
    o.append(P.phone_book(px + 560, top - 70, .5, 0, 0, 5))
    if tr <= 0:
        o.append(P.cups(sx, sy, 1.15, 6, 1))
    # 1) шляпа на голову
    if tr > 0:
        hat_from = (sx, sy - 90)
        hat_to = (hx - 10 * hs / .2, hy - 330 * hs)
        hp = ease_io(clamp((t - t_p) / .3))
        hx_, hy_ = lerp(hat_from[0], hat_to[0], hp), lerp(hat_from[1], hat_to[1], hp) - 160 * math.sin(math.pi * hp)
        o.append(P.plastic_cup(hx_, hy_, 1.4, 180 * hp, "red", 3))
        o.append(P.sparkles(hx_, hy_ + 40, 1.0, clamp(1 - abs(hp - 1) * 3) if hp > .6 else 0, t, 3, 3))
        # 2) телефон-банка: два стаканчика разлетаются с ниткой
        cp = ease_out(clamp((t - t_p - .08) / .35), 2)
        c0 = (lerp(sx, sx - 120, cp), lerp(sy - 40, top - 400, cp))
        c1 = (lerp(sx, sx + 140, cp), lerp(sy - 40, top - 500, cp))
        o.append(P.cup_phone(c0, c1, 1.05, 30 * cp, 4, ("blue", "blue")))
        # 3) горшок с ростком
        gp = clamp((t - t_p - .15) / .4)
        o.append(P.cup_sprout(sx + 150, top - 12, 1.15, gp, t, 5))
        # 4) башенка
        tp_ = clamp((t - t_p) / .35)
        for j in range(3):
            q = clamp(tp_ * 3 - j)
            if q > 0:
                yy = sy + 30 - (j + (j % 2)) * 95 * 1.05 * q
                o.append(P.plastic_cup(sx + (j % 2) * 4, yy, 1.05, 180 if j % 2 else 0, "white", 10 + j))
        for j, (xx, yy, tt) in enumerate(((c0[0], c0[1] - 60, t_p + .3), (sx + 150, top - 150, t_p + .45), (sx, top - 330, t_p + .5))):
            if t > tt:
                o.append(P.sparkles(xx, yy, 1.1, clamp(1 - (t - tt) / .6), t, 20 + j, 4))
    # фонтан стаканчиков вокруг большой искры
    if fo > 0:
        cxs, cys = hx + 40, hy - 470 * hs / .62 * .62
        o.append(P.idea_spark(cxs, cys, 2.2, ease_out(clamp(fo * 2.2), 3) * (1 + .05 * math.sin(t * 9)), t, 7))
        rs = P._rs(35000)
        for j in range(8):
            ts = t_b + j * .045
            q = t - ts
            if q <= 0:
                continue
            u = ease_out(clamp(q / .45), 3)
            a = math.radians(-195 + 210 * (j + .5) / 8 + 10 * math.sin(t * 3 + j))
            R = 280 + 30 * math.sin(j * 1.7)
            tx_, ty_ = cxs + R * math.cos(a), cys - 30 + R * .75 * math.sin(a)
            fx = lerp(sx, tx_, u)
            fy = lerp(sy - 40, ty_, u) - 260 * math.sin(math.pi * u) * (1 - u)
            col = ["red", "blue", "yellow", "white"][j % 4]
            o.append(P.plastic_cup(fx, fy + 45, 1.0, (1 - u) * 300 * (1 if j % 2 else -1) + 15 * math.sin(t * 5 + j), col, 30 + j))
    # камера: наезд, искры подталкивают вверх
    sc = 1.55 + .12 * ease_io(clamp((t - T0("s15") + .2) / 2.0))
    up = 150 * ease_out(clamp((t - t_b) / .5))
    cx = 540 + 8 * math.sin(t * 1.6)
    cy = 1170 - up
    sh = P.shake(t, t_p, 8, .25, 2)
    return frame_svg("".join(o), cx + sh[0], cy + sh[1], sc * .98, .3 * math.sin(t * 1.2))


SCENES = {"s03": s03, "s08": s08, "s10": s10, "s11": s11, "s14": s14, "s15": s15}


def frame(sid, t):
    return SCENES[sid](t)
