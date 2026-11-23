"""План рилса 110 по голосу: shots.json и sound.json из voice/words.json (склейки — на начале слов).
python3 plan.py — пересчитать после новой озвучки (сцены берут время только из shots.json и words.json)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = json.load(open(os.path.join(HERE, "voice", "words.json"), encoding="utf8"))


def W(i):
    return round(WORDS[i]["start"], 3)


def WE(i):
    return round(WORDS[i]["end"], 3)


END = round(WE(len(WORDS) - 1) + 0.95, 2)

# (id, сцена, начало: слово или секунды, хлёст, что в кадре)
P = [
    ("s01", "hook_ring", 0.0, False, "ХУК с 0 с: будильник звенит на тумбе, Дима в кровати открывает глаза, кот на подушке. Надпись «С ПЕРВОГО РАЗА» с 0 с."),
    ("s02", "hook_up", 2, False, "«встаю с первого будильника»: Дима откидывает одеяло и встаёт у кровати, кот на подушке."),
    ("s03", "snooze", 6, True, "«А раньше переставлял его пять раз»: рука жмёт «отложить», счётчик ×5."),
    ("s04", "late", 12, True, "«опаздывал на пары»: бег к аудитории, дверь закрыта."),
    ("s05", "doze", 15, True, "«а потом весь день был разбитым»: Дима клюёт носом над тетрадью."),
    ("s06", "changed", 21, True, "«Вот что я поменял»: спальня, лампочка-идея, кот; надпись «ВОТ ЧТО Я ПОМЕНЯЛ»."),
    ("s07", "by_door", 25, True, "«Будильник стоит у двери, а не у кровати»: будильник на тумбе у двери, крестик у кровати."),
    ("s08", "walk_off", 33, False, "«Чтобы выключить, приходится встать»: Дима идёт к двери и выключает будильник."),
    ("s09", "curtains", 37, True, "«Шторы открыты с вечера»: вечер, Дима раздвигает шторы."),
    ("s10", "sun", 41, False, "«и свет будит вместе со звонком»: утро, солнце заливает комнату, будильник звенит."),
    ("s11", "cat_pillow", 47, True, "«А кот садится на подушку»: кот запрыгивает на подушку."),
    ("s12", "no_room", 52, False, "«и обратно лечь уже некуда»: Дима поворачивается к кровати, кот развалился на подушке."),
    ("s13", "cta_kot", 57, True, "ПРИЗЫВ: печатное жёлтое «КОТ» крупно с первого кадра, кот прыгает к Диме."),
    ("s14", "first_try", 60, False, "«чтобы тоже вставать с первого раза»: Дима встаёт по звонку, бодрый."),
    ("s15", "on_time", 66, True, "«и успевать к первой паре»: Дима заходит в аудиторию, дверь открыта."),
    ("s16", "coffee", 71, True, "«Сегодня в восемь я уже пил кофе»: кухня, часы 8:00, кружка кофе; надпись «8:00 И КОФЕ»."),
    ("s17", "bus_stop", 76, False, "«а не бежал на остановку»: Дима с кофе у окна, за окном люди бегут к автобусу."),
    ("s18", "loop", None, True, "ПЕТЛЯ: кадр хука — будильник начинает звенеть."),
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
    spec = {"_": "Рилс 110 «Первый будильник» (формат 4, история кодом, один голос: Дима от первого лица, male2). "
                 "План пересчитывает plan.py по voice/words.json. Одна группа ext_a (s110.py).",
            "fps": 30, "size": [1080, 1920], "pad": 0.2, "end": END,
            "title": {"text": "С ПЕРВОГО\nРАЗА", "module": "common/big_title.py", "t_in": 0.0, "t_out": T["snooze"],
                      "hits": [1, 2, 5], "why": "надпись хука с кадра 0, тряска на «наконец-то», «встаю», «будильника»"},
            "label": {"text": "ВОТ ЧТО Я ПОМЕНЯЛ", "t_in": W(21), "t_out": W(57), "why": "фразы 3–6: решение"},
            "label2": {"text": "8:00 И КОФЕ", "t_in": W(73), "t_out": round(T["loop"] - 0.12, 3), "why": "итог, последняя фраза"},
            "kot": {"text": "КОТ", "t_in": W(59), "t_out": W(71), "why": "кодовое слово держится до конца призыва"},
            "shots": shots}
    json.dump(spec, open(os.path.join(HERE, "shots.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    sfx = [
        ("fast_whoosh", "удар хука: влёт камеры", {"t": 0.1}),
        ("riser", "нарастание хука: будильник звенит", {"t": 0.2}),
        ("typing", "звон будильника", {"t": 0.3, "gain_db": -3}),
        ("keyboard_soft", "глаза открываются", {"word": 1, "offset": 0.1}),
        ("swoosh", "первая склейка: одеяло летит", {"t": T["hook_up"]}),
        ("fast_whoosh", "одеяло откинуто", {"word": 3}),
        ("level_up", "«будильника»: встал", {"word": 5, "offset": 0.2}),
        ("swoosh_deep", "хлёст к руке на кнопке", {"t": T["snooze"]}),
        ("keyboard_soft", "жмёт «отложить»", {"word": 8, "offset": 0.1}),
        ("keyboard_soft", "ещё раз", {"word": 9}),
        ("shock", "«пять раз»: ×5", {"word": 10}),
        ("swoosh", "хлёст к бегу", {"t": T["late"]}),
        ("fast_whoosh", "бежит по коридору", {"word": 13}),
        ("oof", "дверь закрыта", {"word": 14, "offset": 0.1}),
        ("swoosh_deep", "хлёст к парте", {"t": T["doze"]}),
        ("oof", "«разбитым»: клюёт носом", {"word": 20}),
        ("swoosh", "хлёст к решению", {"t": T["changed"]}),
        ("level_up", "«Вот»: лампочка", {"word": 21, "offset": 0.15}),
        ("swoosh_deep", "хлёст: будильник у двери", {"t": T["by_door"]}),
        ("keyboard_soft", "будильник встаёт на тумбу", {"word": 26}),
        ("shock", "«не у кровати»: крестик", {"word": 32}),
        ("swoosh", "склейка: идёт к двери", {"t": T["walk_off"]}),
        ("keyboard_soft", "жмёт кнопку", {"word": 36}),
        ("swoosh_deep", "хлёст к вечеру", {"t": T["curtains"]}),
        ("fast_whoosh", "шторы раздвигаются", {"word": 38}),
        ("swoosh", "склейка к утру", {"t": T["sun"]}),
        ("level_up", "«свет»: солнце", {"word": 42}),
        ("typing", "звон со светом", {"word": 46, "gain_db": -4}),
        ("swoosh_deep", "хлёст: кот прыгает", {"t": T["cat_pillow"]}),
        ("fast_whoosh", "кот в прыжке", {"word": 49}),
        ("keyboard_soft", "кот плюхается на подушку", {"word": 51}),
        ("swoosh", "склейка: Дима у кровати", {"t": T["no_room"]}),
        ("oof", "«некуда»", {"word": 56}),
        ("swoosh_deep", "хлёст к призыву", {"t": T["cta_kot"]}),
        ("typing", "печатается КОТ", {"t": T["cta_kot"] + 0.1, "gain_db": -4}),
        ("level_up", "«КОТ» напечатан", {"word": 59, "offset": 0.05}),
        ("swoosh", "склейка: встаёт с первого раза", {"t": T["first_try"]}),
        ("fast_whoosh", "встаёт", {"word": 64}),
        ("swoosh_deep", "хлёст к аудитории", {"t": T["on_time"]}),
        ("level_up", "«первой паре»: вовремя", {"word": 69}),
        ("swoosh", "хлёст на кухню", {"t": T["coffee"]}),
        ("keyboard_soft", "кружка ставится", {"word": 73, "offset": 0.1}),
        ("level_up", "«кофе»", {"word": 77}),
        ("fast_whoosh", "автобус за окном", {"word": 80}),
        ("swoosh", "хлёст в петлю к хуку", {"t": T["loop"]}),
    ]
    out = []
    for n, why, at in sfx:
        e = {"name": n, "why": why}
        e.update(at)
        if "word" in at:
            e["word_text"] = WORDS[at["word"]]["word"]
        out.append(e)
    json.dump({"_": "Звуки рилса 110 (plan.py). t — пик звука; word — индекс voice/words.json. Только assets/sfx/reels/library.json.",
               "keys": [1, 2, 5, 10, 14, 20, 21, 26, 32, 36, 38, 42, 48, 51, 56, 59, 65, 69, 73, 77, 82], "sfx": out},
              open(os.path.join(HERE, "sound.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    for s in shots:
        print(s["id"], s["scene"], s["t0"], s["t1"], s["dur"])
    print("end", END)


if __name__ == "__main__":
    main()
