"""Общее для сборщиков reel.json охватных рилсов: перенос матрицы и инвентаря с эп.01 v12 по ролям фраз."""
import json, sys
ROOT = "/home/user/Generator_Stickman"
sys.path.insert(0, ROOT + "/scripts")
import reel_rules as R
EP01 = json.load(open(ROOT + "/videos/01_sdvg_pismo/reel/reel.json", encoding="utf8"))["passport"]

def doll(at, cx=540, cy=760, h=640, actions=(), **kw):
    return dict(at=at, kind="doll", cx=cx, cy=cy, h=h, zoom=kw.pop("zoom", [1.0, 1.06]), actions=list(actions), **kw)

CLOSE = dict(cx=770, cy=580, h=1150, closeup=True)

def b(*bs, how=None): return dict(beats=list(bs), how=how) if how else list(bs)
def w(where, how): return dict(where=where, how=how)
def s(r): return dict(skip=r)

def transfer(beats, MAP, QUOTE, ncand):
    def ev_ok(ev, k):
        kind, _, name = str(ev).partition(":"); bb = beats[k]
        if kind == "gaps": return bool(bb.get("gaps"))
        if kind == "fx": return any(name in (e.get("kind"), e.get("name")) or (name == "strike" and "strike_at" in e) for e in bb.get("fx", []))
        if kind == "shot": return any(name in (x.get("src"), x.get("kind"), x.get("sound")) for x in bb["shots"])
        return False
    def remap(v):
        if isinstance(v, int) and not isinstance(v, bool): return [MAP[v]]
        if isinstance(v, list): return sorted({MAP[x] for x in v if isinstance(x, int)})
        if isinstance(v, dict) and "beats" in v:
            bs = sorted({MAP[x] for x in v["beats"]})
            out = {k: x for k, x in v.items() if k not in ("beats", "quote", "evidence")}
            if v.get("evidence") and any(ev_ok(v["evidence"], k) for k in bs):
                return dict(out, beats=bs, evidence=v["evidence"])
            return dict(out, beats=bs[:1], quote=QUOTE[bs[0]])
        return v
    matrix = {k: (dict(candidate=v["candidate"] % ncand) if isinstance(v, dict) and "candidate" in v else remap(v))
              for k, v in EP01["matrix"].items()}
    inventory = {k: remap(v) for k, v in EP01["inventory"].items()}
    return matrix, inventory

def save(path, spec):
    json.dump(spec, open(path, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print("ok", path, "фраз", len(spec["beats"]), "знаков", sum(len(R.clean(x["text"])) for x in spec["beats"]))

def perm(P):
    """Перестановка номеров фраз (старый -> новый) для полей паспорта: вставили фразу или убрали — номера в покрытии,
    знаниях, переносе матрицы и паспорте хука переезжают одной функцией, а не правкой каждого поля руками."""
    def m(v):
        if isinstance(v, bool): return v
        if isinstance(v, int): return P[v]
        if isinstance(v, list) and v and all(isinstance(x, int) and not isinstance(x, bool) for x in v):
            return sorted({P[x] for x in v})
        if isinstance(v, dict) and "beats" in v: return dict(v, beats=sorted({P[x] for x in v["beats"]}))
        return v
    return m

def apply_perm(passport, P):
    m = perm(P)
    passport["coverage"] = {k: m(v) for k, v in passport["coverage"].items()}
    passport["knowledge"] = {k: ({kk: m(vv) for kk, vv in v.items()} if k == "cta_reason_now" else m(v))
                             for k, v in passport["knowledge"].items()}
    po = passport["hook"]["payoff"]; po["tease"], po["pay"] = m(po["tease"]), m(po["pay"])
    passport["cta_beat"] = m(passport["cta_beat"])
    if "rehook" in passport["hook"]: passport["hook"]["rehook"] = m(passport["hook"]["rehook"])
    return passport
