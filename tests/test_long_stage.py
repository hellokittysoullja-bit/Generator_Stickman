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


def test_every_stage_moment_is_on_screen_even_without_its_own_sound():
    """Звук смысла на слове появления элемента прилипает к его кадру, даже если у элемента своего звука нет (L03,
    фраза 7: level_up на «двадцать» звучал на 36 мс раньше кота с книгой)."""
    sp = long_stage.times(_items(), lambda at: long_edit.word_time(at, WORDS), 0.4)
    assert [round(t, 2) for t in long_stage.beats(sp)] == [0.0, 1.4, 2.6]
    assert len(long_stage.sounds(sp)) == 1


# --- вырезка: SAM + край по туши (владелец 04.11: «обрезается без каких-либо других объектов») ---------------------
PAPER = (250, 248, 242)


def _sheet():
    return np.full((300, 400, 3), PAPER, np.uint8)


def _ring(img, c, r, w=4, color=(20, 20, 20)):
    import cv2
    cv2.circle(img, c, r, color, w)


def test_refine_keeps_the_object_and_drops_a_touching_neighbour():
    """Сосед касается предмета (лапа на песочных часах): SAM его не взял — край по туши не дорастит его обратно."""
    import cv2
    img = _sheet()
    cv2.rectangle(img, (100, 100), (200, 220), (90, 90, 90), -1)          # предмет
    cv2.rectangle(img, (200, 60), (300, 110), (20, 20, 20), -1)           # сосед касается угла
    sam = np.zeros(img.shape[:2], np.uint8)
    sam[101:220, 101:199] = 1                                              # SAM срезал край на 1–2 px
    a = long_stage.refine(img, sam) > 0.5
    assert a[150, 150] and a[100, 100] and a[219, 199]                    # контур возвращён
    assert not a[70, 260] and not a[105, 250]                             # сосед — нет


def test_refine_keeps_a_drawn_surface_sam_punched_through():
    """Страница в рамке (тон чуть темнее бумаги): дыра SAM посреди неё — всё равно предмет."""
    import cv2
    img = _sheet()
    cv2.rectangle(img, (130, 90), (260, 210), (20, 20, 20), 4)
    img[94:207, 134:257] = (238, 236, 230)
    sam = np.zeros(img.shape[:2], np.uint8)
    sam[90:211, 130:261] = 1
    sam[120:180, 160:230] = 0
    a = long_stage.refine(img, sam) > 0.5
    assert a[150, 195] and a[100, 195]


def test_refine_drops_paper_seen_through_a_handle():
    """Просвет ручки — той же бумаги, что снаружи, и SAM его не покрыл: прозрачный; само кольцо — предмет."""
    import cv2
    img = _sheet()
    _ring(img, (200, 150), 60)
    sam = np.zeros(img.shape[:2], np.uint8)
    cv2.circle(sam, (200, 150), 62, 1, -1)
    cv2.circle(sam, (200, 150), 57, 0, -1)                                # SAM — по самой линии (кружка L03: 0,0)
    a = long_stage.refine(img, sam) > 0.5
    assert a[150, 140] and a[90, 200]                                      # кольцо
    assert not a[150, 200]                                                 # просвет


def test_refine_attaches_a_small_coloured_part_sam_left_out():
    """Огонёк на хвосте: цветная часть, касающаяся предмета и меньше его, — его; серая линия соседа — нет."""
    import cv2
    img = _sheet()
    cv2.circle(img, (150, 170), 60, (30, 30, 30), -1)
    cv2.circle(img, (150, 95), 14, (240, 120, 20), -1)                    # огонёк касается сверху
    cv2.line(img, (215, 120), (215, 230), (120, 120, 120), 3)             # серая линия рядом (спинка стула)
    sam = np.zeros(img.shape[:2], np.uint8)
    cv2.circle(sam, (150, 170), 59, 1, -1)
    a = long_stage.refine(img, sam) > 0.5
    assert a[95, 150] and not a[170, 215]


def test_sam_pick_prefers_the_solid_mask_when_both_fill_the_box():
    box = (10, 10, 110, 110)
    solid = np.zeros((200, 200), np.uint8)
    solid[10:110, 10:110] = 1
    hollow = solid.copy()
    hollow[30:90, 30:90] = 0
    assert long_stage.pick_mask([hollow, solid], box) is solid


def test_cutout_falls_back_when_sam_is_not_available(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("нет модели")
    monkeypatch.setattr(long_stage, "_sam_masks", boom)
    assert long_stage._sam_object("x.png", np.zeros((10, 10, 3), np.uint8), (0, 0, 5, 5)) is None


# --- стикеры и рваная бумага (владелец 04.11: «первое берём») ----------------------------------------------------
def test_items_are_stickers_with_a_white_border_that_boils_twelve_times_a_second():
    st = long_stage.sticker(_blob())
    assert st.shape[0] > _blob().shape[0]                                      # обводка снаружи
    a = st[..., 3]
    edge = st[(a > 200) & (np.asarray(np.pad(_blob()[..., 3], (st.shape[0] - 200)//2)) == 0)]
    assert edge.size and edge[..., :3].mean() > 240                             # и она белая
    assert long_stage.boil(0.01, 0) == long_stage.boil(0.07, 0)                 # одна поза на 1/12 с
    assert long_stage.boil(0.01, 0) != long_stage.boil(0.10, 0)


def test_paper_tear_starts_on_the_old_frame_and_ends_on_the_new():
    import paper_tear
    before = np.full((108, 192, 3), 30.0, np.float32)
    after = np.full((108, 192, 3), 220.0, np.float32)
    first = paper_tear.compose(before, after, 0.0)
    last = paper_tear.compose(before, after, 1.0)
    assert first.mean() < 70                                                    # лист ещё цел
    assert abs(last.mean() - 220) < 8                                           # лист улетел
    big = np.full((540, 960, 3), 30.0, np.float32)
    mid = paper_tear.compose(big, np.full((540, 960, 3), 220.0, np.float32), 0.35)
    assert (mid > 240).any()                                                    # белые волокна рваного края


def test_tear_needs_a_previous_shot_and_its_own_sound(tmp_path):
    bad = {"frames": {"3": {"shots": [{"why": "первый план и сразу разрыв", "tear": True, "sound": "swoosh"},
                                      {"why": "разрыв без звука", "at": "x", "tear": True}]}}}
    (tmp_path / "edit.json").write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    err = long_rules.stage_checks(str(tmp_path))
    assert any("план 1" in e and "TEAR" in e for e in err) and any("без звука" in e for e in err)


def test_stage_labels_do_not_fade_before_a_tear():
    """Лист с подписями рвётся целиком: перед планом с "tear" подписи сцены не тают (L03, фраза 56)."""
    fr = {"SW": 2528, "SH": 1696, "off": (0, 0)}
    segs = long_edit.segments(fr, [{"why": "три приёма тремя предметами на бумаге", "stage": _items()},
                                   {"at": "десять", "win": [500, 500, 600], "why": "лист рвётся, под ним морда",
                                    "tear": True, "sound": "swoosh"}], WORDS, 5.0)
    assert segs[0]["stage"].get("hold_labels") and segs[1]["tear"]
    st = long_stage.Stage(segs[0]["stage"], [_blob(), _blob(), _blob()], segs[0]["t1"] - segs[0]["t0"])
    end = segs[0]["t1"] - segs[0]["t0"] - 0.02
    held = st.frame(end)
    segs[0]["stage"]["hold_labels"] = False
    faded = long_stage.Stage(segs[0]["stage"], [_blob(), _blob(), _blob()], end + 0.02).frame(end)
    assert (held < 60).sum() > (faded < 60).sum()                               # чёрная обводка подписей на месте
