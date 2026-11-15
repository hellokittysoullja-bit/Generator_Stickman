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


def throne_world(t, light, st, crown=None, sway=0.0, drape_u=1.0, tassel=18.0, extra_front="", cat_extra=""):
    """Мир хука/петли (кадр): кресло вида low, накидка, кот, корона, подлокотники, свет. -> (слои, (x, y, k))."""
    d = R.throne_scene(t, light, "low", 0.0)
    x, y, k = d["cat"]
    cat = CAT.draw(x, y, k, st, t) + cat_extra
    if crown is not None:
        cat += crown_on(x, y, k, st, t, **crown)
    drape = R.drape74("low", t, drape_u, tassel) if drape_u > .001 else ""
    tf = f'rotate({sway:.3f} 540 1640)'
    fg = f'<g transform="{tf}">{d["back"]}{drape}{d["seat"]}{cat}{d["arms"]}{extra_front}</g>'
    return [d["bg"], fg, d["light"], d["motes"]], (x, y, k), d


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


def frame(sid, t):
    return {"s01": s01}[sid](t)
