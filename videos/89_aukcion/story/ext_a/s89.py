"""Рилс 89 «Аукцион времени», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу wN); числа в коде — длительности движений.
Зал аукциона (hall_world): бордовая стена с занавесом, трибуна с аукционистом и молотком, пьедестал с лотом, окно справа;
в зале покупатели-значки приложений (цветные круглые головы-иконки без букв и логотипов, смокинги, таблички без цифр)
и Дима. Хук s01 — влёт правил 28–29 к молотку; s18 — петля тем же ракурсом. Призыв s09 — scripts/story_cta_tg.py.
NOCAM=1 — без влёта, тряски и заголовка (замер движения рисунка); MASK=1 — только рисунок хука белым на чёрном."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(STORY)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
sys.path.insert(1, os.path.join(REPO, "scripts"))
import big_title  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import cat as CT  # noqa: E402
import props as PR  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape, smooth  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
NOCAM = bool(os.environ.get("NOCAM"))
MASK = bool(os.environ.get("MASK"))


def W(i):
    return WORDS[i]["start"]


def WE(i):
    return WORDS[i]["end"]


def stress(i, u):
    return W(i) + (WE(i) - W(i)) * u


def T0(sid):
    return SHOT[sid]["t0"]


def T1(sid):
    return SHOT[sid]["t1"]


def damp(t, t0, amp, freq=3.0, dmp=6.0):
    u = t - t0
    if u <= 0:
        return 0.0
    return amp * math.exp(-dmp * u) * math.sin(2 * math.pi * freq * u)


def title(t):
    """Заголовок хука «ТВОЁ ВРЕМЯ / ПРОДАНО»: экранный слой s01–s03, уходит сжатием к ~3.5 с."""
    if NOCAM or MASK:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, text=SH["title"]["text"], t_in=SH["title"]["t_in"], t_out=SH["title"]["t_out"], hits=hits)


def hook_wrap(body, t, hit):
    """Влёт правил 28–29 поверх кадра (anim.hook_cam): масштаб, поворот, занос, радиальное размытие копиями."""
    import anim
    hc = anim.hook_cam(t, hit=hit)
    z, r, dx, dy = hc["zoom"], hc["rot"], hc["dx"], hc["dy"]
    tr = f"translate({540 + dx:.2f} {PIV + dy:.2f}) rotate({r:.3f}) scale({z:.5f}) translate(-540 {-PIV})"
    blur = ""
    amt = hc["zoom_blur"] / 0.07
    if amt > 0.03:
        for dk, op in ((.03, .30), (.06, .2), (.1, .12)):
            blur += (f'<g opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {PIV + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-PIV})">{body}</g>')
    return f'<rect width="1080" height="1920" fill="#6b4127"/><g transform="{tr}">{body}</g>{blur}'


PIV = 700.0     # центр влёта и удара — у бойка молотка (ниже заголовка)


MASK_F = '<filter id="mk89"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 9 0"/></filter>'


def mask_svg(world_mask, cam):
    lib.DEFS.append(MASK_F)
    return lib.svg('<rect width="1080" height="1920" fill="#000"/>'
                   f'<g transform="{lib.cam(*cam)}"><g filter="url(#mk89)">{world_mask}</g></g>')




# ═════════════════════════ телефон в руке бегущего (в L-единицах rdima) ═════════════════════════
PH_BODY, PH_SCREEN = "#2b2e36", "#9fd6ff"



# ═════════════════════════ общие помощники планов в комнатах ═════════════════════════

FL = 1240.0                       # пол комнат (мир = кадр при камере (540, 960, 1))
GOLD, GOLD_SH = "#f2b84b", "#c98a22"


def ws(i):
    return WORDS[i]["start"]


def we(i):
    return WORDS[i]["end"]


def ramp(t, a, d):
    return clamp((t - a) / d)


def bump(t, a, up=.08, down=.3):
    """0 → 1 за up, затухание за down."""
    u = t - a
    if u <= 0:
        return 0.0
    return min(1.0, u / up) * (math.exp(-(u - up) / down) if u > up else 1.0)


def shake(t, a, amp=10.0, dur=.35, f=11.0):
    u = t - a
    if u <= 0 or u > dur * 3:
        return 0.0, 0.0
    e = math.exp(-u / dur * 2.5)
    return amp * e * math.sin(2 * math.pi * f * u), amp * .6 * e * math.cos(2 * math.pi * f * .8 * u)


def view(body, cx, cy, s, rot=0.0, bg="#e9dcc6", over=""):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def rect(x0, y0, x1, y1, col, op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{col}"{o}/>'


def shadow(x, y, rx, op=.2):
    return blob(ellipse_pts(x, y, rx, rx * .13, 20), "#3a2a1c", op)


ROOM = dict(wall="#eadcc4", wall_sh="#d9c6a8", floor="#b98d64", floor_sh="#a07650", base="#f4ead8", ln="#8a6a4c")


def room(x0=-1200.0, x1=2400.0, wall=None, floor=None, seed=0):
    P = dict(ROOM)
    if wall:
        P["wall"], P["wall_sh"] = wall, lib.mul(wall, (.93, .92, .9))
    if floor:
        P["floor"], P["floor_sh"] = floor, lib.mul(floor, (.88, .86, .84))
    o = [rect(x0, -1400, x1, FL, P["wall"])]
    g = lib.lin_grad([(0, P["wall_sh"], .0), (1, P["wall_sh"], .9)], 0, -800, 0, FL, units="userSpaceOnUse")
    o.append(f'<rect x="{x0}" y="-1400" width="{x1 - x0}" height="{FL + 1400}" fill="url(#{g})"/>')
    o.append(rect(x0, FL, x1, FL + 1400, P["floor"]))
    for k in range(int((x1 - x0) / 170) + 1):
        x = x0 + k * 170
        o.append(line([(x, FL + 4), (x - 120, FL + 700)], 2.0, P["floor_sh"], seed=3300 + seed + k, op=.6))
    o.append(shape(lib.rect_pts(x0, FL - 26, x1, FL + 4), P["base"], "", w=3.6, seed=3290 + seed))
    return "".join(o)


def window(x0, y0, x1, y1, sky="#9fd2f2", t=0.0, sun=None, moon=None):
    o = [shape(lib.rect_pts(x0 - 18, y0 - 18, x1 + 18, y1 + 18), "#f6eee0", "", w=4.4, seed=3400)]
    o.append(rect(x0, y0, x1, y1, sky))
    if sun is not None:
        g = lib.rad_grad([(0, "#fff7d0", .9), (1, "#fff7d0", 0)], sun[0], sun[1], 110)
        o.append(f'<circle cx="{sun[0]:.1f}" cy="{sun[1]:.1f}" r="110" fill="url(#{g})"/>'
                 f'<circle cx="{sun[0]:.1f}" cy="{sun[1]:.1f}" r="38" fill="#ffe27a"/>')
    if moon is not None:
        o.append(f'<circle cx="{moon[0]:.1f}" cy="{moon[1]:.1f}" r="32" fill="#f4f0dc"/>'
                 f'<circle cx="{moon[0] + 14:.1f}" cy="{moon[1] - 8:.1f}" r="28" fill="{sky}"/>')
    inner = "".join(o[1:])
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    out = o[0] + f'<g clip-path="url(#{c})">{inner}</g>'
    out += line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], 6, "#f6eee0", taper=0, wmin=1, seed=3401)
    out += line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], 6, "#f6eee0", taper=0, wmin=1, seed=3402)
    out += f'<path d="{lib.ink_closed(lib.rect_pts(x0, y0, x1, y1), 4.0, seed=3403)}" fill="{INK}"/>'
    return out


def sofa(x0, x1, y, col="#5a7fb5"):
    """Диван: сиденье верхом на y; спинка выше, подлокотники по краям."""
    sh = lib.mul(col, (.82, .82, .86))
    o = [shape(lib.rrect(x0 + 40, y - 330, x1 - 40, y + 20, 40), sh, "", w=5, seed=3500)]
    o.append(shape(lib.rrect(x0 + 60, y - 20, x1 - 60, y + 150, 30), col, blob(lib.rect_pts(x0 + 60, y + 90, x1 - 60, y + 150), sh, .6), w=5, seed=3501))
    for k, (a, b) in enumerate(((x0 - 10, x0 + 110), (x1 - 110, x1 + 10))):
        o.append(shape(lib.rrect(a, y - 130, b, y + 160, 45), col, blob(lib.rect_pts(a, y + 40, b, y + 160), sh, .5), w=5, seed=3502 + k))
    for x in (x0 + 40, x1 - 60):
        o.append(rect(x, y + 160, x + 22, y + 200, "#5b3d26"))
    return "".join(o)


def phone_up(x, y, k=1.0, rot=0.0, glow=1.0, scroll=0.0, feed=True, dim=0.0):
    """Телефон экраном к зрителю (ЦЕНТР x, y; 120×240·k), без букв: цветные карточки ленты листаются."""
    o = []
    if glow > .01:
        g = lib.rad_grad([(0, "#d8f2ff", .35 * glow), (1, "#d8f2ff", 0)], x, y, 260 * k)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{260 * k:.1f}" fill="url(#{g})"/>')
    body = lib.T(lib.rrect(-60, -120, 60, 120, 18), x, y, k, rot)
    scr = lib.T(lib.rrect(-50, -106, 50, 106, 10), x, y, k, rot)
    inner = blob(scr, lib.mix(PH_SCREEN, "#3b4250", dim))
    if feed:
        for j in range(6):
            yy = -100 + ((j * 42 + scroll * 160) % 252) - 20
            card = lib.T(lib.rrect(-42, yy, 42, yy + 30, 6), x, y, k, rot)
            inner += blob(card, ("#ff8a7a", "#ffd166", "#7bd389", "#c9a7ff", "#ff9ec7", "#6cc4ff")[j], .9 * (1 - dim))
    c = lib.clip_of(scr)
    o.append(shape(body, PH_BODY, f'<g clip-path="url(#{c})">{inner}</g>', w=4.0 * max(.6, k), seed=3600))
    return "".join(o)


def fig(x, y, sc, expr, pose=None, feet="stand", lean=None, head_ang=None, arms=None, hands=None, layers=None, flip=False):
    kw = {}
    if pose:
        kw.update(people.pose_kw(pose, x, y, sc))
    if feet == "stand":
        kw.update(people.stand_kw(x, y, sc))
    elif feet == "sit":
        kw.update(people.sit_kw(x, y, sc))
    elif isinstance(feet, dict):
        kw["feet"] = feet
    if lean is not None:
        kw["lean"] = lean
    if head_ang is not None:
        kw["head_ang"] = head_ang
    if arms is not None:
        kw["arms"] = arms
    if hands is not None:
        kw["hands"] = hands
    return people.figure("dima", x, y, sc, expr=expr, layers=layers, flip=flip, **kw)


def dima_phone(x, y, sc, expr, t, feet="stand", lean=0.12, glow=1.0, ph_k=None, scroll_v=1.6, extra_arms=None, head_ang=0.32):
    """Дима держит телефон двумя руками перед грудью и смотрит в экран. -> (svg, res, точка телефона)."""
    arms = {"f": ("ik", (x + 215 * sc, y - 285 * sc), -1), "n": ("ik", (x + 305 * sc, y - 290 * sc), -1)}
    if extra_arms:
        arms.update(extra_arms)
    hands = {"f": {"dir": (.9, -.3), "curl": (.55, .55, .6, .62), "thumb": .5}, "n": {"dir": (-.6, -.7), "curl": (.6, .6, .65, .68), "thumb": .6}}
    base = fig(x, y, sc, expr, feet=feet, lean=lean, head_ang=head_ang, arms=arms, hands=hands, layers=("legs", "pelvis", "arm_f", "body"))
    near = fig(x, y, sc, expr, feet=feet, lean=lean, head_ang=head_ang, arms=arms, hands=hands, layers=("arm_n",))
    wf, wn = np.array(base["wrist"]["f"]), np.array(base["wrist"]["n"])
    pp = (wf + wn) / 2 + np.array([10 * sc, -40 * sc])
    ph = phone_up(pp[0], pp[1], (ph_k or 0.9) * sc / .5 * .5, -14, glow, t * scroll_v)
    return base["svg"] + ph + near["svg"], base, pp


def cat(x, y, k, t, **st):
    return CT.draw(x, y, k, st, t)


def gold_drop(x, y, k=1.0, rot=0.0):
    return PR.drop(x, y, k, rot, col=GOLD)


def grains(pts, t, n=30, seed=0, k=1.0, speed=1.0, up=False, col=GOLD):
    """Песчинки летят по ломаной pts (от начала к концу) непрерывной струёй."""
    P_ = np.array(pts, float)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P_, axis=0), axis=1))]
    o = []
    rs = np.random.RandomState(5100 + seed)
    for i in range(n):
        ph = (rs.uniform() + t * speed) % 1.0
        d = ph * seg[-1]
        j = min(len(seg) - 2, int(np.searchsorted(seg, d) - 1))
        j = max(j, 0)
        u = (d - seg[j]) / max(1e-6, seg[j + 1] - seg[j])
        p = P_[j] + (P_[j + 1] - P_[j]) * u + rs.uniform(-12, 12, 2) * k
        r = rs.uniform(4, 8) * k
        o.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r:.1f}" fill="{col}" stroke="{INK}" stroke-width="{1.6 * k:.2f}"/>')
    return "".join(o)


def bez(a, c, b, n=16):
    a, c, b = map(np.array, (a, c, b))
    return [tuple((1 - u) ** 2 * a + 2 * u * (1 - u) * c + u * u * b) for u in np.linspace(0, 1, n)]


def dark(op, col="#14183a"):
    return f'<rect x="-3000" y="-3000" width="7000" height="7000" fill="{col}" opacity="{op:.3f}"/>' if op > .005 else ""






# ═════════════════════════ зал аукциона: общие части ═════════════════════════
WALL, WALL_SH, TRIM, WOOD, WOOD_SH = "#8a3242", "#6d2433", "#e0b04a", "#7a4a2a", "#5c341b"
DIMA_RIM = "#e0a43a"                  # обод часов жизни — цвет худи Димы
TAG_RED, TAG_SH = "#e2463c", "#b52f28"
LECT = (330.0, FL)                    # трибуна: центр низа
LECT_TOP = FL - 430.0
BLOCK = (262.0, LECT_TOP - 6)         # подставка молотка на трибуне
PED = (720.0, FL, 1.1)                # пьедестал лота
PED_TOP = FL - 330 * 1.1
WIN = (900.0, 230.0, 1180.0, 600.0)   # окно на стене справа (подоконник — низ)
CLK = (720.0, PED_TOP - 125)          # часы жизни Димы на пьедестале (центр)


def hall_bg(t, x0=-1300.0, x1=2500.0, sun=1.0, win=True):
    o = [rect(x0, -1600, x1, FL, WALL)]
    for k in range(int((x1 - x0) / 110) + 1):             # складки бархата
        x = x0 + k * 110
        o.append(rect(x + 62, -1600, x + 96, FL - 200, WALL_SH, .55))
        o.append(line([(x + 30, -1500), (x + 34, FL - 210)], 3.0, "#a84858", taper=.2, wmin=.4, seed=4000 + k, op=.7))
    o.append(rect(x0, -40, x1, -10, TRIM))
    o.append(rect(x0, FL - 210, x1, FL, WOOD))
    for k in range(int((x1 - x0) / 240) + 1):
        x = x0 + k * 240
        o.append(shape(lib.rect_pts(x + 20, FL - 186, x + 220, FL - 30), WOOD_SH, "", w=3.0, seed=4100 + k))
    o.append(rect(x0, FL - 222, x1, FL - 206, TRIM))
    o.append(rect(x0, FL, x1, FL + 1600, "#6b4127"))
    for k in range(int((x1 - x0) / 150) + 1):
        x = x0 + k * 150
        o.append(line([(x, FL + 4), (x + (x - 540) * 1.2, FL + 1500)], 2.4, "#4f2e1a", seed=4200 + k, op=.7))
    for j, y in enumerate((FL + 120, FL + 320, FL + 600)):
        o.append(line([(x0, y), (x1, y)], 2.0, "#4f2e1a", seed=4300 + j, op=.5))
    if win:
        a, b, c, d = WIN
        o.append(window(a, b, c, d, "#a9dcf5", t, sun=(c - 70, b + 80) if sun > .1 else None))
        o.append(shape(lib.rect_pts(a - 40, d + 18, c + 40, d + 44), "#f6eee0", "", w=4, seed=4400))
        # тяжёлые шторы по бокам окна
        for s_, xx in ((-1, a - 40), (1, c + 40)):
            pts = [(xx, b - 60), (xx + s_ * 90, b - 60), (xx + s_ * 70, d + 10), (xx + s_ * 110, d + 120), (xx, d + 90)]
            o.append(shape(pts, "#b23a4c", line([(xx + s_ * 40, b - 40), (xx + s_ * 46, d + 60)], 3, "#7d2232", seed=4410 + s_), w=4, seed=4405 + s_))
    return "".join(o)


def sun_patch(u, t):
    """Солнечное пятно на подоконнике (и луч из окна), u 0…1."""
    if u <= .01:
        return ""
    a, b, c, d = WIN
    g = lib.lin_grad([(0, "#fff3c4", .0), (1, "#fff3c4", .55 * u)], 0, 0, 0, 1)
    beam = f'<polygon points="{a:.0f},{b:.0f} {c:.0f},{b:.0f} {c + 40:.0f},{d + 30:.0f} {a + 30:.0f},{d + 30:.0f}" fill="url(#{g})"/>'
    gg = lib.rad_grad([(0, "#fff0a8", .8 * u), (1, "#fff0a8", 0)], (a + c) / 2 + 20, d + 20, 240)
    spot = (f'<ellipse cx="{(a + c) / 2 + 20:.0f}" cy="{d + 20:.0f}" rx="240" ry="90" fill="url(#{gg})"/>'
            + blob(ellipse_pts((a + c) / 2 + 20, d + 30, 170 * (.6 + .4 * u), 22, 22), "#ffe070", .95 * u))
    return beam + spot


def lectern(x, yb, k=1.0):
    o = [shape([(x - 150 * k, yb - 430 * k), (x + 150 * k, yb - 430 * k), (x + 125 * k, yb), (x - 125 * k, yb)], WOOD,
               blob([(x + 60 * k, yb - 430 * k), (x + 150 * k, yb - 430 * k), (x + 125 * k, yb), (x + 50 * k, yb)], WOOD_SH)
               + line([(x - 120 * k, yb - 330 * k), (x + 120 * k, yb - 330 * k)], 4 * k, TRIM, seed=4501), w=5 * k, seed=4500)]
    o.append(shape(lib.rect_pts(x - 175 * k, yb - 462 * k, x + 175 * k, yb - 424 * k), "#8f5a33", "", w=4.6 * k, seed=4502))
    o.append(shape(ellipse_pts(x, yb - 210 * k, 62 * k, 62 * k, 26), TRIM, PR.star4(x, yb - 210 * k, 34 * k), w=4 * k, seed=4503))
    return "".join(o)


def gavel_angle(t, hits, rest=18.0):
    """Угол молотка (град; 0 — боёк на подставке, больше — занесён). Перед каждым ударом замах 0.28 с, удар 0.07 с, отскок."""
    a = rest + 3 * math.sin(t * 7.3)
    for h in hits:
        if h - .35 <= t < h - .07:
            u = ease_out(clamp((t - (h - .35)) / .28), 2)
            return a + (62 - a) * u
        if h - .07 <= t < h:
            return 62 * (1 - lib.ease_in(clamp((t - (h - .07)) / .07), 3))
        if h <= t < h + .45:
            q = t - h
            back = smooth(h + .12, h + .45, t)
            return 12 * math.exp(-q * 9) * abs(math.sin(q * 16)) + a * back
    return a


def last_hit(t, hits):
    p = [h for h in hits if h <= t]
    return p[-1] if p else -9.0


def auctioneer(t, hits, expr="talk", look=(-.3, .1), freeze=None):
    """Аукционист (elder82) за трибуной, ближняя рука держит молоток над подставкой. freeze — угол, который держится (s16)."""
    kg = 1.0
    fx, fy = PR.gavel_face(0, 0, kg, 0)
    grip0 = (BLOCK[0] - fx + 10, BLOCK[1] - 44 * .9 - fy)
    a = gavel_angle(t, hits) if freeze is None else freeze
    lh = last_hit(t, hits)
    hip = (LECT[0] + 135, LECT_TOP + 120)
    sc = .62
    ex = dict(people.EXPR["elder82"][expr]) if isinstance(expr, str) else dict(expr)
    ex["look"] = look
    lean = .06 * math.sin(t * 2.1) - .08 * bump(t, lh, .05, .25)
    gx, gy = grip0[0] + 30 * math.sin(math.radians(a)), grip0[1] - 26 * math.sin(math.radians(a))
    arms = {"n": ("ik", (gx + 8, gy + 4), -1), "f": ("ang", .5, .9)}
    hands = {"n": {"dir": (-.2, 1), "curl": (.7, .7, .75, .78), "thumb": .7}, "f": {"dir": (.3, -1), "curl": (.1, .1, .15, .2), "spread": .3}}
    f = people.figure("elder82", hip[0], hip[1], sc, expr=ex, lean=lean, head_ang=-.12, arms=arms, hands=hands,
                      layers=("pelvis", "arm_f", "body"))
    n = people.figure("elder82", hip[0], hip[1], sc, expr=ex, lean=lean, head_ang=-.12, arms=arms, hands=hands, layers=("arm_n",))
    q = t - lh
    o = [f["svg"], lectern(*LECT)]
    o.append(PR.gavel_block(*BLOCK, .9, bounce=math.exp(-q * 9) if 0 <= q < .6 else 0.0, seed=2))
    o.append(PR.gavel(gx, gy, kg, a, t, seed=2))
    o.append(n["svg"])
    if 0 <= q < .5:
        o.append(PR.dust_puff(BLOCK[0] - 80, BLOCK[1] - 10, .7, clamp(q / .5), seed=4))
        o.append(PR.dust_puff(BLOCK[0] + 90, BLOCK[1] - 6, .6, clamp((q - .03) / .45), seed=9))
    return "".join(o), f


# ── покупатели-значки ──
ICONS = {
    "alarm": ("#f39a2e", "alarm"), "feed": ("#ff4f7b", "feed"), "series": ("#d63a35", "play"),
    "chat": ("#3f9cf5", "chat"), "game": ("#5cc46f", "pad"), "shop": ("#9a6cf0", "bag"), "music": ("#14b8a6", "wave"),
}


def glyph(kind, k=1.0):
    """Белая пиктограмма без букв в начале координат (~70 px)."""
    W_ = "#ffffff"
    if kind == "alarm":
        return (shape(ellipse_pts(0, 4, 30, 30, 18), W_, line([(0, 4), (0, -14)], 4, INK, seed=1) + line([(0, 4), (12, 10)], 4, INK, seed=2), w=3, seed=3)
                + shape(ellipse_pts(-24, -24, 11, 9, 10, rot=-35), W_, "", w=3, seed=4) + shape(ellipse_pts(24, -24, 11, 9, 10, rot=35), W_, "", w=3, seed=5))
    if kind == "feed":
        return "".join(blob(lib.rrect(-30, y, 30, y + 14, 6), W_) for y in (-30, -8, 14))
    if kind == "play":
        return blob([(-16, -26), (28, 0), (-16, 26)], W_)
    if kind == "chat":
        return blob(ellipse_pts(0, -4, 32, 24, 18) + [(-14, 18), (-24, 32), (2, 20)], W_)
    if kind == "pad":
        return blob(lib.rect_pts(-9, -28, 9, 28), W_) + blob(lib.rect_pts(-28, -9, 28, 9), W_)
    if kind == "bag":
        return blob(lib.rrect(-26, -12, 26, 28, 6), W_) + line([(-12, -12), (-12, -26), (12, -26), (12, -12)], 5, W_, taper=0, wmin=1, seed=6)
    return line([(-30, 0), (-18, -20), (-6, 18), (6, -24), (18, 16), (30, 0)], 6, W_, taper=0, wmin=1, seed=7)


def paddle(x, y, k=1.0, rot=0.0):
    """Табличка покупателя без цифр: белый овал с красным кантом на ручке; (x, y) — хват."""
    o = shape(lib.rect_pts(-7, -125, 7, 10), "#c08a52", "", w=3, seed=4600)
    o += shape(ellipse_pts(0, -185, 74, 84, 22), "#fbf6ea", blob(ellipse_pts(0, -185, 46, 54, 20), "#fbf6ea")
               + line(ellipse_pts(0, -185, 60, 70, 22) + [ellipse_pts(0, -185, 60, 70, 22)[0]], 5, TAG_RED, taper=0, wmin=1, seed=4601), w=4, seed=4602)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f}) scale({k:.3f})">{o}</g>'


def buyer(x, yb, k, kind, t, raise_u=0.0, look=(0.0, 0.0), turn=0.0, mouth="smug", seed=0, chew=0.0, paddle_on=True, fat=1.0):
    """Покупатель-значок в смокинге (стоит, низ ботинок на yb). raise_u 0…1 — табличка вскинута над головой; look — зрачки;
    mouth: smug / o / grin / chew. -> (svg, точка руки с табличкой, центр головы)."""
    col, gk = ICONS[kind]
    sd = 4700 + seed * 37
    bob = 6 * math.sin(t * 5.1 + seed * 1.7) + 10 * raise_u
    ph = t * 3 + seed
    o = []
    # ноги и ботинки
    for s_ in (-1, 1):
        o.append(shape(lib.rect_pts(s_ * 40 - 26, -230, s_ * 40 + 26, -26), "#1d1f26", "", w=4, seed=sd + 1 + s_))
        o.append(shape(ellipse_pts(s_ * 46, -16, 42, 18, 14), "#111214", blob(ellipse_pts(s_ * 40, -24, 16, 5, 8), "#5a5f6a", .8), w=4, seed=sd + 3 + s_))
    # туловище — фрак
    wq = 1.0 + .18 * (fat - 1)
    tor = [(-92 * wq, -440 - bob, 1), (92 * wq, -440 - bob, 1), (110 * wq, -230, 1), (-110 * wq, -230, 1)]
    inner = blob([(-30, -440 - bob), (30, -440 - bob), (0, -300 - bob)], "#fbf9f4")
    inner += line([(-30, -440 - bob), (0, -300 - bob), (30, -440 - bob)], 3.5, INK, seed=sd + 6)
    inner += blob([(-26, -436 - bob), (-4, -424 - bob), (-26, -410 - bob)], "#16171c") + blob([(26, -436 - bob), (4, -424 - bob), (26, -410 - bob)], "#16171c")
    inner += blob(ellipse_pts(0, -423 - bob, 7, 7, 8), "#16171c")
    for yy in (-350, -300, -260):
        inner += blob(ellipse_pts(0, yy - bob * .5, 4, 4, 6), "#f2c14e")
    o.append(shape(tor, "#22242c", inner, w=4.6, seed=sd + 7))
    # дальняя рука вниз
    o.append(line([(-88 * wq, -420 - bob), (-118 * wq, -330 - bob), (-112 * wq, -250 - bob)], 26, "#22242c", taper=0, wmin=1, seed=sd + 8))
    o.append(shape(ellipse_pts(-112 * wq, -244 - bob, 19, 19, 12), "#fbf9f4", "", w=3.6, seed=sd + 9))
    # голова-значок
    hx, hy = 0.0, -540 - bob
    r = 92 * (1 + .25 * (fat - 1))
    hin = blob(ellipse_pts(hx - 26, hy - 34, 40, 26, 14, rot=-30), "#ffffff", .25)
    g = f'<g transform="translate({hx:.1f} {hy - 26 * (r / 92):.1f}) scale({.82 * r / 92:.3f})">{glyph(gk)}</g>'
    lx, ly = look
    for s_ in (-1, 1):
        ex, ey = hx + s_ * 30 + 12 * turn, hy + 34
        hin += blob(ellipse_pts(ex, ey, 14, 16, 12), "#ffffff")
        hin += blob(ellipse_pts(ex + 6 * lx, ey + 6 * ly, 8, 9, 10), INK)
    my = hy + 62
    if mouth == "o":
        hin += blob(ellipse_pts(hx + 10 * turn, my + 4, 12, 15, 12), "#3a1214")
    elif mouth == "grin":
        hin += blob([(hx - 26, my - 4), (hx + 26, my - 4), (hx, my + 16)], "#3a1214")
    elif mouth == "chew":
        hin += blob(ellipse_pts(hx + 6 * turn, my + 2, 22, 8 + 12 * abs(math.sin(chew)), 14), "#3a1214")
    else:
        hin += line([(hx - 18 + 10 * turn, my), (hx + 2 + 10 * turn, my + 8), (hx + 22 + 10 * turn, my - 6)], 4, INK, seed=sd + 10)
    o.append(shape(ellipse_pts(hx, hy, r, r, 30), col, hin + g, w=5, seed=sd + 11))
    # ближняя рука с табличкой
    sh = (80 * wq, -420 - bob)
    hand = (130 + 20 * raise_u, -300 - bob - 360 * raise_u + 8 * math.sin(ph))
    el = ((sh[0] + hand[0]) / 2 + 40 - 20 * raise_u, (sh[1] + hand[1]) / 2 + 30 * (1 - raise_u))
    if paddle_on:
        o.append(paddle(hand[0], hand[1], .9, 8 * raise_u * math.sin(t * 14) + 10 * (1 - raise_u)))
    o.append(line([sh, el, hand], 26, "#22242c", taper=0, wmin=1, seed=sd + 12))
    o.append(shape(ellipse_pts(hand[0], hand[1], 20, 20, 12), "#fbf9f4", "", w=3.6, seed=sd + 13))
    svg = f'<g transform="translate({x:.1f} {yb:.1f}) scale({k:.4f})">{"".join(o)}</g>'
    return svg, (x + hand[0] * k, yb + hand[1] * k), (x + hx * k, yb + hy * k)


def tag(x, y, k=1.0, rot=0.0, empty=True):
    """Красная бирка-ценник на нитке (x, y — точка подвеса), без букв и цифр."""
    o = line([(0, 0), (0, 60)], 3, INK, seed=4800)
    o += shape([(-34, 60, 1), (34, 60, 1), (34, 160, 1), (0, 190, 1), (-34, 160, 1)], TAG_RED,
               blob([(10, 60), (34, 60), (34, 160), (10, 175)], TAG_SH) + f'<circle cx="0" cy="80" r="8" fill="#f6eee0" stroke="{INK}" stroke-width="3"/>',
               w=4, seed=4801)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f}) scale({k:.3f})">{o}</g>'


def life_clock(x, y, k, t, speed=1.0):
    """Часы жизни Димы (центр x, y): обод цвета его худи, стрелки бегут; ножка-подставка вниз."""
    o = shape(lib.rect_pts(x - 70 * k, y + 100 * k, x + 70 * k, y + 130 * k), "#8f5a33", "", w=4 * k, seed=4900)
    o += line([(x, y + 80 * k), (x, y + 104 * k)], 14 * k, "#8f5a33", taper=0, wmin=1, seed=4901)
    ah, am = (t * 60 * speed) % 360, (t * 520 * speed) % 360
    o += PR.clock(x, y, 100 * k, angle_h=ah, angle_m=am, seed=7, rim=DIMA_RIM)
    return o


def dima_fig(x, y, sc, expr, reach=0.0, t=0.0, wobble=1.0, look=None, lean=0.0, head_ang=0.0, flip=False, near_arm=None, far_arm=None):
    """Дима стоит; reach 0…1 — ближняя рука тянется вверх (робко при 0.5, решительно при 1)."""
    ex = dict(people.EXPR["dima"][expr]) if isinstance(expr, str) else dict(expr)
    if look:
        ex["look"] = look
    sh = (x + 40 * sc, y - 430 * sc)
    rest = (x + 110 * sc, y - 30 * sc)
    top = (x + 200 * sc, y - 1120 * sc)
    w_ = 14 * sc * wobble * math.sin(t * 9)
    hn = (rest[0] + (top[0] - rest[0]) * reach + w_, rest[1] + (top[1] - rest[1]) * reach)
    arms = {"n": near_arm or ("ik", hn, 1), "f": far_arm or ("ang", .12, .2)}
    hands = {"n": {"dir": (.15, -1) if reach > .3 else (.3, .9), "curl": (.15, .12, .15, .2), "spread": .25, "thumb": .3}}
    return fig(x, y, sc, ex, feet="stand", lean=lean, head_ang=head_ang, arms=arms, hands=hands, flip=flip)


HIT01 = [0.07, stress(3, .55)]


def hall_scene(t, hits, lot="clock", dima=None, buyers=None, auct=None, sun=0.0, extra="", cat_=None):
    """Общий зал (ракурс хука): -> (тело, рисунок хука для маски)."""
    o = [hall_bg(t)]
    o.append(sun_patch(sun, t))
    if cat_:
        o.append(cat_)
    ag, _ = auctioneer(t, hits, **(auct or {}))
    o.append(PR.pedestal(PED[0], PED[1], PED[2], seed=1))
    if lot == "clock":
        o.append(life_clock(CLK[0], CLK[1], 1.0, t))
        o.append(tag(CLK[0] + 92, CLK[1] - 40, .7, 14 * math.sin(t * 4.3)))
    o.append(ag)
    o.append(extra)
    fg = []
    if dima:
        fg.append((dima[1], dima[0]))
    for b in buyers or []:
        fg.append((b[1], b[0]))
    for _, s in sorted(fg, key=lambda z: z[0]):
        o.append(s)
    return "".join(o), ag + "".join(s for _, s in fg)


def crowd(t, raise_fn=None, look=(-.5, -.4), skip=()):
    """Зал покупателей: [(svg, yb, имя)]; raise_fn(name) -> 0…1."""
    rows = [("chat", -130.0, FL + 520, 1.05, 1), ("alarm", 140.0, FL + 680, 1.15, 2), ("feed", 1010.0, FL + 640, 1.15, 3),
            ("series", 1290.0, FL + 500, 1.05, 4), ("game", 1480.0, FL + 720, 1.2, 5)]
    out = []
    for name, x, yb, k, sd in rows:
        if name in skip:
            continue
        ru = raise_fn(name) if raise_fn else .5 + .5 * math.sin(t * 6 + sd * 2.1) ** 2
        s, hand, head = buyer(x, yb, k, name, t, ru, look=look, seed=sd)
        out.append((s, yb, name))
    return out


# ═════════════════════════ s01: хук ═════════════════════════
def frame_s01(t):
    hits = HIT01
    ru = lambda n: clamp(.55 + .45 * math.sin(t * 7 + {"chat": 1, "feed": 3, "series": 5, "game": 2}.get(n, 0))) if n != "alarm" else .9
    cr = crowd(t, ru)
    reach = .45 + .12 * math.sin(t * 5)
    dg = dima_fig(600.0, FL + 470, .74, "nervous", reach, t, look=(-.6, -.7))["svg"]
    body, maskw = hall_scene(t, hits, dima=(dg, FL + 400), buyers=[(s, yb) for s, yb, _ in cr])
    # камера сцены: летит от общего плана к трибуне (движется с кадра 0, без разгона)
    u = 1 - math.exp(-t / .55)
    cx = 620 - 280 * u + 14 * math.sin(t * 3)
    cy = 1150 - 160 * u
    s = .62 + .2 * u
    cam = (cx, cy, s, -2.0 + 2.0 * u)
    if MASK:
        return mask_svg(maskw, cam)
    lh = last_hit(t, hits)
    dx, dy = shake(t, lh, 14) if not NOCAM else (0, 0)
    v = f'<g transform="{lib.cam(cx + dx, cy + dy, s, cam[3])}">{body}</g>'
    if NOCAM:
        return lib.svg(f'<rect width="1080" height="1920" fill="{WALL}"/>' + v)
    return lib.svg(hook_wrap(v, t, stress(3, .55)) + title(t))


# ═════════════════════════ s02: лот — часы жизни Димы крупно ═════════════════════════
def spotlight(x, y, u=1.0, w=260.0):
    g = lib.lin_grad([(0, "#fff6d6", .0), (1, "#fff6d6", .38 * u)], 0, 0, 0, 1)
    return f'<polygon points="{x - 60:.0f},-900 {x + 60:.0f},-900 {x + w:.0f},{y:.0f} {x - w:.0f},{y:.0f}" fill="url(#{g})"/>'


def frame_s02(t):
    a = T0("s02")
    o = [hall_bg(t)]
    o.append(spotlight(CLK[0], FL, smooth(a - .2, a + .2, t)))
    o.append(PR.pedestal(PED[0], PED[1], PED[2], seed=1))
    spin = 1.0 + 7.0 * smooth(W(5) - .05, W(5) + .25, t)
    o.append(life_clock(CLK[0], CLK[1], 1.0, a + (t - a) * spin))
    sw = 14 * math.sin(t * 4.3) + damp(t, W(4), 34, 2.2, 3.5)
    o.append(tag(CLK[0] + 92, CLK[1] - 40, .7, sw))
    o.append(PR.sparkles(CLK[0], CLK[1], 1.3, smooth(W(5), W(5) + .2, t), t, seed=3))
    # Дима внизу справа: тянет руку на «твоё», на «время» рука никнет
    up = smooth(W(4) - .25, W(4) + .1, t) * (1 - .7 * smooth(W(5) + .25, W(5) + .6, t))
    ex = "nervous" if t < W(5) + .3 else "glum"
    o.append(dima_fig(960.0, FL + 330, .74, ex, .2 + .8 * up, t, look=(-.7, -.8), wobble=.6)["svg"])
    z = 1.95 + .15 * ease_io(ramp(t, a, T1("s02") - a)) + .08 * bump(t, W(5))
    dx, dy = shake(t, W(5), 8)
    return view("".join(o), 790 + dx, 830 + dy, z, -1.0 + 1.5 * ramp(t, a, 1.4), bg=WALL, over=title(t))


# ═════════════════════════ лоты: утро / обед / вечер (храповик) ═════════════════════════
def lot_art(kind, x, y, t, k=1.0):
    if kind == "morning":
        return PR.sun(x, y, 70 * k, 1.0, t, seed=2)
    if kind == "lunch":
        return PR.plate_soup(x, y + 30 * k, .9 * k, 1.0, t, seed=2)
    return (blob(ellipse_pts(x, y, 120 * k, 120 * k, 24), "#33407a", .35) + PR.moon(x, y, 62 * k, 1.0)
            + PR.star4(x - 80 * k, y - 60 * k, 16 * k) + PR.star4(x + 70 * k, y + 50 * k, 12 * k))


def lot_shot(t, sid, kind, winner, wi, cam, wpos, night=0.0):
    """Лот на пьедестале; winner вскидывает табличку к слову wi, молоток бьёт на его ударном слоге, лот летит к нему."""
    a = T0(sid)
    h = stress(wi, .45)
    hits = [h]
    o = [hall_bg(t)]
    o.append(spotlight(PED[0], FL, 1.0))
    o.append(PR.pedestal(PED[0], PED[1], PED[2], seed=1))
    ag, _ = auctioneer(t, hits, expr="talk" if t < h else "wow", look=(.6, .2))
    o.append(ag)
    wx, wyb, wk = wpos
    ru = smooth(W(wi) - .35, W(wi) - .05, t)
    bs, hand, head = buyer(wx, wyb, wk, winner, t, ru, look=(-.6, -.5), mouth="grin" if t > h else "smug", seed=7)
    # лот: стоит на пьедестале, после удара дугой летит к победителю
    lx0, ly0 = PED[0], PED_TOP - 90
    fu = ease_io(ramp(t, h + .08, .5))
    tx, ty = head[0], head[1] - 150 * wk
    lx = lx0 + (tx - lx0) * fu
    ly = ly0 + (ty - ly0) * fu - 260 * math.sin(math.pi * fu)
    kk = 1.0 - .35 * fu
    o.append(lot_art(kind, lx, ly, t, kk))
    if fu < .02:
        o.append(tag(lx0 + 110, ly0 - 30, .6, 12 * math.sin(t * 4)))
    others = [b for b in crowd(t, look=(-.4, -.5)) if b[2] != winner and abs(dict(chat=-130, alarm=140, feed=1010, series=1290,
              game=1480)[b[2]] - wx) > 700][:1]
    for s_, yb, _ in sorted(others, key=lambda z: z[1]):
        if yb < wyb:
            o.append(s_)
    o.append(bs)
    for s_, yb, _ in sorted(others, key=lambda z: z[1]):
        if yb >= wyb:
            o.append(s_)
    o.append(PR.sparkles(tx, ty, 1.2, smooth(h + .5, h + .65, t) * (1 - smooth(h + .9, h + 1.2, t)), t, seed=5))
    o.append(dark(.38 * night))
    cx, cy, z0 = cam
    z = z0 + .1 * ease_io(ramp(t, a, T1(sid) - a)) + .1 * bump(t, h, .04, .3)
    dx, dy = shake(t, h, 16)
    return view("".join(o), cx + dx, cy + dy, z, 1.2 * math.sin(t * 2), bg=WALL, over=title(t))


def frame_s03(t):
    return lot_shot(t, "s03", "morning", "alarm", 8, (760, 960, 1.12), (990.0, FL + 330, .95))


def frame_s05(t):
    return lot_shot(t, "s05", "lunch", "feed", 16, (470, 980, 1.12), (130.0, FL + 360, .95))


def frame_s06(t):
    return lot_shot(t, "s06", "evening", "series", 20, (760, 960, 1.1), (1000.0, FL + 300, .95), night=.6)


# ═════════════════════════ s04: «пять минут» — стопка подушек ═════════════════════════
PILLOW_COLS = ["#f4d6e0", "#cfe3f4", "#f6e7b8", "#d8efd2", "#e6d6f6"]


def frame_s04(t):
    a = T0("s04")
    drops = [a + .1, W(10), W(11), W(12), W(13)]
    o = [hall_bg(t)]
    o.append(spotlight(PED[0], FL, 1.0))
    o.append(PR.pedestal(PED[0], PED[1], PED[2], seed=1))
    top = PED_TOP
    wob = sum(damp(t, d + .25, 3.5, 2.4, 3.0) for d in drops)
    st = ""
    for i, d in enumerate(drops):
        if t < d - .25:
            continue
        u = clamp((t - (d - .25)) / .25)
        yl = top - 8 - i * 66
        y = yl - (1 - u * u) * 900
        sq = 1 + .25 * bump(t, d, .03, .12)
        rot = (-4 if i % 2 else 5) + wob * (i + 1) * .6
        p = PR.pillow(0, 0, 1.25, rot, col=PILLOW_COLS[i], seed=i)
        st += f'<g transform="translate({PED[0] + (i % 2) * 14 - 7:.1f} {y:.1f}) scale({sq:.3f} {1 / sq:.3f})">{p}</g>'
    o.append(st)
    bs, hand, head = buyer(1060.0, FL + 300, 1.05, "alarm", t, .15 + .2 * math.sin(t * 6) ** 2, look=(-.7, -.6),
                           mouth="grin", seed=7)
    o.append(bs)
    # будильник-значок подпрыгивает и трезвонит на каждой подушке
    for d in drops:
        if 0 <= t - d < .3:
            o.append(PR.speed_arcs(head[0] - 130, head[1] - 40, 1.0, 1 - (t - d) / .3, t, seed=int(d * 10), n=3))
    o.append(title(t) and "")
    z = 1.3 + .18 * ease_io(ramp(t, a, T1("s04") - a))
    cy = 860 - 120 * ease_io(ramp(t, a, T1("s04") - a))
    dx, dy = shake(t, max([d for d in drops if d <= t] or [-9]), 7)
    return view("".join(o), 860 + dx, cy + dy, z, 0, bg=WALL)


# ═════════════════════════ s07: сериал, который ты даже не любишь ═════════════════════════
def frame_s07(t):
    a = T0("s07")
    o = [room(-900, 2200, wall="#4b4470", floor="#5a4636")]
    tvx, tvy = 900.0, 780.0
    o.append(shape(lib.rect_pts(tvx - 40, FL - 260, tvx + 220, FL), "#3b2c22", "", w=4, seed=5000))
    o.append(shape(lib.rect_pts(tvx - 120, tvy - 190, tvx + 300, tvy + 70), "#1d1f26", "", w=5, seed=5001))
    sc_ = ""
    for j in range(5):
        ph = (t * .9 + j * .23) % 1
        cx_ = tvx - 80 + 360 * ((j * .37 + t * .4) % 1)
        sc_ += blob(ellipse_pts(cx_, tvy - 60 + 60 * math.sin(t * 3 + j), 40 + 30 * ph, 30 + 20 * ph, 14), ("#ff8a7a", "#ffd166", "#7bd389", "#c9a7ff", "#6cc4ff")[j], .85)
    c = lib.clip_rect(tvx - 100, tvy - 170, 380, 220)
    o.append(f'<rect x="{tvx - 100}" y="{tvy - 170}" width="380" height="220" fill="#2f5c86"/><g clip-path="url(#{c})">{sc_}</g>')
    g = lib.rad_grad([(0, "#9fd6ff", .25), (1, "#9fd6ff", 0)], tvx, tvy, 700)
    o.append(f'<circle cx="{tvx}" cy="{tvy}" r="700" fill="url(#{g})"/>')
    o.append(sofa(60, 760, FL - 160, "#7a5a8f"))
    yawn = smooth(W(23) - .1, W(23) + .25, t) * (1 - smooth(W(25) + .1, W(25) + .4, t))
    roll = smooth(W(24), W(25), t)
    if yawn > .4:
        ex = dict(people.EXPR["dima"]["sleepy"])
        ex.update(mouth="o", open=.9 * yawn, shut=.6)
    else:
        ex = dict(people.EXPR["dima"]["dull"])
        ex["look"] = (.9, -.2 - .8 * roll)
    hip = (380.0, FL - 165)
    sc = .62
    d = fig(hip[0], hip[1], sc, ex, feet="sit", lean=-.08, head_ang=-.06 + .1 * yawn,
            arms={"n": ("ang", -.3, .9), "f": ("ang", .3, .5)})
    # значок-сериал за диваном, рука в перчатке на плече Димы
    bx_, byb, bk = 130.0, FL + 150, .78
    bs, hand, head = buyer(bx_, byb, bk, "series", t, 0.0, look=(.8, .3), mouth="grin", seed=8, paddle_on=False)
    o.append(d["svg"])
    o.append(bs)
    sh = (d["head"][0] - 60, d["head"][1] + 150)
    s0 = (bx_ + 80 * bk, byb - 420 * bk)
    o.append(line([s0, ((s0[0] + sh[0]) / 2, min(s0[1], sh[1]) - 40), sh], 22, "#22242c", taper=0, wmin=1, seed=5010))
    o.append(shape(ellipse_pts(sh[0], sh[1], 17, 17, 12), "#fbf9f4", "", w=3.4, seed=5011))
    turn = smooth(W(24), W(25), t)
    o.append(cat(700, FL - 150, .5, t, look=(.9 * (1 - turn) - .9 * turn, -.1), turn=-turn, tilt=10 * turn, blink=.9 if turn > .5 else 0.0))
    z = 1.3 + .15 * ease_io(ramp(t, a, T1("s07") - a)) + .08 * bump(t, W(25))
    return view("".join(o), 520, 880, z, 0, bg="#4b4470")


# ═════════════════════════ s08: «все лоты ушли бесплатно» ═════════════════════════
def frame_s08(t):
    a = T0("s08")
    h = stress(30, .25)
    o = [hall_bg(t)]
    o.append(spotlight(PED[0], FL, 1.0))
    o.append(PR.pedestal(PED[0], PED[1], PED[2], seed=1))
    ag, _ = auctioneer(t, [h], expr="talk" if t < h else "proud", look=(.7, .3))
    o.append(ag)
    jump = bump(t, h, .06, .35)
    spin = math.cos(2 * math.pi * ease_out(ramp(t, h + .02, .6), 2))
    ty_ = PED_TOP - 200 - 90 * jump
    o.append(f'<g transform="translate({PED[0] + 40} {ty_:.1f}) scale({spin:.3f} 1) translate({-PED[0] - 40} {-ty_:.1f})">'
             + tag(PED[0] + 40, ty_, 1.15, 10 * math.sin(t * 3) + damp(t, h + .1, 25, 2, 4)) + '</g>')
    o.append(line([(PED[0] + 40, -400), (PED[0] + 40, PED_TOP - 200 - 90 * jump)], 3, INK, seed=5100))
    down = smooth(h + .1, h + .5, t)
    o.append(dima_fig(860.0, FL + 380, .74, "nervous" if t < h else "glum", .8 * (1 - down), t, look=(-.7, -.7), wobble=.5)["svg"])
    others = crowd(t, look=(-.4, -.5))
    for s_, yb, nm in sorted(others, key=lambda z: z[1]):
        if nm in ("chat",):
            o.append(s_)
    z = 1.1 + .15 * ease_io(ramp(t, a, T1("s08") - a)) + .14 * bump(t, h, .04, .3)
    dx, dy = shake(t, h, 18)
    return view("".join(o), 600 + dx, 860 + dy, z, 0, bg=WALL)


# ═════════════════════════ s09: призыв ═════════════════════════
def frame_s09(t):
    import story_cta_tg as tg
    press = W(33) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=os.path.join(STORY, "common"))


def stand_y(sc):
    """Таз Димы, когда ступни на полу FL."""
    return FL - 590 * sc


def coin(x, y, k=1.0):
    return shape(ellipse_pts(x, y, 30 * k, 30 * k, 18), GOLD, blob(ellipse_pts(x - 8 * k, y - 8 * k, 12 * k, 8 * k, 10), "#ffe8a8"), w=3.4 * k, seed=5200)


def small_clock(x, y, k, t):
    return PR.clock(x, y, 46 * k, angle_h=(t * 90) % 360, angle_m=(t * 400) % 360, seed=9, rim=DIMA_RIM)


def hug_dima(x, sc, t, expr, cpos, clock_svg, look=None, head_ang=0.0, r=60.0):
    """Дима держит предмет двумя руками у груди (предмет между дальней и ближней рукой)."""
    y = stand_y(sc)
    ex = dict(people.EXPR["dima"][expr]) if isinstance(expr, str) else dict(expr)
    if look:
        ex["look"] = look
    arms = {"n": ("ik", (cpos[0] - r - 10, cpos[1] + 20), -1), "f": ("ik", (cpos[0] + r + 10, cpos[1] + 20), -1)}
    hands = {"n": {"dir": (.5, -.8), "curl": (.3, .3, .35, .4), "thumb": .4}, "f": {"dir": (-.5, -.8), "curl": (.3, .3, .35, .4), "thumb": .4}}
    b = fig(x, y, sc, ex, feet="stand", lean=.02, head_ang=head_ang, arms=arms, hands=hands, layers=("legs", "pelvis", "arm_f", "body"))
    n = fig(x, y, sc, ex, feet="stand", lean=.02, head_ang=head_ang, arms=arms, hands=hands, layers=("arm_n",))
    return shadow(x, FL + 12, 150 * sc / .6) + b["svg"] + n["svg"] + clock_svg, b


# ═════════════════════════ s10: «выкупить своё время обратно» ═════════════════════════
def frame_s10(t):
    a = T0("s10")
    o = [hall_bg(t), spotlight(PED[0], FL, 1.0), PR.pedestal(PED[0], PED[1], PED[2], seed=1)]
    cu = smooth(W(38) - .1, W(38) + .3, t)                       # монетка с лапы на пьедестал
    hug = ease_io(ramp(t, W(41) - .1, .45))
    sc = .74
    dx_ = 420.0
    chest = (dx_ + 60, stand_y(sc) - 300 * sc)
    cx_, cy_ = CLK[0] + (chest[0] - CLK[0]) * hug, CLK[1] + (chest[1] - CLK[1]) * hug - 120 * math.sin(math.pi * hug)
    kk = 1.0 - .45 * hug
    clk = life_clock(cx_, cy_, kk, t, .3) if hug < .98 else PR.clock(cx_, cy_, 100 * kk, (t * 18) % 360, (t * 150) % 360, seed=7, rim=DIMA_RIM)
    ccx, ccy = PED[0] + 150, PED_TOP
    o.append(cat(ccx, ccy, .5, t, look=(-.8, .2) if t < W(41) else (-.9, -.3), paw=cu * (1 - smooth(W(39), W(39) + .3, t)), paw_dx=-100,
                 smile=hug, tail=8 * math.sin(t * 3)))
    if t > W(38) - .1:
        px = ccx - 90 * (1 - cu) - 40 * cu
        o.append(coin(px - 30, ccy - 60 * (1 - cu) - 22, .9))
        o.append(PR.sparkles(px - 30, ccy - 30, .9, bump(t, W(38) + .3, .05, .4), t, seed=11))
    if hug < .5:
        o.append(clk)
        g = dima_fig(dx_, stand_y(sc), sc, "hope", 0.0, t, look=(.8, -.3), wobble=.3)["svg"]
    else:
        g, _ = hug_dima(dx_, sc, t, "bliss", (chest[0], chest[1]), clk, r=55)
    o.append(g)
    if hug > .5:
        o.append(PR.heart(chest[0] + 230, chest[1] - 200 - 80 * ramp(t, W(41) + .3, 1.0), .7, bump(t, W(41) + .35, .06, .4), seed=3))
    z = 1.35 + .12 * ease_io(ramp(t, a, T1("s10") - a)) + .06 * bump(t, W(41))
    return view("".join(o), 590, 860 - 40 * hug, z, 0, bg=WALL)


# ═════════════════════════ s11: «каждую неделю мы возвращаем себе один лот» ═════════════════════════
def week_row(t, gold_u):
    o = []
    for j in range(7):
        x = 190 + j * 116
        pu = smooth(W(44) + j * .05, W(44) + j * .05 + .15, t)
        if pu < .02:
            continue
        r = 42 * pu
        fill = "#f4ead8"
        inner = ""
        if j == 0 and gold_u > .02:
            inner = blob(ellipse_pts(x, 220, r * gold_u, r * gold_u, 18), GOLD)
        o.append(shape(ellipse_pts(x, 220, r, r, 18), fill, inner, w=4, seed=5300 + j))
    o.append(PR.sparkles(190, 220, 1.0, gold_u * (1 - smooth(W(49) + .3, W(49) + .6, t)), t, seed=12))
    return "".join(o)


def frame_s11(t):
    a = T0("s11")
    gu = smooth(W(48), W(48) + .25, t)
    o = [hall_bg(t, win=False), shape(lib.rrect(110, 140, 970, 300, 30), "#f6eee0", "", w=4, seed=5310), week_row(t, gu)]
    # часок: у значка-ленты в руке → кот выхватывает → у Димы
    take = ease_io(ramp(t, W(46) - .05, .35))
    give = ease_io(ramp(t, W(47), .4))
    bs, hand, head = buyer(230.0, FL + 160, .9, "feed", t, .1, look=(.7, .2), mouth="grin" if take < .5 else "o", seed=3, paddle_on=False)
    o.append(bs)
    catx = 520.0 - 120 * take + 120 * give
    jump = 90 * math.sin(math.pi * take) * (take < .99)
    cpaw = (catx - 70, FL - 300 - jump)
    sc = .72
    dx_ = 820.0
    chest = (dx_ - 40, stand_y(sc) - 280 * sc)
    if take < .5:
        cp = (hand[0] + 10, hand[1] - 30)
    elif give < .02:
        cp = cpaw
    else:
        cp = (cpaw[0] + (chest[0] - cpaw[0]) * give, cpaw[1] + (chest[1] - cpaw[1]) * give)
    o.append(shadow(catx, FL + 12, 90))
    o.append(cat(catx, FL - jump, .48, t, look=(-.9 if t < W(47) else .9, -.3), paw=take * (1 - give), paw_dx=-120, smile=give, tail=10 * math.sin(t * 4)))
    if give > .9:
        g, _ = hug_dima(dx_, sc, t, "bliss", chest, small_clock(*cp, 1.0, t), r=46)
        o.append(g)
    else:
        o.append(dima_fig(dx_, stand_y(sc), sc, "hope", .25 * give, t, look=(-.8, -.2), wobble=.2)["svg"])
        o.append(small_clock(*cp, 1.0, t))
    z = 1.08 + .1 * ease_io(ramp(t, a, T1("s11") - a)) + .05 * bump(t, W(46))
    dx, dy = shake(t, W(46), 6)
    return view("".join(o), 540 + dx, 830 + dy, z, 0, bg=WALL)


# ═════════════════════════ s12: человек отдаёт соцсетям часики ═════════════════════════
def frame_s12(t):
    a = T0("s12")
    o = [hall_bg(t, win=False)]
    give = ease_io(ramp(t, W(53) - .1, .35))
    stash = ease_io(ramp(t, W(53) + .25, .45))
    again = smooth(W(54) + .15, W(54) + .4, t)
    sc = .7
    px, py = 330.0, FL - 590 * sc * 1.02
    reach = (px + 240 * sc + 200 * give * (1 - stash), py - 330 * sc)
    ex = dict(people.EXPR["youth"]["serious"])
    ex["look"] = (.8, .0)
    pf = people.person("youth", px, py, sc, ex, feet=people.stand_kw(px, py, sc, who="youth")["feet"], arms={"n": ("ik", reach, -1)},
                       hands={"n": {"dir": (1, -.2), "curl": (.4, .4, .45, .5), "thumb": .4}})
    o.append(shadow(px, FL + 12, 150))
    bs, hand, head = buyer(800.0, FL + 40, .95, "feed", t, .05, look=(-.8, .1), mouth="grin", seed=3, paddle_on=False, fat=1.0 + .1 * stash)
    o.append(bs)
    o.append(pf["svg"])
    wr = pf["wrist"]["n"]
    if stash < .98:
        tx_, ty_ = 800 - 55, FL + 40 - 330 * .95                  # нагрудный карман фрака
        cp = (wr[0] + 30 + (tx_ - wr[0] - 30) * stash, wr[1] - 20 + (ty_ - wr[1] + 20) * stash - 90 * math.sin(math.pi * stash))
        o.append(f'<g opacity="{1 - smooth(.8, 1.0, stash):.2f}">{small_clock(cp[0], cp[1], 1.0 - .45 * stash, t)}</g>')
    if again > .02:
        o.append(f'<g opacity="{again:.2f}">{small_clock(wr[0] + 30, wr[1] - 20, again, t + 1)}</g>')
    z = 1.2 + .12 * ease_io(ramp(t, a, T1("s12") - a)) + .06 * bump(t, W(53))
    return view("".join(o), 560, 900, z, 0, bg=WALL)


# ═════════════════════════ s13: песок — прямо в рот ленте ═════════════════════════
def frame_s13(t):
    a = T0("s13")
    o = [hall_bg(t, win=False)]
    fat = 1.0 + .35 * ramp(t, a, T1("s13") - a)
    bx_ = 540.0
    bk = 1.25
    bs, hand, head = buyer(bx_, FL + 160, bk, "feed", t, 0.0, look=(0, -.6), mouth="chew", chew=t * 14, seed=3, paddle_on=False, fat=fat)
    o.append(bs)
    mouth = (head[0], head[1] + 66 * bk)
    two = smooth(W(56) - .1, W(56) + .15, t)
    for j, (hx, ph) in enumerate(((bx_ - 290, 0.0), (bx_ + 290, .5))):
        u = 1.0 if j == 0 else two
        if u < .02:
            continue
        hy = head[1] - 330 + (1 - u) * -900
        o.append(PR.giant_hourglass(hx, hy, .8, sand_top=.7 - .2 * ramp(t, a, 2), sand_bot=0.0, stream=1.0, t=t, seed=j, chain=0.0))
        tip = (hx, hy + 200)
        end = (mouth[0] + (-14 if j == 0 else 14), mouth[1])
        o.append(grains(bez(tip, (tip[0] + (end[0] - tip[0]) * .2, end[1] + 40), end), t, n=26, seed=j, speed=2.2, col="#e8c27a"))
    z = 1.0 + .12 * ease_io(ramp(t, a, T1("s13") - a)) + .08 * bump(t, W(56))
    dx, dy = shake(t, W(56), 8)
    return view("".join(o), 540 + dx, 760 + dy, z, 0, bg=WALL)


# ═════════════════════════ s14: целый месяц в году — лист улетает в зал ═════════════════════════
def tear_sheet(x, y, k=1.0, rot=0.0, fy=1.0):
    o = shape(lib.rect_pts(-130, 0, 130, 250), "#fbf6ea", "".join(blob(ellipse_pts(-90 + 45 * (j % 5), 60 + 45 * (j // 5), 7, 7, 8), "#9a8f80")
                                                            for j in range(20)) + blob(lib.rect_pts(-130, 0, 130, 34), TAG_RED), w=4, seed=5400)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f}) scale({k:.3f} {k * fy:.3f})">{o}</g>'


def frame_s14(t):
    a = T0("s14")
    h = stress(67, .4)
    o = [hall_bg(t), spotlight(PED[0], FL, 1.0), PR.pedestal(PED[0], PED[1], PED[2], seed=1)]
    ag, _ = auctioneer(t, [h], expr="talk" if t < h else "proud", look=(.7, .3))
    o.append(ag)
    bx, by = PED[0], PED_TOP - 300
    o.append(shape(lib.rect_pts(bx - 140, by - 20, bx + 140, by + 300), "#8f5a33", "", w=4, seed=5410))
    for j in range(4):
        o.append(line([(bx - 90 + 60 * j, by - 30), (bx - 90 + 60 * j, by + 10)], 8, "#9aa0a8", taper=0, wmin=1, seed=5411 + j))
    o.append(tear_sheet(bx, by + 12, 1.0))
    fu = ramp(t, W(62), 1.4)
    if fu > 0:
        e = ease_out(fu, 2)
        fx_ = bx + (1180 - bx) * e
        fy_ = by + 12 - 240 * math.sin(math.pi * min(1, e * 1.3)) + 700 * e * e
        o.append(tear_sheet(fx_, fy_, 1.0 - .2 * e, 40 * e + 25 * math.sin(t * 9) * e, .55 + .45 * math.cos(t * 10)))
    else:
        o.append(tear_sheet(bx, by + 12, 1.0))
    if t < W(62) + .15:
        o.append(tear_sheet(bx, by + 12, 1.0, 0, 1 - 1.4 * ramp(t, W(62) - .05, .2)))
    ru = lambda n: smooth(W(62) + .3, W(62) + .6, t) * (.6 + .4 * math.sin(t * 9 + len(n)))
    for s_, yb, nm in sorted(crowd(t, ru, look=(.6, -.8)), key=lambda z: z[1]):
        if nm in ("feed", "series", "game"):
            o.append(s_)
    jump = bump(t, h, .06, .35)
    o.append(tag(PED[0] - 100, PED_TOP - 60 * jump, .8, 10 * math.sin(t * 3) + damp(t, h + .05, 25, 2, 4)))
    pan = ease_io(ramp(t, W(62), 1.2))
    back = ease_io(ramp(t, h - .5, .4))
    cx = 700 + 300 * pan - 330 * back
    cy = 700 + 300 * pan - 100 * back
    z = 1.5 - .45 * pan + .25 * back + .1 * bump(t, h, .04, .3)
    dx, dy = shake(t, h, 16)
    return view("".join(o), cx + dx, cy + dy, z, 0, bg=WALL)


# ═════════════════════════ s15: «Дима впервые поднял руку» — зал оборачивается ═════════════════════════
def frame_s15(t):
    a = T0("s15")
    up = ease_out(ramp(t, W(70) - .15, .35), 3)
    turn = ease_io(ramp(t, W(71), .3))
    sc = .78
    x = 330.0
    y = FL + 300 - 40 * up
    ex = "resolve" if up > .3 else "unsure"
    ru = .1 + .9 * up                                             # рука вверх и в сторону от лица, не к часам на пьедестале
    hn = (x + 60 * sc + 120 * sc * ru, y - 30 * sc - 1100 * sc * ru)
    dg = dima_fig(x, y, sc, ex, 0.0, t, look=(-.3, -.9) if up > .3 else (0, .5), wobble=.15, lean=.08 * (1 - up), head_ang=-.05 * up,
                  near_arm=("ang", .12, .2), far_arm=("ik", hn, 1))["svg"]
    lk = lambda nx: (clamp((x - nx) / 300, -1, 1) * turn + -.5 * (1 - turn), .3 * turn - .4 * (1 - turn))
    o = [hall_bg(t)]
    ag, _ = auctioneer(t, [], expr="wow" if turn > .5 else "talk", look=(.9 * turn, .5 * turn))
    o += [PR.pedestal(PED[0], PED[1], PED[2], seed=1), life_clock(CLK[0], CLK[1], 1.0, t), ag]
    rows = [("chat", -60.0, FL + 380, 1.0, 1), ("alarm", 700.0, FL + 520, 1.1, 2), ("feed", 990.0, FL + 480, 1.1, 3),
            ("series", 1180.0, FL + 360, 1.0, 4)]
    fg = [(y + 590 * sc, dg)]
    for nm, bx, yb, k, sd in rows:
        bsv, _, _ = buyer(bx, yb, k, nm, t, .3 * (1 - turn), look=lk(bx), turn=clamp((x - bx) / 400, -1, 1) * turn,
                          mouth="o" if turn > .4 else "smug", seed=sd)
        fg.append((yb, bsv))
    for _, sv in sorted(fg, key=lambda z: z[0]):
        o.append(sv)
    z = .8 + .25 * ease_io(ramp(t, a, T1("s15") - a)) + .07 * bump(t, W(70))
    dx, dy = shake(t, W(71), 8)
    return view("".join(o), 560 + dx, 1080 - 120 * ease_io(ramp(t, a, T1("s15") - a)) + dy, z, 0, bg=WALL)


# ═════════════════════════ s16: «Этот час мой» — молоток зависает ═════════════════════════
FR16 = 38.0


def frame_s16(t):
    a = T0("s16")
    low = ease_io(ramp(t, W(76), .5))
    fr = FR16 - (FR16 - 8) * low + 2.5 * math.sin(t * 23) * (1 - low)
    o = [hall_bg(t), PR.pedestal(PED[0], PED[1], PED[2], seed=1)]
    ag, _ = auctioneer(t, [], expr="wow", look=(.8, .6), freeze=fr)
    o.append(ag)
    hold = ease_out(ramp(t, W(75) - .1, .3), 3)
    sc = .82
    x = 860.0
    chest = (x - 40, stand_y(sc) + 120 - 300 * sc)
    yd = stand_y(sc) + 120
    hn = (x + 60 * sc + 120 * sc, yd - 30 * sc - 900 * sc)       # рука поднята за головой (как в s15), часок в ладони
    cp = (hn[0] + (chest[0] - hn[0]) * hold + 230 * math.sin(math.pi * hold), hn[1] - 40 + (chest[1] - hn[1] + 40) * hold)
    clk = small_clock(cp[0], cp[1], 1.3, t * .2)
    ex = dict(people.EXPR["dima"]["resolve"])
    ex["look"] = (-.6, -.3)
    if hold > .5:
        g, _ = hug_dima(x, sc, t, ex, chest, clk)
        g = f'<g transform="translate(0 120)">{g}</g>'
    else:
        g = dima_fig(x, yd, sc, ex, 0.0, t, wobble=0.0, near_arm=("ang", .12, .2), far_arm=("ik", hn, 1))["svg"] + clk
    o.append(g)
    bsv, _, _ = buyer(80.0, FL + 520, 1.05, "alarm", t, 0.0, look=(.9, -.2), turn=.6, mouth="o", seed=2)
    o.append(bsv)
    o.append(PR.sparkles(cp[0], cp[1], 1.1, smooth(W(75), W(75) + .2, t) * (1 - smooth(W(76) + .4, W(76) + .8, t)), t, seed=13))
    z = 1.05 + .2 * ease_io(ramp(t, a, T1("s16") - a))
    return view("".join(o), 620, 900, z, .8 * math.sin(t * 1.5), bg=WALL)


# ═════════════════════════ s17: кот купил солнечное пятно ═════════════════════════
SILL = WIN[3] + 30


def frame_s17(t):
    a = T0("s17")
    h = stress(81, .2)
    su = ease_out(ramp(t, h, .35), 2)
    o = [hall_bg(t)]
    o.append(sun_patch(su, t))
    if t > h - .02 and su < .99:
        o.append(blob(ellipse_pts((WIN[0] + WIN[2]) / 2 + 20, WIN[1] + 40 + (SILL - WIN[1] - 40) * su, 120, 30, 20), "#ffe58a", .9))
    pu = smooth(W(79) - .1, W(79) + .15, t) * (1 - smooth(h + .3, h + .6, t))
    cx_ = (WIN[0] + WIN[2]) / 2 + 30
    if pu > .05:                                                  # табличка за котом: ручка уходит за тело к лапе, диск над ухом
        o.append(paddle(cx_ - 40, SILL - 50 - 100 * pu, .45, -22 * pu))
    o.append(cat(cx_, SILL, .48, t, look=(-.3, -.6) if t < h else (0, .3), paw=pu, paw_dx=-30, smile=su, squint=su * .8, tail=10 * math.sin(t * 3),
                 flame_e=1.0 + .4 * su))
    o.append(PR.sparkles(cx_, SILL - 120, 1.2, bump(t, h + .1, .06, .5), t, seed=14))
    z = 2.0 + .15 * ease_io(ramp(t, a, T1("s17") - a)) + .08 * bump(t, h)
    dx, dy = shake(t, h, 8)
    return view("".join(o), cx_ - 20 + dx, SILL - 170 + dy, z, 0, bg=WALL)


# ═════════════════════════ s18: петля — ракурс хука, Дима держит свои часы ═════════════════════════
def frame_s18(t):
    a = T0("s18")
    cx_ = (WIN[0] + WIN[2]) / 2 + 30
    stretch = bump(t, W(85), .25, .6)
    catsvg = cat(cx_, SILL, .5, t, look=(0, .3), smile=1.0, squint=.8, sy=1 + .12 * stretch, sx=1 - .05 * stretch, flame_e=1.3)
    catsvg += tag(cx_ + 50, SILL - 150, .55, 18 + 10 * math.sin(t * 2.4))
    sc = .74
    x = 600.0                                                     # место и рост Димы из хука s01: петля к тому же ракурсу
    chest = (x - 30, stand_y(sc) - 300 * sc)
    g, _ = hug_dima(x, sc, t, "bliss", chest, PR.clock(chest[0], chest[1], 66, (t * 18) % 360, (t * 150) % 360, seed=7, rim=DIMA_RIM), r=66)
    g = f'<g transform="translate(0 {470 + 590 * sc - 0:.1f})">{g}</g>'
    ru = lambda n: .1
    cr = crowd(t, ru, look=(-.2, -.3))
    o = [hall_bg(t), sun_patch(1.0, t), catsvg, PR.pedestal(PED[0], PED[1], PED[2], seed=1)]
    ag, _ = auctioneer(t, [], expr="calm", look=(.5, .4))
    o.append(ag)
    fg = sorted([(yb, s_) for s_, yb, _ in cr] + [(FL + 900, g)], key=lambda z: z[0])
    o += [s_ for _, s_ in fg]
    u = ease_io(ramp(t, a, T1("s18") - a))
    cx, cy, s_ = 560 + 60 * u, 1000 + 150 * u, .8 - .18 * u
    return view("".join(o), cx, cy, s_, -2.0 * u, bg=WALL)


FRAMES = {k[6:]: v for k, v in dict(globals()).items() if k.startswith("frame_s")}


def frame(sid, t):
    if sid != "s09":
        lib.DEFS.clear()
    return FRAMES[sid](t)
