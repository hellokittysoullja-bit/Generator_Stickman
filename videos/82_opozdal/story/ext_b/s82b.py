"""Рилс 82 «Опять опоздал?», группа B: люди, кот, призыв. Время — только из shots.json и voice/words.json (слово по индексу wN).
s04: подъезд ×3 — «каждое» (w10) щётка, «утро» (w11) худи наизнанку, третий — полотенце; «не понимает» (w13–w14) автобус уходит.
s06: призыв «Телеграм» модулем scripts/story_cta_tg.py: PRESS = W[22].start + 0.12, T0 = PRESS − 1.10.
s07: кот крутит проектор, на стене сценки утра Димы: «такие» (w26), «истории» (w27), «Диму» (w29).
s08: прихожая, лента под потолком: «минуты» (w31) смотрит, «съел» (w32) укус, «твой мозг» (w33–w34) палец к виску.
s12: прихожая, мелочи бледным пунктиром: «мелочи» (w51) вспыхивают, «не запоминаются» (w53) гаснут, Дима проходит мимо.
s15: ряд людей: «люди» (w61) проезд, «помнят» (w64) короткие ленточки, «короче» (w67) длинные встают за спиной.
s16: люди уходят со шлейфами лент, Дима остаётся и кивает на «шли» (w70).
frame(sid, t) -> SVG 1080×1920; t — общее время ролика."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(STORY)))
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import lib  # noqa: E402
import people  # noqa: E402
import props as P  # noqa: E402
import room as R  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, svg  # noqa: E402,F401

INK = lib.INK
W = json.load(open(os.path.join(STORY, "voice", "words.json")))
W = W if isinstance(W, list) else W["words"]
SH = {s["id"]: s for s in json.load(open(os.path.join(STORY, "shots.json")))["shots"]}


def ws(i):
    return W[i]["start"]


def we(i):
    return W[i]["end"]


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def span(sid):
    return SH[sid]["t0"] - .2, SH[sid]["t1"] + .2


def frame_svg(body, cx, cy, s, rot=0.0, bg="#f4efe4", over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def kick(t, t0, amp=1.0, dur=.35):
    """Толчок: быстро вверх и затухание (0 до t0)."""
    if t < t0:
        return 0.0
    u = (t - t0) / dur
    return amp * math.exp(-3.5 * u) * math.sin(math.pi * min(1.0, u * 2.2)) if u < 3 else 0.0


def shake(t, t0, amp=8.0, dur=.3, seed=0):
    if t < t0 or t > t0 + dur:
        return 0.0, 0.0
    e = 1 - (t - t0) / dur
    return amp * e * math.sin(t * 91 + seed), amp * e * math.cos(t * 77 + seed * 2)


def pop(t, t0, dur=.18):
    """0 до t0, затем быстрый рост с перелётом к 1."""
    if t <= t0:
        return 0.0
    return lib.back_out(clamp((t - t0) / dur)) if hasattr(lib, "back_out") else ease_out(clamp((t - t0) / dur))


# ═══════════════════════════════ s06: призыв «Телеграм» ═══════════════════════════════
def s06(t):
    import story_cta_tg as tg
    press = ws(22) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=COMMON)


# ═══════════════════════════════ s08: прихожая, укус ленты, палец к виску ═══════════════════════════════
S08_X = 640.0
S08_K = .72
S08_STRIP = (-300.0, 380.0, 2100.0)      # x0, y, x1 — лента под потолком от стены до стены


def s08(t):
    a, b = span("s08")
    h = R.hall82(t, "morning")
    o = [h["bg"], h["door"](0.0)]
    t_bite, t_tap1, t_tap2 = ws(32), ws(33), ws(34)
    x0, sy, x1 = S08_STRIP
    k_s = 1.5
    # укусы: два старых (с утра) и новый на «съел»
    nb = clamp((t - t_bite) / .14)
    bites = [(.2, 60, 1, 1.0), (.66, 54, -1, 1.0), (.43, 78, 1, ease_out(nb))]
    crumbs = [(2, t - t_bite)] if t > t_bite else []
    sway = 6 * math.sin(t * 1.7)
    strip = P.time_strip(x0, sy + sway, x1, k_s, bites=bites, crumbs_t=crumbs, seed=82)
    # нити, на которых висит лента
    for xx in (60, 760, 1500):
        o.append(line([(xx, -600), (xx, sy + sway - 60 * k_s)], 2.6, "#7b6a55", taper=0, wmin=1, seed=8200 + int(xx)))
    o.append(strip)
    # крошки нового укуса падают на пол
    bx, by = P.strip_bite_xy(x0, sy + sway, x1, k_s, .43, 1)
    if t > t_bite:
        o.append(P.strip_crumbs(bx, by, k_s, t - t_bite, seed=3, n=9, floor=R.FL82))
    # старые крошки ещё сыплются с первого кадра (движение с кадра 0)
    ox, oy = P.strip_bite_xy(x0, sy + sway, x1, k_s, .2, 1)
    o.append(P.strip_crumbs(ox, oy, k_s, (t - a) * .9 + .05, seed=7, n=5, floor=R.FL82))
    # «ам» — щёлк на укусе: штрихи от края
    if 0 < t - t_bite < .3:
        e = (t - t_bite) / .3
        for i in range(5):
            ang = math.radians(40 + i * 25)
            r0, r1 = 70 + 40 * e, 110 + 60 * e
            o.append(line([(bx + r0 * math.cos(ang), by + r0 * math.sin(ang)), (bx + r1 * math.cos(ang), by + r1 * math.sin(ang))], 5,
                          INK, seed=8210 + i, op=1 - e))
    # Дима: сначала смотрит на ленту (голова вверх), на «съел» вздрагивает, на «твой мозг» стучит пальцем по виску
    hip_y = people.hip_on_floor(R.FL82, S08_K)
    flinch = kick(t, t_bite, 1.0, .35)
    if t < t_tap1 - .18:
        u = ease_io(clamp((t - (a - .05)) / .35))
        fig = people.dima82(S08_X, hip_y, S08_K, "look82" if t < t_bite else "puzzled82", ("d82_rest", "d82_look_up"), t=t, u=max(.35, u),
                            feet="stand", head_add=-.08 * flinch, lean_add=-.04 * flinch)
    else:
        # два стука: на «твой» и на «мозг»; между — палец чуть отходит
        tap = 1.0
        for tt in (t_tap1, t_tap2):
            d = t - tt
            if -.1 < d < .16:
                tap = min(tap, abs(d) / .1 if d < 0 else clamp(d / .16) ** .5) if d >= 0 else tap
        e_in = ease_out(clamp((t - (t_tap1 - .18)) / .18))
        tap_u = lerp(0.0, 1.0, e_in) * (.65 + .35 * tap)
        fig = people.dima82_temple(S08_X, hip_y, S08_K, tap_u, t=t, expr="squint82", feet="stand", head_add=-.1 + .05 * math.sin(t * 9))
    o.append(fig["svg"])
    # камера: мягкий наезд к Диме, толчок на «съел»
    z = ease_io(clamp((t - a) / (b - a)))
    s_ = lerp(1.0, 1.1, z) * (1 + .035 * kick(t, t_bite, 1.0, .4))
    sx, sy_ = shake(t, t_bite, 9, .28, 3)
    cx = lerp(700, 660, z) + sx
    cy = lerp(1000, 1010, z) + sy_
    return frame_svg("".join(o), cx, cy, s_, rot=.4 * math.sin(t * .8), bg="#e9d6b4")


# ═══════════════════════════════ s12: прихожая, мелочи бледным пунктиром ═══════════════════════════════
def faint(svg_, op, gid):
    """Предмет «незамеченным» карандашом: серый графит, штриховой пунктир (маска косых штрихов), прозрачность op."""
    lib.DEFS.append(f'<pattern id="hp{gid}" width="13" height="13" patternUnits="userSpaceOnUse" patternTransform="rotate(32)">'
                    f'<rect width="7" height="13" fill="#fff"/></pattern>'
                    f'<mask id="hm{gid}" maskUnits="userSpaceOnUse" x="-3000" y="-3000" width="9000" height="9000">'
                    f'<rect x="-3000" y="-3000" width="9000" height="9000" fill="url(#hp{gid})"/></mask>'
                    f'<filter id="hf{gid}" x="-20%" y="-20%" width="140%" height="140%"><feColorMatrix type="matrix" '
                    f'values=".16 .26 .06 0 0  .16 .26 .06 0 0  .16 .26 .06 0 .03  0 0 0 1 0"/></filter>')
    return f'<g opacity="{op:.3f}" mask="url(#hm{gid})"><g filter="url(#hf{gid})">{svg_}</g></g>'


S12_K = .78


def s12(t):
    a, b = span("s12")
    h = R.hall82(t, "morning")
    o = [h["bg"], h["door"](0.0)]
    t_m, t_no = ws(51), ws(53)
    an = R.HALL82
    kx, ky = an["keys"]
    stx, sty = an["stool"]
    kex, key = an["stove"]
    items = [(P.thief_keys(kx, ky - 40, 1.2, 0.0, t, seed=1), (kx, ky + 170), t_m),
             (P.thief_sock(stx + 30, sty + 10, 1.0, 0.0, t, seed=2, rot=-80), (stx + 10, sty - 70), t_m + .1),
             (P.thief_kettle(kex, key, .95, 0.0, .35 + .25 * math.sin(t * 3), t, seed=3), (kex, key - 100), t_m + .2)]
    for i, (sv, (gx, gy), tf) in enumerate(items):
        fl = math.exp(-((t - tf - .12) / .2) ** 2)            # вспышка на «мелочи»
        fade = ease_io(clamp((t - t_no) / .55))                # гаснут на «не запоминаются»
        op = (.5 + .5 * fl) * (1 - .7 * fade) + .03 * math.sin(t * 5 + i)
        if fl > .02:
            gg = lib.rad_grad([(0, "#fff6c8", .85 * fl), (1, "#fff6c8", 0)], gx, gy, 190)
            o.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="190" fill="url(#{gg})"/>')
        sc = 1 + .08 * fl
        solid = f'<g opacity="{.75 * fl:.3f}" filter="url(#hf{i})">{sv}</g>' if fl > .02 else ""
        o.append(f'<g transform="translate({gx:.1f} {gy:.1f}) scale({sc:.4f}) translate({-gx:.1f} {-gy:.1f})">{faint(sv, op, i)}{solid}</g>')
    # Дима идёт через прихожую ускоренно, мимо мелочей, не глядя на них
    x = 250 + 600 * (t - a)                    # к вспышке «мелочи» он уже между ключами и плитой
    hip_y = people.hip_on_floor(R.FL82, S12_K)
    ph = (x - 250) / (2 * 210 * S12_K)
    fig = people.dima82_walk(x, hip_y, S12_K, ph, t=t, expr="calm82", mug=True)
    o.append(fig["svg"])
    cx = lerp(700, 880, ease_out(clamp((t - a) / (t_m - a)))) if t < t_no else lerp(880, 1150, ease_io(clamp((t - t_no) / (b - t_no))))
    s_ = .84 * (1 + .02 * kick(t, t_m, 1.0, .4))
    return frame_svg("".join(o), cx, 1040, s_, rot=.3 * math.sin(t * .7), bg="#e9d6b4")


# ═══════════════════════════════ s07: кот крутит проектор, на стене сценки утра Димы ═══════════════════════════════
S07_SCR = (300.0, 170.0, 1040.0, 740.0)        # прямоугольник света на стене
S07_PROJ = (580.0, 1170.0, 1.15)               # проектор: центр дна, масштаб
S07_CAT = (290.0, 1300.0, .95)


def _sepia(gid):
    lib.DEFS.append(f'<filter id="sp{gid}" x="-10%" y="-10%" width="120%" height="120%"><feColorMatrix type="matrix" '
                    f'values=".36 .52 .14 0 .06  .30 .46 .12 0 .03  .22 .34 .09 0 0  0 0 0 1 0"/></filter>')
    return f'filter="url(#sp{gid})"'


def _slide(i, t, cx, cy):
    """Сценка утра Димы на стене (мир сценки — вокруг (cx, cy) низа фигуры)."""
    k = .4
    if i == 0:          # бежит с кедом в руке и бутербродом
        f = people.dima82_run(cx - 60, cy - 215, k, (t * 2.6) % 1.0, t=t, lean=.32)
        return f["svg"]
    if i == 1:          # ищет носок под вешалкой: согнулся к полу, вторая нога босая
        o = P.coat_rack(cx - 200, cy - 520, .62, coat=1, t=t, seed=3)
        hy = cy - (people.LEG_LEN - 12) * k
        f = people.dima82(cx + 30, hy, k, "puzzled82", "d82_shoe", t=t, feet="stand", socks=("shoe", "bare"), head_add=.1 * math.sin(t * 6),
                          flip=True)
        return o + f["svg"]
    # бежит с чайником в руке
    f = people.dima82_run(cx - 80, cy - 215, k, (t * 2.6) % 1.0 + .3, t=t, lean=.3, boot=False, sandwich=False, socks=("sock", "shoe"),
                          expr="panic82")
    hx, hy = f["hold"]
    return f["svg"] + P.thief_kettle(hx + 10, hy + 150, .5, 0.0, .6, t, seed=5)


def s07(t):
    a, b = span("s07")
    o = []
    # тёмная комната вечером
    g = lib.lin_grad([(0, "#1f1a2c", 1), (.6, "#2a2236", 1), (1, "#3a2c34", 1)], 0, 0, 0, 1920, units="userSpaceOnUse")
    o.append(f'<rect x="-400" y="-400" width="1900" height="2700" fill="url(#{g})"/>')
    o.append('<rect x="-400" y="1240" width="1900" height="1100" fill="#2a1f22"/>')
    for i, yy in enumerate((1300, 1390, 1520)):
        o.append(line([(-400, yy), (1500, yy)], 3, "#1a1316", taper=0, wmin=1, seed=8400 + i, op=.8))
    x0, y0, x1, y1 = S07_SCR
    # смена сценок: «такие» — 0, «истории» — 1, «Диму» — 2; кадр плёнки проезжает вверх на смене, вспышка
    sw = [ws(26), ws(27), ws(29)]
    idx = 0 if t < sw[1] else (1 if t < sw[2] else 2)
    ch = max([t - s_ for s_ in sw[1:] if t >= s_] + [9.0])
    slide_u = ease_out(clamp(ch / .16)) if ch < .16 else 1.0
    flick = .9 + .06 * math.sin(t * 47) + .04 * math.sin(t * 23 + 1)
    # свет на стене
    gl = lib.rad_grad([(0, "#fff4cf", 1), (.75, "#f6e3ae", 1), (1, "#d8bf86", 1)], (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * .62, (y1 - y0) * .62)
    o.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="10" fill="url(#{gl})" opacity="{flick:.3f}"/>')
    cid = lib.clip_rect(x0 + 6, y0 + 6, x1 - x0 - 12, y1 - y0 - 12, 8)
    cx, cy = (x0 + x1) / 2, y1 - 40
    scenes = ""
    if slide_u < 1.0 and idx > 0:        # прошлая сценка уезжает вверх, новая въезжает снизу
        dy = (y1 - y0) * slide_u
        scenes += f'<g transform="translate(0 {-dy:.1f})">{_slide(idx - 1, t, cx, cy)}</g>'
        scenes += f'<g transform="translate(0 {(y1 - y0) - dy:.1f})">{_slide(idx, t, cx, cy)}</g>'
    else:
        scenes += _slide(idx, t, cx, cy)
    o.append(f'<g clip-path="url(#{cid})" opacity="{.95 * flick:.3f}"><g {_sepia(1)}>{scenes}</g></g>')
    if ch < .2:     # вспышка смены кадра
        o.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="10" fill="#fffbe8" opacity="{.6 * (1 - ch / .2):.3f}"/>')
    # проектор, луч и пылинки
    px, py, pk = S07_PROJ
    lx, ly = P.projector_lens(px, py, pk)
    o.append(f'<polygon points="{lx:.1f},{ly - 18:.1f} {x0 + 30},{y0 + 20} {x1 - 20},{y0 + 20} {x1 - 20},{y1 - 20} {lx:.1f},{ly + 18:.1f}" '
             f'fill="#fff2c4" opacity="{.16 * flick:.3f}"/>')
    o.append(f'<polygon points="{lx:.1f},{ly - 8:.1f} {x0 + 140},{y0 + 120} {x1 - 120},{y1 - 120} {lx:.1f},{ly + 8:.1f}" fill="#fff8dc" opacity=".12"/>')
    r = P._rs(8407)
    for i in range(26):
        u = (r.uniform(0, 1) + .12 * t * (1 + i % 3) * .3) % 1.0
        qx, qy = lx + (x1 - 60 - lx) * u, ly + (r.uniform(.15, .85) * (y1 - y0) + y0 - ly) * u
        qx += 14 * math.sin(t * 1.3 + i)
        qy += 10 * math.cos(t * 1.1 + i * 2)
        o.append(f'<circle cx="{qx:.1f}" cy="{qy:.1f}" r="{r.uniform(2.2, 4.6):.1f}" fill="#fff6d6" opacity="{.35 + .4 * abs(math.sin(t * 2 + i)):.2f}"/>')
    o.append(P.stool(px + 10, py, 1.0, seed=4))
    o.append(P.film_projector(px, py, pk, t, beam_u=0.0, seed=2, crank=t * 420))
    # кот: сидит слева на полу, лапой переключает кадр (тянется к корпусу на сменах), огонёк светит в пыль
    ctx, cty, ck = S07_CAT
    tap = max([math.exp(-((t - s_ + .06) / .12) ** 2) for s_ in sw] + [0.0])
    st = dict(people.CAT_ST.get("watch82", {}), look=(.7, -.6), turn=.35, paw=.55 + .45 * tap, paw_dx=95 + 40 * tap, perk=.6 + .4 * tap,
              tail=8 * math.sin(t * 2.2), flame_e=1.4)
    gg = lib.rad_grad([(0, "#ffb050", .45), (1, "#ffb050", 0)], ctx + 130 * ck, cty - 270 * ck, 170)
    o.append(f'<circle cx="{ctx + 130 * ck:.1f}" cy="{cty - 270 * ck:.1f}" r="170" fill="url(#{gg})"/>')
    o.append(people.cat_svg(ctx, cty, ck, st, t))
    z = ease_io(clamp((t - a) / (b - a)))
    s_ = lerp(1.08, 1.16, z) * (1 + .02 * sum(kick(t, s_, 1.0, .3) for s_ in sw[1:]))
    return frame_svg("".join(o), lerp(620, 670, z), lerp(930, 860, z), s_, rot=lerp(-.6, .3, z), bg="#1f1a2c")


# ═══════════════════════════════ s15–s16: ряд людей с ленточками ═══════════════════════════════
S15_K = .56
S15_ROW = [("student", 200.0), ("elder", 560.0), ("mom", 920.0), ("courier", 1280.0), ("dima", 1660.0)]
RIB_K = .5                 # ширина ленты (time_strip k)
RIB_SHORT = 400.0          # «как помнится»
RIB_LONG = 2.0 * RIB_SHORT  # «как было» — вдвое длиннее


def street_frame(t, cam, body, bg="#bfe0ee", mood="calm"):
    st = R.street82(t, cam, mood)
    cx, cy, s_, rot = cam
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/>{st["back"]}<g transform="{lib.cam(cx, cy, s_, rot)}">{st["ground"]}{body}'
               f'{st["front"]}</g>')


def rib_hang(x, y, L, sway=0.0, seed=0):
    """Короткая ленточка висит из руки (x, y) вниз длиной L, качается на sway градусов."""
    return f'<g transform="rotate({90 + sway:.2f} {x:.1f} {y:.1f})">{P.time_strip(x, y, x + L, RIB_K, seed=seed, h=100)}</g>'


def rib_rise(x, L, sway=0.0, seed=0, curl=0.0):
    """Длинная лента встаёт с земли (y = 0) вверх на длину L (сзади человека)."""
    if L < 4:
        return ""
    return f'<g transform="rotate({-90 + sway:.2f} {x:.1f} 0)">{P.time_strip(x, 0, x + L, RIB_K, seed=seed, h=100)}</g>'


def _person15(kind, x, k, t, pose_u, look_back, expr):
    hy = -(people.LEG_LEN - 12) * k * people.HEIGHT.get(people._TOWN.get(kind, "dima"), 1.0)
    if kind == "dima":
        ex = "wow82" if look_back else "calm82"
        f = people.dima82(x, hy, k, ex, ("d82_rest", "d82_ribbon"), t=t, u=pose_u, feet="stand", head_add=-.12 * look_back)
    else:
        f = _town_mix(kind, x, hy, k, t, pose_u, expr, look_back)
    return f


def _town_mix(kind, x, hy, k, t, u, expr, look_back):
    who = people._TOWN[kind]
    pk = people.mix_pose("x82_rest", "x82_ribbon", u, x, hy, k, who)
    return people.townsman82(kind, x, hy, k, "rest", t=t, expr=expr, feet="stand", arms=pk["arms"], hands=pk["hands"],
                             head_add=-.12 * look_back)


def s15(t):
    a, b = span("s15")
    t_mem, t_short = ws(64), ws(67)
    o = []
    for i, (kind, x) in enumerate(S15_ROW):
        tr = t_mem + .09 * i                       # поднимает короткую ленточку
        u = ease_out(clamp((t - tr) / .22))
        tl = t_short + .07 * i                     # за спиной встаёт длинная
        ul = clamp((t - tl) / .32)
        lb = ease_io(clamp((t - tl - .1) / .25))   # оглядывается на неё
        if ul > 0:
            o.append(rib_rise(x - 150, RIB_LONG * lib.back_out(ul) if hasattr(lib, "back_out") else RIB_LONG * ease_out(ul),
                              sway=4 * math.sin(t * 3 + i) * (1 - ul * .5), seed=20 + i))
        f = _person15(kind, x, S15_K, t + i * .7, u, lb, "wow" if lb > .5 else "calm")
        o.append(f["svg"])
        if u > .01:
            hx, hy = f["hold"]
            o.append(rib_hang(hx, hy - 10, RIB_SHORT * u, sway=6 * math.sin(t * 2.4 + i), seed=10 + i))
    # камера: проезд вдоль ряда, на «короче» — отъезд, чтобы видеть длинные ленты
    z = ease_io(clamp((t - a) / (t_short - .1 - a)))
    zo = ease_io(clamp((t - t_short + .1) / .45))
    s_ = lerp(1.12, .88, zo) * (1 + .03 * kick(t, t_short, 1.0, .4))
    cx = lerp(lerp(260, 1150, z), 1250, zo)
    cy = lerp(-360, -520, zo)
    return street_frame(t, (cx, cy, s_, .3 * math.sin(t * .9)), "".join(o))


def s16(t):
    a, b = span("s16")
    t_shli = ws(70)
    o = []
    dx = 1660.0
    k = S15_K
    # люди расходятся от Димы в разные стороны, волоча длинные ленты шлейфами (к Диме)
    walkers = [("student", dx - 380, -1, 400.0), ("elder", dx - 700, -1, 300.0), ("mom", dx + 420, 1, 360.0), ("courier", dx + 740, 1, 420.0)]
    for i, (kind, x0, dirn, sp) in enumerate(walkers):
        x = x0 + dirn * sp * (t - a)
        who = people._TOWN[kind]
        hy = -(people.LEG_LEN - 12) * k * people.HEIGHT[who]
        f = people.townsman82_walk(kind, x, hy, k, (t - a) * 1.5 + i * .3, t=t, flip=dirn < 0, expr="calm")
        hx, hy_ = f["hold"]
        o.append(_trail(hx, hy_, hx - dirn * RIB_LONG * 1.25, i, t))
        o.append(f["svg"])
    # Дима остаётся: короткая ленточка в руке у груди, длинная лежит у ног; смотрит на одну, на другую, кивает на «шли»
    hy = -(people.LEG_LEN - 12) * k
    nod = math.sin(math.pi * clamp((t - t_shli) / .35)) if t > t_shli else 0.0
    lk = ease_io(clamp((t - a - .25) / .3))
    look = (lerp(.5, .9, lk), lerp(.6, .95, lk))
    ex = dict(people.EXPR["dima"]["sure82" if t > t_shli + .1 else "puzzled82"], look=look)
    arms = {"n": ("ik", (dx + 230 * k, hy - 330 * k), -1)}
    hands = {"n": dict(people._GRIP, dir=(.6, -.8))}
    o.append(P.time_strip(dx + 60, -10, dx + 60 + RIB_LONG, RIB_K, seed=59, h=100))
    f = people.dima82(dx, hy, k, ex, "d82_rest", t=t, feet="stand", head_add=.2 * nod + .14 * lk, arms=arms, hands=hands)
    o.append(f["svg"])
    hx, hy_ = f["hold"]
    o.append(rib_hang(hx, hy_, RIB_SHORT, sway=5 * math.sin(t * 2.2), seed=14))
    z = ease_io(clamp((t - a) / (b - a)))
    s_ = lerp(.8, .72, z)
    return street_frame(t, (dx + 60, lerp(-430, -470, z), s_, -.2 + .3 * z), "".join(o))


def _trail(hx, hy, tail_x, seed, t, flat=False):
    """Лента-шлейф: из руки (hx, hy) вниз до земли и назад по тротуару до tail_x."""
    o = ""
    gx = hx + (tail_x - hx) * .18
    if not flat:
        L = math.hypot(gx - hx, -6 - hy)
        ang = math.degrees(math.atan2(-6 - hy, gx - hx))
        o += f'<g transform="rotate({ang:.2f} {hx:.1f} {hy:.1f})">{P.time_strip(hx, hy, hx + L, RIB_K, seed=40 + seed, h=100)}</g>'
    x0, x1 = (gx, tail_x) if not flat else (hx, tail_x)
    wav = 3 * math.sin(t * 5 + seed)
    o += P.time_strip(min(x0, x1), -8 + wav, max(x0, x1), RIB_K, seed=50 + seed, h=100)
    return o


# ═══════════════════════════════ s04: подъезд выплёвывает Диму трижды, автобус уходит ═══════════════════════════════
S04_DOOR = (240.0, -70.0, .92)      # центр низа двери (на верхней ступеньке), масштаб
S04_K = .62
S04_BUS = 1430.0                     # центр автобуса на остановке
S04_STOP = 650.0                    # где Дима останавливается на третьем выбеге


def _facade04(t):
    o = []
    wall, wall_sh, ln = "#e6b98f", "#c99a72", "#b07f5a"
    o.append(f'<rect x="-900" y="-1900" width="1500" height="1900" fill="{wall}"/>')
    o.append('<rect x="600" y="-1900" width="1400" height="1900" fill="#d9c9a8"/>')       # соседний дом у остановки
    for j in range(40):
        yy = -1900 + j * 50
        o.append(line([(-900, yy), (600, yy)], 2.0, ln, taper=0, wmin=1, seed=8450 + j, op=.45))
        for i in range(16):
            xx = -900 + i * 110 + (55 if j % 2 else 0)
            o.append(line([(xx, yy), (xx, yy + 50)], 1.6, ln, taper=0, wmin=1, seed=8500 + i + j * 16, op=.35))
    o.append(blob(lib.rect_pts(560, -1900, 600, 0), wall_sh, .9))
    # окна первого этажа (пустые, без надписей)
    for wx in (-560, 760):
        o.append(shape(lib.rect_pts(wx - 120, -1000, wx + 120, -640), "#bcd8e6", blob(lib.rect_pts(wx - 120, -720, wx + 120, -640), "#9cc0d4", .8) +
                       line([(wx, -1000), (wx, -640)], 4, "#f2ece0", taper=0, wmin=1, seed=8601), w=5, seed=8600 + wx))
    dx, dy, dk = S04_DOOR
    # ступеньки
    o.append(shape(lib.rect_pts(dx - 300, -36, dx + 300, 0), "#b9b2a6", blob(lib.rect_pts(dx - 300, -10, dx + 300, 0), "#958e82", .9), w=4, seed=8610))
    o.append(shape(lib.rect_pts(dx - 260, dy, dx + 260, -36), "#cfc8bc", blob(lib.rect_pts(dx - 260, -46, dx + 260, -36), "#a8a094", .9), w=4, seed=8611))
    # козырёк и фонарь
    o.append(shape([(dx - 320, -1010), (dx + 320, -1010), (dx + 340, -960), (dx - 340, -960)], "#7d8a96", blob(lib.rect_pts(dx - 340, -975, dx + 340, -960),
                                                                                                       "#5d6874", .9), w=4.4, seed=8612))
    fl = .8 + .2 * math.sin(t * 9)
    o.append(shape(ellipse_pts(dx + 300, -900, 26, 34, 12), "#fff3c6", w=3.2, seed=8613))
    o.append(f'<circle cx="{dx + 300}" cy="-900" r="70" fill="#fff3c6" opacity="{.25 * fl:.2f}"/>')
    # тротуар
    o.append('<rect x="-900" y="0" width="2900" height="900" fill="#d6d0c4"/>')
    for i in range(30):
        o.append(line([(-900 + i * 140, 0), (-960 + i * 140, 300)], 2.4, "#b8b1a4", taper=0, wmin=1, seed=8620 + i, op=.7))
    o.append(line([(-900, 0), (2000, 0)], 4, INK, taper=0, wmin=1, seed=8650))
    o.append('<rect x="-900" y="240" width="2900" height="40" fill="#bdb6a8"/><rect x="-900" y="280" width="2900" height="700" fill="#6f727a"/>')
    # остановка: столб с пустой табличкой и навес
    sx = S04_STOP + 220
    o.append(line([(sx, 0), (sx, -760)], 12, "#5d6874", taper=0, wmin=1, seed=8660))
    o.append(shape(lib.rrect(sx - 70, -900, sx + 70, -760, 10), "#f2f0ea", blob(lib.rect_pts(sx - 70, -790, sx + 70, -760), "#d8d4ca", .9), w=4, seed=8661))
    o.append(shape(lib.rrect(sx - 40, -880, sx + 40, -840, 8), "#3f86c6", w=3, seed=8662))
    return "".join(o)


def _door04(open_u):
    """Дверь подъезда: открывается наружу (полотно сжимается к петле слева), за ней тёмный тамбур."""
    dx, dy, dk = S04_DOOR
    o = [f'<rect x="{dx - 210 * dk:.1f}" y="{dy - 936 * dk:.1f}" width="{420 * dk:.1f}" height="{936 * dk:.1f}" fill="#3a2e2a"/>']
    if open_u > .01:
        o.append(f'<rect x="{dx - 210 * dk:.1f}" y="{dy - 300 * dk:.1f}" width="{420 * dk:.1f}" height="{300 * dk:.1f}" fill="#5a4a40"/>')
    sq = 1.0 - .82 * clamp(open_u)
    hx = dx - 236 * dk
    o.append(f'<g transform="translate({hx:.1f} 0) scale({sq:.4f} 1) translate({-hx:.1f} 0)">{P.door(dx, dy, dk, seed=4, col="#5e7d6a")}</g>')
    return "".join(o)


def s04(t):
    a, b = span("s04")
    exits = [ws(10), ws(11), ws(12) - .1]          # «каждое», «утро», третий — перед «и не понимает»
    t_bus, t_shrug = ws(13), ws(14)
    gear = [dict(brush=True), dict(inside_out=True), dict(towel=True)]
    o = [_facade04(t)]
    # текущий выбег (рез-повтор: на каждом слове всё начинается заново — дверь хлопает, Дима вылетает)
    idx = max([i for i, te in enumerate(exits) if t >= te - .06] + [-1])
    te = exits[idx] if idx >= 0 else exits[0] - .5
    u = (t - te) / .3
    open_u = 0.0
    if idx >= 0:
        open_u = ease_out(clamp(u / .25)) * (1 - ease_in(clamp((u - 1.4) / .8)) * .9)
    elif t > exits[0] - .2:
        open_u = .1 * abs(math.sin((t - a) * 40))          # дверь дрожит перед первым хлопком
    o.append(_door04(open_u))
    # кот на нижней ступеньке слева: провожает взглядом
    dx, dy, dk = S04_DOOR
    hip0 = -(people.LEG_LEN - 12) * S04_K
    if idx < 0:
        x = dx - 40
        fig = None
    else:
        last = idx == 2
        run_u = clamp(u / 1.0)
        x = lerp(dx + 10, dx + 330, ease_out(run_u)) if not last else lerp(dx + 10, S04_STOP, ease_out(clamp((t - te) / max(.2, t_shrug - te))))
        hop = 60 * math.sin(math.pi * clamp(u / .9)) * (1 - clamp(u - .9))
        if last and t >= t_shrug - .05:
            e = ease_out(clamp((t - t_shrug + .05) / .2))
            fig = people.dima82(x, hip0, S04_K, "panic82", ("d82_rest", "d82_shrug"), t=t, u=e, feet="stand", towel=True)
        else:
            fig = people.dima82_run(x, hip0 - hop - 70 * (1 - clamp(u / .35)), S04_K, (t - te) * 3.2 + idx * .37, t=t, expr="panic82",
                                    boot=False, sandwich=False, socks=None, lean=.34, inside_out=bool(gear[idx].get("inside_out")))
    look_x = 1.0 if fig is None else clamp((x - (dx - 330)) / 400, -1, 1)
    cst = dict(look=(look_x, .1), turn=.4 * look_x, tail=10 * math.sin(t * 2.5), flame_e=1.2, perk=.5 + .5 * (idx >= 0 and u < 1.2))
    o.append(people.cat_svg(dx - 215, -36, .72, cst, t))
    if fig is not None:
        o.append(fig["svg"])
        # предметы выбега поверх фигуры
        if idx == 0 or idx == 2:
            hx, hy = fig["head"]
            sc = fig["scale"]
            if idx == 0:
                mx, my = hx + 64 * sc, hy + 92 * sc
                o.append(people.toothbrush82(mx + 10 * sc, my, sc * 1.05, rot=-6, t=t))
            else:
                o.append(people.towel82(hx - 20 * sc, hy + 160 * sc, sc))
    # автобус на ближней полосе у остановки: стоит, на «не» трогается и уезжает вправо, открывая Диму (облачко выхлопа)
    bu = max(0.0, t - t_bus)
    bx = S04_BUS + 900 * bu * bu + 80 * bu
    o.append(P.bus(bx, 330, 1.9, u=bx * 3, seed=2, puff=clamp(bu / .3)))
    # камера: точка у подъезда с микродрейфом, толчки на хлопках, на «понимает» — доворот к остановке
    s_ = .9 * (1 + sum(.035 * kick(t, e_, 1.0, .3) for e_ in exits))
    sx, sy_ = 0.0, 0.0
    for e_ in exits:
        q = shake(t, e_, 10, .22, int(e_ * 10))
        sx, sy_ = sx + q[0], sy_ + q[1]
    pan = ease_io(clamp((t - t_bus + .1) / .45))
    cx = lerp(470, 600, pan) + 6 * math.sin(t * 1.3) + sx
    cy = -330 + 4 * math.cos(t * 1.1) + sy_
    return frame_svg("".join(o), cx, cy, s_, rot=.3 * math.sin(t * .9), bg="#e6b98f")


def frame(sid, t):
    lib.dyn_begin()
    return globals()[sid](t)
