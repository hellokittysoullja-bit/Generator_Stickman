"""Вариант рилса для пробных Reels: другая первая фраза (и по желанию другой первый кадр) при том же остальном
(07 §8 п.3: 3–5 вариантов хука, победитель — по удержанию 3 с, пересылкам и переходам).

    python scripts/reel_variant.py videos/NN/reel --hook "Это не лень. Это время."            # -> videos/NN/reel_h1/
    python scripts/reel_variant.py videos/NN/reel --hook "…" --first "f5:1000,200,560"           # другой первый кадр
    python scripts/reel.py videos/NN/reel_h1                                                     # рендер варианта

Вариант помечен `passport.variant_of`: правило «против шаблона» не сравнивает его с родителем (это тот же рилс), а
остальные правила — хук ≤ 30 знаков, riser с 0 с, первая склейка ≤ 2 с — проверяются как обычно.
"""
import argparse
import json
import os
import shutil


def make(reel_dir, hook, first=None, name=None):
    spec = json.load(open(os.path.join(reel_dir, "reel.json"), encoding="utf8"))
    parent = os.path.relpath(os.path.abspath(reel_dir), os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    k = 1
    while name is None:
        cand = f"{os.path.abspath(reel_dir).rstrip(os.sep)}_h{k}"
        if not os.path.exists(cand): name = cand
        k += 1
    os.makedirs(name, exist_ok=True)
    if os.path.isdir(os.path.join(reel_dir, "src")) and not os.path.exists(os.path.join(name, "src")):
        shutil.copytree(os.path.join(reel_dir, "src"), os.path.join(name, "src"))
    old = spec["beats"][0]["text"]
    n_old, n_new = len(old.replace("|", "").split()), len(hook.replace("|", "").split())
    b0 = spec["beats"][0]
    for e in b0.get("fx", []):                     # слова сместились — события хука не дальше последнего слова
        if e.get("kind") != "sfx": e["at"] = min(e.get("at", 0), n_new - 1)
    for s in b0.get("shots", []):
        s["at"] = min(s.get("at", 0), n_new - 1)
    if spec.get("clock") and n_new != n_old:       # часы хука привязаны к словам фразы 0
        spec["clock"]["to_word"] = [0, n_new - 1]
    b0["text"] = hook
    if first:
        src, win = first.split(":"); cx, cy, h = (float(x) for x in win.split(","))
        b0["shots"][0].update({"src": src, "from": [cx, cy, h], "to": [cx, cy, h * 0.92]})
    pp = spec.setdefault("passport", {})
    pp["variant_of"] = parent
    pp["hook_variants"] = [old.replace("*", "")] + [v for v in pp.get("hook_variants", []) if v != hook.replace("*", "")][:4]
    json.dump(spec, open(os.path.join(name, "reel.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    return name


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("reel_dir"); ap.add_argument("--hook", required=True); ap.add_argument("--first"); ap.add_argument("--name")
    a = ap.parse_args()
    print(make(a.reel_dir, a.hook, a.first, a.name))
