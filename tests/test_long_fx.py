"""Кот-ведущий и жирный текст длинного ролика (scripts/long_fx.py, пробник 28.10)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import long_fx as fx  # noqa: E402


def test_free_spot_keeps_bold_text_off_the_drawing():
    # пробник 28.10: «2 минуты» легли на ухо кота, потом на стопку бумаг и за край кадра
    f = np.full((fx.H, fx.W, 3), 245, np.float32)
    f[:, :1300] = 30                                 # рисунок слева во всю высоту
    cx, cy, size, share = fx.free_spot(f, "2 минуты", 150, prefer=(600, 300))
    _, _, tw, _ = fx._glyphs("2 минуты", size)
    assert share <= 0.015
    assert cx - tw/2 >= 1300 and cx + tw/2 <= fx.W*0.95   # не на рисунке и не за краем
    assert cy <= fx.H*0.88


def test_free_spot_shrinks_text_before_putting_it_on_ink():
    f = np.full((fx.H, fx.W, 3), 245, np.float32)
    for k in range(4):                               # рисунок по всему кадру: полосы туши 4 px через 20 px
        f[:, k::20] = 30
    f[100:300, 1200:1800] = 245                      # чистое место уже строки полного кегля
    _, _, size, share = fx.free_spot(f, "2 минуты", 150)
    assert size < 150 and share <= 0.015


def test_narrator_is_alive_within_a_short_appearance():
    # владелец 28.10: «чтоб двигал хвостом, ушками, головой… чтоб живой был»; фон куклы за 4 с давал хвост 3,6°,
    # уши — ни разу
    words = [{"word": "Знакомо?", "start": 0.0, "end": 0.6}, {"word": "много", "start": 1.0, "end": 1.3},
             {"word": "думал", "start": 1.7, "end": 2.0}]
    n = fx.Narrator(4.0, words=words, text="Знакомо? много думал", glance=(-0.6, -0.2))
    ts = [k/24 for k in range(96)]
    st = [n.state(t) for t in ts]
    tail = [s["tail"] for s in st]
    assert max(tail) - min(tail) >= 10                # хвост ходит заметно
    assert min(s["ear"] for s in st) <= -10           # ухо дёргается хотя бы раз
    head = [s["head"] for s in st]
    assert max(head) >= fx.Q_TILT - 0.5               # наклон на вопрос зрителю
    i = int(np.argmax(head))
    assert ts[i] > fx.GROW_SEC                        # и не во время роста
    assert any(s["look"][0] < -0.4 for s in st)       # взгляд на текст рядом и обратно
    assert abs(st[-1]["look"][0]) < 0.1
    steps = np.abs(np.diff(head))
    assert steps.max() < 2.0                          # без рывков головы между кадрами


def test_bold_text_outline_stays_weak():
    # владелец дважды: «чуть-чуть сильнее» — обводка тонкая и полупрозрачная, не наклейка
    assert fx.STROKE <= 3 and 0.8 <= fx.STROKE_ALPHA < 1.0


def test_fx_json_needs_why(tmp_path):
    (tmp_path / "fx.json").write_text('{"phrases": {"3": {"narrator": {}}}}', encoding="utf-8")
    import pytest
    with pytest.raises(ValueError):
        fx.load(str(tmp_path))
    (tmp_path / "fx.json").write_text('{"phrases": {"3": {"narrator": {"why": "объяснение"}, '
                                      '"bold": [{"text": "2 минуты", "word": "двух", "why": "цифра"}]}}}', encoding="utf-8")
    got = fx.load(str(tmp_path))
    assert list(got) == [2] and got[2]["narrator"]["why"] == "объяснение"


def test_events_put_text_on_its_word_and_narrator_on_the_phrase():
    words = [{"word": "Первое:", "start": 2.0, "end": 2.4}, {"word": "двух", "start": 3.1, "end": 3.4},
             {"word": "минут", "start": 3.4, "end": 3.8}]
    ev = fx.events({"narrator": {"why": "x"}, "bold": [{"text": "2 минуты", "word": "двух", "why": "x"}]},
                   1.9, 9.0, words, "Первое: двух минут", seed=1)
    nar = next(e for e in ev if e["kind"] == "narrator")
    bold = next(e for e in ev if e["kind"] == "bold")
    assert (nar["t0"], nar["t1"]) == (1.9, 9.0)
    assert nar["words"][1]["start"] == 3.1 - 1.9 - fx.ENTER_SEC      # слова — от выхода кота
    assert abs(bold["t0"] - 3.05) < 1e-9 and bold["t1"] == 9.0        # с котом — до конца фразы
    plain = fx.events({"narrator": None, "bold": [{"text": "2 минуты", "word": "двух", "why": "x"}]},
                      1.9, 9.0, words, "", seed=1)
    assert plain[0]["t1"] - plain[0]["t0"] <= fx.BOLD_HOLD_SEC + 1e-9   # без кота строка не висит через склейки


def test_track_keeps_bold_text_off_the_narrator():
    # встройка 28.10: на перелёте роста ухо кота задевало «Знакомо?»
    ev = fx.events({"narrator": {"why": "x"}, "bold": [{"text": "Знакомо?", "word": "Знакомо", "why": "x"}]},
                   0.0, 3.0, [{"word": "Знакомо?", "start": 0.05, "end": 0.6}], "Знакомо?", seed=0)
    tr = fx.Track(ev, 3.0)
    f = np.full((fx.H, fx.W, 3), 240, np.float32)
    out = tr.apply(f, 0.7)
    b = next(e for e in tr.bold)
    box = tr.nar[0][2]
    o = b["obj"]
    assert o.cx + o.width/2 < box[0] or o.cy + o.h/2 < box[1]          # строка левее кота или выше него
    assert o.size == fx.SIZE_NARRATOR                                   # под котом кегль полный
    assert out.shape == f.shape and not np.array_equal(out, f)
