#!/usr/bin/env python3
"""
hookscore.py — оценивает первую фразу рилса по пяти признакам, которые есть
у сильных хуков, сравнивает пачку хуков между собой и говорит, на какой приём
из базы Кирилла (hooks.json) похож каждый.

Что это: пять локальных эвристик, которые считаются по тексту прямо на твоём
компьютере. Они меряют то, что обычно есть у хуков, которые держат внимание:
длину, которую можно произнести за пару секунд, конкретику (число, имя,
сумму), ставку — что-то, что можно потерять, — главное слово в начале, а не
в конце, и зрителя, к которому фраза обращена.

Чего это НЕ делает: не предсказывает просмотры. Проверка оригинала на
англоязычных хуках показала, что эвристики хорошо отличают нормальный хук от
заведомо плохого и почти не отличают хит автора от его же проходного ролика.
Русская версия — тот же подход, перенесённый на русский язык, отдельно на
русской выборке она не калибровалась. Так что ловит она приветствия,
раскачку, хуки без конкретики и хуки, которые говорить пять секунд. Какой из
двух нормальных хуков полетит, не скажет никакой скрипт: это решают лицо,
монтаж, звук и то, кому Instagram покажет ролик. Верь графику удержания, а не
этой цифре.

Каждый признак — от 0 до 100, больше — лучше.

Запуск
  python3 hookscore.py hooks.txt                  # по хуку на строку, рейтинг
  python3 hookscore.py --hook "Два года назад я ушла из найма в монтаж."
  python3 hookscore.py hooks.txt --wpm 160        # если говоришь быстрее
  pbpaste | python3 hookscore.py -
  python3 hookscore.py hooks.txt --json

Хук — до 4 секунд вслух (10 слов при 140 сл/мин), тот же предел, что в
beats.py. Стоп-факторы — незаполненная заготовка [..] или {{..}} и обещание
результата зрителю: такой хук не выше 40. Код выхода 1, если у лучшего
хука меньше 50 (хука нет), иначе 0.
"""

import argparse
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(HERE, "hooks.json")
DEFAULT_WPM = 140                    # русская речь в кадре ≈ 2,3 слова в секунду
HOOK_SECONDS = 4.3                   # тот же предел, что HOOK_WINDOW в beats.py: 10 слов при 140 сл/мин
NO_HOOK = 50                         # ниже этого у лучшего варианта хука нет (и код выхода 1)

L = "A-Za-zА-Яа-яЁё"
WORD_RE = re.compile(rf"[0-9{L}₽$%][0-9{L}₽$%'’-]*")
NUMBER_RE = re.compile(
    r"\d+(?:\.\d+)?\s?"
    r"(?:%|₽|\$|к\b|k\b|тыс\w*|млн|млрд|руб\w*|р\.|x\b|х\b|раз\w*|сек\w*|мин\w*"
    r"|час\w*|дн\w*|день|недел\w*|месяц\w*|год\w*|лет)?",
    re.IGNORECASE)
HASHTAG_RE = re.compile(r"(?:^|\s)#\w+")
# Незаполненная заготовка: [результат] из шаблона или {{твоё число}} из сценария.
PLACEHOLDER_RE = re.compile(r"\[[^\]\n]+\]|\{\{[^}\n]*\}\}")

# Обещание результата зрителю. Текст перед проверкой приводится к «е» вместо «ё».
_METRIC = (r"(?:подписчик\w*|клиент\w*|просмотр\w*|заказ\w*|заяв\w*|охват\w*|лайк\w*"
           r"|продаж\w*|рубл\w*|₽|доход\w*|денег|деньги|миллион\w*|тысяч\w*"
           r"|\d+\s?(?:к|k|тыс\w*|млн)(?!\w))")
PROMISE_PATTERNS = [
    # «наберёшь», «гарантированно», «попадёшь в рек» — как раньше
    r"наберешь|гарантир\w*|100\s?% результат",
    # «получишь 500 подписчиков», «заработаешь 100 тысяч»
    r"(?<!\w)(?:получишь|получите|наберете|соберешь|соберете|заработаешь|заработаете|привлечешь"
    r"|привлечете|приведешь|будешь получать|будешь зарабатывать|выйдешь на)\s+(?:[^\s.!?]+\s+){0,3}?"
    + _METRIC,
    # «10 тысяч подписчиков за месяц» — если это не твой путь (нет «я/мы/мой», нет прошедшего)
    r"(?:^|(?<=[.!?…]\s))(?![^.!?\n]*(?<!\w)(?:я|мы|мне|меня|мой|моя|мои|мою|моего|моей|наш\w*"
    r"|набрал\w*|собрал\w*|получил\w*|вырос\w*|заработал\w*|привел\w*|пришл\w*|пришел)(?!\w))"
    r"[^.!?\n]*?(?<!\w)(?:\d[\d\s]*\s?(?:к|k|тыс\.?|тысяч\w*|млн|миллион\w*)?|[а-я]+\s+(?:тысяч\w*|миллион\w*)"
    r"|тысяч\w*|миллион\w*|сотн\w+)\s*(?:подписчик\w*|просмотр\w*|клиент\w*|заявок|заказ\w*|охват\w*)"
    r"\s+за\s+[^\s.!?]+",
    # «лучше, чем 99% людей»
    r"лучше,?\s+чем\s+(?:у\s+)?\d{2}(?:[.,]\d)?\s?%|лучше\s+\d{2}(?:[.,]\d)?\s?%"
    r"|(?<!\w)9\d(?:[.,]\d)?\s?%\s+(?:людей|блогеров|экспертов|мастеров|авторов|монтажеров)",
    # «залетишь в рекомендации», «взорвёшь охваты», «точно выстрелит»
    r"(?<!\w)(?:залет(?:ишь|ите|ит|ят)|попад(?:ешь|ете|ет|ут)|вылет(?:ишь|ите|ит)|выйд(?:ешь|ете|ет))"
    r"\s+в\s+(?:реки|рекомендации|рек|тренды|топ)(?!\w)"
    r"|(?<!\w)взорв\w*\s+(?:\w+\s+)?охват\w*|охват\w*\s+(?:взлетят|взлетит|вырастут|вырастет|взорвутся)"
    r"|(?<!\w)(?:точно|гарантированно|100\s?%)\s+(?:в\s+рек\w*|залетит|выстрелит|наберет|попадет|завирусится)"
    r"|(?<!\w)завирусишься|станешь\s+вирусн\w*",
    # «и ты вырастешь»
    r"(?<!\w)ты\s+(?:тоже\s+|точно\s+|сразу\s+)?(?:вырастешь|заработаешь|разбогатеешь|выйдешь на)(?!\w)",
]
PROMISE_RE = re.compile("|".join(f"(?:{p})" for p in PROMISE_PATTERNS), re.IGNORECASE | re.MULTILINE)


def fold(text):
    return text.replace("ё", "е").replace("Ё", "Е")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")

# Числа вслух. «Двести тысяч» так же конкретно, как «200 000».
# «Один» и «первый» нарочно нет: чаще это связка, а не количество.
SPOKEN_EXACT = {
    "ноль", "нуля", "нулём", "два", "две", "двух", "двум", "двумя", "три", "трёх",
    "трех", "трём", "тремя", "четыре", "четырёх", "четырех", "пять", "пяти", "пятью",
    "шесть", "шести", "семь", "семи", "восемь", "восьми", "девять", "девяти",
    "десять", "десяти", "одиннадцать", "двенадцать", "пятнадцать", "сорок", "сорока",
    "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят", "девяносто", "сто", "ста",
    "двести", "триста", "пятьсот", "полгода", "полчаса", "дважды", "трижды", "вдвое",
    "втрое", "дюжина", "лям", "ляма", "косарь", "косаря", "тыща", "тыщ",
}
SPOKEN_STEMS = ("двадцат", "тридцат", "тысяч", "миллион", "миллиард", "полтор",
                "половин", "сотн", "десятк")
# Деньги и метрики ниши: тоже то, что можно проверить.
MONEY_STEMS = ("рубл", "доллар", "бакс", "евро", "процент", "выручк", "прибыл",
               "зарплат", "доход", "аренд", "ипотек", "кредит", "подписчик",
               "просмотр", "охват", "клиент", "заказ", "заявк", "продаж")
MONEY_EXACT = {"руб", "чек", "чека", "чеком", "₽"}

# Слова, которые ставят что-то на кон. Без них фраза — просто утверждение.
STAKE_EXACT = {
    "не", "нет", "ни", "никто", "ничего", "никогда", "нельзя", "но", "до", "пока",
    "вместо", "без", "против", "кроме", "зря", "только", "уже", "ещё", "еще",
    "впервые", "бесплатно", "правда", "правду", "секрет", "ложь", "стоп", "хватит",
    "миф", "должен", "должна", "должны", "бросил", "бросила", "бросить", "чит-код",
    "забанили", "бан", "наконец", "ушла", "ушёл", "ушел", "бросила", "раньше", "теперь",
}
STAKE_STEMS = (
    "ошиб", "неправильн", "потер", "теря", "слил", "слива", "провал", "уволи",
    "удали", "убива", "убил", "замени", "заплат", "переплат", "сэконом", "запрет",
    "заблок", "худш", "ненавиж", "впуст", "обман", "врут", "вран", "скрыва", "скрыт",
    "украл", "укради", "проблем", "риск", "опасн", "предупре", "жале", "пожале",
    "сожале", "страш", "стыд", "кошмар", "разочар", "выгор", "штраф", "стоил",
    "отказ", "отпис", "нечестн", "перестан", "хуже", "сложнее",
)

# Открытия, которые тратят первую секунду впустую.
WEAK_OPENERS = [
    "так", "итак", "ну", "короче", "вообще", "вообщем", "окей", "ок", "ладно",
    "кстати", "просто", "наверное", "эээ", "ээ", "мм", "смотрите", "слушайте",
    "знаете", "привет", "всем", "здравствуйте", "приветствую", "друзья", "ребята",
    "ребят", "народ", "сегодня", "давайте", "я хочу", "хочу рассказать",
    "хочу поделиться", "в этом", "как вы", "многие из", "есть такая", "есть такой",
    "это видео", "это ролик", "у меня вопрос", "не знаю", "сейчас расскажу",
    "сейчас покажу", "вы знали", "дело в", "как известно", "всем известно",
]

YOU = {"ты", "тебя", "тебе", "тобой", "твой", "твоя", "твоё", "твое", "твои", "твоего",
       "твоей", "твоим", "твоих", "твою", "вы", "вас", "вам", "ваш", "ваша", "ваше",
       "ваши", "вашего", "вашей", "вами"}
FIRST_PERSON = {"я", "мне", "меня", "мной", "мой", "моя", "моё", "мое", "мои", "моего",
                "моей", "моим", "моих", "мою", "мы", "нас", "нам", "нами", "наш", "наша",
                "наше", "наши", "нашего", "нашей"}
NOT_VERBS = {"лишь", "мышь", "тишь", "глушь", "вишь"}
VERB_YOU_RE = re.compile(r"(?:ешь|ёшь|ишь)(?:ся)?$")
# Повелительное наклонение в начале фразы держит место не хуже числа.
IMPERATIVES = {
    "стоп", "хватит", "перестань", "укради", "сохрани", "забери", "скопируй", "удали",
    "попробуй", "смотри", "посмотри", "слушай", "прочитай", "сделай", "делай",
    "используй", "напиши", "пиши", "отправь", "возьми", "начни", "брось", "проверь",
    "замени", "запомни", "лови", "загни", "идём", "идем", "сними", "снимай", "забудь",
    "повтори", "представь", "давай", "не", "никогда", "всегда", "выкинь", "выброси",
    "открой", "включи", "выключи", "монтируй", "убери",
}

DEALBREAKERS = [
    (re.compile(r"(?i)(?:^|[,.!—]\s*)(?:стоп,?\s*)?(?:не листай|не пролистывай|не скролль|остановись"
                r"|подожди,? не|досмотри до конца|смотри до конца)"),
     "Начало с «не листай». Просить внимания — значит признать, что не заработал его."),
    (re.compile(r"(?i)\b(?:в этом (?:видео|ролике|рилсе)|в сегодняшнем (?:видео|ролике)"
                r"|сегодня (?:я |мы )?(?:расскажу|покажу|поговорим|разберём|разберем|хочу)"
                r"|хочу (?:вам )?(?:рассказать|поделиться)|давайте поговорим"
                r"|я (?:вам )?(?:расскажу|покажу), как)\b"),
     "Раскачка в духе «сегодня я расскажу». Удали её и начни сразу с сути."),
    (re.compile(r"(?i)^\s*(?:всем привет|привет всем|привет,? (?:друзья|ребята|ребят|народ|всем)"
                r"|здравствуйте|приветствую|доброе утро|добрый (?:день|вечер)|всем хай"
                r"|хай\b|салют\b|друзья\b|ребята\b|ребят\b|дорогие\b)"),
     "Приветствие. В ленту приходят не за тем, чтобы с ними здоровались."),
    (PROMISE_RE,
     "Обещание результата зрителю. Instagram режет такие формулировки, и это неправда: "
     "показывай свой путь, а не гарантируй чужой."),
    (PLACEHOLDER_RE,
     "Заготовка не заполнена ([…] или {{…}}). Это ещё не хук: впиши своё число, срок, нишу."),
    (HASHTAG_RE,
     "Хэштег в хуке. Хэштегам место внизу подписи, если вообще где-то."),
    (EMOJI_RE,
     "Эмодзи в хуке. В крупном тексте на экране есть место либо для слов, либо для эмодзи."),
]


def clamp(n):
    return max(0.0, min(100.0, n))


def normalize(text):
    """«50 000 ₽» вслух — это одно число, значит и здесь одно слово."""
    t = re.sub(r"(?<=\d)[\s\u00a0\u202f](?=\d{3}\b)", "", text)
    t = re.sub(r"(?<=\d)[,.](?=\d)", ".", t)
    t = re.sub(r"(?<=\d)\s?₽", "₽", t)
    return t


def words(text):
    return WORD_RE.findall(normalize(text))


def low(token):
    return token.lower().replace("ё", "е").strip("'’-")


def is_spoken_number(w):
    return w in SPOKEN_EXACT or w.startswith(SPOKEN_STEMS)


def is_money(w):
    return w in MONEY_EXACT or w.startswith(MONEY_STEMS) or w.endswith("₽")


def is_stake(w):
    return w in STAKE_EXACT or w.startswith(STAKE_STEMS)


def proper_nouns(text):
    """Имена, бренды, города: с заглавной не в начале предложения. Плюс аббревиатуры."""
    raw = normalize(text).split()
    if sum(ch.isupper() for ch in text) > 0.6 * max(1, sum(ch.isalpha() for ch in text)):
        return []                           # весь хук капсом — заглавные ничего не значат
    found = []
    for i, tok in enumerate(raw):
        core = re.sub(rf"^[^0-9{L}]+|[^0-9{L}]+$", "", tok)
        if not core or tok[0] in "«\"„“(":
            continue
        new_sentence = i == 0 or raw[i - 1][-1:] in ".!?…:"
        if len(core) >= 2 and core.isupper() and core.isalpha():
            found.append(core)              # ИИ, SMM, CTA
        elif not new_sentence and core[0].isupper() and len(core) >= 3:
            found.append(core)
    return found



def pl(n, one, few, many):
    """Русское множественное: 1 слово, 2 слова, 5 слов."""
    n = abs(int(n))
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many

def c1(x):
    """Русская десятичная запятая для вывода: 3,9 с."""
    return f"{x:.1f}".replace(".", ",")


def hook_max_words(wps):
    """Сколько слов успевает прозвучать за HOOK_SECONDS. Тот же счёт, что в beats.py."""
    return max(4, int(HOOK_SECONDS * wps + 1e-9))


def check_length(text, wps):
    """Хук должен прозвучать до того, как палец сдвинется: до трёх секунд."""
    n = len(words(text))
    secs = n / wps
    chars = len(text.strip())
    top = hook_max_words(wps)
    if 4 <= n <= top:
        score = 100.0
    elif n < 4:
        score = clamp(100 - (4 - n) * 20)
    else:
        score = clamp(100 - (n - top) * 12)
    if chars > 70:                          # больше двух строк крупного текста
        score -= 12
    return clamp(score), f"{n} {pl(n, 'слово', 'слова', 'слов')}, {chars} {pl(chars, 'знак', 'знака', 'знаков')}, ~{c1(secs)} с вслух (нужно 4–{top} слов, до {HOOK_SECONDS:g} с)"


def check_specificity(text):
    """Одна конкретная вещь сильнее трёх абстрактных."""
    nums = [n.strip() for n in NUMBER_RE.findall(normalize(text)) if n.strip()]
    propers = set(proper_nouns(text))
    lw = [low(w) for w in words(text)]
    # «10 тысяч» уже посчитано как число — «тысяч» второй раз не считаем
    spoken = [w for i, w in enumerate(lw)
              if (is_spoken_number(w) or is_money(w)) and not re.match(r"\d", w)
              and not (i and re.match(r"\d", lw[i - 1]))]
    hits = len(nums) + len(propers) + len(spoken)
    score = 15.0 if hits == 0 else clamp(45 + hits * 30)
    found = ", ".join(nums[:2] + sorted(propers)[:2] + spoken[:2])
    return score, (f"конкретика: {hits}" + (f" ({found})" if found else
                   " — ни числа, ни имени, нечего проверить"))


def check_stakes(text):
    """Напряжение, цена, отрицание. То, что зритель может потерять."""
    lw = [low(w) for w in words(text)]
    markers = sorted({w for w in lw if is_stake(w)})
    if re.search(r"\d\s?(?:₽|руб|тыс|к\b)|\$\s?\d", normalize(text), re.IGNORECASE):
        markers.append("цена")
    if re.search(r"(?i)на самом деле|вс[её] ещ[её]|если не\b", text):
        markers.append("оборот-поворот")
    if re.search(r"(?i)\b(?:сейчас|а теперь|а сейчас)\s*—", text):
        markers.append("контраст было/стало")
    n = len(markers)
    score = {0: 20.0, 1: 70.0}.get(n, 100.0)
    detail = f"ставка: {n}" + (f" ({', '.join(markers[:4])})" if markers else
                               " — в этой фразе ничего не стоит на кону")
    return clamp(score), detail


def check_frontload(text):
    """Главное слово не может стоять девятым."""
    w = words(text)
    if not w:
        return 0.0, "пусто"
    lw = [low(x) for x in w]
    opener = " ".join(lw[:2])
    penalty, hit_opener = 0, None
    for weak in WEAK_OPENERS:
        if opener == weak or opener.startswith(weak + " ") or lw[0] == weak:
            penalty, hit_opener = 30, weak
            break
    propers = {low(p) for p in proper_nouns(text)}
    payload = None
    for i, token in enumerate(lw):
        if (is_stake(token) or is_spoken_number(token) or is_money(token)
                or NUMBER_RE.match(w[i]) and re.match(r"\d", w[i])
                or (i and token in propers)):
            payload = i
            break
    if payload is None:
        base, where = 30.0, "в фразе нет ни одного цепляющего слова"
    elif payload <= 3:
        base, where = 100.0, f"цепляющее слово на {payload + 1}-м месте"
    elif payload <= 6:
        base, where = 70.0, f"цепляющее слово на {payload + 1}-м месте, можно раньше"
    else:
        base, where = 40.0, f"цепляющее слово на {payload + 1}-м месте, слишком поздно"
    detail = where + (f"; слабое начало «{hit_opener}»" if hit_opener else "")
    return clamp(base - penalty), detail


def check_address(text):
    """Обращено к одному зрителю или висит в воздухе."""
    lw = [low(x) for x in words(text)]
    if any(w in YOU for w in lw):
        polite = any(w in {"вы", "вас", "вам", "ваш", "ваша", "ваше", "ваши"} for w in lw)
        return 100.0, "говорит со зрителем" + (" (на «вы»; в рилсах обычно живее «ты»)"
                                               if polite else "")
    if lw and lw[0] in IMPERATIVES:
        return 90.0, f"начинается с призыва («{lw[0]}»)"
    if any(VERB_YOU_RE.search(w) and w not in NOT_VERBS for w in lw):
        return 95.0, "глагол на «ты» — зритель в фразе есть"
    if any(w in FIRST_PERSON for w in lw):
        return 70.0, "от первого лица, зритель не назван"
    return 35.0, "третье лицо, в кадре никого"


CHECKS = ["ДЛИНА", "КОНКРЕТИКА", "СТАВКА", "НАЧАЛО", "АДРЕСАТ"]


def run(text, wpm=DEFAULT_WPM):
    wps = wpm / 60.0
    results = {
        "ДЛИНА": check_length(text, wps),
        "КОНКРЕТИКА": check_specificity(text),
        "СТАВКА": check_stakes(text),
        "НАЧАЛО": check_frontload(text),
        "АДРЕСАТ": check_address(text),
    }
    folded = fold(text)
    flags = [msg for pattern, msg in DEALBREAKERS if pattern.search(folded)]
    promise = PROMISE_RE.search(folded)
    hole = PLACEHOLDER_RE.search(text)
    scores = [results[c][0] for c in CHECKS]
    # Самый слабый признак тянет вниз весь хук: одного провала хватает,
    # чтобы палец листал дальше.
    overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4 - len(flags) * 15
    overall = clamp(overall)
    if promise or hole:                 # обещание и дырка — стоп-факторы, их не спасает ничто
        overall = min(overall, 40.0)
    verdict = "СИЛЬНЫЙ" if overall >= 70 and min(scores) >= 55 and not flags else (
        "НОРМ" if overall >= NO_HOOK else "СЛАБЫЙ")
    return results, overall, verdict, flags


# --- база хуков Кирилла --------------------------------------------------

STOP = set("""и в во не что он на я с со как а то все всё она так его но да ты к у же вы за бы
по только ее её мне было вот от меня еще ещё нет о из ему теперь когда даже ну ли если уже или ни
быть был него вас опять вам ведь там потом себя ничего ей может они тут где есть надо ней для мы
тебя их чем была сам чтоб чего раз тоже себе под будет ж тогда кто этот того потому этого какой
совсем ним здесь этом один почти мой тем чтобы нее сейчас были куда зачем всех можно при об хоть
над тот эти нас про всего них какая много три эту моя свою этой перед том такой им
это тебе твой мои свой вот штука""".split())


def stem(w):
    w = low(w)
    return w[:5] if len(w) > 5 else w


def content_stems(text):
    return {stem(w) for w in words(re.sub(r"\[[^\]]*\]", " ", text))
            if low(w) not in STOP and not re.match(r"\d", w)}


def load_base(path=BASE_PATH):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return None
    groups = [(g["id"], g["name"], re.compile(g["match"], re.IGNORECASE), g)
              for gid in d["classify_order"] for g in d["groups"] if g["id"] == gid]
    for h in d["hooks"]:
        h["_stems"] = content_stems(h["template"])
    return {"groups": groups, "hooks": d["hooks"]}


CAUTION_SIM = 0.25                  # доля общих слов с шаблоном, при которой он «тот самый»


def classify(text, base):
    """Приём из базы, к которому ближе всего этот хук, и 2 похожих шаблона."""
    if not base:
        return None
    t = normalize(text).strip().lower()
    gid, gname, ginfo = None, "без приёма", None
    for g_id, g_name, rx, info in base["groups"]:
        if rx.search(t):
            gid, gname, ginfo = g_id, g_name, info
            break
    mine = content_stems(text)
    pool = [h for h in base["hooks"] if h["group"] == gid] or base["hooks"]

    def sim(h):
        inter = len(mine & h["_stems"])
        return inter / (len(mine | h["_stems"]) or 1), -len(h["template"])

    nearest = sorted(pool, key=sim, reverse=True)[:2]
    if gid is None:                     # без приёма показываем только реально похожие
        nearest = [h for h in nearest if mine & h["_stems"]]
    cat = None
    if ginfo and ginfo.get("categories"):
        cat = max(ginfo["categories"].items(), key=lambda kv: kv[1])[0]
    return {"group": gid, "group_name": gname, "category": cat,
            "nearest": [dict({"id": h["id"], "template": h["template"]},
                             # пометку caution показываем, только если хук правда близок к шаблону
                             **({"caution": h["caution"]}
                                if h.get("caution") and sim(h)[0] >= CAUTION_SIM else {}))
                        for h in nearest]}


# --- вывод ----------------------------------------------------------------

def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render_one(text, results, overall, verdict, flags, cls, out=sys.stdout):
    print("\nОЦЕНКА ХУКА", file=out)
    print("=" * 62, file=out)
    print(f"  «{text.strip()}»\n", file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {name:<11} {bar(score)} {c1(score):>5}", file=out)
        print(f"  {'':<11} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'ИТОГ':<11} {bar(overall)} {c1(overall):>5}   {verdict}", file=out)
    for f in flags:
        print(f"\n  СТОП-ФАКТОР  {f}", file=out)
    if cls:
        cat = f", обычно {cls['category']}" if cls["category"] else ""
        print(f"\n  ПРИЁМ ИЗ БАЗЫ  {cls['group_name']}{cat}", file=out)
        for n in cls["nearest"]:
            print(f"    похоже на {n['id']}: {n['template']}", file=out)
            if n.get("caution"):
                print(f"      осторожно: {n['caution']}", file=out)
    if verdict != "СИЛЬНЫЙ":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print(f"\n  Слабее всего: {weakest}. Исправь это и прогони ещё раз.", file=out)
    print("", file=out)


def render_table(rows, out=sys.stdout):
    print("\nРЕЙТИНГ ХУКОВ\n" + "=" * 78, file=out)
    for i, r in enumerate(rows, 1):
        mark = "->" if i == 1 else "  "
        hook = r["hook"] if len(r["hook"]) <= 60 else r["hook"][:57] + "..."
        print(f"{mark} {c1(r['score']):>5} {r['verdict']:<8} {hook}", file=out)
        tail = f"слабее всего: {r['weakest']} ({r['checks'][r['weakest']]['score']:.0f})"
        if r.get("base"):
            tail += f" · приём: {r['base']['group_name']}"
        print(f"        {tail}", file=out)
        for f in r["flags"]:
            print(f"        стоп-фактор: {f}", file=out)
        for n in (r.get("base") or {}).get("nearest", []):
            if n.get("caution"):
                print(f"        осторожно ({n['id']}): {n['caution']}", file=out)
    print(f"\nСнимай верхний. Если у верхнего меньше {NO_HOOK} — хука среди этих нет.\n", file=out)


def main():
    ap = argparse.ArgumentParser(description="Оценка хука рилса по пяти признакам.")
    ap.add_argument("input", nargs="?", default="-", help="файл, по хуку на строку, или -")
    ap.add_argument("--hook", help="оценить один хук из командной строки")
    ap.add_argument("--wpm", type=float, default=DEFAULT_WPM,
                    help=f"темп речи, слов в минуту (по умолчанию {DEFAULT_WPM})")
    ap.add_argument("--base", default=BASE_PATH, help="путь к hooks.json")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.hook:
        lines = [args.hook]
    else:
        raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
        lines = [l.strip() for l in raw.splitlines() if l.strip() and not l.startswith("#")]
    if not lines:
        print("нечего оценивать", file=sys.stderr)
        sys.exit(2)
    base = load_base(args.base)
    if base is None:
        print("заметка: hooks.json не найден, приёмы из базы не определены (--base)",
              file=sys.stderr)

    payload = []
    for line in lines:
        results, overall, verdict, flags = run(line, args.wpm)
        payload.append({
            "hook": line,
            "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
            "weakest": min(CHECKS, key=lambda c: results[c][0]),
            "flags": flags,
            "score": round(overall, 1),
            "verdict": verdict,
            "base": classify(line, base),
        })

    if args.json:
        print(json.dumps(payload if len(payload) > 1 else payload[0], indent=2, ensure_ascii=False))
    elif len(payload) == 1:
        results, overall, verdict, flags = run(lines[0], args.wpm)
        render_one(lines[0], results, overall, verdict, flags, payload[0]["base"])
    else:
        render_table(sorted(payload, key=lambda r: -r["score"]))

    sys.exit(0 if max(p["score"] for p in payload) >= NO_HOOK else 1)


if __name__ == "__main__":
    main()
