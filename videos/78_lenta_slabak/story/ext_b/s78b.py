"""Рилс 78 «Лента, ты слабак», группа B: Дима ночью, кот, изобретатель. Время — только из shots.json и voice/words.json (слово по индексу wN).
s04: ночь, кровать сверху; «каждую» (w12) швыряет телефон на одеяло экраном вниз и натягивает одеяло на голову, «ночь» (w13) плюхается,
     «палец» (w15) рука сама выползает и пальцы шагают к телефону, «листал» (w18) палец переворачивает телефон, лицо поворачивается к экрану.
s05: ночь, средний план, кот запрыгивает в свет экрана; «Напиши» (w19) стук лапой по стеклу к зрителю, рукописное «кот» (w20),
     «узнаешь» (w22) прищур, «три» (w23) огонёк трижды вспыхивает.
s08: (хлёст) поводок отдёргивает руку «напишешь» (w32), кукловод «решила» (w36), кивок «за тебя» (w37–w38).
s09: кот отдёргивает экран-шторку «смотри» (w41), «кто» (w42) заглядывает, «самом деле» (w44–w45) «вот он».
s12: мастерская, «Человек» (w58) поднимает ленту, «придумал» (w60) хлопает по рулону, «бесконечную» (w61) лента бежит.
s13: лента опутала дома, «ленту» (w62) смотрит в окно, «признался» (w65) к нам, «жалеет» (w67) за голову, «ней» (w69) тянет ленту.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import people  # noqa: E402
import props as P  # noqa: E402
import room as R  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, svg  # noqa: E402

INK = lib.INK
W = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = {s["id"]: s for s in json.load(open(os.path.join(STORY, "shots.json")))["shots"]}


def ws(i):
    return W[i]["start"]


def we(i):
    return W[i]["end"]


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (lerp(a[0], b[0], u), lerp(a[1], b[1], u))


def frame_svg(body, cx, cy, s, rot, bg="#05070f", over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def whip_in(t, t0, dur=.2):
    """Хлёст на входе: 1 → 0 с ease_out (смещение и размытие камеры)."""
    return 1 - ease_out(clamp((t - t0) / dur), 3)


CARD_COLS = ["#e8645a", "#f2c14e", "#5fb3a8", "#7a8ee0", "#e88ab8", "#8fcf6a"]


def phone_top(x, y, k=1.0, rot=0.0, face_down=True, glow=0.0, scroll=0.0, flip=1.0, seed=0):
    """Телефон сверху (без перспективы): корпус 150×300 (·k). face_down — спинка с камерой; иначе экран: цветные плашки ленты без букв,
    бегут вниз (scroll — смещение ленты в px экрана), glow — яркость. flip — ширина при перевороте (cos), только предмет."""
    sd = 78900 + seed
    o = [shape(lib.rrect(-75, -150, 75, 150, 24), "#23262d", "", w=4.2, seed=sd)]
    if face_down:
        inner = blob(lib.rrect(-62, -136, 62, 136, 16), "#3a3f49")
        inner += shape(lib.rrect(-54, -132, -8, -88, 12), "#2b2e35", blob(ellipse_pts(-31, -110, 12, 12, 10), "#14161b"), w=2.4, seed=sd + 1)
        inner += line([(40, -120), (46, 110)], 4, "#5a616e", taper=.5, wmin=.3, seed=sd + 2)
        o.append(shape(lib.rrect(-75, -150, 75, 150, 24), "#2b2e35", inner, w=4.2, seed=sd + 3))
    else:
        g = clamp(glow)
        cid = lib.clip_rect(-64, -138, 128, 276, 14)
        scr = [f'<rect x="-64" y="-138" width="128" height="276" fill="{lib.mix("#10131c", "#2a3a66", g)}"/>']
        off = scroll % 76
        for i in range(-1, 5):
            yy = -138 - 76 + off + i * 76
            c = CARD_COLS[(i - int(scroll // 76)) % len(CARD_COLS)]
            scr.append(f'<rect x="-54" y="{yy + 8:.1f}" width="108" height="60" rx="10" fill="{lib.mix("#1a1f2c", c, .25 + .75 * g)}"/>')
        o.append(f'<g clip-path="url(#{cid})">{"".join(scr)}</g>')
    body = "".join(o)
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k * flip:.4f} {k:.4f})">{body}</g>'


def screen_pool(x, y, rx, ry, u, t, col="#bfe0ff"):
    """Холодное пятно света экрана с чётким краем (не огромный овал): эллипс + ядро."""
    if u <= .01:
        return ""
    fl = 1 + .03 * math.sin(t * 9.1)
    return blob(ellipse_pts(x, y, rx, ry, 22), col, .16 * u * fl) + blob(ellipse_pts(x, y, rx * .55, ry * .55, 18), "#e6f4ff", .14 * u * fl)


def quilt_top(top_y, t, PAL, bump=0.0, x0=70.0, x1=1000.0, y1=2100.0, seed=7801):
    """Одеяло сверху: прямоугольник по кровати с волнистым краем у головы (край ходит с дыханием), складки, подвёрнутая кромка."""
    n = 10
    top = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        top.append((x, top_y + 10 * math.sin(i * 1.7) + 4 * math.sin(t * 1.3 + i) - bump * 22 * math.sin(math.pi * i / n)))
    pts = [(x0 + 6, y1, 1), (x0, top_y + 30)] + top[1:-1] + [(x1, top_y + 30), (x1 - 6, y1, 1)]
    inner = blob([(x0, top_y + 60), (x0 + 120, top_y + 60), (x0 + 110, y1), (x0, y1)], PAL["quilt_sh"], .6)
    inner += blob([(x1 - 120, top_y + 60), (x1, top_y + 60), (x1, y1), (x1 - 110, y1)], PAL["quilt_sh"], .6)
    for i in range(5):
        fx = x0 + 160 + i * (x1 - x0 - 320) / 4
        inner += line([(fx, top_y + 70), (fx + 26 * math.sin(i + t * .7), top_y + 600), (fx - 20, y1)], 4, PAL["quilt_sh"], taper=.4, wmin=.3, seed=seed + i, op=.8)
    inner += blob([(p[0], p[1] + 4) for p in top] + [(x1, top_y + 50), (x0, top_y + 50)], PAL["quilt_hi"], .9)
    inner += line([(x0 + 10, top_y + 52), (x1 - 10, top_y + 50)], 3, PAL["quilt_sh"], taper=.2, wmin=.5, seed=seed + 9, op=.9)
    return shape(pts, PAL["quilt"], inner, w=4.6, seed=seed + 20)


# ═══════════════════════════════ s04: кровать сверху, пальцы шагают к телефону ═══════════════════════════════
def s04(t):
    lib.dyn_begin()
    T_EACH, T_NIGHT, T_FING, T_SCROLL = ws(12), ws(13), ws(15), ws(18)
    t_thr0, t_rel, t_land = T_EACH - .1, T_EACH + .08, T_EACH + .3
    t_cov0, t_cov1 = t_land + .02, T_NIGHT - .02
    t_out = T_FING - .32                      # рука выползает
    t_flip = T_SCROLL                         # переворот телефона
    t_rev0, t_rev1 = T_SCROLL + .06, T_SCROLL + .46
    nt = R.night78(t, "top", glow=1.0)
    PAL = nt["P"]
    k = .8
    hip = (450.0, 760.0)
    head_tgt = (505.0, 300.0)
    o = [nt["bg"]]
    # ── фаза Димы ──
    thr = ease_out(clamp((t - t_thr0) / (t_rel - t_thr0 + .06)), 2)
    cov = ease_io(clamp((t - t_cov0) / (t_cov1 - t_cov0)))
    rev = ease_io(clamp((t - t_rev0) / (t_rev1 - t_rev0)))
    # край одеяла: грудь → над головой → (переворот) сползает до плеч
    top_chest, top_head, top_rev = 520.0, 140.0, 470.0
    top_y = lerp(top_chest, top_head, cov) if t < t_rev0 else lerp(top_head, top_rev, rev)
    bump = math.exp(-7 * max(0.0, t - T_NIGHT)) * math.sin(2 * math.pi * 3.2 * max(0.0, t - T_NIGHT)) if t > T_NIGHT else 0.0
    # телефон: в руке → полёт → на одеяле экраном вниз → переворот
    land = (830.0, 1050.0)
    sc = k * people.HEIGHT["dima"]
    if t >= t_rev0 - .2:
        ex = dict(people.EXPR["dima"]["turn78"])
        ex["look"] = (.75, .7)
    else:
        ex = {"brows": "pinch", "mouth": "frown", "lid": .42, "look": (.5, -.3), "bags": True, "hair": 6}
    # руки до укрытия: ближняя держит телефон над лицом → бросок вниз-вправо; потом обе тянут одеяло
    if t < t_cov0:
        hold = (hip[0] + 190 * sc, hip[1] - 640 * sc)
        throw = (hip[0] + 470 * sc, hip[1] - 260 * sc)
        n_t = lerp2(hold, throw, thr)
        f_t = (hip[0] + 120 * sc, hip[1] - 300 * sc)
        arms = {"n": ("ik", n_t, -1), "f": ("ik", f_t, -1)}
        hands = {"n": {"dir": (lerp(.3, 1, thr), lerp(-1, .5, thr)), "curl": (.55, .6, .65, .7) if t < t_rel else (.15, .1, .15, .2),
                       "spread": .1 if t < t_rel else .35, "thumb": .55 if t < t_rel else .1},
                 "f": {"dir": (1, -.2), "curl": (.65, .7, .72, .75), "thumb": .6}}
    else:
        ey = top_y + 18
        arms = {"n": ("ik", (hip[0] + 260 * sc, ey + 30 * sc), -1), "f": ("ik", (hip[0] + 40 * sc, ey + 10 * sc), -1)}
        hands = {"n": {"dir": (.2, -1), "curl": (.7, .72, .75, .78), "thumb": .6}, "f": {"dir": (.1, -1), "curl": (.7, .72, .75, .78), "thumb": .6}}
    shake = 6 * math.sin(t * 38) * (1 - thr) if t < t_rel + .1 else 0.0
    fig = people.dima(hip[0] + shake, hip[1], k, ex, arms=arms, hands=hands, lean_add=0.0, head_add=-.05 + .12 * rev,
                      layers=("pelvis", "body"))
    armsvg = people.dima(hip[0] + shake, hip[1], k, ex, arms=arms, hands=hands, head_add=-.05 + .12 * rev, layers=("arm_f", "arm_n"))
    hd = fig["head"]
    # голова и плечи: под одеялом, когда оно накрыто (рисуем всё равно — одеяло поверх)
    o.append(fig["svg"])
    # одеяло (поверх тела) + бугор тела под ним
    quilt = quilt_top(top_y, t, PAL, bump)
    hx_ = hip[0] - 20 * cov
    hump = blob(ellipse_pts(hx_ + 10, 1000, 230, 330, 24), PAL["quilt_hi"], .35)            # туловище
    hump += blob(ellipse_pts(hx_ - 50, 1500, 105, 300, 20), PAL["quilt_hi"], .35) + blob(ellipse_pts(hx_ + 90, 1520, 100, 300, 20), PAL["quilt_hi"], .3)
    hump += blob(ellipse_pts(hx_ + 200, 1150, 50, 520, 20), PAL["quilt_sh"], .55)
    hump += line([(hx_ + 20, 1230), (hx_ + 20, 1800)], 5, PAL["quilt_sh"], taper=.5, wmin=.3, seed=7811, op=.8)     # между ногами
    for j, fx in enumerate((hx_ - 60, hx_ + 100)):                                                              # стопы
        hump += blob(ellipse_pts(fx, 1840, 70, 50, 14), PAL["quilt_hi"], .45)
    hump += line([(hip[0] - 200, top_y + 170), (hip[0] - 230, 1150), (hip[0] - 180, 1800)], 5, PAL["quilt_sh"], taper=.5, wmin=.3, seed=7810)
    o.append(quilt)
    o.append(f'<g opacity="{1 - .4 * cov * (1 - rev):.3f}">{hump}</g>')
    if cov > .85 and rev < .5:      # хохолок волос торчит из-под одеяла
        hh = hd[1] - 120 * sc
        for j, dx in enumerate((-40, -10, 22, 48)):
            o.append(shape([(hd[0] + dx - 12, top_y + 6, 1), (hd[0] + dx + 4 * math.sin(t * 3 + j), top_y - 38 - 10 * (j % 2)), (hd[0] + dx + 14, top_y + 6, 1)],
                           "#5a3826", "", w=3.2, seed=7820 + j))
        del hh
    if t < t_cov1 + .05:            # руки поверх одеяла (видна только часть над краем)
        cid = lib.clip_rect(-200, -200, 1500, top_y + 230)
        o.append(f'<g clip-path="url(#{cid})">{armsvg["svg"]}</g>')
    # телефон
    flip_u = clamp((t - t_flip) / .2)
    if t < t_rel:
        ph = people.hand_pos(armsvg, "n", 70)
        o.append(phone_top(ph[0], ph[1], .7, lerp(-20, 30, thr), True))
        ph_c = ph
    elif t < t_land:
        u = (t - t_rel) / (t_land - t_rel)
        p0 = (hip[0] + 470 * sc + 60, hip[1] - 260 * sc)
        pp = (lerp(p0[0], land[0], u), lerp(p0[1], land[1], u) - 140 * 4 * u * (1 - u))
        o.append(phone_top(pp[0], pp[1], .7 * (1 + .25 * math.sin(math.pi * u)), 30 + 260 * u, True))
        ph_c = pp
    else:
        sq = P.squash(t, t_land, .2, 3.5, 8)
        hopy = P.hop(t, T_NIGHT + .02, 26, .26)
        o.append(blob(lib.T(lib.rrect(-75, -150, 75, 150, 24), land[0] + 10, land[1] + 14, .7, 290), "#000000", .3))
        fu = abs(math.cos(math.pi * flip_u))
        face_up = flip_u >= .5
        gl = ease_out(clamp((t - t_flip - .1) / .3)) if face_up else 0.0
        o.append(phone_top(land[0], land[1] + hopy, .7 * sq[1], 290, not face_up, gl, scroll=(t - t_flip) * 260, flip=max(.06, fu)))
        ph_c = land
    # рука выползает и пальцы шагают к телефону (из-под одеяла справа от тела)
    if t >= t_out:
        base = (hip[0] + 70, 690.0)
        aim = (land[0] - 40, land[1] - 40)
        d = np.array(aim) - np.array(base)
        dl = float(np.linalg.norm(d))
        d = d / dl
        emer = ease_out(clamp((t - t_out) / .3), 2)
        walk = clamp((t - T_FING) / (t_flip - .12 - T_FING))
        reach = lerp(130, 230, emer) + (dl - 70 - 230) * walk
        if t > t_flip - .12:          # подцепляет край и переворачивает
            reach = dl - 70 + 26 * math.sin(math.pi * clamp((t - t_flip + .12) / .3))
        tip = (base[0] + d[0] * reach, base[1] + d[1] * reach)
        phase = (reach - 130) / 80.0
        o.append(blob(ellipse_pts(base[0], base[1], 62, 34, 14), "#0b1024", .55))      # щель под одеялом
        o.append(people.finger_walker78(base, tip, .95, phase, t, lift=1.0 if t < t_flip - .12 else .3))
        o.append(shape([(base[0] - 80, base[1] - 4), (base[0] - 40, base[1] - 34), (base[0] + 40, base[1] - 38), (base[0] + 80, base[1] - 8),
                        (base[0] + 40, base[1] - 14), (base[0] - 40, base[1] - 12)], PAL["quilt"],
                       line([(base[0] - 60, base[1] - 20), (base[0] + 60, base[1] - 24)], 3, PAL["quilt_hi"], seed=7830, op=.8), w=4.0, seed=7831))
    # свет: экран в руке → темно, телефон экраном вниз → вспышка экрана после переворота
    glow_now = (1 - ease_in(clamp((t - t_rel) / .2))) * .9 + (ease_out(clamp((t - t_flip - .1) / .25)) if t > t_flip + .1 else 0.0)
    o.append(f'<rect x="-900" y="-900" width="2880" height="3720" fill="#03050c" opacity="{.42 - .2 * clamp(glow_now):.3f}"/>')
    if t < t_rel + .1:
        o.append(R.screen_light74(hd[0] + 30, hd[1] + 50, 120, 120, (1 - thr) * .9, t))
    if t > t_flip + .1:
        gl = ease_out(clamp((t - t_flip - .1) / .25))
        flash = .6 * math.exp(-8 * max(0.0, t - t_flip - .1))
        o.append(screen_pool(land[0], land[1], 170, 230, gl * (1 + flash), t))
        if rev > .2:
            o.append(R.screen_light74(hd[0] + 50, hd[1] + 40, 170, 200, rev, t, rot=20))
    # камера: медленный наезд сверху за шагающими пальцами; «ночь» — толчок; вспышка — лёгкий толчок
    push = ease_io(clamp((t - SH["s04"]["t0"]) / (SH["s04"]["t1"] - SH["s04"]["t0"])))
    s = 1.22 + .12 * push + .025 * math.sin(math.pi * clamp((t - t_flip - .1) / .25))
    cx = lerp(560, 640, push)
    cy = lerp(740, 860, ease_io(clamp((t - T_FING + .3) / (t_flip - T_FING + .3)))) - 14 * bump
    rot = .6 * math.sin(t * .8) - 1.0 * (1 - push)
    return frame_svg("".join(o), cx, cy, s, rot, bg="#080b18")


# ═══════════════════════════════ s05: кот в свете экрана, «кот» от руки ═══════════════════════════════
import cat as CAT  # noqa: E402
import hand_kot  # noqa: E402

KOT05 = (640.0, 620.0, 1.45)          # чистая тёмная стена над котом (окно — левее x=540): за буквами ни одного предмета


def bump(t, t0, dur):
    u = (t - t0) / dur
    return math.sin(math.pi * u) if 0 < u < 1 else 0.0


def touch_rings(x, y, t, t0, k=1.0, col="#cfe2ff"):
    """Кольца касания по «стеклу» (к зрителю): два кольца расходятся и тают за 0.4 с."""
    o = ""
    for j in range(2):
        u = (t - t0 - .07 * j) / .4
        if 0 < u < 1:
            r = (30 + 120 * ease_out(u, 2)) * k
            o += line(ellipse_pts(x, y, r, r * .92, 26) + [ellipse_pts(x, y, r, r * .92, 26)[0]], 6 * (1 - u) * k + 1, col, taper=0, wmin=1,
                      seed=7850 + j, op=.9 * (1 - u))
    return o


def night_bed_dima(t, nt, hip, k, expr, roll=.6, phone_glow=1.0, scroll=True):
    """Дима лежит на боку лицом к нам, ближняя рука держит телефон у лица (экран к нему — нам видна спинка)."""
    fig = people.dima_bed(hip[0], hip[1], k, expr, roll=roll, t=t, cover=.25, arm="out", col="blue", seed=5)
    wr = fig["wrist"]["n"]
    ph = (wr[0] + 40 * k, wr[1] - 120 * k)
    phone = phone_top(ph[0], ph[1], .62 * k, -14 + 3 * math.sin(t * 1.7), True, seed=4)
    th = ""
    if scroll:      # большой палец ходит по экрану
        th = shape(lib.T(lib.rrect(-10, -28, 10, 18, 9), ph[0] - 20 * k, ph[1] - 30 * k - 14 * k * math.sin(t * 9), k * 1.5, -25), "#ecc4a2", "",
                   w=3.2, seed=953)
    return fig, phone + th, ph


def s05(t):
    lib.dyn_begin()
    T_NAP, T_KOT, T_UZ, T_TRI = ws(19), ws(20), ws(22), ws(23)
    kot_t0, kot_dur = T_NAP + .3, we(20) - (T_NAP + .3)
    nt = R.night78(t, "mid", glow=1.0)
    PAL = nt["P"]
    an = nt["anchors"]
    o = [nt["bg"]]
    hip = (700.0, an["bed_top"] + 10)
    ex = dict(people.EXPR["dima"]["lit78"])
    ex["look"] = (.5, -.3)
    fig, phone, ph = night_bed_dima(t, nt, hip, .62, ex)
    o.append(fig["svg"])
    o.append(nt["front"])
    o.append(phone)
    # кот: прыжок на кровать в свет (с кадра 0 уже в воздухе), садится, поворачивается к зрителю
    t_j0 = SH["s05"]["t0"] - .2
    cpos = (815.0, an["bed_top"] + 28)
    ck = .88
    ju = clamp((t - t_j0) / .42 * .55 + .45)
    tu = ease_io(clamp((t - (t_j0 + .42)) / .25))
    tap_u = max(bump(t, T_NAP + .02, .26), bump(t, T_NAP + .24, .24))
    reach = ease_out(clamp((t - (T_NAP - .1)) / .14), 2) * (1 - ease_io(clamp((t - (T_NAP + .55)) / .2)))
    smug = ease_io(clamp((t - (T_UZ - .05)) / .2))
    raise3 = ease_out(clamp((t - (T_TRI - .1)) / .14), 2)
    flashes = [T_TRI - .04 + .085 * j for j in range(3)]
    fl = max([bump(t, tf, .07) for tf in flashes] + [0.0])
    st = dict(turn=lerp(-.5, 0.0, tu), look=(lerp(-.7, 0.0, tu), lerp(-.2, 0.0, tu)), tilt=3 * math.sin(t * 1.4) - 5 * smug,
              tail=-10 + 7 * math.sin(t * 2.4), ear=4 * math.sin(t * 2.9), perk=.6 * reach,
              paw=max(.85 * reach + .15 * tap_u, .7 * raise3), paw_dx=26 if reach > raise3 else 60, smug=.85 * smug, smile=1.0 if tu > .6 and smug < .3 else 0.0,
              flame_e=1.0 + 2.2 * fl + .3 * raise3, blink=1.0 if abs(t - (T_KOT + .55)) < .05 else 0.0)
    if ju < 1:
        cat_svg = people.cat_jump((cpos[0] + 260, cpos[1] + 420), cpos, ck, ju, t, dict(st, turn=-.5, look=(-.7, -.2)))
    else:
        cat_svg = CAT.draw(cpos[0], cpos[1] - 14 * ck * tap_u, ck, st, t)
    # свет экрана на стене за котом и на одеяле (кот — силуэт на светлом)
    o.append(screen_pool(cpos[0] - 90, cpos[1] - 150, 230, 210, .55, t))
    o.append(blob(ellipse_pts(cpos[0] + 20, cpos[1] + 4, 170 * ck, 18, 16), "#000000", .3 * clamp(ju * 2 - 1)))
    o.append(nt["dark"])
    o.append(R.screen_light74(fig["head"][0] + 40, fig["head"][1] + 20, 150, 150, 1.0, t, rot=10))
    o.append(screen_pool(ph[0] + 10, ph[1] - 30, 110, 90, .6, t))
    o.append(cat_svg)
    # огонёк трижды вспыхивает: ореол
    if fl > .01 and ju >= 1:
        fx = cpos[0] + (CAT.FLAME_BASE[0] - CAT.CX) * ck
        fy = cpos[1] + (CAT.FLAME_BASE[1] - CAT.CBOT) * ck - 40 * ck
        o.append(P.glow(fx, fy, 150, 1.2 * fl, "#ffc060"))
    # стук лапой по стеклу к зрителю: кольца у подушечки
    if ju >= 1:
        tip = people.cat_paw_tip(cpos[0], cpos[1] - 14 * ck * tap_u, ck, st)
        o.append(touch_rings(tip[0], tip[1] - 10, t, T_NAP + .1, 1.0))
        o.append(touch_rings(tip[0], tip[1] - 10, t, T_NAP + .33, .85))
    # рукописное «кот» светлыми чернилами на чистой стене
    o.append(hand_kot.kot(t, kot_t0, kot_dur, KOT05[0], KOT05[1], KOT05[2], col="#eef2ff"))
    # камера: мягкий наезд на кота; «Напиши» — толчок к зрителю; дописано — мини-удар
    u = ease_io(clamp((t - t_j0) / (SH["s05"]["t1"] - t_j0)))
    s = lerp(1.36, 1.46, u) + .045 * bump(t, T_NAP, .3) + .015 * bump(t, kot_t0 + kot_dur, .3)
    cx = lerp(620, 660, u) + 3 * math.sin(t * 1.3)
    cy = lerp(840, 830, u) + 3 * math.sin(t * 1.6)
    return frame_svg("".join(o), cx, cy, s, lerp(.6, -.3, u), bg="#080b18")


# ═══════════════════════════════ s08: поводок и телефон-кукловод ═══════════════════════════════
def whip_wrap(g, t, t0, dx=-620.0, dur=.22):
    """Хлёст на входе плана: кадр въезжает сбоку с горизонтальным размытием (только пока летит)."""
    u = clamp((t - (t0 - .08)) / dur)
    if u >= 1:
        return g
    e = ease_out(u, 3)
    off = dx * (1 - e)
    bl = 60 * (1 - e)
    fid = lib.uid("wh")
    lib.DEFS.append(f'<filter id="{fid}" x="-30%" y="-5%" width="160%" height="110%"><feGaussianBlur stdDeviation="{bl:.1f} 0"/></filter>')
    return f'<g transform="translate({off:.1f} 0)" filter="url(#{fid})">{g}</g>'


def s08(t):
    lib.dyn_begin()
    t0 = SH["s08"]["t0"]
    T_NE, T_NAP, T_RESH, T_ZA, T_TEB = ws(31), ws(32), ws(36), ws(37), ws(38)
    nt = R.night78(t, "mid", glow=1.0)
    an = nt["anchors"]
    o = [nt["bg"]]
    k = .82
    sc = k * people.HEIGHT["dima"]
    hip = (470.0, an["bed_top"] + 40)
    stand = (1010.0, an["nstand"][1] + 8)
    face_hold = (hip[0] + 290 * sc, hip[1] - 470 * sc)
    # хореография: тянется положить на тумбочку → «напишешь» резинка отдёргивает руку к лицу → дальше держит у лица
    reach_u = ease_io(clamp((t - (t0 - .25)) / (T_NAP - (t0 - .25))))
    snap = ease_out(clamp((t - T_NAP - .04) / .16), 3)
    near = lerp2(lerp2(face_hold, (stand[0] - 70, stand[1] - 40), reach_u), face_hold, snap)
    if snap > 0:
        near = (near[0] + 26 * math.exp(-9 * (t - T_NAP - .2)) * math.sin(32 * (t - T_NAP)) * (t > T_NAP + .2), near[1])
    pull = ease_io(clamp((t - T_RESH) / .25))
    nods = [T_ZA - .02, T_TEB + .02]
    nod = max([bump(t, tn, .28) for tn in nods] + [0.0])
    jerk = 12 * pull * math.sin(t * 7)
    far = (hip[0] + 230 * sc, hip[1] - 400 * sc + jerk * .5 - 30 * pull)
    near = (near[0], near[1] - 40 * pull + jerk)
    ex = dict(people.EXPR["dima"]["lit78"] if snap < .5 else people.EXPR["dima"]["nod78" if pull > .3 else "cower78"])
    if snap < .5:
        ex.update(look=(.8, .35), brows="worry")
    lean = .22 * reach_u * (1 - snap)
    arms = {"n": ("ik", near, -1), "f": ("ik", far, -1)}
    hands = {"n": {"dir": (.4, -1), "curl": (.62, .66, .7, .74), "thumb": .55}, "f": {"dir": (.85, -.4), "curl": (.6, .62, .66, .7), "thumb": .5}}
    body = people.dima(hip[0], hip[1], k, ex, arms=arms, hands=hands, lean_add=lean + .05 * nod, head_add=.35 * nod - .05 * pull,
                       layers=("pelvis", "arm_f", "body"))
    arm = people.dima(hip[0], hip[1], k, ex, arms=arms, hands=hands, lean_add=lean + .05 * nod, head_add=.35 * nod - .05 * pull, layers=("arm_n",))
    o.append(body["svg"])
    o.append(nt["front"])
    # телефон в ближней руке (спинка к нам), большой палец сам скользит при «решила»
    ph = people.hand_pos(arm, "n", 64)
    o.append(phone_top(ph[0], ph[1], .55, -10 + 20 * (1 - snap) * reach_u, True, seed=8))
    o.append(arm["svg"])
    if pull > .05:
        tb = (ph[0] - 24, ph[1] - 40 - 40 * (.5 + .5 * math.sin(t * 11)) * pull)
        o.append(shape(lib.T(lib.rrect(-11, -30, 11, 20, 10), tb[0], tb[1], 1.0, -20), "#ecc4a2", "", w=3.2, seed=8081))
    # поводок: от телефона к запястью (натянут, когда тянется; щёлк на «напишешь»)
    wr = arm["wrist"]["n"]
    tens = .35 + .65 * reach_u * (1 - snap) + .3 * snap * math.exp(-6 * max(0.0, t - T_NAP))
    o.append(P.rubber_leash((ph[0] + 30, ph[1] + 70), (wr[0] - 10, wr[1] + 10), clamp(tens), t, .7, seed=3))
    if 0 < t - T_NAP < .25:          # штрихи щелчка
        u = (t - T_NAP) / .25
        for j in range(3):
            a = math.radians(-40 + 40 * j)
            c = (ph[0] + 40, ph[1] + 40)
            o.append(line([(c[0] + math.cos(a) * 70, c[1] + math.sin(a) * 70), (c[0] + math.cos(a) * (70 + 60 * (1 - u)), c[1] + math.sin(a) * (70 + 60 * (1 - u)))],
                          6 * (1 - u) + 1, "#e8eefc", taper=.5, wmin=.2, seed=8090 + j))
    # тёмный телефон-кукловод над кроватью, нити к запястьям и макушке
    hd = body["head"]
    ends = [(far[0] - 10, far[1] - 30), (hd[0] + 10, hd[1] - 120 * sc), (wr[0], wr[1] - 20)]
    up_ = ease_io(clamp((t - (T_RESH - .55)) / .65))
    pup_y = lerp(-330, -300, pull)
    o.append(f'<g opacity="{.55 + .4 * up_:.2f}">{P.phone_puppeteer(hip[0] + 150, pup_y, 1.45, t, pull, ends=ends)}</g>')
    o.append(nt["dark"])
    o.append(R.screen_light74(hd[0] + 50, hd[1] + 30, 170, 170, 1.0, t, rot=10))
    o.append(screen_pool(ph[0] - 40, ph[1] - 60, 160, 130, .6, t))
    # камера: тесно на Диме → «решила» уверенный отъезд вверх к кукловоду → «тебя» мини-рывок вниз
    up = ease_io(clamp((t - (T_RESH - .55)) / .65))
    s = lerp(1.25, .84, up) + .03 * bump(t, T_NAP, .25)
    cx = lerp(600, 610, up)
    cy = lerp(880, 470, up) + 26 * bump(t, T_TEB, .25)
    g = f'<g transform="{lib.cam(cx, cy, s, .4 * math.sin(t * .9))}">{"".join(o)}</g>'
    return svg('<rect width="1080" height="1920" fill="#080b18"/>' + whip_wrap(g, t, t0))


# ═══════════════════════════════ s09: кот отдёргивает экран, как шторку ═══════════════════════════════
def s09(t):
    lib.dyn_begin()
    t0 = SH["s09"]["t0"]
    T_TEP, T_SM, T_KTO, T_SAM = ws(40), ws(41), ws(42), ws(44)
    nt = R.night78(t, "mid", glow=1.0)
    an = nt["anchors"]
    o = [nt["bg"]]
    # телефон стоит, прислонён к подушке, экраном к нам; кот сидит справа на одеяле
    phc = (470.0, an["bed_top"] - 150)
    pk = .72
    open_u = ease_io(clamp((t - (T_SM + .04)) / .45))
    o.append(nt["front"])
    o.append(blob(ellipse_pts(phc[0] + 10, phc[1] + 222 * pk, 150 * pk, 22, 14), "#000000", .4))
    o.append(P.phone_curtain(phc[0], phc[1], pk, open_u, t, side=-1))
    ck = 1.0
    cpos = (phc[0] + 255, an["bed_top"] + 70)
    # лапа (левая от зрителя — та же передняя) идёт к левому краю экрана и тащит его вправо
    edge = P.curtain_edge(phc[0], phc[1], pk, min(open_u, .42), -1)
    hook = clamp((t - (T_SM - .3)) / .3)
    rel = ease_io(clamp((t - (T_SM + .22)) / .25))           # отпустил — шторка доезжает сама, лапа на опоре
    point = ease_out(clamp((t - (T_SAM - .1)) / .25), 2)    # «вот он» — лапа к тёмной дыре
    tgt0 = (cpos[0] - 120, cpos[1] - 120)
    tgt = lerp2(tgt0, (edge[0] + 10, edge[1] - 60), ease_out(hook, 2))
    tgt = lerp2(tgt, tgt0, rel)
    tgt = lerp2(tgt, (phc[0] + 70, phc[1] + 60), point * .8)
    dy = (cpos[1] - tgt[1]) / ck
    pw = clamp(dy / 150.0, 0, 1.0)
    dxw = max(0.0, ((cpos[0] - tgt[0]) / ck - 25) / (1.6 * max(pw, .2)))
    reach = max(hook * (1 - rel), point)
    perk = ease_out(clamp((t - (T_TEP - .05)) / .2), 2)
    peek = bump(t, T_KTO - .05, .6)
    turn_v = ease_io(clamp((t - (T_SAM - .15)) / .25))
    st = dict(paw_l=pw * reach, paw_l_dx=dxw, perk=perk * (1 - .5 * peek), ear=6 * math.sin(t * 2.6),
              turn=lerp(lerp(.15, -.6, ease_io(clamp((t - (T_SM - .4)) / .25))), 0.0, turn_v) - .2 * peek,
              look=(lerp(-.85, 0.0, turn_v), lerp(.2, 0.0, turn_v) + .35 * peek), tilt=-10 * peek + 6 * turn_v * math.sin(min(1.0, t - T_SAM) * 9) * (t > T_SAM),
              rot=-6 * peek, tail=-8 + 8 * math.sin(t * 2.2), smug=.6 * turn_v, flame_e=1.0 + .4 * turn_v,
              blink=1.0 if abs(t - (t0 + .1)) < .05 else 0.0)
    o.append(blob(ellipse_pts(cpos[0] + 30, cpos[1] + 6, 200 * ck, 24, 16), "#000000", .32))
    o.append(nt["dark"])
    sl = 1 - .6 * open_u
    o.append(screen_pool(phc[0], phc[1], 200, 260, .5 * sl, t))
    cat_svg = CAT.draw(cpos[0], cpos[1], ck, st, t)
    o.append(cat_svg)
    if reach > .05 and hook > .9 and rel < .5:      # коготь в край экрана
        tip = people.cat_paw_tip(cpos[0], cpos[1], ck, st, "l")
        o.append(line([(tip[0] - 4, tip[1] - 30), (tip[0] - 26, tip[1] - 44), (tip[0] - 30, tip[1] - 24)], 5, "#f4f1ea", taper=.6, wmin=.3, seed=8095))
    # камера: дрейф за лапой; «смотри» — наклон 2° к телефону
    tilt = 2.0 * ease_out(clamp((t - T_SM) / .2), 2) * (1 - ease_io(clamp((t - (T_SM + .6)) / .4)))
    u = ease_io(clamp((t - t0) / (SH["s09"]["t1"] - t0)))
    s = lerp(1.7, 1.8, u)
    cx = lerp(640, 615, ease_io(clamp((t - T_SM) / .6))) + 4 * math.sin(t * 1.2)
    cy = an["bed_top"] - 150 + 4 * math.sin(t * 1.5)
    return frame_svg("".join(o), cx, cy, s, -tilt + .3 * math.sin(t * .8), bg="#080b18")


# ═══════════════════════════════ s12–s13: мастерская изобретателя ═══════════════════════════════
INV_K = .92


def ribbon_loop(cx, cy, rx, ry, t, seed, w=70.0, turns=1.0, rot=0.0, speed=0.0):
    """Петля ленты (кольцо карточек) — для куч и гор ленты."""
    n = int(28 * turns)
    a0 = rot
    pts = [(cx + rx * math.cos(a0 + 2 * math.pi * turns * i / n) + 8 * math.sin(i * 1.3 + seed),
            cy + ry * math.sin(a0 + 2 * math.pi * turns * i / n) + 6 * math.cos(i * 1.7 + seed)) for i in range(n + 1)]
    return P.feed_ribbon(pts, t, speed=speed, seed=seed, w=w, card=w * 1.25, gap=w * .1, ink_w=2.6)


def s12(t):
    lib.dyn_begin()
    t0 = SH["s12"]["t0"]
    T_CH, T_PR, T_BES = ws(58), ws(60), ws(61)
    ws_ = R.workshop(t, 0.0)
    bx0, by, bx1 = ws_["anchors"]["bench"]
    o = [ws_["bg"]]
    k = INV_K
    hip = (330.0, 955.0)
    # хореография: сшивает → «Человек» гордо поднимает конец ленты → «придумал» хлопает по рулону → «бесконечную» смотрит вслед ленте
    u_raise = ease_io(clamp((t - (T_CH - .12)) / .26))
    u_slap = ease_out(clamp((t - (T_PR - .14)) / .16), 2)
    u_look = ease_io(clamp((t - (T_BES + .1)) / .3))
    if u_raise < 1:
        pose, u = ("sew", "raise"), u_raise
        ex = "busy" if u_raise < .5 else "proud"
    elif u_slap < 1 and t < T_PR + .05:
        pose, u = ("raise", "slap"), u_slap
        ex = "proud" if u_slap < .5 else "slap"
    else:
        pose, u = "slap", 1.0
        ex = "slap" if u_look < .5 else "look"
    sew_j = (1 - u_raise) * 10 * math.sin(t * 14)
    rk = .78
    R_ = 150 * rk
    rx, ry = 700.0, by - R_
    arms = None
    if u_slap > 0:      # ладонь точно на рулон: летит сверху и прихлопывает
        top = (rx - 70, ry - R_ + 6)
        arms = {"n": ("ik", lerp2((top[0] - 40, top[1] - 160), top, u_slap), -1)}
    fig = people.inventor(hip[0] + sew_j * .3, hip[1], k, pose, t, expr=ex, u=u, feet="stand", head_add=.12 * u_look, lean_add=-.04 * u_look,
                          arms=arms, hands={"n": {"dir": (1, .15), "curl": (.05, .05, .1, .12), "spread": .2, "thumb": .15}} if u_slap > 0 else None)
    o.append(fig["svg"])
    o.append(ws_["bench"])
    # рулон на верстаке: хлопок → начинает разматываться сам, лента через стол, на пол и в дверь (за правый край)
    unroll = ease_in(clamp((t - (T_PR + .04)) / (SH["s12"]["t1"] + .2 - (T_PR + .04))), 1.4)
    sq = P.squash(t, T_PR + .02, .14, 4, 9)
    trail = [(rx + 40, ry + R_ * .9), (bx1 - 10, by - 4), (bx1 + 40, by + 120), (bx1 + 30, 1460), (bx1 + 200, 1510), (1500, 1515)]
    # кусок в руках: от рулона к поднятой кисти (пока не хлопнул)
    if t < T_PR + .02:
        hold = fig["hold"]
        mid = ((hold[0] + rx) / 2, min(hold[1], ry) + 60)
        o.append(P.feed_ribbon([(rx - 60, ry + 20), mid, hold], t, speed=0.0 if u_raise > .5 else -40, seed=12, w=60, card=74, gap=6, ink_w=2.6))
    roll = P.ribbon_roll(rx, ry, rk, max(.02, unroll), t * (1 + 5 * unroll), trail=trail, seed=12)
    o.append(f'<g transform="translate({rx:.1f} {by:.1f}) scale({sq[0]:.4f} {sq[1]:.4f}) translate({-rx:.1f} {-by:.1f})">{roll}</g>')
    # штрихи хлопка
    if 0 < t - T_PR < .25:
        uu = (t - T_PR) / .25
        for j in range(3):
            a = math.radians(-130 + 40 * j)
            c = (rx - 20, ry - R_ - 10)
            o.append(line([(c[0] + math.cos(a) * 40, c[1] + math.sin(a) * 40), (c[0] + math.cos(a) * (40 + 70 * (1 - uu)), c[1] + math.sin(a) * (40 + 70 * (1 - uu)))],
                          7 * (1 - uu) + 1, INK, taper=.5, wmin=.2, seed=8120 + j))
    o.append(ws_["front"])
    # камера: лёгкий наезд, «бесконечную» — дрейф за бегущей лентой вправо-вниз
    push = ease_io(clamp((t - (t0 - .2)) / (T_BES - t0 + .2)))
    drift = ease_io(clamp((t - (T_BES - .1)) / .6))
    s = lerp(1.18, 1.26, push) + .02 * bump(t, T_PR, .25) - .06 * drift
    cx = lerp(520, 540, push) + 160 * drift
    cy = lerp(930, 950, push) + 120 * drift
    return frame_svg("".join(o), cx, cy, s, .3 * math.sin(t * .9) - .8 * drift, bg="#3a2a20")


def wrap_house(hb, t, seed, u=1.0):
    """Лента, обмотавшая дом: две диагональные полосы через фасад и крышу."""
    x0, y0, x1, y1 = hb
    o = ""
    for j in range(2):
        a = (x0 - 30, y0 + (y1 - y0) * (.25 + .4 * j))
        b = (x1 + 30, y0 + (y1 - y0) * (.55 + .35 * j) - 20)
        o += P.feed_ribbon([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 12), b], t, speed=0.0, seed=seed + j, w=26, card=34, gap=4, ink_w=1.8,
                           end=clamp(u * 1.5 - .5 * j))
    return o


def s13(t):
    lib.dyn_begin()
    t0 = SH["s13"]["t0"]
    T_LE, T_PRI, T_ZH, T_NEI = ws(62), ws(65), ws(67), ws(69)
    ws_ = R.workshop(t, .8 + .2 * clamp((t - t0) / 2.6))
    bx0, by, bx1 = ws_["anchors"]["bench"]
    x0w, y0w, x1w, y1w = ws_["win"]
    o = [ws_["bg"]]
    # дома за окном опутаны лентой; лента выходит в окно с кучи
    cid = lib.clip_rect(x0w, y0w, x1w - x0w, y1w - y0w)
    wr = "".join(wrap_house(hb, t, 1300 + 10 * i, 1.0) for i, hb in enumerate(ws_["houses"]))
    o.append(f'<g clip-path="url(#{cid})">{wr}</g>')
    o.append(P.feed_ribbon([(560, 1250), (640, 980), (760, 770), (900, 640), (1080, 560)], t, speed=-30, seed=1320, w=90, card=110, gap=8))
    o.append(ws_["bench"])
    # горы петель на верстаке и на полу
    for i, (cx_, cy_, rx_, ry_) in enumerate(((300, 1130, 190, 60), (560, 1120, 170, 70), (820, 1140, 160, 55), (180, 1420, 210, 80), (720, 1440, 260, 90),
                                               (980, 1400, 160, 70))):
        o.append(ribbon_loop(cx_, cy_, rx_, ry_, t, 1330 + i, w=62, turns=1.6, rot=i * .7))
    pile = (420.0, 1450.0)
    for i in range(4):
        o.append(ribbon_loop(pile[0] + 30 * (i % 2) - 10, pile[1] - 30 * i, 230 - 22 * i, 70 - 6 * i, t, 1350 + i, w=70, turns=1.3, rot=i * 1.1))
    # изобретатель сидит на куче ленты
    k = INV_K
    hip = (pile[0], 1290.0)
    u_win = ease_io(clamp((t - (T_LE - .3)) / .3))
    u_turn = ease_io(clamp((t - (T_PRI - .08)) / .3))
    u_head = ease_out(clamp((t - (T_ZH - .1)) / .22), 2)
    u_pull = ease_io(clamp((t - (T_NEI - .2)) / .25))
    if u_pull > 0:
        pose, u, ex = ("head", "pull"), u_pull, "tug" if u_pull > .5 else "regret"
    elif u_head > 0:
        pose, u, ex = ("sit", "head"), u_head, "regret" if u_head > .4 else "turn"
    else:
        pose, u, ex = "sit", 1.0, "look" if u_turn < .5 else "turn"
    exd = dict(people.EXPR["inventor"][ex])
    if ex == "look":
        exd["look"] = (.8, -.6)
    head_add = -.22 * u_win * (1 - u_turn) + .1 * u_head * (1 - u_pull)
    sag = .1 * u_head * (1 - u_pull)
    flip = False
    fig = people.inventor(hip[0], hip[1], k, pose, t, expr=exd, u=u, feet="sit", head_add=head_add, lean_add=sag - .08 * u_pull, flip=flip)
    o.append(fig["svg"])
    # «ней» — тянет кусок ленты обратно, она натянута и не идёт
    if u_pull > .3:
        hold = fig["hold"]
        tug = 6 * math.sin(t * 40) * u_pull
        o.append(P.feed_ribbon([hold, (hold[0] + 160, hold[1] + 20 + tug), (hold[0] + 330, hold[1] - 30), (900, 640)], t, speed=0.0, seed=1370, w=54,
                               card=66, gap=6, ink_w=2.4))
        if u_pull > .6:
            for j in range(2):
                c = (hold[0] + 80 + 60 * j, hold[1] - 40)
                o.append(line([(c[0], c[1]), (c[0] + 8, c[1] - 24)], 4, INK, taper=.5, wmin=.2, seed=1380 + j, op=.8))
    o.append(ws_["front"])
    # камера: медленный отъезд, открывающий масштаб ленты; «жалеет» — короткий толчок к лицу
    back = ease_io(clamp((t - (t0 - .2)) / (T_ZH - t0)))
    hd = fig["head"]
    jab = bump(t, T_ZH, .45)
    s = lerp(1.3, 1.02, back) + .12 * jab
    cx = lerp(470, 560, back) + (hd[0] - 560) * .3 * jab
    cy = lerp(1040, 920, back) + (hd[1] - 920) * .3 * jab
    return frame_svg("".join(o), cx, cy, s, .3 * math.sin(t * .8), bg="#3a2a20")


SCENES = {"s04": s04, "s05": s05, "s08": s08, "s09": s09, "s12": s12, "s13": s13}


def frame(sid, t):
    return SCENES[sid](t)
