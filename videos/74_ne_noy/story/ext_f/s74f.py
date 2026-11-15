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
