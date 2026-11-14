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
    nerv = {"brows": "worry", "mouth": "talk", "open": .1, "smile": 0.0, "lid": .92, "look": (.55, .15), "bags": False}
    stead = {"brows": "calm", "mouth": "talk", "open": .1, "smile": .45, "lid": .78, "look": (.5, .05), "bags": False}
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
    # письмо в дальней руке: дрожит, пока голос дрожит
    let_d = (1 - u) * 3.5 * math.sin(t * 2 * math.pi * 7.3)
    arms = {"f": ("ik", (hip[0] - 205 * sc, hip[1] - (250 + 30 * u) * sc), -1)}
    base = P.dima(hip[0], hip[1], sc, ex, "mobile_letter", layers=("legs", "pelvis", "arm_f", "body"), arms=arms, **kw)
    wf = base["wrist"]["f"]
    lx, ly = wf[0] - 38 * sc, wf[1] - 120 * sc + let_d
    letter = PR.letter(lx, ly, k=sc * 1.05, rot=-6 + let_d * .4, w=200, h=260, write=1.0, seed=3)
    handf = P.dima(hip[0], hip[1], sc, ex, "mobile_letter", layers=("hand_f",), arms=arms, **kw)
    mob = P.mobile_at_ear(base, sc, flip=True)
    armn = P.dima(hip[0], hip[1], sc, ex, "mobile_letter", layers=("arm_n",), arms=arms, **kw)
    body = rw["bg"] + base["svg"] + letter + handf["svg"] + mob + armn["svg"]
    a = ease_io(clamp((t - 33.72) / 2.4))
    cx, cy, s = lerp(-170, -110, a), lerp(930, 780, a), lerp(.95, 1.1, a)
    cx += 6 * math.sin(t * .9)
    return frame_svg(body, cx, cy, s, rot=.4 * math.sin(t * .7))


def frame(sid, t):
    lib.dyn_begin()
    lib.DEFS.clear()
    return {"s14": s14}[sid](t)
