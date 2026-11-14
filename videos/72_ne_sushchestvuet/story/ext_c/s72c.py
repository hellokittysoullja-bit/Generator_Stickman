"""Рилс 72 «СДВГ не существует», группа C — хук, поворот, петля:
s01 (хук: надменный кот на кухонном столе уже в середине кивка, телефон крутится волчком; прихлоп лапой на «СДВГ», второй кивок
на «ГЭ», качает головой на «не»), s06 (поворот: белый сбой, темнота, тлеет искра и дым, на 7.35 вспыхивает костёр),
s22 (петля тем же ракурсом, что s01, ночью у костра: кот кладёт ледяной кубик на место телефона, тёплый кивок).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Места — common/room.py, кот — common/cat.py, предметы — common/props.py.
Букв и цифр нет. NOCAM=1 — без камеры (замер движения рисунка), MASK=face|phone — силуэт для замера доли кадра."""
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
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line  # noqa: E402,F401

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


def keys(t, ks):
    """Кусочная интерполяция ключей [(t, value)] с ease_io; value — число или кортеж."""
    if t <= ks[0][0]:
        return ks[0][1]
    for (ta, a), (tb, b) in zip(ks, ks[1:]):
        if t <= tb:
            u = ease_io((t - ta) / max(1e-6, tb - ta))
            if isinstance(a, tuple):
                return tuple(x + (y - x) * u for x, y in zip(a, b))
            return a + (b - a) * u
    return ks[-1][1]


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def hook_cam(t, t_hit, t_hit2, rot0=3.6, side0=-55.0):
    """Влёт правил 28/29: с 40 % дальше (1/(1+0.4)) за 0.22 с, перелёт с отскоком, поворот rot0 с возвратом, занос сбоку;
    удар +8 % на ударном слоге t_hit2 и поменьше на t_hit. Возвращает (масштаб-множитель, поворот, занос)."""
    u = clamp(t / .22)
    e = ease_out(u, 3)
    s = 1 / 1.4 + (1 - 1 / 1.4) * e
    if t > .22:
        s += .06 * math.exp(-7 * (t - .22)) * math.sin(2 * math.pi * 2.2 * (t - .22) + math.pi / 2)
    rot = rot0 * (1 - e) + damp(t, .22, -1.2, 2.0, 6.0)
    side = side0 * (1 - e)
    hit = 0.0
    for th, a in ((t_hit, .04), (t_hit2, .08)):
        if t > th:
            h = t - th
            hit += a * math.exp(-5.5 * h) * (1 if h > .03 else h / .03)
    return s * (1 + hit), rot, side


def mask_svg(svg, kind):
    """Силуэт для замера: всё нарисованное — сплошным цветом (face — красный, phone — синий)."""
    col = "1 0 0" if kind == "face" else "0 0 1"
    fid = f"mk{kind}"
    if not any(f'id="{fid}"' in d for d in lib.DEFS):
        r, g, b = col.split()
        lib.DEFS.append(f'<filter id="{fid}"><feColorMatrix type="matrix" values="0 0 0 0 {r} 0 0 0 0 {g} 0 0 0 0 {b} 0 0 0 9 0"/></filter>')
    return f'<g filter="url(#{fid})">{svg}</g>'


# ═════════════════════════ кот: голова в системе рисунка cat.draw (для бровки-складки и замера морды) ═════════════════════════
def head_tf(x, y, k, st):
    """Тот же переход, что у головы в cat.draw: мир ← рисунок (единицы кота 384 в высоту)."""
    sl = st.get("sleep", 0.0)
    br = 1 + 0.012 * math.sin(st.get("_t", 0.0) * 2 * math.pi / 3.1) * (1 + 1.5 * sl)
    sy = br * (1 - .2 * sl) * st.get("sy", 1.0)
    hy = -(sy - 1) * (CAT.CBOT - CAT.NECK[1]) + 34 * sl + 70 * st.get("drop", 0.0)
    tilt = st.get("tilt", 0.0) + 16 * sl
    return (f'translate({x:.2f} {y:.2f}) rotate({st.get("rot", 0.0):.2f}) scale({k:.4f}) translate({-CAT.CX} {-CAT.CBOT}) '
            f'translate({22 * sl:.2f} {hy:.2f}) rotate({tilt:.2f} {CAT.NECK[0]} {CAT.NECK[1]})')


def face_mask(x, y, k, st, t):
    """Морда кота целиком (голова с ушами, как её рисует cat.head) — красным, для замера."""
    return mask_svg(f'<g transform="{head_tf(x, y, k, st)}">{CAT.head(st, t)}</g>', "face")


# ═════════════════════════ s01: хук ═════════════════════════
T_HIT = wt("сдвг")          # 0.22: прихлоп и кивок (удар камерой)
T_HIT1 = .24
T_GE = .86                  # ударный «ГЭ»: второй кивок, удар камерой +8 %
T_NE = wt("не")             # 1.15: качает головой
T_MID = .55                 # второй подскок телефона и малый кивок между ударами


def s01_cat(t):
    """Кот: в кадре 0 голова уже идёт вниз (кивок), лапа уже занесена; прихлоп на T_HIT1, малый кивок T_MID, большой T_GE,
    медленно качает головой с T_NE. Глаза полуприкрыты, бровь поднята, ухмылка."""
    # кивок: голова-наклон вниз (tilt вперёд даёт поворот морды; кивок — сдвиг головы вниз drop и сжатие тела)
    if t < T_HIT1:
        nod = lerp(.45, 1.0, clamp(t / T_HIT1) ** .8)        # уже в середине кивка, скорость с кадра 0
    else:
        nod = 1.0 - ease_out(clamp((t - T_HIT1) / .25), 2)
    nod += .55 * bump(t, T_MID - .08, .26) + 1.0 * bump(t, T_GE - .16, .42)
    shake = sm(t, T_NE, T_NE + .08) * math.sin(2 * math.pi * 1.6 * (t - T_NE)) if t > T_NE else 0.0
    st = dict(_t=t)
    st["drop"] = .38 * nod
    st["tilt"] = -5.0 * nod + 6 * shake + 2.0 * math.sin(t * 9) * (1 - sm(t, .3, .6))
    st["turn"] = -.18 + .55 * shake + .1 * math.sin(t * 5.3)
    st["look"] = (-.35 + .5 * shake, -.55)
    lid = .42 + .1 * nod - .08 * bump(t, T_GE, .3)
    st["blink_L"] = lid + .08
    st["blink_R"] = lid
    st["ear"] = 14 * math.sin(t * 19) * (1 - sm(t, .3, .7)) + damp(t, T_HIT1, 18, 4.5, 6) + damp(t, T_GE, 12, 4.5, 6) + 4 * math.sin(t * 7)
    st["perk"] = .2 + .2 * bump(t, T_GE, .3)
    st["tail"] = 16 * math.sin(2 * math.pi * 1.9 * t + 1.2) + damp(t, T_HIT1, 10, 3, 5)
    st["flame_e"] = 1.6 + .6 * bump(t, T_HIT1, .3)
    st["smile"] = 0.0
    # лапа: в кадре 0 уже занесена и падает; прихлоп на T_HIT1; малый тык на T_MID; потом лежит
    if t < T_HIT1:
        paw = lerp(.75, .04, ease_in2(t / T_HIT1))
    else:
        paw = .04 + .3 * bump(t, T_MID - .14, .26)
    st["paw"] = paw
    st["paw_dx"] = 40.0
    # тело: сжатие на ударе и вдох-подскок
    sq = damp(t, T_HIT1, .07, 3.0, 7) + .05 * bump(t, T_GE - .1, .3)
    st["sy"] = 1 - sq - .02 * nod
    st["sx"] = 1 + .6 * sq
    st["rot"] = -1.2 * nod + 1.5 * shake
    return st


def ease_in2(u):
    u = clamp(u)
    return u * u


def s01_phone(t):
    """Телефон экраном вниз: с кадра 0 крутится волчком и подпрыгивает; прихлоп на T_HIT1 — подскок и встал; T_MID — малый подскок."""
    px, py = R.KC_PHONE
    if t < T_HIT1:
        spin = -40 + 1500 * t
        hop = 30 * abs(math.sin(2 * math.pi * 4.2 * t))
        dx = 40 * (1 - t / T_HIT1)
    else:
        spin0 = -40 + 1500 * T_HIT1
        spin = spin0 + (14 - spin0 % 180 + (180 if spin0 % 180 > 14 else 0)) * ease_out(clamp((t - T_HIT1) / .2), 3) + damp(t, T_HIT1 + .2, 6, 3, 6)
        hop = 70 * bump(t, T_HIT1 + .01, .28) + 34 * bump(t, T_MID - .04, .22) + 18 * bump(t, T_GE - .02, .2)
        dx = 0.0
    return px + dx, py - hop, spin


def s01(t):
    lib.dyn_begin()
    kc = R.kitchen_close(t)
    x, y = R.KC_CAT
    k = R.KC_CAT_K
    st = s01_cat(t)
    ph_x, ph_y, spin = s01_phone(t)
    phk = 1.5
    shadow_ph = blob(ellipse_pts(ph_x + 40, R.KC_PHONE[1] + 30, 120 * (1 - .2 * (R.KC_PHONE[1] - ph_y) / 80), 40, 18), "#b08657", .55)
    cat_sh = blob([(x - 160, y - 10), (x + 230, y - 30), (x + 470, y + 60), (x + 40, y + 70)], "#c09468", .65)    # жёсткая тень от окна вправо-вниз
    phone = PR.phone_flat(ph_x, ph_y, phk, rot=0.0, spin=spin, face_down=True)
    st["smug"] = 1.0       # cat.py (группа B): тяжёлые веки, брови вразлёт, ухмылка краем рта
    cat = CAT.draw(x, y, k, st, t)
    over = ""
    # пылинки в луче + искорки-мелочь от удара телефона
    world = [kc["bg"], kc["table"], cat_sh, shadow_ph, phone, cat, over, kc["motes"](t, 1.0)]
    mk = os.environ.get("MASK")
    if mk:
        world = ['<rect x="-3000" y="-3000" width="8000" height="8000" fill="#fff"/>']
        if mk in ("face", "both"):
            world.append(face_mask(x, y, k, st, t))
        if mk in ("phone", "both"):
            world.append(mask_svg(phone, "phone"))
    cx0, cy0, s0 = R.CAM_KC
    if os.environ.get("NOCAM"):
        set_ink(s0)
        return lib.svg(f'<g transform="{lib.cam(cx0, cy0, s0)}">{"".join(world)}</g>')
    kk, rc, side = hook_cam(t, T_HIT1, T_GE)
    sx1, sy1 = shake2(t, T_HIT1 + .01, 12)
    cx = cx0 + side - sx1 + 8 * math.sin(t * 2.3)
    cy = cy0 - sy1
    s = s0 * kk * (1 + .03 * sm(t, .4, 1.6))
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s, rc)}">{"".join(world)}</g>')


# ═════════════════════════ s06: поворот — белый сбой, темнота с искрой, вспышка костра ═════════════════════════
T_CUT = 6.42                # свет гаснет (вместе с глитчем riser)
T_FIRE = 7.35               # костёр вспыхивает


def _glitch_day(t):
    """Дневная комната с креслом-мешком (хвост s05) — до сбоя."""
    br = R.bag_room(t)
    return br["bg"] + PR.bean_bag(R.BB[0], R.BB[1], 1.0, sag=.6)


def s06(t):
    lib.dyn_begin()
    fx, fy = R.FIRE
    if t < T_CUT + 2 / 30:      # день и белый сбой-всполох (2 кадра): срезы кадра сдвинуты, белое заливает
        set_ink(1.0)
        day = f'<g transform="{lib.cam(*R.CAM_BB)}">{_glitch_day(t)}</g>'
        if t < T_CUT:
            return lib.svg(day)
        g = (t - T_CUT) * 30          # 0…2
        cid = []
        out = []
        for i, (y0, h, dx) in enumerate(((120, 160, 70), (520, 90, -110), (900, 210, 140), (1380, 120, -60))):
            c = lib.clip_rect(0, y0, 1080, h)
            out.append(f'<g clip-path="url(#{c})"><g transform="translate({dx * (1 + g):.1f} 0)">{day}</g></g>')
            cid.append(c)
        wh = .75 + .2 * g
        return lib.svg(day + "".join(out) + f'<rect width="1080" height="1920" fill="#ffffff" opacity="{wh:.2f}"/>'
                       + f'<rect y="{700 + 300 * g:.0f}" width="1080" height="26" fill="#0b0f1e" opacity=".7"/>')
    # огонь: искра → вспышка с перелётом → ровное пламя
    if t < T_FIRE:
        u = .05
    else:
        q = t - T_FIRE
        u = .05 + .95 * clamp(q / .22) ** .6 + .12 * math.exp(-5 * q) * math.sin(2 * math.pi * 2.0 * q) * clamp(q / .1)
        u = clamp(u, 0, 1.12)
    uf = clamp(u)
    fs = R.fire_scene(t, uf, "wide")
    world = [fs["sky"], fs["bg"], fs["ground"], fs["stones_back"], fs["fire"], fs["stones_front"], fs["log"]]
    # темнота: почти чёрная вуаль, проём вокруг искры; на вспышке вуаль уходит за 0.3 с
    dk = .93 * (1 - ease_out(clamp((t - T_FIRE) / .32), 2))
    ember = ""
    if dk > .01:
        hole = PR.circle_d(fx + 4, fy - 40, 60 + 10 * math.sin(t * 7))
        world.append(PR.darkness(dk, "#020409", holes=[(hole, .9)], blur_sd=18, box=(-1500, -1500, 2700, 3000)))
        # тонкая струйка дыма над искрой (видна в темноте светлой линией) и сама искра поверх вуали
        e = .5 + .5 * math.sin(t * 7)
        ember += blob(ellipse_pts(fx + 4, fy - 40, 11 + 3 * e, 8 + 2 * e, 10), lib.mix("#c2491e", "#ffd24a", e), dk)
        ember += blob(ellipse_pts(fx + 4, fy - 40, 4.5, 3.5, 8), "#fff2c0", dk)
        pts = [(fx + 6 + 14 * math.sin(t * 2.6 + q * 5) * q, fy - 52 - 330 * q) for q in [i / 16 for i in range(17)]]
        ember += line(pts, 7, "#8b93a6", taper=.7, wmin=.15, seed=7301, op=.75 * dk)
        pts2 = [(fx - 2 + 18 * math.sin(t * 2.1 + 1.7 + q * 4) * q, fy - 50 - 240 * q) for q in [i / 14 for i in range(15)]]
        ember += line(pts2, 5, "#6f7787", taper=.7, wmin=.15, seed=7302, op=.55 * dk)
    world.append(ember)
    # тёплый толчок света на вспышке: короткая оранжевая вуаль по всему кадру (screen), гаснет за 0.4 с
    warm = .16 * math.exp(-6 * max(0.0, t - T_FIRE)) * (1 if t >= T_FIRE else 0)
    # камера: в темноте близко к искре с микродрейфом; на вспышке — лёгкий отъезд и толчок
    q = clamp((t - T_FIRE) / .5)
    e = ease_out(q, 3)
    cx = lerp(fx + 10, 560.0, e) + 6 * math.sin(t * 1.7)
    cy = lerp(fy - 110, 1150.0, e) + 5 * math.sin(t * 1.3 + 1)
    s = lerp(1.9, 1.32, e) * (1 + .03 * (t - T_CUT)) * (1 + .05 * bump(t, T_FIRE, .3)) - .04 * sm(t, T_FIRE + .5, 8.2)
    s = max(s, 1.0)
    set_ink(s)
    body = f'<g transform="{lib.cam(cx, cy, s, -.4 * bump(t, T_FIRE, .4))}">{"".join(world)}</g>'
    if warm > .01:
        body += f'<rect width="1080" height="1920" fill="#ffb054" opacity="{warm:.3f}" style="mix-blend-mode:screen"/>'
    return lib.svg(body)


def frame(sid, t):
    return {"s01": s01, "s06": s06}[sid](t)
