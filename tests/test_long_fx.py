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
