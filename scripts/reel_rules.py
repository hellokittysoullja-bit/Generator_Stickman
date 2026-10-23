"""Правила рилса — кодом, а не памятью агента (22.10, по вопросу владельца: «новый агент с нуля не должен сделать хуже»).

Каждое правило проверено на рилсе эп.02 и названо по своему источнику (подробно — docs/REELS_PLAYBOOK.md).
`reel.py` зовёт `check` перед рендером и не рендерит рилс с ошибкой (`--force` — только осознанно, с причиной).

    python scripts/reel_rules.py videos/NN/reel     # проверить reel.json без рендера
"""
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
MIN_SHOT_SEC = 0.7         # план короче 0.7 с не читается (плейбук; v12 минимум 0.706)
MAX_SRC_CHANGES_30S = 10   # смен рисунка за любые 30 с (Lang 1999: перегрузка содержания), v12 — 9
CAP_HOLD_PAD = 0.6         # субтитр стоит не дольше чтения + 0.6 с (Szarkowska 2018, Stern 2024), v12 — максимум +0.47
CTA_BEFORE_END = 5.0       # призыв начинается не позже чем за 5 с до конца (финал — зона ухода: Dashlet, NSDI 2023)
LATE_ZONE, LATE_SHOT_SEC = 0.8, 2.0   # гипотеза: в последних 20 % планы ≤ 2 с (предупреждение, не запрет)
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
    prev = [r for r in log if os.path.normpath(r.get("reel", "")) != os.path.normpath(reel_dir)]
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


def warnings(spec, shots, total):
    """Гипотезы без доказанного порога — печатаются, рендер не останавливают."""
    out = []
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
    errs = check_spec(spec, set(reel.SFX)) + check_passport(spec, log, os.path.relpath(sys.argv[1]))
    print("\n".join("✗ " + e for e in errs) or "✓ reel.json по правилам (тайминг проверит reel.py при рендере)")
    sys.exit(1 if errs else 0)
