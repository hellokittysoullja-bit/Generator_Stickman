"""Рилс 71 «два лагеря», группа C — кровать и кокон: s01 (хук: кокон уже катится на камеру с кадра 0, плюх на подушку на «Люди»,
брови на «СДВГ», гусеницей на камеру на «объясните»), s03 (сидит в коконе-капюшоне, одеяло сползает на глаза, сдувает край),
s06 (пузыри бьют в лоб, проседает в одеяло по глаза), s22 (петля тем же ракурсом: кот тычет лапой, Дима выпрыгивает, на ногах).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Места — common/room.py, люди и кот — common/people.py, common/cat.py,
предметы — common/props.py. Букв и цифр нет."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import INK, clamp, ease_in, ease_io, ease_out, line  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?«»:").lower() == word:
            return w["start"]
    raise KeyError(word)


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


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


def ex(name, **kw):
    e = dict(people.EXPR["dima"][name])
    e.update(kw)
    return e


def blinkv(t, times, dur=.16):
    v = 0.0
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


def hook_cam(t, t_hit, t_hit2, rot0=3.6, side0=-55.0):
    """Влёт правил 28/29: с 40 % дальше (1/(1+0.4)) за 0.22 с, перелёт с отскоком, поворот rot0 с возвратом, занос сбоку;
    удар +8 % на ударном слоге t_hit2 и маленький на t_hit. Возвращает (масштаб-множитель, поворот, занос)."""
    u = clamp(t / .22)
    e = ease_out(u, 3)
    s = 1 / 1.4 + (1 - 1 / 1.4) * e
    if t > .22:
        s += .06 * math.exp(-7 * (t - .22)) * math.sin(2 * math.pi * 2.2 * (t - .22) + math.pi / 2)
    rot = rot0 * (1 - e) + damp(t, .22, -1.2, 2.0, 6.0)
    side = side0 * (1 - e)
    hit = 0.0
    for th, a in ((t_hit, .035), (t_hit2, .08)):
        if t > th:
            h = t - th
            hit += a * math.exp(-5.5 * h) * (1 if h > .03 else h / .03)
    return s * (1 + hit), rot, side


def whip_in(t, t0, dur=.18):
    """Хвост хлёста на входе плана: сдвиг по x и наклон гаснут за dur."""
    u = clamp((t - t0) / dur)
    e = 1 - ease_out(u, 3)
    return -160 * e, -2.0 * e


# ═════════════════════════ кокон: people.dima_cocoon, положенный по диагонали к камере ═════════════════════════
CO_HX, CO_HY = -410.0, -171.6        # центр головы в своих единицах кокона (people.dima_cocoon, лёжа)


def cocoon_pt(face, k, ang, squash, lp):
    """Точка lp в своих единицах кокона (people.dima_cocoon) — в мир, при той же раскладке, что cocoon_lying."""
    sx, sy = 1 + .18 * squash, 1 - .35 * squash
    a = math.radians(ang)

    def rot(px, py):
        return px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)
    hx, hy = rot(CO_HX * sx * k, CO_HY * sy * k)
    px, py = rot(lp[0] * sx * k, lp[1] * sy * k)
    return face[0] - hx + px, face[1] - hy + py


def cocoon_lying(face, k, ang, roll=0.0, squash=0.0, wriggle=0.0, expr=None, t=0.0, head_up=0.0, feet=1.0, mask=None):
    """Лежащий кокон людей из people.py, повёрнутый на ang° (голова вверху-слева, ступни к камере вниз-вправо) так, что центр
    головы стоит в face. head_up — поворот головы в кадре (0 — прямо к зрителю). mask: None | "head" | "body" — для замера доли кадра."""
    sx, sy = 1 + .18 * squash, 1 - .35 * squash
    lx, ly = CO_HX * sx * k, CO_HY * sy * k
    a = math.radians(ang)
    wx = lx * math.cos(a) - ly * math.sin(a)
    wy = lx * math.sin(a) + ly * math.cos(a)
    x, y = face[0] - wx, face[1] - wy
    r = people.dima_cocoon(0.0, 0.0, k, roll=roll, squash=squash, wriggle=wriggle, expr=expr, t=t, head_rot=-ang + head_up, feet=feet)
    svg = r["svg"]
    if mask:
        svg = mask_svg(svg, mask)
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({ang:.3f})">{svg}</g>'


def mask_svg(svg, kind):
    """Силуэт для замера: всё, что нарисовано, — сплошным цветом (head — красный, body — синий)."""
    col = "1 0 0" if kind == "head" else "0 0 1"
    fid = f"mk{kind}"
    if not any(f'id="{fid}"' in d for d in lib.DEFS):
        r, g, b = col.split()
        lib.DEFS.append(f'<filter id="{fid}"><feColorMatrix type="matrix" values="0 0 0 0 {r} 0 0 0 0 {g} 0 0 0 0 {b} 0 0 0 9 0"/></filter>')
    return f'<g filter="url(#{fid})">{svg}</g>'


# ═════════════════════════ s01: хук ═════════════════════════
T_LU = .30                     # ударный слог «Лю-ди»: плюх на подушку
T_SD = wt("сдвг")              # 0.72
T_SD_HIT = .95                 # ударный слог «СДВ-Г»: второй удар камерой
T_OB = wt("объясните")         # 1.24
T_HOP = .12                    # второй подскок кокона до удара (не плавное ожидание)


def s01_state(t):
    """Кокон с кадра 0 уже катится к камере (из глубины справа), подскок, плюх лицом к зрителю, гусеницей на камеру."""
    fx, fy = R.BC_FACE
    u = clamp(t / T_LU)
    e = ease_out(u, 1.5)
    x = lerp(fx + 300, fx, e)
    y = lerp(fy - 70, fy, e) - 80 * math.sin(math.pi * clamp(t / T_HOP)) - 60 * bump(t, T_HOP, T_LU - T_HOP) - 40 * bump(t, T_SD - .02, .3)
    k = lerp(1.6, 2.2, e)
    ang = lerp(28.0, 58.0, e) + damp(t, T_LU, -5.0, 2.2, 5.5) + 2.6 * math.sin(2 * math.pi * 2.1 * t) * sm(t, .2, .5) + 4 * bump(t, T_SD, .3)
    roll = 720 * (t - .6 * t * t) if t < T_LU else 720 * (T_LU - .6 * T_LU ** 2) + damp(t, T_LU, 40, 2.6, 6) + 140 * (t - T_LU)
    head_up = lerp(-55.0, 0.0, e) + 18 * math.sin(t * 22) * (1 - e) + damp(t, T_LU, 9, 2.4, 5)
    squash = max(0.0, damp(t, T_LU, .55, 2.8, 6.5)) + .35 * bump(t, T_HOP - .02, .1) + .08 * (1 + math.sin(2 * math.pi * 3.0 * t)) * sm(t, .35, .6) - .2 * bump(t, T_SD, .3)
    inch = 0.0
    wr = 0.0
    for a in (T_OB, T_OB + .27):
        p = clamp((t - a) / .27)
        inch += ease_io(p)
        wr += math.sin(math.pi * p)
    k *= 1 + .06 * inch
    y += 40 * inch
    x -= 10 * inch
    squash += .22 * wr
    return dict(x=x, y=y, k=k, ang=ang, roll=roll, head_up=head_up, squash=squash, wriggle=.4 + .8 * wr, inch=inch)


def s01_expr(t):
    if t < T_SD - .04:
        e = ex("surprise_day", brows="worry", mouth="o", open=.25 + .25 * bump(t, T_LU, .3), lid=.95, look=(0, 0))
    elif t < T_OB:
        e = ex("surprise_day", mouth="o", open=.35 + .15 * bump(t, T_SD, .4), lid=1.0, look=(0, 0), scale_n=1.14, scale_f=1.14)
        e["brows"] = ("worry", "up", sm(t, T_SD - .04, T_SD + .08))
    else:
        e = ex("surprise_day", brows="worry", mouth="o", open=.55 + .15 * math.sin(t * 9), lid=.98, look=(0, 0))
    e["hair"] = 10 * math.sin(t * 13) * (1 - sm(t, .5, 1.0)) + 6 * bump(t, T_LU, .25) + 4 * math.sin(t * 7)
    return e


def s01(t):
    lib.dyn_begin()
    bc = R.bed_close(t)
    st = s01_state(t)
    pil_sq = max(0.0, damp(t, T_LU, .9, 2.4, 5.5)) + .15 * bump(t, T_HOP - .02, .14)
    mk = os.environ.get("MASK")
    co = cocoon_lying((st["x"], st["y"]), st["k"], st["ang"], st["roll"], st["squash"], st["wriggle"], s01_expr(t), t, st["head_up"])
    world = [bc["bg"], bc["mattress"], bc["pillow"](pil_sq, st["x"] - R.BC_PILLOW[0]), co, bc["motes"](t)]
    if mk:      # замер доли кадра: голова — красным, кокон — синим, остальное белое
        hd = cocoon_lying((st["x"], st["y"]), st["k"], st["ang"], st["roll"], st["squash"], st["wriggle"], s01_expr(t), t, st["head_up"], mask="body")
        world = ['<rect x="-3000" y="-3000" width="8000" height="8000" fill="#fff"/>', hd]
        world.append(head_mask((st["x"], st["y"]), st["k"], st["ang"], st["squash"], st["head_up"], s01_expr(t)))
    cx0, cy0, s0 = R.CAM_BED_CLOSE
    if os.environ.get("NOCAM"):
        set_ink(s0)
        return lib.svg(f'<g transform="{lib.cam(cx0, cy0, s0)}">{"".join(world)}</g>')
    k, rc, side = hook_cam(t, T_LU, T_SD_HIT)
    sx1, sy1 = shake2(t, T_LU + .01, 14)
    cx = cx0 + side - sx1 + 10 * math.sin(t * 2.3)
    cy = cy0 - sy1 + 30 * st["inch"]
    s = s0 * k * (1 + .04 * sm(t, .4, 1.9))
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s, rc)}">{"".join(world)}</g>')


def head_mask(face, k, ang, squash, head_up, expr):
    """Только голова (как её рисует people.dima_cocoon: dima_head ×1.15 в повороте) — красным, для замера."""
    people.C = people.PAL["dima"]
    sx, sy = 1 + .18 * squash, 1 - .35 * squash
    del sx, sy
    h = people.dima_head(expr)
    return mask_svg(f'<g transform="translate({face[0]:.1f} {face[1]:.1f}) rotate({head_up:.2f}) scale({1.15 * k:.4f})">{h}</g>', "head")


# ═════════════════════════ s22: петля — тот же ракурс, кот тычет, Дима выпрыгивает ═════════════════════════
T_POM = wt("помогает", 35.0)     # 36.37
T_VST = wt("встать", 36.0)       # 37.10
T_SDE = wt("сделать", 36.0)      # 37.71
CAT22 = (1000.0, 1180.0)
CAT22_K = 1.7
D22_SC = 1.12


def s22(t):
    lib.dyn_begin()
    bc = R.bed_close(t)
    fx, fy = R.BC_FACE
    burst = 1.0 if t >= T_VST - .03 else 0.0          # кокон распахивается за кадр: без полупрозрачного наложения
    # кокон: лежит, как в хуке, улыбается, ёрзает от тычков (тычок — на «помогает» и ещё раз)
    poke = bump(t, T_POM, .22) + bump(t, T_POM + .32, .2)
    k, ang = 2.2, 58.0 + 3 * math.sin(t * 5.3) + 6 * poke
    squash = .08 * (1 + math.sin(2 * math.pi * 2.4 * t)) + .25 * poke + .5 * bump(t, T_VST - .2, .22)
    face = (fx + 14 * poke, fy + 10 * math.sin(t * 4.1) + 30 * bump(t, T_VST - .2, .22))
    e = ex("smile_cam", look=(-.5 + .5 * sm(t, T_POM + .1, T_POM + .4), .2), lid=.75 + .25 * poke)
    e["hair"] = 5 * math.sin(t * 9) + 6 * poke
    world = [bc["bg"], bc["mattress"], bc["pillow"](.12 + .3 * bump(t, T_VST - .1, .3) * (1 - burst), 0.0)]
    # кот справа на матрасе (за коконом, зеркально): тянет лапу и тычет в бок кокона, потом довольно садится
    pw = sm(t, T_POM - .25, T_POM - .02) * (1 - sm(t, T_VST - .1, T_VST + .15)) + .25 * bump(t, T_POM + .3, .2)
    cst = dict(paw=clamp(pw), paw_dx=90, look=(.7, -.2), tilt=-8 * pw, tail=10 * math.sin(t * 3.4), perk=bump(t, T_VST, .5),
               smile=sm(t, T_SDE - .1, T_SDE + .2), blink=blinkv(t, [36.25, 37.95]))
    if t > T_VST + .1:
        cst["look"] = (.4, -.9 + .5 * sm(t, T_SDE, T_SDE + .3))
    cat_y = CAT22[1] - 30 * bump(t, T_VST + .05, .3)
    cat = people.cat_svg(CAT22[0], cat_y, CAT22_K, cst, t)
    world.append(f'<g transform="translate({2 * CAT22[0]:.1f} 0) scale(-1 1)">{cat}</g>')      # зеркально: лапа влево, к кокону
    if burst < 1:
        # нога в полосатом носке торчит из-под края одеяла (верхний бок кокона ближе к камере), пальцы шевелятся
        a1 = cocoon_pt(face, k, ang, squash, (-60, -300))
        dv = (math.cos(math.radians(ang - 70)), math.sin(math.radians(ang - 70)))
        wig = 8 * math.sin(t * 10)
        sock = PR.sock_worn(a1[0], a1[1], k * .5, (dv[0], dv[1] + wig * .01), 1.0, seed=3)
        co = cocoon_lying(face, k, ang, 300 * t, squash, .5 + .6 * poke, e, t, 2 * math.sin(t * 3))
        world += [f'<g opacity="{1 - burst:.3f}">{co}{sock}</g>']
    # Дима выпрыгивает: таз из кокона вверх по дуге, приземляется на матрас на ноги, руки вверх
    cam_up = 0.0
    if burst > 0:
        u = clamp((t - (T_VST - .04)) / (T_SDE - T_VST + .02))
        hx = lerp(fx + 160, 600, u)
        land = 1760 - 598 * D22_SC
        hy = lerp(fy + 300, land, u) - 520 * 4 * u * (1 - u) + damp(t, T_SDE - .02, 30, 2.6, 6)
        de = ex("laugh_day", hair=10 * math.sin(t * 12) * (1 - sm(t, T_SDE, T_SDE + .4)))
        if t > T_SDE + .05:
            de = ex("smile_cam", look=(0, .1), hair=3 * math.sin(t * 6))
        st = people.stand_kw(hx, hy, D22_SC)
        if u < 1:      # ноги в воздухе поджаты
            tuck = 4 * u * (1 - u)
            st = {"feet": {kk: ((v[0][0] + 60 * tuck, v[0][1] - 260 * tuck * D22_SC), v[1]) for kk, v in st["feet"].items()}}
        wv = 60 * math.sin(t * 8) * (1 - sm(t, T_SDE, T_SDE + .3))
        sc_ = D22_SC * people.HEIGHT["dima"]
        arms = {"f": ("ik", (hx - 300 * sc_, hy + (-700 + wv) * sc_), 1), "n": ("ik", (hx + (300 - 140 * sm(t, T_SDE - .1, T_SDE + .2)) * sc_, hy + (-560 - wv * .5) * sc_ + 420 * sc_ * sm(t, T_SDE - .1, T_SDE + .2)), -1)}
        fig = people.dima(hx, hy, D22_SC, de, "hooray", feet=st["feet"], arms=arms, lean_add=-.04 * math.sin(t * 7))
        # одеяло распахнулось и закрутилось вокруг ног: взлетает вместе с ним и опадает на кровать к ступням
        a_n, a_f = st["feet"]["n"][0], st["feet"]["f"][0]
        mx, my = (a_n[0] + a_f[0]) / 2, (a_n[1] + a_f[1]) / 2 - 60
        bu = clamp((t - (T_VST - .06)) / .7)
        flat = sm(t, T_SDE - .05, T_SDE + .2)
        bl = people.cocoon_blanket(0, 0, 1.0, min(.32, bu), t)
        blank = (f'<g transform="translate({mx:.1f} {my + 60 * flat:.1f}) rotate({-14 + 18 * math.sin(t * 9) * (1 - flat):.1f}) '
                 f'scale({1.05 + .25 * flat:.3f} {1.05 - .45 * flat:.3f})">{bl}</g>')
        world += [fig["svg"], blank]
        cam_up = sm(t, T_VST, T_SDE + .1)
    world.append(bc["motes"](t))
    cx0, cy0, s0 = R.CAM_BED_CLOSE
    sx1, sy1 = shake2(t, T_SDE, 10)
    cx = cx0 + 8 * math.sin(t * 2.1) - sx1 + 40 * cam_up
    cy = cy0 - 260 * cam_up + 40 * bump(t, T_VST, .3) - sy1
    s = s0 * (1.03 + .02 * sm(t, 36.2, T_VST) - .18 * cam_up)
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s, .4 * math.sin(t * 1.3))}">{"".join(world)}</g>')


# ═════════════════════════ кровать средним планом: Дима сидит в коконе-капюшоне (s03, s06) ═════════════════════════
HOOD_K = 1.12
HOOD_BASE = (560.0, 1300.0)     # центр дна кокона: сидит на матрасе, ступни свисают через переднюю царгу


def hood_cocoon(t, expr, sag=0.0, tilt=0.0, sink=0.0, dx=0.0, squash=0.0):
    """Сидящий кокон-капюшон (people.dima_cocoon hood=True) с наклоном tilt° вокруг дна; sink 0…1 — проседает в одеяло: кокон
    опускается, спереди поднимается край одеяла (props.blanket) до глаз. Возвращает (svg, лицо в мире)."""
    x, y = HOOD_BASE[0] + dx, HOOD_BASE[1] + 200 * sink
    r = people.dima_cocoon(x, y, HOOD_K, hood=True, sag=sag, expr=expr, t=t, squash=squash, feet=1.0)
    hx, hy = r["head"]
    svg = f'<g transform="rotate({tilt:.2f} {x:.1f} {y:.1f})">{r["svg"]}'
    if sink > .01:
        h = lerp(300, 760, sink)
        svg += PR.blanket(x, HOOD_BASE[1] + 30, 1.0, w=960, h=h, seed=5, col="quilt", bump=1.0)
    svg += "</g>"
    a = math.radians(tilt)
    fx, fy = x + (hx - x) * math.cos(a) - (hy - y) * math.sin(a), y + (hx - x) * math.sin(a) + (hy - y) * math.cos(a)
    return svg, (fx, fy)


def sill_cat(t, eye=0.0):
    """Кот клубком на подоконнике в глубине (спит; в s08 его поднимает группа F)."""
    return people.cat_curl(R.BM_SILL[0] + 20, R.BM_SILL[1] + 4, .55, dict(eye=eye, breath=1.0, tail=4 * math.sin(t * 1.3)), t)


def puff_lines(x, y, u, seed=0):
    """Сдул край одеяла: три коротких штриха-выдоха вверх от губ."""
    if not 0 < u < 1:
        return ""
    o = ""
    for i, a in enumerate((-110, -90, -70)):
        r0, r1 = 30 + 120 * u, 70 + 150 * u
        aa = math.radians(a)
        o += line([(x + math.cos(aa) * r0, y + math.sin(aa) * r0), (x + math.cos(aa) * r1, y + math.sin(aa) * r1)], 6 * (1 - u) + 1.5, INK,
                  taper=.5, wmin=.2, seed=6100 + seed + i)
    return o


# ═════════════════════════ s03: сидит в коконе-капюшоне и не понимает ═════════════════════════
T3_DIMA, T3_PRAV, T3_NE, T3_PON = wt("дима", 4.0), wt("правда", 4.0), wt("не", 4.9), wt("понимает", 4.9)   # 4.47 4.69 4.99 5.08


def s03(t):
    lib.dyn_begin()
    bm = R.bed_mid(t)
    # одеяло со лба съезжает на глаза на «понимает», он сдувает край — край подпрыгивает и снова сползает чуть ниже бровей
    cover = .15 * sm(t, 3.78, 4.3) + .85 * sm(t, T3_PON - .02, T3_PON + .16) - .45 * bump(t, T3_PON + .3, .3)
    cover = clamp(cover)
    blink = blinkv(t, [T3_DIMA + .05], .42)          # медленное моргание
    if t < T3_NE - .02:
        e = ex("unsure", bags=False, look=(.3 * math.sin(t * 1.4), .1), lid=.8)
    else:
        e = ex("puzzled", look=(0, -.4 + .3 * sm(t, T3_PON + .3, T3_PON + .5)))
        if T3_PON + .25 < t < T3_PON + .5:
            e = dict(e, mouth="o", open=.5)
    e["closed"] = blink
    e["cover"] = cover
    tilt = 1.5 * math.sin(t * 2.1) - 7 * sm(t, T3_PRAV - .05, T3_NE + .1) + 3 * bump(t, T3_PON + .3, .3)
    co, face = hood_cocoon(t, e, sag=0.0, tilt=tilt, squash=.05 * math.sin(t * 2.6))
    puff = puff_lines(face[0] + 40, face[1] + 20 * HOOD_K, clamp((t - T3_PON - .28) / .3))
    world = [bm["bg"], sill_cat(t), bm["bed"], co, puff]
    cx0, cy0, s0 = R.CAM_BED_MID
    z = sm(t, 3.78, 5.82)
    cx = lerp(face[0] + 40, face[0], z) + 6 * math.sin(t * 1.7)
    cy = lerp(face[1] + 330, face[1] + 230, z)
    s = s0 * (1.45 + .2 * z)
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s, -1.2 * z * (tilt < 0) + .3 * math.sin(t * 1.1))}">{"".join(world)}</g>')


# ═════════════════════════ s06: пузыри бьют в лоб, проседает в одеяло ═════════════════════════
T6_DEL, T6_CHTO, T6_TUT, T6_SL = wt("делаешь", 9.0), wt("что", 9.5), wt("тут", 9.5), wt("сложного", 9.5)   # 9.41 9.78 9.9 10.13
HITS6 = [(T6_DEL, (1, 0), 1.25, "arrow_up"), (T6_CHTO, (1, -.5), .9, "arrow_up"), (T6_TUT + .04, (-1, -.4), .9, "waves")]


def s06(t):
    lib.dyn_begin()
    bm = R.bed_mid(t)
    sink = sm(t, T6_SL - .02, T6_SL + .3)
    hit_any = sum(bump(t, th, .25) for th, *_ in HITS6)
    e = ex("puzzled", look=(.2, -.6), lid=.9)
    if hit_any > .2:
        e = ex("squish", closed=.8)
    if t > T6_SL:
        e = ex("puzzled", look=(0, -.2), lid=.95, brows="worry")
    e["hair"] = 8 * hit_any
    rock = sum(damp(t, th, 7 * d[0], 2.6, 5.5) for th, d, *_ in HITS6)
    co, face = hood_cocoon(t, e, sag=.12, tilt=rock + 1.2 * math.sin(t * 2.3), sink=sink, squash=.12 * hit_any)
    # пузыри влетают из-за правого края (жёлтый лагерь), бьют в лоб, отскакивают и разлетаются
    bub = ""
    for i, (th, d, kk, icon) in enumerate(HITS6):
        fly = clamp((t - (th - .22)) / .22)
        if fly <= 0:
            continue
        brow = (face[0] + 10, face[1] - 60)
        start = (brow[0] + 900 * d[0], brow[1] - 300 + 200 * i)
        if t < th:
            p = lerp2(start, brow, ease_in(fly, 1.6))
            wob, sc = 0.0, 1.0
        else:
            v = t - th
            p = (brow[0] + d[0] * 520 * v + 40 * (-1) ** i * v, brow[1] - 900 * v + 1600 * v * v)
            wob, sc = math.exp(-6 * v) * math.cos(30 * v), 1 - .25 * clamp(v / .8)
        bub += PR.comment_bubble(p[0], p[1], kk * sc, icon, 1.0, wob, seed=60 + i, tail=(-60 * d[0], 50), col=PR.BUB_YELLOW)
        # штрихи удара в момент касания
        hu = (t - th) / .2
        if 0 < hu < 1:
            for j, ang in enumerate((-160, -130, -50, -20)):
                aa = math.radians(ang)
                r0 = 150 + 60 * hu
                bub += line([(brow[0] + math.cos(aa) * r0, brow[1] + math.sin(aa) * r0),
                             (brow[0] + math.cos(aa) * (r0 + 60), brow[1] + math.sin(aa) * (r0 + 60))], 7 * (1 - hu) + 1.5, INK, taper=.5,
                            wmin=.2, seed=6200 + 10 * i + j)
    world = [bm["bg"], sill_cat(t), bm["bed"], co, bub]
    cx0, cy0, s0 = R.CAM_BED_MID
    sx1 = sum(shake2(t, th + .01, 12 * kk)[0] for th, d, kk, _ in HITS6)
    sy1 = sum(shake2(t, th + .01, 12 * kk)[1] for th, d, kk, _ in HITS6)
    cx = face[0] - sx1 + 8 * math.sin(t * 1.9)
    cy = face[1] + 260 - 120 * sink - sy1
    s = s0 * (1.4 + .08 * sink)
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s, .5 * math.sin(t * 1.4))}">{"".join(world)}</g>')


def frame(sid, t):
    return {"s01": s01, "s03": s03, "s06": s06, "s22": s22}[sid](t)
