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


def test_bold_text_outline_is_thick_black_like_reference():
    # 28.10 — тонкая полупрозрачная; 04.11 по образцу канала Дани: «чуть сильнее обводку… на постоянке»
    assert fx.STROKE >= 6 and fx.STROKE_ALPHA == 1.0


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
    ready = 1.9 + fx.ENTER_SEC + fx.GROW_SEC + fx.SETTLE_SEC + fx.BOLD_AFTER_NARRATOR
    assert abs(bold["t0"] - max(3.05, ready)) < 1e-9 and bold["t1"] == 9.0   # на слове, но не раньше, чем кот сел
    plain = fx.events({"narrator": None, "bold": [{"text": "2 минуты", "word": "двух", "why": "x"}]},
                      1.9, 9.0, words, "", seed=1)
    assert plain[0]["t1"] - plain[0]["t0"] <= fx.BOLD_HOLD_SEC + 1e-9   # без кота строка не висит через склейки


def test_track_keeps_bold_text_off_the_narrator():
    # встройка 28.10: на перелёте роста ухо кота задевало «Знакомо?»
    ev = fx.events({"narrator": {"why": "x"}, "bold": [{"text": "Знакомо?", "word": "Знакомо", "why": "x"}]},
                   0.0, 3.0, [{"word": "Знакомо?", "start": 0.05, "end": 0.6}], "Знакомо?", seed=0)
    tr = fx.Track(ev, 3.0)
    f = np.full((fx.H, fx.W, 3), 240, np.float32)
    out = tr.apply(f, 2.0)                                       # строка — после того, как кот вырос и сел
    b = next(e for e in tr.bold)
    box = tr.nar[0][2]
    o = b["obj"]
    assert o.cx + o.width/2 < box[0] or o.cy + o.h/2 < box[1]          # строка левее кота или выше него
    assert o.size >= 0.72*fx.SIZE_NARRATOR                              # под котом — крупно, длинное мельчает
    assert out.shape == f.shape and not np.array_equal(out, f)


def test_narrator_waits_until_written_thought_is_read():
    # критик L02, фр.56→57: «его возвращают» ушла в размытие недописанной, целиком видна 0,25 с
    evs = [dict(kind="narrator", t0=5.0, t1=11.0, words=[dict(word="Хочешь", start=0.2, end=0.6)]),
           dict(kind="bold", text="листок", t0=5.4, t1=11.0, narrator=True)]
    out = fx.after_writing(evs, [5.5], 1.5)
    nar = next(e for e in out if e["kind"] == "narrator")
    assert nar["t0"] == 7.0 and abs(nar["words"][0]["start"] - (0.2 - 2.0)) < 1e-9
    bold = next(e for e in out if e["kind"] == "bold")
    ready = 7.0 + fx.ENTER_SEC + fx.GROW_SEC + fx.SETTLE_SEC + fx.BOLD_AFTER_NARRATOR
    assert bold["narrator"] is True and bold["t0"] >= ready - 1e-9   # строка кота переезжает за котом (04.11)
    short = [dict(evs[0], t1=9.5), evs[1]]
    assert fx.after_writing(short, [7.9], 1.5)[0]["kind"] == "narrator_dropped"   # мысль почти до конца — ведущего нет
    assert fx.after_writing(evs, [1.0], 1.5)[0]["t0"] == 5.0                    # давно дописанная не мешает


def test_bold_lines_are_not_replaced_before_they_are_read():
    # критик L02, финал: «маленький шаг» сменилась на «записке возврата» недопечатанной («маленький ш», 0,7 с)
    words = [dict(word=w, start=s, end=s + 0.3) for w, s in (("телефон", 0.5), ("шаг", 1.2), ("записка", 1.7))]
    spec = {"bold": [dict(text="телефон", word="телефон", why="x"), dict(text="маленький шаг", word="шаг", why="x"),
                     dict(text="записка возврата", word="записка", why="x")]}
    ev = [e for e in fx.events(spec, 0.0, 6.0, words, "") if e["kind"] == "bold"]
    assert all(b["t0"] - a["t0"] >= fx.BOLD_MIN_SEC - 1e-9 for a, b in zip(ev, ev[1:]))


def test_scene_under_narrator_fades_toward_paper():
    # критик L02: размытый чёрный кот сцены под ведущим читался вторым котом
    f = np.zeros((40, 40, 3), np.float32)
    out = fx.focus_blur(f, 2.0, 0.0, 5.0)
    assert out.mean() > 0.3*245


def test_bold_line_place_accounts_for_later_shots():
    # критик L02: строка, чистая на первом кадре, ложилась на голову кота следующего плана
    clean = np.full((fx.H, fx.W, 3), 245, np.float32)
    later = clean.copy()
    later[0:500, 600:1400] = 30                      # следующий план: голова кота вверху по центру
    ev = [dict(kind="bold", text="Напарник", t0=0.0, t1=2.0, narrator=False, style="letters")]
    tr = fx.Track(ev, 3.0, peek=lambda t: later if t > 0.5 else clean)
    tr.apply(clean.copy(), 0.0)
    o = tr.bold[0]["obj"]
    beside = o.cx + o.width/2 < 600 or o.cx - o.width/2 > 1400
    below = o.cy - 0.45*o.size > 500
    assert beside or below


def test_parallax_moves_near_more_than_far_and_is_identity_at_start():
    """Параллакс по глубине (02.11): в начале плана кадр не меняется; ближнее сдвигается сильнее дальнего."""
    import depth_parallax as dp
    H, W = 120, 200
    img = np.full((H, W, 3), 240, np.float32)
    img[40:80, 90:110] = 30                                          # ближний предмет
    img[10:20, 20:30] = 120                                          # дальний предмет
    D = np.zeros((H, W), np.float32); D[35:85, 85:115] = 1.0          # глубина: предмет близко
    assert np.allclose(dp.apply(img, D, 0.0), img)
    out = dp.apply(img, dp.prepare(img, D), 1.0, dx=12, dz=0.0)
    near = np.argwhere(out[60, :, 0] < 100).mean() - 99.5
    far = np.argwhere(out[15, :, 0] < 180).mean() - 24.5
    assert abs(near) > abs(far) + 3


def test_narrator_text_comes_after_the_cat_and_leaves_with_it():
    """Владелец 04.11: «никогда не так, что кот появился и сразу жирный шрифт… сначала кот, чисто, потом текст с
    анимацией… и исчезает вместе с котом»."""
    words = [{"word": "Хочешь", "start": 0.05, "end": 0.4}, {"word": "сейчас", "start": 0.5, "end": 0.9}]
    spec = {"narrator": {"why": "x"}, "bold": [{"text": "попробуй", "word": "Хочешь", "why": "x"},
                                               {"text": "сейчас", "word": "сейчас", "why": "x"}]}
    ev = fx.events(spec, 0.0, 6.0, words, "Хочешь попробовать сейчас?", seed=0)
    bold = sorted((e for e in ev if e["kind"] == "bold"), key=lambda e: e["t0"])
    ready = fx.ENTER_SEC + fx.GROW_SEC + fx.SETTLE_SEC + fx.BOLD_AFTER_NARRATOR
    assert bold[0]["t0"] >= ready - 1e-9                              # кот сначала вырос и сел, фон чистый
    assert bold[1]["t0"] >= bold[0]["t0"] + fx.BOLD_MIN_SEC - 1e-9
    assert bold[-1]["t1"] == 6.0                                       # последняя строка уходит вместе с котом
    o = fx.BoldText("сейчас", 900, 300, size=120, t0=0.0)
    f = np.full((fx.H, fx.W, 3), 240, np.float32)
    shown = o.composite(f.copy(), 3.0, t_end=6.0)
    leaving = o.composite(f.copy(), 6.0 - fx.BOLD_EXIT_SEC/2, t_end=6.0)
    gone = o.composite(f.copy(), 6.0, t_end=6.0)
    ink = lambda g: float((np.abs(g - f) > 30).mean())                 # noqa: E731
    assert ink(shown) > ink(leaving) > ink(gone) == 0.0                 # уходит анимацией, а не щелчком


def test_text_sound_lands_where_the_line_is_seen_after_the_narrator_sat():
    """Звук строки — у самой строки: строка ведущего сдвинута за кота (BOLD_AFTER_NARRATOR), и её звук едет с ней
    (L03, фраза 8: свист «строка влетает» был на слове, на 1,5 с раньше строки). В подпись клипа звук не входит."""
    import frame_clip
    words = [{"word": "покажу", "start": 0.3, "end": 0.6}, {"word": "рыбка", "start": 0.7, "end": 1.0}]
    spec = {"narrator": {"why": "обещание"}, "bold": [{"text": "рыбка?", "word": "рыбка", "why": "вопрос",
                                                       "sound": "fast_whoosh"}]}
    ev = fx.events(spec, 0.0, 6.0, words, "покажу рыбка")
    snd = frame_clip.text_sounds({}, ev, 24)
    bold = next(e for e in frame_clip.final_fx({}, ev, 24) if e["kind"] == "bold")
    assert len(snd) == 1 and snd[0][1] == "fast_whoosh"
    assert snd[0][0] >= bold["t0"] - 1e-9 and snd[0][0] - bold["t0"] < 1/24
    assert bold["t0"] > 0.7 + 0.5                       # строка не на слове, а после того, как кот сел
    rec = frame_clip.plan_record({"hand": [{"text": "×4", "sound": "swoosh", "sound_why": "т"}], "segments": []})
    assert "sound" not in rec["hand"][0]
