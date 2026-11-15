"""Рилс 74 «Прекрати ныть», группа B: Дима.
s02 (1.40–2.80, whip): сверху с трона из-за плеча кота вниз на стол Димы. Край красной накидки и подлокотник у верхнего края,
    затылок, ухо и плечо кота сверху слева. Дима держит телефон двумя руками у груди и с кадра 0 поднимает голову к трону;
    «взрослые» (1.75) лапа кота из-за края указывает вниз на него; «люди» (2.30) вжимает голову в плечи; «просто» (2.59) плечи
    опускаются, телефон уходит к животу.
s08 (9.15–11.30): ночь, свет экрана и маленькой лампы. Дима опускает телефон, «написал» (9.16) кладёт его экраном вниз;
    «взрослый человек» (9.57–10.40) трёт щетину, выпрямляется; «и это я» (10.70–11.12) поворачивается к камере с усталой
    полуулыбкой, пожимает плечом; кот на столе смотрит на него снизу и прижимается боком к локтю.
s10 (13.60–15.15): ночь, тёплая лампа. Кот поворачивает голову к Диме и на «Мы не ноем» (13.73–14.40) твёрдо мотает головой;
    «нам тяжело» (14.52–15.04) Дима берёт банку двумя руками и пытается открутить крышку — не поддаётся; «начать» (15.12)
    руки соскальзывают.
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
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?:«»").lower() == word:
            return w["start"]
    raise KeyError(word)


def lerp(a, b, u):
    return a + (b - a) * u


def frame_svg(body, cx, cy, s, rot, bg="#05070f", over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def tint_k(svg_, k):
    return R._tint(svg_, f"{k[0]:.3f} 0 0 0 0 0 {k[1]:.3f} 0 0 0 0 0 {k[2]:.3f} 0 0 0 0 0 1 0", "t74b")


# ═══════════════════════════════ s02: сверху с трона на Диму ═══════════════════════════════
T2_V = wt("взрослые")       # 1.75
T2_L = wt("люди")           # 2.30
T2_P = wt("просто")         # 2.59
S2 = .82


def s02(t):
    lib.dyn_begin()
    th = R.throne_scene(t, "regal", "top")
    pal = th["pal"]
    kk = pal["k"]
    o = [th["bg"], th["chair_back"]]
    hx, hy = th["dima"]
    # голова поднимается к трону с кадра 0; «люди» — вжимается; «просто» — плечи опускаются, телефон к животу
    up = ease_out(clamp((t - 1.2) / .45), 2)
    shr = ease_out(clamp((t - T2_L) / .16), 2)
    drop = ease_io(clamp((t - T2_P) / .25))
    ex = dict(people.EXPR["dima"]["guilty74" if t < T2_L else "shrink74"])
    ex["look"] = (lerp(.5, .3, up), lerp(-.2, -.85, up))
    if t > T2_P + .1:
        ex["look"] = (.3, lerp(-.85, -.5, drop))
    br = 3 * math.sin(t * 2.4)
    fig = people.dima_phone(hx, hy + br, S2, ex, "phone_chest74", u_pose=("phone_belly74", drop), shrug=.85 * shr - .25 * drop,
                            head_add=lerp(.2, -.24, up) + .1 * shr + .1 * drop, lean_add=-.05 * up + .04 * drop, phone_rot=-14 + 10 * drop)
    dima_svg = fig["svg"]
    if shr > 0 and t < T2_L + .5:          # вздрог: короткие штрихи у плеч
        u = clamp((t - T2_L) / .35)
        hd = fig["head"]
        for j, sx in enumerate((-1, 1)):
            for q in range(2):
                a0 = (hd[0] + sx * (150 + 30 * q) * S2, hd[1] + (90 + 40 * q) * S2)
                dima_svg += line([a0, (a0[0] + sx * 34 * (1 - u), a0[1] - 20 * (1 - u))], 6 * (1 - u), INK, taper=.6, wmin=.1, seed=2200 + j * 4 + q)
    o.append(tint_k(dima_svg, kk))
    o.append(th["desk"])
    o.append(th["light"])
    o.append(th["motes"])
    # камера мира: хлёст вниз, медленный наезд на Диму, толчок на «люди»
    wu = clamp((t - 1.2) / .22)
    wy = -300 * (1 - ease_out(wu, 3))
    push = ease_io(clamp((t - 1.4) / 1.4))
    jab = .03 * math.sin(math.pi * clamp((t - T2_L) / .22))
    s = 1.55 * (1 + .05 * push + jab)
    cx = lerp(500, 520, push)
    cy = lerp(1130, 1150, push) + wy / s
    rot = -1.6 * (1 - ease_out(wu, 3)) + .3 * math.sin(t * 1.3)

    def scr(p):         # мир → кадр
        a = math.radians(rot)
        x, y = (p[0] - cx) * s, (p[1] - cy) * s
        return 540 + x * math.cos(a) - y * math.sin(a), 960 + x * math.sin(a) + y * math.cos(a)
    # передний план в координатах кадра (ближе к камере — едет сильнее): край накидки, затылок и плечо кота, лапа
    par = 1.25
    fy = wy * par
    ov = []
    ov.append(tint_k(P.throne_drape(640, -960 + fy, 1.85, 1.0, 14, t, seed=1), (min(1, kk[0] * 1.4), min(1, kk[1] * 1.4), min(1, kk[2] * 1.12))))
    point = ease_out(clamp((t - T2_V + .08) / .2), 3)
    hd = scr(fig["head"])
    if point > 0:
        tip0 = (300, -160)
        tip1 = (hd[0] + 30, hd[1] - 330)
        tip = (lerp(tip0[0], tip1[0], point) + 6 * math.sin(t * 4), lerp(tip0[1], tip1[1], point) + 10 * math.sin(t * 3.1) * point)
        tip = (tip[0], tip[1] + 30 * P.hop(t, T2_L, 1, .2))      # «люди» — лапа коротко тычет
        ov.append(tint_k(people.cat_forearm((150, -60 + fy), tip, 1.5, claw=.6 * point, seed=1), (1.15, 1.15, 1.25)))
    ov.append(tint_k(people.cat_back74(110, 170 + fy, 1.05, t, turn=.3 * point), (1.15, 1.15, 1.25)))
    return frame_svg("".join(o), cx, cy, s, rot, bg=lib.mul("#4e3624", kk), over="".join(ov))


# ═══════════════════════════════ s08: «и это я» ═══════════════════════════════
T8_N = wt("написал")        # 9.16
T8_V = wt("взрослый")       # 9.57
T8_I = wt("и", 10.5)        # 10.56
T8_E = wt("это", 10.6)      # 10.70
T8_YA = wt("я", 10.9)       # 11.00
DS = .92
PH8 = (655.0, R.DESK_TOP - 30)


def _desk_dima(t, nd, ex, pose, u_pose=None, extra="", near_extra="", **kw):
    """Слои Димы за столом ночью: стул, ноги, стол, тело, предметы, ближняя рука (порядок desk_scene)."""
    hx, hy = nd["sit"]
    fkw = dict(people.sit_kw(hx, hy, DS))
    fkw.update(kw)
    legs = people.dima(hx, hy, DS, ex, pose, u_pose=u_pose, layers=("legs",), **fkw)
    body = people.dima(hx, hy, DS, ex, pose, u_pose=u_pose, layers=("pelvis", "arm_f", "body"), **fkw)
    arm = people.dima(hx, hy, DS, ex, pose, u_pose=u_pose, layers=("arm_n",), **fkw)
    o = [nd["chair_back"], nd["desk_top"], nd["pool"], legs["svg"], nd["desk_legs"], nd["chair_seat"], body["svg"], extra, arm["svg"], near_extra]
    return "".join(o), arm


def s08(t):
    lib.dyn_begin()
    nd = R.night_desk(t, .72, "mid")
    hx, hy = nd["sit"]
    o = [nd["bg"]]
    # хореография рук: опускает телефон → кладёт → трёт щетину → выпрямляется → пожимает плечом
    lay = ease_io(clamp((t - 8.95) / (T8_N + .3 - 8.95)))
    on_desk = t >= T8_N + .28
    rub = ease_io(clamp((t - T8_V) / .22)) * (1 - ease_io(clamp((t - 10.3) / .25)))
    turn = ease_io(clamp((t - T8_E + .1) / .3))
    shrug = .32 * math.sin(math.pi * clamp((t - T8_YA + .05) / .4))
    if t < T8_V:
        pose, up = "phone_chest74", ("place74", lay)
        ex = "screen74"
    elif t < 10.3:
        pose, up = "place74", ("rub74", rub)
        ex = "rub74" if rub > .5 else "screen74"
    elif t < T8_E - .1:
        pose, up = "rub74", ("desk74", 1 - rub)
        ex = "straight74"
    else:
        pose, up = "desk74", ("shrug74", turn)
        ex = "halfsmile74" if turn > .4 else "straight74"
    exd = dict(people.EXPR["dima"][ex])
    if t > T8_I - .02 and t < T8_E:
        exd = people.awake_blink(exd, math.sin(math.pi * clamp((t - T8_I) / .14)))
    arms = None
    if 9.57 <= t < 10.3 and rub > .3:   # ладонь ходит по щетине
        tx, ty = 165 + 14 * math.sin((t - T8_V) * 15), -352 + 10 * math.cos((t - T8_V) * 15)
        arms = {"n": ("ik", (hx + tx * DS, hy + ty * DS), -1)}
    straight = ease_io(clamp((t - 10.1) / .4))
    lean_add = .1 * (1 - straight) - .04 * straight + .03 * math.sin(t * 1.5)
    head_add = .14 * (1 - straight) - .12 * turn + .08 * rub
    phone = ""
    near = ""
    if not on_desk:
        pass
    else:
        sq = P.squash(t, T8_N + .28, .12, 3, 9)
        phone = P.phone_flat(PH8[0], PH8[1], .55 * sq[0], 0, 14, face_down=True, seed=3)
    cat_st = _cat8(t)
    cx_, cy_, ck = nd["cat"]
    catpos = (712 - 26 * ease_io(clamp((t - 10.05) / .4)), cy_ - 40)
    catsvg = blob(ellipse_pts(catpos[0], catpos[1] + 4, 110 * ck, 14, 14), "#000000", .2) + people.cat_svg(catpos[0], catpos[1], ck * .85, cat_st, t)
    body_svg, arm = _desk_dima(t, nd, exd, pose, up, extra=catsvg + phone, arms=arms, lean_add=lean_add, head_add=head_add,
                               shrug=shrug) if True else ("", None)
    o.append(body_svg)
    if not on_desk:      # телефон в руке: спинкой к нам, опускается к столу
        ph = people.hand_pos(arm, "n", 46)
        o.append(people.mobilnik(ph[0], ph[1], 1.35 * DS, lerp(-14, -80, lay), seed=952))
        o.append(people.dima(hx, hy, DS, exd, pose, u_pose=up, layers=("arm_n",), lean_add=lean_add, head_add=head_add, shrug=shrug,
                             **people.sit_kw(hx, hy, DS))["svg"])
    o.append(nd["lamp"])
    o.append(nd["dark"])
    # свет экрана на лице, пока телефон в руке; гаснет, когда он лёг экраном вниз
    head = arm["head"]
    o.append(R.screen_light74(head[0] + 52, head[1] + 62, 100, 110, 1 - ease_in(clamp((t - T8_N - .1) / .3)), t))
    # камера: медленный наезд к лицу, на «я» стоп
    cam = nd["cam"]
    push = ease_io(clamp((t - 8.95) / (T8_YA - 8.95)))
    s = 1.85 * (1 + .05 * push)
    fx, fy = head
    cx = lerp(505, fx + 120, .25 * push)
    cy = lerp(890, fy + 220, .25 * push)
    return frame_svg("".join(o), cx, cy, s, .25 * math.sin(t * .9))


def _cat8(t):
    """Кот на столе: смотрит снизу на Диму, на «человек» прижимается боком к его локтю, моргает медленно."""
    nz = ease_io(clamp((t - 10.05) / .4))
    st = dict(people.CAT_ST["warm74"])
    st.update(look=(-.75, -.55), turn=-.45, tail=6 * math.sin(t * 2.2), blink=0.0, smile=0.0)
    if nz > 0:
        st.update(tilt=-12 * nz, rot=-7 * nz, blink=.3 * nz, smile=1.0 if nz > .5 else 0.0, look=(lerp(-.75, -.45, nz), lerp(-.55, -.2, nz)))
    for tb in (9.4, 10.9):
        if abs(t - tb) < .07:
            st["blink"] = 1.0
    return st


# ═══════════════════════════════ s10: банка не поддаётся ═══════════════════════════════
T10_M = wt("мы")            # 13.73
T10_NO = wt("ноем")         # 14.08
T10_N = wt("нам")           # 14.52
T10_T = wt("тяжело")        # 14.70
T10_S = wt("начать")        # 15.12


def s10(t):
    lib.dyn_begin()
    nd = R.night_desk(t, "lamp", "mid")
    hx, hy = nd["sit"]
    o = [nd["bg"]]
    jx, jy, jk = hx + 365 * DS, R.DESK_TOP - 58, .74
    grab = ease_out(clamp((t - T10_N) / .2), 2)
    strain = clamp((t - T10_T + .05) / .15) * (1 - clamp((t - T10_S) / .1))
    slip = ease_out(clamp((t - T10_S) / .16), 2)
    jit = 5 * strain * math.sin(t * 57)
    lid = P.jar_lid_c(jx, jy, jk)
    if grab <= 0:
        pose, up = "desk74", None
        ex = "look_cat74"
        arms = None
    else:
        pose, up = "desk74", ("jar74", grab)
        ex = "jar74" if strain > .3 else ("slip74" if slip > .3 else "look_cat74")
        if slip > .3:
            ex = "slip74"
        arms = {"f": ("ik", (lerp(hx + 210 * DS, jx - 64 * jk, grab) - 70 * slip, lerp(hy - 200 * DS, jy - 110 * jk, grab) + 30 * slip), -1),
                "n": ("ik", (lerp(hx + 270 * DS, lid[0] + 4, grab) + jit + 30 * slip, lerp(hy - 200 * DS, lid[1] + 30, grab) - 16 * slip), -1)}
    hands = {"n": {"dir": (lerp(1, .9, slip), lerp(.3, -.1, slip)), "curl": tuple(lerp(.45, .78, grab * (1 - slip)) for _ in range(4)), "thumb": .65},
             "f": {"dir": (lerp(1, .25, grab), lerp(.3, -1, grab)), "curl": tuple(lerp(.45, .74, grab * (1 - slip)) for _ in range(4)), "thumb": .6}}
    exd = dict(people.EXPR["dima"][ex])
    if ex == "look_cat74":
        exd["look"] = (.7, .55)
    jar_svg = P.jar(jx + jit * .3, jy, jk, 0, jit * .2, 0.0, strain, seed=1, t=t)
    cat_st = _cat10(t)
    cx_, cy_, ck = nd["cat"]
    catpos = (805, cy_ - 52)
    catsvg = blob(ellipse_pts(catpos[0], catpos[1] + 4, 100 * ck, 13, 14), "#000000", .2) + people.cat_svg(catpos[0], catpos[1], ck * .85, cat_st, t)
    lean = .08 * grab - .06 * slip + .03 * strain * math.sin(t * 40)
    body_svg, arm = _desk_dima(t, nd, exd, pose, up, extra=catsvg + jar_svg, arms=arms, hands=hands, lean_add=lean, head_add=.05 * strain - .05 * slip,
                               shrug=.35 * strain)
    o.append(body_svg)
    if strain > .05:
        o.append(people.strain_marks(arm["head"], DS, t, strain))
    o.append(nd["lamp"])
    # камера: лёгкий дрейф вправо, на «тяжело» дрожь 1 % в такт усилию
    cam = nd["cam"]
    d = ease_io(clamp((t - 13.4) / 1.9))
    sh = 8 * strain * math.sin(t * 43)
    return frame_svg("".join(o), 560 + 25 * d + sh, 840 + sh * .5, 1.62 * (1 + .02 * d), .2 * math.sin(t * 1.1))


def _cat10(t):
    """Кот поворачивает голову к Диме (кадр 0 уже в повороте), «Мы не ноем» — твёрдо мотает головой «нет», уши разлетаются."""
    st = dict(people.CAT_ST["no74"])
    tu = ease_out(clamp((t - 13.4) / .25), 2)
    st.update(turn=lerp(.1, -.55, tu), look=(-.8, -.4), tail=7 * math.sin(t * 2.4), flame_e=1.1)
    u = clamp((t - T10_M) / (14.42 - T10_M))
    if 0 < u < 1:
        sw = math.sin(u * 2 * math.pi * 3.0) * math.sin(math.pi * u) ** .5
        st.update(turn=.95 * sw, tilt=-7 * sw, ear=22 * sw, look=(0, 0), perk=1.0, blink=.25)
    if t > 14.42:
        st.update(turn=lerp(.0, -.4, ease_io(clamp((t - 14.42) / .3))), look=(-.7, -.2), perk=.4)
    return st


SCENES = {"s02": s02, "s08": s08, "s10": s10}


def frame(sid, t):
    return SCENES[sid](t)
