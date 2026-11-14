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


# ═════════════════════════════ s02: класс-воспоминание → фото в рамке в руке взрослого Димы ═════════════════════════════
T_SPAS, T_UCH, T_NO, T_OTKL = 1.42, 2.29, 3.25, 3.65
CFL = 1560.0                                   # пол класса
CLS_BOX = (-400.0, 300.0, 1480.0, 1710.0)      # область класса, что видна на фото (4:3)
Q_PH = 160.0 / (CLS_BOX[2] - CLS_BOX[0])       # класс → фото (фото 160×120 в единицах рамки)
CLS_C = ((CLS_BOX[0] + CLS_BOX[2]) / 2, (CLS_BOX[1] + CLS_BOX[3]) / 2)
T_HIP = (470.0, 0.0)
T_SC = .7
K_SC = .72
K_HIP = (800.0, 0.0)
DESK2 = (600.0, 760.0)
FR_K = 1.6
import room as _R  # noqa: E402,F811


def _sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def _blinkv(t, times, dur=.15):
    v = 0.0
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


def _set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def class_bg(t):
    """Класс: стена, панель, чистая доска без мела, окно слева с полосой света формы окна, пол."""
    x0, y0, x1, y1 = CLS_BOX
    o = [blob(rect_pts(x0 - 300, y0 - 300, x1 + 300, CFL), "#e2d6b4")]
    o.append(shape(rect_pts(x0 - 300, 1250, x1 + 300, CFL), "#a9b98e", blob(rect_pts(x0 - 300, 1250, x1 + 300, 1268), "#c3d0a6"), w=3.4, seed=1100))
    o.append(blob(rect_pts(x0 - 300, CFL, x1 + 300, y1 + 400), "#b98a5a"))
    for i in range(12):
        yy = CFL + 18 + i * 30 + i * i * 2
        o.append(line([(x0 - 300, yy), (x1 + 300, yy + 3)], 2.2, "#8f6640", taper=0, wmin=1, seed=1110 + i, op=.55))
    o.append(line([(x0 - 300, CFL), (x1 + 300, CFL)], 4.0, seed=1109))
    # окно слева: рама, небо, ветка
    wx0, wy0, wx1, wy1 = -330.0, 430.0, 60.0, 1130.0
    sky = blob(rect_pts(wx0, wy0, wx1, wy1), "#cfe6ef") + blob(rect_pts(wx0, wy0 + 420, wx1, wy1), "#e8f2ea", .8)
    sway = 6 * math.sin(t * 1.3)
    sky += line([(wx0, 700), (-150 + sway, 640), (-40 + sway * 1.4, 600)], 9, "#6e4a2c", taper=.5, seed=1120)
    for j, (lx, ly) in enumerate(((-170, 625), (-90, 600), (-40, 620), (-120, 660))):
        sky += blob(ellipse_pts(lx + sway * 1.2, ly, 46, 26, 12), "#8fb86a", .95)
    o.append(shape(rect_pts(wx0, wy0, wx1, wy1), "#cfe6ef", sky, w=4.6, seed=1121))
    for xs in ((wx0 + wx1) / 2,):
        o.append(shape(rect_pts(xs - 10, wy0, xs + 10, wy1), "#f1ece0", "", w=3.0, seed=1122))
    o.append(shape(rect_pts(wx0, (wy0 + wy1) / 2 - 10, wx1, (wy0 + wy1) / 2 + 10), "#f1ece0", "", w=3.0, seed=1123))
    o.append(shape(rect_pts(wx0 - 24, wy1, wx1 + 24, wy1 + 26), "#f1ece0", "", w=3.4, seed=1124))
    # полоса света формы окна на стене и полу (четыре стекла, чёткие края)
    def pane(a, b, c, d):
        return f'<polygon points="{" ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in (a, b, c, d))}" fill="#fff4d2" opacity=".45"/>'
    sh = 330.0
    gx = [wx0, (wx0 + wx1) / 2 - 10, (wx0 + wx1) / 2 + 10, wx1]
    gy = [wy0, (wy0 + wy1) / 2 - 10, (wy0 + wy1) / 2 + 10, wy1]
    for (ax, bx) in ((gx[0], gx[1]), (gx[2], gx[3])):
        for (ay, by) in ((gy[0], gy[1]), (gy[2], gy[3])):
            dx, dy = 470.0, 330.0
            o.append(pane((ax + dx + (ay - wy0) * .35, ay + dy), (bx + dx + (ay - wy0) * .35, ay + dy), (bx + dx + (by - wy0) * .35, by + dy),
                          (ax + dx + (by - wy0) * .35, by + dy)))
    del sh
    # доска: чистая, без мела, деревянная рамка и полочка
    bx0, by0, bx1, by1 = 640.0, 420.0, 1420.0, 800.0
    inner = blob([(bx0 + 60, by0 + 60), (bx0 + 300, by0 + 40), (bx0 + 360, by0 + 120), (bx0 + 90, by0 + 150)], "#456b55", .55)
    inner += blob([(bx1 - 300, by1 - 120), (bx1 - 80, by1 - 140), (bx1 - 60, by1 - 60), (bx1 - 260, by1 - 50)], "#3a5c48", .5)
    o.append(shape(rect_pts(bx0 - 22, by0 - 22, bx1 + 22, by1 + 22), C_WOOD2, "", w=4.0, seed=1130))
    o.append(shape(rect_pts(bx0, by0, bx1, by1), "#3f6450", inner, w=3.6, seed=1131))
    o.append(shape(rect_pts(bx0 - 40, by1 + 22, bx1 + 40, by1 + 44), C_WOOD2, blob(rect_pts(bx0 - 40, by1 + 36, bx1 + 40, by1 + 44), "#8a5b32"), w=3.4, seed=1132))
    return "".join(o)


C_WOOD2 = "#b27c4c"


def school_desk(khy):
    """Парта сбоку: крышка, полка под ней, металлические ножки."""
    x0, x1 = DESK2
    top = khy - 175 * K_SC * .66
    o = [shape(rect_pts(x0, top, x1, top + 22), "#c99a62", blob(rect_pts(x0, top + 14, x1, top + 22), "#a07440"), w=3.6, seed=1140)]
    o.append(shape(rect_pts(x0 + 16, top + 70, x1 - 30, top + 84), "#a07440", "", w=3.0, seed=1141))
    for i, lx in enumerate((x0 + 28, x1 - 34)):
        o.append(shape(rect_pts(lx - 7, top + 22, lx + 7, CFL), "#5b6770", blob(rect_pts(lx + 2, top + 22, lx + 7, CFL), "#3f4850"), w=2.8, seed=1142 + i))
    o.append(blob(ellipse_pts((x0 + x1) / 2, CFL + 4, (x1 - x0) / 2 + 20, 10, 16), "#7a5232", .35))
    return "".join(o), top


def kid_chair(x, y):
    """Стул школьника сбоку, спинка за спиной (справа)."""
    o = [shape(rect_pts(x - 110, y + 18, x + 70, y + 40), "#c99a62", "", w=3.2, seed=1150)]
    o.append(shape(rect_pts(x + 52, y - 230, x + 72, y + 40), "#c99a62", "", w=3.0, seed=1151))
    o.append(shape(rect_pts(x + 40, y - 230, x + 84, y - 150), "#c99a62", "", w=3.0, seed=1152))
    for i, lx in enumerate((x - 96, x + 60)):
        o.append(shape(rect_pts(lx - 6, y + 40, lx + 6, CFL), "#5b6770", "", w=2.6, seed=1153 + i))
    return "".join(o)


def classroom(t):
    """Сцена класса в своих координатах (для фото и для крупного плана)."""
    ts = T_SC * P.HEIGHT["teacher_y"]
    ks = K_SC * P.HEIGHT["kid2"]
    thx, thy = T_HIP[0], CFL - (P.LEG_LEN - 12) * ts
    khx = K_HIP[0]
    khy = CFL - 330 * ks - 30
    desk, dtop = school_desk(khy)
    u_sh = _sm(t, T_UCH - .1, T_UCH + .32)               # ладонь на плечо
    beam = _sm(t, T_UCH - .05, T_UCH + .3)
    # школьник: сидит лицом влево, предплечья на парте; на «учительнице» поднимает глаза и сияет
    kex = dict(P.EXPR["kid2"]["shy"])
    kex = mix_expr(kex, dict(P.EXPR["kid2"]["beam"], look=(.5, -.75)), beam)
    kex["closed"] = _blinkv(t, [1.75])
    kfeet = {"n": ((khx - 128 + 8 * math.sin(t * 4.5), khy + 112), .15), "f": ((khx - 108, khy + 118), .15)}
    karms = {"f": ("ik", (2 * khx - (DESK2[0] + 90), dtop - 10), -1), "n": ("ik", (2 * khx - (DESK2[0] + 60), dtop - 6), -1)}
    khands = {"f": {"curl": (.4, .45, .5, .55), "thumb": .4}, "n": {"curl": (.3, .3, .35, .4), "thumb": .3}}
    kkw = dict(feet=kfeet, flip=True, arms=karms, hands=khands, lean_add=.06 - .05 * beam + .01 * math.sin(t * 3),
               head_add=-.12 * beam + .02 * math.sin(t * 2.4), shrug=.12 * beam)
    k_back = P.kid_dima(khx, khy, K_SC, kex, "sit_desk", layers=("legs", "pelvis", "arm_f", "body"), **kkw)
    k_arm = P.kid_dima(khx, khy, K_SC, kex, "sit_desk", layers=("arm_n",), **kkw)
    k_sh = k_back["head"]
    shoulder = (khx + 14 * ks, khy - 375 * ks)
    del k_sh
    # учительница: склоняется к парте, в дальней руке его лист, ближняя ладонь — к листу, потом на плечо
    tex = dict(P.EXPR["teacher_y"]["kind"], look=(.55, .55))
    tex = mix_expr(tex, dict(P.EXPR["teacher_y"]["praise"], look=(.6, .2)), _sm(t, T_UCH - .05, T_UCH + .35))
    tex["closed"] = _blinkv(t, [2.0, 3.05])
    lean = .52 + .03 * math.sin(t * 2.2) + .04 * u_sh
    sheet_c = (thx + 185 + 4 * math.sin(t * 2.6), khy - 200 * ks + 3 * math.cos(t * 2.1) + 14 * u_sh)
    G = (sheet_c[0] - 62 * .55 + 6, sheet_c[1] + 10)
    W_f = (G[0] - 58 * ts, G[1] + 26 * ts)
    pnt = (sheet_c[0] + 10, sheet_c[1] - 10 + 12 * math.sin(t * 5) * (1 - u_sh))
    W_n = lerp2(pnt, (shoulder[0] - 30, shoulder[1] - 6), u_sh)
    tarms = {"f": ("ik", W_f, -1), "n": ("ik", W_n, -1)}
    hn = {"dir": (.6, .5), "curl": (.15, .55, .65, .7), "spread": .05, "thumb": .4} if u_sh < .5 else \
        {"dir": (.75, .65), "curl": (.2, .25, .3, .35), "spread": .12, "thumb": .25}
    thands = {"f": {"kind": "none"}, "n": hn}
    tfeet = P.stand_kw(thx, thy, T_SC, "teacher_y", spread=70)["feet"]
    tkw = dict(feet=tfeet, arms=tarms, hands=thands, lean_add=lean - .42, head_add=.04 * math.sin(t * 1.7) - .05 * u_sh)
    t_back = P.teacher("young", thx, thy, T_SC, tex, "lean_desk", layers=("legs", "pelvis", "arm_f", "body"), **tkw)
    t_arm = P.teacher("young", thx, thy, T_SC, tex, "lean_desk", layers=("arm_n",), **tkw)
    gb, gf = P.grip_svg("teacher_y", G, 9 * .55, -1, k=ts * .95, h=60, seed=1160)
    sheet = PR.letter(sheet_c[0], sheet_c[1], k=.55, rot=-8, w=200, h=250, write=1.0, seed=7)
    chair = kid_chair(khx, khy)
    return "".join([class_bg(t), t_back["svg"], chair, k_back["svg"], desk, k_arm["svg"], gb, sheet, gf, t_arm["svg"]])


def photo_framed(inner, face=1.0, glare=0.0, seed=0):
    """Рамка 200×160 с фото (без надписей); face 1 — лицом, к 0 — поворот через нижнее ребро; glare — блик на стекле."""
    sd = 16700 + seed
    a = math.pi * (1 - clamp(face))
    sy = math.cos(a)
    if abs(sy) < .04:
        return shape(rect_pts(-100, -7, 100, 7), "#8A5B32", "", w=3.2, seed=sd + 6)
    if sy > 0:
        c = lib.clip_rect(-80, -60, 160, 120)
        ph = blob(rect_pts(-84, -64, 84, 64), "#E9DDC2") + inner + blob(rect_pts(-84, -64, 84, 64), "#c8955a", .14)
        fr = shape(rect_pts(-100, -80, 100, 80), "#B27C4C", blob(rect_pts(-100, 60, 100, 82), "#8A5B32") + blob(rect_pts(-100, -80, 100, -72), "#CE9A68"),
                   w=3.6, seed=sd)
        fr += shape(rect_pts(-80, -60, 80, 60), "#E9DDC2", f'<g clip-path="url(#{c})">{ph}</g>', w=2.8, seed=sd + 1)
        if glare > .01:
            fr += line([(-66, -48), (-34, -54)], 3, "#FFFFFF", taper=.5, wmin=.3, seed=sd + 2, op=glare)
    else:
        fr = shape(rect_pts(-100, -80, 100, 80), "#8A5B32", shape(rect_pts(-84, -64, 84, 64), "#A7835A", "", w=2.4, seed=sd + 4) +
                   shape([(-14, 30), (14, 30), (8, 76), (-8, 76)], "#8A6A44", "", w=2.4, seed=sd + 5), w=3.6, seed=sd + 3)
    return f'<g transform="scale(1 {sy:.4f})">{fr}</g>'


def _whip_in(t, t0, dur=.18):
    e = 1 - ease_out(clamp((t - t0) / dur), 3)
    return -160 * e, -2.0 * e


def s02(t):
    # камера класса: медленный наезд на лица; на «но всё» — быстрый откат к рамке
    face_c = (660.0, 1040.0)
    s_c0 = lerp(1.42, 1.62, _sm(t, 1.22, T_NO))
    pull = ease_io(clamp((t - T_NO) / .42))
    lay = _sm(t, T_OTKL - .02, T_OTKL + .5)
    # мир стола (вечер): Дима держит рамку ближней рукой
    SX, SY = _R.SIT
    BS = 1.0
    fc0 = (SX + 290.0, SY - 330.0)
    fc1 = (SX + 330.0, _R.DESK_TOP - 70.0)
    fc = lerp2(fc0, fc1, lay)
    fc = (fc[0] + 3 * math.sin(t * 2.3) * (1 - lay), fc[1] + 2 * math.cos(t * 1.9) * (1 - lay))
    face = lerp(1.0, .37, lay)
    frot = lerp(-3.0, 4.0, lay)
    # класс → фото → мир: точка класса p ↦ fc + FR_K·Q_PH·(p − CLS_C)
    kq = FR_K * Q_PH
    desk_cam = (lerp(fc0[0] - 20, _R.CAM_DESK_CLOSE[0] - 30, lay), lerp(fc0[1] + 70, _R.CAM_DESK_CLOSE[1] + 40, lay), 1.3)
    cls_cam_world = (fc0[0] + kq * (face_c[0] - CLS_C[0]), fc0[1] + kq * (face_c[1] - CLS_C[1]), s_c0 / kq)
    ls = lerp(math.log(cls_cam_world[2]), math.log(desk_cam[2]), pull)
    cx = lerp(cls_cam_world[0], desk_cam[0], pull)
    cy = lerp(cls_cam_world[1], desk_cam[1], pull)
    s = math.exp(ls)
    s_cls = s * kq
    rot = .4 * math.sin(t * .9) + 1.6 * math.sin(math.pi * pull)
    wdx, wrot = _whip_in(t, T_SPAS)
    cx += wdx / s
    rot += wrot
    _set_ink(s_cls)
    cls = classroom(t)
    inner = f'<g transform="translate({-CLS_C[0] * Q_PH:.4f} {-CLS_C[1] * Q_PH:.4f}) scale({Q_PH:.6f})">{cls}</g>'
    inner = f'<g transform="scale({1 / 1:.4f})">{inner}</g>'
    _set_ink(s)
    if t < T_NO - .01:     # до отката — только класс (быстрее), камера та же
        body = f'<g transform="{lib.cam(cx, cy, s, rot)}"><g transform="translate({fc0[0]:.3f} {fc0[1]:.3f}) scale({FR_K})">{inner}</g></g>'
        over = vignette(1.0)
        return svg(f'<rect width="1080" height="1920" fill="#e2d6b4"/>{body}{over}')
    sc = _R.desk_scene(t, "evening", drawer=0.0)
    gl = clamp((pull - .6) / .4)
    frame_svg_ = photo_framed(inner, face, glare=gl * .8)
    frame_g = f'<g transform="translate({fc[0]:.3f} {fc[1]:.3f}) rotate({frot:.3f}) scale({FR_K})">{frame_svg_}</g>'
    # ближняя рука держит правый край рамки
    sy_f = math.cos(math.pi * (1 - face))
    G = (fc[0] + 100 * FR_K * math.cos(math.radians(frot)) - 8, fc[1] + 100 * FR_K * math.sin(math.radians(frot)) + 6 * sy_f)
    W_n = (G[0] + 64 * BS, G[1] + 26 * BS)
    W_f = (SX + 240, _R.DESK_TOP - 70 + 4 * math.sin(t * 2))
    e = dict(P.EXPR["dima"]["thoughtful"], brows="sad", mouth="smile", smile=.25 * (1 - lay), look=(.6, .35 + .3 * lay), lid=.6 - .1 * lay)
    e["closed"] = _blinkv(t, [3.95])
    kw = dict(feet={"n": ((SX + 300, _R.FL - 52), 0.0), "f": ((SX + 250, _R.FL - 50), 0.0)}, arms={"f": ("ik", W_f, -1), "n": ("ik", W_n, -1)},
              hands={"n": {"kind": "none"}, "f": {"curl": (.35, .35, .4, .45), "thumb": .35, "dir": (1, .3)}},
              lean_add=.06 * lay + .02 * math.sin(t * 2), head_add=.08 * lay)
    parts = {k: P.dima(SX, SY, BS, e, "card", layers=(k,), **kw)["svg"] for k in ("legs", "pelvis", "arm_f", "body", "arm_n")}
    gb, gf = P.grip_svg("dima", G, 7 * FR_K, +1, k=BS * .95, h=70, seed=1170)
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], sc["pool"], parts["legs"], sc["desk_legs"], sc["chair_seat"], parts["pelvis"], parts["arm_f"],
             parts["body"], parts["arm_n"], gb, frame_g, gf, sc["lamp"]]
    sx = sy = 0.0
    if t > T_OTKL + .45:      # рамка легла — лёгкий толчок
        h = t - (T_OTKL + .45)
        sx, sy = 6 * math.exp(-9 * h) * math.sin(h * 110), 5 * math.exp(-9 * h) * math.sin(h * 90 + 1)
    body = f'<g transform="{lib.cam(cx + sx, cy + sy, s, rot)}">{"".join(world)}</g>'
    return svg(f'<rect width="1080" height="1920" fill="#2a2440"/>{body}{vignette(1 - pull)}')


def frame(sid, t):
    lib.dyn_begin()
    lib.DEFS.clear()
    return {"s02": s02, "s14": s14, "s15": s15}[sid](t)
