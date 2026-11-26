"""Общая часть plan.py рилсов 111–116: shots.json и sound.json из voice/words.json (склейки — на начале слов)."""
import json
import os


def build(here, name, P, extra, sfx, keys, tail=0.95):
    words = json.load(open(os.path.join(here, "voice", "words.json"), encoding="utf8"))
    W = lambda i: round(words[i]["start"], 3)  # noqa: E731
    WE = lambda i: round(words[i]["end"], 3)  # noqa: E731
    end = round(WE(len(words) - 1) + tail, 2)
    shots = []
    for sid, scene, st, wh, what in P:
        t0 = round(WE(len(words) - 1) + 0.06, 3) if st is None else (st if isinstance(st, float) else W(st))
        shots.append(dict(id=sid, scene=scene, t0=t0, what=what, group="ext_a", **({"whip": True} if wh else {})))
    for a, b in zip(shots, shots[1:]):
        a["t1"] = b["t0"]
    shots[-1]["t1"] = end
    shots[0]["hook"] = True
    shots[0]["hit_word"] = 0
    for s in shots:
        s["dur"] = round(s["t1"] - s["t0"], 2)
    T = {s["id"]: s["t0"] for s in shots}
    T1 = {s["id"]: s["t1"] for s in shots}
    spec = {"_": f"Рилс {name} (формат 4, история кодом, голос по reel.json). План пересчитывает plan.py "
                 "по voice/words.json. Одна группа ext_a (scenes.py).", "fps": 30, "size": [1080, 1920], "pad": 0.2, "end": end}
    spec.update(extra(W, WE, T, T1, end))
    spec["shots"] = shots
    json.dump(spec, open(os.path.join(here, "shots.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    out = []
    for n, why, at in sfx(W, T):
        e = {"name": n, "why": why}
        e.update(at)
        if "word" in at:
            e["word_text"] = words[at["word"]]["word"]
        out.append(e)
    json.dump({"_": f"Звуки рилса {name} (plan.py). t — пик звука; word — индекс voice/words.json. Только assets/sfx/reels/library.json.",
               "keys": keys, "sfx": out}, open(os.path.join(here, "sound.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    for s in shots:
        print(s["id"], s["scene"], s["t0"], s["t1"], s["dur"], "!!" if s["dur"] > 2.5 else "")
    print("end", end, "sfx", len(out))
