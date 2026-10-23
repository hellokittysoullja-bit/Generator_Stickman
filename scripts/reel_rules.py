"""Правила рилса — кодом, а не памятью агента (22.10, по вопросу владельца: «новый агент с нуля не должен сделать хуже»).

Каждое правило проверено на рилсе эп.02 и названо по своему источнику (подробно — docs/REELS_PLAYBOOK.md).
`reel.py` зовёт `check` перед рендером и не рендерит рилс с ошибкой (`--force` — только осознанно, с причиной).

    python scripts/reel_rules.py videos/NN/reel     # проверить reel.json без рендера
"""
import math
import os
import re

MAX_SHOT_SEC = 3.0         # план не дольше 3 с (разбор роликов о Reels: смена картинки каждые 2–3 с)
FIRST_CUT_SEC = 2.0        # первая склейка в первые 2 с — «решают первые 1–2 секунды» (владелец 22.10)
HOOK_MAX_CHARS = 30        # первая фраза читается за ~1.3–1.8 с при 17 знаках в секунду
RISER_START_MAX = 0.05     # riser звучит с нулевой секунды (владелец 22.10), а не после хука
RISER_PEAK_ON_CUT = 0.10   # пик riser — на склейке (Clumzzy: riser — ожидание перед раскрытием)
MIN_PICTURE_H = 1360       # владелец 22.10: «столько воздуха в рилсах не оставляют» — при 1100 низ был пуст
MAX_FROZEN_SHARE = 0.05    # доля почти неподвижных кадров готового файла (reel_metrics.py), v9 — 0.025
READ_CPS, READ_PAD = 17.0, 0.3   # дочитать группу: знаки / 17 + 0.3 с (StudioBinder 17 зн/с; разбор 189 роликов 23.10)
ACCENT_KINDS = ("punch", "shake", "spot", "circle")   # акцент — только на ключевом слове, не на предлоге
CLITICS = {"в", "во", "на", "с", "со", "к", "ко", "по", "о", "об", "от", "до", "из", "у", "за", "для", "при", "без",
           "и", "а", "но", "не", "ни", "же", "ли", "бы", "что", "как", "это", "то", "он", "она", "ты", "я", "мы"}


# Против шаблона (владелец 23.10: «чтобы агент не делал шаблонно»): у каждого рилса паспорт — тип хука, схема,
# приёмы; журнал прошлых рилсов — docs/reels_log.json. Типы хуков — из базы знаний (01_hook_script_retention.md).
STEP_MIN, STEP_SHIFT = 1.4, 0.33   # правило 30° (Бордуэлл): соседние окна одного рисунка — ×1.4 или сдвиг на треть окна
MIN_SHOT_SEC = 0.7         # план короче 0.7 с не читается (плейбук; v12 минимум 0.706)
MAX_SRC_CHANGES_30S = 10   # смен рисунка за любые 30 с (Lang 1999: перегрузка содержания), v12 — 9
CAP_HOLD_PAD = 0.6         # субтитр стоит не дольше чтения + 0.6 с (Szarkowska 2018, Stern 2024), v12 — максимум +0.47
CTA_BEFORE_END = 5.0       # призыв начинается не позже чем за 5 с до конца (финал — зона ухода: Dashlet, NSDI 2023)
LATE_ZONE, LATE_SHOT_SEC = 0.8, 2.0   # гипотеза: в последних 20 % планы ≤ 2 с (предупреждение, не запрет)
ONE_MOTION_SEC = 0.2       # гипотеза: старты движений (наезд, хлёст, пометка, жест куклы) не ближе 0.2 с
PUNCH_MIN_GAP = 3.0        # гипотеза: наезды ближе 3 с обесценивают друг друга (Дмитрык: лишние крупные ослабляют следующие)
LONG_WORD_SYLLABLES = 4    # в первых трёх фразах слова не длиннее 4 слогов (тест незнакомца; предупреждение)
# Безопасные зоны экрана 1080×1920 (Meta/Restream): верх 14 % — шапка Reels, низ 400 px — подпись и кнопки, бока 70 px,
# правая колонка кнопок x > 930 ниже 45 % высоты. Рукописные надписи и маркер — целиком внутри.
SAFE_TOP, SAFE_BOTTOM, SAFE_SIDE, SAFE_RIGHT_COL, RIGHT_COL_FROM = 269, 1520, 70, 930, 864
# Стоп-слова (план 04 п.1.3): преувеличение гасит любопытство, Instagram режет «сенсационный» контент о здоровье,
# медицинские обещания и ложный дефицит — бан рекомендаций и удар по доверию; шаблон «если ты X — у тебя СДВГ».
STOP_WORDS = (r"\bшок", r"врачи скрывают", r"\b100\s?%", r"гарантированн", r"\bбомб", r"\bвылеч", r"\bизлеч",
              r"навсегда", r"убить время", r"чуть не умер", r"только для ленивых", r"осталось \d+ мест", r"только сегодня",
              r"если ты .{1,40}[—–-] у тебя сдвг")
HOOK_TYPES = ("диссонанс", "вопрос", "число", "POV", "середина истории", "что если", "термин", "ошибка/запрет",
              "желаемый результат", "сравнение", "секрет/закулисье", "абсурд", "прямое обращение к узнаванию")
MAX_DEVICE_OVERLAP = 0.5   # приёмы нового рилса совпадают с прошлым не больше чем наполовину


def check_passport(spec, log, reel_dir=""):
    """Паспорт рилса против журнала: тип хука и первые слова не как у предыдущего рилса, приёмы не те же."""
    err = []
    pp = spec.get("passport")
    if not pp:
        return ["нет паспорта рилса (passport: hook_type, structure, devices) — без него не проверить шаблонность"]
    goal = pp.get("goal") or {}
    if not (goal.get("question") and goal.get("emotion")):
        err.append('в паспорте нет цели: "goal": {"question": один вопрос зрителя, "emotion": целевая эмоция} (Kallaway)')
    if pp.get("hook_type") not in HOOK_TYPES:
        err.append(f"тип хука «{pp.get('hook_type')}» — не из списка {HOOK_TYPES}")
    if len(pp.get("devices", [])) < 5:
        err.append("в паспорте меньше 5 приёмов — опишите, чем этот рилс держит")
    parent = os.path.normpath(pp.get("variant_of", "")) if pp.get("variant_of") else None   # вариант для пробных Reels
    prev = [r for r in log if os.path.normpath(r.get("reel", "")) not in (os.path.normpath(reel_dir), parent)]
    if prev:
        last = prev[-1]
        if pp.get("hook_type") == last.get("hook_type"):
            err.append(f"тип хука «{pp['hook_type']}» как у прошлого рилса ({last['reel']}): смените тип хука")
        first = " ".join(clean(spec["beats"][0]["text"]).split()[:2]).lower()
        if any(first == r.get("first_words", "").lower() for r in prev):
            err.append(f"рилс начинается теми же словами «{first}», что прошлый: хук станет узнаваемым шаблоном")
        a, b = set(pp.get("devices", [])), set(last.get("devices", []))
        if a and len(a & b) / len(a) > MAX_DEVICE_OVERLAP:
            err.append(f"приёмы совпадают с прошлым рилсом на {len(a & b) / len(a):.0%} (> {MAX_DEVICE_OVERLAP:.0%}): "
                       f"общие — {sorted(a & b)}")
    return err


def clean(text):
    return re.sub(r"\s+", " ", text.replace("*", "").replace("|", "")).strip()


def check_spec(spec, sfx_names):
    """Правила самого reel.json: звуки владельца, хук, раскладка, петля. Список ошибок (пустой — годно)."""
    err = []
    beats = spec.get("beats", [])
    if len(beats) < 2:
        return ["меньше двух фраз — хук и раскрытие не из чего собрать"]
    if "music" in spec or any(e.get("name") == "music" for b in beats for e in b.get("fx", [])):
        err.append("музыка: в рилсах её нет (решение владельца 22.10)")
    for i, b in enumerate(beats):
        for e in b.get("fx", []):
            if e.get("kind") == "sfx" and e.get("name") not in sfx_names:
                err.append(f"фраза {i}: звук «{e.get('name')}» — не из звуков владельца {sorted(sfx_names)}")
        for s in b.get("shots", []):
            if s.get("sound") and s["sound"] not in sfx_names:
                err.append(f"фраза {i}: звук плана «{s['sound']}» — не из звуков владельца")
    hook = clean(beats[0]["text"])
    if len(hook) > HOOK_MAX_CHARS:
        err.append(f"хук «{hook}» — {len(hook)} знаков, нужно ≤ {HOOK_MAX_CHARS}: первая фраза бьёт в лоб, коротко")
    riser = [e for e in beats[0].get("fx", []) if e.get("kind") == "sfx" and e.get("name") == "riser"]
    if not riser:
        err.append("в первой фразе нет riser: он звучит с нулевой секунды в каждом рилсе (владелец 22.10)")
    else:
        e = riser[0]
        start = spec.get("lead_in", 0.0) + e.get("dt", 0.0) if e.get("at", 0) == 0 and not e.get("after") else None
        if e.get("align") != "start" or start is None or start > RISER_START_MAX:
            err.append('riser должен начинаться с 0 с: {"at": 0, "align": "start", "dt": -lead_in}')
    if beats[1].get("after_sfx") != "riser":
        err.append('вторая фраза должна вставать на пик riser: "after_sfx": "riser"')
    if spec.get("picture_h", 1380) < MIN_PICTURE_H:
        err.append(f"picture_h {spec.get('picture_h')} < {MIN_PICTURE_H}: низ экрана будет пустой бумагой")
    for i, b in enumerate(beats):                     # эп.02 v11: наезд стоял на «при», а не на «СДВГ» (замер 23.10)
        words = [w for w in clean(b["text"]).split() if w not in ("—", "–", "-")]
        for e in b.get("fx", []):
            k = e.get("at", 0)
            if e.get("kind") in ACCENT_KINDS and k < len(words):
                w = re.sub(r"[^\w-]", "", words[k].lower())
                if w in CLITICS:
                    err.append(f"фраза {i}: {e['kind']} на служебном слове «{words[k]}» — акцент ставится на ключевое")
        marked = [w.startswith("*") or w.startswith("«*") or "*" in w for w in b["text"].replace("|", "").split()
                  if w not in ("—", "–", "-")]
        for e in b.get("fx", []):
            k = e.get("at", 0)
            if e.get("kind") in ACCENT_KINDS and k < len(words) and k < len(marked) and not marked[k]:
                if (k > 0 and marked[k - 1]) or (k + 1 < len(marked) and marked[k + 1]):
                    err.append(f"фраза {i}: {e['kind']} на «{words[k]}», а ключевое (*) — соседнее слово: сдвиг на одно")
        low = clean(b["text"]).lower()
        for pat in STOP_WORDS:
            if re.search(pat, low):
                err.append(f"фраза {i}: стоп-слово «{re.search(pat, low).group(0)}» — сенсация, медицинское обещание или "
                           "ложный дефицит: режет охват и доверие")
    whips = [s["whip"][0] for b in beats for s in b.get("shots", []) if s.get("whip") and not s.get("whip_back")]
    if whips and min(whips) < 0 < max(whips):
        err.append("хлёсты «вперёд по сюжету» в разные стороны: одна сторона на ролик (правило 180°), "
                   "обратный — с \"whip_back\": true")
    first = next((s for s in beats[0]["shots"] if "src" in s), None)
    last = next((s for s in beats[-1]["shots"] if "src" in s), None)
    if first and last and first["src"] != last["src"]:
        err.append(f"петля: финал на {last['src']}, а начало на {first['src']} — конец = начало")
    return err


def check_timeline(shots, events, sfx_peaks, caps=None, total=None):
    """Правила по рассчитанному таймингу: длина планов, первая склейка, пик riser на склейке; с субтитрами (caps —
    [{t0, t1, text}]) ещё: хук дочитывается до первой склейки, группа субтитров не идёт через склейку, последняя
    группа успевает прочитаться."""
    err = []
    cuts = [s["t0"] for s in shots[1:]]
    if caps:
        need = len(caps[0]["text"]) / READ_CPS + READ_PAD
        if cuts and need > cuts[0] + 0.02:
            err.append(f"хук «{caps[0]['text']}» читается {need:.2f} с, а склейка на {cuts[0]:.2f} с: короче хук")
        for c in caps:
            for k in cuts:
                if c["t0"] + 0.05 < k < c["t1"] - 0.05:
                    err.append(f"субтитр «{c['text']}» ({c['t0']:.2f}–{c['t1']:.2f} с) идёт через склейку {k:.2f} с:"
                               " план на начало группы или «|» перед словом склейки")
        if total is not None:
            last = caps[-1]; need = len(last["text"]) / READ_CPS + READ_PAD
            if total - last["t0"] < need - 0.02:
                err.append(f"последний субтитр «{last['text']}» стоит {total - last['t0']:.2f} с, нужно {need:.2f}: больше tail")
        for c in caps[1:]:
            need = len(c["text"]) / READ_CPS + READ_PAD
            if c["t1"] - c["t0"] > need + CAP_HOLD_PAD + 0.02 and not c.get("gap"):
                err.append(f"субтитр «{c['text']}» стоит {c['t1'] - c['t0']:.2f} с при чтении {need:.2f}: "
                           "дольше чтения + 0.6 с глаз уходит с рисунка — следующая группа раньше")
    changes = [b["t0"] for a, b in zip(shots, shots[1:]) if (b.get("src") or b.get("kind")) != (a.get("src") or a.get("kind"))]
    for c0 in [0.0] + changes:
        n = sum(c0 <= c < c0 + 30.0 for c in changes)
        if n > MAX_SRC_CHANGES_30S:
            err.append(f"{n} смен рисунка за 30 с с {c0:.1f} с > {MAX_SRC_CHANGES_30S}: перегрузка, держите рисунок дольше"); break
    for a, b in zip(shots, shots[1:]):                # правило 30°: соседние окна одного рисунка — на ступень
        if a.get("src") and a.get("src") == b.get("src") and "from" in a and "from" in b and not b.get("jump"):
            pa, pb = a.get("to", a["from"]), b["from"]
            ratio = pb[2] / pa[2]; shift = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
            if 1 / STEP_MIN < ratio < STEP_MIN and shift < STEP_SHIFT * max(pa[2], pb[2]):
                err.append(f"склейка {b['t0']:.2f} с: окна одного рисунка {a['src']} почти одинаковы (×{ratio:.2f}, сдвиг "
                           f"{shift:.0f}) — скачок; крупнее/мельче хотя бы в {STEP_MIN} раза или \"jump\": true")
    for s in shots[:-1]:
        if s["t1"] - s["t0"] < MIN_SHOT_SEC - 0.02:
            err.append(f"план {s['t0']:.2f}–{s['t1']:.2f} с — {s['t1'] - s['t0']:.2f} с < {MIN_SHOT_SEC}: не успеть прочитать")
    for s in shots:
        d = s["t1"] - s["t0"]
        if d > MAX_SHOT_SEC + 0.02:
            err.append(f"план {s['t0']:.2f}–{s['t1']:.2f} с идёт {d:.2f} с > {MAX_SHOT_SEC}: разрежьте его вторым планом")
    if len(shots) > 1 and shots[1]["t0"] > FIRST_CUT_SEC:
        err.append(f"первая склейка на {shots[1]['t0']:.2f} с > {FIRST_CUT_SEC}: хук без смены картинки")
    for e in events:
        if e.get("kind") == "sfx" and e.get("name") == "riser":
            peak = e["t"] + (sfx_peaks["riser"] if e.get("align") == "start" else 0.0)
            gap = min(abs(peak - s["t0"]) for s in shots[1:]) if len(shots) > 1 else 9.0
            if gap > RISER_PEAK_ON_CUT:
                err.append(f"пик riser на {peak:.2f} с не на склейке (ближайшая в {gap:.2f} с)")
    return err


SOUND_MAX = {"swoosh_deep": 3, "oof": 2, "riser": 2}   # «появление важного» и «провал» обесцениваются повтором
SOUND_REPEAT_SEC = 4.0     # один и тот же звук не ближе 4 с (кроме swoosh на хлёсте и тихих свистов наезда)
SOUND_DENSE_WIN, SOUND_DENSE_MAX = 0.5, 2   # не больше двух звуков в 0.5 с (Мёрч, «2,5 слоя»): предупреждение


def check_sounds(plan):
    """Звуки по reel.sound_plan: лимиты повторов (library.json, поле avoid) и одинаковые звуки подряд."""
    err = []
    for name, mx in SOUND_MAX.items():
        n = sum(p["name"] == name for p in plan)
        if n > mx:
            err.append(f"звук «{name}» {n} раз > {mx}: повтор обесценивает смысл звука (library.json, avoid)")
    loud = [p for p in plan if not p.get("soft")]
    by = {}
    for p in loud:
        by.setdefault(p["name"], []).append(p)
    for name, ps in by.items():
        ps = sorted(ps, key=lambda p: p["peak"])
        for a, b in zip(ps, ps[1:]):
            if b["peak"] - a["peak"] < SOUND_REPEAT_SEC and not (name == "swoosh" and (a.get("whip") or b.get("whip"))):
                err.append(f"«{name}» на {a['peak']:.2f} и {b['peak']:.2f} с — ближе {SOUND_REPEAT_SEC} с: повтор слышен")
    return err


def sound_warnings(plan):
    pk = sorted(p["peak"] for p in plan)
    for i, t in enumerate(pk):
        n = sum(t <= q < t + SOUND_DENSE_WIN for q in pk[i:])
        if n > SOUND_DENSE_MAX:
            return [f"{n} звука за {SOUND_DENSE_WIN} с с {t:.2f} с — звук спорит с текстом, разведите"]
    return []


# Знания базы, которые обязан применить каждый рилс (владелец 23.10: «не вижу, чтобы во всех новых рилсах автоматически
# использовались все эти знания»): docs/reels_knowledge/apply_checklist.json. Как сделать пункт — решает рилс; рендер не
# начнётся, пока у каждого пункта в passport.knowledge нет номера фразы или отказа с причиной.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKLIST_PATH = os.path.join(ROOT_DIR, "docs", "reels_knowledge", "apply_checklist.json")
BRAND_PATH = os.path.join(ROOT_DIR, "docs", "reels_brand.json")
SKIP_MIN_CHARS = 15
SHAME_WORDS = (r"\bсоберись", r"\bперестань", r"возьми себя в руки", r"\bхватит ныть", r"\bлентя[йи]",
               r"вот почему ты вс[её] срываешь")
# Волна 8 (23.10, docs/reels_knowledge/08_deep_persuasion_funnel.md): давление включает реактивность (мета-анализы
# 2025–2026, r ≈ .20) — призыв без «обязательно», «срочно», «успей», «должен»; закреп «напиши 1 / 2» — дословно пример
# приманки вовлечения из правил Instagram 2024; смысловые петли не реже раза в 12 с (Kallaway 20–30 с — мнение, берём строже
# с запасом); у рилса-серии — название и номер серии (персонаж-сериал: System1/IPA, Duolingo).
CONTROL_WORDS = (r"\bобязательно\b", r"\bсрочно\b", r"\bуспей", r"\bнемедленно\b", r"\bты должн", r"\bвы должн",
                 r"\bнужно перейти", r"\bпереходи прямо", r"\bне упусти")
BAIT_PATTERNS = (r"напиши\s*[«\"']?\d", r"пиши\s*[«\"']?\d", r"\b1\b[^.]{0,40}\b2\b.{0,20}(напиши|пиши|ставь)",
                 r"(напиши|пиши|ставь)[^.]{0,30}\b1\b[^.]{0,40}\b2\b", r"ставь\s*[+❤🔥]")
LOOP_GAP_MAX = 12.5        # с: между смысловыми петлями (passport.knowledge.meaning_loops) и от начала до первой
COVER_MAX_WORDS, COVER_MAX_CHARS = 4, 24
CAPTION_HEAD = 125         # Instagram показывает ~125 знаков подписи до «ещё»: ключевая фраза ниши — в них
LENGTH_WORK_SEC = 40.0     # рабочая вилка 20–40 с (07 §8 п.35, мнение) — предупреждение


def load_json(p, default):
    import json
    return json.load(open(p, encoding="utf8")) if os.path.exists(p) else default


def brand_beat(spec, brand):
    name = (brand or {}).get("brand", "")
    return next((i for i, b in enumerate(spec.get("beats", [])) if name and name.lower() in clean(b["text"]).lower()), None)


def _beats_of(v):
    if isinstance(v, bool):
        return []
    if isinstance(v, int):
        return [v]
    if isinstance(v, list):
        return [x for x in v if isinstance(x, int) and not isinstance(x, bool)]
    if isinstance(v, dict):
        return [x for k, x in v.items() if k != "skip" and isinstance(x, int) and not isinstance(x, bool)]
    return []


def check_knowledge(spec, checklist=None, brand=None):
    """Каждый пункт чек-листа знаний закрыт в паспорте фразой или отказом с причиной; пункты kind=code — проверка кодом."""
    checklist = checklist if checklist is not None else load_json(CHECKLIST_PATH, {"items": []})
    brand = brand if brand is not None else load_json(BRAND_PATH, {})
    pp = spec.get("passport") or {}; kn = pp.get("knowledge") or {}
    beats = spec.get("beats", []); n = len(beats); cta = pp.get("cta_beat"); br = brand_beat(spec, brand)
    err = []
    for it in checklist.get("items", []):
        if it["kind"] != "beat":
            continue
        v = kn.get(it["id"])
        where = f"знание «{it['id']}» ({it['title']}; {it['source']})"
        if v is None or v == "TODO":
            err.append(f"{where}: в passport.knowledge нет ни номера фразы, ни отказа с причиной"); continue
        if isinstance(v, dict) and "skip" in v:
            if len(str(v["skip"]).strip()) < SKIP_MIN_CHARS:
                err.append(f"{where}: отказ без причины — напишите, почему здесь не к месту")
            continue
        bs = _beats_of(v)
        if not bs or any(not 0 <= b < n for b in bs):
            err.append(f"{where}: {v!r} — не номер фразы 0…{n - 1}"); continue
        for f in it.get("fields", []):
            if not isinstance(v, dict) or f not in v:
                err.append(f"{where}: нужны поля {it['fields']}")
        rule = it.get("check", "")
        lo, hi = min(bs), max(bs)
        bad = ((rule == "beat == 0" and lo != 0) or
               (rule == "beat < cta" and cta is not None and lo >= cta) or
               (rule == "beat <= cta" and cta is not None and lo > cta) or
               (rule == "beat >= cta" and cta is not None and hi < cta) or
               (rule == "beat < brand" and br is not None and lo >= br) or
               (rule.startswith("authority") and isinstance(v, dict) and "loss" in v and "authority" in v
                and not 1 <= v["authority"] - v["loss"] <= 2))
        if bad:
            err.append(f"{where}: фраза {v!r} нарушает «{rule}» (призыв — {cta}, продукт — {br})")
    low = " ".join(clean(b["text"]).lower() for b in beats)
    for pat in CONTROL_WORDS:
        m = re.search(pat, low)
        if m:
            err.append(f"давящее слово «{m.group(0)}» — включает реактивность: зритель делает наоборот (08 §1, мета-анализы "
                       "реактивности); призыв — как выбор («захочешь — …»)")
    pin = pp.get("pinned_comment") or brand.get("pinned_comment_default") or ""
    for pat in BAIT_PATTERNS:
        if re.search(pat, pin.lower()):
            err.append(f"закреплённый комментарий «{pin[:60]}…» — приманка вовлечения («напиши цифру»): пример из правил "
                       "Instagram о снижении показов (08 §2); нужен открытый вопрос о зрителе")
            break
    ser = pp.get("series")
    if ser is not None and not (isinstance(ser, dict) and ser.get("name") and ser.get("episode")):
        err.append('серия рилса: "series": {"name": …, "episode": N} — название и номер (08 §2, персонаж-сериал)')
    for pat in SHAME_WORDS:
        m = re.search(pat, low)
        if m:
            err.append(f"стыдящее повеление «{m.group(0)}» — зритель с СДВГ слышит упрёк (07 §8 п.33, правила Meta)")
    labels = pp.get("labels")
    if labels is None:
        err.append('в паспорте нет "labels" — терминов-ярлыков рилса (не больше двух, 07 §8 п.18)')
    elif len(labels) > 2:
        err.append(f"ярлыков {len(labels)} > 2: третий термин «нарочно усложняет» (07 §8 п.18)")
    cover = (pp.get("cover") or {}).get("text", "")
    if not cover:
        err.append('в паспорте нет "cover": {"text": …} — обложка = первый рисунок + ясный текст (07 §8 п.11)')
    elif len(cover.split()) > COVER_MAX_WORDS or len(cover) > COVER_MAX_CHARS:
        err.append(f"текст обложки «{cover}» длиннее {COVER_MAX_WORDS} слов / {COVER_MAX_CHARS} знаков: в сетке не читается")
    cap = pp.get("caption", "")
    if not cap:
        err.append('в паспорте нет "caption" — подписи с ключевой фразой ниши и 3–5 хэштегами (07 §8 п.24)')
    else:
        tags = re.findall(r"#\w+", cap)
        if not any(k.lower() in cap[:CAPTION_HEAD].lower() for k in brand.get("niche_keywords", [])):
            err.append(f"в первых {CAPTION_HEAD} знаках подписи нет ключевой фразы ниши {brand.get('niche_keywords')}")
        if not 3 <= len(tags) <= brand.get("max_hashtags", 5):
            err.append(f"хэштегов {len(tags)}: нужно 3–{brand.get('max_hashtags', 5)}")
    if not (pp.get("pinned_comment") or brand.get("pinned_comment_default")):
        err.append("нет закреплённого комментария (passport.pinned_comment или brand.pinned_comment_default)")
    hv = pp.get("hook_variants") or []
    hook = clean(beats[0]["text"]) if beats else ""
    if not 3 <= len(hv) <= 5:
        err.append(f"вариантов хука {len(hv)}: нужно 3–5 для пробных Reels (07 §8 п.3)")
    lib = load_json(os.path.join(ROOT_DIR, "assets", "sfx", "reels", "library.json"), {})
    peak = (lib.get("riser") or {}).get("peak_sec", 1.65)
    for v in hv:                                    # вариант дочитывается до пика riser — до первой склейки (тот же расчёт,
        need = len(clean(v)) / READ_CPS + READ_PAD  # что check_timeline для хука); длиннее — склейка уедет за 2 с
        if len(clean(v)) > HOOK_MAX_CHARS or need > peak + 0.02:
            mx = int((peak - READ_PAD) * READ_CPS)
            err.append(f"вариант хука «{v}» читается {need:.2f} с > пика riser {peak} с: короче (≤ {mx} знаков)")
    if len({clean(v).lower() for v in hv} | {hook.lower()}) != len(hv) + 1:
        err.append("варианты хука повторяют друг друга или сам хук")
    return err


def knowledge_timing(spec, beat_t0, total):
    """Ре-хук стоит на 35–60 % ролика; смысловые петли (meaning_loops) — не реже раза в LOOP_GAP_MAX с от начала до
    призыва (по рассчитанному времени фраз)."""
    kn = (spec.get("passport") or {}).get("knowledge") or {}
    err = []
    bs = _beats_of(kn.get("re_hook"))
    if bs and bs[0] < len(beat_t0):
        share = beat_t0[bs[0]] / total
        if not 0.35 <= share <= 0.60:
            err.append(f"ре-хук (фраза {bs[0]}) на {share:.0%} ролика — нужно 35–60 % (01: Kallaway, heyDominik)")
    loops = sorted(set(b for b in _beats_of(kn.get("meaning_loops")) if b < len(beat_t0)))
    if loops:
        cta = (spec.get("passport") or {}).get("cta_beat")
        end = beat_t0[cta] if cta is not None and cta < len(beat_t0) else total
        ts = [0.0] + [beat_t0[b] for b in loops] + [end]
        for a, b in zip(ts, ts[1:]):
            if b - a > LOOP_GAP_MAX + 0.02:
                err.append(f"смысловых петель нет {b - a:.1f} с ({a:.1f}–{b:.1f} с) > {LOOP_GAP_MAX}: новый вопрос, поворот "
                           "или обещание — чаще (08 §3)")
    return err


def check_overlays(boxes):
    """Рукописные надписи и маркер (boxes — [(фраза, текст, x0, y0, x1, y1)] по туши, в пикселях экрана 1080×1920)
    целиком в безопасной зоне: не под шапкой Reels, не под подписью, не у края и не под колонкой кнопок."""
    err = []
    for i, txt, x0, y0, x1, y1 in boxes:
        where = []
        if y0 < SAFE_TOP: where.append(f"верх {y0:.0f} < {SAFE_TOP} (шапка Reels)")
        if y1 > SAFE_BOTTOM: where.append(f"низ {y1:.0f} > {SAFE_BOTTOM} (подпись и кнопки)")
        if x0 < SAFE_SIDE or x1 > 1080 - SAFE_SIDE: where.append(f"x {x0:.0f}–{x1:.0f} у края экрана")
        if y1 > RIGHT_COL_FROM and x1 > SAFE_RIGHT_COL: where.append(f"правый край {x1:.0f} под колонкой кнопок")
        if where:
            err.append(f"фраза {i}: надпись «{txt}» — " + "; ".join(where))
    return err


def check_cta(spec, beat_t0, total):
    """Призыв (passport.cta_beat) начинается не позже чем за 5 с до конца: позже — до него не досматривают."""
    k = (spec.get("passport") or {}).get("cta_beat")
    if k is None or k >= len(beat_t0):
        return ['в паспорте нет "cta_beat" — номера фразы призыва: без него не проверить, что призыв успевают увидеть']
    if beat_t0[k] > total - CTA_BEFORE_END + 0.02:
        return [f"призыв (фраза {k}) начинается на {beat_t0[k]:.1f} с, за {total - beat_t0[k]:.1f} с до конца < {CTA_BEFORE_END}"]
    return []


def syllables(w):
    return len(re.findall(r"[аеёиоуыэюяaeiouy]", w.lower()))


HAND_WORDS_MAX, HAND_WIN = 3, 7.0   # рукописных слов не больше 3 за 7 с (п.1.15), два текста не в одни 0.5 с
ARCS, CHARGES = ("t", "r"), ("+", "-", "−")


def check_writing(events, shots):
    """Рукописный текст до первой склейки — ошибка: хук работает одной картинкой и одним субтитром (п.1.15)."""
    cut = shots[1]["t0"] if len(shots) > 1 else 9e9
    return [f"рукописное «{e['text']}» на {e['t']:.2f} с — до первой склейки {cut:.2f} с: в хуке один текст — субтитр"
            for e in events if e.get("kind") in ("write", "mark") and e["t"] < cut - 0.01]


def warnings(spec, shots, total, events=()):
    """Гипотезы без доказанного порога — печатаются, рендер не останавливают."""
    out = []
    hand = sorted((e["t"], e["text"]) for e in events if e.get("kind") in ("write", "mark"))
    for i, (t, _) in enumerate(hand):
        n = sum(len(clean(x).split()) for tt, x in hand[i:] if tt < t + HAND_WIN)
        if n > HAND_WORDS_MAX:
            out.append(f"рукописных слов {n} за {HAND_WIN:.0f} с с {t:.2f} с > {HAND_WORDS_MAX}: читать некогда (п.1.15)"); break
    for (t1, x1), (t2, x2) in zip(hand, hand[1:]):
        if t2 - t1 < 0.5:
            out.append(f"«{x1}» и «{x2}» начаты через {t2 - t1:.2f} с: два текста сразу (п.1.15)")
    beats = spec.get("beats", [])
    arcs = [b.get("arc") for b in beats]; ch = [b.get("charge") for b in beats]
    if any(arcs):                                       # кривая «напряжение — разрядка» (п.1.23), если размечена
        for i, (a, b) in enumerate(zip(arcs, arcs[1:])):
            if a == b == "r":
                out.append(f"фразы {i} и {i + 1} — две разрядки подряд: напряжение падает (п.1.23)")
        run = 1
        for i in range(1, len(ch)):
            run = run + 1 if ch[i] and ch[i] == ch[i - 1] else 1
            if run > 2:
                out.append(f"фразы {i - 2}–{i} — три подряд со знаком «{ch[i]}»: качели ценности замерли (п.1.23)")
        if ch and ch[-1] not in ("+", None):
            out.append("рилс кончается на «−»: конец на «+» (п.1.23)")
    starts = [(e["t"], e["kind"]) for e in events if e.get("kind") in ("punch", "write", "mark", "circle", "arrow")]
    starts += [(s["t0"], "вход наездом" if s.get("zoom_in") else "хлёст") for s in shots[1:] if s.get("zoom_in") or s.get("whip")]
    starts += [(s["t0"] + a["t"], "жест куклы") for s in shots if s.get("kind") == "doll"
               for a in s.get("actions", []) if a.get("do") in ("tilt", "look", "pose", "paw")]
    starts.sort()
    for (t1, k1), (t2, k2) in zip(starts, starts[1:]):    # Mital, Smith, Henderson: держит одно движущееся
        if t2 - t1 < ONE_MOTION_SEC:
            out.append(f"{k1} {t1:.2f} и {k2} {t2:.2f} с — два движения сразу: разведите на {ONE_MOTION_SEC} с")
    if total > LENGTH_WORK_SEC:
        out.append(f"рилс {total:.1f} с > {LENGTH_WORK_SEC:.0f}: каждую фразу сверх вилки проверить сжатием (07 §8 п.35)")
    pt = sorted(e["t"] for e in events if e.get("kind") == "punch")
    for a, b in zip(pt, pt[1:]):
        if b - a < PUNCH_MIN_GAP:
            out.append(f"наезды на {a:.2f} и {b:.2f} с — ближе {PUNCH_MIN_GAP} с: второй слабее, оставьте сильнейший")
    for s in shots:
        if s["t0"] >= LATE_ZONE * total and s["t1"] - s["t0"] > LATE_SHOT_SEC + 0.02:
            out.append(f"финал: план {s['t0']:.2f}–{s['t1']:.2f} с длиннее {LATE_SHOT_SEC} с — в последних 20 % уходят чаще")
    for i, b in enumerate(spec.get("beats", [])[:3]):
        for w in clean(b["text"]).split():
            if syllables(w) > LONG_WORD_SYLLABLES:
                out.append(f"фраза {i}: «{w}» — {syllables(w)} слогов в начале ролика: проще слово (тест незнакомца)")
    return out


if __name__ == "__main__":
    import json
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import reel
    spec = json.load(open(os.path.join(sys.argv[1], "reel.json"), encoding="utf8"))
    log_p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "reels_log.json")
    log = json.load(open(log_p, encoding="utf8")) if os.path.exists(log_p) else []
    errs = check_spec(spec, set(reel.SFX)) + check_passport(spec, log, os.path.relpath(sys.argv[1])) + check_knowledge(spec)
    print("\n".join("✗ " + e for e in errs) or "✓ reel.json по правилам (тайминг проверит reel.py при рендере)")
    sys.exit(1 if errs else 0)
