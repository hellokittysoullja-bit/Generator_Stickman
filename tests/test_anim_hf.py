"""Общий модуль сцен на HyperFrames (scripts/anim_hf.py): время из озвучки в data-vars, ключ кэша (без рендера)."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import anim_hf  # noqa: E402


def _project(tmp_path, vars_json='{"hit": 0.94}'):
    p = tmp_path / "proj"; p.mkdir()
    (p / "index.html").write_text(f"<div id=\"root\" data-vars='{vars_json}'></div>", encoding="utf-8")
    a = tmp_path / "assets"; a.mkdir()
    (a / "body.png").write_bytes(b"x")
    return str(p), str(a)


def test_default_vars_and_signature_follow_timing_and_layers(tmp_path):
    p, a = _project(tmp_path)
    assert anim_hf.default_vars(p) == {"hit": 0.94}
    s1 = anim_hf.signature(p, a, {"hit": 0.94}, 30)
    assert anim_hf.signature(p, a, {"hit": 1.10}, 30) != s1           # другое время удара — другие кадры
    open(os.path.join(a, "body.png"), "wb").write(b"y")
    assert anim_hf.signature(p, a, {"hit": 0.94}, 30) != s1           # перерезали слой — кадры пересобираются


def test_existing_scenes_are_on_the_shared_module():
    root = os.path.join(os.path.dirname(__file__), "..", "videos")
    for scene, proj in (("13_dver/reel/anim/door_hf.py", "13_dver/reel/anim/door_hf"),
                        ("L02_otvlechenie/anim/fridge_light.py", "L02_otvlechenie/anim/fridge_hf")):
        src = open(os.path.join(root, scene), encoding="utf-8").read()
        assert "anim_hf.Scene(" in src
        assert isinstance(anim_hf.default_vars(os.path.join(root, proj)), dict)
    json.dumps(anim_hf.default_vars(os.path.join(root, "13_dver/reel/anim/door_hf")))
