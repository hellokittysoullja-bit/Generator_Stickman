"""Звуки длинного ролика на событиях (scripts/long_sfx.py, 27.10): у каждого звука есть зачем, слово ищется в своей
фразе, чужой или ненайденный звук — ошибка, а не догадка."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import long_sfx  # noqa: E402

STARTS = [0.0, 6.0]
WORDS = [[{"word": "Сколько", "start": 0.1, "end": 0.5}, {"word": "понедельника,", "start": 3.0, "end": 3.6}],
         [{"word": "Но", "start": 6.1, "end": 6.2}]]


def test_word_and_offset_resolve_to_absolute_time():
    ev, errs = long_sfx.resolve([{"name": "fast_whoosh", "phrase": 1, "word": "понедельник", "offset": 0.1, "why": "лист"},
                                 {"name": "riser", "phrase": 2, "at": 0.0, "why": "поворот"}], STARTS, WORDS)
    assert errs == []
    assert [round(e["t"], 2) for e in ev] == [3.1, 6.0]


def test_sound_without_reason_or_unknown_or_missing_word_is_an_error():
    _, errs = long_sfx.resolve([{"name": "fast_whoosh", "phrase": 1, "at": 0},
                                {"name": "music_sting", "phrase": 1, "at": 0, "why": "x"},
                                {"name": "oof", "phrase": 2, "word": "никогда", "why": "x"}], STARTS, WORDS)
    assert len(errs) == 3
