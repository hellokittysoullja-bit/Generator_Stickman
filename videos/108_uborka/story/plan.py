"""План рилса 108 по голосу: shots.json и sound.json из voice/words.json (склейки — на начале слов).
python3 plan.py — пересчитать после новой озвучки (сцены берут время только из shots.json и words.json)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = json.load(open(os.path.join(HERE, "voice", "words.json"), encoding="utf8"))


def W(i):
    return round(WORDS[i]["start"], 3)


def WE(i):
    return round(WORDS[i]["end"], 3)


END = round(WE(len(WORDS) - 1) + 0.55, 2)

# (id, сцена, начало: слово или секунды, хлёст, что в кадре)
P = [
    ("s01", "hook_grow", 0.0, False, "ХУК с 0 с: прихожая, на стуле гора одежды растёт вещь за вещью до потолка, камера едет вверх. Надпись «ГОРА НА СТУЛЕ» с 0 с."),
    ("s02", "hook_fall", 2, False, "«всю квартиру»: гора рушится на пол, Дима отскакивает; на «квартиру» кот выныривает сверху кучи."),
    ("s03", "ten_min", 4, True, "«Десять минут в день»: таймер «10:00» на бумаге, кот рядом."),
    ("s04", "clean", 8, False, "«и у меня чисто»: та же прихожая, стул пустой, Дима довольный, искры чистоты, кот на стуле."),
    ("s05", "weekend", 12, True, "«Ждал выходного на генеральную»: календарь, суббота обведена, дни зачёркиваются, а гора на стуле рядом растёт."),
    ("s06", "wardrobe", 16, True, "«Начинал с одного шкафа»: открытый шкаф, Дима выкидывает вещи на пол, вещи летят."),
    ("s07", "quit", 20, False, "«и бросал на середине»: Дима сидит посреди вываленной одежды, лицо уставшее, шкаф полупустой, кот на куче."),
    ("s08", "guests_bell", 24, True, "«А гости заставали»: звонок в дверь, дверь открывается, двое гостей в проёме."),
    ("s09", "guests_pile", 27, False, "«гору на стуле»: Дима раскинул руки и заслоняет стул с горой, гости смотрят, «!»."),
    ("s10", "changed", 30, True, "«Вот что я поменял»: Дима в прихожей, лампочка-идея, кот; маленькая надпись «ВОТ ЧТО Я ПОМЕНЯЛ»."),
    ("s11", "timer", 34, True, "«Таймер на десять минут»: телефон крупно, таймер 10:00 запускается и идёт."),
    ("s12", "tidy", 38, True, "«убираю только то, что вижу»: прихожая, вещи со стула по одной улетают в шкаф и в корзину, таймер в углу идёт."),
    ("s13", "cta_kot", 43, True, "ПРИЗЫВ: «Напиши слово «КОТ»»: печатное жёлтое «КОТ» крупно с первого кадра, кот прыгает к Диме."),
    ("s14", "last_shirt", 46, False, "«чтобы самому поменять это»: Дима сам кладёт последнюю футболку в корзину, кот смотрит."),
    ("s15", "forever", 51, False, "«в своей жизни навсегда»: чистая прихожая, Дима гладит кота на чистом стуле, сердечко."),
    ("s16", "guests_in", 54, True, "«Вчера гости пришли»: дверь распахивается, гости заходят без предупреждения."),
    ("s17", "guests_see", 58, False, "«без предупреждения»: гости видят чистый стул, на нём кот."),
    ("s18", "no_shame", 59, True, "«и мне было не стыдно»: Дима улыбается рядом с чистым стулом и котом, гости машут; надпись «БЕЗ СТЫДА»."),
    ("s19", "loop", None, True, "ПЕТЛЯ: кадр хука — стул, гора начинает расти."),
]


def main():
    shots = []
    for sid, scene, st, wh, what in P:
        if st is None:
            t0 = round(WE(len(WORDS) - 1) + 0.06, 3)
        elif isinstance(st, float):
            t0 = st
        else:
            t0 = W(st)
        shots.append(dict(id=sid, scene=scene, t0=t0, what=what, group="ext_a", **({"whip": True} if wh else {})))
    for a, b in zip(shots, shots[1:]):
        a["t1"] = b["t0"]
    shots[-1]["t1"] = END
    shots[0]["hook"] = True
    shots[0]["hit_word"] = 0
    for s in shots:
        s["dur"] = round(s["t1"] - s["t0"], 2)
    T = {s["scene"]: s["t0"] for s in shots}
    spec = {"_": "Рилс 108 «Уборка» (формат 4, история кодом, один голос: Дима от первого лица, male2). "
                 "План пересчитывает plan.py по voice/words.json. Одна группа ext_a (s108.py).",
            "fps": 30, "size": [1080, 1920], "pad": 0.2, "end": END,
            "title": {"text": "ГОРА\nНА СТУЛЕ", "module": "common/big_title.py", "t_in": 0.0, "t_out": T["ten_min"],
                      "hits": [0, 1, 3], "why": "надпись хука с кадра 0, тряска на «Перестань», «убирать», «квартиру»"},
            "label": {"text": "ВОТ ЧТО Я ПОМЕНЯЛ", "t_in": W(30), "t_out": W(34), "why": "только фраза «Вот что я поменял»"},
            "label2": {"text": "БЕЗ СТЫДА", "t_in": W(60), "t_out": round(T["loop"] - 0.12, 3), "why": "итог, последняя фраза"},
            "kot": {"text": "КОТ", "t_in": W(45), "t_out": W(54), "why": "кодовое слово держится до конца призыва"},
            "shots": shots}
    json.dump(spec, open(os.path.join(HERE, "shots.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    sfx = [
        ("fast_whoosh", "удар хука: влёт камеры", {"t": 0.1}),
        ("riser", "нарастание хука: гора растёт", {"t": 0.2}),
        ("keyboard_soft", "вещь шлёпается на гору", {"word": 0, "offset": 0.25, "gain_db": -2}),
        ("keyboard_soft", "ещё вещь", {"word": 1, "offset": 0.05}),
        ("swoosh", "первая склейка: гора рушится", {"t": T["hook_fall"]}),
        ("shock", "«квартиру»: гора падает на пол", {"word": 3}),
        ("level_up", "кот выныривает из кучи", {"word": 3, "offset": 0.4}),
        ("swoosh_deep", "хлёст к таймеру", {"t": T["ten_min"]}),
        ("typing", "таймер тикает", {"word": 5, "gain_db": -5}),
        ("swoosh", "склейка к чистой прихожей", {"t": T["clean"]}),
        ("level_up", "«чисто»: искры", {"word": 11, "offset": 0.05}),
        ("swoosh_deep", "хлёст к календарю", {"t": T["weekend"]}),
        ("keyboard_soft", "суббота обведена", {"word": 13}),
        ("typing", "дни зачёркиваются", {"word": 14, "gain_db": -4}),
        ("oof", "«генеральную»: гора выросла", {"word": 15, "offset": 0.1, "gain_db": -2}),
        ("swoosh", "хлёст к шкафу", {"t": T["wardrobe"]}),
        ("fast_whoosh", "вещи летят из шкафа", {"word": 18}),
        ("fast_whoosh", "ещё вещи", {"word": 19, "gain_db": -2}),
        ("swoosh", "склейка: сидит посреди вещей", {"t": T["quit"]}),
        ("oof", "«бросал»: уставший вздох", {"word": 21, "offset": 0.05}),
        ("keyboard_soft", "кот прыгает на кучу", {"word": 23}),
        ("swoosh_deep", "хлёст к двери", {"t": T["guests_bell"]}),
        ("level_up", "дзынь: звонок в дверь", {"word": 25, "offset": -0.05}),
        ("fast_whoosh", "дверь открывается", {"word": 26}),
        ("swoosh", "склейка: Дима заслоняет стул", {"t": T["guests_pile"]}),
        ("shock", "«стуле»: гости видят гору", {"word": 29}),
        ("swoosh_deep", "хлёст к решению, надпись", {"t": T["changed"]}),
        ("level_up", "«Вот»: лампочка", {"word": 30, "offset": 0.15}),
        ("keyboard_soft", "«поменял»: кот садится рядом", {"word": 33}),
        ("swoosh", "хлёст к таймеру", {"t": T["timer"]}),
        ("keyboard_soft", "палец жмёт «старт»", {"word": 35}),
        ("typing", "таймер идёт", {"word": 36, "offset": 0.2, "gain_db": -5}),
        ("swoosh", "хлёст к уборке", {"t": T["tidy"]}),
        ("fast_whoosh", "вещь летит в шкаф", {"word": 39}),
        ("fast_whoosh", "вещь летит в корзину", {"word": 41, "gain_db": -2}),
        ("level_up", "«вижу»: стул чистый", {"word": 42, "offset": 0.1}),
        ("swoosh_deep", "хлёст к призыву", {"t": T["cta_kot"]}),
        ("typing", "печатается КОТ", {"t": T["cta_kot"] + 0.1, "gain_db": -4}),
        ("level_up", "«КОТ» напечатан", {"word": 45, "offset": 0.05}),
        ("fast_whoosh", "кот прыгает к Диме", {"t": T["cta_kot"] + 0.3}),
        ("swoosh", "склейка к последней футболке", {"t": T["last_shirt"]}),
        ("keyboard_soft", "футболка в корзине", {"word": 48, "offset": 0.1}),
        ("swoosh", "склейка к коту на стуле", {"t": T["forever"]}),
        ("level_up", "«навсегда»: сердечко", {"word": 53}),
        ("swoosh_deep", "хлёст к двери", {"t": T["guests_in"]}),
        ("fast_whoosh", "дверь распахивается", {"word": 55}),
        ("swoosh", "склейка: гости видят чистый стул", {"t": T["guests_see"]}),
        ("keyboard_soft", "кот на стуле машет хвостом", {"word": 58, "offset": 0.3}),
        ("swoosh", "хлёст к Диме", {"t": T["no_shame"]}),
        ("level_up", "«не стыдно»: БЕЗ СТЫДА", {"word": 62}),
        ("swoosh", "хлёст в петлю к хуку", {"t": T["loop"]}),
    ]
    out = []
    for n, why, at in sfx:
        e = {"name": n, "why": why}
        e.update(at)
        if "word" in at:
            e["word_text"] = WORDS[at["word"]]["word"]
        out.append(e)
    json.dump({"_": "Звуки рилса 108 (plan.py). t — пик звука; word — индекс voice/words.json. Только assets/sfx/reels/library.json.",
               "keys": [3, 5, 11, 13, 15, 19, 21, 27, 29, 36, 42, 45, 48, 53, 58, 62], "sfx": out},
              open(os.path.join(HERE, "sound.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    for s in shots:
        print(s["id"], s["scene"], s["t0"], s["t1"], s["dur"])
    print("end", END)


if __name__ == "__main__":
    main()
