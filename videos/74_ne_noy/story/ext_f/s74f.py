"""Рилс 74 «Прекрати ныть», группа F — телефон.
s07 (7.85–9.15): через плечо Димы ночью (свет только от экрана): черновик из двух серых волнистых строк, курсор мигает, пылинка на
    значке; «черновик» (7.90–8.40) строки подсвечиваются по очереди; «письма» (8.43) большой палец зависает над стрелкой и дрожит,
    но не нажимает.
s13 (18.55–20.05): средний план, тёплая лампа: Дима за столом с телефоном, рядом кот, кусочек крекера и закрытая банка. С кадра 0 кот
    подталкивает кусочек носом; «оказывается» (18.59) Дима съедает кусочек и печатает одно слово; «что мы» (19.14) кот кладёт лапу на
    запястье; «можем» (19.42) крышка банки сама слетает, Дима поднимает брови и улыбается краешком рта.
s14 (20.05–21.70, хлёст вниз): через плечо в тёплом свете; палец идёт к стрелке, «отправил» (20.69) нажимает — конверт улетает,
    «письмо» (21.25) галочка, экран вспыхивает тёплым, пылинка слетает.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Комната — common/room.py, Дима — common/people.py, кот — common/cat.py,
предметы — common/props.py; здесь только хореография и камера. Надписей, букв и цифр нет."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
sys.path.insert(0, os.path.join(STORY, "ext_e"))
import cat as CAT  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from h74 import blinks, bump, flame_world, lerp, lerp2, set_ink, shake, sm, wt  # noqa: E402
from lib import blob, clamp, ease_in, ease_out, ellipse_pts, line  # noqa: E402

FRAMES = {}


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')


def whip_v(g, t, t_in, amp=360.0, blur=34.0, dur=.22):
    """Хлёст вниз: кадр приезжает сверху с размытием по вертикали."""
    e = ease_out(clamp((t - t_in) / dur), 2)
    dy, b = -amp * (1 - e), blur * (1 - e)
    g = f'<g transform="translate(0 {dy:.1f})">{g}</g>'
    if b > .5:
        fid = lib.uid("wv")
        lib.DEFS.append(f'<filter id="{fid}" x="-5%" y="-20%" width="110%" height="140%"><feGaussianBlur stdDeviation="0 {b:.1f}"/></filter>')
        g = f'<g filter="url(#{fid})">{g}</g>'
    return g


# ═════════════════════════ через плечо: общий для s07 и s14 ═════════════════════════
PH_K = 1.0
SH_PHONE = (690.0, 1090.0)     # телефон правее затылка: обе руки видны
SH_DIMA = (215.0, 1620.0)      # основание шеи Димы (голова у левого нижнего края)
SH_K = 1.75


def line_glow(pc, rot, k, which, u):
    """Подсветка строки черновика (0 — первая, 1 — вторая) в координатах телефона phone_draft."""
    if u <= .01:
        return ""
    x0, x1, yy = ((-112, 112, -60), (-112, 48, 0))[which]
    g = blob(lib.rrect(x0, yy - 20, x1, yy + 20, 14), "#9CC8F2", .45 * u)
    return f'<g transform="translate({pc[0]:.2f} {pc[1]:.2f}) rotate({rot:.2f}) scale({k:.5f})">{g}</g>'


def shoulder_shot(t, light, ph, thumb_u, press, jit, extra_top="", tilt=0.0, sway=0.0):
    """Кадр через плечо: комната (night_desk shoulder), Дима со спины с телефоном в обеих руках. ph — kwargs для phone_draft."""
    sc = R.night_desk(t, light, "shoulder")
    pcx, pcy = SH_PHONE
    rot = -5 + 1.6 * math.sin(t * 1.3) + sway
    pc = (pcx + 6 * math.sin(t * 1.1), pcy + 5 * math.sin(t * 1.7 + .4))
    phone = PR.phone_draft(pc[0], pc[1], PH_K, rot, **ph) + extra_top(pc, rot) if callable(extra_top) else PR.phone_draft(pc[0], pc[1], PH_K, rot, **ph)
    dx, dy = SH_DIMA
    lu = 1.0 if light == "lamp" else 0.0
    dm = people.dima_over_shoulder(dx, dy, SH_K, pc, PH_K, rot, phone, thumb_u=thumb_u, press=press, jit=jit, t=t, tilt=tilt,
                                   shade=.75 - .45 * lu)
    glow_ = PR.glow(pc[0], pc[1], 420, .28 if lu < .5 else .16, "#DDE8FF" if lu < .5 else "#FFE7B8", ry=520)
    world = [sc["bg"], sc["desk"], sc["pool"], sc["lamp"], sc["dark"], glow_, dm["svg"]]
    return "".join(world), pc, dm


# ═════════════════════════ s07: черновик через плечо, палец дрожит над стрелкой ═════════════════════════
T_A07 = 7.85
T_CHER, T_PIS = wt(17), wt(18)                  # 7.90, 8.43


def s07(t):
    hl1 = bump(t, T_CHER - .02, .3)
    hl2 = bump(t, T_CHER + .22, .3)
    reach = sm(t, T_CHER + .2, T_PIS + .05)
    hover = sm(t, T_PIS - .05, T_PIS + .1)
    jit = hover * (3.2 * math.sin(t * 47) + 2.0 * math.sin(t * 31 + 1))
    ph = dict(glow=1.0, cursor_t=t * 1.7, hl=.7 * hover, dust_u=1.0)

    def top(pc, rot):
        return line_glow(pc, rot, PH_K, 0, hl1) + line_glow(pc, rot, PH_K, 1, hl2)
    body, pc, dm = shoulder_shot(t, "screen", ph, thumb_u=.15 + .85 * reach, press=0.0, jit=jit, extra_top=top, tilt=-2 + 1.2 * math.sin(t * 1.4))
    # камера: наезд 6 % к экрану, покачивание вместе с руками
    u = sm(t, T_A07 - .2, 9.35)
    s = 1.0 + .06 * u
    cx = lerp(560, pc[0] - 40, u) + 3 * math.sin(t * 1.3)
    cy = lerp(1060, pc[1] + 20, u) + 3 * math.sin(t * 1.9)
    set_ink(s)
    return f'<g transform="{lib.cam(cx, cy, s, .4 * math.sin(t * 1.2))}">{body}</g>', "#0a0d18"


FRAMES["s07"] = s07


# ═════════════════════════ s14: отправил — конверт улетает, галочка ═════════════════════════
T_A14 = 20.05
T_OTP, T_PISMO = wt(53), wt(55)                # 20.69, 21.25


def dust_off(pc, rot, k, t):
    """Пылинка слетает с угла экрана после галочки."""
    q = clamp((t - (T_PISMO + .1)) / .55)
    if q <= 0 or q >= 1:
        return ""
    a = math.radians(rot)
    lx, ly = 120 + 160 * q, -250 - 120 * q + 60 * q * q
    x = pc[0] + (lx * math.cos(a) - ly * math.sin(a)) * k
    y = pc[1] + (lx * math.sin(a) + ly * math.cos(a)) * k
    return blob(ellipse_pts(x + 8 * math.sin(q * 11), y, 5, 4, 8), "#C9BFAE", 1 - q)


def trail(pc, rot, k, su):
    """Шлейф улетающего конверта (тот же путь, что у конверта в props.phone_draft), внутри экрана."""
    if su <= .02 or su >= .95:
        return ""
    fly = ease_in(su, 2)
    ex, ey = -60 + 260 * fly, -160 - 340 * fly
    o = []
    for j, off in enumerate((-18, 0, 18)):
        p0 = (ex - 80 * fly * .9 + off * .6, ey + 100 * fly + off)
        p1 = (ex - 20, ey + 30 + off * .5)
        o.append(line([p0, p1], 5, "#9CC8F2", taper=.7, wmin=.1, seed=7480 + j, op=.8 * (1 - su)))
    cid = lib.clip_rect(-134, -284, 268, 568, 30)
    return f'<g transform="translate({pc[0]:.2f} {pc[1]:.2f}) rotate({rot:.2f}) scale({k:.5f})"><g clip-path="url(#{cid})">{"".join(o)}</g></g>'


def s14(t):
    go = sm(t, T_A14 - .2, T_OTP - .04)
    press = bump(t, T_OTP - .02, .22) ** .6 if t < T_OTP + .2 else 0.0
    send = clamp((t - (T_OTP - .02)) / .1) * (1 - clamp((t - (T_OTP + .18)) / .15))
    sent = clamp((t - (T_OTP + .04)) / .4)
    tick = clamp((t - (T_PISMO - .02)) / .35)
    dust = 1 - sm(t, T_PISMO + .05, T_PISMO + .35)
    ph = dict(glow=1.0, cursor_t=t * 1.7 if sent <= 0 else None, hl=.5 * go * (1 - sent), send_u=send, sent_u=sent, tick_u=tick, dust_u=dust)
    flash = bump(t, T_PISMO, .45)

    def top(pc, rot):
        o = dust_off(pc, rot, PH_K, t) + trail(pc, rot, PH_K, sent)
        if flash > .01:
            o += PR.glow(pc[0], pc[1], 300, .7 * flash, "#FFD98A", ry=420)
        return o
    lift = ease_out(clamp((t - (T_OTP + .3)) / .3))      # палец уходит с экрана после нажатия
    body, pc, dm = shoulder_shot(t, "lamp", ph, thumb_u=lerp(.25 + .75 * go, .3, lift), press=press, jit=0.0, extra_top=top,
                                 tilt=1.5 * math.sin(t * 1.3) + 3 * sm(t, T_PISMO, T_PISMO + .4))
    # камера: наезд 5 % к экрану, на «отправил» короткий толчок вверх вслед за конвертом
    u = sm(t, T_A14 - .2, 21.9)
    kick = bump(t, T_OTP + .03, .35)
    s = 1.0 + .05 * u + .02 * kick
    cx = lerp(560, pc[0] - 40, u) + 3 * math.sin(t * 1.3)
    cy = lerp(1060, pc[1] + 20, u) - 30 * kick
    set_ink(s)
    g = f'<g transform="{lib.cam(cx, cy, s, .3 * math.sin(t * 1.1))}">{body}</g>'
    warm = '<rect width="1080" height="1920" fill="#ff9a40" opacity=".14" style="mix-blend-mode:soft-light"/>'
    return whip_v(g + warm, t, T_A14), "#24170f"


FRAMES["s14"] = s14


# ═════════════════════════ s13: кусочек, одно слово, крышка банки слетает сама ═════════════════════════
T_A13 = 18.55
T_OKAZ, T_CHTO, T_MOZH = wt(47), wt(48), wt(50)     # 18.59, 19.14, 19.42
DS13 = .92
CAT13 = (800.0, R.DESK_TOP - 52)
CAT13_K = .85
JAR13 = (982.0, R.DESK_TOP - 62)
JAR13_K = .74
BIT_Y = R.DESK_TOP - 30
T_PICK, T_MOUTH, T_BACK = T_OKAZ + .03, T_OKAZ + .25, T_OKAZ + .45     # берёт кусочек, у рта, руки снова на телефоне


def bit_x(t):
    """Кусочек крекера: кот толкает носом двумя толчками к руке Димы."""
    x = 718.0
    for t0, dx in ((18.30, -22.0), (18.46, -26.0)):
        x += dx * ease_out(clamp((t - t0) / .12), 2)
    return x


def cat13(t):
    st = dict(people.CAT_ST["warm74"])
    nudge = bump(t, 18.27, .2) + bump(t, 18.43, .2)
    low = 1 - sm(t, 18.58, 18.8)                    # голова опущена к кусочку, затем поднимается — смотрит на Диму
    st.update(turn=-.6, look=(lerp(-.6, -.85, 1 - low), lerp(.6, -.1, 1 - low)), drop=.85 * low + .2 * nudge, rot=-13 * low - 6 * nudge,
              tilt=-6 * low + 3 * math.sin(t * 1.7), tail=-6 + 7 * math.sin(t * 2.2), ear=2 * math.sin(t * 3.3),
              blink=blinks(t, (19.55,)), flame_e=1.1 + .7 * bump(t, T_MOZH, .5))
    return st


def s13(t):
    nd = R.night_desk(t, "lamp", "mid")
    hx, hy = nd["sit"]
    fkw = dict(people.sit_kw(hx, hy, DS13))
    bx = bit_x(t)
    # руки: телефон у груди → ближняя кисть берёт кусочек → ко рту → обратно к телефону, печатает одно слово
    pick = sm(t, T_PICK - .1, T_PICK + .08)
    tomouth = sm(t, T_PICK + .08, T_MOUTH)
    back = sm(t, T_MOUTH + .1, T_BACK)
    eat_phase = pick > 0 and back < 1
    mouth_kw = people.pose_kw("eat74", hx, hy, DS13)
    Wm = mouth_kw["arms"]["n"][1]
    Wbit = (bx - 34, BIT_Y - 18)
    chest_kw = people.pose_kw("phone_chest74", hx, hy, DS13)
    Wc = chest_kw["arms"]["n"][1]
    Wn = lerp2(lerp2(lerp2(Wc, Wbit, pick), Wm, tomouth), Wc, back)
    # мимика
    if t < T_PICK + .05:
        e = dict(people.EXPR["dima"]["screen74"], look=(.6, .6), bags=False)
    elif t < T_BACK + .1:
        e = dict(people.EXPR["dima"]["chew74"], bags=False)
        e["mouth"] = "flat" if t < T_MOUTH else ("o" if int(t * 12) % 2 else "flat")
        e["open"] = .12
    elif t < T_MOZH:
        e = dict(people.EXPR["dima"]["screen74"], look=(.55, .55), lid=.62, bags=False)
    else:
        e = dict(people.EXPR["dima"]["type_up74"])
        e["look"] = (.75, .3) if t < T_MOZH + .35 else (.5, .5)
    e["closed"] = blinks(t, (18.42, 19.9))
    lean = .02 * math.sin(t * 2.1) + .05 * sm(t, T_MOZH, T_MOZH + .25)
    head = .02 * math.sin(t * 1.6) + .06 * tomouth * (1 - back) - .05 * sm(t, T_MOZH, T_MOZH + .3)
    legs = people.dima(hx, hy, DS13, e, "phone_chest74", layers=("legs",), **fkw)["svg"]
    if eat_phase:
        u = tomouth * (1 - back)
        arms = {"n": ("ik", Wn, -1)}
        hands = {"n": {"dir": lerp2((1, .4), (.3, -1), u), "curl": (.55, .6, .7, .75), "thumb": .7}}
        body = people.dima(hx, hy, DS13, e, "phone_chest74", u_pose=("eat74", u), layers=("pelvis", "arm_f", "body"), arms=arms, hands=hands,
                           lean_add=lean, head_add=head, **fkw)
        arm = people.dima(hx, hy, DS13, e, "phone_chest74", u_pose=("eat74", u), layers=("arm_n",), arms=arms, hands=hands, lean_add=lean,
                          head_add=head, **fkw)
        pf = people.hand_pos(body, "f", 55)
        phone = people.mobilnik(pf[0] + 18 * DS13, pf[1] - 30 * DS13, 1.45 * DS13, -12, seed=952)
        body_svg = body["svg"] + phone
        arm_svg = arm["svg"]
        wrist_n = arm["wrist"]["n"]
        bit_hand = people.hand_pos(arm, "n", 62) if pick > .6 and t < T_MOUTH + .02 else None
    else:
        typing = sm(t, T_BACK - .05, T_BACK + .05) * (1 - sm(t, T_CHTO + .22, T_CHTO + .3))
        fig = people.dima_phone(hx, hy, DS13, e, "phone_chest74", thumb=typing, t=t, layers_body=("pelvis", "arm_f", "body"), lean_add=lean,
                                head_add=head, **fkw)
        body_svg, arm_svg = fig["svg"], ""
        wrist_n = fig["wrist"]["n"]
        bit_hand = None
    # кусочек крекера: на столе → в руке → съеден
    if pick < .6:
        bit = PR.cracker_bit(bx, BIT_Y, .7, rot=-20 + 40 * (bx - 718) / 48, seed=3)
    elif bit_hand is not None:
        bit = PR.cracker_bit(bit_hand[0], bit_hand[1], .7, rot=20, seed=3)
    else:
        bit = ""
    crumbs = ""
    if T_MOUTH < t < T_MOUTH + .35:
        hd = people.dima(hx, hy, DS13, e, "phone_chest74", layers=("legs",), **fkw)["head"]
        q = (t - T_MOUTH) / .35
        for j in range(4):
            crumbs += blob(ellipse_pts(hd[0] + 70 + 14 * j, hd[1] + 90 + 140 * q * q + 10 * j, 4, 3, 6), PR.C_CRACKER, 1 - q)
    # кот: толкает кусочек носом, «что мы» кладёт левую (от зрителя) переднюю лапу на ближнее запястье, вторая на столе
    st = cat13(t)
    cx, cy = CAT13
    reach = sm(t, T_CHTO - .02, T_CHTO + .2) * (1 - sm(t, 19.85, 20.15))
    if reach > .01:
        tgt = (wrist_n[0] + 8, wrist_n[1] - 10)
        pw = max(.05, (cy - tgt[1]) / (150 * CAT13_K))
        dxw = max(10.0, ((cx - tgt[0]) / CAT13_K - 25) / (1.6 * pw))
        st.update(paw_l=pw * reach, paw_l_dx=dxw, turn=lerp(st["turn"], -.85, reach), look=(-.9, lerp(st["look"][1], .2, reach)))
    cat = CAT.draw(cx, cy, CAT13_K, st, t)
    if reach > .05:
        sh_ = (cx + (-25 + 4) * CAT13_K, cy + (1238 - CAT.CBOT) * CAT13_K)
        tip_ = people.cat_paw_tip(cx, cy, CAT13_K, st, side="l")
        cat += people.cat_forearm(sh_, tip_, k=.6 * CAT13_K, seed=13)
        cat += blob(ellipse_pts(sh_[0] + 6 * CAT13_K, sh_[1], 30 * CAT13_K, 26 * CAT13_K, 14), CAT.CAT)
    flx, fly = flame_world(cx, cy, CAT13_K, st["tail"])
    cat = blob(ellipse_pts(cx, cy + 4, 130 * CAT13_K, 12, 16), "#2a1a12", .25) + cat + PR.glow(flx, fly - 30, 70, .3 + .3 * bump(t, T_MOZH, .5), "#ffb347")
    # банка: закрыта, на «можем» крышка сама слетает с пружинкой
    pre = bump(t, T_MOZH - .12, .12)          # крышка вздрагивает перед щелчком
    jx, jy, jk = JAR13[0], JAR13[1], JAR13_K
    closed = PR.jar(jx, jy, jk, 0, 6 * pre, 0.0, .5 * pre, seed=2, t=t)
    cut = jy - 247 * jk                        # граница горлышка и крышки (общий рисунок props.jar разрезан клипом)
    cb = lib.clip_rect(jx - 300, cut, 600, 600)
    jar = f'<g clip-path="url(#{cb})">{closed}</g>'
    q = clamp((t - (T_MOZH - .01)) / .62)      # крышка: щелчок вверх дугой, кувырок, падает на стол перед банкой и подпрыгивает
    if q <= 0:
        cl = lib.clip_rect(jx - 300, cut - 300, 600, 300)
        jar += f'<g clip-path="url(#{cl})">{closed}</g>'
    else:
        land = (jx - 105, R.DESK_TOP - 6)
        lid0 = (jx, cut - 14 * jk)
        qq = min(q, 1.0)
        px = lerp(lid0[0], land[0], ease_out(qq, 1.3))
        py = lerp(lid0[1], land[1], qq) - 260 * math.sin(math.pi * qq) * (1 - .3 * qq)
        py += PR.hop(t, T_MOZH + .61, 22, .2)
        rot_ = -360 * ease_out(qq, 1.6)
        cl = lib.clip_rect(jx - 300, cut - 300, 600, 300)
        lid_g = f'<g clip-path="url(#{cl})">{closed}</g>'
        jar += f'<g transform="translate({px - lid0[0]:.2f} {py - lid0[1]:.2f}) rotate({rot_:.2f} {lid0[0]:.2f} {lid0[1]:.2f})">{lid_g}</g>'
    lx, ly = PR.jar_lid_c(JAR13[0], JAR13[1], JAR13_K)
    pop_ = ""
    pu = bump(t, T_MOZH, .3)
    if pu > .01:      # штрихи щелчка
        for j, a in enumerate((-150, -110, -70, -30)):
            ar = math.radians(a)
            r0, r1 = 60 + 30 * pu, 90 + 70 * pu
            pop_ += line([(lx + r0 * math.cos(ar), ly - 20 + r0 * math.sin(ar)), (lx + r1 * math.cos(ar), ly - 20 + r1 * math.sin(ar))], 5, lib.INK,
                         taper=.7, wmin=.1, seed=7490 + j, op=pu)
    # свет экрана на лице (тёплый, приглушённый — горит лампа)
    hd = people.dima(hx, hy, DS13, e, "phone_chest74", layers=("legs",), **fkw)["head"]
    face = R.screen_light74(hd[0] + 75, hd[1] + 20, 130, 170, .55, t)
    world = [nd["bg"], nd["chair_back"], nd["desk_top"], nd["pool"], legs, nd["desk_legs"], nd["chair_seat"], body_svg, bit, arm_svg,
             cat, jar, pop_, crumbs, face, nd["lamp"]]
    # камера: мягкий наезд 4 %, на «можем» отскок вверх 3 % вслед за крышкой
    u = sm(t, T_A13 - .2, 20.25)
    kick = bump(t, T_MOZH, .45)
    s = 1.38 * (1 + .04 * u + .03 * kick)
    ccx = lerp(655, 666, u) + 3 * math.sin(t * 1.4)
    ccy = lerp(850, 840, u) - 40 * kick + 3 * math.sin(t * 1.7)
    set_ink(s)
    warm = '<rect x="-3000" y="-3000" width="8000" height="8000" fill="#ff9a40" opacity=".18" style="mix-blend-mode:soft-light"/>'
    return f'<g transform="{lib.cam(ccx, ccy, s, lerp(-.3, .3, u))}">{"".join(world)}{warm}</g>', "#24170f"


FRAMES["s13"] = s13
