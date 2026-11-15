"""Рилс 74 «Прекрати ныть», группа C — хук, поворот, петля:
s01 (хук: снизу крупно самодовольный кот-«король» на троне из офисного кресла под красной накидкой, в маленькой короне, лапы
скрещены; в кадре 0 голова уже на середине резкого движения к зрителю, корона качается, хвост хлещет, кисти накидки раскачиваются,
пылинки в луче; «Прекра-ТИ» — голова встаёт на зрителя, корона подпрыгивает; «ныть» — верхняя лапа стукает когтем по подлокотнику;
«СДВГ» — кот закатывает глаза, корона съезжает набок),
s06 (поворот: белый всполох-сбой, темнота; корона падает и катится, кот спрыгивает с кресла, накидка сползает — трон оказывается
обычным креслом; 7.40 загорается экран телефона и выхватывает лицо Димы за столом, кот запрыгивает на стол),
s17 (петля тем же ракурсом, что s01, в тёплом свете лампы: кот без короны ломает крекер, раскладывает три кусочка на подлокотнике,
щелчком отправляет кусочек к зрителю, тёплый кивок).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Места — common/room.py, кот — common/cat.py, предметы — common/props.py,
Дима — common/people.py. Букв и цифр нет. NOCAM=1 — без камеры (замер движения рисунка), MASK=both|face — силуэт для замера."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import cat as CAT  # noqa: E402
import lib  # noqa: E402
import people as PE  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, rect_pts, shape  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?«»:").lower() == word:
            return w["start"]
    raise KeyError(word)


def lerp(a, b, u):
    return a + (b - a) * u


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def damp(t, t0, amp, freq=3.0, dmp=6.0):
    u = t - t0
    if u <= 0:
        return 0.0
    return amp * math.exp(-dmp * u) * math.sin(2 * math.pi * freq * u)


def shake2(t, t0, amp, k=9.0, fr=19.0):
    def dec(tt):
        if tt < 0:
            return 0.0
        return math.exp(-k * tt) * math.sin(2 * math.pi * fr * tt)
    return amp * dec(t - t0), amp * .7 * dec(t - t0 - .013)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def hook_cam(t, t_hit, t_hit2, rot0=3.6, side0=-55.0):
    """Влёт правил 28/29: с 40 % дальше (1/(1+0.4)) за 0.22 с, перелёт 5 % с отскоком, поворот rot0 с возвратом, занос сбоку;
    удар +8 % на t_hit2 и поменьше (+4 %) на t_hit. Возвращает (масштаб-множитель, поворот, занос)."""
    u = clamp(t / .22)
    e = ease_out(u, 3)
    s = 1 / 1.4 + (1 - 1 / 1.4) * e
    if t > .22:
        s += .05 * math.exp(-7 * (t - .22)) * math.sin(2 * math.pi * 2.2 * (t - .22) + math.pi / 2)
    rot = rot0 * (1 - e) + damp(t, .22, -1.2, 2.0, 6.0)
    side = side0 * (1 - e)
    hit = 0.0
    for th, a in ((t_hit, .04), (t_hit2, .08)):
        if t > th:
            h = t - th
            hit += a * math.exp(-5.5 * h) * (1 if h > .03 else h / .03)
    return s * (1 + hit), rot, side


def mask_svg(svg, kind):
    """Силуэт для замера: всё нарисованное — сплошным цветом (face — красный, остальное — синий)."""
    col = "1 0 0" if kind == "face" else "0 0 1"
    fid = f"mk{kind}"
    if not any(f'id="{fid}"' in d for d in lib.DEFS):
        r, g, b = col.split()
        lib.DEFS.append(f'<filter id="{fid}"><feColorMatrix type="matrix" values="0 0 0 0 {r} 0 0 0 0 {g} 0 0 0 0 {b} 0 0 0 9 0"/></filter>')
    return f'<g filter="url(#{fid})">{svg}</g>'


# ═════════════════════════ кот: точки и голова в системе рисунка cat.draw ═════════════════════════
def _head_params(st, t):
    sl = st.get("sleep", 0.0)
    br = 1 + 0.012 * math.sin(t * 2 * math.pi / 3.1) * (1 + 1.5 * sl)
    sy = br * (1 - .2 * sl) * st.get("sy", 1.0)
    hy = -(sy - 1) * (CAT.CBOT - CAT.NECK[1]) + 34 * sl + 70 * st.get("drop", 0.0)
    tilt = st.get("tilt", 0.0) + 16 * sl
    return sl, hy, tilt


def head_pt(x, y, k, st, t, px, py):
    """Точка головы (единицы рисунка кота) → мир; и угол головы в мире (град)."""
    sl, hy, tilt = _head_params(st, t)
    a = math.radians(tilt)
    nx, ny = CAT.NECK
    qx = nx + (px - nx) * math.cos(a) - (py - ny) * math.sin(a) + 22 * sl
    qy = ny + (px - nx) * math.sin(a) + (py - ny) * math.cos(a) + hy
    b = math.radians(st.get("rot", 0.0))
    lx, ly = (qx - CAT.CX) * k, (qy - CAT.CBOT) * k
    return x + lx * math.cos(b) - ly * math.sin(b), y + lx * math.sin(b) + ly * math.cos(b), tilt + st.get("rot", 0.0)


def head_svg(x, y, k, st, t):
    sl, hy, tilt = _head_params(st, t)
    return (f'<g transform="translate({x:.2f} {y:.2f}) rotate({st.get("rot", 0.0):.2f}) scale({k:.4f}) translate({-CAT.CX} {-CAT.CBOT})">'
            f'<g transform="translate({22 * sl:.2f} {hy:.2f}) rotate({tilt:.2f} {CAT.NECK[0]} {CAT.NECK[1]})">{CAT.head(st, t)}</g></g>')


def crown_on(x, y, k, st, t, slide=0.0, rot=0.0, hop=0.0, bounce=0.0, shine=0.0, kc=.56):
    """Корона на голове кота: стоит между ушей, едет вместе с головой; slide — съезжает вбок (ед. рисунка), rot — свой наклон."""
    FX = 22 * st.get("turn", 0.0)
    cx_, cy_, ang = head_pt(x, y, k, st, t, 836 + FX * .6 + slide, 1000 - hop)
    return PR.crown(cx_, cy_, k * kc, ang + rot, bounce=bounce, shine=shine, seed=1)


# ═════════════════════════ s01: хук ═════════════════════════
S0 = 1.1                     # базовый масштаб камеры хука и петли (вид THRONE74["low"] в координатах кадра)
CAMH = (590.0, 1000.0)       # центр камеры
T_HIT = 0.42                 # «Прекра-ТИ»: голова встаёт на зрителя
T_NY = wt("ныть")            # 0.60 — коготь стукает по подлокотнику (касание T_TAP)
T_TAP = T_NY + .05
T_SD = wt("сдвг")            # 1.08 — закатывает глаза, корона съезжает
T_MID = .2                   # подскок короны и рывок кистей между стартом и первым ударом


def s01_cat(t):
    st = dict(PE.CAT_ST["king74"]) if "king74" in getattr(PE, "CAT_ST", {}) else dict(cross=1.0, smug=1.0, cold=.55)
    # голова: в кадре 0 уже на середине резкого движения вниз к зрителю (скорость с кадра 0, *.out), встаёт к «ТИ»
    u = clamp(t / T_HIT)
    e = 1 - (1 - u) ** 2.4
    st["turn"] = lerp(.42, 0.0, e) + damp(t, T_HIT, -.1, 3.0, 7)
    st["drop"] = lerp(-.42, .06, e) + damp(t, T_HIT, .12, 3.2, 7) + .05 * bump(t, T_TAP - .02, .25)
    st["tilt"] = lerp(-13.0, -4.0, e) + damp(t, T_HIT, 3.4, 2.8, 6) + damp(t, T_TAP, -2.0, 3.4, 7) + 12 * sm(t, T_SD, T_SD + .2)
    st["look"] = (lerp(.7, 0.0, e) + .7 * bump(t, T_TAP - .18, .42), lerp(-.5, .38, e))
    st["roll"] = sm(t, T_SD + .02, T_SD + .2)
    st["smug"] = 1.0
    st["ear"] = lerp(-12, -4, e) + damp(t, T_HIT, 7, 4.2, 6) + damp(t, T_TAP, 5, 5, 7) + 4 * math.sin(t * 11)
    # хвост хлещет с края кресла: резкие рывки туда-обратно, с кадра 0 на скорости
    st["tail"] = -10 + 24 * math.sin(2 * math.pi * 1.7 * t + 1.25) + 7 * math.sin(2 * math.pi * 3.4 * t + .3) + damp(t, T_TAP, -9, 3, 5)
    st["flame_e"] = 1.2 + .4 * math.sin(t * 9)
    # стук когтем: верхняя (правая) лапа из скрещения к подлокотнику и обратно
    ct = 0.0
    if t > T_TAP - .14:
        ct = ease_out(clamp((t - (T_TAP - .14)) / .14), 2) if t < T_TAP else 1 - ease_io(clamp((t - T_TAP - .08) / .22))
    st["cross"] = 1.0
    st["cross_tap"] = ct
    sq = damp(t, T_HIT, .03, 3.0, 7) + damp(t, T_TAP, .02, 3.2, 8)
    st["sy"] = 1 - sq
    st["sx"] = 1 + .5 * sq
    st["rot"] = lerp(-3.0, 0.0, e) + damp(t, T_HIT, 1.0, 2.5, 6) + damp(t, T_TAP, .6, 3, 7)
    return st


def s01_crown(t):
    """Корона: качается на голове с кадра 0, подскок T_MID, подпрыгивает на «ТИ» и на стуке, съезжает набок на «СДВГ»."""
    rot = 11 * math.cos(2 * math.pi * 2.3 * t + .6) * math.exp(-1.1 * t) + damp(t, T_HIT, -8, 3.0, 4.5) + damp(t, T_TAP, 6, 3.4, 5)
    hop = 34 * bump(t, T_MID - .08, .2) + 40 * bump(t, T_HIT - .02, .22) + 22 * bump(t, T_TAP, .18)
    slide = 26 * sm(t, T_SD, T_SD + .22)
    rot += 16 * sm(t, T_SD, T_SD + .22) + damp(t, T_SD + .22, 3, 3, 5)
    bounce = .5 * bump(t, T_HIT + .12, .14) + .3 * bump(t, T_TAP + .1, .12)
    shine = bump(t, T_HIT - .02, .3) + .7 * bump(t, T_TAP, .26)
    return dict(rot=rot, hop=hop, slide=slide, bounce=bounce, shine=min(1.0, shine))


def throne_world(t, light, st, crown=None, sway=0.0, drape_u=1.0, tassel=18.0, extra_front="", cat_extra="", floor=""):
    """Мир хука/петли (кадр): кресло вида low, накидка, кот, корона, подлокотники, свет. -> (слои, (x, y, k))."""
    d = R.throne_scene(t, light, "low", 0.0)
    x, y, k = d["cat"]
    cat = CAT.draw(x, y, k, st, t) + cat_extra
    if crown is not None:
        cat += crown_on(x, y, k, st, t, **crown)
    drape = R.drape74("low", t, drape_u, tassel) if drape_u > .001 else ""
    tf = f'rotate({sway:.3f} 540 1640)'
    fg = f'<g transform="{tf}">{d["back"]}{drape}{d["seat"]}{cat}{d["arms"]}{extra_front}</g>'
    return [d["bg"] + floor, fg, d["light"], d["motes"]], (x, y, k), d


def s01(t):
    lib.dyn_begin()
    st = s01_cat(t)
    cr = s01_crown(t)
    sway = 1.3 * math.sin(2 * math.pi * 1.25 * t + 1.0) + damp(t, T_HIT, 1.2, 2.2, 5) + damp(t, T_TAP, -.8, 2.6, 6)
    tassel = 24 + 16 * bump(t, T_HIT, .4) + 12 * bump(t, T_TAP, .3)
    world, (x, y, k), d = throne_world(t, "regal", st, cr, sway, 1.0, tassel)
    mk = os.environ.get("MASK")
    if mk:
        g = '<rect x="-3000" y="-3000" width="8000" height="8000" fill="#fff"/>'
        body = CAT.draw(x, y, k, st, t) + crown_on(x, y, k, st, t, **cr)
        if mk == "both":
            g += mask_svg(body, "both")
        else:
            g += mask_svg(head_svg(x, y, k, st, t), "face")
        world = [g]
    if os.environ.get("NOCAM"):
        set_ink(S0)
        return lib.svg(f'<g transform="{lib.cam(CAMH[0], CAMH[1], S0)}">{"".join(world)}</g>')
    kk, rc, side = hook_cam(t, T_HIT, T_TAP)
    rc += -1.6 * sm(t, T_SD, T_SD + .25)          # лёгкий наклон кадра на закатывании глаз
    sx1, sy1 = shake2(t, T_TAP, 6)
    ccx = CAMH[0] + side - sx1 + 3 * math.sin(t * 2.3)
    ccy = CAMH[1] - sy1
    s = S0 * kk * (1 + .015 * sm(t, .5, 1.6))
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(ccx, ccy, s, rc)}">{"".join(world)}</g>')


# ═════════════════════════ s06: поворот ═════════════════════════
T6 = 6.25                    # всполох-сбой
T_CROWN = 6.90               # корона падает
T_JUMP = 6.96                # кот отталкивается (толчок), приземление на стол T_LAND
T_LAND = 7.30
T_SCREEN = 7.40              # загорается экран телефона
RCAM = (560.0, 1000.0, 1.25)               # камера мира комнаты (Дима за столом) → кадр
FT = (880.0, 1650.0, .7)                   # трон «front» (координаты вида) → кадр: точка сиденья (540, 1452) встаёт сюда
DESK_CAT_W = (735.0, 925.0)                # где кот садится на стол (мир)
DESK_CAT_K = .8


def w2f(x, y):
    cx, cy, s = RCAM
    return 540 + (x - cx) * s, 960 + (y - cy) * s


def t2f(x, y):
    X, Y, s = FT
    return X + (x - 540) * s, Y + (y - 1452) * s


def _ft(svg):
    X, Y, s = FT
    return f'<g transform="translate({X - 540 * s:.2f} {Y - 1452 * s:.2f}) scale({s})">{svg}</g>'


def s06_cat(t):
    """Кот: на троне (королём) → в темноте настораживается, расцепляет лапы → прыжок с кресла на стол → садится рядом с Димой.
    Возвращает (x, y, k, st) в координатах кадра."""
    st = dict(PE.CAT_ST.get("king74", dict(cross=1.0, smug=1.0, cold=.55)))
    sx0, sy0 = t2f(540, 1452)
    k0 = 2.5 * FT[2]
    x1, y1 = w2f(*DESK_CAT_W)
    k1 = DESK_CAT_K * RCAM[2]
    st["cross"] = 1 - sm(t, 6.58, 6.84)
    st["smug"] = 1 - sm(t, 6.4, 6.7)
    st["cold"] = .55 * (1 - sm(t, 6.4, 6.7))
    st["perk"] = sm(t, 6.36, 6.5)
    st["ear"] = 6 * bump(t, 6.36, .3) + 4 * math.sin(t * 9)
    st["turn"] = -.45 * sm(t, 6.45, 6.75) + .2 * sm(t, T_LAND, T_LAND + .25)
    st["look"] = (-.8 * sm(t, 6.45, 6.75) - .1 * sm(t, T_LAND, T_LAND + .3), .1 + .3 * sm(t, T_LAND + .1, T_LAND + .4))
    st["blink"] = .9 * bump(t, 6.38, .12)
    st["tail"] = 8 * math.sin(2 * math.pi * 1.1 * t) + 10 * bump(t, 6.36, .4)
    st["flame_e"] = .8 + .2 * math.sin(t * 8)
    if t < T_JUMP:
        cr = bump(t, T_JUMP - .12, .2) if t > T_JUMP - .12 else 0.0     # присел перед толчком
        st["sy"] = 1 - .13 * cr
        st["sx"] = 1 + .06 * cr
        st["tilt"] = -6 * cr
        return sx0, sy0, k0, st
    if t < T_LAND:
        u = (t - T_JUMP) / (T_LAND - T_JUMP)
        e = ease_io(u)
        x = lerp(sx0, x1, e)
        y = lerp(sy0, y1, e) - 330 * math.sin(math.pi * u)
        k = lerp(k0, k1, e)
        st["legs"] = 1.0 if u < .8 else 1 - (u - .8) / .2
        st["rot"] = -18 * math.sin(math.pi * u) - 6 * (1 - u)
        st["sy"] = 1 + .08 * math.sin(math.pi * u)
        st["sx"] = 1 - .04 * math.sin(math.pi * u)
        st["tail"] = -24 * math.sin(math.pi * u)
        return x, y, k, st
    land = bump(t, T_LAND, .2)
    st["sy"] = 1 - .14 * land + damp(t, T_LAND + .12, .03, 3, 6)
    st["sx"] = 1 + .07 * land
    st["drop"] = .15 * land
    return x1, y1, k1, st


def s06_crown(t, st, cx, cy, ck):
    """Корона: на голове кота дрожит, на T_CROWN съезжает и падает, бьётся о подлокотник, катится вниз за край кадра."""
    if t < T_CROWN:
        wob = 4 * math.sin(t * 17) * sm(t, 6.4, 6.6) + 9 * sm(t, 6.7, T_CROWN)
        return crown_on(cx, cy, ck, st, t, slide=18 * sm(t, 6.6, T_CROWN), rot=wob, kc=.56)
    # слетает с головы (точка схода — над левым ухом), падает на левый подлокотник, отскакивает, катится вниз-влево
    x0, y0, a0 = head_pt(*t2f(540, 1452), 2.5 * FT[2], st, T_CROWN, 836 + 20, 990)
    ax, ay = t2f(230, 1383 - 30)
    kk = 2.5 * FT[2] * .56
    u = t - T_CROWN
    if u < .18:
        q = u / .18
        x = lerp(x0, ax, q)
        y = y0 + (ay - y0) * q * q
        rot = a0 - 140 * q
    elif u < .42:
        q = (u - .18) / .24
        x = ax - 160 * q
        y = ay - 120 * math.sin(math.pi * q) + 60 * q
        rot = a0 - 140 - 220 * q
    else:
        q = u - .42
        x = ax - 160 - 420 * q
        y = ay + 60 + 900 * q * q + 260 * q
        rot = a0 - 360 - 400 * q
    return PR.crown(x, y, kk, rot, bounce=.5 * bump(t, T_CROWN + .18, .12), shine=bump(t, T_CROWN + .18, .3), seed=1)


def s06(t):
    lib.dyn_begin()
    pre = t < T6
    # ── комната: Дима за столом (мир) ──
    nd = R.night_desk(t, "screen", "mid")
    sx, sy = R.SIT
    br = 1 + .006 * math.sin(2 * math.pi * t / 3.2)
    lit = sm(t, T_SCREEN, T_SCREEN + .08) * (1 - .25 * bump(t, T_SCREEN + .1, .08))
    fig = PE.dima_phone(sx, sy, 1.0, "screen74", "phone_chest74", **PE.sit_kw(sx, sy, 1.0))
    dima = f'<g transform="translate({sx} {sy}) scale(1 {br:.4f}) translate({-sx} {-sy})">{fig["svg"]}</g>'
    room = nd["bg"] + nd["chair_back"] + nd["desk_top"] + dima + nd["desk_legs"] + nd["chair_seat"] + nd["lamp"]
    hx, hy = fig["head"]
    px, py = fig["phone"]
    room_f = f'<g transform="{lib.cam(*RCAM)}">{room}</g>'
    # затемнение с вырезом света экрана на лице и у телефона; контур светлее фона поверх
    fx, fy = w2f(hx + 10, hy + 20)
    pfx, pfy = w2f(px, py)
    dark = f'<rect x="-600" y="-600" width="2280" height="3120" fill="#04060e" opacity=".88"/>'
    rim_room = R.rim74(f'<g transform="{lib.cam(*RCAM)}">{dima}{nd["desk_top"]}{nd["chair_back"]}</g>', "#3c4a78", 2.5, .9, only=True)
    glow = ""
    if lit > .01:
        # свет экрана: освещённая копия Димы поверх темноты только там, куда бьёт экран (лицо и кисти), стена остаётся тёмной
        mid_ = lib.uid("mk")
        g1 = lib.rad_grad([(0, "#ffffff", 1), (.55, "#ffffff", .85), (1, "#ffffff", 0)], fx + 20, fy, 150, 175)
        g2 = lib.rad_grad([(0, "#ffffff", 1), (.6, "#ffffff", .7), (1, "#ffffff", 0)], pfx, pfy, 130, 105)
        lib.DEFS.append(f'<mask id="{mid_}" maskUnits="userSpaceOnUse" x="-600" y="-600" width="2280" height="3120">'
                        f'<rect x="-600" y="-600" width="2280" height="3120" fill="#000"/>'
                        f'<ellipse cx="{fx + 20:.1f}" cy="{fy:.1f}" rx="150" ry="175" fill="url(#{g1})"/>'
                        f'<ellipse cx="{pfx:.1f}" cy="{pfy:.1f}" rx="130" ry="105" fill="url(#{g2})"/></mask>')
        lit_d = R.cold_tint(f'<g transform="{lib.cam(*RCAM)}">{dima}</g>', .9)
        glow = f'<g mask="url(#{mid_})" opacity="{lit:.3f}">{lit_d}</g>'
        glow += R.screen_light74(fx + 34, fy + 14, 150, 190, .8 * lit, t, rot=-10)
        glow += R.motes(t, (pfx - 260, pfy - 420, pfx + 160, pfy + 60), n=10, u=.8 * lit, seed=76)
    # ── трон на переднем плане (вид front, свой масштаб) ──
    th = R.throne_scene(t, "regal" if pre else "dark", "front", 0.0)
    drape_u = 1 - sm(t, 7.0, 7.42)
    drape = R.drape74("front", t, drape_u, 10 + 14 * bump(t, 7.0, .4)) if drape_u > -1 else ""
    if not pre:
        drape = R.rim74(R.cold_tint(drape, 0, .8), "#3c4a78", 2.5)
    cx, cy, ck, st = s06_cat(t)
    cat = CAT.draw(cx, cy, ck, st, t)
    crown = s06_crown(t, st, cx, cy, ck)
    if not pre:
        cat = R.rim74(R.cold_tint(cat, 0, .75 * (1 - .35 * lit)), "#46548a", 2.5)
        crown = R.rim74(R.cold_tint(crown, 0, .55), "#46548a", 2.0)
    throne = _ft(th["back"] + drape + th["seat"]) + (cat if t < T_JUMP + .05 else "") + _ft(th["arms"])
    on_top = crown + (cat if t >= T_JUMP + .05 else "")
    body = room_f + dark + rim_room + glow + throne + on_top
    # ── камера: медленный дрейф к столу, после экрана — мягкий наезд к лицу ──
    z = 1 + .02 * sm(t, T6, T_SCREEN) + .04 * sm(t, T_SCREEN, 7.95)
    tx = lerp(540, fx, .25 * sm(t, T6, 7.9))
    ty = lerp(960, fy, .3 * sm(t, T6, 7.9))
    sh = shake2(t, T_CROWN + .18, 5)
    out = f'<g transform="translate(540 960) scale({z:.4f}) translate({-tx - sh[0]:.2f} {-ty - sh[1]:.2f})">{body}</g>'
    out += R.glitch_flash(t, T6, 0.0)
    set_ink(1.0)
    return lib.svg(out)


# ═════════════════════════ s17: петля ═════════════════════════
T_BR = 25.15                 # «разлО-маю»: крекер ломается
T_STEPS = (wt("на", 25.5) + .03, wt("шаги") + .02, wt("шаги") + .22)    # кусочки встают в ряд на подлокотнике
T_FLICK = 26.40              # «пришлю»: щелчок, кусочек летит к зрителю
T_NOD = 26.85
SLOTS = (928.0, 952.0, 976.0)                 # места кусочков на подлокотнике (ед. рисунка кота, x; верх подлокотника y≈1268)
CR_SEED = 3


def cat_u(x, y, k, ux, uy):
    """Точка тела кота (ед. рисунка) → мир (без поворота и сжатия тела — в s17 их нет)."""
    return x + (ux - CAT.CX) * k, y + (uy - CAT.CBOT) * k


def paw_over(x, y, k, st, side):
    """Подушечка вытянутой передней лапы ПОВЕРХ крекера — та же лапа, что cat.body рисует под ним (тот же кончик), без новой лапы."""
    sx = 1 if side == "r" else -1
    fx = CAT.CX + sx * 25
    pw = st.get("paw" if side == "r" else "paw_l", 0.0)
    pdx = st.get("paw_dx", 70.0) if side == "r" else -st.get("paw_l_dx", 70.0)
    if pw <= .02:
        return ""
    tip = (fx + pdx * pw * 1.6, 1306 - 150 * pw)
    pp = ellipse_pts(tip[0] + 4 * sx, tip[1], 24, 21, 12, rot=-30 * pw * sx)
    o = shape(pp, CAT.CAT, "", w=4.4, seed=245 + (0 if sx > 0 else -1) + 50)
    o += blob(ellipse_pts(tip[0] + 10 * sx, tip[1] + 4, 9, 7, 8), "#e8823a")
    for kk in (-8, 6):
        o += line([(tip[0] + kk - 6, tip[1] - 14), (tip[0] + kk + 2, tip[1] - 4)], 2.2, seed=245 + kk)
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.4f}) translate({-CAT.CX} {-CAT.CBOT})">{o}</g>'


def s17_cat(t):
    st = dict(PE.CAT_ST.get("warm74", dict(blink=.3, smile=1.0, flame_e=1.4)))
    st["perk"] = .8
    st["look"] = (.0 + .5 * sm(t, 25.55, 25.7) * (1 - sm(t, 26.2, 26.35)), .1 + .4 * sm(t, 25.55, 25.7) * (1 - sm(t, 26.2, 26.35)))
    st["blink"] = .06 + .9 * bump(t, 24.95, .16) + .65 * bump(t, T_NOD + .05, .3)
    st["tilt"] = 5 * math.sin(2 * math.pi * .45 * t) + damp(t, T_BR, 2.5, 3, 6) + 6 * bump(t, T_NOD - .05, .5)
    st["drop"] = PE.cat_nod(t, T_NOD, .45, .3) if hasattr(PE, "cat_nod") else .3 * bump(t, T_NOD, .45)
    st["ear"] = 3 * math.sin(t * 2.1) + damp(t, T_BR, 5, 4, 6)
    st["tail"] = -6 + 12 * math.sin(2 * math.pi * .7 * t + .4)
    st["flame_e"] = 1.4 + .9 * bump(t, T_NOD, .5) + .3 * bump(t, T_BR, .3)
    # лапы: держат крекер у груди → отпускают при разломе → правая раскладывает кусочки → щелчок → на месте
    hold = 1 - sm(t, T_BR + .02, T_BR + .25)
    st["paw"] = .45 * hold
    st["paw_dx"] = 54.0
    st["paw_l"] = .45 * hold
    st["paw_l_dx"] = 54.0
    # правая лапа к подлокотнику: к каждому месту кусочка, потом к щелчку
    reach = 0.0
    tx = SLOTS[0]
    marks = [(ts - .14, ts + .06, SLOTS[i]) for i, ts in enumerate(T_STEPS)] + [(T_FLICK - .16, T_FLICK + .02, SLOTS[2] + 4)]
    for a, b, sx_ in marks:
        if a - .06 <= t <= b + .14:
            reach = max(reach, sm(t, a, a + .1) * (1 - sm(t, b, b + .12)))
            tx = sx_
    if T_STEPS[0] - .2 < t < T_FLICK + .2:
        reach = max(reach, .55)
    if reach > .01:
        pw = .253 * reach
        st["paw"] = pw
        st["paw_dx"] = (tx - 861) / (1.6 * .253)
    st["sy"] = 1 + damp(t, T_BR, .02, 3, 7)
    return st


def s17_floor(t):
    """Пол спереди (ракурс снизу): тёплые доски, ком накидки и корона на боку — «трон» снят."""
    o = [blob([(-600, 1700), (1700, 1680), (1700, 2600), (-600, 2600)], "#6a4630")]
    o.append(line([(-600, 1700), (1700, 1680)], 4, INK, taper=0, wmin=1, seed=7901))
    d = "".join(f"M{x} 1700L{x * 1.25 - 120:.0f} 2600" for x in range(-500, 1700, 170))
    o.append(f'<path d="{d}" stroke="#4e3424" stroke-width="3" opacity=".6" fill="none"/>')
    o.append(f'<g transform="translate(820 985) scale(1.3)">{PR.throne_drape(0, 0, 1.0, 0.0, 0.0, t, 0)}</g>')
    o.append(PR.crown(230, 1790, 1.15, -62, shine=.25 + .25 * math.sin(t * 3), seed=1))
    return "".join(o)


def s17(t):
    lib.dyn_begin()
    st = s17_cat(t)
    x, y, k = R.THRONE74["low"]["cat"]
    # крекер: у груди → трещина → разлом, кусочки разлетаются и падают на колени
    crack = sm(t, T_BR - .2, T_BR - .02)
    bu = clamp((t - T_BR) / .45)
    cy_u = 1222 + 24 * ease_in_(bu)
    ccx, ccy = cat_u(x, y, k, 836, cy_u - 4 * math.sin(t * 2.4) * (1 - bu))
    hide = tuple(i for i, ts in enumerate(T_STEPS) if t >= ts - .05)
    cr = PR.cracker(ccx, ccy, k * .36, crack, bu, seed=CR_SEED, rot=-8 + 10 * bu, hide=hide)
    cr += PR.cracker_bits(ccx, ccy - 20, k * .6, clamp((t - T_BR) / .5), seed=CR_SEED, n=6) if T_BR < t < T_BR + .5 else ""
    over = paw_over(x, y, k, st, "r") + paw_over(x, y, k, st, "l") if t < T_BR + .25 else ""
    # кусочки на подлокотнике (верх подлокотника y≈1268 ед.), один улетает к зрителю
    bits = ""
    fly = ""
    for i, ts in enumerate(T_STEPS):
        if t < ts - .05:
            continue
        bx, by = cat_u(x, y, k, SLOTS[i], 1262)
        pop_ = .35 * bump(t, ts - .05, .22)
        if i == 2 and t > T_FLICK:
            q = clamp((t - T_FLICK) / .38)
            e = q * q
            fx_ = lerp(bx, 470, e)
            fy_ = lerp(by, 760, e) - 160 * math.sin(math.pi * q * .8)
            fly = PR.cracker_bit(fx_, fy_, k * .62 * (1 + 9 * e), 40 + 400 * q, seed=CR_SEED + i)
            if q >= 1:
                fly = ""
            continue
        bits += PR.cracker_bit(bx, by, k * .62 * (1 + pop_), -10 + 14 * i, seed=CR_SEED + i)
    sway = .5 * math.sin(2 * math.pi * .4 * t) + damp(t, T_BR, .5, 2.5, 5)
    world, (x, y, k), d = throne_world(t, "warm", st, None, sway, 0.0, 8.0, extra_front=bits, cat_extra=cr + over, floor=s17_floor(t))
    world = [R.warm_tint(w_, .5) if i == 1 else w_ for i, w_ in enumerate(world)]
    if os.environ.get("MASK"):
        g = '<rect x="-3000" y="-3000" width="8000" height="8000" fill="#fff"/>'
        g += mask_svg(CAT.draw(x, y, k, st, t) + cr, "both")
        world = [g]
    if os.environ.get("NOCAM"):
        set_ink(S0)
        return lib.svg(f'<g transform="{lib.cam(CAMH[0], CAMH[1], S0)}">{"".join(world)}</g>')
    z = 1 + .03 * sm(t, 24.65, 27.1) + .03 * bump(t, T_BR, .35) + .02 * bump(t, T_FLICK + .1, .45)
    s = S0 * z
    set_ink(s)
    body = f'<g transform="{lib.cam(CAMH[0] + 2 * math.sin(t * 1.3), CAMH[1] - 30 * sm(t, 24.65, 27.1), s)}">{"".join(world)}</g>'
    return lib.svg(body + (f'<g>{fly_cam(fly, CAMH, s, t)}</g>' if fly else ""))


def fly_cam(svg, camh, s, t):
    """Летящий кусочек — поверх всего, в той же камере (он ближе всего к зрителю)."""
    return f'<g transform="{lib.cam(camh[0] + 2 * math.sin(t * 1.3), camh[1] - 30 * sm(t, 24.65, 27.1), s)}">{svg}</g>'


def ease_in_(u):
    u = clamp(u)
    return u * u


def frame(sid, t):
    return {"s01": s01, "s06": s06, "s17": s17}[sid](t)
