"""Рилс 71 «два лагеря», группа D — стена: s11 (три дела в комнате, взгляд с одного на другое, нос в невидимое), s12 (мим у
невидимой стены, меловой контур у ладоней, кот проходит насквозь и оглядывается), s14 (ящик-дело щепотью в кубик), s15 (стена-сторож
с сонными глазами, кубик и Дима проскальзывают). frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Места — common/room.py,
люди и кот — common/people.py, предметы — common/props.py; помощники времени и камеры — ext_c/s71c.py. Букв и цифр нет."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "ext_c"))
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import INK, clamp, ease_in, ease_out, line  # noqa: E402,F401
from s71c import blinkv, bump, damp, ex, lerp, lerp2, set_ink, shake2, sm, whip_in, wt  # noqa: E402,F401

SC = 1.0
DX, DY = R.DR_DIMA


def three_tasks(t, glass_fill=0.0):
    """Три дела по местам комнаты: закрытый ноутбук на столе, полосатый носок на полу, графин и пустой стакан на тумбе."""
    lap = PR.laptop(R.DR_LAPTOP[0] + 20, R.DR_LAPTOP[1], .62, 0.0, "dark", t=t, seed=2, turn=.3)
    sock = PR.striped_sock(R.DR_SOCK[0], R.DR_SOCK[1], .9, -6, seed=2, flat=.8)
    jug = PR.jug(R.DR_JUG[0], R.DR_JUG[1], .8, fill=.7, seed=2)
    gl = PR.glass(R.DR_GLASS[0], R.DR_GLASS[1], .8, 0, fill=glass_fill, t=t, seed=2)
    return lap, sock, jug + gl


# ═════════════════════════ s11: три дела, взгляд, нос в невидимое ═════════════════════════
T11_A, T11_DIMA, T11_PER, T11_KAZH, T11_DEL, T11_BUD = (wt("а", 18.5), wt("дима", 18.5), wt("перед", 19.0), wt("каждым", 19.0),
                                                       wt("делом", 19.0), wt("будто", 20.0))     # 18.88 19.08 19.4 19.65 19.98 20.28


def s11(t):
    lib.dyn_begin()
    dr = R.day_room(t)
    lap, sock, stand_items = three_tasks(t)
    # шаг вперёд (вправо, к стене-невидимке): два шага на «А Дима», решительно
    # два коротких шага: ближняя нога, потом дальняя (стопа поднимается дугой и ставится впереди), таз едет за ними
    s1 = sm(t, T11_A - .02, T11_A + .26)
    s2 = sm(t, T11_DIMA + .02, T11_DIMA + .28)
    hx = DX - 140 + 75 * s1 + 75 * s2 + 20 * bump(t, T11_BUD - .1, .3)
    hy = DY - 14 * (bump(t, T11_A - .02, .28) + bump(t, T11_DIMA + .02, .26))
    base = people.stand_kw(DX - 140, DY, SC, spread=70)["feet"]
    (an, pn), (af, pf) = base["n"], base["f"]
    feet = {"n": ((an[0] + 150 * s1, an[1] - 70 * bump(t, T11_A - .02, .28)), 0.0),
            "f": ((af[0] + 150 * s2, af[1] - 70 * bump(t, T11_DIMA + .02, .26)), 0.0)}
    walk = {"feet": feet}
    hip = (hx, hy)
    # взгляд: ноутбук (слева внизу) → носок (пол) → стакан (справа) — голова поворачивается через промежуточные кадры
    look = (lerp(-.8, .2, sm(t, T11_PER, T11_KAZH + .1)), lerp(.5, .9, sm(t, T11_PER, T11_KAZH + .1)))
    look = (lerp(look[0], .9, sm(t, T11_DEL - .05, T11_DEL + .15)), lerp(look[1], .2, sm(t, T11_DEL - .05, T11_DEL + .15)))
    head = -.12 * sm(t, T11_PER, T11_KAZH) + .2 * sm(t, T11_KAZH, T11_DEL) + .06 * sm(t, T11_DEL, T11_DEL + .2)
    hit = bump(t, T11_BUD, .3)
    if t < T11_BUD - .02:
        e = ex("resolve", bags=False, look=look) if "resolve" in people.EXPR["dima"] else ex("focus", bags=False, look=look)
        pose, u_pose = None, None
        arms = {"f": ("ang", .15 + .2 * math.sin(t * 7), .2), "n": ("ang", -.05 - .2 * math.sin(t * 7), .25)}
        fig = people.dima(hip[0], hip[1], SC, e, None, feet=walk["feet"], arms=arms, head_add=head, lean_add=.05)
    else:
        e = ex("squish")
        fig = people.dima(hip[0] - 30 * hit, hip[1], SC, e, "nose_wall", feet=walk["feet"], head_add=-.12 * hit, lean_add=-.08 * hit)
        del pn, pf
    # «будто»: штрихи удара у носа
    hits = ""
    hu = (t - T11_BUD) / .22
    if 0 < hu < 1:
        hx, hy = fig["head"]
        for j, ang in enumerate((-40, -10, 20)):
            aa = math.radians(ang)
            r0 = 190 + 50 * hu
            hits += line([(hx + math.cos(aa) * r0, hy + math.sin(aa) * r0), (hx + math.cos(aa) * (r0 + 60), hy + math.sin(aa) * (r0 + 60))],
                         8 * (1 - hu) + 1.5, INK, taper=.5, wmin=.2, seed=6300 + j)
    world = [dr["bg"], dr["desk"], lap, dr["stand"], stand_items, sock, fig["svg"], hits]
    cx0, cy0, s0 = R.CAM_ROOM
    sx1, sy1 = shake2(t, T11_BUD + .01, 12)
    wx, wr = whip_in(t, 18.6)
    z = sm(t, 18.6, 20.7)
    cx = cx0 + 60 * z - sx1 + wx
    cy = cy0 + 40 - 30 * z - sy1
    s = s0 * (1.02 + .1 * z)
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s, wr)}">{"".join(world)}</g>')


# ═════════════════════════ s12: мим у стены, кот проходит насквозь ═════════════════════════
T12_ST, T12_U, T12_STE, T12_KOT, T12_NIK, T12_KR, T12_NV = (wt("стоит", 20.4), wt("у", 20.8), wt("стены", 20.8), wt("которую", 21.0),
                                                            wt("никто", 21.0), wt("кроме", 21.5), wt("видит", 22.0))
WALL12_X = DX + 300.0          # плоскость невидимой стены (Дима лицом вправо)


def s12(t):
    lib.dyn_begin()
    dr = R.day_room(t)
    lap, sock, stand_items = three_tasks(t)
    hip = (DX - 20, DY)
    feet = people.stand_kw(hip[0], hip[1], SC, spread=90)["feet"]
    slide = sm(t, T12_KR - .05, T12_KR + .35)
    sweep = math.sin(math.pi * clamp((t - T12_KR) / .9))
    if t < T12_ST:
        fig = people.dima(hip[0], hip[1], SC, ex("puzzled", look=(.8, 0)), "rest", u_pose=("mime_wall_lo", sm(t, 20.3, T12_ST)), feet=feet)
    else:
        e = ex("puzzled", look=(.8, -.2 + .3 * sweep), lid=.9)
        if t > T12_NV - .1:
            e = ex("plea", look=(.6, .4))
        fig = people.dima(hip[0], hip[1], SC, e, "mime_wall_lo", u_pose=("mime_wall", .9 * sweep), feet=feet,
                          lean_add=.04 * math.sin(t * 3), head_add=.05 * math.sin(t * 2.2))
    # меловой контур кирпичей проявляется у ладоней на «у стены» и гаснет; ещё раз слабее, когда ведёт по стене
    wr = fig["wrist"]
    pu = bump(t, T12_U - .05, .55) + .6 * bump(t, T12_KR, .6)
    masks = [(wr["n"][0] + 40, wr["n"][1] - 60, 330), (wr["f"][0] + 40, wr["f"][1] - 60, 300)]
    chalk = (PR.chalk_wall(WALL12_X - 40, 120, WALL12_X + 300, R.FL - 10, u=pu, masks=masks, t=t, seed=3, col="#5d7189", sh="#3f4d5c", wline=7.0)
             if pu > .01 else "")
    # кот идёт по полу справа налево сквозь стену, не замечая; на «видит» оборачивается через плечо
    cu = clamp((t - (T12_KOT - .35)) / (T12_NV - T12_KOT + .1))
    cx_ = lerp(1250, 740, cu)
    cst = dict(look=(-.8, .1), tail=12 * math.sin(t * 4))
    if t > T12_NV - .15:
        cst.update(turn=.9 * sm(t, T12_NV - .15, T12_NV + .1), look=(.9, -.1), tilt=-10 * sm(t, T12_NV - .15, T12_NV + .1))
        cat = people.cat_svg(cx_, R.FL - 6, 1.05, cst, t)
    else:
        cat = people.cat_walk(cx_, R.FL - 6, 1.05, t, cst, period=.45)
    world = [dr["bg"], dr["desk"], lap, dr["stand"], stand_items, sock, chalk, fig["svg"], cat]
    cx0, cy0, s0 = R.CAM_ROOM_NEAR
    z = sm(t, 20.3, 23.3)
    cx = cx0 + 40 + 120 * z + 6 * math.sin(t * 1.3)
    cy = 1080 + 10 * math.sin(t * 1.7)
    s = 1.12 * (1 + .015 * math.sin(t * 2.0))
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s, .3 * math.sin(t * .9))}">{"".join(world)}</g>')


# ═════════════════════════ графика на бумаге (s14, s15) ═════════════════════════
CHALK, CHALK_SH = "#5d7189", "#3f4d5c"      # та же меловая стена, что у ладоней в s12


def paper_bg():
    d = "".join(f"M-1400 {i * 64}H3000" for i in range(-20, 50)) + "".join(f"M{i * 64} -1400V3200" for i in range(-24, 48))
    return f'<path d="M-1400 -1400H3000V3200H-1400Z" fill="{PR.C_PAGE}"/><path d="{d}" stroke="#E3DECF" stroke-width="2" fill="none"/>'


def ground(y, x0=-1400, x1=3000, seed=0):
    return line([(x0, y), (x1, y + 4)], 6, INK, taper=.05, wmin=.9, seed=6400 + seed, op=.85)


# ═════════════════════════ s14: ящик-дело щепотью в кубик ═════════════════════════
T14_DEL, T14_PER, T14_SH, T14_TAK, T14_MAL = (wt("делать", 24.8), wt("первый", 24.8), wt("шаг", 24.8), wt("таким", 25.5),
                                             wt("маленьким", 25.5))      # 25.01 25.31 25.58 25.81 26.11
D14 = (300.0, 1560.0)
D14_SC = 1.5
CRATE14 = (790.0, 1330.0)
CRATE14_K = 1.55


def s14(t):
    lib.dyn_begin()
    raise_u = sm(t, T14_DEL - .05, T14_SH + .1)
    e = ex("focus_smile", look=(.8, -.3 + .2 * raise_u))
    if t < T14_DEL:
        e = ex("unsure", bags=False, look=(.8, -.6), brows="worry")
    if t > T14_MAL + .15:
        e = ex("sly", look=(.6, -.2))
    e["closed"] = blinkv(t, [24.85])
    fig = people.dima(D14[0], D14[1], D14_SC, e, "rest", u_pose=("pinch", raise_u), lean_add=.03 * math.sin(t * 2.4),
                      head_add=.04 * math.sin(t * 1.9))
    wr = fig["wrist"]["n"]
    tip = (wr[0] + 58 * D14_SC, wr[1] - 92 * D14_SC)      # между большим и указательным
    # ящик: стоит и чуть «дышит» (верёвка натянута), на «маленьким» сжимается и прыгает в щепоть
    shr = sm(t, T14_TAK - .02, T14_MAL + .25)
    fly = sm(t, T14_TAK + .05, T14_MAL + .3)
    base = (CRATE14[0], CRATE14[1] + 4 * math.sin(t * 6))
    pos = lerp2(base, (tip[0], tip[1] + 40), fly)
    pos = (pos[0], pos[1] - 120 * math.sin(math.pi * fly))
    crate = PR.task_crate(pos[0], pos[1], CRATE14_K * (1 - .55 * fly), shrink=shr, rot=-6 * math.sin(math.pi * shr) + 2 * math.sin(t * 5), seed=1)
    # пока щепоть пустая — пальцы чуть «примериваются»; после — кубик зажат, лучики-искорки
    spark = ""
    su = (t - (T14_MAL + .28)) / .35
    if 0 < su < 1:
        for j, ang in enumerate((-120, -60, 0, 60)):
            aa = math.radians(ang)
            r0 = 50 + 40 * su
            spark += line([(tip[0] + math.cos(aa) * r0, tip[1] + math.sin(aa) * r0), (tip[0] + math.cos(aa) * (r0 + 34), tip[1] + math.sin(aa) * (r0 + 34))],
                          6 * (1 - su) + 1.5, INK, taper=.5, wmin=.2, seed=6500 + j)
    world = [paper_bg(), crate if fly < .9 else "", fig["svg"], crate if fly >= .9 else "", spark]
    wx, wr_ = whip_in(t, 24.75)
    punch = sm(t, T14_MAL - .03, T14_MAL + .12)
    cx = lerp(560, tip[0], .4 * punch) + 30 * sm(t, 24.75, T14_MAL) + wx
    cy = lerp(980, tip[1] + 60, .6 * punch)
    s = 1.0 * (1 + .06 * sm(t, 24.75, T14_MAL) + .3 * punch)
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s, wr_ + .4 * math.sin(t * 1.5))}">{"".join(world)}</g>')


# ═════════════════════════ s15: стена-сторож, кубик и Дима проскальзывают ═════════════════════════
T15_STENA, T15_EGO, T15_ZAM = wt("стена", 26.5), wt("его", 26.9), wt("замечает", 27.0)     # 26.69 27.02 27.32
W15 = (320.0, 120.0, 900.0, 1290.0)       # стена: x0, y0, x1, пол
ARCH15 = (540.0, 700.0, 1290.0, 190.0)    # проход у основания: центр x, верх, низ, полуширина
D15_SC = .78


def s15(t):
    lib.dyn_begin()
    x0, y0, x1, fl = W15
    ax, atop, abot, aw = ARCH15
    eyes = lerp(.35, .85, sm(t, T15_STENA - .05, T15_STENA + .2))
    blink = blinkv(t, [T15_ZAM + .1, 28.1], .45)
    wall = PR.chalk_wall(x0, y0, x1, fl, u=1.0, eyes=eyes, blink=blink, eye_at=((x0 + x1) / 2, y0 + 170), t=t, seed=5, col=CHALK, sh=CHALK_SH,
                         wline=6.0)
    # проход-щель: бумага закрывает кирпичи, меловая арка пунктиром
    arch = [(ax - aw, abot)] + [(ax - aw * math.cos(math.pi * q / 12), atop + (abot - atop) * .35 * (1 - math.sin(math.pi * q / 12)))
                                 for q in range(13)] + [(ax + aw, abot)]
    hole = lib.blob(arch, PR.C_PAGE) + PR.dash_path(arch, 1.0, w=7.0, col=CHALK, seed=5)
    # кубик катится по полу и ныряет в проход
    cu = clamp((t - (T15_EGO - .45)) / .75)
    cxu = lerp(-80, 1150, ease_in(cu, 1.2))
    cube = PR.task_crate(cxu, fl, 1.0, shrink=1.0, rot=360 * cu * 1.4, seed=1)
    # Дима крадётся на цыпочках пригнувшись, ныряет в проход, по ту сторону оглядывается и беззвучно смеётся
    du = clamp((t - 26.42) / (T15_ZAM + .35 - 26.42))
    hx = lerp(-260, 1080, du)
    hy = fl - 520 * D15_SC * people.HEIGHT["dima"] - 20
    ph = (t - 26.42) * 2.4
    if du < 1:
        e = ex("sly", look=(.3, -.9), lid=.5)
        fig = people.dima(hx, hy + 30 * D15_SC * abs(math.sin(math.pi * ph)), D15_SC, e, "sneak", feet=people.tiptoe_kw(hx, hy, D15_SC, ph)["feet"])
    else:
        e = ex("silent_laugh")
        e["hair"] = 5 * math.sin(t * 14)
        fig = people.dima(hx, hy + 8 * math.sin(t * 22), D15_SC, e, "sneak", u_pose=("rest", .6), flip=True,
                          feet=people.stand_kw(hx, hy + 60 * D15_SC, D15_SC, spread=80)["feet"], lean_add=.06 * math.sin(t * 20))
    world = [paper_bg(), ground(fl), wall, hole, cube, fig["svg"]]
    cx = lerp(380, 820, sm(t, 26.42, 28.4)) + 6 * math.sin(t * 1.6)
    cy = 820 + 8 * math.sin(t * 1.2)
    s = 1.0
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s, .3 * math.sin(t * 1.1))}">{"".join(world)}</g>')


def frame(sid, t):
    return {"s11": s11, "s12": s12, "s14": s14, "s15": s15}[sid](t)
