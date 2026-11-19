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
    t_look, t_bite, t_tap1, t_tap2 = ws(31), ws(32), ws(33), ws(34)
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


def frame(sid, t):
    lib.dyn_begin()
    return globals()[sid](t)
