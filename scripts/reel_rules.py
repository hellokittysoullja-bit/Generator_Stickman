"""Правила рилса — кодом, а не памятью агента (22.10, по вопросу владельца: «новый агент с нуля не должен сделать хуже»).

Каждое правило проверено на рилсе эп.02 и названо по своему источнику (подробно — docs/REELS_PLAYBOOK.md).
`reel.py` зовёт `check` перед рендером и не рендерит рилс с ошибкой (`--force` — только осознанно, с причиной).

    python scripts/reel_rules.py videos/NN/reel     # проверить reel.json без рендера
"""
import re

MAX_SHOT_SEC = 3.0         # план не дольше 3 с (разбор роликов о Reels: смена картинки каждые 2–3 с)
FIRST_CUT_SEC = 2.0        # первая склейка в первые 2 с — «решают первые 1–2 секунды» (владелец 22.10)
HOOK_MAX_CHARS = 30        # первая фраза читается за ~1.3–1.8 с при 17 знаках в секунду
RISER_START_MAX = 0.05     # riser звучит с нулевой секунды (владелец 22.10), а не после хука
RISER_PEAK_ON_CUT = 0.10   # пик riser — на склейке (Clumzzy: riser — ожидание перед раскрытием)
MIN_PICTURE_H = 1400       # владелец 22.10: «столько воздуха в рилсах не оставляют» — при 1100 низ был пуст
MAX_FROZEN_SHARE = 0.05    # доля почти неподвижных кадров готового файла (reel_metrics.py), v9 — 0.025


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
    if spec.get("picture_h", 1420) < MIN_PICTURE_H:
        err.append(f"picture_h {spec.get('picture_h')} < {MIN_PICTURE_H}: низ экрана будет пустой бумагой")
    first = next((s for s in beats[0]["shots"] if "src" in s), None)
    last = next((s for s in beats[-1]["shots"] if "src" in s), None)
    if first and last and first["src"] != last["src"]:
        err.append(f"петля: финал на {last['src']}, а начало на {first['src']} — конец = начало")
    return err


def check_timeline(shots, events, sfx_peaks):
    """Правила по рассчитанному таймингу: длина планов, первая склейка, пик riser на склейке."""
    err = []
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
    errs = check_spec(spec, set(reel.SFX))
    print("\n".join("✗ " + e for e in errs) or "✓ reel.json по правилам (тайминг проверит reel.py при рендере)")
    sys.exit(1 if errs else 0)
