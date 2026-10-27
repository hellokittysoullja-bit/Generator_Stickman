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
