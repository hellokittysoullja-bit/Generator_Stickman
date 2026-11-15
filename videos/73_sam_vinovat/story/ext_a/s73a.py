"""Рилс 73 «Ты сам виноват», группа A: графика и доска.
s02 (1.70–2.80): графика на холодной бумаге — молоток на подставке подрагивает; «ты» (1.76) сверху входит лапа кота и берёт молоток
    за ручку; «сам» (2.00) замах; «виноват» (удар ≈2.45) — молоток бьёт по подставке: штрихи удара, подскок, пыль, тряска камеры.
s05 (5.80–6.90): лапа кота выталкивает к зрителю пустой пузырь комментария (серые волнистые черты); «Пиши» (5.86) пузырь растёт;
    «что я» (6.20) коготь подталкивает ближе; «неправ» (≈6.65) стук когтем — пузырь вздрагивает; свет гаснет к краям; наезд с разгоном
    в склейку 6.90.
s16 (21.62–23.22): доска с пустыми карточками и конвертами в тёплом свете ночника; кот идёт шагом по полке под доской, присматривается;
    «самое старое» (22.55–23.21) лапой вытягивает из-под других самую пыльную карточку в паутине, на «старое» (22.86) паутина рвётся,
    облачко пыли. Камера — панорама за котом, на «старое» наезд 5 %.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Предметы — common/props.py, кот — common/people.py / cat.py, место — room.py."""
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
import room as R  # noqa: E402
from lib import clamp, ease_in, ease_io, ease_out, line, svg  # noqa: E402

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?:«»").lower() == word:
            return w["start"]
    raise KeyError(word)


def lerp(a, b, u):
    return a + (b - a) * u


def frame_svg(body, cx, cy, s, rot, bg, over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


PAPER = "#E3E8EE"
GRID = "#CDD5DE"


def paper_bg(col=PAPER, grid=GRID):
    d = "".join(f"M-900 {i * 64}H2600" for i in range(-14, 46)) + "".join(f"M{i * 64} -900V2800" for i in range(-14, 42))
    return (f'<path d="M-900 -900H2600V2800H-900Z" fill="{col}"/>'
            f'<path d="{d}" stroke="{grid}" stroke-width="2" fill="none"/>')


def vignette(u, col="#0b0f1c"):
    if u <= .01:
        return ""
    g = lib.rad_grad([(0, col, 0), (.45, col, 0), (1, col, 1)], 540, 900, 760, 1150)
    return f'<rect width="1080" height="1920" fill="url(#{g})" opacity="{min(1, u):.3f}"/>'


# ═══════════════════════════════ s02: молоток ═══════════════════════════════
T2_TY = wt("ты")                  # 1.76
T2_SAM = wt("сам")                # 2.00
T2_HIT = 2.45                     # ударный слог «ват»
KG = 1.55
BLOCK = (430.0, 1120.0)
KB = 1.6
_fx, _fy = P.gavel_face(0, 0, KG, 0)
GRIP0 = (BLOCK[0] - _fx + 20, BLOCK[1] - 44 * KB - _fy + 4)       # хват, при котором ударная грань ложится на подставку
PAW_K = 1.45


def _gavel_state(t):
    """(хват x, y, угол) молотка."""
    gx, gy = GRIP0
    if t < T2_SAM:
        a = 5 + 2.5 * math.sin(t * 31) + 1.5 * math.sin(t * 17)            # дрожит, чуть приподнят
        if t > T2_TY + .2:
            a = lerp(a, 9, clamp((t - T2_TY - .2) / .1))
        return gx, gy - 6, a
    if t < T2_HIT - .09:
        u = ease_out(clamp((t - T2_SAM) / (T2_HIT - .09 - T2_SAM)), 2)
        return gx + 40 * u, gy - 6 - 110 * u, lerp(9, 50, u)
    if t < T2_HIT:
        u = ease_in(clamp((t - (T2_HIT - .09)) / .09), 3)
        return gx + 40 * (1 - u), gy - 116 * (1 - u), lerp(50, 0, u)
    q = t - T2_HIT
    return gx, gy, 9 * math.exp(-q * 7) * abs(math.sin(q * 15))           # отскок


def s02(t):
    lib.dyn_begin()
    o = [paper_bg()]
    gx, gy, a = _gavel_state(t)
    q = t - T2_HIT
    bounce = math.exp(-q * 9) if q >= 0 else 0.0
    o.append(R.cold_tint(P.gavel_block(*BLOCK, KB, bounce=bounce, seed=2), .7))
    o.append(R.cold_tint(P.gavel(gx, gy, KG, a, t, seed=2), .7))
    # лапа кота сверху: входит на «ты» и держит ручку до конца
    e = ease_out(clamp((t - T2_TY) / .2), 3)
    if e > 0:
        tip = (gx + 4, gy - 4)
        base = (tip[0] + 230, tip[1] - 620)
        tip = (lerp(base[0] - 60, tip[0], e), lerp(base[1] + 200, tip[1], e))
        o.append(people.cat_forearm(base, tip, PAW_K, claw=.6 * e, seed=21))
    # пыль на ударе
    if q >= 0:
        fx, fy = P.gavel_face(gx, gy, KG, a)
        o.append(P.dust_puff(fx - 70, fy, 1.0, clamp(q / .6), seed=4))
        o.append(P.dust_puff(fx + 80, fy + 6, .8, clamp((q - .03) / .55), seed=9))
    # камера: микродрейф вниз, на ударе тряска и отскок 4 %
    sx, sy = P.shake(t, T2_HIT, 22, .3, seed=3)
    s = 1.42 * (1.0 + .04 * math.exp(-max(0, q) * 8) * (q >= 0))
    cy = BLOCK[1] - 200 + 25 * clamp((t - 1.5) / 1.5)
    return frame_svg("".join(o), BLOCK[0] + 175 - sx / 1.42, cy - sy / 1.42, s, 0.0, PAPER)


# ═══════════════════════════════ s05: пузырь комментария ═══════════════════════════════
T5_PISH = wt("пиши")              # 5.86
T5_CHTO = wt("что", 6.0)          # 6.20
T5_TAP = 6.65                     # ударный слог «прав»
T5_CUT = 6.90


def _bubble_state(t):
    """(x, y, k, wobble)."""
    if t < T5_PISH:
        x, y, k = 600, 900, 2.1
    else:
        u = ease_out(clamp((t - T5_PISH) / .3), 3)
        x, y, k = lerp(600, 520, u), lerp(900, 760, u), lerp(2.1, 3.3, u)
        u2 = ease_out(clamp((t - T5_CHTO) / .2), 2)
        y -= 20 * u2
        k += .45 * u2
    wb = .5 * math.sin(t * 9) * math.exp(-max(0, t - 5.6) * 1.4)            # качается на кадре 0
    for t0, amp in ((T5_PISH, .45), (T5_CHTO, .35), (T5_TAP, .7)):
        q = t - t0
        if q > 0:
            wb += amp * math.exp(-q * 7) * math.sin(q * 34)
    return x, y, k, wb


def _waves(x, y, k, wb, t, tremble):
    sx, sy = 1 + .14 * wb, 1 - .14 * wb
    o = []
    for j, (yy, ww) in enumerate(((-28, 60), (0, 66), (28, 38))):
        pts = []
        for q in range(9):
            px = -ww + 2 * ww * q / 8
            jit = tremble * 4 * math.sin(t * 60 + q * 2.1 + j)
            pts.append((px, yy + (6 if q % 2 else -6) + jit))
        o.append(line(pts, 6.0, "#8C94A2", taper=.3, wmin=.4, seed=5300 + j))
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({6 * wb:.2f}) scale({k * sx:.4f} {k * sy:.4f})">{"".join(o)}</g>'


def s05(t):
    lib.dyn_begin()
    o = [paper_bg()]
    x, y, k, wb = _bubble_state(t)
    o.append(P.comment_bubble(x, y, k, icon="none", u=1.0, wobble=wb, seed=5, tail=(-50, 55)))
    q = t - T5_TAP
    tremble = math.exp(-q * 5) if q > 0 else .25
    o.append(_waves(x, y, k, wb, t, tremble))
    # лапа: из правого нижнего угла упирается в правый край пузыря; на «что я» и «неправ» выпускает коготь
    push = 0.0
    for t0 in (T5_CHTO, T5_TAP):
        qq = t - t0
        if -.08 < qq < .25:
            push = max(push, math.sin(math.pi * clamp((qq + .08) / .33)))
    tip = (x + 100 * k + 20 - 30 * push, y + 50 * k + 16 - 10 * push)
    base = (tip[0] + 260, tip[1] + 520)
    claw = clamp(push * 1.5)
    o.append(people.cat_forearm(base, tip, 2.3, claw=claw, seed=51))
    # камера: наезд с разгоном к пузырю в склейку 6.90
    u = ease_in(clamp((t - 6.2) / (T5_CUT - 6.2)), 2.4)
    s = 1.0 + .35 * u
    cx = lerp(600, x + 90, .5 * u)
    cy = lerp(900, y, .8 * u)
    dark = .25 + .75 * ease_in(clamp((t - 6.1) / .8), 1.6)
    return frame_svg("".join(o), cx, cy, s, -.6 * u, PAPER, vignette(dark))


# ═══════════════════════════════ s16: доска, кот вытягивает самую старую карточку ═══════════════════════════════
T16_DOL = wt("дольше")            # 21.65
T16_SAM = wt("самое")             # 22.55
T16_OLD = wt("старое")            # 22.86
SHELF_Y = 1000.0
KC = 1.0
CARDS16 = [   # (тип, x, y, swing0, dust, col, seed)
    ("card", -1235, 400, -3, .15, "#F7DC6F", 1),
    ("env", -1035, 370, 2, .35, None, 2),
    ("card", -830, 420, 4, .1, "#9FD0EA", 3),
    ("card", -650, 390, -2, .2, "#F4A6B7", 4),
    ("card", -700, 660, 3, .3, "#B6DE8E", 5),
]
OLD_PIN = (-1125.0, 800.0)
OVER16 = ("env", -1010, 690, -3, .45, None, 6)       # конверт, под которым прячется старая карточка
CAT_X0, CAT_X1 = -560.0, -880.0
PAW_DX = 110.0


def _cat16(t):
    """x кота, поза st, хват (кончик лапы) или None."""
    wu = clamp((t - 21.42) / (22.25 - 21.42))
    x = lerp(CAT_X0, CAT_X1, ease_io(wu) * .2 + wu * .8)
    walking = wu < 1
    st = {"turn": -.55, "look": (-.6, -.5), "tail": 6 * math.sin(t * 5), "flame_e": 1.3}
    if not walking:
        sn = clamp((t - 22.25) / .3)
        st.update(tilt=6 * sn + 2 * math.sin(t * 14) * sn, look=(-.5, -.9), turn=-.4)
    reach = 0.0
    if t >= T16_SAM:
        reach = ease_out(clamp((t - T16_SAM) / .22), 2)
        pull = ease_io(clamp((t - T16_OLD) / .3))
        reach = reach * (1 - .45 * pull)
        st.update(paw_l=reach, paw_l_dx=PAW_DX, look=(-.5, -.6 + .9 * pull), smile=1.0 if t > T16_OLD + .2 else 0.0)
    return x, st, walking


def s16(t):
    lib.dyn_begin()
    d = R.bedroom(t, "lamp", "board")
    Pl = d["P"]
    o = [d["bg"], d.get("light", "")]
    # полка под доской
    o.append(lib.shape(lib.rect_pts(-1420, SHELF_Y, -470, SHELF_Y + 34), "#9a6b44", lib.blob(lib.rect_pts(-1420, SHELF_Y + 20, -470, SHELF_Y + 36), "#7a5034"),
                       w=4.0, seed=1601))
    for bx in (-1340, -560):
        o.append(lib.shape([(bx - 12, SHELF_Y + 34, 1), (bx + 12, SHELF_Y + 34, 1), (bx + 4, SHELF_Y + 110, 1)], "#7a5034", "", w=3.4, seed=1602 + bx % 7))
    items = []
    for kind, x, y, sw0, dust, col, sd in CARDS16:
        sw = sw0 + 1.2 * math.sin(t * 2.2 + sd)
        items.append(P.pinned_envelope(x, y, .9, sw, dust, 0.0, t=t, seed=sd) if kind == "env" else
                     P.pinned_card(x, y, 1.0, sw, dust, 0.0, t=t, seed=sd, col=col))
    # самая старая карточка: в паутине, под конвертом; на «старое» паутина рвётся и карточка уезжает с лапой
    x, st, walking = _cat16(t)
    tip = people.cat_paw_tip(x, SHELF_Y, KC, st, "l") if st.get("paw_l", 0) > .02 else None
    pull = ease_io(clamp((t - T16_OLD) / .3))
    torn = clamp((t - T16_OLD) / .18)
    cx_, cy_ = OLD_PIN
    if pull > 0 and tip is not None:
        cx_ = lerp(OLD_PIN[0], tip[0] - 6, pull)
        cy_ = lerp(OLD_PIN[1], tip[1] - P.CARD_H + P.CARD_PIN + 18, pull)
    sw_old = 1.5 * math.sin(t * 3) - 14 * pull
    tug = 0.0
    if T16_SAM + .2 < t < T16_OLD:
        tug = 3 * math.sin((t - T16_SAM) * 40)
    web_l = P.cobweb(OLD_PIN[0] - 95, OLD_PIN[1] - 26, 1.0, tremble=min(1, abs(tug) / 2 + .2), torn=torn, t=t, ang=10, span=80, L=150, seed=61)
    web_r = P.cobweb(OLD_PIN[0] + 95, OLD_PIN[1] - 26, .9, tremble=min(1, abs(tug) / 2 + .2), torn=torn, t=t, ang=100, span=80, L=140, seed=62)
    o.append(R.light_tint("".join(items), Pl))
    old_card = R.light_tint(P.pinned_card(cx_, cy_ + tug * .5, 1.0, sw_old + tug, 1.0, 0.0, t=t, seed=7, col="#E9E1CC", pin=pull < .05), Pl)
    if pull < .05:
        o.append(old_card)
    else:
        o.append(R.light_tint(P.push_pin(*OLD_PIN, .9), Pl))
    kind, ox, oy, osw, odust, ocol, osd = OVER16
    o.append(R.light_tint(P.pinned_envelope(ox, oy, .9, osw + 1.2 * math.sin(t * 2.2) + tug * .4, odust, 0.0, t=t, seed=osd), Pl))
    o.append(web_l + web_r)
    # кот
    if walking:
        cs = people.cat_walk(x, SHELF_Y, KC, t, st, period=.42)
    else:
        cs = people.cat_svg(x, SHELF_Y, KC, st, t)
    o.append(R.warm_tint(cs, 1.0))
    if pull >= .05:      # вытянутая карточка — перед котом, в лапе
        o.append(old_card)
    o.append(P.dust_puff(OLD_PIN[0] - 40, OLD_PIN[1] + 10, .9, clamp((t - T16_OLD) / .7), seed=16))
    # камера: панорама за котом, на «старое» наезд 5 %
    cam_x = x - 120
    q = t - T16_OLD
    s = 1.75 * (1 + .05 * ease_out(clamp(q / .25), 2)) if q > 0 else 1.75
    cam_y = 790 + 25 * ease_out(clamp(q / .25), 2) * (q > 0)
    return frame_svg("".join(o), cam_x, cam_y, s, 0.0, "#2a1c18")


SHOTS = {"s02": s02, "s05": s05, "s16": s16}


def frame(sid, t):
    return SHOTS[sid](t)
