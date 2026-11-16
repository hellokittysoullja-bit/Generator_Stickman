"""Рилс 79 «Месть сну», группа B: люди, кот, призыв. Время — только из shots.json и voice/words.json (слово по индексу wN).
s05: призыв «Телеграм» модулем scripts/story_cta_tg.py: PRESS = W[20].start + 0.12 («Телеграм»), T0 = PRESS − 1.10.
s07: мансарда снизу на люк, кот на изголовье: «смотри» (w30) к зрителю, «куда» (w31) звёзды стекают в свет экрана, «ночь» (w33) люк пуст.
s09: офис, «работы» (w39) шлёпается стопка папок, «других» (w42) люди с просьбами, Дима кивает и берёт.
s12: Дима обнимает тёплый сектор, «время» (w53) луна тянет луч, «сна» (w55) прижимает, «так» (w57) улыбка, кот вздыхает.
s15: тёплый вечер, «теперь» (w68) телефон в ящик, «берёт» (w70) гитару со стены, сдувает пыль, «себе» (w71) прижимает.
s16: играет на коврике, «полчаса» (w72) аккорд, «вечером» (w73) кот в такт, «ещё» (w74) глаза закрыты.
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


# ═══════════════════════════════ s05: призыв «Телеграм» ═══════════════════════════════
def s05(t):
    import story_cta_tg as tg
    press = ws(20) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=COMMON)


def frame_svg(body, cx, cy, s, rot=0.0, bg="#05070f", over=""):
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


def lie_at(head, k, t, **kw):
    """Дима лёжа, голова в точке head (мир): подбираем таз по первому вызову."""
    f0 = people.dima_lie79(0.0, 0.0, k, t, **kw)
    dx, dy = head[0] - f0["head"][0], head[1] - f0["head"][1]
    lib_defs = len(lib.DEFS)
    del lib.DEFS[lib_defs:]
    return people.dima_lie79(dx, dy, k, t, **kw)


# ═══════════════════════════════ s07: загадка — звёзды стекают в экран ═══════════════════════════════
S07_STARS = [(735, 540, 22), (860, 545, 18), (960, 640, 24), (800, 650, 17), (905, 735, 20), (712, 640, 16)]


def s07(t):
    lib.dyn_begin()
    T_LOOK, T_WHERE, T_NIGHT = ws(30), ws(31), ws(33)
    a = R.attic(t, "night_phone", sky="empty", pillow=False)
    o = [a["bg"], a["sky"]]
    # звёзды в люке (до своего срыва), мерцают; срываются по одной с «куда»
    fall = [T_WHERE + .02 + i * .13 for i in range(len(S07_STARS))]
    DUR = .62
    head = (330.0, 920.0)
    k = .5
    dima = lie_at(head, k, t, mode="phone", glow=1.0, blanket=.15)
    ph = dima["phone"]
    cid = lib.clip_of([(x, y, 1) for x, y in R.AT_SKY])
    st_in, drips = [], []
    for i, ((sx, sy, r), tf) in enumerate(zip(S07_STARS, fall)):
        tw = .75 + .25 * math.sin(t * 7.3 + i * 1.9)
        if t < tf:
            st_in.append(P.star4(sx, sy, r * 1.4 * tw, 1.0))
        u = (t - tf) / DUR
        if 0 < u < 1:
            drips.append(P.star_drip(sx, sy, ph[0] + 20, ph[1] - 10, u, r=r * 2.1, seed=i))
    # к «ночь» небо сереет и пустеет
    gr = ease_io(clamp((t - (T_NIGHT - .2)) / .45))
    grey = blob([(x, y, 1) for x, y in R.AT_SKY], "#6b7088", .45 * gr)
    o.append(f'<g clip-path="url(#{cid})">{"".join(st_in)}</g>')
    o.append(a["frame"] + grey)
    o.append(dima["svg"])
    o.append("".join(drips))
    # вспышки экрана, когда звезда в нём гаснет
    for i, tf in enumerate(fall):
        v = t - (tf + DUR * .92)
        if 0 < v < .25:
            g = lib.rad_grad([(0, "#eef8ff", .7 * (1 - v / .25)), (1, "#cfe6ff", 0)], ph[0], ph[1], 90)
            o.append(f'<circle cx="{ph[0]:.1f}" cy="{ph[1]:.1f}" r="90" fill="url(#{g})"/>')
    # кот на одеяле у колен Димы: смотрит на люк → к зрителю (прищур) → бровь, смотрит на Диму
    st = dict(people.CAT_ST["ridge79"])
    st["look"] = (.2, -.9)
    st["tail"] = 8 * math.sin(t * 2.6)
    if t >= T_LOOK - .05:
        u = ease_out(clamp((t - (T_LOOK - .05)) / .22))
        st = dict(people.CAT_ST["sly79"])
        st["tilt"] = -8 * u
        st["tail"] = 8 * math.sin(t * 2.6)
    if t >= T_WHERE:      # следит за звёздами, но с прищуром
        st["look"] = (.3, -.6 + 1.2 * clamp((t - T_WHERE) / .8))
    if t >= T_NIGHT - .04:
        st = dict(people.CAT_ST["brow79"])
        st["tail"] = 10 * math.sin(t * 2.2)
        st["drop"] = .15 * kick(t, T_NIGHT - .04, 1.0, .4)
    cx_cat, cy_cat = 800.0, 1010.0
    o.append(people.cat_svg(cx_cat, cy_cat, .72, st, t))
    o.append(a["bed"] + a["front"] + a["light"])
    # камера: дрейф вверх за звёздами, толчок на «ночь»
    t0, t1 = SH["s07"]["t0"] - .2, SH["s07"]["t1"] + .2
    u = (t - t0) / (t1 - t0)
    cx = 610 + 20 * u
    cy = 830 - 60 * ease_io(clamp(u))
    s_ = 1.25 + .06 * u + .06 * kick(t, T_NIGHT, 1.0, .45)
    jx, jy = shake(t, T_NIGHT, 6, .25)
    return frame_svg("".join(o), cx + jx, cy + jy, s_, 0.0, over=a["shade"])


# ═══════════════════════════════ s09: папки и чужие просьбы ═══════════════════════════════
def office_chair(x, y, k=1.0):
    """Офисный стул сбоку: сиденье (верх на y), спинка за тазом, стойка и колёса до пола R.OD_FL."""
    fl = R.OD_FL
    o = shape(lib.rrect(x - 150 * k, y, x + 130 * k, y + 46 * k, 18 * k), "#3b4252", blob(lib.rrect(x - 150 * k, y + 26 * k, x + 130 * k, y + 46 * k, 14 * k),
                                                                                         "#2a303c"), w=4.0, seed=7971)
    o += shape(lib.rrect(x - 190 * k, y - 330 * k, x - 130 * k, y + 20 * k, 26 * k), "#3b4252", "", w=4.0, seed=7972)
    o += shape(lib.rect_pts(x - 14 * k, y + 46 * k, x + 14 * k, fl - 50), "#6a7180", "", w=3.2, seed=7973)
    o += line([(x - 150 * k, fl - 40), (x + 150 * k, fl - 40)], 12 * k, "#4a5160", taper=0, wmin=1, seed=7974)
    for wx in (x - 140 * k, x + 140 * k):
        o += shape(ellipse_pts(wx, fl - 18, 20, 18, 10), "#2a2e36", "", w=3.0, seed=7975 + int(wx) % 7)
    return o


def s09(t):
    lib.dyn_begin()
    T_WORK, T_OTH = ws(39), ws(42)
    sun = .6 + .12 * clamp((t - SH["s09"]["t0"]) / 2.0)
    od = R.office_day(t, sun)
    dx0, dx1, dy = R.OD_DESK
    dx0 = 470.0                        # свой стол: начинается у колен Димы (иначе крышка режет его по животу)
    sc_ = .66
    hip = (300.0, 1236.0)
    o = [od["bg"]]
    # люди с просьбами — за столом справа, входят с края по очереди на «других»
    T_P = [T_OTH - .06, T_OTH + .2, T_OTH + .44]
    NOD = [tp + .2 for tp in T_P]
    ppl = []
    specs = [("mama", 820.0, 0.0, .66), ("friend", 1100.0, 0.0, .66), ("col", 960.0, 0.0, .66)]
    for (kind, px, py, ps), tp in zip(specs, T_P):
        e = clamp((t - tp) / .28)
        if e <= 0:
            continue
        sl = (1 - ease_out(e, 3)) * 420 + 14 * math.sin(math.pi * clamp(e * 1.4)) * (1 - e)
        offer = ease_out(clamp((t - tp - .12) / .25))
        who = {"col": "girl", "mama": "mama", "friend": "friend"}[kind]
        py = R.OD_FL - 30 - (people.LEG_LEN - 12) * ps * people.HEIGHT[who]
        X = px + sl
        ft = people.stand_kw(X, py, ps, who)["feet"]
        if kind == "col":
            f = people.colleague79(X, py, ps, offer, t, feet=ft)
        elif kind == "mama":
            f = people.mama79(X, py, ps, offer, t, feet=ft)
        else:
            f = people.friend79(X, py, ps, offer, t, feet=ft)
        ppl.append(({"col": 1, "mama": 2, "friend": 0}[kind], f["svg"]))
    # Дима: таз и ноги за столом (стул), тело поверх
    o.append(office_chair(hip[0] - 10, hip[1] + 30, .62))
    # стопка папок: падает и шлёпается на «работы», потом подрастает чужими вещами
    land = T_WORK
    sx, sy = 560.0, dy
    if t < land:
        u = clamp(1 - (land - t) / .32)
        yy = sy - 900 * (1 - u * u)
        stack = P.folder_stack(sx, yy, .9, n=5, lean=-4 * (1 - u)) if u > 0 else ""
        sq = 0.0
    else:
        e = t - land
        sq = math.exp(-9 * e) * math.sin(e * 38)
        stack = f'<g transform="translate({sx} {sy}) scale({1 + .08 * sq:.4f} {1 - .12 * sq:.4f}) translate({-sx} {-sy})">{P.folder_stack(sx, sy, .9, n=5)}</g>'
        stack += P.dust_puff(sx - 150, sy - 10, .8, clamp(e / .5), seed=1) + P.dust_puff(sx + 150, sy - 10, .8, clamp(e / .5), seed=2)
    # чужие вещи ложатся на стопку после кивка
    top = sy - 44 * 5 * .9
    if t > NOD[0] + .1:
        u = ease_out(clamp((t - NOD[0] - .1) / .2))
        stack += P.cup_plain(sx - 40, top - 30 * u + 30 * (1 - u) - 10, .9 * u + .01)
    if t > NOD[2] + .1:
        u = ease_out(clamp((t - NOD[2] - .1) / .2))
        stack += people.cardbox79(sx + 30, top - 70 - 60 * (1 - u), .5 * (.3 + .7 * u), -4)
    # руки: на столе (печатает) → подхватывает стопку
    grab = ease_out(clamp((t - land + .02) / .16))
    tw = math.sin(t * 22) * 8 * (1 - grab)
    sc = sc_ * people.HEIGHT["dima"]
    desk_f, desk_n = (hip[0] + 230 * sc, hip[1] - 196 * sc + tw), (hip[0] + 300 * sc, hip[1] - 194 * sc - tw)
    st_f, st_n = (sx + 30, sy - 150), (sx - 150, sy - 100)
    arms = {"f": ("ik", (lerp(desk_f[0], st_f[0], grab), lerp(desk_f[1], st_f[1], grab)), -1),
            "n": ("ik", (lerp(desk_n[0], st_n[0], grab), lerp(desk_n[1], st_n[1], grab)), -1)}
    hands = {"f": {"dir": (1, .35 - .9 * grab), "curl": (.4, .45, .5, .55), "thumb": .4},
             "n": {"dir": (1, .35 - 1.2 * grab), "curl": (.35, .4, .45, .5), "thumb": .4}}
    nod = sum(math.sin(math.pi * clamp((t - n0) / .3)) for n0 in NOD) * .3
    ex = "work79" if t < land else ("nodjerk79" if t < land + .3 else "yes79")
    if any(n0 <= t <= n0 + .3 for n0 in NOD):
        ex = dict(people.EXPR["dima"]["yes79"], closed=.6)
    feet = {"n": ((hip[0] + 170 * sc, R.OD_FL - 20), 0.0), "f": ((hip[0] + 110 * sc, R.OD_FL - 14), 0.0)}
    kw = dict(arms=arms, hands=hands, feet=feet, head_add=nod + .06 * kick(t, land, 1, .3), lean_add=.05 * grab)
    o.append(people.person("dima", hip[0], hip[1], sc_, ex, layers=("legs", "pelvis", "arm_f", "body"), **kw)["svg"])
    desk = shape(lib.rect_pts(dx0, dy, dx1 + 200, dy + 40), "#cfd6dc", blob(lib.rect_pts(dx0, dy + 28, dx1 + 200, dy + 40), "#a8b0b8"), w=4.0, seed=8014)
    for lx in (dx0 + 30, dx1 - 60):
        desk += shape(lib.rect_pts(lx, dy + 40, lx + 30, R.OD_FL), "#8c949c", "", w=3.2, seed=8015 + int(lx) % 5)
    o.append(desk + stack)
    o += [s_ for _, s_ in sorted(ppl)]          # люди у торца стола, ближе к нам: руки с просьбами тянутся над стопкой
    o.append(people.person("dima", hip[0], hip[1], sc_, ex, layers=("arm_n",), **kw)["svg"])
    # камера: наезд на «работы», качок на каждом человеке
    t0 = SH["s09"]["t0"] - .2
    s_ = 1.12 + .02 * (t - t0) + .07 * ease_out(clamp((t - land) / .3)) + .03 * kick(t, land, 1, .3)
    rot = sum(1.2 * (-1) ** i * kick(t, tp + .05, 1, .4) for i, tp in enumerate(T_P))
    jx, jy = shake(t, land, 9, .25)
    return frame_svg("".join(o), 610 + jx, 960 + jy, s_ - .06, rot, bg="#e4e0d6")


# ═══════════════════════════════ s12: «хоть так» — обнимает украденное время ═══════════════════════════════
def light_hand(p0, p1, u, t, w=26.0):
    """Рука-луч луны: мягкая светлая лента от p0 (луна) к p1 (сектор), u — насколько дотянулась; на конце — круглая ладошка."""
    if u <= .01:
        return ""
    ex, ey = lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u)
    mx, my = (p0[0] + ex) / 2 - 60, (p0[1] + ey) / 2 - 30 + 10 * math.sin(t * 5)
    pts = [(p0[0], p0[1]), (mx, my), (ex, ey)]
    o = line(pts, w * 2.2, "#fff2b8", taper=.2, wmin=.6, seed=7981, op=.22)
    o += line(pts, w, "#fff6d0", taper=.35, wmin=.5, seed=7982, op=.75)
    o += blob(ellipse_pts(ex, ey, w * .9, w * .8, 12), "#fff6d0", .9)
    for i in (-1, 0, 1):          # пальчики-лучики
        o += line([(ex, ey), (ex - 18 + 20 * i, ey + 26)], w * .32, "#fff6d0", taper=.4, wmin=.4, seed=7983 + i, op=.9)
    return o


def s12(t):
    lib.dyn_begin()
    T_TIME, T_SLEEP, T_SO = ws(53), ws(55), ws(57)
    a = R.attic(t, "night_phone", sky="empty", pillow=False)
    o = [a["bg"], a["sky"]]
    cid = lib.clip_of([(x, y, 1) for x, y in R.AT_SKY])
    stars = "".join(P.star4(x, y, r * (.8 + .2 * math.sin(t * 6 + i)), 1.0) for i, (x, y, r) in enumerate([(700, 520, 10), (990, 600, 12), (930, 760, 9)]))
    # луна: сонная → тянется лучом на «время» → надулась на «сна»
    pull = ease_out(clamp((t - T_TIME + .05) / .3)) * (1 - .7 * ease_io(clamp((t - T_SLEEP) / .35)))
    mx, my = 712.0, 615.0
    moon = P.moon_cap(mx - 14 * pull, my, 62, t, "pout" if t > T_SLEEP else "sleepy", pull)
    o.append(f'<g clip-path="url(#{cid})">{stars}{moon}</g>')
    o.append(a["frame"])
    # сектор у груди: на «время» луна тянет его (сдвиг к люку), на «сна» Дима прижимает крепче
    tug = pull * 34
    squeeze = kick(t, T_SLEEP, 1.0, .5)
    held_c = {}

    def held(c):
        cx, cy = c[0] + 95 + tug * .8, c[1] + 5 - tug * .5
        held_c["c"] = (cx, cy)
        sec = P.sector_piece(cx, cy, 190, -25 + 8 * pull, 1.0, t, bend=.4 + .4 * squeeze)
        ph = people.mobilnik(cx - 70, cy + 40, .9, 70)
        return ph + f'<g transform="translate({cx:.1f} {cy:.1f}) scale({1 - .1 * squeeze:.3f} {1 + .06 * squeeze:.3f}) translate({-cx:.1f} {-cy:.1f})">{sec}</g>'
    if t < T_SO - .05:
        ex = {"brows": "worry", "mouth": "flat", "lid": .45, "look": (.5, .35)}
        if t > T_TIME:
            ex = {"brows": "worry", "mouth": "o", "open": .12, "lid": .7, "look": (.85, -.6)}       # глянул на луну
        if t > T_SLEEP:
            ex = {"brows": "pinch", "mouth": "pressed", "lid": .3, "look": (.4, .4)}               # прижал
    else:
        ex = dict(people.EXPR["dima"]["hug79"])
    blink = .8 * max(0.0, math.sin(math.pi * clamp((t - (T_SO - .3)) / .2)))
    head = (395.0, 925.0)
    d = lie_at(head, .66, t, mode="hug", u=1.0, held_svg=held, expr=ex, blanket=.05, blink=blink, bump=6 * squeeze)
    # кот на подушке за головой: вздыхает на «так»
    st = dict(people.CAT_ST["sway79"])
    st["look"] = (.4, .4)
    st["tail"] = 6 * math.sin(t * 2.4)
    sg = clamp((t - (T_SO - .1)) / .5)
    if sg > 0:
        st = dict(people.CAT_ST["sigh79"])
        st["drop"] = .5 * math.sin(math.pi * min(1.0, sg * 1.2))
        st["flame_e"] = 1.0 - .4 * math.sin(math.pi * min(1.0, sg))
        st["sy"] = 1 - .05 * math.sin(math.pi * min(1.0, sg))
    pil = P.pillow(270, 1000, 1.7, 0)
    o.append(pil)
    o.append(people.cat_svg(205, 985, .58, st, t))
    o.append(d["svg"])
    if "c" in held_c:
        hc = held_c["c"]
        o.append(light_hand((mx - 40, my + 40), (hc[0] + 40, hc[1] - 50), pull, t))
    o.append(a["bed"] + a["front"] + a["light"])
    t0, t1 = SH["s12"]["t0"] - .2, SH["s12"]["t1"] + .2
    u = (t - t0) / (t1 - t0)
    s_ = 1.5 + .1 * ease_io(clamp(u)) + .05 * kick(t, T_SLEEP, 1, .4)
    cx, cy = 470 - 10 * ease_io(clamp(u)), 830 + 30 * ease_io(clamp(u))
    jx, jy = shake(t, T_SLEEP, 5, .2)
    return frame_svg("".join(o), cx + jx, cy + jy, s_, 0.0, over=a["shade"])


# ═══════════════════════════════ s15: телефон в ящик, гитара со стены ═══════════════════════════════
def drawer_open(u, phone_in=False, P_=None):
    """Ящик тумбочки мансарды (R.AT_NSTAND): лицевая панель выезжает к зрителю (вниз и шире), видно тёмное нутро; phone_in — телефон внутри."""
    nx, ny = R.AT_NSTAND
    u = clamp(u)
    if u <= .01:
        return ""
    wood = (P_ or {}).get("wood", "#8a5634")
    d = 70 * u
    inner = shape([(nx - 140, ny + 12, 1), (nx + 140, ny + 12, 1), (nx + 150, ny + 12 + d, 1), (nx - 150, ny + 12 + d, 1)], "#3a2214",
                  blob([(nx - 120, ny + 16), (nx + 120, ny + 16), (nx + 126, ny + 10 + d * .6), (nx - 126, ny + 10 + d * .6)], "#24140a"), w=3.2, seed=7991)
    if phone_in:
        inner += people.mobilnik(nx + 10, ny + 18 + d * .45, .55, 84, seed=7992)
    front = shape(lib.rrect(nx - 150, ny + 12 + d, nx + 150, ny + 128 + d * 1.08, 6), lib.mul(wood, (1.08, 1.06, 1.04)),
                  shape(lib.rrect(nx - 24, ny + 58 + d, nx + 24, ny + 76 + d, 5), "#c8b49a", "", w=2.0, seed=7993), w=3.8, seed=7994)
    return inner + front


def s15(t):
    lib.dyn_begin()
    T_NOW, T_TAKE, T_SELF = ws(68), ws(70), ws(71)
    a = R.attic(t, "warm_lamp")
    sc_ = .68
    hipy = R.AT_FL - 6 - (people.LEG_LEN - 12) * sc_
    nail = R.AT_GUITAR_NAIL
    gk = people.GUITAR_K * sc_ * people.HEIGHT["dima"]
    g_wall = (nail[0], nail[1] + 700 * gk, 0.0)                    # висит на гвозде за головку
    o = [a["bg"], a["sky"], a["frame"]]
    t_put0, t_close0, t_close1 = T_NOW - .4, T_NOW + .04, T_NOW + .24
    t_walk0, t_walk1 = T_NOW + .22, T_TAKE - .1
    x_stand, x_guitar = -440.0, nail[0] + 230
    # ящик
    opn = ease_out(clamp((t - (t_put0 - .3)) / .3)) * (1 - ease_in(clamp((t - t_close0) / (t_close1 - t_close0))))
    guitar_on_wall = t < T_TAKE
    if guitar_on_wall:
        o.append(P.guitar(*g_wall[:2], gk, g_wall[2], dust_u=1.0, t=t))
    if t < t_walk0:
        u = ease_io(clamp((t - t_put0) / (T_NOW - t_put0)))
        tgt = (R.AT_NSTAND[0] - 20, R.AT_NSTAND[1] + 20 + 40 * opn)
        f = people.dima_drawer79(x_stand, hipy + 30 * u, sc_, u, t, expr="screen79" if u < .5 else "warm79", phone=t < T_NOW, target=tgt)
        o.append(f["svg"])
        o.append(drawer_open(opn, t >= T_NOW, a.get("P")))
    elif t < t_walk1:
        o.append(drawer_open(opn, True, a.get("P")))
        u = clamp((t - t_walk0) / (t_walk1 - t_walk0))
        x = lerp(x_stand, x_guitar, ease_io(u))
        wk = people.walk_kw(x, hipy, sc_, u * 1.6, stride=300.0)
        # смотрит влево (flip): ноги в неотражённой системе
        f = people.person("dima", x, wk["hip"][1], sc_, "warm79", feet=wk["feet"], flip=True, lean_add=.12,
                          arms={"f": ("ang", .5 * math.sin(6 * u), .5), "n": ("ang", -.5 * math.sin(6 * u), .5)})
        o.append(f["svg"])
    else:
        o.append(drawer_open(0, True, a.get("P")))
        # гитара: со стены → к лицу (сдувает пыль) → прижал
        u1 = ease_io(clamp((t - t_walk1) / (T_TAKE + .02 - t_walk1)))       # руки к гитаре на стене
        u2 = ease_io(clamp((t - T_TAKE) / .22))                             # снял и поднёс
        u3 = ease_io(clamp((t - T_SELF) / .25))                             # прижал
        g_blow = (x_guitar - 140, hipy - 10, -40.0)
        g_hug = (x_guitar - 150, hipy + 90, -54.0)
        if u3 > 0:
            gp = tuple(lerp(g_blow[i], g_hug[i], u3) for i in range(3))
        else:
            gp = tuple(lerp(g_wall[i], g_blow[i], u2) for i in range(3))
            gp = (gp[0], gp[1] - 60 * math.sin(math.pi * u2), gp[2])
        dust = 1.0 - clamp((t - (T_TAKE + .16)) / .3)
        ex = "warm79" if t < T_TAKE + .12 else ("blow79" if t < T_SELF else "warm79")
        f = people.dima_guitar79(x_guitar, hipy, sc_, "hold", u=u1, t=t, expr=ex, gpos=gp, dust_u=dust, lean_add=-.04 + .06 * u3)
        o.append(f["svg"])
        pu = clamp((t - (T_TAKE + .15)) / .45)
        if 0 < pu < 1:
            o.append(P.dust_puff(f["hole"][0] - 40, f["hole"][1] - 60, 1.1, pu, seed=3))
    o.append(a["front"] + a["light"])
    # камера: у тумбочки → панорама за Димой к гитаре; мягкий наезд
    pan = ease_io(clamp((t - t_walk0 + .05) / (t_walk1 - t_walk0 + .15)))
    cx = lerp(-380, x_guitar - 60, pan)
    s_ = .98 + .05 * clamp((t - SH["s15"]["t0"]) / 1.8) + .03 * kick(t, T_TAKE, 1, .35)
    return frame_svg("".join(o), cx, 1000, s_, -.6 * kick(t, T_SELF, 1, .5), over=a["shade"], bg="#2a1608")


# ═══════════════════════════════ s16: играет на коврике ═══════════════════════════════
def s16(t):
    lib.dyn_begin()
    T_HALF, T_EVE, T_MORE = ws(72), ws(73), ws(74)
    a = R.attic(t, "warm_lamp")
    o = [a["bg"], a["sky"], a["frame"]]
    sc_ = .86
    rx, ry = R.AT_RUG
    x, y = rx + 40, ry - 30 - 112 * sc_
    BEAT = .5
    ph = (t - T_HALF) / BEAT if t >= T_HALF else (t - T_HALF) / 1.2
    strum_ph = ph % 1.0
    hit = math.exp(-6 * (strum_ph * BEAT)) if t >= T_HALF - .02 else 0.0
    sway = math.sin(2 * math.pi * ph * .5)
    ex = "warm79" if t < T_MORE else "play79"
    f = people.dima_guitar79(x, y, sc_, "play", t=t, expr=ex, strum_ph=strum_ph * .5, strum=hit, lean_add=.03 * sway)
    # кот справа на коврике: качает хвостом в такт с «вечером», огонёк разгорается
    st = dict(people.CAT_ST["sway79"])
    eve = clamp((t - T_EVE) / .3)
    st["tail"] = 4 * math.sin(t * 2) + 16 * eve * math.sin(2 * math.pi * (t - T_EVE) / BEAT)
    st["tilt"] = 6 * eve * math.sin(2 * math.pi * (t - T_EVE) / BEAT)
    st["flame_e"] = 1.0 + .9 * eve
    st["look"] = (-.5, .1)
    st["blink"] = .55 if t < T_MORE else .9
    o.append(people.cat_svg(rx + 320, ry + 24, .62, st, t))
    o.append(f["svg"])
    if t >= T_HALF - .02:
        wu = clamp((t - T_HALF) / .25)
        o.append(P.music_waves(f["hole"][0] - 30, f["hole"][1] - 40, 1.0 + .25 * hit, t, wu, ang=-100, n=3))
    o.append(a["front"] + a["light"])
    # облёт: камера плывёт вбок, лёгкий качок в такт
    t0 = SH["s16"]["t0"] - .2
    u = (t - t0) / 1.9
    cx = rx - 40 - 60 * ease_io(clamp(u))
    s_ = 1.08 + .06 * ease_io(clamp(u)) + .02 * hit
    rot = -1.2 + 2.0 * ease_io(clamp(u)) + .5 * sway
    return frame_svg("".join(o), cx, 1230, s_, rot, over=a["shade"], bg="#2a1608")


def frame(sid, t):
    return globals()[sid](t)
