"""Рилс 75 «Ток или скука», группа B: люди и кот.
s05 призыв: кот у коробки кнопкой к зрителю, «кот» пишется пером (hand_kot), «узнаешь» — подвигает коробку к камере, «сколько» —
    маленький счётчик крутится смазом, «ты» — лапа на зрителя.
s06 кот у стены со счётчиком под тряпицей: «Не напишешь» — пожимает плечами и отодвигает коробку, «боишься» — приподнимает уголок
    (тёплый свет), «ответ» — отпускает, пыль.
s09 участник (youth) один в белой комнате: солнечный квадрат ползёт («пятнадцать минут»), ёрзает, стучит пальцами, смотрит в
    потолок, вздыхает; «только» — глаза на кнопку; «кнопка тока» — дуга на кнопке, палец дёргается.
s12 Дима вечером: «Мозгу» — первая тучка из головы, «мыслями» — кружат, тыкаются, «неуютно» — ёжится и ёрзает; кот на краю столика,
    уши в сторону.
s13 «даже» — рука к кнопке, «боль» — разряд, волосы дыбом, тучки разлетаются; «лучше» — ошалелая полуулыбка, дымок; кот закрывает
    морду лапой.
s16 днём: телефон жужжит, «теперь» — рука к нему, «хватает» — замирает, улыбка, «телефон» — в ящик к кнопке, ящик закрыт, кот кивает.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. ВСЕ времена — из shots.json и voice/words.json (по индексу слова)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import cat as CAT  # noqa: E402
import hand_kot  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as P  # noqa: E402
import room as R  # noqa: E402
from lib import clamp, ease_in, ease_io, ease_out, line, svg  # noqa: E402

INK = lib.INK
WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SHOTS = {s["id"]: s for s in json.load(open(os.path.join(STORY, "shots.json")))["shots"]}


def ws(i):
    return WORDS[i]["start"]


def we(i):
    return WORDS[i]["end"]


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def win(t, a, b):
    return clamp((t - a) / max(1e-6, b - a))


def frame_svg(body, cx, cy, s, rot=0.0, over=""):
    return svg(f'<rect width="1080" height="1920" fill="#e9ebe8"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def shake(t, t0, amp, dur=.3, f=23.0):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0, 0.0
    e = (1 - u) ** 2 * amp
    return e * math.sin(t * f * 6.28), e * math.cos(t * f * 5.1)


def seated(who, x, y, s, target, reach, press, expr, t, parts, **kw):
    """Сидящий человек слоями (legs / torso / arm) для порядка комнаты C. Возвращает (dict слоёв, fig)."""
    out = {}
    fig = None
    for nm, ly in (("legs", ("legs",)), ("torso", ("pelvis", "arm_f", "body")), ("arm", ("arm_n",))):
        if nm not in parts:
            continue
        fig = people.press_at(who, x, y, s, target, reach=reach, press=press, expr=expr, t=t, layers=ly, **kw)
        out[nm] = fig["svg"]
    return out, fig


# ═══════════════════════════════ s05: призыв ═══════════════════════════════
S05 = SHOTS["s05"]
C05 = (790.0, R.LAB_TOP - 44.0, 1.43)          # кот: точка между задних лап, k
BOX05 = (585.0, R.LAB_TOP - 8.0, .9)          # коробка кнопкой к зрителю: центр дна, k
CNT05 = (560.0, 640.0, .44)                    # маленький счётчик на стене слева от головы кота, под «кот»
KOT05 = (462.0, 548.0, .7)                    # рукописное «кот»: x0, низ строки, size (мир)


def s05(t):
    lib.dyn_begin()
    L = R.lab_room(t, "cat_box")
    t_nap, t_kot, t_uz, t_sk, t_ty = ws(17), ws(18), ws(20), ws(21), ws(25)
    cx_, cy_, ck = C05
    # коробка: «узнаешь» — подвигается к камере (растёт и съезжает к краю столика)
    push = ease_io(win(t, t_uz, t_uz + .5))
    bx = BOX05[0] - 30 * push
    by = BOX05[1] + 34 * push
    bk = BOX05[2] * (1 + .42 * push)
    glow = .35 + .25 * math.sin(t * 5.0) + .3 * push
    box = P.shock_button(bx, by, bk, view="face", glow=clamp(glow), t=t, seed=5)
    btop = (bx + 92 * bk, by - 96 * bk)          # правый верх коробки — куда ложится лапа
    # кот: наклон вперёд при толчке (k растёт), взгляд
    lean = math.sin(math.pi * win(t, t_uz - .05, t_uz + .6))
    k = ck * (1 + .035 * lean)
    st = dict(look=(0.0, 0.05), tilt=-3 * lean, perk=.3 * lean)
    wr = win(t, t_kot, t_kot + .62)
    if 0 < wr < 1:                                # пока пишется «кот» — косится на перо
        st["look"] = (-.75 * math.sin(math.pi * min(1, wr * 1.3)), -.55 * math.sin(math.pi * min(1, wr * 1.3)))
    sk = win(t, t_sk, t_sk + .25)
    if t > t_sk and t < t_ty:
        st["look"] = (.8 * sk, -.55 * sk)
        st["turn"] = .25 * sk
    ty = ease_out(win(t, t_ty - .12, t_ty + .2))
    if ty > 0:
        st.update(people.cat_st("sly"))
        st["tilt"] = 11 * ty
        st["smug"] = .8 * ty
        st["look"] = (0.0, 0.0)
        st["turn"] = 0.0
    st["tail"] = 8 * math.sin(t * 2.2)
    # лапа (левая от зрителя): со столика — на коробку к «Напиши», держит при толчке, к «ты» — на зрителя подушечкой
    rest = (811.0, 1292.0)
    on_box = people.cat_world_paw(cx_, cy_, k, btop)
    reach = ease_out(win(t, SHOTS["s05"]["t0"] - .2, t_nap + .12), 2)
    tip = lerp2(rest, on_box, reach)
    front = False
    if ty > 0:
        tip = lerp2(tip, (806.0, 1140.0), ty)
        front = ty > .5
    tip = (tip[0], tip[1] - 4 * math.sin(t * 7) * (1 - reach))
    st["hide"] = ("l",)
    cat_body = CAT.draw(cx_, cy_, k, st, t)
    paw = people.cat_paw(cx_, cy_, k, st, t, tip, side="l", front=front, bend=-16, seed=5, body=False)
    # маленький счётчик: «сколько» — выскакивает, барабаны крутятся смазом (цифр нет)
    cnt = ""
    if t >= t_sk:
        cu = P.pop(t, t_sk, dur=.3)[1]
        cnt = P.drum_counter(CNT05[0], CNT05[1], CNT05[2] * cu, value=0, blank=True, t=t, seed=5)
    kot = hand_kot.kot(t, t_kot, .6, KOT05[0], KOT05[1], KOT05[2])
    body = "".join([L["bg"], L["chair_back"], L["table_top"], L["table_legs"], kot, cnt, cat_body, box, paw, L["light"]])
    # камера: лёгкий наезд, на толчке — ещё ближе к коробке
    u = win(t, S05["t0"] - .2, S05["t1"] + .2)
    s = 1.75 * (1 + .035 * u + .06 * push)
    cx = 760 - 40 * push + 10 * math.sin(t * .9)
    cy = 820 + 30 * push
    dx, dy = shake(t, t_uz + .42, 6)
    return frame_svg(body, cx + dx, cy + dy, s, .4 * math.sin(t * 1.1))


# ═══════════════════════════════ s06: тряпица на счётчике ═══════════════════════════════
S06 = SHOTS["s06"]
C06 = (870.0, R.LAB_TOP - 14.0, .9)
CN06 = (R.LAB_COUNTER[0], R.LAB_COUNTER[1], 1.0)


def s06(t):
    lib.dyn_begin()
    L = R.lab_room(t, "cat_wall")
    t_ne, t_nap, t_bo, t_ot = ws(26), ws(27), ws(29), ws(31)
    cx_, cy_, ck = C06
    # «боишься» — уголок приподнят (peek), «ответ» — падает обратно
    lift = ease_out(win(t, t_bo - .1, t_bo + .3))
    drop = ease_in(win(t, t_ot, t_ot + .16))
    peek = lift * (1 - drop)
    cnt = P.drum_counter(*CN06, value=190, cover=1.0, peek=peek, t=t, seed=6)
    corner = (CN06[0] + 160 * CN06[2], CN06[1] + 92 * CN06[2] - 40 * peek)
    # коробка на столике слева от кота: «напишешь» — кот отодвигает её лапой вбок (за край кадра влево)
    sh_u = ease_io(win(t, t_nap + .1, t_nap + .6))
    bx = 660 - 220 * sh_u
    box = P.shock_button(bx, R.LAB_TOP - 30, .8, view="face", glow=.25, t=t, seed=6)
    st = dict(look=(0.0, 0.0), tail=8 * math.sin(t * 2.0))
    # пожимает плечами на «Не»: обе лапы в стороны ладонями вверх (те же передние)
    shr = math.sin(math.pi * win(t, t_ne - .05, t_ne + .55)) if t < t_nap + .2 else 0.0
    paw_side = "l"
    tip = None
    front = False
    if shr > 0:
        st.update(paw=.5 * shr + .03, paw_l=.5 * shr + .03, paw_dx=95, paw_l_dx=95, tilt=-7 * shr, smug=.6 * shr, look=(0, 0))
    elif t < t_bo - .2:                                   # толкает коробку левой лапой
        pu = win(t, t_nap - .05, t_nap + .65)
        a = math.sin(math.pi * pu)
        edge = people.cat_world_paw(cx_, cy_, ck, (bx + 92, R.LAB_TOP - 62))
        tip = lerp2((811.0, 1292.0), edge, a)
        st["look"] = (-.6 * a, .3 * a)
    else:                                                 # правая лапа к уголку тряпицы
        paw_side = "r"
        k_ = ck
        cw = people.cat_world_paw(cx_, cy_, k_, corner)
        up = ease_out(win(t, t_bo - .25, t_bo + .2)) * (1 - ease_in(win(t, t_ot + .05, t_ot + .4)))
        tip = lerp2((861.0, 1292.0), cw, up)
        st.update(smug=.8 * up, look=(-.1 * up, 0.0), tilt=-8 * up, turn=-.15 * up, sy=1 + .2 * up, rot=3 * up)
        if t > t_ot:                                      # хитро щурится
            sq = ease_out(win(t, t_ot + .1, t_ot + .4))
            st.update(blink=.5 * sq, smile=1.0 if sq > .5 else 0.0, smug=.9)
    if tip is not None:
        cat_svg = people.cat_paw(cx_, cy_, ck, st, t, tip, side=paw_side, bend=-16 if paw_side == "l" else 48, seed=6)
    else:
        cat_svg = CAT.draw(cx_, cy_, ck, st, t)
    dust = ""
    if t > t_ot + .12:
        dust = P.dust_puff(CN06[0], CN06[1] + 90, 1.4, u=win(t, t_ot + .12, t_ot + .8), seed=6)
    body = "".join([L["bg"], cnt, L["chair_back"], L["table_top"], L["table_legs"], box, cat_svg, dust, L["light"]])
    u = win(t, S06["t0"] - .2, S06["t1"] + .2)
    s = 1.6 * (1 + .05 * u)
    cx = lerp(800, 760, ease_io(u))
    cy = 745
    dx, dy = shake(t, t_ot + .14, 9)
    return frame_svg(body, cx + dx, cy + dy, s, .3 * math.sin(t * 1.2))


# ═══════════════════════════════ s09: участник один ═══════════════════════════════
S09 = SHOTS["s09"]


def s09(t):
    lib.dyn_begin()
    t_15, t_min, t_only, t_btn, t_tok = ws(44), ws(45), ws(46), ws(49), ws(50)
    lp = ease_io(win(t, S09["t0"] - .2, t_min + .9))
    L = R.lab_room(t, "wide", light_patch=lp)
    x, y = R.LAB_SIT
    s = 1.0
    bx, by = R.LAB_BOX
    bk = .8
    arc = ease_out(win(t, t_btn, t_btn + .15)) * (.6 + .4 * math.sin(t * 31))
    box = P.shock_button(bx, by, bk, view="top", arc=arc, glow=.2 + .5 * win(t, t_btn, t_tok), t=t, seed=9)
    btn = P.shock_button_top(bx, by, bk, view="top")
    # ёрзает, пока ползёт свет; потом замирает и смотрит на кнопку
    calm = win(t, t_only - .1, t_only + .3)
    la, ha, shr = people.fidget(t, 1.7 * (1 - calm), seed=3)
    if t < t_min:
        ex = "bored75"
    elif t < t_min + .55:
        ex = "ceiling75"
    elif t < t_only:
        ex = "sigh75"
    else:
        ex = "eye_btn75"
    twitch = math.sin(math.pi * win(t, t_tok - .05, t_tok + .45))
    reach = .42 * twitch + .05 * math.sin(math.pi * win(t, t_btn, t_btn + .3))
    head_add = ha - (.25 if ex == "ceiling75" else 0.0) + .08 * calm
    far = people.knee_tap(t) if t < t_only else None
    lay, fig = seated("youth", x, y, s, btn, reach, 0.0, ex, t, ("legs", "torso", "arm"), lean_add=la, head_add=head_add, shrug=shr,
                      far_hand=far)
    # вздох — облачко выдоха
    sig = ""
    if ex == "sigh75":
        su = win(t, t_min + .55, t_only)
        hd = fig["head"]
        sig = P.smoke_rings(hd[0] + 90, hd[1] + 20, .5, u=1 - su, t=t, seed=9) if hasattr(P, "smoke_rings") else ""
    wire = P.cuff_wire(P.shock_button_wire(bx, by, bk, view="top"), fig["wrist"]["f"], sway=6, t=t, k=.8, seed=9, cuff_rot=20)
    body = "".join([L["bg"], L["chair_back"], L["table_top"], lay["legs"], L["table_legs"], L["chair_seat"], lay["torso"], box, wire,
                    lay["arm"], sig, L["light"]])
    u = win(t, S09["t0"] - .2, S09["t1"] + .2)
    sc = 1.08 * (1 + .1 * ease_io(u))
    tilt = ease_out(win(t, t_tok - .1, t_tok + .35))
    cx = 470 + 60 * tilt
    cy = lerp(930, 880, ease_io(u)) + 20 * tilt
    return frame_svg(body, cx, cy, sc * (1 + .03 * tilt), -1.2 * tilt)


# ═══════════════════════════════ s12, s13: Дима вечером с тучками ═══════════════════════════════
S12, S13 = SHOTS["s12"], SHOTS["s13"]
CAT12 = (790.0, R.HOME_WIN[3] + 2.0, .52)        # кот на подоконнике в углу окна


def _eve_scene(t, dima_kw, clouds, extra_top="", cat_svg="", head_fx=""):
    L = R.room_eve(t, "mid")
    x, y = R.LAB_SIT
    bx, by = R.LAB_BOX
    bk = .8
    box = P.shock_button(bx, by, bk, view="top", press=dima_kw.pop("press_btn", 0.0), arc=dima_kw.pop("arc", 0.0),
                         glow=dima_kw.pop("glow", .2), t=t, seed=12)
    btn = P.shock_button_top(bx, by, bk, view="top")
    lay, fig = seated("dima", x, y, 1.0, btn, dima_kw.pop("reach", 0.0), dima_kw.pop("press", 0.0), dima_kw.pop("expr"), t,
                      ("legs", "torso", "arm"), **dima_kw)
    wire = P.cuff_wire(P.shock_button_wire(bx, by, bk, view="top"), fig["wrist"]["f"], sway=5, t=t, k=.8, seed=12, cuff_rot=20)
    cl = clouds(fig) if clouds else ""
    body = "".join([L["bg"], L["chair_back"], L["table_top"], lay["legs"], L["table_legs"], L["chair_seat"], lay["torso"], box, wire,
                    extra_top, cat_svg, lay["arm"], head_fx(fig) if head_fx else "", cl, L["light"]])
    return body, fig, btn


def s12(t):
    lib.dyn_begin()
    t_mz, t_na, t_my, t_ne = ws(62), ws(63), ws(65), ws(67)
    n_u = win(t, t_mz, t_my + .2)
    n = 1 + int(round(4 * n_u)) if t >= t_mz else 0
    spin = .18 + .5 * win(t, t_na, t_ne)
    pk = .5 + .5 * math.sin(t * 6.0) if t > t_my else 0.0
    shr = ease_out(win(t, t_ne - .05, t_ne + .25))
    la, ha, _ = people.fidget(t, .4 + 1.2 * shr, seed=5)
    if t < t_mz:
        ex = "calm75"
    elif t < t_ne:
        ex = dict(people.EXPR["dima"]["shrink75"], look=(.1 + .2 * math.sin(t * 3), -.6))
    else:
        ex = "shrink75"
    hop = 6 * abs(math.sin(t * 9)) * shr       # сиденье «колется»

    def clouds(fig):
        if n <= 0:
            return ""
        hx, hy = fig["head"]
        pop = ease_out(win(t, t_mz, t_mz + .25))
        k = 1.45 * (.4 + .6 * pop)
        return P.thought_clouds(hx + 10, hy - 190, k, n, spin, t, scatter=0.0, poke=pk, seed=12)
    st = dict(people.cat_st("side_eye"), tail=6 * math.sin(t * 1.8))
    cat_svg = CAT.draw(CAT12[0], CAT12[1], CAT12[2], st, t)
    body, fig, _ = _eve_scene(t, dict(expr=ex, lean_add=la - .04 * shr, head_add=ha, shrug=.9 * shr, reach=0.0), clouds, cat_svg=cat_svg)
    body = f'<g transform="translate(0 {-hop:.2f})">{body}</g>' if hop > .1 else body
    u = win(t, S12["t0"] - .2, S12["t1"] + .2)
    s = 1.3 * (1 + .08 * ease_io(u))
    jit = 2.5 * win(t, t_na, t_ne) * math.sin(t * 41)
    return frame_svg(body, 480 + jit, 800 - 20 * ease_io(u), s, .3 * math.sin(t * 1.4))


def s13(t):
    lib.dyn_begin()
    t_ch, t_da, t_bol, t_kaj, t_lu = ws(68), ws(69), ws(70), ws(71), ws(72)
    reach = ease_io(win(t, t_ch - .25, t_bol - .02))
    press = ease_out(win(t, t_bol - .06, t_bol + .02)) * (1 - ease_in(win(t, t_bol + .35, t_bol + .6)))
    zap_u = math.exp(-max(0.0, t - t_bol) * 3.0) if t >= t_bol else 0.0
    hair = clamp(zap_u * 1.4)
    if t < t_bol:
        ex = dict(people.EXPR["dima"]["reach75"])
    elif t < t_kaj - .05:
        ex = people.zapped("zap75", hair, t, twitch=1.0)
    else:
        ex = people.zapped("dazed75", hair * .8, t, twitch=.6 * zap_u)
    reach_b = reach * (1 - .55 * ease_out(win(t, t_bol + .25, t_bol + .7)))
    scatter = ease_out(win(t, t_bol, t_bol + .7))

    def clouds(fig):
        if scatter >= 1:
            return ""
        hx, hy = fig["head"]
        return P.thought_clouds(hx + 10, hy - 210, 1.45, 5, .55, t, scatter=scatter, poke=0.0 if t > t_bol else .5 + .5 * math.sin(t * 6), seed=12)

    def head_fx(fig):
        o = ""
        if t >= t_bol:
            hd = fig["head"]
            o += P.smoke_rings(hd[0] - 10, hd[1] - 190, 1.7, u=clamp(1.2 - .4 * (t - t_bol)), t=t, seed=13)
            if zap_u > .25:          # молния бежит по руке: палец → запястье → локоть → плечо
                w, e = fig["wrist"]["n"], fig["elbow"]["n"]
                o += P.zap(fig["tip"], w, t, seed=13, u=zap_u, w=12) + P.zap(w, e, t, seed=14, u=zap_u, w=12)
                o += P.zap(e, (hd[0] - 20, hd[1] + 200), t, seed=15, u=zap_u, w=12)
                o += P.zap_net(fig["head"][0] - 140, fig["head"][1] + 150, fig["head"][0] + 160, fig["head"][1] + 520, t, seed=13, u=zap_u * .7)
        return o
    # кот на краю столика закрывает морду лапой на «боль»
    cp = ease_out(win(t, t_bol + .05, t_bol + .3))
    st = dict(tail=6 * math.sin(t * 1.8), look=(-.7, .2), perk=.6 * zap_u)
    if cp > 0:
        st.update(people.cat_st("facepaw"))
        tip = lerp2((861.0, 1292.0), (858.0, 1062.0), cp)
        cat_svg = people.cat_paw(CAT12[0], CAT12[1], CAT12[2], st, t, tip, side="r", front=True, seed=13)
    else:
        cat_svg = CAT.draw(CAT12[0], CAT12[1], CAT12[2], st, t)
    body, fig, btn = _eve_scene(t, dict(expr=ex, reach=reach_b, press=press, press_btn=press, glow=.3 + .6 * zap_u, arc=zap_u,
                                        lean_add=-.08 * zap_u), clouds, cat_svg=cat_svg, head_fx=head_fx)
    # вспышка на разряде
    over = ""
    if 0 < t - t_bol < .12:
        over = f'<rect width="1080" height="1920" fill="#fff6c8" opacity="{.45 * (1 - (t - t_bol) / .12):.3f}"/>'
    hit = math.exp(-max(0.0, t - t_bol) * 5) if t >= t_bol else 0.0
    out_ = ease_io(win(t, t_bol + .3, S13["t1"] + .2))
    s = 1.55 * (1 + .1 * hit - .06 * out_) * (1 + .02 * win(t, S13["t0"] - .2, t_bol))
    dx, dy = shake(t, t_bol, 14)
    cx = lerp(500, 540, reach) + dx
    cy = 760 + dy
    return frame_svg(body, cx, cy, s, 1.5 * hit * math.sin(t * 40), over)


# ═══════════════════════════════ s16: телефон в ящик ═══════════════════════════════
S16 = SHOTS["s16"]


def s16(t):
    lib.dyn_begin()
    t_tep, t_hv, t_tel = ws(86), ws(89), ws(90)
    dr_open = ease_out(win(t, t_tel - .3, t_tel + .05))
    dr_close = ease_in(win(t, t_tel + .62, t_tel + .9))
    drawer = dr_open * (1 - dr_close)
    L = R.room_day(t, "mid", drawer=drawer)
    x, y = R.LAB_SIT
    # телефон: жужжит экраном вниз на столике
    ph0 = (700.0, R.LAB_TOP - 32)
    buzz = 1.0 - win(t, t_hv - .1, t_hv + .1)
    bz = buzz * (3.5 * math.sin(t * 90) if (t * 2.5) % 1 < .6 else 0.0)
    reach = ease_io(win(t, t_tep, t_hv - .05))
    freeze = 1 if t >= t_hv and t < t_tel - .35 else 0
    hover = (ph0[0] - 40, ph0[1] - 70)
    # путь руки: к телефону (зависает над ним) → берёт → в ящик
    grab = ease_io(win(t, t_tel - .35, t_tel - .1))
    into = ease_io(win(t, t_tel - .1, t_tel + .45))
    ins = L.get("inside") or (R.HOME_DRAWER[0] - 150, R.LAB_TOP + 40, R.HOME_DRAWER[0] + 150, R.LAB_TOP + 90)
    dc = ((ins[0] + ins[2]) / 2, (ins[1] + ins[3]) / 2 + 10)
    target = lerp2(hover, ph0, grab)
    target = lerp2(target, (dc[0] + 40, dc[1] - 10), into)
    back = ease_io(win(t, t_tel + .45, t_tel + .9))
    rch = reach * (1 - back) if t < t_tel + .45 else (1 - back)
    if t < t_tel - .35:
        rch = reach
    if freeze:
        target = (hover[0] + 2 * math.sin(t * 13), hover[1])
    ex = "reach75" if t < t_hv else ("smile75" if t < t_tel + .45 else dict(people.EXPR["dima"]["smile75"], look=(.3, .2)))
    holding = t >= t_tel - .1 and t < t_tel + .45
    lay, fig = seated("dima", x, y, 1.0, target, rch, 0.0, ex, t, ("legs", "torso", "arm"),
                      head_add=-.08 * freeze, fdir=(1.0, .9))
    # телефон: на столе / в руке / в ящике
    if holding:
        tp, wq = fig["tip"], fig["wrist"]["n"]
        ph_svg = P.phone_flat(wq[0] + .7 * (tp[0] - wq[0]), wq[1] + .7 * (tp[1] - wq[1]) + 14, .5, rot=-10, face_down=True, seed=16)
        ph_layer = "hand"
    elif t >= t_tel + .45:
        ph_svg = P.phone_flat(dc[0] + 40, dc[1], .5, face_down=True, seed=16)
        ph_layer = "drawer"
    else:
        ph_svg = P.phone_flat(ph0[0] + bz, ph0[1] - abs(bz) * .5, .5, face_down=True, glow_=.6 * buzz * (abs(bz) > 0), seed=16)
        if buzz > 0 and abs(bz) > 0:
            for j, sx in enumerate((-1, 1)):
                ph_svg += line([(ph0[0] + sx * 50, ph0[1] - 20), (ph0[0] + sx * 66, ph0[1] - 34)], 4, INK, seed=1600 + j)
                ph_svg += line([(ph0[0] + sx * 54, ph0[1] - 4), (ph0[0] + sx * 74, ph0[1] - 8)], 4, INK, seed=1602 + j)
        ph_layer = "table"
    btn_in = ""
    if drawer > .02:
        btn_in = P.shock_button(dc[0] - 60, dc[1] + 14, .45, view="top", t=t, seed=16)
    # кот на столике справа: смотрит, на «телефон» одобрительно кивает
    nod = people.cat_nod(t, t_tel + .5, .4, .32)
    st = dict(people.cat_st("approve"), drop=nod, look=(-.6, .3), tail=8 * math.sin(t * 2.1)) if t > t_tel + .3 else \
        dict(look=(-.7, .25), tail=8 * math.sin(t * 2.1), perk=.5 * buzz)
    cat_svg = CAT.draw(860.0, R.LAB_TOP - 14.0, .7, st, t)
    o = [L["bg"], L["chair_back"], L["table_top"], btn_in, ph_svg if ph_layer == "drawer" else "", L.get("drawer_front", ""),
         lay["legs"], L["table_legs"], L["chair_seat"], lay["torso"], ph_svg if ph_layer == "table" else "", cat_svg, ph_svg if ph_layer == "hand" else "",
         lay["arm"], L["light"]]
    body = "".join(o)
    # хлёст на входе: камера влетает сбоку, дальше дрейф за рукой
    wu = ease_out(win(t, S16["t0"] - .2, S16["t0"] + .12), 3)
    s = 1.3 * (1 + .05 * ease_io(win(t, t_tep, t_tel + .4)))
    cx = 520 + 260 * (1 - wu) + 40 * reach - 30 * into
    cy = 860 + 30 * into
    return frame_svg(body, cx, cy, s, -2.5 * (1 - wu))


FN = {"s05": s05, "s06": s06, "s09": s09, "s12": s12, "s13": s13, "s16": s16}


def frame(sid, t):
    return FN[sid](t)
