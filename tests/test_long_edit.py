"""Ручной монтаж кадров длинного ролика (scripts/long_edit.py, edit.json, владелец 28.10): план начинается на своём
слове, у каждого плана есть why, удар влетает из прошлого окна, прожектор темнит края."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import long_edit  # noqa: E402

WORDS = [{"word": "Сколько", "start": 0.0, "end": 0.4}, {"word": "когда", "start": 1.5, "end": 1.8},
         {"word": "С", "start": 3.2, "end": 3.3}, {"word": "когда", "start": 5.6, "end": 5.9}]
FR = {"off": (0, 0), "SW": 1600, "SH": 900}


def test_word_time_exact_word_then_occurrence():
    assert long_edit.word_time("С", WORDS) == 3.2               # «С», а не «Сколько»
    assert long_edit.word_time(["когда", 2], WORDS) == 5.6
    with pytest.raises(ValueError):
        long_edit.word_time("никогда", WORDS)


def test_segments_need_why_and_order():
    shots = [{"win": [800, 450, 1600], "why": "общий"}, {"at": "когда", "win": [400, 300, 600], "punch": True,
                                                          "shake": 8, "spot": [400, 300, 100], "why": "лицо"}]
    segs = long_edit.segments(FR, shots, WORDS, 7.0)
    assert [s["t0"] for s in segs] == [0.0, 1.5] and segs[-1]["t1"] == 7.0
    assert segs[1]["punch_from"] == segs[0]["win_to"]
    w = long_edit.window_at(segs[1], 1.5)
    assert w == pytest.approx(segs[0]["win_to"])                  # удар начинается из прошлого окна
    with pytest.raises(ValueError):
        long_edit.segments(FR, [{"win": [800, 450, 1600]}], WORDS, 7.0)


def test_spot_darkens_edges_not_focus():
    s = {"t0": 0.0, "spot": (960, 540, 100)}
    f = np.full((1080, 1920, 3), 200.0, np.float32)
    out = long_edit.spot(f, s, 1.0, (0, 0, 1920, 1080), 1920, 1080)
    assert out[540, 960, 0] == pytest.approx(200) and out[10, 10, 0] == pytest.approx(150)
