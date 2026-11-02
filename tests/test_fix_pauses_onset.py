"""Подрезка пауз не срезает атаку слова (аудит звука L02: 4–16 мс начала слов на 22 склейках)."""
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import fix_pauses  # noqa: E402


def test_silence_end_stops_before_the_word_attack(tmp_path):
    sr = 48000
    t = np.arange(int(3.5 * sr)) / sr
    x = np.zeros_like(t)
    on = (t >= 2.0) & (t < 3.5)
    x[on] = 0.5 * np.sin(2 * np.pi * 220 * t[on])
    wav = tmp_path / "v.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-", str(wav)],
                   input=x.astype(np.float32).tobytes(), check=True)
    pairs = fix_pauses.detect_silences(str(wav), total=3.5)
    ss, se = pairs[0]
    assert ss < 0.05 and 2.0 - fix_pauses.ONSET_GUARD_SEC - 0.02 <= se <= 2.0 - fix_pauses.ONSET_GUARD_SEC + 0.02
