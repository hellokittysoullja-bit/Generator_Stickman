"""Голос рилсов: шаблон из бренда, а не из `.env` машины; поле `voice` (теги интонации) не меняет слов фразы."""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import reel_voice  # noqa: E402


def test_reel_voice_uses_brand_template(monkeypatch):
    """26.10: рилс 06 озвучился шаблоном из `.env` (другой голос). Бренд главнее `.env`."""
    brand = json.load(open(reel_voice.BRAND, encoding="utf8"))["voice_template"]
    monkeypatch.setenv("LUMEAN_REEL_TEMPLATE_ID", "другой-шаблон")
    assert reel_voice.voice_template() == brand


def test_voice_field_keeps_words_and_adds_tags():
    beats = [dict(text="Идёшь *убираться*?", voice="[energetic] Идёшь убираться?"), dict(text="Но это не *лень*: |полы")]
    assert reel_voice.phrase_texts(beats) == ["[energetic] Идёшь убираться?", "Но это не лень: полы"]
    with pytest.raises(SystemExit):
        reel_voice.phrase_texts([dict(text="Идёшь убираться?", voice="[energetic] Идёшь мыть полы?")])
