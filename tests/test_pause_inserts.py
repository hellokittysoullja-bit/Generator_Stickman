"""fix_pauses.py вставляет тишину, доводя тег-паузы до документированной длины (pause_inserts), — пересчёт
времени голоса обязан её учитывать (L01 27.10: 24 вставки, +4.9 с, картинка обгоняла голос на секунду)."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import speech_timing as st  # noqa: E402


def test_raw_to_real_subtracts_cuts_and_adds_inserts():
    m = st.PauseMap([(10.0, 10.5)])
    m.inserts = [(5.0, 0.2), (20.0, 0.3)]
    assert st.raw_to_real_time(4.0, m) == 4.0
    assert abs(st.raw_to_real_time(8.0, m) - 8.2) < 1e-9          # после вставки
    assert abs(st.raw_to_real_time(15.0, m) - 14.7) < 1e-9        # вставка +0.2, вырез −0.5
    assert abs(st.raw_to_real_time(25.0, m) - 25.0) < 1e-9        # ещё вставка +0.3


def test_pause_cuts_reads_inserts_from_fix_pauses(tmp_path):
    (tmp_path / "media_plan").mkdir()
    (tmp_path / "media_plan" / "pause_cuts.json").write_text(json.dumps(
        {"cuts": [[1.0, 1.5]], "pause_inserts": [[3.0, 0.25]]}), encoding="utf-8")
    m = st.SpeechTiming(str(tmp_path)).pause_cuts()
    assert list(m) == [(1.0, 1.5)] and m.inserts == [(3.0, 0.25)]
    assert abs(st.raw_to_real_time(4.0, m) - 3.75) < 1e-9
