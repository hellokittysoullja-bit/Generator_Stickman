"""План рилса 107 по голосу: shots.json и sound.json из voice/words.json (склейки — на начале слов).
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
    ("s01", "hook_pay", 0.0, False, "ХУК с 0 с: телефон в руке крупно, палец жмёт зелёную «Оплатить», из экрана вылетают коробки прямо в камеру. "
                                    "Надпись «КУПИЛ НА ЭМОЦИЯХ» с 0 с."),
    ("s02", "hook_pile", 2, False, "«на эмоциях»: коробки сыплются на Диму в комнате, гора по грудь; на «эмоциях» кот выныривает сверху горы."),
    ("s03", "month", 4, True, "«За месяц я сэкономил»: настенный календарь, дни месяца зачёркиваются, Дима рядом довольный, кот на полу."),
    ("s04", "counter", 8, False, "«двенадцать тысяч»: на бумаге выскакивает счётчик «+12 000 ₽», монетки и искры, кот прыгает."),
    ("s05", "bored", 10, True, "«Раньше скучно»: Дима на диване зевает, листает телефон, кот спит рядом."),
    ("s06", "cart_fill", 13, False, "«и корзина полная»: телефон крупно, корзина, товары падают в неё один за другим, счётчик на значке растёт."),
    ("s07", "courier", 15, True, "«Курьер»: прихожая, звонок в дверь (дзынь), дверь открывается, курьер с коробкой."),
    ("s08", "forgot", 19, False, "«а я уже забыл, что заказал»: Дима держит коробку, над ним «?», кот обнюхивает коробку."),
    ("s09", "fridge", 22, True, "«Конец месяца»: Дима открывает холодильник, внутри пусто, одна лампочка, муха."),
    ("s10", "balance", 26, False, "«на еду не хватает»: телефон крупно, банк: баланс «37 ₽» красным, экран дрожит."),
    ("s11", "cta_kot", 29, True, "ПРИЗЫВ: «Напиши «КОТ»»: поле комментария, печатное жёлтое «КОТ» крупно; кот прыгает к Диме."),
    ("s12", "pause", 32, False, "«между хочу и оплатить появилась пауза»: две кнопки «ХОЧУ» и «ОПЛАТИТЬ», на «пауза» кот лапой ставит между ними знак паузы."),
    ("s13", "self_pause", 38, False, "«которую ты сам себе поставишь»: Дима за столом сам жмёт паузу в телефоне, кот кивает рядом."),
    ("s14", "changed", 43, True, "«Вот что я поменял»: Дима за столом, лампочка-идея, кот рядом; маленькая надпись «ВОТ ЧТО Я ПОМЕНЯЛ»."),
    ("s15", "to_cart", 47, False, "«Всё, что хочу купить»: телефон крупно, палец кладёт кроссовки, наушники и игру в корзину."),
    ("s16", "wait_day", 51, True, "«кладу в корзину и жду сутки»: корзина с замком, таймер «24 ч» обходит круг, кот сторожит."),
    ("s17", "morning", 57, True, "«Половину утром удаляю сам»: утро, Дима с телефоном свайпом удаляет товары из корзины, кот доволен; надпись «+12 000 ₽»."),
    ("s18", "loop", None, True, "ПЕТЛЯ: кадр хука — палец над «Оплатить»."),
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
    spec = {"_": "Рилс 107 «Покупки на эмоциях» (формат 4, история кодом, один голос: Дима от первого лица, male2). "
                 "План пересчитывает plan.py по voice/words.json. Одна группа ext_a (s107.py).",
            "fps": 30, "size": [1080, 1920], "pad": 0.2, "end": END,
            "title": {"text": "КУПИЛ НА\nЭМОЦИЯХ", "module": "common/big_title.py", "t_in": 0.0, "t_out": T["month"],
                      "hits": [0, 1, 3], "why": "надпись хука с кадра 0, тряска на «Перестань», «покупать», «эмоциях»"},
            "label": {"text": "ВОТ ЧТО Я ПОМЕНЯЛ", "t_in": W(43), "t_out": W(47), "why": "только фраза 6 (решение)"},
            "label2": {"text": "+12 000 ₽", "t_in": W(58), "t_out": round(T["loop"] - 0.12, 3), "why": "итог, фраза 7"},
            "kot": {"text": "КОТ", "t_in": W(32), "t_out": W(43), "why": "кодовое слово держится до конца призыва"},
            "shots": shots}
    json.dump(spec, open(os.path.join(HERE, "shots.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    sfx = [
        ("fast_whoosh", "удар хука: влёт камеры к телефону", {"t": 0.1}),
        ("riser", "нарастание хука", {"t": 0.2}),
        ("keyboard_soft", "палец жмёт «Оплатить»", {"word": 0, "offset": 0.12}),
        ("shock", "из экрана вылетают коробки", {"word": 1, "offset": 0.05}),
        ("swoosh", "первая склейка: коробки сыплются на Диму", {"t": T["hook_pile"]}),
        ("oof", "гора коробок накрыла Диму", {"word": 3, "offset": 0.0}),
        ("level_up", "кот выныривает сверху горы", {"word": 3, "offset": 0.45}),
        ("swoosh_deep", "хлёст к календарю", {"t": T["month"]}),
        ("typing", "дни зачёркиваются", {"word": 5, "gain_db": -4}),
        ("swoosh", "склейка к счётчику", {"t": T["counter"]}),
        ("level_up", "«двенадцать»: +12 000 ₽", {"word": 8, "offset": 0.05}),
        ("keyboard_soft", "«тысяч»: монетки звякают", {"word": 9, "offset": 0.05}),
        ("swoosh_deep", "хлёст к дивану", {"t": T["bored"]}),
        ("oof", "«скучно»: зевок", {"word": 11, "offset": 0.05, "gain_db": -3}),
        ("swoosh", "склейка к корзине", {"t": T["cart_fill"]}),
        ("keyboard_soft", "товар падает в корзину", {"word": 13, "offset": 0.1}),
        ("keyboard_soft", "ещё товар", {"word": 14, "offset": 0.0, "gain_db": 1}),
        ("swoosh_deep", "хлёст к двери", {"t": T["courier"]}),
        ("level_up", "дзынь: звонок в дверь", {"word": 15, "offset": 0.1}),
        ("fast_whoosh", "дверь открывается", {"word": 16}),
        ("swoosh", "склейка к Диме с коробкой", {"t": T["forgot"]}),
        ("fast_glitch", "«забыл»: знак вопроса", {"word": 19, "offset": 0.05, "gain_db": -3}),
        ("keyboard_soft", "«заказал»: кот трогает коробку", {"word": 21}),
        ("swoosh_deep", "хлёст к холодильнику", {"t": T["fridge"]}),
        ("fast_whoosh", "холодильник открывается", {"word": 23}),
        ("oof", "внутри пусто", {"word": 24, "offset": 0.1}),
        ("swoosh", "склейка к банку", {"t": T["balance"]}),
        ("shock", "«хватает»: баланс 37 ₽", {"word": 27, "offset": 0.0}),
        ("swoosh_deep", "хлёст к призыву", {"t": T["cta_kot"]}),
        ("typing", "печатается КОТ", {"word": 30, "offset": -0.05, "gain_db": -4}),
        ("level_up", "«КОТ» напечатан", {"word": 30, "offset": 0.2}),
        ("fast_whoosh", "кот прыгает к Диме", {"word": 31}),
        ("swoosh", "склейка к двум кнопкам", {"t": T["pause"]}),
        ("keyboard_soft", "«хочу»: кнопка", {"word": 33}),
        ("keyboard_soft", "«оплатить»: кнопка", {"word": 35, "gain_db": 1}),
        ("shock", "«пауза»: кот ставит паузу лапой", {"word": 37, "offset": 0.0}),
        ("swoosh", "склейка к Диме за столом", {"t": T["self_pause"]}),
        ("keyboard_soft", "«сам»: жмёт паузу", {"word": 40}),
        ("level_up", "«поставишь»: пауза стоит", {"word": 42, "offset": 0.1}),
        ("swoosh_deep", "хлёст к решению, надпись", {"t": T["changed"]}),
        ("level_up", "«Вот»: лампочка", {"word": 43, "offset": 0.15}),
        ("keyboard_soft", "«поменял»: кот садится рядом", {"word": 46}),
        ("swoosh", "склейка к телефону", {"t": T["to_cart"]}),
        ("fast_whoosh", "товар летит в корзину", {"word": 49}),
        ("keyboard_soft", "«купить»: ещё товар", {"word": 50}),
        ("swoosh_deep", "хлёст к таймеру", {"t": T["wait_day"]}),
        ("typing", "таймер 24 ч идёт", {"word": 53, "gain_db": -5}),
        ("level_up", "«сутки»: круг замкнулся", {"word": 56, "offset": 0.1}),
        ("swoosh", "хлёст к утру", {"t": T["morning"]}),
        ("fast_whoosh", "свайп: товар удалён", {"word": 58}),
        ("fast_whoosh", "свайп: ещё товар", {"word": 59, "gain_db": -2}),
        ("level_up", "«сам»: +12 000 ₽", {"word": 60}),
        ("swoosh", "хлёст в петлю к хуку", {"t": T["loop"]}),
    ]
    out = []
    for n, why, at in sfx:
        e = {"name": n, "why": why}
        e.update(at)
        if "word" in at:
            e["word_text"] = WORDS[at["word"]]["word"]
        out.append(e)
    json.dump({"_": "Звуки рилса 107 (plan.py). t — пик звука; word — индекс voice/words.json. Только assets/sfx/reels/library.json.",
               "keys": [1, 3, 8, 9, 11, 14, 15, 19, 26, 28, 30, 37, 40, 46, 56, 59], "sfx": out},
              open(os.path.join(HERE, "sound.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    for s in shots:
        print(s["id"], s["scene"], s["t0"], s["t1"], s["dur"])
    print("end", END)


if __name__ == "__main__":
    main()
