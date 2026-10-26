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
    # владелец 25.10: картинка чуть ниже — сверху 60 px бумаги, внизу меньше (было: 0–1380, субтитры 1455)
    assert reel.PIC_TOP == 60 and reel.PH == 1440 and reel.CAP_CY == 1575   # картинка 60–1500, граница интерфейса 1560
    assert reel_rules.SAFE_BOTTOM == 1560
    s2 = copy.deepcopy(s); reel.layout(s2)
    assert abs(s2["beats"][0]["shots"][0]["from"][2] - 113.0) < 1e-6          # view_scale 1.13 при 1440
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
    new["passport"]["hook_type"] = next(t for t in reel_rules.HOOK_TYPES if t != log[-1].get("hook_type"))  # не как у последнего
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
    assert [x["name"] for x in plan][:5] == ["swoosh", "swoosh_deep", "riser", "swoosh", "swoosh"]
    assert plan[0]["whip"] and plan[0]["pan"] == 0.3 and plan[3]["soft"] and plan[3]["gain_db"] == reel.SOFT_DB["zoom"]
    assert [(x["name"], x["t"]) for x in plan[5:]] == [("swoosh", 0.0)]   # переход 24.10: удар на первом кадре


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


def test_cover_waits_for_anchor_words(tmp_path):
    """26.10: обложка бралась на 0.05 с — маркер якоря уже проведён, слов ещё нет (пустая жёлтая полоса)."""
    import reel_publish
    spec_ = {"beats": [{"fx": [{"kind": "mark", "anchor": True, "text": "Потом помою полы", "at": 0, "speed": 2.0}]}]}
    (tmp_path / "reel.json").write_text(json.dumps(spec_), encoding="utf8")
    rep = {"events": [{"kind": "mark", "t": 0.0, "beat": 0}]}
    assert reel_publish.cover_time(str(tmp_path), rep) >= 0.3
    (tmp_path / "reel.json").write_text(json.dumps({"beats": [{"fx": []}]}), encoding="utf8")
    assert reel_publish.cover_time(str(tmp_path), {"events": []}) == 0.05


def test_question_first_answer_only_at_the_end():
    """26.10, владелец: «чтоб никогда не нарушено… иначе пролистывание». Живой промах «Пошёл мыть полы» v1: вопроса
    в начале не было, а ответ «заодно» прозвучал на 9.4 с из 39.6 — к «раскрытию» на 22.7 с он был уже известен."""
    def build(texts, loop, caption="Почему я ничего не довожу?", peaks=(), gap=0.5):
        beats = [{"text": t} for t in texts]
        words, spans, times, t = [], [], [], 0.0
        for b in beats:
            ws = b["text"].split(); spans.append((len(words), len(words) + len(ws))); words += ws
            for w in ws:
                if "заодн" in w: t += gap                     # «звуковой вакуум» перед ответом
                times.append({"start": t, "end": t + 0.4}); t += 0.45
        sp = {"beats": beats, "passport": {"standard": 17, "hook": {"loop": loop, "payoff": {"pay": 5}}, "caption": caption,
                                           "cover": {"text": "Пошёл мыть полы"}, "cta_beat": 6}}
        return reel_rules.check_open_loop(sp, words, times, spans, t, (), peaks)
    good = ["Шёл мыть полы, а сажаю цветы.", "Как так вышло? Полы я, кстати, домыл.", "И это не лень, правда.",
            "Одно слово уводит дальше, цветы, стирка, чайник, кино.", "А потом заметил, где теряюсь: на слове «заодно».",
            "Полы помыты.", "Напиши в комментах."]
    def gap_at(texts):
        n = 0
        for t in texts:
            for w in t.split():
                if "заодн" in w: return n * 0.45
                n += 1
    loop = {"question": 1, "reveal": 4, "answer": ["заодн"], "preblock": 2, "preview": 1, "loops": [[1, 4], [1, 5], [3, 4]]}
    assert build(good, loop) == []
    assert any("пауза" in e for e in build(good, loop, gap=0.0))                       # без тишины перед ответом
    assert any("звучит звук" in e for e in build(good, loop, peaks=[gap_at(good) + 0.2]))           # звук в тишине перед ответом
    assert any("preblock" in e for e in build(good, dict(loop, preblock=3)))          # догадка закрыта поздно
    assert any("preview" in e for e in build(good, dict(loop, preview=None)))         # нет превью концовки
    assert any("превью концовки" in e for e in build(good, dict(loop, preview=3)))    # превью позже 4.5 с
    assert any("петель" in e for e in build(good, dict(loop, loops=[[1, 4]])))        # одна петля — мало
    assert any("в призыве" in e for e in build(good, dict(loop, loops=[[1, 4], [2, 6], [3, 4]])))
    leak = list(good); leak[3] = "Каждое «заодно» уводит дальше, цветы, стирка, чайник, кино."
    assert any("до раскрытия" in e for e in build(leak, loop))
    noq = list(good); noq[1] = "Через час сажал цветы, вот так вышло."
    assert any("вопроса нет" in e for e in build(noq, loop))
    assert any("подпись" in e for e in build(good, loop, caption="Это «заодно» уводит от дел"))
    assert any("loop" in e for e in build(good, {}))
    early = good[:2] + [good[4]] + good[2:4] + good[5:] + ["И отправь тому, кто тоже начинает с полов, а заканчивает кино."]
    assert any("раньше середины" in e for e in build(early, dict(loop, reveal=2)))


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


def test_hook_caption_is_one_group():                           # эп.01 v5: хук резался на две группы по 2 слова —
    words = "Тебе же *плевать*, да? Он так думает, |а ты неделю боишься.".split()   # первый кадр показывал полхука
    times = [dict(start=i * 0.3, end=i * 0.3 + 0.25) for i in range(len(words))]
    groups = [[words[j] for j in c["idx"]] for c in reel.chunks(words, times)]
    assert groups[0] == ["Тебе", "же", "*плевать*,", "да?"], groups
    assert all(len(g) <= 3 for g in groups[1:]), groups
    wide = "Он решил: тебе *плевать*. А ты молчишь.".split()           # шире строки (913 > 860 px) — делится,
    groups = [[wide[j] for j in c["idx"]] for c in reel.chunks(wide, times)]   # а не вылезает под кнопки Reels
    assert all(reel.cap_width(c["idx"], wide) <= reel.CAP_MAX_W for c in reel.chunks(wide, times)), groups


EP01 = os.path.join(ROOT, "tests", "fixtures", "reel_ep01_v4.json")   # v4 — текст, отклонённый владельцем (рилс уже v5)


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


def test_coverage_gate():                                       # 24.10: ни один пункт не забыт, но в рилсе — только сильнейшие
    items = {"L1": "парадокс", "L2": "переворот", "L3": "довод", "L4": "если ты", "L5": "мечта",
             "S1": "хук", "F1": "вдруг ленивый", "D1": "рядом"}
    s = _std11(["a", "b", "c"])
    e = reel_rules.check_coverage(s, items=items)
    assert sum("нет решения" in x for x in e) == 8
    s["passport"]["coverage"] = {"L1": 0, "L2": 1, "L3": 2, "L4": 2, "L5": {"skip": "мечта и стыд — в следующей серии"},
                                 "S1": {"skip": "рилс короткий, не влезло"}, "F1": [1], "D1": {"where": "site", "how": "кот"}}
    e = reel_rules.check_coverage(s, items=items)
    assert any("шаг формулы не пропускается" in x for x in e)   # скелет обязателен
    assert any("чем снят страх" in x for x in e)                # страх без «how» — не решён
    assert any("вне ролика" in x for x in e)                    # «how» короче 15 знаков
    s["passport"]["coverage"].update({"S1": [0], "F1": {"beats": [1, 2], "how": "фраза 2 снимает: ленивые себя не грызут"},
                                      "D1": {"where": "site", "how": "кот просит посидеть с ним на сайте"}})
    assert reel_rules.check_coverage(s, items=items) == []
    s["passport"]["coverage"].update({"L3": {"skip": "не подходит к письму, другой сюжет"}})
    assert any("связок во фразах 3" in x for x in reel_rules.check_coverage(s, items=items))   # меньше 4 — слабо
    many = {f"L{i}": "x" for i in range(1, 13)}
    s["passport"]["coverage"] = {k: 0 for k in many}
    assert any("связок во фразах 12" in x for x in reel_rules.check_coverage(s, items=many))   # больше 10 — вода (v7: 33)
    s["passport"]["coverage"] = {k: 0 if k in ("L1", "L2", "L3", "L4") else {"skip": f"отложено в серию, пункт {k}"}
                                 for k in many}
    assert reel_rules.check_coverage(s, items=many) == []       # отказов сколько угодно, но у каждого своя причина
    s["beats"] = [{"text": "слово " * 120}]
    assert any("знаков" in x for x in reel_rules.check_coverage(s, items=many))                 # текст длиннее ~40 с


def test_new_reel_must_be_standard_11():                        # 24.10: старым стандартом новый рилс не обойти
    log = json.load(open(os.path.join(ROOT, "docs", "reels_log.json"), encoding="utf8"))
    v4 = json.load(open(EP01, encoding="utf8"))
    assert reel_rules.check_coverage(v4, log, "videos/01_sdvg_pismo/reel") == []   # v4 в журнале — пересобирается
    v4["beats"][0]["text"] = "Новый хук про письмо."
    assert any("стандартом 10" in x for x in reel_rules.check_coverage(v4, log, "videos/01_sdvg_pismo/reel"))
    assert reel_rules.check_coverage(spec(), log, "videos/02_sdvg_vremya/reel") == []   # эталон v15 — тоже


def test_inventory_phrase_decision_needs_proof():             # 24.10, владелец: «из стольких источников — один пример?»
    inv = [{"id": "Itest01", "line": 1, "title": "приём", "scope": "reel"}]   # v5: 955 голых номеров фраз, ноль правок
    beats = [{"text": "«Тебе просто *плевать*.»", "shots": [{"src": "f6"}], "fx": []},
             {"text": "Кому плевать, вокруг писем не *ходит*.", "shots": [{"src": "f1"}],
              "fx": [{"kind": "write", "text": "плевать", "strike_at": 4}], "gaps": [[5, 0.6]]}]

    def errs(dec):
        s = {"beats": beats, "passport": {"standard": 12, "inventory": {"Itest01": dec}}}
        return reel_rules.check_inventory(s, inventory=inv, matrix=[])
    assert errs(1) and "голый номер" in errs(1)[0]
    assert errs({"beats": [1], "quote": "вокруг писем не ходит"}) == []
    assert errs({"beats": [1], "quote": "Вокруг писем, не ходит!"}) == []        # регистр и знаки не важны
    assert errs({"beats": [0], "quote": "вокруг писем"})                          # цитата из другой фразы — нет
    assert errs({"beats": [1], "quote": "две минуты"})                            # выдуманная цитата — нет
    assert errs({"beats": [1], "evidence": "fx:strike"}) == []
    assert errs({"beats": [1], "evidence": "gaps"}) == []
    assert errs({"beats": [0], "evidence": "fx:strike"})                          # зачёркивания во фразе 0 нет
    assert errs({"beats": [0], "evidence": "shot:f6"}) == []
    assert errs({"beats": [0], "evidence": "shot:f3"})


def test_strike_is_opt_in_and_draws_over_word():               # 24.10: зачёркивание от руки — только если поле задано
    import numpy as np
    im = reel.text_img("плевать", reel.font(reel.HAND, 120, 700), reel.INK)
    base = np.full((600, 1080, 3), 245, np.uint8)
    reel.strike(base, im, 540, 300, 1.0, 0.0)
    assert (base == 245).all()                                  # u = 0: ещё ничего не нарисовано
    reel.strike(base, im, 540, 300, 1.0, 1.0)
    red = (base[..., 0] > 180) & (base[..., 1] < 90)
    xs = np.where(red.any(axis=0))[0]
    assert red.sum() > 500 and xs[-1] - xs[0] > im.getchannel("A").getbbox()[2] - im.getchannel("A").getbbox()[0]


def test_hook_that_does_not_fit_one_line_is_an_error():        # эп.01 v6: «„Тебе просто плевать.“» 984 px — делился молча
    def errs(text):
        words = (text + " А ты третий день думаешь.").split()
        times = [dict(start=i * 0.3, end=i * 0.3 + 0.25) for i in range(len(words))]
        n = len(text.split())
        return reel.hook_split_errors(words, times, [(0, n), (n, len(words))])
    assert errs("«Тебе просто *плевать*.»")
    assert errs("«Тебе *плевать*.»") == []


def test_after_sfx_takes_nearest_sound_not_first():           # эп.01 v6: второй riser вёл раскрытие к пику первого
    beats = [{"text": "а", "fx": [{"kind": "sfx", "name": "riser", "at": 0}]}, {"text": "б", "after_sfx": "riser"},
             {"text": "в", "fx": [{"kind": "sfx", "name": "riser", "at": 0, "tag": 2}]}, {"text": "г", "after_sfx": "riser"}]
    assert reel.after_sfx_source(beats, 1)[0] == 0
    assert reel.after_sfx_source(beats, 3) == (2, beats[2]["fx"][0])


def test_hook_needs_five_layers_and_3c():                    # правило владельца 24.10: хук — пять слоёв и 3C
    EP01 = os.path.join(ROOT, "videos", "01_sdvg_pismo", "reel", "reel.json")
    s = json.load(open(EP01, encoding="utf8"))
    assert reel_rules.check_hook_layers(s) == []
    for k in reel_rules.HOOK_LAYERS + reel_rules.HOOK_C3:
        t = copy.deepcopy(s); h = t["passport"]["hook"]
        (h["layers"] if k in reel_rules.HOOK_LAYERS else h["c3"]).pop(k)
        assert any(f"«{k}»" in e for e in reel_rules.check_hook_layers(t)), k
    t = copy.deepcopy(s); t["passport"]["caption"] = "Другая первая строка. " + t["passport"]["caption"]
    assert any("caption" in e for e in reel_rules.check_hook_layers(t))       # слой подписи — её первая строка
    t = copy.deepcopy(s); t["beats"][0]["fx"] = []; t["beats"][0].pop("gaps", None)
    assert any("аудиослоя" in e for e in reel_rules.check_hook_layers(t))
    t = copy.deepcopy(s); t["passport"]["standard"] = 11
    assert reel_rules.check_hook_layers(t) == []                              # старые рилсы не ломаются


def test_call_to_comment_is_always_there():                  # владелец 24.10: призыв в комментарии — в каждом рилсе
    EP01 = os.path.join(ROOT, "videos", "01_sdvg_pismo", "reel", "reel.json")
    s = json.load(open(EP01, encoding="utf8")); k = s["passport"]["cta_beat"]
    s["beats"][k]["text"] = "Напиши в комментах, что у тебя вызывает такой *ступор*."
    assert reel_rules.check_call_to_comment(s) == []
    t = copy.deepcopy(s); t["beats"][k]["text"] = "Можешь посидеть со мной. Это бесплатно."
    assert reel_rules.check_call_to_comment(t)                                   # тёплая фраза без призыва — ошибка
    t = copy.deepcopy(s); del t["passport"]["cta_beat"]
    assert reel_rules.check_call_to_comment(t)                                   # призыва нет — ошибка
    t = copy.deepcopy(s); t["passport"]["standard"] = 11
    assert reel_rules.check_call_to_comment(t) == []                             # старые рилсы не ломаются


def test_voice_segments_follow_phrase_shifts():               # голос Lumean режется по фразам и встаёт на их новые места
    nat = [dict(start=0.0, end=0.4), dict(start=0.5, end=0.9), dict(start=1.5, end=1.9), dict(start=2.0, end=2.3)]
    times = [dict(w, start=w["start"] + 0.12, end=w["end"] + 0.12) for w in nat[:2]] + \
            [dict(w, start=w["start"] - 0.2, end=w["end"] - 0.2) for w in nat[2:]]   # перебивка + подтяжка к пику riser
    segs = reel.voice_segments("x", nat, times)
    assert len(segs) == 2
    assert segs[0]["s0"] == 0.0 and abs(segs[0]["dst"] - 0.12) < 1e-9
    cut = (0.9 + 1.5) / 2                                                       # граница — середина тишины
    assert abs(segs[0]["s1"] - cut) < 1e-9 and abs(segs[1]["s0"] - cut) < 1e-9
    assert abs(segs[1]["dst"] - (cut - 0.2)) < 1e-9 and segs[1]["s1"] is None


def test_text_limit_rises_only_with_owner_word():            # владелец 24.10: «43 секунды не страшно» — только явно
    EP01 = os.path.join(ROOT, "videos", "01_sdvg_pismo", "reel", "reel.json")
    s = json.load(open(EP01, encoding="utf8"))
    def long(e):
        return [x for x in e if "знаков >" in x]
    assert not long(reel_rules.check_coverage(s))                                  # 582 знака со словом владельца
    t = copy.deepcopy(s); t["passport"].pop("text_max")
    assert long(reel_rules.check_coverage(t))                                      # без слова — 520
    t = copy.deepcopy(s); t["passport"]["text_max"] = {"chars": 900, "owner": "владелец разрешил всё"}
    t["beats"][0]["text"] += " " + "слово " * 60
    assert long(reel_rules.check_coverage(t))                                      # потолок 600 даже со словом


def test_every_cut_is_heard():                               # владелец 24.10: на каждой новой картинке — звук
    shots = [dict(t0=0.0, src="f1"), dict(t0=1.7, src="f2"), dict(t0=3.4, src="f2", zoom_in=0.2), dict(t0=5.0, src="f3")]
    events = [dict(kind="sfx", name="oof", t=5.05)]                                  # смысловой звук рядом со склейкой
    plan = reel.sound_plan(shots, events)
    assert reel_rules.check_cut_sounds(plan, shots) == []
    names = {round(p["peak"], 2): p["name"] for p in plan}
    assert names[1.7] in ("swoosh", "fast_whoosh") and names[3.4] in ("swoosh", "fast_whoosh")
    assert not any(abs(p["peak"] - 5.0) < 0.3 and p["name"] != "oof" for p in plan)   # смысловой не дублируется свистом
    assert reel_rules.check_cut_sounds([], shots)                                   # без звуков — ошибка на каждой склейке


def test_brand_and_doll_face_are_not_lost():                   # владелец 24.10: в v5 пропали «Напарник» и весёлое лицо
    EP01 = os.path.join(ROOT, "videos", "01_sdvg_pismo", "reel", "reel.json")
    s = json.load(open(EP01, encoding="utf8"))
    assert reel_rules.check_brand_and_face(s, "Напарник") == []
    t = copy.deepcopy(s)
    for b in t["beats"]:
        b["fx"] = [f for f in b.get("fx", []) if "Напарник" not in f.get("text", "")]
    assert any("Напарник" in e for e in reel_rules.check_brand_and_face(t, "Напарник"))      # имени нет — ошибка
    t = copy.deepcopy(s)
    for b in t["beats"]:
        for sh in b.get("shots", []):
            sh["actions"] = [a for a in sh.get("actions", []) if a.get("do") != "face"]
    assert any("эмоци" in e for e in reel_rules.check_brand_and_face(t, "Напарник"))         # кукла без лица — ошибка
    t["passport"]["standard"] = 11
    assert reel_rules.check_brand_and_face(t, "Напарник") == []                               # старые рилсы не ломаются


def test_written_word_is_not_cut_by_a_splice():                # v11: «бесплатно» начиналось за 0,3 с до склейки
    shots = [dict(t0=35.85, t1=38.57, kind="doll"), dict(t0=38.57, t1=40.06, kind="doll"), dict(t0=40.06, t1=41.3, kind="crop")]
    late = [dict(kind="mark", text="бесплатно", t=39.737, dur=0.6, hold=1.2)]
    assert reel_rules.check_written_read(late, shots)                                        # как было в v11 — ошибка
    on_word = [dict(kind="mark", text="бесплатно", t=38.84, dur=0.6, hold=1.0)]
    assert reel_rules.check_written_read(on_word, shots) == []                               # на само слово — годно
    through = [dict(kind="write", text="Напарник", t=38.0, dur=0.6, hold=1.0)]               # держится через план того же рода
    assert reel_rules.check_written_read(through, shots) == []


def test_hook_steals_attention():                              # владелец 25.10: визуал, вербал, невербал, движение — не один эффект
    steal = {"visual": "крупно рука указывает на кота сверху", "verbal": "Тебя всю жизнь звали ленивым",
             "nonverbal": "кот вжался, уши прижаты, голос с нажимом", "motion": "ракурс снизу, наезд с разгоном и тряска"}
    b0 = {"text": "Тебя всю жизнь звали *ленивым*.", "shots": [{"at": 0, "src": "f1", "from": [500, 500, 700],
          "to": [500, 480, 520], "ease": "in"}], "fx": [{"kind": "shake", "at": 4, "dur": 0.4}]}
    s = {"passport": {"standard": 13, "hook": {"steal": steal}}, "beats": [b0, {"text": "дальше"}]}
    assert reel_rules.check_hook_steal(s) == []
    t = copy.deepcopy(s); t["beats"][0]["fx"] = []
    assert any("эффектов" in e for e in reel_rules.check_hook_steal(t))           # один наезд — мало
    t = copy.deepcopy(s); t["beats"][0]["shots"][0]["to"] = [500, 495, 680]
    assert any("эффектов" in e for e in reel_rules.check_hook_steal(t))           # дрейф 3 % — не движение
    t = copy.deepcopy(s); del t["passport"]["hook"]["steal"]["nonverbal"]
    assert any("nonverbal" in e for e in reel_rules.check_hook_steal(t))
    t = copy.deepcopy(s); t["passport"]["standard"] = 12
    assert reel_rules.check_hook_steal(t, [], "videos/99_new/reel")               # новый рилс ниже 13 — ошибка
    EP01 = os.path.join(ROOT, "videos", "01_sdvg_pismo", "reel", "reel.json")
    old = json.load(open(EP01, encoding="utf8"))
    log = json.load(open(os.path.join(ROOT, "docs", "reels_log.json"), encoding="utf8"))
    assert reel_rules.check_hook_steal(old, log, "videos/01_sdvg_pismo/reel") == []   # старые рилсы пересобираются


def test_dark_night_background_is_not_paper():                 # рилс 25.10: синий фон ночи делился как бумага, кот белел
    import canvas
    import numpy as np
    night = np.full((200, 300, 3), (42, 50, 62), np.float32); night[80:120, 130:170] = 20
    col, share = canvas.paper_color(night)
    assert share >= canvas.PAPER_MIN_SHARE and not canvas.is_paper(col, share)
    paper = np.full((200, 300, 3), 238, np.float32); paper[80:120, 130:170] = 20
    assert canvas.is_paper(*canvas.paper_color(paper))


def test_hook_moves_inside_the_drawing(tmp_path):
    """Стандарт 14 (владелец 25.10): движение внутри рисунка (сцена anim.py), голос и удар с 0 с, якорь 2–4 слова,
    повторный хук не позже 4.2 с; якорь не считается «вторым текстом» и «надписью на рисунке»."""
    import reel_rules as R
    (tmp_path / "anim").mkdir(); (tmp_path / "anim" / "drop.py").write_text("")
    good = {"lead_in": 0.0, "passport": {"standard": 14, "hook": {"rehook": 1}},
            "beats": [{"text": "Лежал и *устал*.", "shots": [{"src": "fa", "anim": "drop"}],
                       "fx": [{"kind": "sfx", "name": "fast_whoosh", "at": 0, "align": "start"},
                              {"kind": "mark", "anchor": True, "text": "Груз несделанного", "at": 0}]},
                      {"text": "И отдых тут не поможет.", "shots": [{"src": "f2"}]}]}
    assert R.check_hook_motion(good, [], "videos/x/reel", str(tmp_path)) == []
    import copy
    bad = copy.deepcopy(good); bad["beats"][0]["shots"][0].pop("anim")
    assert any("без движения" in e for e in R.check_hook_motion(bad, [], "videos/x/reel", str(tmp_path)))
    bad = copy.deepcopy(good); bad["lead_in"] = 0.12
    assert any("lead_in" in e for e in R.check_hook_motion(bad, [], "videos/x/reel", str(tmp_path)))
    bad = copy.deepcopy(good); bad["beats"][0]["fx"] = bad["beats"][0]["fx"][1:]
    assert any("удара звука" in e for e in R.check_hook_motion(bad, [], "videos/x/reel", str(tmp_path)))
    bad = copy.deepcopy(good); bad["beats"][0]["fx"][1]["text"] = "Лежал и устал"
    assert any("повторяет голос" in e for e in R.check_hook_motion(bad, [], "videos/x/reel", str(tmp_path)))
    bad = copy.deepcopy(good); bad["passport"]["hook"] = {}
    assert any("повторного хука" in e for e in R.check_hook_motion(bad, [], "videos/x/reel", str(tmp_path)))
    old = copy.deepcopy(good); old["passport"]["standard"] = 13
    assert any("стандартом 13" in e for e in R.check_hook_motion(old, [], "videos/x/reel", str(tmp_path)))
    assert R.rehook_timing(good, [0.0, 1.7]) == [] and R.rehook_timing(good, [0.0, 4.6])
    ev = [{"kind": "mark", "anchor": True, "text": "Груз несделанного", "t": 0.0}]
    assert R.check_writing(ev, [{"t0": 0.0}, {"t0": 1.65}]) == []


def test_sound_level_follows_role_from_voice(tmp_path):
    """25.10: пик звука = p95 пиков голоса + цель роли (ghost-editor), а не подбор на глаз; замер на дорожке звуков."""
    import numpy as np
    SR = reel.SR
    tone = (0.3 * np.sin(2 * np.pi * 220 * np.arange(int(2.0 * SR)) / SR)).astype(np.float32)   # «голос»: пик −10.5 dBFS
    vw = tmp_path / "v.wav"
    import wave
    with wave.open(str(vw), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((tone * 32767).astype(np.int16).tobytes())
    voice = [dict(src=str(vw), s0=0.0, s1=None, dst=0.0)]
    events = [dict(kind="sfx", name="oof", t=3.0, align="peak"), dict(kind="sfx", name="swoosh_deep", t=6.0, align="peak"),
              dict(kind="sfx", name="riser", t=9.0, align="peak")]
    shots = [dict(t0=0.0)]
    r = reel.mix_audio(str(tmp_path / "m.wav"), 11.0, shots, events, {}, True, voice)
    assert -14.0 < r["voice_p95"] < -10.0          # −10.5 dBFS моно; ffmpeg раскладывает моно в стерео на −3 дБ
    got = {x["name"]: x["vs_voice_db"] for x in r["sounds"]}
    assert abs(got["oof"] - reel.ROLE_DB["meme"]) < 0.6
    assert abs(got["swoosh_deep"] - reel.ROLE_DB["impact"]) < 0.6
    assert abs(got["riser"] - reel.ROLE_DB["whoosh"]) < 0.6
    assert not r["errors"]


def test_sound_gate_catches_inaudible_and_too_loud():
    """Звук ниже −22 дБ к голосу не слышен, выше +1.5 — громче голоса: оба ошибки, рендер не начнётся."""
    import numpy as np
    SR = reel.SR
    sx = np.zeros(int(4 * SR), np.float32)
    sx[int(0.5 * SR):int(0.6 * SR)] = 10 ** (-30 / 20)          # на −25 дБ к голосу −5
    sx[int(2.0 * SR):int(2.1 * SR)] = 10 ** (-2 / 20)           # на +3 дБ к голосу
    plan = [dict(name="swoosh", role="whoosh", t0=0.5, peak=0.55, rate=1.0, soft=True, gain_db=0.0),
            dict(name="oof", role="meme", t0=2.0, peak=2.05, rate=1.0, soft=False, gain_db=0.0)]
    out, err, warn = reel.sound_levels(plan, sx, -5.0)
    assert len(err) == 2 and {o.get("flag") for o in out} == {"inaudible", "loud"}


def test_meme_on_word_is_mixed_as_impact(tmp_path):
    """Мем-звук громок (−3) только в паузе; на слове он заглушил бы слово — ставится уровнем удара (−8)."""
    shots = [dict(t0=0.0)]
    ev = [dict(kind="sfx", name="oof", t=1.0, align="peak"), dict(kind="sfx", name="oof", t=4.0, align="peak")]
    r = reel.mix_audio(str(tmp_path / "m.wav"), 6.0, shots, ev, {}, False, None, words=[dict(start=0.8, end=1.3)])
    lv = {x["peak"]: x for x in r["sounds"]}
    assert lv[1.0]["role"] == "impact" and abs(lv[1.0]["vs_voice_db"] - reel.ROLE_DB["impact"]) < 0.6
    assert lv[4.0]["role"] == "meme" and abs(lv[4.0]["vs_voice_db"] - reel.ROLE_DB["meme"]) < 0.6
    assert any("мем-звук на слове" in w for w in r["warnings"])


def test_hard_punch_jumps_holds_and_cuts_back():
    """25.10: удар-наезд склейкой — без разгона: кадр до слова 1.0, кадр на слове уже 1.22, после hold — снова 1.0."""
    s = dict(t0=0.0, t1=3.0)
    ev = [dict(kind="punch", t=1.0, style="cut", amt=0.22, hold=0.45)]
    assert reel.punch_at(ev, s, 0.99) == 1.0
    assert abs(reel.punch_at(ev, s, 1.0) - 1.22) < 1e-9 and abs(reel.punch_at(ev, s, 1.44) - 1.22) < 1e-9
    assert reel.punch_at(ev, s, 1.46) == 1.0
    soft = [dict(kind="punch", t=1.0, amt=0.14)]
    assert 1.0 < reel.punch_at(soft, s, 1.03) < 1.14             # обычный наезд — плавно


def test_hard_punch_zooms_to_its_focus():
    """Удар-наезд с focus тянется к своей точке и только пока держится."""
    s = dict(t0=0.0, t1=3.0)
    ev = [dict(kind="punch", t=1.0, style="cut", amt=0.22, hold=0.45, focus=[765, 700])]
    assert reel.punch_focus(ev, s, 1.2) == [765, 700]
    assert reel.punch_focus(ev, s, 0.9) is None and reel.punch_focus(ev, s, 1.5) is None


def test_dead_pause_after_hook_is_an_error():
    """Ночь 25.10: голос хука кончился на 0.80, следующая фраза ждала пика riser до 1.72 — 0.9 с пустоты в начале."""
    times = [dict(start=0.0, end=0.32), dict(start=0.36, end=0.40), dict(start=0.48, end=0.80), dict(start=1.72, end=1.80)]
    beats = [dict(fx=[dict(kind="sfx", name="riser", at=0, align="start")]), dict()]
    err = reel_rules.check_hook_gap(times, [(0, 3), (3, 4)], beats)
    assert err and '"dt": -0.57' in err[0]
    times[3] = dict(start=1.15, end=1.25)
    assert reel_rules.check_hook_gap(times, [(0, 3), (3, 4)], beats) == []


def test_montage_like_sample_doll_at_end_drawings_accents():
    """25.10, образец эп.02 v9: кукла только в конце, рисунков ≥ 6 и один свой, акцентов ≥ 4 на 10 с и ≥ 5 видов."""
    spec = {"passport": {"standard": 14}, "sources": {f"f{i}": {"frame": f"gen/g{i}.png" if i == 1 else f"../e/{i}.png"}
                                                      for i in range(1, 7)}}
    total = 30.0
    shots = [dict(t0=i * 3.0, t1=i * 3.0 + 3.0, src=f"f{i % 6 + 1}") for i in range(8)] + \
            [dict(t0=24.0, t1=27.0, kind="doll"), dict(t0=27.0, t1=30.0, kind="doll")]
    shots[1]["zoom_in"] = 0.1; shots[2]["whip"] = [-500, 0]; shots[0]["anim"] = "x"
    kinds = ["punch", "shake", "spot", "circle", "arrow", "write", "punch", "spot", "shake"]
    events = [dict(kind=k, t=1.0 + i * 2.5) for i, k in enumerate(kinds)]
    assert reel_rules.check_montage(spec, shots, events, total) == []
    early = shots[:3] + [dict(t0=9.0, t1=12.0, kind="doll")] + shots[4:]
    assert any("кукла" in e for e in reel_rules.check_montage(spec, early, events, total))
    few = [dict(s, src="f1") if s.get("src") in ("f5", "f6") else s for s in shots]
    assert any("рисунков" in e for e in reel_rules.check_montage(spec, few, events, total))
    assert any("акцентов" in e for e in reel_rules.check_montage(spec, shots, events[:3], total))
    assert reel_rules.check_montage({"passport": {"standard": 13}}, early, [], total) == []   # старые — своими правилами


def test_whooshes_not_back_to_back():
    """26.10, владелец: «не супер часто свуши, тук-тук-тук» — переходные свисты не ближе 1.5 с друг к другу, свист новой
    картинки важнее свиста того же рисунка ближе; склейка без свиста из-за этого не считается проваленной."""
    assert reel_rules.WHOOSH_GAP == 1.5
    shots = [dict(t0=0.0, src="f1"), dict(t0=0.8, src="f1"), dict(t0=1.6, src="f2"), dict(t0=2.4, src="f2"),
             dict(t0=3.2, src="f3"), dict(t0=4.0, src="f3"), dict(t0=6.0, src="f3")]
    plan = reel.sound_plan(shots, [])
    wh = sorted(p["peak"] for p in plan if p["name"] in reel_rules.WHOOSHES)
    assert all(b - a >= reel_rules.WHOOSH_GAP for a, b in zip(wh, wh[1:]))
    assert 1.6 in wh and 3.2 in wh and 6.0 in wh             # новые картинки и одинокая склейка — со свистом
    assert reel_rules.check_whoosh_gap(plan) == []
    assert reel_rules.check_cut_sounds(plan, shots) == []
    hand = [dict(name="swoosh", peak=1.0), dict(name="fast_whoosh", peak=1.9)]
    assert reel_rules.check_whoosh_gap(hand)


def test_spots_only_on_key_word_and_not_in_a_row():
    """26.10, владелец: «чуть меньше затемнений… в ненужных местах не надо зря затемнять» — прожектор только на ключевом
    слове фразы и не чаще раза в 5 с."""
    spec = {"passport": {"standard": 15}, "beats": [
        dict(text="Дело висит, а ты *устаёшь*.", fx=[dict(kind="spot", at=4)]),
        dict(text="Это как стакан на *руке*.", fx=[dict(kind="spot", at=2)])]}
    errs = reel_rules.check_spots(spec, [dict(kind="spot", t=1.0), dict(kind="spot", t=3.0)])
    assert any("«стакан»" in e for e in errs) and any("ближе" in e for e in errs)
    assert not any("«устаёшь" in e for e in errs)
    assert reel_rules.check_spots(dict(spec, passport={"standard": 14}), []) == []   # готовые рилсы 25.10 не трогаем


def test_mindful_accents_why_and_rare_circles():
    """26.10, владелец: «кружочки на каждом ненужном и нужном месте… осознанность включи вообще везде» — у каждого
    выделения есть причина, кругов не больше двух на рилс и не ближе 8 с, только на ключевом слове."""
    why = "показать, что именно этот предмет — ловушка"
    spec = {"passport": {"standard": 16}, "beats": [
        dict(text="Хотел помыть *полы*.", fx=[dict(kind="punch", at=2, why=why)], shots=[]),
        dict(text="И пошёл за *тряпкой*.", fx=[dict(kind="circle", at=3, why=why)], shots=[dict(at=0, zoom_in=0.1)]),
        dict(text="А потом полил *цветы*.", fx=[dict(kind="circle", at=1), dict(kind="spot", at=3, why=why),
                                             dict(kind="shake", at=3, why=why)], shots=[])]}
    ev = [dict(kind="circle", t=3.0), dict(kind="circle", t=6.0), dict(kind="circle", t=20.0)]
    errs = reel_rules.check_mindful(spec, ev)
    assert any("без \"why\"" in e and "circle" in e for e in errs)            # круг без причины
    assert any("вход наездом" in e for e in errs)                            # вход наездом без причины
    assert any("«потом»" in e for e in errs)                                 # круг не на ключевом слове
    assert any("выделений 3" in e for e in errs) and any("круг и затемнение" in e for e in errs)
    assert any("кругов 3" in e for e in errs) and any("ближе 8.0" in e for e in errs)
    assert not any("фраза 0" in e for e in errs)                              # удар с причиной — годен
    assert reel_rules.check_mindful(dict(spec, passport={"standard": 15}), ev) == []
