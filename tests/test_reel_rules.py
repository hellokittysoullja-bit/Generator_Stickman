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
    assert broken(lambda s: s["beats"][-1]["shots"][-1].__setitem__("src", "f4"))   # последний кадр ролика — не начало


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


def test_knowledge_checklist_blocks_reel_without_marketing():  # владелец 23.10: знания — в каждом рилсе, а не в справочнике
    s = spec()
    assert reel_rules.check_knowledge(s) == []                                   # эп.02 закрывает все пункты
    s2 = copy.deepcopy(s); del s2["passport"]["knowledge"]["honest_limit"]
    assert any("honest_limit" in e for e in reel_rules.check_knowledge(s2))     # пункт забыт — не рендерится
    s3 = copy.deepcopy(s); s3["passport"]["knowledge"]["value_before_ask"] = {"skip": "нет"}
    assert any("без причины" in e for e in reel_rules.check_knowledge(s3))      # отказ без причины не принимается
    s4 = copy.deepcopy(s); s4["passport"]["knowledge"]["value_before_ask"] = 16
    assert any("value_before_ask" in e for e in reel_rules.check_knowledge(s4)) # приём после призыва — не взаимность
    s5 = copy.deepcopy(s); s5["beats"][6]["text"] = "Соберись и сделай."
    assert any("стыдящее" in e for e in reel_rules.check_knowledge(s5))
    s6 = copy.deepcopy(s); s6["passport"]["caption"] = "Просто ролик #кот"
    assert len(reel_rules.check_knowledge(s6)) >= 2                              # нет ключевой фразы ниши, мало хэштегов
    s7 = copy.deepcopy(s); s7["passport"]["hook_variants"] = s7["passport"]["hook_variants"][:1]
    assert any("вариантов хука" in e for e in reel_rules.check_knowledge(s7))
    assert not any("ре-хук" in e for e in reel_rules.knowledge_timing(s, [0.0] * 9 + [21.0] + [0.0] * 7, 45.0))
    assert any("ре-хук" in e for e in reel_rules.knowledge_timing(s, [0.0] * 9 + [35.0] + [0.0] * 7, 45.0))  # 78 % — поздно


def test_draft_carries_knowledge_todo(tmp_path):
    import reel_draft
    p = tmp_path / "reel_script.txt"
    p.write_text("Ты не *ленишься*.  @f1\nТы не видишь *время*.  @f5\nНачни с пяти минут.  @f1\n", encoding="utf8")
    items = reel_rules.load_json(reel_rules.CHECKLIST_PATH, {"items": []})["items"]
    stub = {it["id"]: "TODO" for it in items if it["kind"] == "beat"}
    errs = reel_rules.check_knowledge({"beats": reel_draft.parse(str(p)), "passport": {"knowledge": stub}})
    assert sum("passport.knowledge" in e for e in errs) == len(stub)          # черновик не пройдёт, пока TODO


def test_publish_kit_and_variant(tmp_path):
    import shutil
    import reel_publish
    import reel_variant
    d = tmp_path / "reel"; d.mkdir()
    for f in ("reel.json", "reel_report.json"):
        shutil.copy(os.path.join(os.path.dirname(EP02), f), d / f)
    out = reel_publish.publish(str(d))
    txt = open(out, encoding="utf8").read()
    assert "utm_campaign=" in txt
    assert "Честный предел" in txt and "#сдвг" in txt
    v = reel_variant.make(os.path.dirname(EP02), "Это не лень. Это время.", name=str(tmp_path / "v1"))
    sv = json.load(open(os.path.join(v, "reel.json"), encoding="utf8"))
    assert sv["beats"][0]["text"] == "Это не лень. Это время." and sv["passport"]["variant_of"]
    assert reel_rules.check_spec(sv, SFX) == []


def test_geometry_catches_slivers_dolls_and_text_on_drawing(tmp_path):
    """reel_geom (23.10): то, что в v12–v14 находилось только глазами после рендера, ловится до рендера."""
    import numpy as np
    from PIL import Image
    import reel_geom
    d = tmp_path / "reel"; (d / "src").mkdir(parents=True)
    img = np.full((1600, 2400, 3), 245, np.uint8)
    img[200:1400, 100:900] = 30                         # большой «кот» слева (в координатах окна x 50–450)
    img[500:900, 1500:1900] = 30                        # «часы» справа (x 750–950)
    Image.fromarray(img).save(d / "src" / "geomtest_c.png")
    (d / "reel.json").write_text('{"sources": {}}', encoding="utf8")
    reel.layout({"beats": [], "picture_h": 1380})
    clean = [dict(t0=0.0, t1=2.0, src="geomtest", kind="crop", **{"from": [850, 350, 300]})]
    edge = [dict(t0=0.0, t1=2.0, src="geomtest", kind="crop", **{"from": [570, 350, 400]})]   # край окна задевает «кота»
    assert reel_geom.slivers(reel, str(d), clean) == []
    assert reel_geom.slivers(reel, str(d), edge)
    big = [dict(t0=0.0, t1=2.0, kind="doll", h=1000, cy=700, zoom=[1.0, 1.04])]
    ok = [dict(t0=0.0, t1=2.0, kind="doll", h=600, cx=515, cy=700, zoom=[1.0, 1.04])]
    assert reel_geom.doll_fit(reel, big, []) and reel_geom.doll_fit(reel, ok, []) == []
    on_cat = [dict(kind="write", text="Напарник", x=540, y=500, size=150, t=0.5, dur=0.5, beat=0, kind_of_shot="doll")]
    assert reel_geom.overlay_on_drawing(reel, str(d), ok, on_cat)
    on_paper = [dict(on_cat[0], y=150)]
    assert reel_geom.overlay_on_drawing(reel, str(d), ok, on_paper) == []


def test_geometry_macro_of_big_figure_is_not_a_sliver(tmp_path):
    """Рилс эп.01 (23.10): крупный план искры на мозге — мозг, цепь, глыба и кот одно пятно, в окне 3 % его. Это не обрывок,
    если пятно главное в окне и раскинуто по нему; сплошная полоса того же пятна у края — по-прежнему обрывок."""
    import numpy as np
    from PIL import Image
    import reel_geom
    d = tmp_path / "reel"; (d / "src").mkdir(parents=True)
    img = np.full((1600, 2400, 3), 245, np.uint8)
    img[100:1500, 100:2300:6] = 30                      # огромная «фигура» штриховкой во весь рисунок
    img[100:1500:6, 100:2300] = 30
    Image.fromarray(img).save(d / "src" / "macro_c.png")
    reel.layout({"beats": [], "picture_h": 1380})
    macro = [dict(t0=0.0, t1=2.0, src="macro", kind="crop", **{"from": [600, 400, 200]})]   # окно целиком внутри фигуры
    assert reel_geom.slivers(reel, str(d), macro) == []
    reel_geom._INK.clear()


def test_fill_windows_keeps_push_in_when_window_taller_than_drawing(tmp_path):
    """Рилс эп.01: окна 710/666 выше рисунка сжимались к 530/528 — наезд пропадал, 9 % неподвижных кадров."""
    import numpy as np
    from PIL import Image
    d = tmp_path / "reel"; (d / "src").mkdir(parents=True)
    img = np.full((1600, 2400, 3), 245, np.uint8); img[400:1200, 600:1400] = 30   # рисунок 400 точек кадра в высоту
    Image.fromarray(img).save(d / "src" / "short_c.png")
    sp = {"beats": [{"text": "a", "shots": [{"src": "short", "from": [500, 400, 700], "to": [500, 400, 650]}]}]}
    reel.fill_windows(str(d), sp)
    s = sp["beats"][0]["shots"][0]
    assert s["to"][2] / s["from"][2] < 0.95                  # наезд сохранён
    assert s["from"][2] <= 400 * 1.05


def test_load_src_cache_is_per_reel(tmp_path):
    import numpy as np
    from PIL import Image
    for k, v in (("a", 10), ("b", 200)):
        (tmp_path / k / "src").mkdir(parents=True)
        Image.fromarray(np.full((8, 8, 3), v, np.uint8)).save(tmp_path / k / "src" / "f1_c.png")
    assert reel.load_src(str(tmp_path / "a"), "f1")[0, 0, 0] == 10
    assert reel.load_src(str(tmp_path / "b"), "f1")[0, 0, 0] == 200


def test_draft_reads_own_drawings_of_the_reel(tmp_path):
    import reel_draft
    p = tmp_path / "reel_script.txt"
    p.write_text("@f6 = gen/r1_phone.png\nТри дня. *Письмо*.  @f1\nОткрываешь почту.  @f6\n", encoding="utf8")
    extra = {}
    beats = reel_draft.parse(str(p), extra)
    assert extra == {"f6": "gen/r1_phone.png"} and [b["src"] for b in beats] == ["f1", "f6"]


def test_cover_opens_counters_filled_by_outline():
    """Обложка эп.01: обводка залила просветы «в» двумя чёрными точками."""
    import numpy as np
    from PIL import Image
    import reel_publish
    a = np.zeros((60, 60, 4), np.uint8)
    a[10:50, 10:50] = (255, 255, 255, 255)                  # белая буква
    a[25:35, 25:35] = (0, 0, 0, 255)                        # просвет, целиком залитый обводкой
    out = np.asarray(reel_publish.open_counters(Image.fromarray(a)))
    assert out[30, 30, 3] == 0 and out[15, 15, 3] == 255


def test_wave8_persuasion_rules():
    """Волна 8 (23.10): давящие слова, закреп-приманка «напиши 1/2», серия без номера, смысловые петли реже 12 с."""
    s = spec()
    assert reel_rules.check_knowledge(s) == []
    bad = copy.deepcopy(s); bad["beats"][15]["text"] = "Обязательно переходи по ссылке, *успей*."
    assert any("давящее" in e for e in reel_rules.check_knowledge(bad))
    bait = copy.deepcopy(s); bait["passport"]["pinned_comment"] = "Напиши 1 — есть диагноз, 2 — нет"
    assert any("приманка" in e for e in reel_rules.check_knowledge(bait))
    ok = copy.deepcopy(s); ok["passport"]["pinned_comment"] = "Какое дело висит у тебя дольше всех?"
    assert not any("приманка" in e for e in reel_rules.check_knowledge(ok))
    ser = copy.deepcopy(s); ser["passport"]["series"] = {"name": "Кот и дела"}
    assert any("серия" in e for e in reel_rules.check_knowledge(ser))
    todo = copy.deepcopy(s); todo["passport"]["knowledge"].pop("if_then_cta")
    assert any("if_then_cta" in e for e in reel_rules.check_knowledge(todo))
    t0 = [i * 2.5 for i in range(len(s["beats"]))]
    lp = copy.deepcopy(s); lp["passport"]["knowledge"]["meaning_loops"] = [1, 12]
    assert any("петель" in e for e in reel_rules.knowledge_timing(lp, t0, 45.0))
    lp["passport"]["knowledge"]["meaning_loops"] = [1, 5, 9, 13]
    assert not any("петель" in e for e in reel_rules.knowledge_timing(lp, t0, 45.0))


def test_ep01_reel_v2_passes_all_rules():
    p = os.path.join(ROOT, "videos", "01_sdvg_pismo", "reel", "reel.json")
    s = json.load(open(p, encoding="utf8"))
    assert reel_rules.check_spec(s, SFX) == [] and reel_rules.check_knowledge(s) == []
    assert s["passport"]["series"]["episode"] == 1


def _w9(s):                                                     # минимальный паспорт хука стандарта 9 на рилсе эп.02
    pp = s["passport"]
    pp["standard"] = 9
    cands = [s["beats"][0]["text"].replace("*", "")] + [f"Кандидат хука номер {i}" for i in range(20)]
    pp["hook"] = {"who": "кто откладывает и винит себя", "pain": "листает вместо дела",
                  "audience_quote": {"text": "Хотел делать дела - а тут как раз новое видео", "likes": 1000,
                                     "video": "EJNSe9OPWkU"},
                  "blame_off": "это не лень", "lever": [7, 3],
                  "payoff": {"promise": "как начать прямо сейчас", "tease": 1, "pay": len(s["beats"]) - 1},
                  "first_frame": {"event": "кот листает телефон", "object": "телефон", "focus_points": 3},
                  "candidates": [{"text": c, "score": 5} for c in cands]}
    pp["hook_variants"] = [{"text": "Листаешь вместо дела.", "first": "f1:600,400,500"},
                           {"text": "Это не лень. Стена.", "first": "f3:600,400,500"}, "Третий вариант хука"]
    return s


def test_wave9_hook_passport():                                 # 09 §6, §22: паспорт хука — кодом, для стандарта 9
    assert reel_rules.check_hook(spec()) == []                 # прежние рилсы (эталон v15) — без изменений
    s = _w9(spec())
    assert reel_rules.check_hook(s) == [], reel_rules.check_hook(s)

    def errs(fn, log=()):
        x = _w9(spec()); fn(x); return " ".join(reel_rules.check_hook(x, list(log)))
    assert "не найдена в комментариях" in errs(lambda x: x["passport"]["hook"]["audience_quote"].update(text="выдумка автора про лень"))
    assert "lever" in errs(lambda x: x["passport"]["hook"].update(lever=17))
    assert "как у прошлого рилса" in errs(lambda x: None, [{"reel": "videos/99/reel", "lever": 7}])
    assert "не в первых двух" in errs(lambda x: x["passport"]["hook"]["payoff"].update(tease=4))
    assert "не в последних 40" in errs(lambda x: x["passport"]["hook"]["payoff"].update(pay=2))
    assert "фокусных точек" in errs(lambda x: x["passport"]["hook"]["first_frame"].update(focus_points=5))
    assert "решение" in errs(lambda x: x["beats"][0]["shots"].insert(0, {"kind": "doll", "at": 0}))
    assert "кандидатов хука" in errs(lambda x: x["passport"]["hook"].update(candidates=x["passport"]["hook"]["candidates"][:5]))
    assert "не из списка кандидатов" in errs(lambda x: x["beats"][0].update(text="Совсем другой *хук*."))
    assert "другим первым кадром" in errs(lambda x: x["passport"].update(hook_variants=["a", "b", "c"]))
    assert "blame_off" in errs(lambda x: x["passport"]["hook"].pop("blame_off"))

    def early_cta(x):
        x["beats"][3]["text"] = "Напиши мне *слово*."
    assert "один призыв" in errs(early_cta)

    def kw(x):
        x["passport"]["keyword"] = {"word": "КОТ", "delivers": "ссылку на сессию"}
        x["beats"][x["passport"]["cta_beat"]]["text"] = "Напиши *КОТ* — пришлю, где я сижу."
        x["passport"]["caption"] = "СДВГ и дела. Напиши КОТ в комментариях. #сдвг #прокрастинация #дела"
        x["passport"]["pinned_comment"] = "Какое дело висит дольше всех?"
    assert errs(kw) == ""
    assert "кодового слова" in errs(lambda x: (kw(x), x["beats"][x["passport"]["cta_beat"]].update(text="Пиши мне.")))

    def kw_and_bio(x):
        kw(x); x["beats"][-1]["text"] = "Ссылка в шапке."
    assert "шапка профиля" in errs(kw_and_bio)
    assert not [e for e in reel_rules.check_knowledge(s) if "вариант" in e]   # варианты-словари читаются как текст


def test_variant_from_wave9_dict(tmp_path):                     # пробный вариант берёт текст и первый кадр из паспорта
    import reel_variant
    d = tmp_path / "reel"; d.mkdir()
    s = _w9(spec()); json.dump(s, open(d / "reel.json", "w", encoding="utf8"), ensure_ascii=False)
    out = reel_variant.make(str(d), "Листаешь вместо дела.", "f1:600,400,500")
    v = json.load(open(os.path.join(out, "reel.json"), encoding="utf8"))
    assert v["beats"][0]["shots"][0]["src"] == "f1" and v["passport"]["variant_of"]
    assert all(reel_rules.variant_text(x) != "Листаешь вместо дела." for x in v["passport"]["hook_variants"])
    assert not [e for e in reel_rules.check_hook(v) if "другим первым кадром" in e]


def test_text_on_fit_shot_is_caught(tmp_path):                 # эп.01 v3: «КОТ» лёг коту на глаз — fit-планы не смотрелись
    import numpy as np
    from PIL import Image
    import reel_geom
    d = tmp_path / "reel"; (d / "src").mkdir(parents=True)
    img = np.full((1600, 2400, 3), 245, np.uint8)
    img[100:1000, 600:1800] = 30                        # «кот» в верхней половине рисунка (кадр 1200×800: x 300–900, y 50–500)
    Image.fromarray(img).save(d / "src" / "fittest_c.png")
    (d / "reel.json").write_text('{"sources": {}}', encoding="utf8")
    reel.layout({"beats": [], "picture_h": 1380})
    fit = [dict(t0=0.0, t1=2.0, src="fittest", kind="fit", region=[0, 0, 1200, 800], cy=560, width=1.0, zoom=[1.0, 1.0])]
    on_cat = [dict(kind="write", text="КОТ", x=540, y=420, size=230, t=0.5, dur=0.5)]
    assert reel_geom.overlay_on_drawing(reel, str(d), fit, on_cat)
    assert reel_geom.overlay_on_drawing(reel, str(d), fit, [dict(on_cat[0], y=1150)]) == []


def test_variant_with_new_first_frame_keeps_loop(tmp_path):    # конец = начало и у пробного варианта
    import reel_variant
    d = tmp_path / "reel"; d.mkdir()
    json.dump(spec(), open(d / "reel.json", "w", encoding="utf8"), ensure_ascii=False)
    out = reel_variant.make(str(d), "Это не лень. Время.", "f3:600,400,500")
    v = json.load(open(os.path.join(out, "reel.json"), encoding="utf8"))
    assert not [e for e in reel_rules.check_spec(v, SFX) if "петля" in e]


def test_reading_push_keeps_riser_cut(tmp_path):               # эп.01 v3: хук в две группы уводил склейку с пика riser
    import shutil
    d = tmp_path / "reel"; shutil.copytree(os.path.join(ROOT, "videos", "01_sdvg_pismo", "reel", "src"), d / "src")
    s = json.load(open(os.path.join(ROOT, "videos", "01_sdvg_pismo", "reel", "reel.json"), encoding="utf8"))
    s["sources"] = {k: {"frame": os.path.join(ROOT, "videos", "01_sdvg_pismo", "reel", v["frame"])} for k, v in s["sources"].items()}
    s["fill_ink"] = False
    json.dump(s, open(d / "reel.json", "w", encoding="utf8"), ensure_ascii=False)
    got = {}
    orig = reel.contact_sheet
    reel.contact_sheet = lambda rd, shots: got.setdefault("cut", shots[1]["t0"])
    try:
        reel.build(str(d), sheet=True, force=True)
    finally:
        reel.contact_sheet = orig
    assert abs(got["cut"] - reel.SFX["riser"][1]) <= reel_rules.RISER_PEAK_ON_CUT


def test_matrix_gate():                                         # 24.10: каждый приём базы решён в рилсе стандарта 10
    m = [{"id": "H001", "title": "парадокс внутри боли", "scope": "reel", "ask": "Где?"},
         {"id": "B001", "title": "снять вину до объяснения", "scope": "reel"},
         {"id": "V001", "title": "склейка на слово", "scope": "global", "status": "код"},
         {"id": "X001", "title": "выдуманный дефицит", "scope": "forbidden"}]
    s = spec(); s["passport"]["standard"] = 9
    assert reel_rules.check_matrix(s, m) == []                  # стандарт 9 и раньше — без матрицы
    s = _w9(spec()); s["passport"]["standard"] = 10
    e = reel_rules.check_matrix(s, m)
    assert len(e) == 2 and all("нет решения" in x for x in e)   # global и forbidden в рилсе не решаются
    s["passport"]["matrix"] = {"H001": {"candidate": 0}, "B001": 4}
    assert reel_rules.check_matrix(s, m) == []
    s["passport"]["matrix"]["B001"] = {"skip": "коротко"}
    assert "без причины" in " ".join(reel_rules.check_matrix(s, m))
    s["passport"]["matrix"]["B001"] = {"where": "caption", "how": "в подписи первой строкой"}
    assert reel_rules.check_matrix(s, m) == []
    s["passport"]["matrix"]["B001"] = 99
    assert "не номер фразы" in " ".join(reel_rules.check_matrix(s, m))
    many = [{"id": f"B{i:03d}", "title": "x", "scope": "reel"} for i in range(5)]
    s["passport"]["matrix"] = {f"B{i:03d}": {"skip": "не подходит этому рилсу вообще"} for i in range(5)}
    assert "одна и та же отговорка" in " ".join(reel_rules.check_matrix(s, many))
    cv = reel_rules.matrix_coverage(s, many)
    assert cv["skip"] == 5 and cv["none"] == 0


def test_keyword_caption_and_engagement_bait():                 # 24.10, слияние матрицы: пробелы, найденные в коде
    s = _w9(spec())
    s["passport"]["keyword"] = {"word": "КОТ", "delivers": "ссылку на сессию"}
    s["beats"][s["passport"]["cta_beat"]]["text"] = "Напиши *КОТ* — пришлю, где я сижу."
    s["passport"]["caption"] = "СДВГ и дела. Напиши КОТ — пришлю. #сдвг #прокрастинация #дела"
    assert not [e for e in reel_rules.check_hook(s) if "подпис" in e or "caption" in e]
    s["passport"]["caption"] = "СДВГ и дела. Ссылка в шапке. #сдвг #прокрастинация #дела"
    e = " ".join(reel_rules.check_hook(s))
    assert "caption" in e and "нет кодового слова" in e
    s = spec(); s["beats"][3]["text"] = "Досмотри до *конца*."
    assert "приманка удержания" in " ".join(reel_rules.check_knowledge(s))
    s = spec(); s["passport"]["pinned_comment"] = "Поставь лайк, если узнал себя"
    assert "приманка удержания" in " ".join(reel_rules.check_knowledge(s))


def test_matrix_b_stop_phrases_and_rhythm():                    # 24.10, матрица B: затёртые фразы, «вы», ровный ритм
    for txt in ("Вы не поверите, что *было*.", "Итак, *начнём*.", "Купи *курс*.", "Вам это *знакомо*?"):
        assert broken(lambda s, t=txt: s["beats"][3].update(text=t)), txt
    s = spec()
    for i in range(3):
        s["beats"][i + 3]["text"] = "Ровно двадцать знаков."
    assert any("одной длины" in w for w in reel_rules.warnings(s, [], 30.0))


def test_captions_two_three_words():
    """Владелец 24.10: субтитры по 2–3 слова, а не по одному. Одиночная группа — только у предложения из одного
    слова; запятая — не обрыв; группа не кончается предлогом."""
    words = "Чем дольше молчишь, тем длиннее кажется извинение. Там правда ничего страшного не было. Неделю.".split()
    times = [dict(start=i * 0.3, end=i * 0.3 + 0.25) for i in range(len(words))]
    groups = [[words[j] for j in c["idx"]] for c in reel.chunks(words, times)]
    assert all(2 <= len(g) <= 3 for g in groups[:-1]), groups
    assert groups[-1] == ["Неделю."]
    assert not any(reel.bare(g[-1]) in reel.CLITICS for g in groups), groups


EP01 = os.path.join(ROOT, "videos", "01_sdvg_pismo", "reel", "reel.json")


def _std11(beats):
    return {"beats": [{"text": t} for t in beats], "passport": {"standard": 11}}


def test_human_text_catches_machine_style():                   # 24.10, владелец: тире и рваная парцелляция — нейросеть
    v4 = json.load(open(EP01, encoding="utf8"))                 # v4 — текст, который владелец назвал нейросетевым
    v4["passport"]["standard"] = 11
    e = reel_rules.check_human(v4)
    assert any("тире" in x for x in e) and any("осколк" in x for x in e) and any("Не X. А Y" in x for x in e)
    for bad, sign in (("Это сложно — но можно.", "тире"), ("Не просто кот, а напарник.", "не просто"),
                      ("Зачем? Потому что страшно.", "Потому что"), ("Важно понимать, что это не лень.", "важно"),
                      ("Секрет прост: начни.", "секрет"), ("Я сижу. Я жду. Я молчу.", "три предложения")):
        assert any(sign.lower() in x.lower() for x in reel_rules.check_human(_std11([bad]))), bad
    assert reel_rules.check_human(_std11(["Две минуты.", "Одна строчка."]))      # осколки через фразы — тоже подряд
    live = ["Мне написали в понедельник, а сейчас пятница, и я всё ещё не открыл.",
            "Там же ничего такого, просто «как дела», но открыть страшнее, чем сдать отчёт.",
            "С 3–5 минут начать легче, поэтому я сажусь рядом."]
    assert reel_rules.check_human(_std11(live)) == []           # длинные живые фразы и числовой диапазон проходят
    assert reel_rules.check_human({"beats": [{"text": "А это — нет."}], "passport": {"standard": 10}}) == []


def test_coverage_items_come_from_documents():                  # 24.10: список берётся из 12 и 09, а не вписан в код
    it = reel_rules.strategy_items()
    n = {g: sum(1 for k in it if k[0] == g) for g in reel_rules.COVERAGE_GROUPS}
    assert n == {"L": 40, "S": 9, "R": 16, "F": 10, "B": 15, "D": 15}
    assert it["L1"].startswith("Парадокс") and it["S1"] == "Хук-парадокс" and it["R7"].startswith("Поймать в моменте")


def test_coverage_gate():                                       # 24.10: ни один пункт стратегии нельзя молча пропустить
    items = {"L1": "парадокс", "S1": "хук", "F1": "вдруг ленивый", "D1": "рядом"}
    s = _std11(["a", "b", "c"])
    e = reel_rules.check_coverage(s, items=items)
    assert len(e) == 4 and all("нет решения" in x for x in e)
    s["passport"]["coverage"] = {"L1": 0, "S1": {"skip": "рилс короткий, не влезло"}, "F1": [1], "D1": {"where": "site", "how": "кот"}}
    e = reel_rules.check_coverage(s, items=items)
    assert any("шаг формулы не пропускается" in x for x in e)   # скелет обязателен
    assert any("чем снят страх" in x for x in e)                # страх без «how» — не решён
    assert any("вне ролика" in x for x in e)                    # «how» короче 15 знаков
    s["passport"]["coverage"] = {"L1": 0, "S1": [0], "F1": {"beats": [1, 2], "how": "фраза 2 снимает: ленивые себя не грызут"},
                                 "D1": {"where": "site", "how": "кот просит посидеть с ним на сайте"}}
    assert reel_rules.check_coverage(s, items=items) == []
    many = {f"L{i}": "x" for i in range(1, 5)}
    s["passport"]["coverage"] = {k: {"skip": f"не подходит к теме письма, номер {k}"} for k in many}
    assert any("стратегия не использована" in x for x in reel_rules.check_coverage(s, items=many))


def test_new_reel_must_be_standard_11():                        # 24.10: старым стандартом новый рилс не обойти
    log = json.load(open(os.path.join(ROOT, "docs", "reels_log.json"), encoding="utf8"))
    v4 = json.load(open(EP01, encoding="utf8"))
    assert reel_rules.check_coverage(v4, log, "videos/01_sdvg_pismo/reel") == []   # v4 в журнале — пересобирается
    v4["beats"][0]["text"] = "Новый хук про письмо."
    assert any("стандартом 10" in x for x in reel_rules.check_coverage(v4, log, "videos/01_sdvg_pismo/reel"))
    assert reel_rules.check_coverage(spec(), log, "videos/02_sdvg_vremya/reel") == []   # эталон v15 — тоже
