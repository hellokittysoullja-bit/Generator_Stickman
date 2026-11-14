"""Рилс 63, группа D, s11 (21.5–23.6): спальня ночью, вид сверху (common/room.py bed_top). Дима лежит на спине под одеялом, глаза
распахнуты в потолок (= в камеру). «Тогда» (21.56) на тумбочке тикают стрелки часов без цифр, «мешает» (22.46) глаза распахиваются
шире пружиной, у груди стучит сердце штрихами, «спать» (22.88) ворочается на бок и обратно (поворот тела и головы через
промежуточные положения, не сжатие), одеяло комкается; лунная полоса формы окна. Камера сверху, мини-тряска на «мешает».
Вид сверху на лежащего на спине = вид спереди на стоящего: фигура people.figure стоит «вверх головой» по кровати."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
import people  # noqa: E402
import room as R  # noqa: E402
import s63d as D  # noqa: E402
from lib import clamp, ease_io, smooth  # noqa: E402

props = D.props
SC = 1.25
HEAD = (530.0, 590.0)
HIP = (HEAD[0] - 54 * SC, HEAD[1] + 548 * SC)
QUILT_Y = HEAD[1] + 225 * SC


def tick_angle(t, t0=D.T_TOGDA, step=.42, deg=6.0):
    """Минутная стрелка тикает рывками с отскоком после t0 (до — стоит)."""
    if t < t0:
        return 0.0
    n = int((t - t0) / step)
    u = (t - t0) - n * step
    return deg * (n + lib.spring(u, 5.0, 10.0))


def toss(t):
    """(поворот тела°, поворот головы, сдвиг x): на бок и обратно через промежуточные положения."""
    t0 = D.T_SPAT
    a = 0.0
    a += 15 * ease_io(clamp((t - t0) / .3)) * (1 - ease_io(clamp((t - t0 - .38) / .32)))
    a += -10 * ease_io(clamp((t - t0 - .62) / .22)) * (1 - ease_io(clamp((t - t0 - .9) / .3)))
    a += 3 * math.sin(t * 1.3)
    head = .02 + a / 40.0
    return a, head, 1.2 * a


def legs_under(hx, hy, ang, crumple, t):
    """Ноги под одеялом: два длинных валика складками и бугорки стоп у изножья; при повороте тела съезжают вбок."""
    sh, hi = "#41528c", "#7486c8"
    o = []
    bot = R.B_TOP_BED[1] + R.B_TOP_BED[3] / 2 - 120
    for j, s_ in enumerate((-1, 1)):
        x0 = hx + s_ * 70 + 2 * ang
        x1 = hx + s_ * 85 + 5 * ang
        o.append(lib.line([(x0 + s_ * 70, hy - 60), (x0 + s_ * 80, hy + 120), (x1 + s_ * 60, bot - 50)], 4.5, sh, taper=.4, wmin=.3, seed=9900 + j))
        o.append(lib.line([(x0 + s_ * 20, hy), (x0 + s_ * 25, bot - 160)], 5, hi, taper=.6, wmin=.2, seed=9910 + j))
        fx = x1 + s_ * 20
        o.append(lib.line([(fx - 55, bot), (fx - 30, bot - 50), (fx + 30, bot - 50), (fx + 55, bot)], 4.5, sh, taper=.3, wmin=.3, seed=9920 + j))
    o.append(lib.line([(hx - 10 + 3 * ang, hy + 60), (hx + 4 * ang, bot - 70)], 4, sh, taper=.5, wmin=.2, seed=9930))
    return "".join(o)


def frame11(t):
    lib.INK_K[0] = 1.0
    rm = R.bed_top(t)
    o = [rm["bg"]]
    # часы на тумбочке (лежат циферблатом вверх), стрелки тикают
    sx, sy = R.B_TOP_STAND
    ah, am = props.clock_hm(2, 10)
    am += tick_angle(t)
    o.append(props.clock(sx, sy, 78, ah + am / 12, am, seed=11))
    # мимика: глаза в потолок → «мешает» распахиваются пружиной
    mesh = t >= D.T_MESH
    k = lib.spring(t - D.T_MESH, 3.4, 6.0) if mesh else 0.0
    ang, head_ang, dx = toss(t)
    wide = 1.08 + .38 * k
    blink = D.bump(t, 21.85, .22)
    look_x = .05 * math.sin(t * 2.2) + .45 * clamp(abs(ang) / 22) * (1 if ang > 0 else -1)
    trem = .05 * math.sin(t * 41) * clamp(k)
    ex = {"brows": "worry" if not mesh else "up", "mouth": "flat" if not mesh else "o", "open": .2 * clamp(k), "lid": .78 * (1 - blink) + .2 * clamp(k),
          "look": (look_x + trem, -.05 + trem), "scale_n": wide, "scale_f": wide}
    breath = math.sin(t * 2 * math.pi / (1.2 if mesh else 2.4))
    hx, hy = HIP[0] + dx, HIP[1]
    arms = {"f": ("ik", (hx + 20 * SC, hy - 150 * SC), 1), "n": ("ik", (hx + 150 * SC, hy - 140 * SC), -1)}
    hands = {"f": {"curl": (.35, .4, .45, .5), "thumb": .3, "spread": .1, "dir": (-1, .15)}, "n": {"curl": (.4, .45, .5, .55), "thumb": .3, "spread": .1, "dir": (-1, -.1)}}
    fig = people.figure("dima", hx, hy, SC, ex, lean=-.02, head_ang=head_ang, arms={"f": ("ang", .1, .1), "n": ("ang", -.1, .1)}, hands={"f": {"kind": "none"}, "n": {"kind": "none"}}, torso_k=1 + .015 * breath,
                        layers=("pelvis", "body"))
    armsv = people.figure("dima", hx, hy, SC, ex, lean=-.02, head_ang=head_ang, arms=arms, hands=hands, torso_k=1 + .015 * breath,
                          layers=("arm_f", "arm_n"))
    rot = f'rotate({ang:.3f} {hx:.1f} {hy - 200:.1f})'
    o.append(f'<g transform="{rot}">{fig["svg"]}</g>')
    crumple = clamp((t - D.T_SPAT + .05) / .7)
    o.append(R.quilt(t, crumple=crumple, y_top=QUILT_Y - 6 * breath, seed=4))
    o.append(legs_under(hx, hy, ang, crumple, t))
    o.append(rm["moon"])
    # руки под одеялом, пальцы вцепились в край одеяла у подбородка
    qy = QUILT_Y - 6 * breath
    grip = .55 + .25 * clamp(k)
    for j, (xh, fl) in enumerate(((-120, 1), (95, 1))):
        cxh = hx + 54 * SC + xh + .9 * dx
        hs = people.hand_svg("dima", (cxh, qy - 34), (0.08 * (1 if j else -1), 1.0), k=SC * .95, flip=fl,
                             curl=(grip, grip + .05, grip + .08, grip + .1), spread=.08, thumb=.2, bend=.2, seed=9950 + 30 * j)
        o.append(f'<g transform="{rot}">{hs}</g>')
    # сердце стучит у груди штрихами (поверх одеяла)
    if mesh:
        per = .42
        u = ((t - D.T_MESH) % per) / per
        beat = clamp(u / .45)
        appear = smooth(D.T_MESH, D.T_MESH + .15, t)
        cxh, cyh = hx + 54 * SC + .8 * dx, QUILT_Y + 190
        o.append(props.heart(cxh, cyh, .9 * appear, beat if beat < 1 else 0.0, seed=3))
    # камера сверху: медленный наезд, мини-тряска на «мешает», лёгкий наклон
    u = ease_io(clamp((t - 21.3) / 2.5))
    z = 1.16 + .12 * u
    sh = props.shake(t, D.T_MESH, amp=9, dur=.32, seed=4)
    cx, cy = 490 + sh[0], 930 - 50 * u + sh[1]
    return f'<g transform="{lib.cam(cx, cy, z, 1.5 - 3 * u)}">{"".join(o)}</g>'
