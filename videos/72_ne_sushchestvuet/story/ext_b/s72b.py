"""Рилс 72 «СДВГ не существует», группа B: день, провокация, кресло-мешок (резкий белый свет, комната room.bag_room).
s03 (2.38–4.02, whip): Дима развалился в кресле-мешке с телефоном у лица (экран к нему, свет экрана на щеках); кот стоит на полу
    слева и показывает на него лапой «вот, видите». «лень» (2.68) Дима обмякает и съезжает, кресло оплывает; «телефон» (3.17)
    телефон вспыхивает, глаза стеклянные, кот самодовольно кивает.
s04 (4.02–5.40): средний план, кот на переднем плане справа подходит вплотную. «Ну правда» (4.05) разводит лапами; «просто
    положи» (4.82–5.36) лапой забирает телефон из руки Димы и кладёт экраном вниз на пол; рука Димы зависла, он провожает телефон.
s05 (5.40–6.40): с потолка перед Димой падает башня чистых листов с лентой, подскакивает и встаёт выше его головы; «сделай» (6.06)
    Дима вжимается в кресло, глаза-блюдца, кот показывает лапой на башню; белый свет всё резче.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Комната — common/room.py, предметы — props.py, люди и кот — people.py."""
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
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, svg  # noqa: E402

INK = lib.INK
WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?«»").lower() == word:
            return w["start"]
    raise KeyError(word)


def lerp(a, b, u):
    return a + (b - a) * u


def whip_in(t, t0, dur=.22, amp=170.0):
    u = clamp((t - t0) / dur)
    e = 1 - ease_out(u, 3)
    return amp * e, 2.2 * e * (1 if amp > 0 else -1)


def frame_svg(body, cx, cy, s, rot, white=0.0):
    w = f'<rect width="1080" height="1920" fill="#FFFFFF" opacity="{white:.3f}"/>' if white > .005 else ""
    return svg(f'<rect width="1080" height="1920" fill="#e9ecea"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{w}')


BAG = (560.0, 1500.0)
BAG_K = 1.3
DS = .85                          # масштаб Димы
CAT_COL = None


def hip_of(sag, slide=0.0):
    x, y = P.bean_seat(BAG[0], BAG[1], BAG_K, sag)
    return x + 40 + 40 * slide, y + 40 + 50 * slide


def screen_glow(head, u, t, flash=0.0):
    """Свет экрана на лице: маленькое холодное пятно у щеки (не огромный овал); flash — вспышка."""
    if u <= .01:
        return ""
    fl = .5 + .5 * math.sin(t * 17) * .1
    return (P.glow(head[0] + 34, head[1] + 6, 82 + 40 * flash, (.55 + .45 * flash) * u * (1 + fl * .1), "#D6E4FF", ry=96 + 40 * flash))


# ═══════════════════════════════ s03: Дима в кресле-мешке с телефоном ═══════════════════════════════
T3_L = wt("лень")          # 2.68
T3_T = wt("телефон")       # 3.17
CAT3 = (215.0, 1560.0)
CAT3_K = 1.0


def s03(t):
    lib.dyn_begin()
    rb = R.bag_room(t)
    o = [rb["bg"]]
    slump = ease_out(clamp((t - T3_L) / .35), 2)
    sag = .15 + .55 * clamp(P.settle(t, T3_L, 0.0, 1.0, 2.2, 5.0))
    hx, hy = hip_of(sag, slump)
    o.append(P.bean_bag(BAG[0], BAG[1], BAG_K, sag, seed=1))
    flash = math.exp(-max(0.0, t - T3_T) * 4.0) * (t >= T3_T)
    ex = dict(people.EXPR["dima"]["glassy" if t < T3_L else "slump"])
    if t > T3_T:
        ex = dict(people.EXPR["dima"]["glassy"], lid=.62 - .2 * clamp((t - T3_T - .4) / .4))
    ex["look"] = (.35, -.35)
    thumb = 6 * math.sin(t * 9) * (1 - slump * .5)       # большой палец листает — кисть чуть подрагивает
    fig = people.dima(hx, hy, DS, ex, "phone_face", lean_add=-.12 - .14 * slump, head_add=.14 + .1 * slump, **people.beanbag_kw(hx, hy, DS, sag),
                      arms={"n": ("ik", (hx + (90 + 30 * slump) * DS, hy - (420 - 60 * slump) * DS + thumb), -1)})
    o.append(fig["svg"])
    ph = people.hand_pos(fig, "n", 38)
    o.append(people.mobilnik(ph[0], ph[1], 1.35 * DS, -12 + 3 * math.sin(t * 3), seed=951))
    o.append(screen_glow(fig["head"], 1.0, t, flash))
    if flash > .05:     # вспышка: короткие лучики от телефона
        for j in range(6):
            a = math.radians(-30 + 40 * j)
            r0 = 70 + 60 * (1 - flash)
            o.append(line([(ph[0] + math.cos(a) * r0, ph[1] + math.sin(a) * r0), (ph[0] + math.cos(a) * (r0 + 50 * flash), ph[1] + math.sin(a) * (r0 + 50 * flash))],
                          6, "#8FB2F0", taper=.6, wmin=.1, seed=3300 + j, op=.9))
    # кот слева: показывает лапой на Диму, на «телефон» — самодовольно кивает
    pw = .7 + .3 * ease_out(clamp((t - 2.3) / .25))
    st = dict(smug=.4 + .5 * clamp((t - T3_T + .1) / .2), paw=pw, paw_dx=52 + 5 * math.sin(t * 5), look=(.8, -.2), tilt=-4,
              drop=people.cat_nod(t, T3_T + .08, .3, .26) + people.cat_nod(t, T3_T + .5, .3, .2), tail=6 * math.sin(t * 2.3),
              blink=1.0 if abs(t - 2.95) < .05 else 0.0)
    o.append(blob(ellipse_pts(CAT3[0], CAT3[1] + 4, 120 * CAT3_K, 16, 14), "#000000", .12))
    o.append(people.cat_svg(CAT3[0], CAT3[1], CAT3_K, st, t))
    o.append(rb["front"])
    wx, wr = whip_in(t, 2.18, .22, 180)
    cy = 1235 + 40 * ease_io(clamp((t - 2.4) / 1.6))
    s = 1.13 + .025 * ease_io(clamp((t - 2.4) / 1.6))
    return frame_svg("".join(o), 585 + wx, cy, s, wr + .4 * math.sin(t * 1.2))


# ═══════════════════════════════ s04: кот забирает телефон ═══════════════════════════════
T4_N = wt("ну")            # 4.05
T4_P = wt("просто")        # 4.82
T4_POL = wt("положи")      # 5.01
CAT4 = (905.0, 1565.0)
CAT4_K = 1.15
PHONE_FLOOR = (770.0, 1522.0)


def _cat4(t):
    """Состояние кота s04 и положение кончика левой лапы: (st, x кота, кончик)."""
    walk = clamp((t - 3.82) / .3)
    cx = lerp(1060, CAT4[0], ease_out(walk, 2))
    st = dict(tail=8 * math.sin(t * 2.6), look=(-.6, -.3), smug=.6)
    if t < T4_N + .02:
        st["walk"] = (t - 3.82) / .25 if walk < 1 else None
    # «Ну правда» — разводит лапами
    sp = ease_out(clamp((t - T4_N) / .18), 2) * (1 - ease_in(clamp((t - 4.6) / .2)))
    if sp > 0:
        st.update(paw=.62 * sp, paw_l=.62 * sp, paw_dx=44, paw_l_dx=44, tilt=7 * sp, smug=.85)
    # «просто положи» — левая лапа тянется к телефону, берёт, опускает на пол
    reach = ease_out(clamp((t - T4_P + .05) / .2), 2)
    lower = ease_io(clamp((t - T4_POL - .05) / .3))
    tip = None
    if reach > 0:
        p = lerp(lerp(0, 1.85, reach), .35, lower)
        dx = lerp(lerp(60, 54, reach), 150, lower)
        st.update(paw_l=p, paw_l_dx=dx, paw=0.0, tilt=-5 * reach, look=(-.7, -.6 + 1.1 * lower), smug=.5)
        tip = people.cat_paw_tip(cx, CAT4[1], CAT4_K, st, "l")
    return st, cx, tip


def _held_phone(x, y, k, tip, lay):
    """Телефон в лапе: подушечка лежит поверх нижней трети корпуса (хват, а не «молоток» за середину);
    lay 0…1 — по пути к полу поворачивается плашмя."""
    import cat
    bx, by = x + (cat.CX - 25 - cat.CX) * k, y + (1236 - cat.CBOT) * k
    ux, uy = tip[0] - bx, tip[1] - by
    L = math.hypot(ux, uy) + 1e-6
    ux, uy = ux / L, uy / L
    rot = lerp(-28, -95, ease_io(lay))
    a = math.radians(rot)
    up = (math.sin(a), -math.cos(a))
    kk = 1.35 * DS
    ph = (tip[0] + up[0] * 26 * kk, tip[1] + up[1] * 26 * kk)
    o = people.mobilnik(ph[0], ph[1], kk, rot, seed=951)
    pad = ellipse_pts(tip[0] + ux * 4, tip[1] + uy * 4, 24 * k, 21 * k, 12, rot=math.degrees(math.atan2(uy, ux)))
    o += cat.shape(pad, cat.CAT, "", w=4.4 * k, seed=295)
    o += blob(ellipse_pts(tip[0] + ux * 9 * k, tip[1] + uy * 9 * k + 3 * k, 9 * k, 7 * k, 8), "#e8823a")
    for kq in (-7, 6):
        o += line([(tip[0] + kq * k - 5 * k, tip[1] - 12 * k), (tip[0] + kq * k + 2 * k, tip[1] - 3 * k)], 2.2 * k, seed=296 + kq)
    return o


def s04(t):
    lib.dyn_begin()
    rb = R.bag_room(t)
    o = [rb["bg"]]
    sag = .7
    hx, hy = hip_of(sag, 1.0)
    o.append(P.bean_bag(BAG[0], BAG[1], BAG_K, sag, seed=1))
    st, cx, tip = _cat4(t)
    taken = t > T4_P + .2
    on_floor = t > T4_POL + .33
    # рука Димы: держит телефон у живота; после — зависла в воздухе, пальцы полусогнуты
    hand_t = (hx + 105 * DS, hy - 200 * DS)
    look_follow = clamp((t - T4_P - .15) / .3)
    ex = dict(people.EXPR["dima"]["glassy"])
    ex["look"] = (lerp(.45, .75, look_follow), lerp(.55, .85, clamp((t - T4_POL) / .3)))
    if taken:
        ex = dict(people.EXPR["dima"]["surprise_day"], look=ex["look"], lid=.85)
    drift = 10 * ease_out(clamp((t - T4_P - .2) / .2)) * math.sin((t - T4_P) * 7) * math.exp(-max(0, t - T4_P - .2) * 2)
    fig = people.dima(hx, hy, DS, ex, "phone_face" if not taken else "hand_hang", head_add=.18, lean_add=-.04,
                      **people.beanbag_kw(hx, hy, DS, sag),
                      arms={"n": ("ik", (hand_t[0] + drift - 30 * taken, hand_t[1] - 70 * taken), -1)},
                      hands={"n": {"dir": (1, -.35), "curl": (.6, .62, .66, .7) if not taken else (.35, .45, .5, .55), "thumb": .55}})
    o.append(fig["svg"])
    ph = people.hand_pos(fig, "n", 36)
    # телефон: в руке → в лапе → на полу экраном вниз
    if not taken:
        o.append(people.mobilnik(ph[0], ph[1], 1.35 * DS, -28, seed=951))
    o.append(blob(ellipse_pts(cx, CAT4[1] + 4, 130 * CAT4_K, 18, 14), "#000000", .12))
    if on_floor:
        land = P.squash(t, T4_POL + .33, .18, 3, 9)
        o.append(P.phone_flat(PHONE_FLOOR[0], PHONE_FLOOR[1], .62 * land[0], 0, 18, face_down=True, seed=2))
    o.append(people.cat_svg(cx, CAT4[1], CAT4_K, st, t))
    if taken and not on_floor and tip is not None:
        o.append(_held_phone(cx, CAT4[1], CAT4_K, tip, clamp((t - T4_POL) / .3)))
    if on_floor and t < T4_POL + .7:
        u = clamp((t - T4_POL - .33) / .3)
        for j in range(4):
            a = math.radians(-160 + 45 * j)
            o.append(line([(PHONE_FLOOR[0] + math.cos(a) * (90 + 40 * u), PHONE_FLOOR[1] + math.sin(a) * (30 + 20 * u)),
                           (PHONE_FLOOR[0] + math.cos(a) * (120 + 50 * u), PHONE_FLOOR[1] + math.sin(a) * (44 + 22 * u))], 5 * (1 - u), INK, taper=.6,
                          wmin=.1, seed=4400 + j))
    o.append(rb["front"])
    # камера: дрейф за лапой с телефоном, лёгкий наклон к полу
    f = ease_io(clamp((t - T4_P) / .6))
    cx_ = lerp(640, 690, f)
    cy_ = lerp(1240, 1290, f)
    s = 1.3 + .04 * ease_io(clamp((t - 3.82) / 1.6))
    return frame_svg("".join(o), cx_, cy_, s, lerp(-.5, 1.4, f))


# ═══════════════════════════════ s05: башня-диплом падает перед Димой ═══════════════════════════════
T5_F = 5.41                 # начало падения
T5_LAND = 5.62
T5_S = wt("сделай")        # 6.06
TOWER5 = (985.0, 1540.0)
TOWER5_K = 1.25
CAT5 = (285.0, 1540.0)
CAT5_K = .74


def s05(t):
    lib.dyn_begin()
    rb = R.bag_room(t)
    o = [rb["bg"]]
    press = ease_out(clamp((t - T5_S) / .2), 3)
    sag = .7 + .2 * press
    hx, hy = hip_of(sag, 1.0 - .7 * press)
    o.append(P.bean_bag(BAG[0], BAG[1], BAG_K, sag, seed=1))
    # телефон на полу (из s04)
    o.append(P.phone_flat(PHONE_FLOOR[0], PHONE_FLOOR[1], .62, 0, 18, face_down=True, seed=2))
    # Дима: рука ещё зависла → вздрагивает на приземлении → вжимается
    landed = t >= T5_LAND
    if t < T5_LAND:
        ex, pose = dict(people.EXPR["dima"]["surprise_day"], look=(.7, .8), lid=.85), "hand_hang"
    elif t < T5_S:
        ex, pose = dict(people.EXPR["dima"]["plea"], look=(.75, -.5)), "hand_hang"
    else:
        ex, pose = dict(people.EXPR["dima"]["saucer"], look=(.8, -.4)), "press_back"
    jump = P.hop(t, T5_LAND, 26, .22)
    fig = people.dima(hx, hy + jump, DS, ex, pose, shrug=.9 * press, head_add=-.08 * press, lean_add=-.1 * press,
                      **people.beanbag_kw(hx, hy, DS, sag))
    o.append(fig["svg"])
    # башня: падает с потолка (ускорение), удар, подскок, встаёт и покачивается
    tx, ty = TOWER5
    if t < T5_LAND:
        u = clamp((t - T5_F) / (T5_LAND - T5_F))
        dy = -1500 * (1 - u * u)
        lean = 4 * (1 - u)
        sq = (1.0, 1.0)
    else:
        dy = P.hop(t, T5_LAND, 60, .26)
        lean = 3.5 * math.sin((t - T5_LAND) * 9) * math.exp(-(t - T5_LAND) * 3) - 1.5 * press
        sq = P.squash(t, T5_LAND, .16, 3.2, 7)
    if t >= T5_F - .05:
        tw = P.paper_tower(0, 0, TOWER5_K, lean=lean, flutter=.8 if t > T5_LAND else .3, t=t, n=62, seed=4)
        o.append(blob(ellipse_pts(tx, ty + 4, 290 * clamp(.3 + .7 * (1 + dy / 1500)), 26, 16), "#000000", .14))
        o.append(f'<g transform="translate({tx:.1f} {ty + dy:.1f}) scale({sq[0]:.4f} {sq[1]:.4f})">{tw}</g>')
        if t < T5_LAND:
            for j in range(3):
                xx = tx - 150 + 150 * j
                o.append(line([(xx, ty + dy - 900), (xx, ty + dy - 1150)], 7, INK, taper=.6, wmin=.1, seed=5500 + j, op=.8))
    # удар: пыль и штрихи у основания, листочки взлетают
    if landed and t < T5_LAND + .6:
        u = (t - T5_LAND) / .6
        o.append(P.puff_cloud(tx - 260, ty - 30, 1.3, u, seed=3, col="#E7E9E6"))
        o.append(P.puff_cloud(tx + 230, ty - 30, 1.1, u, seed=4, col="#E7E9E6"))
        for j in range(5):
            a = math.radians(-170 + 40 * j)
            r0 = 260 + 120 * u
            o.append(line([(tx + math.cos(a) * r0, ty - 20 + math.sin(a) * r0 * .35), (tx + math.cos(a) * (r0 + 60), ty - 20 + math.sin(a) * (r0 + 60) * .35)],
                          7 * (1 - u), INK, taper=.6, wmin=.1, seed=5600 + j))
        for j in range(3):
            fx = tx - 120 + 120 * j + 80 * u * (j - 1)
            fy = ty - 820 - 200 * math.sin(math.pi * u) + 300 * u * u
            o.append(P.paper(fx, fy, .55, 80 * u * (j - 1) + 30 * math.sin(t * 12 + j), seed=40 + j, kind="blank", bend=.5 * math.sin(t * 15 + j)))
    # кот слева: показывает лапой на башню
    pw = ease_out(clamp((t - T5_LAND - .05) / .2)) * (1 - .0)
    st = dict(paw=.4 + .6 * pw, paw_dx=56, look=(.9, -.5), perk=1.0 if t > T5_LAND else 0.0, tail=8 * math.sin(t * 3), smug=.3 * (1 - pw),
              tilt=-5)
    o.append(blob(ellipse_pts(CAT5[0], CAT5[1] + 4, 120 * CAT5_K, 16, 14), "#000000", .12))
    o.append(people.cat_svg(CAT5[0], CAT5[1], CAT5_K, st, t))
    o.append(rb["front"])
    # камера: дрожит на приземлении, удар-наезд на «сделай»
    sh = P.shake(t, T5_LAND, 26, .4, seed=5)
    punch = .1 * ease_out(clamp((t - T5_S) / .1)) - .03 * ease_io(clamp((t - T5_S - .1) / .3))
    s = 1.0 + punch + .02 * ease_io(clamp((t - 5.2) / 1.2))
    cx_ = lerp(700, 715, ease_out(clamp((t - T5_S) / .15)))
    cy_ = lerp(1180, 1120, ease_out(clamp((t - T5_S) / .15)))
    white = .32 * ease_in(clamp((t - 5.4) / 1.05), 2)
    return frame_svg("".join(o), cx_ + sh[0], cy_ + sh[1], s, .8 * math.sin(t * 1.4) + sh[0] * .04, white)


SCENES = {"s03": s03, "s04": s04, "s05": s05}


def frame(sid, t):
    return SCENES[sid](t)
