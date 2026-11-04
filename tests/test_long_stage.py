"""Сцены на бумаге длинного ролика (scripts/long_stage.py, владелец 04.11 по монтажу канала-образца): вырезки и две
карточки на кремовой бумаге со слабой виньеткой; элементы встают на словах, подпись едет со своим элементом, сцена в
edit.json проверяется кодом и её звуки ложатся на те же слова."""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import long_edit  # noqa: E402
import long_rules  # noqa: E402
import long_stage  # noqa: E402

W, H = long_stage.W, long_stage.H
WORDS = [{"word": "Досчитать", "start": 0.4, "end": 0.9}, {"word": "одно", "start": 1.6, "end": 1.8},
         {"word": "окно", "start": 1.8, "end": 2.2}, {"word": "десять", "start": 3.0, "end": 3.4}]


def _blob(color=(30, 30, 30)):
    a = np.zeros((200, 160, 4), np.uint8)
    a[20:180, 20:140, :3] = color
    a[20:180, 20:140, 3] = 255
    return a


def _items():
    return {"type": "items", "items": [{"src": "a", "box": [0, 0, 1, 1], "label": "ДО 10", "at": "Досчитать"},
                                       {"src": "b", "box": [0, 0, 1, 1], "label": "ОДНО ОКНО", "at": "окно",
                                        "sound": "swoosh"},
                                       {"src": "c", "box": [0, 0, 1, 1], "label": "10 МИНУТ", "at": "десять"}]}


def test_elements_appear_on_their_words_and_their_sounds_follow():
    sp = long_stage.times(_items(), lambda at: long_edit.word_time(at, WORDS), 0.4)
    assert [round(e["t"], 2) for e in sp["items"]] == [0.0, 1.4, 2.6]       # от начала плана, а не ролика
    assert [(round(t, 2), n) for t, n, _ in long_stage.sounds(sp)] == [(1.4, "swoosh")]


def test_cards_focus_on_its_word():
    sp = {"type": "cards", "cards": [{"src": "a", "label": "МИФ"}, {"src": "b", "label": "ПРАВДА", "at": "окно"}],
          "focus": 1, "focus_at": "десять", "focus_sound": "swoosh_deep"}
    sp = long_stage.times(sp, lambda at: long_edit.word_time(at, WORDS), 0.0)
    assert round(sp["focus_t"], 2) == 3.0
    assert ("swoosh_deep" in [n for _, n, _ in long_stage.sounds(sp)])


def test_lonely_element_stands_in_the_middle_and_the_group_spreads_for_the_next():
    """Первый элемент не висит в углу, пока не пришёл второй (L03, фраза 16: карточка 2,5 с в левой четверти)."""
    sp = long_stage.times({"type": "cards", "cards": [{"src": "a", "at": "Досчитать"}, {"src": "b", "at": "десять"}]},
                          lambda at: long_edit.word_time(at, WORDS), 0.0)
    st = long_stage.Stage(sp, [_blob(), _blob()], 6.0)
    assert abs(st.xs[0] + st.shift(1.0) - W/2) < 1                       # одна карточка — по центру
    assert abs(st.shift(3.0 + long_stage.GROUP_SEC + 0.01)) < 1          # пришла вторая — обе на своих местах


def test_stage_frame_is_cream_paper_with_a_weak_vignette_and_the_element_on_it():
    sp = long_stage.times(_items(), lambda at: long_edit.word_time(at, WORDS), 0.4)
    st = long_stage.Stage(sp, [_blob(), _blob(), _blob()], 5.0)
    f = st.frame(4.0)
    assert f.shape == (H, W, 3)
    centre, corner = f[200:260, W//2 - 50:W//2 + 50].mean(), f[:60, :60].mean()     # пустая бумага
    assert 0 < centre - corner < 0.12*centre                              # виньетка есть, но слабая
    assert f[int(H*0.5), int(st.xs[1] + st.shift(4.0))].mean() < 80       # элемент лёг на бумагу


def test_stage_shot_needs_no_camera_window():
    fr = {"SW": 2528, "SH": 1696, "off": (0, 0)}
    segs = long_edit.segments(fr, [{"why": "три приёма тремя предметами на бумаге", "stage": _items()},
                                   {"at": "десять", "win": [500, 500, 600], "why": "морда кота на «десять минут»"}],
                              WORDS, 5.0)
    assert segs[0]["stage"]["items"][1]["t"] > 0 and segs[0]["win"] == segs[0]["win_to"]


def test_stage_spec_is_checked(tmp_path):
    bad = {"frames": {"3": {"shots": [
        {"why": "две вырезки рядом", "stage": {"type": "items", "items": [{"src": "a", "label": "один два три четыре"}]}},
        {"why": "карточки сравнения", "at": "x", "stage": {"type": "cards", "cards": [{"src": "a"}]}},
        {"why": "непонятная сцена", "at": "y", "stage": {"type": "grid", "items": []}}]}}}
    (tmp_path / "edit.json").write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    err = long_rules.stage_checks(str(tmp_path))
    assert any("нет рамки" in e for e in err) and any("длиннее трёх слов" in e for e in err)
    assert any("ровно две" in e for e in err) and any("grid" in e for e in err)
