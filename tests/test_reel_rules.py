"""Стражи рилса (22.10): новый агент с нуля не должен сделать рилс хуже эп.02.

Правила — в scripts/reel_rules.py, reel.py не рендерит рилс, который их нарушает. Здесь проверено, что каждое правило
ловит своё нарушение, что одобренный рилс эп.02 проходит, и что одобренные владельцем значения стоят по умолчанию."""
import copy
import json
import os

import reel
import reel_rules

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP02 = os.path.join(ROOT, "videos", "02_sdvg_vremya", "reel", "reel.json")
SFX = set(reel.SFX)


def spec():
    return json.load(open(EP02, encoding="utf8"))


def broken(fn):
    s = spec(); fn(s); return reel_rules.check_spec(s, SFX)


def test_approved_ep02_reel_passes():
    assert reel_rules.check_spec(spec(), SFX) == []


def test_only_owner_sounds_and_no_music():
    assert {"riser", "swoosh", "swoosh_deep", "oof"} <= set(reel.SFX)
    for name, v in reel.SFX_LIB.items():          # у каждого звука библиотеки — файл и описание «что значит, когда ставить»
        assert os.path.exists(os.path.join(reel.SFX_DIR, v["file"])), name
        for key in ("sound", "meaning", "use", "avoid", "peak_sec", "level_db"):
            assert v.get(key) not in (None, ""), (name, key)
    assert broken(lambda s: s["beats"][3].setdefault("fx", []).append({"kind": "sfx", "name": "tick"}))
    assert broken(lambda s: s.__setitem__("music", "track.mp3"))


def test_hook_rules():
    assert broken(lambda s: s["beats"][0].__setitem__("text", "Ты, скорее всего, вовсе не ленишься, а просто устал."))
    assert broken(lambda s: s["beats"][0].__setitem__("fx", []))                                  # нет riser
    assert broken(lambda s: s["beats"][0]["fx"][0].__setitem__("dt", 0.6))                       # riser поздно
    assert broken(lambda s: s["beats"][0]["fx"][0].__setitem__("after", True))                   # «после хука» — старое
    assert broken(lambda s: s["beats"][1].pop("after_sfx"))                                      # раскрытие не на пике


def test_layout_and_loop():
    assert broken(lambda s: s.__setitem__("picture_h", 1100))
    assert broken(lambda s: s["beats"][-1]["shots"][0].__setitem__("src", "f4"))


def test_timeline_rules():
    peaks = {k: v[1] for k, v in reel.SFX.items()}
    ok = [dict(t0=0.0, t1=1.65), dict(t0=1.65, t1=4.0), dict(t0=4.0, t1=6.5)]
    riser = [dict(kind="sfx", name="riser", align="start", t=0.0)]
    assert reel_rules.check_timeline(ok, riser, peaks) == []
    assert reel_rules.check_timeline([dict(t0=0.0, t1=1.65), dict(t0=1.65, t1=5.2)], riser, peaks)   # план 3.55 с
    assert reel_rules.check_timeline([dict(t0=0.0, t1=2.6), dict(t0=2.6, t1=4.0)], [], peaks)          # склейка поздно
    assert reel_rules.check_timeline(ok, [dict(riser[0], t=0.5)], peaks)                               # пик мимо склейки


def test_approved_values_are_defaults():
    s = {"beats": [{"text": "a", "shots": [{"src": "f1", "from": [0, 0, 100]}]}]}
    reel.layout(copy.deepcopy(s))
    assert reel.PH == 1380 and reel.CAP_CY == 1455
    s2 = copy.deepcopy(s); reel.layout(s2)
    assert abs(s2["beats"][0]["shots"][0]["from"][2] - 111.0) < 1e-6          # view_scale 1.11 по умолчанию
    reel.layout({"beats": [], "picture_h": 1100})                              # вернуть модуль как был


def test_segment_cache_key_sees_only_what_the_shot_shows():
    shots = [dict(t0=0.0, t1=2.0, src="f1", **{"from": [1, 1, 100]}), dict(t0=2.0, t1=4.0, src="f1", **{"from": [2, 2, 100]}),
             dict(t0=4.0, t1=12.0, src="f1", **{"from": [3, 3, 100]}), dict(t0=12.0, t1=14.0, src="f1", **{"from": [4, 4, 100]})]
    ev = [dict(kind="punch", t=1.0, amt=0.1), dict(kind="punch", t=13.0, amt=0.1)]
    def key(e):
        return reel.segment_key("/nonexistent", 30, 0, 60, 0, shots, e, [], [], [], None, 14.0, "v")
    base = key(ev)
    assert key([dict(ev[0], amt=0.2), ev[1]]) != base          # своё событие поменялось — план перерисуется
    assert key([ev[0], dict(ev[1], amt=0.2)]) == base          # событие через 12 с — план из кэша
    assert key([dict(ev[0], _anchor={1: 2}), ev[1]]) == base   # служебное поле рендера ключ не меняет


def test_draft_parses_script_and_windows_do_not_cut_drawing(tmp_path):
    import numpy as np
    import reel_draft
    p = tmp_path / "reel_script.txt"
    p.write_text("Ты не *ленишься*.  @f1\nТы не видишь *время*.  @f2\nА дело не начато.\n", encoding="utf8")
    beats = reel_draft.parse(str(p))
    assert [b["src"] for b in beats] == ["f1", "f2", "f2"] and beats[0]["text"] == "Ты не *ленишься*."
    img = np.full((1696, 2528, 3), 250, np.uint8)            # два «предмета» на бумаге, как в кадре эпизода (src ×2)
    img[500:1300, 300:900] = 20; img[400:1200, 1700:2300] = 20
    views = reel_draft.ink_views(img)
    assert len(views) >= 2
    for cx, _cy, h in views[1:]:                              # окна по предметам: край окна не идёт по туши
        k = reel_draft.reel.W / reel_draft.reel.PH * 1.11
        w = h * k
        for x in (cx - w / 2, cx + w / 2):
            xs = int(x * 2)
            if 0 <= xs < img.shape[1]:
                assert (img[:, max(0, xs - 2):xs + 3] < 200).mean() < 0.05


def test_accent_not_on_function_word():
    def put_punch_on_pri(s):
        b = next(b for b in s["beats"] if b["text"].startswith("Так часто"))
        b["fx"] = [{"kind": "punch", "at": 3, "amt": 0.12}]          # «при» — эталон v11 стоял ровно так
    assert broken(put_punch_on_pri)


def test_caption_rules_on_timeline():
    peaks = {k: v[1] for k, v in reel.SFX.items()}
    shots = [dict(t0=0.0, t1=1.65), dict(t0=1.65, t1=4.0), dict(t0=4.0, t1=6.0)]
    riser = [dict(kind="sfx", name="riser", align="start", t=0.0)]
    good = [dict(t0=0.0, t1=1.65, text="Ты не ленишься"), dict(t0=1.65, t1=4.0, text="Ты не видишь время совсем никогда"),
            dict(t0=4.0, t1=5.0, text="Настоящих")]
    assert reel_rules.check_timeline(shots, riser, peaks, good, total=5.0) == []
    long_hook = [dict(good[0], text="Ты вовсе не ленишься, ты просто устал")] + good[1:]
    assert reel_rules.check_timeline(shots, riser, peaks, long_hook, total=5.0)     # хук не дочитан до склейки
    across = good[:1] + [dict(t0=1.65, t1=4.6, text="при СДВГ")] + [dict(good[2], t0=4.6)]
    assert reel_rules.check_timeline(shots, riser, peaks, across, total=5.6)        # субтитр через склейку 4.0
    assert reel_rules.check_timeline(shots, riser, peaks, good, total=4.5)          # «Настоящих» 0.5 с — не дочитать


def test_passport_blocks_template_reels():
    log = json.load(open(os.path.join(ROOT, "docs", "reels_log.json"), encoding="utf8"))
    ep02 = spec()
    assert reel_rules.check_passport(ep02, log, "videos/02_sdvg_vremya/reel") == []       # сам себе не шаблон
    new = copy.deepcopy(ep02)
    assert reel_rules.check_passport(new, log, "videos/03_new/reel")                      # тот же хук и приёмы
    new["passport"]["hook_type"] = "вопрос"
    new["beats"][0]["text"] = "Сколько раз за день ты говоришь «потом»?"
    new["passport"]["devices"] = ["раскадровка дня", "счётчик", "хлёст", "пауза", "кукла машет", "эхо в призыве"]
    assert reel_rules.check_passport(new, log, "videos/03_new/reel") == []                # другой хук, другие приёмы
    del new["passport"]
    assert reel_rules.check_passport(new, log, "videos/03_new/reel")                      # без паспорта нельзя


def test_stop_words_and_accent_shift():                       # план 04 п.1.3, п.1.24
    assert broken(lambda s: s["beats"][14].__setitem__("text", "«Напарник» вылечит прокрастинацию навсегда."))
    assert broken(lambda s: s["beats"][2].__setitem__("text", "Шок: так бывает при *СДВГ*. И без диагноза тоже."))
    def shift(s):                                              # наезд на соседнее с ключевым слово
        b = next(b for b in s["beats"] if b["text"].startswith("Интересное"))
        b["fx"][0]["at"] = 3
    assert broken(shift)
    def mixed_whips(s):
        s["beats"][6]["shots"][1]["whip"] = [560, 0]
    assert broken(mixed_whips)


def test_passport_needs_goal():                                # план 04 п.1.29
    log = json.load(open(os.path.join(ROOT, "docs", "reels_log.json"), encoding="utf8"))
    s = spec(); del s["passport"]["goal"]
    assert reel_rules.check_passport(s, log, "videos/02_sdvg_vremya/reel")


def test_overlays_in_safe_zone_and_cta_before_end():           # план 04 п.1.25, п.1.1
    assert reel_rules.check_overlays([(14, "Напарник", 207, 280, 885, 430)]) == []
    assert reel_rules.check_overlays([(14, "Напарник", 207, 202, 885, 376)])        # v12 до 23.10: под шапкой Reels
    assert reel_rules.check_overlays([(15, "бесплатно", 600, 900, 950, 1000)])      # под колонкой кнопок
    s = spec()
    assert reel_rules.check_cta(s, [0.0] * 15 + [36.7, 41.1], 43.4) == []
    assert reel_rules.check_cta(s, [0.0] * 15 + [39.5, 41.1], 43.4)                 # призыв за 3.9 с до конца
    s["passport"].pop("cta_beat")
    assert reel_rules.check_cta(s, [0.0] * 17, 43.4)


def test_timeline_min_shot_and_src_changes():                  # план 04 п.1.24
    peaks = {k: v[1] for k, v in reel.SFX.items()}
    riser = [dict(kind="sfx", name="riser", align="start", t=0.0)]
    short = [dict(t0=0.0, t1=1.65, src="a"), dict(t0=1.65, t1=2.1, src="b"), dict(t0=2.1, t1=4.0, src="a")]
    assert reel_rules.check_timeline(short, riser, peaks)                           # план 0.45 с
    many = [dict(t0=0.0, t1=1.65, src="a")] + [dict(t0=1.65 + i * 1.5, t1=3.15 + i * 1.5, src="ab"[i % 2]) for i in range(12)]
    assert any("смен рисунка" in e for e in reel_rules.check_timeline(many, riser, peaks))


def test_overlay_box_follows_paper_zoom():
    ev = [dict(kind="write", text="?", x=540, y=300, size=200, t=0.0, dur=0.3, beat=0)]
    still = [dict(t0=0.0, t1=2.0, src="f", **{"from": [500, 500, 600]})]
    zoom = [dict(t0=0.0, t1=2.0, src="f", **{"from": [500, 500, 600], "to": [500, 500, 400]})]
    reel.layout({"beats": [], "picture_h": 1380})
    b0 = reel.overlay_boxes(ev, still)[0]; b1 = reel.overlay_boxes(ev, zoom)[0]
    assert b1[3] < b0[3] and b1[4] - b1[2] > b0[4] - b0[2]       # наезд уносит надпись вверх и растит её


def test_close_punches_warn():                                 # план 04 п.1.5 (гипотеза — предупреждение)
    ev = [dict(kind="punch", t=18.0), dict(kind="punch", t=19.6)]
    assert reel_rules.warnings({"beats": []}, [], 40.0, ev)
    assert not reel_rules.warnings({"beats": []}, [], 40.0, [ev[0], dict(kind="punch", t=23.0)])


def test_thirty_degree_rule():                                  # план 04 п.1.9
    peaks = {k: v[1] for k, v in reel.SFX.items()}
    riser = [dict(kind="sfx", name="riser", align="start", t=0.0)]
    a = dict(t0=0.0, t1=1.65, src="f4", **{"from": [1031, 440, 738], "to": [1031, 440, 700]})
    b = dict(t0=1.65, t1=3.0, src="f4", **{"from": [1031, 440, 560]})
    assert any("почти одинаковы" in e for e in reel_rules.check_timeline([a, b], riser, peaks))
    assert not any("почти одинаковы" in e for e in reel_rules.check_timeline([a, dict(b, jump=True)], riser, peaks))
    assert not any("почти одинаковы" in e for e in reel_rules.check_timeline([a, dict(b, **{"from": [1031, 440, 480]})], riser, peaks))


def test_sound_limits_and_one_motion():                         # план 04 п.1.11, 1.13
    def p(name, t, **k):
        return dict(name=name, t=t, peak=t, **k)
    assert reel_rules.check_sounds([p("riser", 1.65), p("swoosh_deep", 12.0), p("oof", 25.0), p("swoosh", 40.0)]) == []
    assert reel_rules.check_sounds([p("oof", 10.0), p("oof", 20.0), p("oof", 30.0)])             # провал трижды
    assert reel_rules.check_sounds([p("swoosh_deep", 10.0), p("swoosh_deep", 12.5)])              # повтор через 2.5 с
    assert reel_rules.check_sounds([p("swoosh", 10.0, whip=True), p("swoosh", 11.0)]) == []       # хлёст — можно
    assert reel_rules.sound_warnings([p("swoosh", 5.0), p("oof", 5.2), p("riser", 5.4)])
    shots = [dict(t0=0.0, t1=2.0), dict(t0=2.0, t1=4.0, kind="doll", actions=[dict(t=0.1, do="tilt")])]
    assert reel_rules.warnings({"beats": []}, shots, 10.0, [dict(kind="punch", t=2.05)])
    assert not reel_rules.warnings({"beats": []}, shots, 10.0, [dict(kind="punch", t=1.8)])


def test_sound_plan_matches_mixer_order():
    shots = [dict(t0=0.0), dict(t0=2.0, whip=[-560, 0]), dict(t0=5.0, zoom_in=0.3), dict(t0=9.0, sound="swoosh_deep")]
    plan = reel.sound_plan(shots, [dict(kind="sfx", name="riser", t=0.0, align="start"), dict(kind="punch", t=12.5)])
    assert [x["name"] for x in plan] == ["swoosh", "swoosh_deep", "riser", "swoosh", "swoosh"]
    assert plan[0]["whip"] and plan[0]["pan"] == 0.3 and plan[3]["soft"] and plan[3]["gain_db"] == -7.0


def test_writing_budget_and_arc():                              # план 04 п.1.15, 1.23
    shots = [dict(t0=0.0, t1=1.65), dict(t0=1.65, t1=4.0)]
    assert reel_rules.check_writing([dict(kind="write", text="?", t=0.5)], shots)
    assert not reel_rules.check_writing([dict(kind="write", text="?", t=2.0)], shots)
    many = [dict(kind="mark", text="бесплатно", t=10.0), dict(kind="write", text="без карты и регистрации", t=10.4)]
    assert len(reel_rules.warnings({"beats": []}, [], 40.0, many)) == 2
    two_r = {"beats": [dict(text="a", arc="t", charge="+"), dict(text="b", arc="r", charge="-"), dict(text="c", arc="r", charge="+")]}
    assert any("разрядки" in w for w in reel_rules.warnings(two_r, [], 40.0))
    ends_minus = {"beats": [dict(text="a", arc="t", charge="+"), dict(text="b", arc="r", charge="-")]}
    assert any("кончается" in w for w in reel_rules.warnings(ends_minus, [], 40.0))


def test_new_look_flags_draw_only_when_on():                    # план 04 п.1.20–1.22: по флагу, по умолчанию выключено
    import numpy as np
    a = np.full((400, 600, 3), 245, np.uint8); b = a.copy(); c = a.copy()
    reel.arrow(a, (500, 50), (100, 350), 1.0)
    reel.arrow(b, (500, 50), (100, 350), 1.0, dash_t=0.3, u_head=1.0)
    assert (a < 200).sum() > (b < 200).sum() > 0                 # пунктир — меньше туши, но стрелка есть
    reel.pen_tip(c, 300, 200, 200)
    assert (c < 120).sum() > 0 and not ((c[..., 0].astype(int) - c[..., 2].astype(int)) > 30).any()   # серый, не тёплый
