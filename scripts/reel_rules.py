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
HOOK_TYPES = ("диссонанс", "вопрос", "число", "POV", "середина истории", "что если", "термин", "ошибка/запрет",
              "желаемый результат", "сравнение", "секрет/закулисье", "абсурд", "прямое обращение к узнаванию")
MAX_DEVICE_OVERLAP = 0.5   # приёмы нового рилса совпадают с прошлым не больше чем наполовину


def check_passport(spec, log, reel_dir=""):
    """Паспорт рилса против журнала: тип хука и первые слова не как у предыдущего рилса, приёмы не те же."""
    err = []
    pp = spec.get("passport")
    if not pp:
        return ["нет паспорта рилса (passport: hook_type, structure, devices) — без него не проверить шаблонность"]
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
