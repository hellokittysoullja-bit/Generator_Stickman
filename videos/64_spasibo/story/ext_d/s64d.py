"""Рилс 64 «спасибо», группа D: учительница — воспоминание и звонок.
s02 (1.42–4.40, whip): класс-воспоминание (полоса света формы окна, чистая доска). Молодая учительница склоняется к парте маленького
    Димы, у неё его лист со штрихами; «учительнице» (2.29) ладонь ему на плечо, он сияет; «но всё» (3.25) картинка отъезжает и
    оказывается старой фотографией в рамке в руке взрослого Димы; «откладывал» (3.65) рука кладёт рамку лицом вниз на стол.
s14 (33.92–35.90): комната днём, Дима у окна в полный рост с мобильником у уха и письмом в руке; «учительнице» (33.92) читает,
    голос дрожит; «по телефону» (34.53) крепнет, выпрямляется; деревья за окном качаются.
s15 (35.90–38.56, whip): дом пожилой учительницы — кресло, торшер с небольшим чётким кругом, столик с кружкой; мобильник у уха;
    «молчала» (36.38) замирает, глаза влажные, ладонь к губам; «потом» (37.17) плечи дрогнули, «засмеялась» (37.48) смеётся,
    запрокинув голову, вытирает слезу пальцем.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Люди и кот — common/people.py, комната — common/room.py, предметы —
common/props.py; здесь только фон класса и дома учительницы и хореография."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import people as P  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import blob, clamp, ease_io, ease_out, ellipse_pts, line, rect_pts, shape, smooth, svg  # noqa: E402

INK = lib.INK
WORDS = lib.words()


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def mix_expr(a, b, u):
    """Плавный переход мимики: числа и пары — линейно, категории (рот, брови) — от b после середины."""
    u = clamp(u)
    o = {}
    for k in set(a) | set(b):
        va, vb = a.get(k), b.get(k)
        if va is None:
            va = vb if not isinstance(vb, (int, float)) else 0.0
        if vb is None:
            vb = va if not isinstance(va, (int, float)) else 0.0
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            o[k] = va + (vb - va) * u
        elif isinstance(va, tuple) and isinstance(vb, tuple):
            o[k] = lerp2(va, vb, u)
        else:
            o[k] = vb if u > .5 else va
    return o


def speaking(t, amp=.3, base=.08):
    """Раскрытие рта по словам голоса: 0 между словами, слоги — по синусу."""
    for w in WORDS:
        if w["start"] - .03 <= t <= w["end"]:
            ph = (t - w["start"]) / max(.08, (w["end"] - w["start"])) * max(1, len(w["word"]) // 3)
            return base + amp * abs(math.sin(math.pi * ph))
    return 0.0


def frame_svg(body, cx, cy, s, rot=0.0, bg="#f4efe4", over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def vignette(u, col="#7a4a22", op=.55):
    """Тёплая виньетка воспоминания по краям экрана (не пятно света)."""
    if u <= 0.01:
        return ""
    g = lib.rad_grad([(0, col, 0), (.62, col, 0), (1, col, op * u)], 540, 960, 1150, 1150 * 1.0)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


# ═════════════════════════════ s14: Дима у окна с мобильником и письмом ═════════════════════════════
S14_X = -20.0
S14_SC = .86


def s14(t):
    sc = S14_SC
    hip = (S14_X, R.FL - 640 * sc)
    rw = R.window_scene(t, "day", sway=1.5)
    # голос дрожит → крепнет (34.53–34.69), выпрямляется
    u = ease_io(clamp((t - 34.50) / .34))
    nerv = {"brows": "worry", "mouth": "talk", "open": .1, "smile": 0.0, "lid": .92, "look": (.5, .55), "bags": False}
    stead = {"brows": "calm", "mouth": "talk", "open": .1, "smile": .45, "lid": .78, "look": (.45, .3), "bags": False}
    ex = mix_expr(nerv, stead, u)
    sp = speaking(t, amp=.26 + .12 * u, base=.06)
    ex["open"] = sp
    if t > 35.25:     # дочитал — губы сомкнулись в улыбку, ждёт ответа
        ex["mouth"] = "smile"
        ex["smile"] = .55 * ease_out(clamp((t - 35.25) / .3))
        ex["lid"] = .7
    trem = (1 - u) * (.022 * math.sin(t * 2 * math.pi * 9.0) + .012 * math.sin(t * 2 * math.pi * 13.3))
    shrug = .38 * (1 - u)
    lean = lerp(.13, -.03, u) + .01 * math.sin(t * 2.1)
    breath = .006 * math.sin(t * 2 * math.pi * .45)
    feet = P.stand_kw(hip[0], hip[1], sc, spread=70)["feet"]
    kw = dict(feet=feet, flip=True, shrug=shrug, lean_add=lean - .02 + breath, head_add=trem + lerp(.08, -.04, u))
    # письмо в дальней руке у груди: пальцы огибают правый край листа, большой палец за листом; дрожит, пока голос дрожит
    let_d = (1 - u) * 3.5 * math.sin(t * 2 * math.pi * 7.3)
    lk = sc * 1.0
    L = (hip[0] - 250 * sc, hip[1] - (330 + 25 * u) * sc + let_d)
    rot_l = -4 + let_d * .4
    xr = L[0] + 100 * lk
    G = (xr - 6 * lk, L[1] + 60 * lk)
    arms = {"f": ("ik", (2 * hip[0] - (G[0] + 64 * lk), G[1] + 22 * lk), -1)}
    hands = {"f": {"kind": "none"}}
    base = P.dima(hip[0], hip[1], sc, ex, "mobile_letter", layers=("legs", "pelvis", "arm_f", "body"), arms=arms, hands=hands, **kw)
    gb, gf = P.grip_svg("dima", G, 12 * lk, +1, k=lk * .95, h=70, seed=930)
    letter = PR.letter(L[0], L[1], k=lk, rot=rot_l, w=200, h=260, write=1.0, seed=3)
    mob = P.mobile_at_ear(base, sc, flip=True)
    armn = P.dima(hip[0], hip[1], sc, ex, "mobile_letter", layers=("arm_n",), arms=arms, hands=hands, **kw)
    body = rw["bg"] + base["svg"] + gb + letter + gf + mob + armn["svg"]
    a = ease_io(clamp((t - 33.72) / 2.4))
    cx, cy, s = lerp(-170, -110, a), lerp(930, 780, a), lerp(.95, 1.1, a)
    cx += 6 * math.sin(t * .9)
    return frame_svg(body, cx, cy, s, rot=.4 * math.sin(t * .7))


# ═════════════════════════════ s15: дом пожилой учительницы ═════════════════════════════
S15_HIP = (480.0, 1300.0)
S15_SC = 1.15
CH_GREEN, CH_GREEN_SH, CH_GREEN_HI = "#6d8a5c", "#516b43", "#89a677"


def home_bg(t):
    """Комната учительницы: тёплые обои с полоской, плинтус, пол, картинка без букв, торшер с небольшим кругом света."""
    o = [blob(rect_pts(-600, -600, 1700, 1700), "#d8c4a4")]
    for i in range(-12, 40):
        x = i * 64
        o.append(blob(rect_pts(x, -600, x + 22, 1700), "#cfb995", .8))
        for j in range(-6, 26):     # мелкий узор-веточка штрихом (не буквы)
            y = j * 96 + (48 if i % 2 else 0)
            o.append(line([(x + 43, y), (x + 43, y + 22)], 2.0, "#bfa47c", taper=.4, wmin=.3, seed=900 + i * 40 + j, op=.7))
            o.append(line([(x + 43, y + 8), (x + 52, y + 2)], 1.8, "#bfa47c", taper=.4, wmin=.3, seed=1900 + i * 40 + j, op=.7))
    o.append(shape(rect_pts(-600, 1640, 1700, 1700), "#ead8b8", blob(rect_pts(-600, 1680, 1700, 1700), "#c9b18c"), w=3.0, seed=950))
    o.append(blob(rect_pts(-600, 1700, 1700, 2600), "#8a5a3a"))
    for i in range(-6, 22):
        o.append(line([(-600, 1700 + i * 60), (1700, 1700 + i * 60 + 4)], 2.2, "#6e4428", taper=0, wmin=1, seed=960 + i, op=.6))
    o.append(R.wall_picture(860, 470, 250, 180, "day", seed=8))
    # торшер слева за креслом: небольшой чёткий круг света вокруг абажура
    lx, ly, lk = 175.0, 1700.0, 2.2
    o.append(PR.lamp_floor(lx, ly, k=lk, on=1.0, seed=4))
    top = ly - 360 * lk
    o.append(PR.glow(lx, top, r=150, u=.85 + .05 * math.sin(t * 3.1)))
    return "".join(o)


def armchair_back(x, y):
    """Спинка кресла с «ушами» (ставить ДО учительницы); (x, y) — таз сидящей."""
    o = []
    back = [(x - 260, y + 60, 1), (x - 290, y - 380), (x - 250, y - 560, 1), (x - 120, y - 620), (x + 60, y - 610, 1), (x + 170, y - 540),
            (x + 200, y - 380), (x + 190, y + 60, 1)]
    o.append(shape(back, CH_GREEN, blob([(x - 300, y - 300), (x - 160, y - 640), (x - 120, y - 300), (x - 150, y + 80), (x - 300, y + 80)], CH_GREEN_SH, .8)
                   + blob([(x + 40, y - 600), (x + 150, y - 560), (x + 120, y - 520), (x + 20, y - 570)], CH_GREEN_HI, .9)
                   + "".join(line([(x - 200 + 70 * i, y - 560 + abs(i - 2) * 14), (x - 210 + 70 * i, y + 40)], 2.0, CH_GREEN_SH, seed=980 + i, op=.6)
                             for i in range(6)), w=5.0, seed=979))
    return "".join(o)


def armchair_front(x, y):
    """Сиденье и подлокотники кресла (после таза и ног, ДО туловища — подлокотник ближний кладётся отдельно armchair_arm)."""
    o = []
    seat = [(x - 250, y - 40, 1), (x + 230, y - 60, 1), (x + 280, y + 70, 1), (x + 270, y + 230, 1), (x - 240, y + 240, 1)]
    o.append(shape(seat, CH_GREEN_SH, blob(rect_pts(x - 260, y + 120, x + 300, y + 260), "#3f5636", .9), w=5.0, seed=990))
    for lx in (x - 220, x + 240):
        o.append(shape(rect_pts(lx - 18, y + 230, lx + 18, y + 330), "#5a3a24", "", w=3.0, seed=991 + int(lx) % 7))
    return "".join(o)


def armchair_arm(x, y):
    """Ближний (правый) подлокотник-валик — поверх бёдер."""
    arm = [(x + 150, y - 150, 1), (x + 330, y - 170, 1), (x + 360, y - 120), (x + 340, y + 200, 1), (x + 170, y + 210, 1)]
    return shape(arm, CH_GREEN, blob([(x + 150, y + 40), (x + 360, y + 20), (x + 360, y + 220), (x + 150, y + 220)], CH_GREEN_SH, .85)
                 + blob(ellipse_pts(x + 270, y - 150, 80, 22, 14), CH_GREEN_HI, .9), w=5.0, seed=995)


def side_table_mug(t):
    o = [shape(rect_pts(985, 1260, 1005, 1700), "#6e4a2c", "", w=2.6, seed=1000)]
    o.append(shape(ellipse_pts(995, 1250, 150, 30, 20), "#a8784a", blob(ellipse_pts(1000, 1256, 140, 22, 18), "#c48e5a", .7), w=3.2, seed=1001))
    o.append(PR.mug(960, 1248, k=1.25, col="blue", coffee=True, steam=.8, t=t, handle=-1, seed=5))
    return "".join(o)


def _teacher_parts(t):
    """Хореография s15: мимика, наклон, цели рук. Возвращает dict."""
    ph_freeze = ease_io(clamp((t - 36.40) / .38))           # рука к губам, замерла
    ph_then = clamp((t - 37.17) / .3)                         # «потом» — плечи дрогнули
    ph_laugh = ease_out(clamp((t - 37.46) / .3))              # засмеялась
    ph_wipe = ease_io(clamp((t - 37.98) / .35))               # вытирает слезу
    listen = {"brows": "up", "mouth": "talk", "open": 0.0, "smile": .15, "lid": .9, "look": (.35, .1)}
    moved = {"brows": "sad", "mouth": "wobble", "open": 0.0, "smile": 0.0, "lid": .72, "look": (.25, .3), "tear": 1.0, "laugh": 0.0}
    smiling = {"brows": "sad", "mouth": "talk", "open": .05, "smile": 1.0, "lid": .55, "look": (.25, .25), "tear": 1.0, "laugh": .35}
    laugh = {"brows": "up", "mouth": "talk", "open": .85, "smile": 1.0, "lid": .5, "laugh": 1.0, "tear": 1.0}
    wipe = {"brows": "calm", "mouth": "talk", "open": .3, "smile": 1.0, "lid": .5, "laugh": .75, "tear": 1.0, "tear_run": .6}
    ex = dict(listen)
    ex["tear"] = 0.0
    ex = mix_expr(ex, moved, ph_freeze)
    ex = mix_expr(ex, smiling, ease_io(ph_then))
    ex = mix_expr(ex, laugh, ph_laugh)
    ex = mix_expr(ex, wipe, ph_wipe)
    # смех толчками «ха-ха»
    if t > 37.46:
        hh = abs(math.sin((t - 37.46) * 2 * math.pi * 3.2))
        ex["open"] = ex.get("open", 0) * (.6 + .4 * hh)
    # моргание в начале (живая, пока слушает)
    if 35.95 < t < 36.08:
        ex["closed"] = math.sin(math.pi * (t - 35.95) / .13)
    lean = .04 + .015 * math.sin(t * 2 * math.pi * .4) * (1 - ph_freeze)       # дышит, на «молчала» — замирает
    head = .03 * math.sin(t * 1.3) * (1 - ph_freeze)
    shrug = 0.0
    if t > 37.17:       # плечи дрогнули
        tr = math.exp(-(t - 37.17) * 2.0)
        shrug = .18 * abs(math.sin((t - 37.17) * 2 * math.pi * 3.2)) * (1 - .4 * ph_wipe) + .05 * tr
    lean += lerp(0, -.14, ph_laugh) * (1 - .55 * ph_wipe)
    head += lerp(0, -.32, ph_laugh) * (1 - .6 * ph_wipe)
    return dict(ex=ex, lean=lean, head=head, shrug=shrug, ph_freeze=ph_freeze, ph_laugh=ph_laugh, ph_wipe=ph_wipe)


def _rotv(v, a):
    c, s_ = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s_, v[0] * s_ + v[1] * c)


def s15(t):
    hx, hy = S15_HIP
    sc = S15_SC
    st = _teacher_parts(t)
    feet = {"n": ((hx + 330 * sc, hy + 300 * sc), 0.0), "f": ((hx + 290 * sc, hy + 306 * sc), 0.0)}
    kw = dict(feet=feet, shrug=st["shrug"], lean_add=st["lean"], head_add=st["head"])
    # первый проход — где голова (цели рук от неё)
    probe = P.teacher("old", hx, hy, sc, st["ex"], "mobile", layers=("body",), **kw)
    hd = probe["head"]
    pk = P.pose_kw("mobile", hx, hy, sc * P.HEIGHT.get("teacher_o", 1.0) / P.HEIGHT.get("teacher_o", 1.0), "teacher_o")
    ang = 0.04 * .5 + st["lean"] * .5 + st["head"]
    # мобильник у ближнего уха — рука следует за головой
    ear = (hd[0] + _rotv((-150, 120), ang)[0] * sc, hd[1] + _rotv((-150, 120), ang)[1] * sc)
    arm_n = ("ik", ear, 1)
    # дальняя рука: колени → губы → грудь → глаз
    rest = (hx + 250 * sc, hy - 40 * sc)
    mouth = (hd[0] + _rotv((40, 230), ang)[0] * sc, hd[1] + _rotv((40, 230), ang)[1] * sc)
    chest = (hx + 150 * sc, hy - 190 * sc)
    eye = (hd[0] + _rotv((0, 120), ang)[0] * sc, hd[1] + _rotv((0, 120), ang)[1] * sc)
    w = lerp2(rest, mouth, st["ph_freeze"])
    w = lerp2(w, chest, st["ph_laugh"])
    w = lerp2(w, eye, st["ph_wipe"])
    hf = {"dir": (.1, -1), "curl": (.15, .15, .2, .25), "spread": .1, "thumb": .2}
    if st["ph_freeze"] < .3:
        hf = {"dir": (1, .2), "curl": (.35, .35, .4, .45), "thumb": .35}
    if st["ph_laugh"] > .5:
        hf = {"dir": (-.35, -1), "curl": (.15, .15, .2, .25), "spread": .12, "thumb": .2}
    if st["ph_wipe"] > .4:
        hf = {"dir": (.15, -1), "curl": (0, .8, .85, .85), "spread": .05, "thumb": .7}
    arms = {"n": arm_n, "f": ("ik", w, -1)}
    hands = {"n": {"dir": (.15, -1), "curl": (.6, .65, .7, .7), "thumb": .7}, "f": hf}
    base = P.teacher("old", hx, hy, sc, st["ex"], None, arms=arms, hands=hands, layers=("legs", "pelvis"), **kw)
    torso = P.teacher("old", hx, hy, sc, st["ex"], None, arms=arms, hands=hands, layers=("body",), **kw)
    armf = P.teacher("old", hx, hy, sc, st["ex"], None, arms=arms, hands=hands, layers=("arm_f",), **kw)
    armn = P.teacher("old", hx, hy, sc, st["ex"], None, arms=arms, hands=hands, layers=("arm_n",), **kw)
    mob = P.mobile_at_ear(torso, torso["scale"])
    body = (home_bg(t) + armchair_back(hx, hy) + armchair_front(hx, hy) + base["svg"] + torso["svg"] + armf["svg"] + mob + armn["svg"]
            + side_table_mug(t))
    a = ease_io(clamp((t - 35.70) / 3.0))
    cx, cy, s = lerp(600, 580, a), lerp(1010, 900, a), lerp(1.05, 1.28, a)
    if t > 37.46:     # мини-тряска на смехе
        e = math.exp(-(t - 37.46) * 3.0)
        cx += 7 * e * math.sin((t - 37.46) * 61)
        cy += 5 * e * math.sin((t - 37.46) * 47 + 1)
    return frame_svg(body, cx, cy, s, rot=.3 * math.sin(t * .8))


def frame(sid, t):
    lib.dyn_begin()
    lib.DEFS.clear()
    return {"s14": s14, "s15": s15}[sid](t)
