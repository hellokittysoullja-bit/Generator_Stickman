"""Рилс 77 «СДВГ не бывает?», группа A: предметы и графика — s05, s06, s08, s11, s13, s16, s19.
Время — ТОЛЬКО из shots.json (t0/t1 плана) и voice/words.json (слово по индексу wN); числа в коде — длительности движений.
s05 торт: свечи цепочкой с «пока» (w12), разом вспыхивают «сорок» (w15), отец задувает «лет» (w16); наезд, тряска огней.
s06 опросник: галочка «узнал» (w18), остальные «что» (w19) … «него» (w21); «СДВГ» (w22) — очки сняты, откинулся, лапа кота на руке.
s08 ключи (бумага): веер «семи» (w28), звон «вопросам» (w29), Дима вбегает «лень» (w30), ключ в скважину «тебя» (w32),
    крышка вздрагивает и щель светится «или» (w33) – «нет» (w34), не открывается.
s11 забор: панорама вдоль забора, граница покраски на середине «всю жизнь» (w50–w51), кисть падает «бросал» (w52), отец уходит.
s13 штора гаража: тянет «Оказалось» (w60), на ладонь «мозгу» (w62), с грохотом вниз «начать» (w64), пыль «скучное» (w65).
s16 доски (бумага): зеленеют одна за другой с «маленькому» (w80), «шагу» (w81), у каждой отпечаток лапы.
s19 рамка с фото: лапа поправляет рамку, блик «фото» (w95).
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
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, rect_pts, shape, svg  # noqa: E402

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


def A(sid):
    return max(0.0, T0(sid) - .2)


def B(sid):
    return T1(sid) + .2


def lerp(a, b, u):
    return a + (b - a) * u


def ramp(t, a, d):
    return clamp((t - a) / d)


def wob(t, f, ph=0.0):
    return math.sin(t * f + ph)


def frame_svg(body, cx, cy, s, rot, bg="#FBF3DC", over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def paper_bg(col=None, grid="#E3D9BE"):
    d = "".join(f"M-900 {i * 64}H2600" for i in range(-14, 80)) + "".join(f"M{i * 64} -900V5000" for i in range(-14, 42))
    return (f'<path d="M-900 -900H2600V5000H-900Z" fill="{col or P.C_PAGE}"/>'
            f'<path d="{d}" stroke="{grid}" stroke-width="2" fill="none"/>')


def shadow(x, y, rx, op=.13, col="#6B5B3A"):
    return blob(ellipse_pts(x, y, rx, rx * .14, 18), col, op)


def punch(t, t0, amp=.06, dur=.32):
    """Удар-наезд: быстро вверх, затухающий отскок (множитель масштаба)."""
    if t < t0:
        return 1.0
    u = (t - t0) / dur
    return 1 + amp * math.exp(-3.2 * u) * math.cos(min(u, 3) * 2.2) if u < 3 else 1.0


def fall(t, t0, y0, y1, dur=.32):
    """Падение с ускорением до y1 и маленький отскок."""
    if t <= t0:
        return y0, 0.0
    u = (t - t0) / dur
    if u < 1:
        return y0 + (y1 - y0) * u * u, u
    v = u - 1
    return y1 - 26 * math.exp(-4 * v) * abs(math.sin(v * 5)), 1.0


def cat_st(t, **kw):
    st = dict(blink=1.0 if (t % 3.1) < .09 else 0.0, tail=6 * wob(t, 2.3), breath=1)
    st.update(kw)
    return st


# ═══════════════════════════════ тёмная кухня (s05, s06) ═══════════════════════════════
C_WALL_N = "#1F2546"
C_WALL_N2 = "#283058"
C_FLOOR_N = "#161A33"


def night_room(x0=-600, x1=1700, floor=1500, tile=True):
    o = [blob(rect_pts(x0, -800, x1, floor), C_WALL_N), blob(rect_pts(x0, floor, x1, 2600), C_FLOOR_N)]
    if tile:      # кафельный фартук — едва видные швы
        d = "".join(f"M{x0} {y}H{x1}" for y in range(820, floor, 90)) + "".join(f"M{x} 820V{floor}" for x in range(x0, x1, 90))
        o.append(f'<path d="{d}" stroke="{C_WALL_N2}" stroke-width="3" fill="none"/>')
    o.append(line([(x0, floor), (x1, floor)], 5, "#0E1124", taper=.1, wmin=.8, seed=7701))
    return "".join(o)


def pendant(x, y, k, swing, on=1.0, cord=520.0):
    """Подвесная лампа: шнур от (x, y−cord) вниз, абажур в (x, y) с качанием swing (°). Вернёт (svg, центр света)."""
    a = math.radians(swing)
    top = (x - math.sin(a) * cord * k, y - math.cos(a) * cord * k)
    lx, ly = x, y
    o = [line([top, (lx, ly - 40 * k)], 4 * k, "#0B0D18", taper=.05, wmin=.9, seed=7702)]
    shade = lib.T([(-90, 30, 1), (-40, -40), (40, -40), (90, 30, 1)], lx, ly, k, swing)
    o.append(shape(shade, "#C99A3B", blob(lib.T([(20, -40), (90, 30), (40, 30)], lx, ly, k, swing), "#9E7528", .8), w=4 * k, seed=7703))
    bx, by = lib.T([(0, 34)], lx, ly, k, swing)[0]
    o.append(shape(ellipse_pts(bx, by, 26 * k, 18 * k, 12), "#FFF3C4", "", w=2.6 * k, seed=7704))
    return "".join(o), (bx, by)


# ═══════════════════════════════ s05: торт с лесом свечей ═══════════════════════════════
def s05(t):
    lib.dyn_begin()
    a = A("s05")
    w_pok, w_sam, w_sor, w_let = ws(12), ws(13), ws(15), ws(16)
    # свечи: две уже горят с первого кадра; цепочка с «пока» до «сорок» — ~60 %, на «сорок» — все разом
    lit = .05 + .55 * ease_in(ramp(t, w_pok, w_sor - w_pok), 1.3)
    flare = 0.0
    if t >= w_sor:
        lit = 1.0
        flare = math.exp(-(t - w_sor) * 5) * 1.0
    blow = ease_out(ramp(t, w_let + .04, .5), 2)
    o = [night_room(floor=1560)]
    o.append(P.kitchen_table(540, 1300, 1500, 1.0, 0, seed=5, depth=300))
    # отец сидит за столом лицом вправо, к торту; дует на «лет»
    ub = ease_out(ramp(t, w_let - .12, .18), 2)
    fa = people.father(330, 1210, .95, None, ("sit", "blow"), t, ub, breath=True,
                       head_add=-.04 * ease_out(ramp(t, w_sor, .2)) + .02 * wob(t, 2.1), look=(.75, .35))
    o.append(fa["svg"])
    hx, hy = fa["head"]
    sc = fa["scale"]
    hat_rot = 18 + 4 * wob(t, 3.1) - 10 * ub
    o.append(P.party_hat(hx - 10 * sc, hy - 120 * sc, .75, hat_rot, seed=5))
    # торт
    ck = 1.45
    cx, cy = 720, 1215
    o.append(shadow(cx, cy + 8, 300, .25, "#05060E"))
    o.append(P.candle_cake(cx, cy, ck, lit, blow, t, flare, n=40, seed=5))
    # свет свечей: растёт с числом огней, вспышка на «сорок», гаснет при задувании
    light = (.25 + .75 * lit) * (1 - .85 * blow) + .5 * flare
    dark = P.darkness(.78 - .25 * light, "#070A1C",
                      holes=[(P.circle_d(cx, cy - 330, 470 + 120 * flare, 360 + 80 * flare), clamp(.35 + .6 * light)),
                             (P.circle_d(hx + 60 * sc, hy + 60 * sc, 260, 300), clamp(.2 + .6 * light))],
                      blur_sd=60, box=(-600, -600, 1800, 2600))
    o.append(dark)
    o.append(P.cake_glow(cx, cy, ck, .35 * light))
    o.append(P.glow(hx + 80 * sc, hy + 140 * sc, 240, .25 * light + .3 * flare, "#FFB453"))
    # дым после задувания
    # камера: медленный наезд к торту; дрожь огней на «сорок»
    u = (t - a) / (B("s05") - a)
    s = 1.32 + .12 * ease_io(u)
    sh = P.shake(t, w_sor, 9, .3, seed=5)
    ccx = lerp(610, 660, ease_io(u)) + sh[0]
    ccy = lerp(930, 960, ease_io(u)) + sh[1]
    return frame_svg("".join(o), ccx, ccy, s, .4 * wob(t, 1.3), bg="#070A1C")


# ═══════════════════════════════ s06: опросник, очки ═══════════════════════════════
def s06(t):
    lib.dyn_begin()
    a = A("s06")
    w_uz, w_chto, w_nego, w_sd = ws(18), ws(19), we(21), ws(22)
    # галочки: первая на «узнал», остальные шесть — с «что» по конец «него»
    ticks = (ease_out(ramp(t, w_uz + .05, .25)) + 6 * ramp(t, w_chto, w_nego - w_chto)) / 7
    off = ease_io(ramp(t, w_sd, .55))               # очки снимаются
    back = ease_out(ramp(t, w_sd + .25, .6), 2)       # откидывается
    o = [night_room(floor=1560)]
    sw = 3.5 * wob(t, 2.2)
    lamp, lc = pendant(560, 300, 1.0, sw)
    o.append(P.kitchen_table(540, 1300, 1500, 1.0, 0, seed=6, depth=300))
    hip = (300 - 30 * back, 1250)
    fa = people.father(hip[0], hip[1], .86, "stunned" if t >= w_sd else "tired", ("sit", "glasses_off"), t, off, lean_add=-.12 * back,
                       head_add=-.06 * back, glasses=1.0 - off, look=(.55, .55) if t < w_sd else (.15, .05))
    # лист на столе справа от него, чуть дрожит после «СДВГ»
    lx, ly = 960, 960
    o.append(P.checklist(lx, ly, .86, ticks, t, rot=5, shake=2.5 * ramp(t, w_sd, .2), seed=6))
    o.append(fa["svg"])
    # очки в руке после снятия
    if off > .55:
        hx, hy = fa["hold"]
        o.append(P.glasses(hx + 6, hy - 10, 1.1, -20 + 10 * wob(t, 2), fold=ramp(t, w_sd + .4, .3)))
    # кот сидит на столе между отцом и листом и тихо кладёт лапу ему на руку (на «СДВГ»)
    paw = ease_io(ramp(t, w_sd + .15, .5))
    ck = .72
    cxp, cyp = 700, 1215
    hfx, hfy = fa["wrist"]["n"]
    pdx = max(40.0, ((cxp - hfx) / ck - 25) / 1.6)
    st = cat_st(t, turn=-.5, look=(-.6, .25), ear=.2, paw_l=paw, paw_l_dx=pdx, tilt=-5 * paw)
    o.append(shadow(cxp, cyp + 4, 120, .3, "#05060E"))
    o.append(people.cat_svg(cxp, cyp, ck, st, t))
    # свет лампы: пятно на столе и лице, остальное в синем сумраке
    hx, hy = fa["head"]
    dark = P.darkness(.6, "#070A1C", holes=[(P.circle_d(lc[0] + 20, 1050, 520, 360), .9), (P.circle_d(hx, hy, 230, 250), .7)],
                      blur_sd=50, box=(-600, -600, 1800, 2600))
    o.append(dark)
    o.append(lamp)
    o.append(P.glow(lc[0], lc[1] + 30, 170, .9, "#FFE29A"))
    o.append(P.glow(lc[0] + 30, 1100, 420, .25, "#FFCF7A", ry=260))
    # камера: медленный наезд на лист, на «СДВГ» мягкий отъезд к лицу отца
    u = ease_io(ramp(t, a, w_sd - a))
    v = ease_io(ramp(t, w_sd, .9))
    s = lerp(1.25, 1.36, u) - .1 * v
    ccx = lerp(lerp(640, 700, u), hx + 220, v)
    ccy = lerp(lerp(900, 930, u), hy + 330, v)
    return frame_svg("".join(o), ccx, ccy, s, .3 * wob(t, 1.1), bg="#070A1C")


# ═══════════════════════════════ s08: ключи и сундучок (бумага) ═══════════════════════════════
def s08(t):
    lib.dyn_begin()
    a = A("s08")
    w_sem, w_vop, w_len, w_teb, w_ili, w_net = ws(28), ws(29), ws(30), ws(32), ws(33), ws(34)
    fan = ramp(t, w_sem - .06, (w_vop + .1) - (w_sem - .06))
    jingle = math.exp(-max(0.0, t - w_vop) * 3) if t >= w_vop else .3
    o = [paper_bg()]
    ground = 1260
    # сундучок
    chx, chy, chk = 720, ground, 1.25
    shake = 0.0
    if t >= w_ili:
        shake = clamp(1 - (t - w_ili) / .5) + .6 * clamp(1 - abs(t - w_net - .05) / .25)
    glow_ = ease_out(ramp(t, w_ili + .05, .4)) * (.75 + .25 * wob(t, 9))
    o.append(shadow(chx, chy, 220, .16))
    o.append(P.small_chest(chx, chy, chk, shake, glow_, t, seed=8))
    # Дима вбегает справа на «лень» и смотрит на сундук (лицом влево)
    run = ease_out(ramp(t, w_len - .05, .5), 2)
    if t >= w_len - .05:
        dx = lerp(1450, 1010, run)
        dk = .72
        hip0 = ground - 640 * dk
        if run < .98:
            # шаг считаем вправо вокруг зеркальной точки и отражаем фигуру
            wk = people.walk_kw(dx, hip0, dk, (t - w_len) * 2.6, stride=300, lift=90)
            fe, hy = wk["feet"], wk["hip"][1]
        else:
            fe, hy = people.stand_kw(dx, hip0, dk)["feet"], hip0
        dm = people.dima(dx, hy, dk, "look77", None, feet=fe, flip=True,
                         head_add=.05 * wob(t, 2.0) + .1 * ease_out(ramp(t, w_ili, .3)), lean_add=.08 * (1 - run))
        o.append(shadow(dx, ground + 4, 120, .14))
        o.append(dm["svg"])
    # кот с кольцом ключей в зубах слева; на «тебя» шагает к сундуку и вставляет ключ в скважину
    ck = 1.0
    ins = ease_io(ramp(t, w_teb - .4, .4))
    khx, khy = P.chest_keyhole(chx, chy, chk)
    kk = 1.4
    reach = (35 + 26 + 132 - 40) * kk           # от центра кольца до вошедшего в скважину кончика
    cx1 = khx - reach - 6 * ck
    my1 = ground + (1132 - 1306 + 70 * .75) * ck
    cx = lerp(330, cx1, ins)
    walk = (t - (w_teb - .4)) * 2.2 if 0 < ins < 1 else None
    drop = .75 * ins
    st = cat_st(t, turn=.5 * ins + .15, look=(.5, .2 + .3 * ins), ear=.3 * wob(t, 3), walk=walk, drop=drop)
    o.append(shadow(cx, ground + 4, 160, .15))
    o.append(people.cat_svg(cx, ground, ck, st, t))
    mx, my = cx + 6 * ck, ground + (1132 - 1306 + 70 * drop) * ck      # рот кота (опущенная голова — ниже)
    if ins > 0:      # ведущий ключ к скважине, кольцо — у рта
        mx, my = lerp(mx, khx - reach, ins), lerp(my, khy, ins)
    o.append(P.key_ring(mx, my, kk, fan, t, seed=8, jingle=jingle * (1 - ins), lead=(0, -90.0, ins) if ins > 0 else None))
    # щелчки веера — искорки
    for i in range(7):
        ti = w_sem - .06 + (i + .5) / 7 * ((w_vop + .1) - (w_sem - .06))
        u = clamp((t - ti) / .3)
        if 0 < u < 1 and ins <= 0:
            tx_, ty_ = P.key_ring_tip(mx, my, kk, fan, i)
            o.append(P.sparkles(tx_, ty_, .7, 1 - u, t, seed=80 + i, n=3, r=55))
    # камера: дрейф вправо за ключами (крупно кот и ключи), с «лень» — шире, на «нет» короткий наезд на щель
    u = ease_io(ramp(t, a, w_len - a))
    wv = ease_io(ramp(t, w_len, .5))
    pn = ease_out(ramp(t, w_net, .25), 2)
    s = lerp(lerp(1.95, 2.05, u), 1.08, wv) + .55 * pn
    ccx = lerp(lerp(390, 440, u), 680, wv)
    ccy = lerp(1090, 960, wv)
    ccx = lerp(ccx, chx, pn)
    ccy = lerp(ccy, chy - 330, pn)
    return frame_svg("".join(o), ccx, ccy, s, -.4 + .8 * u)


# ═══════════════════════════════ s11: забор до середины ═══════════════════════════════
FENCE_N = 24
FENCE_P = 96.0
FENCE_K = 1.25


def yard_bg(t, x0=-800, x1=3600, ground=1420, warm=0.0):
    sky = lib.lin_grad([(0, lib.mix("#8EC3EC", "#F2B57A", warm), 1), (1, lib.mix("#DDEFF8", "#FCE3B5", warm), 1)], 0, 0, 0, 1)
    o = [f'<rect x="{x0}" y="-900" width="{x1 - x0}" height="{ground + 900}" fill="url(#{sky})"/>']
    for j, xx in enumerate(range(x0 + 100, x1, 420)):
        o.append(P.tree(xx + 60 * math.sin(j * 1.7), ground - 160, 1.6 + .3 * math.sin(j), 1.0, t, seed=j))
    o.append(blob(rect_pts(x0, ground - 170, x1, 2700), "#7DB46A"))
    o.append(blob(rect_pts(x0, ground - 20, x1, 2700), "#6FA65D"))
    for j in range(60):
        xx = x0 + j * 75 + 20 * math.sin(j * 2.1)
        o.append(line([(xx, ground + 60 + 40 * math.sin(j)), (xx + 8, ground + 30 + 40 * math.sin(j))], 3, "#4F8A42", taper=.5, wmin=.2, seed=1100 + j))
    return "".join(o)


def s11(t):
    lib.dyn_begin()
    a = A("s11")
    w_ot, w_vs, w_zh, w_br = ws(49), ws(50), ws(51), ws(52)
    ground = 1400
    fx0 = -200
    o = [yard_bg(t, ground=ground + 60)]
    half = FENCE_N // 2
    # граница — середина забора; последняя доска перед ней покрашена наполовину (сверху вниз)
    painted = (half - 1 + lerp(.25, .55, ramp(t, a, w_br - a))) / FENCE_N
    drip = (half - 1, ease_in(ramp(t, w_br + .1, .9), 1.4)) if t >= w_br + .1 else None
    o.append(P.fence(fx0, ground, FENCE_K, painted, t, FENCE_N, seed=11, pitch=FENCE_P, drip=drip))
    bx, btop, bbot = P.fence_board(fx0, ground, FENCE_K, half - 1, FENCE_P)
    # ведро с краской у границы
    o.append(P.paint_bucket(bx - 150, ground + 70, .7, 0, seed=11))
    # отец у границы с кистью; на «бросал» роняет кисть и уходит вправо
    fk = .74
    hipy = ground + 70 - 640 * fk * 1.04
    drop_u = ramp(t, w_br, .2)
    walk_u = ramp(t, w_br + .3, 1.5)
    fxp = bx + 150 + 520 * walk_u
    if walk_u > 0:
        wk = people.walk_kw(fxp, hipy, fk, (t - w_br - .3) * 1.8, "father77", stride=260, lift=70)
        fe, hyy = wk["feet"], wk["hip"][1]
    else:
        fe, hyy = people.stand_kw(fxp, hipy, fk, "father77", spread=80)["feet"], hipy
    # мазки до «бросал»: рука ходит вверх-вниз по доске (зеркально — лицом к забору, влево)
    strokes = math.sin((t - a) * 9) if t < w_br else 0.0
    pfrac = painted * FENCE_N - (half - 1)
    hand = (bx + 30, lerp(btop, bbot, pfrac) - 110 + 50 * strokes)
    turned = t >= w_br + .3
    arms = {"n": ("ik", (2 * fxp - hand[0], hand[1]), -1)} if t < w_br else (
        {"n": ("ang", -.05 + .25 * wob(t, 7), .2), "f": ("ang", .15 - .25 * wob(t, 7), .15)} if turned else None)
    fa = people.father(fxp, hyy, fk, "paint" if t < w_br else "sad", ("brush", "drop"), t, drop_u, feet=fe, flip=not turned, arms=arms,
                       head_add=.03 * wob(t, 2.4))
    o.append(shadow(fxp, ground + 74, 150, .16))
    o.append(fa["svg"])
    # кисть: в руке до «бросал», потом падает на землю у доски и подпрыгивает
    if t < w_br:
        hx, hy = fa["hold"]
        o.append(P.paint_brush(hx, hy + 30, .6, 25 + 10 * strokes, 1.0, seed=11))
    else:
        hx0, hy0 = bx + 40, btop + 170
        y_, uu = fall(t, w_br, hy0, ground + 50, .34)
        rot = 25 + 75 * min(1.0, (t - w_br) / .34)
        o.append(P.paint_brush(hx0 + 30 * min(1.0, (t - w_br) / .34), y_ - 60, .6, rot, 1.0, seed=11))
        if uu >= 1:
            o.append(blob(ellipse_pts(hx0 + 40, ground + 60, 40, 8, 12), P.C_PAINT, .85))
    # камера: панорама слева направо с постоянной скоростью до «бросал», там стоп и удар-наезд
    v = 520.0
    tc = min(t, w_br)
    ccx = bx - 520 + v * (tc - a)
    s = 1.22 * punch(t, w_br, .07, .3)
    return frame_svg("".join(o), ccx, 1030, s, 0.0, bg="#8EC3EC")


# ═══════════════════════════════ s13: штора гаража ═══════════════════════════════
def garage_bg(x0=-700, x1=1800, floor=1480):
    o = [blob(rect_pts(x0, -900, x1, floor), "#6C6A66")]
    d = "".join(f"M{x0} {y}H{x1}" for y in range(-880, floor, 70))
    d += "".join(f"M{x0 + (j % 2) * 75 + i * 150} {-880 + j * 70}v70" for j in range(int((floor + 880) / 70)) for i in range(int((x1 - x0) / 150) + 1))
    o.append(f'<path d="{d}" stroke="#5A5854" stroke-width="3" fill="none"/>')
    o.append(blob(rect_pts(x0, floor, x1, 2700), "#8A8782"))
    o.append(line([(x0, floor), (x1, floor)], 5, "#3E3C39", taper=.1, wmin=.8, seed=1301))
    for j in range(5):
        o.append(blob(ellipse_pts(-100 + j * 420, floor + 180 + 50 * (j % 2), 120, 18, 14), "#7A7772", .7))
    return "".join(o)


def s13(t):
    lib.dyn_begin()
    a = A("s13")
    w_ok, w_moz, w_nach, w_sku = ws(60), ws(62), ws(64), ws(65)
    floor = 1480
    dx, dk = 700, 1.0
    # подъём: дёргает (не идёт) с «Оказалось», на «мозгу» — на ладонь, дрожит, на «начать» падает
    pull = ease_out(ramp(t, w_ok, .25)) * (.025 + .01 * wob(t, 31))
    lift = pull
    if t >= w_moz:
        lift = .025 + .11 * ease_out(ramp(t, w_moz, .35), 2) + .006 * wob(t, 37)
    slam = 0.0
    if t >= w_nach:
        u = ramp(t, w_nach, .12)
        lift = (.14) * (1 - u * u)
        slam = ramp(t, w_nach + .12, .55) if t >= w_nach + .12 else 0.0
    dust = ramp(t, w_sku - .1, .9) if t >= w_sku - .1 else 0.0
    o = [garage_bg(floor=floor)]
    o.append(P.garage_junk(-330, floor + 10, .62, seed=13))
    o.append(P.roll_door(dx, floor, dk, lift, slam, dust, 0.0, t, seed=13))
    # отец на корточках у шторы держит ручку двумя руками и тянет вверх; на «начать» отпускает и отшатывается назад
    hx, hy = P.roll_door_handle(dx, floor, dk, lift)
    fk = .86
    sc = fk * 1.04
    recoil = ease_out(ramp(t, w_nach + .05, .35), 2)
    rise = clamp(lift / .14)
    fhx = dx - 230 - 110 * recoil
    fhy = floor - 360 * sc - 70 * sc * rise + 40 * sc * recoil
    feet = {"n": ((fhx + 150 * sc, floor), -.2), "f": ((fhx + 40 * sc, floor + 6), -.2)}
    if recoil < .5:
        arms = {"n": ("ik", (hx - 20, hy + 4), -1), "f": ("ik", (hx - 70, hy + 6), -1)}
    else:
        arms = {"n": ("ik", (fhx + 260 * sc, fhy - 260 * sc), -1), "f": ("ik", (fhx + 160 * sc, fhy - 200 * sc), -1)}
    ex = "strain" if t < w_nach else "surprised"
    fa = people.father(fhx, fhy, fk, ex, "shoulder", t, 1.0, feet=feet, arms=arms, lean_add=-.05 + .12 * rise - .5 * recoil,
                       hands={"n": {"curl": (.7, .7, .7, .75), "thumb": .5}, "f": {"curl": (.7, .7, .7, .75), "thumb": .5}})
    o.append(shadow(fhx + 60, floor + 6, 200, .2, "#2A2825"))
    o.append(fa["svg"])
    if t < w_nach and t >= w_ok:
        o.append(people.strain_marks(fa["head"], sc, t, ease_out(ramp(t, w_ok, .3))))
    # голая лампочка под потолком
    o.append(line([(380, -900), (380, 120)], 4, "#2A2825", taper=.05, wmin=.9, seed=1302))
    o.append(shape(ellipse_pts(380, 150, 26, 32, 12), "#FFF3C4", "", w=3, seed=1303))
    o.append(P.glow(380, 150, 260, .55, "#FFE7A3"))
    # камера: низкий ракурс (снизу), тряска на падении
    u = ease_io(ramp(t, a, B("s13") - a))
    sh = P.shake(t, w_nach + .1, 22, .45, seed=13)
    s = lerp(1.04, 1.1, u) * punch(t, w_nach + .1, .05, .3)
    return frame_svg("".join(o), 560 + 40 * u + sh[0], 1080 + sh[1], s, -2.0 + .5 * u, bg="#6C6A66")


# ═══════════════════════════════ s16: доски зеленеют (бумага) ═══════════════════════════════
def paw_print(x, y, k=1.0, u=1.0, rot=0.0):
    if u <= .01:
        return ""
    s = lib.back_out(clamp(u), 2.0)
    o = [blob(ellipse_pts(0, 0, 18, 15, 12), "#2B2F33")]
    for j, (px, py) in enumerate(((-18, -20), (-6, -30), (8, -30), (19, -20))):
        o.append(blob(ellipse_pts(px, py, 6.5, 8, 10), "#2B2F33"))
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k * s:.3f})">{"".join(o)}</g>'


def s16(t):
    lib.dyn_begin()
    a = A("s16")
    w_mal, w_sha = ws(80), ws(81)
    n = 12
    pitch, fk, bh = 96.0, 1.5, 640.0
    x0, ground = 40.0, 1330.0
    per = .2
    # одна доска на «маленькому», дальше — по доске с «шагу»
    cnt = .12 + .88 * ease_out(ramp(t, w_mal, .4))
    if t >= w_sha:
        cnt = 1.0 + (t - w_sha) / per
    o = [paper_bg()]
    o.append(line([(x0 - 600, ground + 6), (x0 + pitch * n * fk + 600, ground + 6)], 6, INK, taper=.1, wmin=.8, seed=1601))
    o.append(P.fence(x0, ground, fk, min(cnt, n) / n, t, n, seed=16, h=bh, pitch=pitch))
    # маленькая кисть ведёт мазок по текущей доске сверху вниз
    i = int(min(cnt, n - 1))
    cxb, top, bot = P.fence_board(x0, ground, fk, i, pitch, bh)
    frac = clamp(cnt - i)
    by = lerp(top + 30, bot - 20, frac)
    o.append(P.paint_brush(cxb + 70, by - 150, .9, -28 + 8 * wob(t, 22), 1.0, seed=16))
    # отпечаток лапы у основания каждой готовой доски
    for j in range(min(n, int(cnt))):
        cxj, _, _ = P.fence_board(x0, ground, fk, j, pitch, bh)
        tj = (w_mal + .4) if j == 0 else (w_sha + (j - 1) * per + per)
        o.append(paw_print(cxj, ground + 70, 2.4, ramp(t, tj - .05, .2), -8 + 14 * (j % 2)))
    # камера: постоянный дрейф вправо за окрашенными досками
    ccx = 400 + 330 * (t - a)
    return frame_svg("".join(o), ccx, 1020, 1.12, -.3)


# ═══════════════════════════════ s19: рамка с фото на полке ═══════════════════════════════
def s19(t):
    lib.dyn_begin()
    a = A("s19")
    w_fot = ws(95)
    o = [blob(rect_pts(-800, -900, 1900, 2800), "#BFD8B4")]            # свежая стена
    d = "".join(f"M{x} -900V2800" for x in range(-800, 1900, 160))
    o.append(f'<path d="{d}" stroke="#B2CCA6" stroke-width="10" fill="none"/>')
    o.append(P.glow(300, 500, 700, .35, "#FFE7A3"))
    sy = 1450
    o.append(P.shelf(540, sy, 2.0, 1, seed=19, w=640))
    # рамка: стоит чуть криво, лапа поправляет на «фото»
    fix = ease_io(ramp(t, w_fot - .2, .35))
    rot = lerp(-6, 0, fix) + (1.2 * math.exp(-max(0, t - w_fot - .15) * 6) * math.sin((t - w_fot) * 20) if t > w_fot + .15 else 0)
    fk = 5.0
    fy = sy - 100 * fk
    o.append(shadow(540, sy + 6, 380, .2, "#4A5A40"))
    o.append(f'<g transform="rotate({rot:.2f} 540 {sy})">' + P.photo_frame(540, fy, fk, 0, 1.0, None, seed=19,
                                                                         glint=ramp(t, w_fot, .55), portrait=True, t=t) + '</g>')
    # лапа кота справа: подходит, толкает край рамки, уходит
    ck = 2.2
    reach = ease_io(ramp(t, a, w_fot - a)) - .35 * ease_io(ramp(t, w_fot + .3, .4))
    base = (1300, sy - 120)
    tip = (lerp(1130, 540 + 80 * fk + 20, reach), sy - 360 + 20 * wob(t, 3) * (1 - reach))
    o.append(people.cat_forearm(base, tip, ck, 0.0, seed=19))
    # камера: наезд на фото
    u = ease_io(ramp(t, a, B("s19") - a))
    s = lerp(.98, 1.1, u) * punch(t, w_fot, .03, .3)
    return frame_svg("".join(o), 540, lerp(1000, fy + 40, u), s, lerp(-1.0, 0, u), bg="#BFD8B4")


SCENES = dict(s05=s05, s06=s06, s08=s08, s11=s11, s13=s13, s16=s16, s19=s19)


def frame(sid, t):
    return SCENES[sid](t)
