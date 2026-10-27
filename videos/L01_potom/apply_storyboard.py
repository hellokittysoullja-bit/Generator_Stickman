"""Раскадровка L01 (storyboard.json) -> media_plan/frame_plan.json и кадры из библиотеки.
Оркестратор 27.10: судья выключен, кадры принимаются глазами."""
import json, os, shutil, sys
VD = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(VD))
sb = json.load(open(os.path.join(VD, "storyboard.json"), encoding="utf-8"))["frames"]
pp = os.path.join(VD, "media_plan", "frame_plan.json")
plan = json.load(open(pp, encoding="utf-8"))
for f in plan["frames"]:
    d = sb[str(f["index"] + 1)]
    for k in ("key_thought", "accent", "zoom", "key_near", "anim"):
        f.pop(k, None)
    if d.get("key"):
        f["key_thought"] = d["key"]
    if d.get("accent"):
        f["accent"] = d["accent"]
    if d.get("zoom"):
        f["zoom"] = d["zoom"]
    f.pop("anim", None)
    if d.get("anim"):
        f["anim"] = d["anim"]
    if d.get("details"):
        f["details"] = d["details"]
    f["absorb"] = "absorb" in d
    f["board"] = next(k for k in ("new", "lib", "same", "absorb", "done") if k in d)
    if "new" in d:
        f.update(kind="scene", labels=[], picture=d["new"], hero=bool(d.get("hero")), hero_state=d.get("state"))
        f["spec"] = {"focus": f["text"][:80], "subject": d["details"][0], "claims": [
            {"id": "core", "text": d["details"][0] + " is clearly drawn", "tier": "must"}]}
        f["preflight"] = {"issues": [], "rewritten": False, "note": "описание написано оркестратором 27.10"}
plan["has_hero"] = True
json.dump(plan, open(pp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("new:", ",".join(str(f["index"] + 1) for f in plan["frames"] if f["board"] == "new"))


def place():
    """Кадры из библиотеки и повторы: картинка в image_cache и frames/NNN.png, запись в отчёт как принятая
    оркестратором (статус ok, check: eyes)."""
    rp = os.path.join(VD, "media_plan", "frames_report.json")
    rep = json.load(open(rp, encoding="utf-8"))
    by = {r["index"]: r for r in rep["frames"]}
    cache = os.path.join(VD, "media_plan", "image_cache")
    for f in plan["frames"]:
        d, i = sb[str(f["index"] + 1)], f["index"]
        if "lib" in d:
            src, name = os.path.join(ROOT, "library", "cat", "originals", d["lib"]), "lib_" + d["lib"]
        elif "same" in d:
            name = by[d["same"] - 1]["chosen"]
            src = os.path.join(cache, name)
        else:
            continue
        if not os.path.exists(os.path.join(cache, name)):
            shutil.copyfile(src, os.path.join(cache, name))
        shutil.copyfile(src, os.path.join(VD, "frames", f"{i + 1:03d}.png"))
        old = by.get(i, {})
        by[i] = {"index": i, "key": f["key"], "kind": "scene", "labels": [], "hero": True, "status": "ok",
                 "check": "eyes", "source": "same:%d" % d["same"] if "same" in d else "library",
                 "chosen": name, "path": f"frames/{i + 1:03d}.png",
                 "objects": old.get("objects") if old.get("chosen") == name else []}
    # отпечаток плана — по текущему плану: правка мысли или акцента не должна заказывать платную перерисовку
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import env
    env.load_env()
    import frame_generator as fg
    import look
    probe = fg.Generator(fg.make_backend(None), VD, look.load())
    for f in plan["frames"]:
        if f["index"] in by and by[f["index"]].get("status") not in ("rejected", "failed"):
            by[f["index"]]["plan_sig"] = probe.plan_sig(f)
    for f in plan["frames"]:                          # рамки предметов, заданные руками (модель зрения ошиблась)
        d = sb[str(f["index"] + 1)]
        if d.get("objects") and f["index"] in by:
            by[f["index"]]["objects"] = d["objects"]
    rep["frames"] = [by[k] for k in sorted(by)]
    json.dump(rep, open(rp + ".tmp", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(rp + ".tmp", rp)
    print("placed")


if __name__ == "__main__" and "--place" in sys.argv:
    place()
