"""Обязательная структура длинного ролика (scripts/long_rules.py, владелец 27.10: «без которой вообще невозможно
сделать ролик»): правильный ролик проходит, каждое нарушение ловится, make_video.py без неё дальше не идёт."""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import long_rules  # noqa: E402

FILLER = ("Кот смотрит на чашку и долго думает о своём деле. Потом он встаёт, идёт к окну и возвращается обратно. "
          "За окном шумит дождь, а на столе лежит открытая тетрадь. Хвост медленно качается, огонёк еле тлеет. "
          "Хочется начать, но рука сама тянется к телефону. И вот уже прошло полчаса, а тетрадь всё такая же пустая. "
          "Так бывает почти с каждым, кто ждёт подходящего настроения. ")

SCRIPT = f"""=== METADATA ===
TITLE: Почему ты откладываешь то, что любишь

=== HOOK ===
Ты откладываешь даже то, что любишь? И дело не в лени. Покажу, почему так выходит, что с этим делать сегодня и как начать за две минуты.
{FILLER}

=== BLOCK 1: Ловушка ===
Знаешь, что первым ломается утром? Я сидел над письмом и не мог открыть его до вечера. Мозг ждёт награду, а дело её прячет. Узнаёшь себя?
{FILLER}

=== BLOCK 2: Тело ===
А что, если дело не в голове? Это как машина зимой, её сначала греют. Поэтому первый шаг всегда маленький. А у тебя так бывает?
{FILLER}

=== BLOCK 3: Шаг ===
Вот самое странное. Я поставил таймер на две минуты и сел рядом с делом. Две минуты легко начать. Попробуешь?
{FILLER}

=== FINAL ===
Но есть одна ловушка, из-за которой всё это ломается к четвергу. Про неё следующий ролик.
"""


def passport(spoken_words):
    p = long_rules.template()
    p.update({
        "questions": ["почему откладываю любимое", "что с этим делать", "как начать", "это лень?", "у всех так?"],
        "promise": ["почему так выходит", "что с этим делать сегодня", "как начать за две минуты"],
        "climax": "Начало прячет награду",
        "skeleton": ["хук", "ловушка", "история кота", "тело", "шаг", "конец-хук"],
        "hook_candidates": [f"вариант {i}" for i in range(10)],
        "hook_voiced": ["voice/hook_a.wav", "voice/hook_b.wav"],
        "points": [
            {"block": "BLOCK 1: Ловушка", "rehook": "Знаешь, что первым ломается утром?", "unpack": "story",
             "unpack_quote": "Я сидел над письмом", "payoff_quote": "Мозг ждёт награду", "emotion": "тревога"},
            {"block": "BLOCK 2: Тело", "rehook": "А что, если дело не в голове?", "unpack": "metaphor",
             "unpack_quote": "Это как машина зимой", "payoff_quote": "первый шаг всегда маленький", "emotion": "смешно"},
            {"block": "BLOCK 3: Шаг", "rehook": "Вот самое странное.", "unpack": "story",
             "unpack_quote": "Я поставил таймер", "payoff_quote": "Две минуты легко начать", "emotion": "облегчение"},
        ],
        "end_hook": "Но есть одна ловушка, из-за которой всё это ломается к четвергу",
        "revision": {"words_before": int(spoken_words / 0.85), "words_after": spoken_words},
        "approved": {"title": True, "hook": True, "script": True},
    })
    p["items"] = {k: {"how": "сделано"} for k in p["items"]}
    p["final_checks"] = {"viewer_watch": ["2:10 скучно — сократил"], "distraction_test": "ок",
                         "phone_audio": "разборчиво", "outsider": "понял"}
    return p


def make(tmp_path, script=SCRIPT, edit=None):
    (tmp_path / "script.txt").write_text(script, encoding="utf-8")
    _, secs = long_rules.sections(script)
    p = passport(len(long_rules.words(" ".join(t for _, t in secs))))
    if edit:
        edit(p)
    (tmp_path / long_rules.PASSPORT).write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    return str(tmp_path)


def ids(errs):
    return {e.split(":")[0] for e in errs}


def test_valid_long_video_passes(tmp_path):
    vd = make(tmp_path)
    assert long_rules.check(vd, final=True) == []


def test_every_decide_rule_of_the_checklist_needs_a_decision(tmp_path):
    vd = make(tmp_path, edit=lambda p: p["items"].pop("H6"))
    assert "H6" in ids(long_rules.check(vd))
    decide = {it["id"] for it in long_rules.checklist() if it["kind"] == "decide"}
    assert decide == set(long_rules.template()["items"])     # заготовка содержит все пункты чек-листа


@pytest.mark.parametrize("old,new,rule", [
    ("TITLE: Почему ты откладываешь то, что любишь", "TITLE: " + "очень длинное название " * 4, "T1"),
    ("TITLE: Почему ты откладываешь то, что любишь", "TITLE: Успей понять, почему откладываешь", "T1"),
    ("Ты откладываешь даже", "Привет, это мой канал. Ты откладываешь даже", "H1"),
    ("как начать за две минуты", "как начать", "H3"),
    ("Знаешь, что первым ломается утром? Я сидел", "Я сидел", "P2"),
    ("Мозг ждёт награду, а дело её прячет. ", "", "P3"),
    ("Про неё следующий ролик.", "Про неё следующий ролик. Спасибо за просмотр!", "E1"),
    ("ломается к четвергу", "ломается к 4 числу", "R3"),
    ("Мозг ждёт награду", "Мозг — ждёт награду", "R4"),
])
def test_each_code_rule_is_caught(tmp_path, old, new, rule):
    assert old in SCRIPT
    vd = make(tmp_path, script=SCRIPT.replace(old, new, 1))
    assert rule in ids(long_rules.check(vd)), long_rules.check(vd)


def test_payoff_before_story_is_caught(tmp_path):
    s = SCRIPT.replace("Я сидел над письмом и не мог открыть его до вечера. Мозг ждёт награду, а дело её прячет.",
                       "Мозг ждёт награду, а дело её прячет. Я сидел над письмом и не мог открыть его до вечера.")
    vd = make(tmp_path, script=s)
    assert any("раньше истории" in e for e in long_rules.check(vd))


@pytest.mark.parametrize("edit,rule", [
    (lambda p: p.update(questions=["a", "b"]), "Q1"),
    (lambda p: p.update(climax="одна две три четыре пять шесть семь восемь девять десять одиннадцать"), "Q2"),
    (lambda p: p.update(skeleton=["a", "b"]), "Q4"),
    (lambda p: p.update(hook_candidates=["a"] * 3), "H4"),
    (lambda p: p.update(hook_voiced=["a"]), "H4"),
    (lambda p: [x.update(emotion="тревога") for x in p["points"]], "P5"),
    (lambda p: p["revision"].update(words_before=p["revision"]["words_after"]), "R1"),
    (lambda p: p["approved"].update(script=False), "A1"),
])
def test_passport_rules_are_caught(tmp_path, edit, rule):
    vd = make(tmp_path, edit=edit)
    assert rule in ids(long_rules.check(vd))


def test_final_checks_only_at_the_end(tmp_path):
    vd = make(tmp_path, edit=lambda p: p.update(final_checks={}))
    assert long_rules.check(vd) == []
    assert {"F1", "F2", "F3", "F4"} <= ids(long_rules.check(vd, final=True))


def test_long_video_detected_without_passport(tmp_path):
    (tmp_path / "script.txt").write_text(SCRIPT, encoding="utf-8")
    assert long_rules.is_long(str(tmp_path))
    errs = long_rules.check(str(tmp_path))
    assert errs and "--template" in errs[0]
    short = tmp_path / "short"
    short.mkdir()
    (short / "script.txt").write_text("=== HOOK ===\nКороткая проба на тридцать слов.", encoding="utf-8")
    assert not long_rules.is_long(str(short))           # эпизоды-пробы 01/02 не задеты


def test_make_video_stops_before_paid_steps_without_structure(tmp_path):
    import subprocess
    (tmp_path / "script.txt").write_text(SCRIPT, encoding="utf-8")
    r = subprocess.run([sys.executable, os.path.join(HERE, "..", "scripts", "make_video.py"), str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode != 0
    assert "Структура длинного ролика" in r.stdout + r.stderr
    assert "План кадров" not in r.stdout                  # до планировщика (модель) дело не дошло


# ── Хук длинного ролика как у нынешних рилсов (владелец 04.11) ────────────────────────────────────────────────────
HOOK_SCENE_HIT = "import anim\nclass Scene:\n    def cam(self, t):\n        return anim.hook_cam(t, hit=0.4)\n"
HOOK_SCENE_OLD = "import anim\nclass Scene:\n    def cam(self, t):\n        return anim.hook_cam(t)\n"


HOOK_LINE = "Ты не досмотришь это видео, и палец уже тянется листать дальше."
REEL_SHOTS = [{"win": [800, 500, 1500], "why": "весь кот с телефоном"},
              {"at": "это", "win": [700, 450, 900], "punch": True, "why": "«это видео» — удар-наезд на экран"},
              {"at": "палец", "win": [900, 520, 800], "shake": 8, "spot": [900, 520, 300], "why": "«палец уже тянется» — палец крупно"},
              {"at": "листать", "win": [800, 500, 1200], "whip": "left", "why": "«листать дальше» — хлёст как свайп"}]


def _on_word(events):
    """Звуки тестов — на слово (секунды от начала фразы запрещены с 04.11): первое слово фразы + сдвиг."""
    out = []
    for e in events:
        if "word" not in e:
            e = dict(e)
            e["word"], e["offset"] = ("Ты" if e["phrase"] <= 9 else "Знаешь"), e.pop("at", 0.0)
        out.append(e)
    return out


def hooked(tmp_path, scene=HOOK_SCENE_HIT, sfx=None, labels=True, name="L09_test", edit=True, shots=None):
    """Длинный ролик с видеохуком из 9 фраз (~45 с), смонтированным как рилс."""
    vd = tmp_path / name
    vd.mkdir()
    hook = " [pause] ".join([HOOK_LINE] * 9)
    script = SCRIPT.replace(SCRIPT[SCRIPT.index("=== HOOK ===") + 13:SCRIPT.index("=== BLOCK 1")], hook + "\n\n")
    (vd / "script.txt").write_text(script, encoding="utf-8")
    frames = [["1", {"lib": "x.png", "anim": "hook", "key": "мысль"}]] + [
        [str(i), {"lib": "x.png", "key": "мысль"} if labels else {"lib": "x.png"}] for i in range(2, 13)]
    (vd / "storyboard.json").write_text(json.dumps({"frames": frames}, ensure_ascii=False), encoding="utf-8")
    if scene is not None:
        (vd / "anim").mkdir()
        (vd / "anim" / "hook.py").write_text(scene, encoding="utf-8")
    names = ["level_up", "typing", "shock", "oof", "riser", "fast_glitch"]   # звуки смысла: свист — только на движении
    if sfx is None:                          # плотно: ~каждые 1,3 с, шесть разных
        sfx = [{"name": names[k % 6], "phrase": 1 + k // 4, "at": 1.3 * (k % 4), "why": "тест"} for k in range(36)]
        sfx += [{"name": names[k % 6], "phrase": 10, "at": 4.0 * k, "why": "тест"} for k in range(81)]    # 2,5 на 10 с
    (vd / "sfx.json").write_text(json.dumps(_on_word(sfx), ensure_ascii=False), encoding="utf-8")
    if edit:
        ed = {str(i): {"shots": shots or REEL_SHOTS} for i in range(1, 11)}
        (vd / "edit.json").write_text(json.dumps({"frames": ed}, ensure_ascii=False), encoding="utf-8")
    return str(vd)


def test_long_hook_like_reels_passes_when_dense_and_hit(tmp_path):
    errs = long_rules.hook_build(hooked(tmp_path))
    assert [e for e in errs if not e.startswith("MANUAL")] == []      # минуты после хука — test_first_three_minutes_*


def test_long_hook_without_storyboard_is_not_checked_yet(tmp_path):
    assert long_rules.hook_build(make(tmp_path)) == []


@pytest.mark.parametrize("scene, part", [(None, "сцены anim/hook.py ещё нет"), (HOOK_SCENE_OLD, "hook_cam(t, hit=")])
def test_long_hook_needs_scene_with_hit_fly_in(tmp_path, scene, part):
    errs = long_rules.hook_build(hooked(tmp_path, scene=scene))
    assert any(e.startswith("HOOK-MOTION") and part in e for e in errs), errs


def test_long_hook_with_few_sounds_like_l02_is_caught(tmp_path):
    sparse = [{"name": "fast_whoosh", "phrase": 1, "at": 0.0, "why": "т"}, {"name": "riser", "phrase": 2, "at": 0, "why": "т"}]
    errs = long_rules.hook_build(hooked(tmp_path, sfx=sparse))
    assert any("на 10 с" in e for e in errs) and any("разных звуков" in e for e in errs) and any("тишина" in e for e in errs)


def test_built_long_videos_are_legacy_and_not_rechecked(tmp_path):
    assert long_rules.hook_build(hooked(tmp_path, scene=HOOK_SCENE_OLD, sfx=[], labels=False, name="L02_otvlechenie")) == []


def test_long_assembly_applies_fly_in_motion_blur():
    """Сборщик длинного ролика кладёт размытие влёта cam['zoom_blur'] сцены, как reel.py (до 04.11 терял его)."""
    import inspect
    import frame_clip
    src = inspect.getsource(frame_clip.render)
    assert 'cam.get("zoom_blur"' in src and "zoom_blur(" in src
    import numpy as np
    import anim
    import reel
    img = np.zeros((90, 160, 3), np.uint8); img[:, ::8] = 255
    assert np.array_equal(reel.zoom_blur(img, 0.06), anim.zoom_blur(img, 0.06))


def test_video_hook_slideshow_without_manual_montage_is_caught(tmp_path):
    """Владелец 04.11: первые 40–60 с длинного — «видеохук», спроектированный как рилс, «не просто слайд-шоу»."""
    errs = long_rules.hook_build(hooked(tmp_path, edit=False))
    assert any("без ручного монтажа" in e for e in errs), errs


@pytest.mark.parametrize("shots, part", [
    ([{"win": [1, 1, 900], "why": "один план на всю картинку"}], "> 3.0"),
    ([{"win": [1, 1, 900], "why": "а"}, {"at": "листать", "win": [1, 1, 800], "why": "б"}], "первая склейка"),
    ([{"win": [1, 1, 900], "why": "а"}, {"at": "это", "win": [1, 1, 800], "why": "б"},
      {"at": "палец", "win": [1, 1, 700], "why": "в"}, {"at": "листать", "win": [1, 1, 600], "why": "г"}], "акцентов"),
    ([{"win": [1, 1, 900]}, {"at": "это", "win": [1, 1, 800], "punch": True, "why": "б"}], "нет why"),
])
def test_video_hook_montage_like_reel(tmp_path, shots, part):
    errs = long_rules.hook_build(hooked(tmp_path, shots=shots))
    assert any(e.startswith("VIDEO-HOOK") and part in e for e in errs), errs


def test_video_hook_needs_new_pictures_often(tmp_path):
    vd = hooked(tmp_path)
    sb = json.load(open(os.path.join(vd, "storyboard.json"), encoding="utf-8"))
    sb["frames"] = [sb["frames"][0]] + [[k, {"absorb": True}] for k, _ in sb["frames"][1:]]
    json.dump(sb, open(os.path.join(vd, "storyboard.json"), "w", encoding="utf-8"))
    errs = long_rules.hook_build(vd)
    assert any("картинок в видеохуке" in e for e in errs), errs


def test_labels_are_rare_not_on_every_phrase(tmp_path):
    """Владелец 04.11, вечер: «рисунков карандашом слишком много… даже там, где не надо» — надпись не на каждой фразе,
    а не чаще одной в 5 с в хуке и не больше 3 на минуту дальше."""
    vd = hooked(tmp_path, labels=False)
    assert not any(e.startswith("LABELS") for e in long_rules.hook_build(vd))     # без надписей — не ошибка
    dense = {"10": {"hand": [{"text": "x", "word": "ты", "to": [1, 1], "why": "т"}] * 3,
                    "bold": [{"text": "y", "word": "ты", "why": "т"}]}}
    _fx(tmp_path, dense)
    errs = long_rules.hook_build(vd)
    assert any(e.startswith("LABELS") and "за минуту" in e for e in errs), errs
    hook = {str(i): {"hand": [{"text": "x", "word": "ты", "to": [1, 1], "why": "т"}]} for i in range(1, 10)}
    hook.update({str(i): {"bold": [{"text": "y", "word": "ты", "why": "т"}]} for i in range(1, 10)})
    _fx(tmp_path, hook)
    assert any(e.startswith("LABELS") and "видеохуке" in e for e in long_rules.hook_build(vd))


def test_pencil_label_leaves_after_it_is_read():
    """Дописанная надпись карандашом стоит PENCIL_SHOW_SEC и уходит, а не висит до конца картинки."""
    import inspect
    import frame_clip
    assert 1.5 <= frame_clip.PENCIL_SHOW_SEC <= 3.0
    src = inspect.getsource(frame_clip.render) + inspect.getsource(frame_clip._writes)
    assert 'life=' in src and "PENCIL_FADE_SEC" in src


def test_orchestrated_pencil_labels_are_never_dropped_by_timer():
    import assemble_frames as af
    job = {"key": "до титров", "accent": "двадцать минут", "T0": 12.0}
    written = [(10.0, 3)]                                   # 2 с назад уже написано 3 слова
    assert af.labels_for(job, 10.0, written, 2, manual=True)[:2] == ("до титров", "двадцать минут")
    assert af.labels_for(job, 10.0, written, 2, manual=False)[:2] == (None, None)   # без раскадровки — прежний бюджет


def test_long_video_sounds_at_least_two_per_every_ten_seconds(tmp_path):
    """Владелец 05.11: «звуков 2–3 на каждые 10 с по смыслу» во всех длинных — по всему ролику, каждый кусок."""
    vd = hooked(tmp_path)
    assert not [e for e in long_rules.hook_build(vd) if e.startswith("SFX")]
    sfx = json.load(open(os.path.join(vd, "sfx.json"), encoding="utf-8"))
    json.dump(_on_word([e for e in sfx if e["phrase"] <= 9]), open(os.path.join(vd, "sfx.json"), "w", encoding="utf-8"))
    errs = [e for e in long_rules.hook_build(vd) if e.startswith("SFX")]      # хук плотный, а тело без звуков
    assert errs and any("меньше 2 на 10 с" in e for e in errs), errs


def test_long_video_sounds_float_two_to_three_not_more(tmp_path):
    """Владелец 05.11: «звуков 2–3 на каждые 10 с по смыслу» (04.11 вечером было 3–4: «слишком много звуков»)."""
    vd = hooked(tmp_path)
    sfx = json.load(open(os.path.join(vd, "sfx.json"), encoding="utf-8"))
    dense = [e for e in sfx if e["phrase"] <= 9] + [{"name": "swoosh", "phrase": 10, "at": 1.3 * k, "why": "т"}
                                                    for k in range(260)]
    json.dump(_on_word(dense), open(os.path.join(vd, "sfx.json"), "w", encoding="utf-8"))
    assert any("в среднем" in e for e in long_rules.hook_build(vd))          # 7,7 на 10 с — слишком часто
    gap = [e for e in sfx if e["phrase"] <= 9] + [{"name": "swoosh", "phrase": 10, "at": t, "why": "т"}
                                                  for t in [0.5, 3, 8.5, 9.5, 11.5, 15, 19.5, 19.9, 21, 24, 26, 29.5]]
    json.dump(_on_word(gap), open(os.path.join(vd, "sfx.json"), "w", encoding="utf-8"))
    assert any("тишина без звуков" in e and e.startswith("SFX") for e in long_rules.hook_build(vd))


def test_first_three_minutes_are_hand_edited(tmp_path):
    """Владелец 04.11: «ручной у тебя будет на 3 минуты… собственноручно… без шаблонности и автоматики»."""
    vd = hooked(tmp_path)
    errs = [e for e in long_rules.hook_build(vd) if e.startswith("MANUAL")]
    assert any("фразы 11" in e and "без ручного монтажа" in e for e in errs), errs      # блок 1 начинается на ~45 с
    ed = json.load(open(os.path.join(vd, "edit.json"), encoding="utf-8"))
    ed["frames"]["11"] = {"shots": [{"win": [1, 1, 900], "why": "один план на весь блок"}]}
    json.dump(ed, open(os.path.join(vd, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False)
    errs = [e for e in long_rules.hook_build(vd) if e.startswith("MANUAL")]
    assert any("вторым планом" in e for e in errs), errs


def test_manual_shots_never_cut_a_written_thought():
    """L03 04.11: после того как мысль дописана, ручной крупный план резал её до «тс», «только д…». Теперь каждый
    следующий план показывает надпись целиком или не задевает её вовсе."""
    import camera
    import long_edit
    SW, SH = 3000, 1688
    box = (2000, 300, 2600, 420)                       # дописанная мысль справа вверху
    segs = [dict(t0=0, t1=2, win=camera.window(1500, 844, 3000, SW, SH), win_to=camera.window(1500, 844, 2900, SW, SH)),
            dict(t0=2, t1=4, win=camera.window(2100, 500, 900, SW, SH), win_to=camera.window(2100, 500, 860, SW, SH)),
            dict(t0=4, t1=6, win=camera.window(1700, 900, 1400, SW, SH), win_to=camera.window(1700, 900, 1350, SW, SH))]
    long_edit.keep_text(segs, 1.0, box, SW, SH)
    for s in segs:
        for w in (s["win"], s["win_to"]):
            assert camera.inside(box, w) or camera.overlap_share(w, box) <= long_edit.TEXT_EDGE


def _fx(tmp_path, phrases, name="L09_test"):
    (tmp_path / name / "fx.json").write_text(json.dumps({"phrases": phrases}, ensure_ascii=False), encoding="utf-8")


def test_bold_text_may_not_outnumber_handwriting(tmp_path):
    """Владелец 04.11 по L03: «90 % занимает жирный шрифт… хочу 60 % рисованный и только 40 % жирный»."""
    vd = hooked(tmp_path, labels=False)
    bold = {str(i): {"bold": [{"text": "строка", "word": "ты", "why": "т"}]} for i in range(1, 13)}
    _fx(tmp_path, bold)
    assert any(e.startswith("TEXT-SHARE") for e in long_rules.hook_build(vd))
    mixed = {str(i): ({"bold": [{"text": "строка", "word": "ты", "why": "т"}]} if i <= 2 else
                      {"hand": [{"text": "палец", "word": "ты", "to": [100, 100], "why": "т"}]}) for i in (1, 2, 4, 6, 8, 10)}
    _fx(tmp_path, mixed)
    errs = long_rules.hook_build(vd)
    assert not any(e.startswith("TEXT-SHARE") for e in errs)
    assert not any(e.startswith("LABELS") for e in errs), errs      # надписей мало — и это не ошибка


def test_share_counts_pencil_thoughts_as_handwriting(tmp_path):
    vd = hooked(tmp_path)                                           # 12 карандашных мыслей раскадровки
    _fx(tmp_path, {str(i): {"bold": [{"text": "строка", "word": "ты", "why": "т"}]} for i in range(1, 8)})
    assert not any(e.startswith("TEXT-SHARE") for e in long_rules.hook_build(vd))


def test_hand_label_needs_target_and_reason(tmp_path):
    import long_fx
    vd = hooked(tmp_path)
    _fx(tmp_path, {"2": {"hand": [{"text": "палец", "word": "ты", "why": "т"}]}})
    with pytest.raises(ValueError):
        long_fx.load(vd)
    _fx(tmp_path, {"2": {"hand": [{"text": "палец", "word": "ты", "to": "subject", "why": "т"}]}})
    assert long_fx.load(vd)[1]["hand"][0]["to"] == "subject"


def test_hand_label_is_written_on_its_word():
    import long_fx
    words = [{"word": "Палец", "start": 0.4, "end": 0.7}, {"word": "тянется", "start": 0.8, "end": 1.2},
             {"word": "палец", "start": 2.0, "end": 2.3}]
    spec = {"hand": [{"text": "палец", "word": "палец", "nth": 2, "to": [1, 1], "why": "т"},
                     {"text": "поздно", "word": "палец", "to": [1, 1], "why": "т"}]}
    ev = long_fx.hand_events(spec, 0.0, 3.0, words)
    assert [round(e["t"], 2) for e in ev] == [1.95, 0.35]
    assert [e["t"] for e in long_fx.hand_events(spec, 0.0, 2.4, words)] == [0.35]   # вторая не успевает — не ставится


def test_bold_line_stays_on_top_and_bigger():
    """Жирный — только поясняющая строка сверху (как у Дани) и на 25 % крупнее (владелец 04.11)."""
    import numpy as np
    import long_fx
    assert long_fx.SIZE_PLAIN >= 170 and long_fx.STROKE >= 6 and long_fx.STROKE_ALPHA == 1.0   # 04.11: крупнее, обводка гуще
    f = np.full((long_fx.H, long_fx.W, 3), 245, np.float32)
    f[int(long_fx.H*0.2):, :] = 20                                  # чистая бумага только сверху — строка там
    f[:, :300] = 20
    cx, cy, sz, _ = long_fx.free_spot(f, "ДЕНЬ БЫЛ ТЯЖЁЛЫЙ", long_fx.SIZE_PLAIN, prefer=(960, 600),
                                      top_band=long_fx.BOLD_TOP_BAND)
    assert cy <= long_fx.H*long_fx.BOLD_TOP_BAND
    g = np.full((long_fx.H, long_fx.W, 3), 245, np.float32)
    cx, cy, sz, _ = long_fx.free_spot(g, "ЛУЧШЕ ЗАВТРА", long_fx.SIZE_PLAIN, prefer=(960, 900),
                                      top_band=long_fx.BOLD_TOP_BAND)
    assert cy <= long_fx.H*long_fx.BOLD_TOP_BAND and sz >= 0.85*long_fx.SIZE_PLAIN   # пусто везде — всё равно сверху


def test_hand_label_has_pen_drawn_arrow_to_the_object():
    """Подпись к предмету пишется карандашом и стрелка к нему — тем же пером, со своими штрихами (как схема эп.01)."""
    import numpy as np
    import writeon
    a = writeon.arrow_letter((300, 300), (700, 520), 0.18, 96, 1920, 1080)
    ev, T = writeon.plan([a], 24)
    assert len(ev) == 3 and T > 0.1                                 # древко и два уса наконечника
    ys, xs = np.nonzero(a["soft"] > 0.5)
    assert xs.min() < 320 and xs.max() > 680                        # от надписи до предмета
    tip = ev[0]["path"][-1]
    assert abs(tip[1] - 700) < 2 and abs(tip[0] - 520) < 2          # кончик — у предмета (path в (y, x))


def test_hand_label_sits_on_paper_next_to_object_and_skips_object_out_of_frame():
    import numpy as np
    import frame_clip
    SW, SH = 960, 540
    img = np.full((SH, SW, 3), 245, np.uint8)
    img[220:320, 420:540] = 20                                      # предмет посередине
    fr = dict(final_rgb=img, SW=SW, SH=SH, off=(0, 0), objects=[])
    box = frame_clip.hand_target(fr, [480, 270])
    res = frame_clip.hand_layout(fr, "палец", box, (0, 0, SW, SH))
    assert res is not None
    letters, (cx, cy), size, arr = res
    assert letters[-1]["ch"] == "→" and arr is not None             # стрелка тем же пером — последней «буквой»
    sx, sy = cx*SW/1920, cy*SH/1080
    assert not (420 <= sx <= 540 and 220 <= sy <= 320)              # подпись не на предмете
    assert frame_clip.hand_layout(fr, "палец", box, (600, 0, 960, 202)) is None   # предмета нет в кадре


def test_narrator_not_in_first_10s_and_every_1_5_to_3_minutes():
    """Владелец 04.11: кот-ведущий «не в первые 10 секунд видео, не чаще одного раза в 1,5–2 минуты и не реже раза
    в 3 минуты»."""
    starts = [0.0, 5.0, 40.0, 100.0, 150.0, 250.0, 300.0, 400.0, 450.0]
    ends = starts[1:] + [560.0]
    nar = {"why": "т"}
    b = [{"text": "строка", "word": "ты", "why": "т"}]
    ok = {"3": {"narrator": nar, "bold": b}, "5": {"narrator": nar, "bold": b}, "7": {"narrator": nar, "bold": b},
          "9": {"narrator": nar, "bold": b}}
    assert long_rules.narrator_rhythm(ok, starts, ends) == []        # 40, 150, 300, 450 с; конец 560
    assert any("без жирной строки" in e for e in long_rules.narrator_rhythm(dict(ok, **{"3": {"narrator": nar}}),
                                                                             starts, ends))   # ведущий всегда с жирным
    early = dict(ok, **{"2": {"narrator": nar, "bold": b}})
    assert any("первые 10 с" in e for e in long_rules.narrator_rhythm(early, starts, ends))
    often = dict(ok, **{"4": {"narrator": nar, "bold": b}})                       # 100 с — через 60 с после 40
    assert any("чаще раза" in e for e in long_rules.narrator_rhythm(often, starts, ends))
    rare = {"3": {"narrator": nar, "bold": b}, "8": {"narrator": nar, "bold": b}}            # 40 → 400: 360 с без ведущего
    assert any("реже раза" in e for e in long_rules.narrator_rhythm(rare, starts, ends))


def test_sound_without_word_or_announcing_a_cut_is_rejected(tmp_path):
    """Владелец 04.11: «максимальная точность звуков… никогда не промахивались». Секунды от начала фразы промахивались
    (L03: три свиста на 0,5–0,9 с мимо склейки); звук склейки ставится у плана монтажа и встаёт ровно на склейку."""
    vd = hooked(tmp_path)
    sfx = json.load(open(os.path.join(vd, "sfx.json"), encoding="utf-8"))
    bad = sfx + [{"name": "swoosh", "phrase": 2, "at": 0.4, "why": "т"},
                 {"name": "swoosh", "phrase": 3, "word": "Ты", "why": "склейка на экран"}]
    json.dump(bad, open(os.path.join(vd, "sfx.json"), "w", encoding="utf-8"))
    errs = [e for e in long_rules.hook_build(vd) if e.startswith("SFX")]
    assert any("без слова" in e for e in errs) and any("у плана монтажа" in e for e in errs), errs


def test_cut_sound_from_montage_counts_and_lands_on_the_cut(tmp_path):
    vd = hooked(tmp_path, shots=[dict(REEL_SHOTS[0], sound="swoosh")] + REEL_SHOTS[1:])
    ts = long_rules.edit_sounds(vd, *_ctx(vd))
    assert ts and all(name == "swoosh" for _, _, name in ts)
    import long_sfx
    ev, errs = long_sfx.resolve([{"name": "swoosh", "phrase": 1, "at": 0.3, "why": "т"}], [0.0], [[]])
    assert not ev and "без слова" in errs[0]


def test_sound_on_word_takes_the_same_occurrence_as_the_cut():
    import long_sfx
    words = [[{"word": "я", "start": 0.2, "end": 0.3}, {"word": "сидел", "start": 0.4, "end": 0.8},
              {"word": "я", "start": 1.5, "end": 1.6}]]
    ev, errs = long_sfx.resolve([{"name": "swoosh", "phrase": 1, "word": ["я", 2], "why": "т"}], [0.0], words)
    assert not errs and abs(ev[0]["t"] - 1.5) < 1e-9


def test_rule_check_finds_the_word_where_the_assembler_cuts():
    """Проверка правил искала слово по началу («Вот» находило «вот-вот» раньше), сборщик — точное совпадение первым:
    L02 05.11 получил ложный план 4,4 с, которого в сборке нет. Правило одно — words.occurrences."""
    import long_edit
    ws = [{"word": "вот-вот", "start": 1.0}, {"word": "закипит.", "start": 1.5}, {"word": "Вот", "start": 4.0}]
    blocks = [{"text": "вот-вот закипит. Вот"}]
    t_rule = long_rules._word_t(blocks, [0.0], [5.0], [0], "Вот", [ws])
    assert t_rule == long_edit.word_time("Вот", ws) == 4.0


def test_plan_reason_must_say_why_not_just_wide_shot(tmp_path):
    vd = hooked(tmp_path, shots=[dict(REEL_SHOTS[0], why="общий план")] + REEL_SHOTS[1:])
    assert any(e.startswith("EDIT-WHY") for e in long_rules.hook_build(vd))


def _ctx(vd):
    import script_parser
    blocks = script_parser.parse_blocks(os.path.join(vd, "script.txt"))
    starts, ends = long_rules._phrase_times(vd, blocks)
    frames = dict(json.load(open(os.path.join(vd, "storyboard.json"), encoding="utf-8"))["frames"])
    return blocks, frames, starts, ends


def test_whoosh_must_sit_on_motion_not_in_the_air(tmp_path):
    """Свист — звук движения (04.11, L03: свист «третий приём» остался на «прыжков», где ничего не появляется; свист
    «строка влетает» звучал на 1,5 с раньше строки). На склейке — можно, в пустоту — ошибка, у надписи — у надписи."""
    vd = hooked(tmp_path)
    ok = long_rules.hook_build(vd)
    assert not any("свист" in e for e in ok), ok
    sfx = json.load(open(os.path.join(vd, "sfx.json"), encoding="utf-8"))
    air = sfx + [{"name": "fast_whoosh", "phrase": 2, "word": "дальше", "why": "просто так"},       # «листать» — склейка,
                 {"name": "swoosh", "phrase": 2, "word": "листать", "why": "хлёст как свайп"},     # «дальше» — пусто
                 {"name": "fast_whoosh", "phrase": 3, "word": "палец", "why": "«палец» на экране"}]
    json.dump(air, open(os.path.join(vd, "sfx.json"), "w", encoding="utf-8"), ensure_ascii=False)
    errs = long_rules.hook_build(vd)
    assert any("свист «fast_whoosh» во фразе 2 на «дальше»" in e for e in errs), errs
    assert not any("на «листать»" in e for e in errs)
    assert any("у самой надписи" in e and "фразе 3" in e for e in errs)


def test_whoosh_on_handwriting_is_rejected_and_text_sounds_count(tmp_path):
    vd = hooked(tmp_path)
    fx = {"phrases": {"10": {"hand": [{"text": "×4", "word": "Знаешь", "to": [10, 10], "why": "число",
                                       "sound": "fast_whoosh"}],
                             "bold": [{"text": "суть", "word": "Знаешь", "why": "вывод", "sound": "level_up"}]}}}
    json.dump(fx, open(os.path.join(vd, "fx.json"), "w", encoding="utf-8"), ensure_ascii=False)
    errs = long_rules.hook_build(vd)
    assert any("рукописной подписи" in e for e in errs)
    blocks, frames, starts, ends = _ctx(vd)
    assert sorted(n for _, _, n in long_rules.text_sounds(vd, blocks, starts, ends)) == ["hand:fast_whoosh", "level_up"]
