"""Стражи рилса (22.10): новый агент с нуля не должен сделать рилс хуже эп.02.

Правила — в scripts/reel_rules.py, reel.py не рендерит рилс, который их нарушает. Здесь проверено, что каждое правило
ловит своё нарушение, что одобренный рилс эп.02 проходит, и что одобренные владельцем значения стоят по умолчанию."""
import copy
import json
import os

import reel
import reel_rules

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP02 = os.path.join(ROOT, "videos", "02_sdvg_vremya", "reel", "reel.json")
SFX = set(reel.SFX)


def spec():
    return json.load(open(EP02, encoding="utf8"))


def broken(fn):
    s = spec(); fn(s); return reel_rules.check_spec(s, SFX)


def test_approved_ep02_reel_passes():
    assert reel_rules.check_spec(spec(), SFX) == []


def test_only_owner_sounds_and_no_music():
    assert {"riser", "swoosh", "swoosh_deep", "oof"} <= set(reel.SFX)
    for name, v in reel.SFX_LIB.items():          # у каждого звука библиотеки — файл и описание «что значит, когда ставить»
        assert os.path.exists(os.path.join(reel.SFX_DIR, v["file"])), name
        for key in ("sound", "meaning", "use", "avoid", "peak_sec", "level_db"):
            assert v.get(key) not in (None, ""), (name, key)
    assert broken(lambda s: s["beats"][3].setdefault("fx", []).append({"kind": "sfx", "name": "tick"}))
    assert broken(lambda s: s.__setitem__("music", "track.mp3"))


def test_hook_rules():
    assert broken(lambda s: s["beats"][0].__setitem__("text", "Ты, скорее всего, вовсе не ленишься, а просто устал."))
    assert broken(lambda s: s["beats"][0].__setitem__("fx", []))                                  # нет riser
    assert broken(lambda s: s["beats"][0]["fx"][0].__setitem__("dt", 0.6))                       # riser поздно
    assert broken(lambda s: s["beats"][0]["fx"][0].__setitem__("after", True))                   # «после хука» — старое
    assert broken(lambda s: s["beats"][1].pop("after_sfx"))                                      # раскрытие не на пике


def test_layout_and_loop():
    assert broken(lambda s: s.__setitem__("picture_h", 1100))
    assert broken(lambda s: s["beats"][-1]["shots"][0].__setitem__("src", "f4"))


def test_timeline_rules():
    peaks = {k: v[1] for k, v in reel.SFX.items()}
    ok = [dict(t0=0.0, t1=1.65), dict(t0=1.65, t1=4.0), dict(t0=4.0, t1=6.5)]
    riser = [dict(kind="sfx", name="riser", align="start", t=0.0)]
    assert reel_rules.check_timeline(ok, riser, peaks) == []
    assert reel_rules.check_timeline([dict(t0=0.0, t1=1.65), dict(t0=1.65, t1=5.2)], riser, peaks)   # план 3.55 с
    assert reel_rules.check_timeline([dict(t0=0.0, t1=2.6), dict(t0=2.6, t1=4.0)], [], peaks)          # склейка поздно
    assert reel_rules.check_timeline(ok, [dict(riser[0], t=0.5)], peaks)                               # пик мимо склейки


def test_approved_values_are_defaults():
    s = {"beats": [{"text": "a", "shots": [{"src": "f1", "from": [0, 0, 100]}]}]}
    reel.layout(copy.deepcopy(s))
    assert reel.PH == 1420 and reel.CAP_CY == 1495
    s2 = copy.deepcopy(s); reel.layout(s2)
    assert abs(s2["beats"][0]["shots"][0]["from"][2] - 112.0) < 1e-6          # view_scale 1.12 по умолчанию
    reel.layout({"beats": [], "picture_h": 1100})                              # вернуть модуль как был


def test_segment_cache_key_sees_only_what_the_shot_shows():
    shots = [dict(t0=0.0, t1=2.0, src="f1", **{"from": [1, 1, 100]}), dict(t0=2.0, t1=4.0, src="f1", **{"from": [2, 2, 100]}),
             dict(t0=4.0, t1=12.0, src="f1", **{"from": [3, 3, 100]}), dict(t0=12.0, t1=14.0, src="f1", **{"from": [4, 4, 100]})]
    ev = [dict(kind="punch", t=1.0, amt=0.1), dict(kind="punch", t=13.0, amt=0.1)]
    key = lambda e: reel.segment_key("/nonexistent", 30, 0, 60, 0, shots, e, [], [], [], None, 14.0, "v")
    base = key(ev)
    assert key([dict(ev[0], amt=0.2), ev[1]]) != base          # своё событие поменялось — план перерисуется
    assert key([ev[0], dict(ev[1], amt=0.2)]) == base          # событие через 12 с — план из кэша
    assert key([dict(ev[0], _anchor={1: 2}), ev[1]]) == base   # служебное поле рендера ключ не меняет
