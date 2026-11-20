#!/usr/bin/env python3
"""
caption.py — проверяет подпись к посту в Instagram и показывает ровно то, что
видно в ленте до «… ещё».

В ленте у подписи примерно 125 символов, остальное прячется за тапом. Почти
каждая неудачная подпись проваливается именно там: хук в третьем
предложении, первая строка — приветствие, или всё начинается с хэштега.
Скрипт печатает видимое окно рамкой, чтобы ты прочитал его глазами
незнакомца, который листает ленту, а потом проверяет восемь вещей, которые
стоит проверять.

125 символов — приблизительно. Реальная граница гуляет от устройства, размера
шрифта и переносов строк, поэтому нужен запас, а не подпись, подогнанная под
125 знаков. Русский текст длиннее английского при том же смысле, так что в
окно влезает меньше слов: проверяй смысл, а не счёт. Другую границу можно
задать через --truncate.

Запуск
  python3 caption.py caption.txt
  python3 caption.py caption.txt --keywords "монтаж рилс,торт на заказ"
  pbpaste | python3 caption.py -
  python3 caption.py caption.txt --json
"""

import argparse
import json
import re
import sys
import textwrap

LIMIT = 2200             # жёсткий лимит подписи в Instagram
TRUNCATE = 125           # примерно здесь лента режет до «… ещё»
HASHTAG_LIMIT = 5        # Instagram ограничил хэштеги пятью на пост (раньше было 30)
                         # и сам советует брать меньше, но точнее

L = "A-Za-zА-Яа-яЁё"
HASHTAG_RE = re.compile(r"(?:^|\s)(#\w+)")
MENTION_RE = re.compile(r"(?:^|\s)(@[A-Za-z0-9_.]+)")
LINK_RE = re.compile(
    r"https?://\S+|\bwww\.\S+|\bt\.me/\S+"
    r"|\b[a-z0-9-]+\.(?:com|ru|рф|su|by|kz|ua|me|co|io|net|org|ai|app|link|site|online|pro)\b/?\S*",
    re.IGNORECASE)
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿←-⇿️]")

UP = "A-ZА-ЯЁ0-9"
# Призывы. Ключевое слово для комментария — заглавными, как его и просят писать.
ASKS = [
    (re.compile(rf"(?i:напиши(?:те)?|пиши(?:те)?|оставь(?:те)?|отправь(?:те)?|кидай|кинь|жми)"
                rf"[^.!?\n]{{0,40}}?[«\"„“]?\b[{UP}]{{3,}}\b"
                rf"|(?i:напиши(?:те)?|пиши(?:те)?|поставь(?:те)?|ставь(?:те)?)\s+[«\"]?\+"),
     "слово в комментарии"),
    (re.compile(r"(?i)\b(?:напиши(?:те)? (?:мне )?(?:в )?(?:директ|личку|лс)|пиши(?:те)? в (?:директ|личку|лс)"
                r"|в директ\b|в личные сообщения)"),
     "написать в директ"),
    (re.compile(r"(?i)\bсохран(?:и|ите|яй|яйте)\b"), "сохранить"),
    (re.compile(r"(?i)\b(?:отправь(?:те)? (?:другу|подруге|тому|той|маме|коллеге|мужу|жене)"
                r"|перешли(?:те)?\b|поделись\b|поделитесь\b)"),
     "переслать"),
    (re.compile(r"(?i)\bподпис(?:ывайся|ывайтесь|ись|итесь)\b"), "подписаться"),
    (re.compile(r"(?i)\bссылк\w* (?:в|во) (?:шапке|профиле|био|описании профиля)\b"),
     "ссылка в профиле"),
    (re.compile(r"(?i)\bлистай(?:те)? (?:дальше|вправо|влево|карусель|до конца)\b|\bлистай(?:те)?\s*[→>]"),
     "листать карусель"),
    (re.compile(r"(?i)\b(?:а (?:ты|у тебя|вы|у вас)\b[^.!\n]{0,40}\?|как думаешь\b|как думаете\b"
                r"|расскажи(?:те)? в комментариях|напиши(?:те)?,? (?:как|что|какой|какая|какое|кто|где)\b"
                r"|какой вариант|что выберешь|что выберете)"),
     "ответить на вопрос"),
]

FILLER_TAGS = {
    "#рекомендации", "#рек", "#реки", "#рекомендация", "#втоп", "#хочуврек",
    "#хочувреки", "#хочувтоп", "#рилс", "#рилсы", "#тренды", "#тренд", "#популярное",
    "#вирусное", "#топ", "#лайк", "#подписка", "#взаимнаяподписка", "#взаимныеподписки",
    "#инстаграм", "#любовь", "#explore", "#explorepage", "#viral", "#fyp", "#foryou",
    "#foryoupage", "#trending", "#instagood", "#love", "#follow", "#like4like", "#reels",
    "#reelsinstagram", "#viralreels", "#instadaily",
}

GREETING_RE = re.compile(
    r"(?i)^\s*(?:всем привет|привет всем|привет,? (?:друзья|ребята|ребят|народ|мои)"
    r"|приветик|здравствуйте|приветствую|доброе утро|добрый (?:день|вечер)|друзья\b|ребята\b"
    r"|дорогие\b|девочки\b|всем хай)")


def pl(n, one, few, many):
    """Русское множественное: 1 слово, 2 слова, 5 слов."""
    n = abs(int(n))
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many

def c1(x):
    """Русская десятичная запятая для вывода."""
    return f"{x:.1f}".replace(".", ",")


def concrete(text):
    """Числа и суммы, имена и бренды не в начале предложения, аббревиатуры."""
    found = re.findall(r"\d[\d\s\u00a0]*(?:[.,]\d+)?\s?(?:₽|%|тыс\w*|к\b)?", text)
    for line in text.split("\n"):
        # эмодзи между фразами не считаем словами: «… 🥰 Сегодня» — начало предложения
        raw = [t for t in line.split() if re.search(rf"[0-9{L}.!?…:]", t)]
        for i, tok in enumerate(raw):
            core = re.sub(rf"^[^{L}]+|[^{L}]+$", "", tok)
            if not core or tok[0] in "«\"„“(#@":
                continue
            new_sentence = i == 0 or raw[i - 1][-1:] in ".!?…:" or not re.search(
                rf"[0-9{L}]", raw[i - 1])
            if len(core) >= 2 and core.isupper() and core.isalpha():
                found.append(core)
            elif not new_sentence and core[0].isupper() and len(core) >= 3:
                found.append(core)
    return [f.strip() for f in found if f.strip()]


def visible_window(text, cut):
    """Что показывает лента. Instagram режет посреди слова, и здесь так же."""
    flat = text.strip()
    return flat if len(flat) <= cut else flat[:cut]


def render_box(window, truncated, out=sys.stdout, width=52):
    print("\n  ЧТО ВИДНО В ЛЕНТЕ", file=out)
    print("  +" + "-" * (width + 2) + "+", file=out)
    lines = []
    for raw in window.split("\n"):
        lines.extend(textwrap.wrap(raw, width) or [""])
    for line in lines[:8]:
        print(f"  | {line:<{width}} |", file=out)
    tail = "… ещё" if truncated else "(подпись видна целиком)"
    print("  +" + "-" * (width + 2 - len(tail) - 2) + f" {tail} " + "+", file=out)


def analyse(text, cut=TRUNCATE, keywords=None):
    text = text.rstrip()
    stripped = text.strip()
    chars = len(stripped)
    lines = stripped.split("\n")
    first_line = lines[0].strip() if lines else ""
    tags = HASHTAG_RE.findall(stripped)
    mentions = MENTION_RE.findall(stripped)
    links = LINK_RE.findall(stripped)
    emoji = EMOJI_RE.findall(stripped)
    window = visible_window(stripped, cut)
    truncated = chars > cut
    asks = [name for pattern, name in ASKS if pattern.search(stripped)]
    filler = [t for t in tags if t.lower() in FILLER_TAGS]
    keywords = [k.strip() for k in (keywords or []) if k.strip()]
    hits = concrete(window)

    checks = []

    def add(name, status, detail):
        checks.append({"check": name, "status": status, "detail": detail})

    add("ДЛИНА", "ПРОВАЛ" if chars > LIMIT else "ОК",
        f"{chars} / {LIMIT} знаков" + (f", на {chars - LIMIT} больше лимита"
                                       if chars > LIMIT else ""))

    if not first_line:
        add("ПЕРВАЯ СТРОКА", "ПРОВАЛ", "подпись начинается с пустой строки")
    elif first_line.startswith("#") or first_line.startswith("@"):
        add("ПЕРВАЯ СТРОКА", "ПРОВАЛ",
            "начинается с хэштега или упоминания — а это единственное место, где нужна фраза")
    elif GREETING_RE.search(first_line):
        add("ПЕРВАЯ СТРОКА", "ПРОВАЛ",
            "начинается с приветствия. Самые дорогие 125 знаков уходят на «здравствуйте»")
    elif EMOJI_RE.match(first_line):
        add("ПЕРВАЯ СТРОКА", "ВНИМ", "первый символ — эмодзи. В превью он съедает место у слов")
    elif len(first_line) > cut:
        add("ПЕРВАЯ СТРОКА", "ВНИМ",
            f"{len(first_line)} {pl(len(first_line), 'знак', 'знака', 'знаков')}, обрежется на {cut} посреди мысли. "
            "Нормально, если обрыв — интрига, плохо, если обрывается придаточное")
    else:
        add("ПЕРВАЯ СТРОКА", "ОК", f"{len(first_line)} {pl(len(first_line), 'знак', 'знака', 'знаков')}, видна целиком")

    add("КОНКРЕТИКА", "ОК" if hits else "ВНИМ",
        f"в видимом окне чисел и имён: {len(hits)}"
        + (f" ({', '.join(hits[:3])})" if hits else " — до тапа нечего проверить"))

    if len(tags) > HASHTAG_LIMIT:
        add("ХЭШТЕГИ", "ПРОВАЛ", f"{len(tags)} {pl(len(tags), 'тег', 'тега', 'тегов')}, а Instagram разрешает {HASHTAG_LIMIT}. "
                                 "Лишние не сработают, а сам блок выглядит устаревшим")
    elif len(tags) == HASHTAG_LIMIT and filler:
        add("ХЭШТЕГИ", "ВНИМ", f"{len(tags)} {pl(len(tags), 'тег', 'тега', 'тегов')}, это предел, и {len(filler)} из них "
                               "ни о чём. Потрать пять мест на темы")
    elif filler:
        add("ХЭШТЕГИ", "ВНИМ", f"{len(tags)} {pl(len(tags), 'тег', 'тега', 'тегов')}, {len(filler)} из них ни о чём "
                               f"({', '.join(filler[:3])}). Они ничего не описывают")
    else:
        add("ХЭШТЕГИ", "ОК", f"тегов: {len(tags)}" + (f" ({' '.join(tags)})" if tags else ""))

    if not tags:
        add("МЕСТО ТЕГОВ", "ОК", "тегов нет, ставить некуда")
    elif any(re.search(r"(?:^|\s)" + re.escape(t) + r"(?!\w)", window) for t in tags):
        add("МЕСТО ТЕГОВ", "ВНИМ", "хэштег попал в видимое окно и тратит место в ленте на ярлык")
    else:
        add("МЕСТО ТЕГОВ", "ОК", "теги ниже обрыва")

    add("ССЫЛКИ", "ВНИМ" if links else "ОК",
        f"ссылок в подписи: {len(links)}, а в подписи они не кликаются. "
        "Перенеси в профиль или в директ" if links else "мёртвых ссылок нет")

    if len(asks) == 1:
        add("ОДИН ПРИЗЫВ", "ОК", f"призыв один: {asks[0]}")
    elif not asks:
        add("ОДИН ПРИЗЫВ", "ВНИМ", "призыва нет. Реши, зачем этот пост")
    else:
        add("ОДИН ПРИЗЫВ", "ВНИМ", f"призывов {len(asks)} ({', '.join(asks)}). "
                                   "Два призыва — то же, что ни одного")

    density = len(emoji) * 100 / max(chars, 1)
    add("ЭМОДЗИ", "ВНИМ" if density > 4 else "ОК",
        f"эмодзи: {len(emoji)}, {c1(density)} на 100 знаков"
        + (" — уже украшение, а не пунктуация" if density > 4 else ""))

    if keywords:
        low = stripped.lower().replace("ё", "е")
        win = window.lower().replace("ё", "е")
        norm = [(k, k.lower().replace("ё", "е")) for k in keywords]
        found = [k for k, n in norm if n in low]
        missing = [k for k, n in norm if n not in low]
        in_window = [k for k, n in norm if n in win]
        status = "ОК" if not missing else ("ВНИМ" if found else "ПРОВАЛ")
        add("ПОИСК", status,
            f"есть {len(found)} из {len(keywords)}"
            + (f", в видимом окне {len(in_window)}" if found else "")
            + (f". Нет: {', '.join(missing)}" if missing else "")
            + (". Ищут по точной фразе: пиши её так, как набирают в поиске, "
               "в той же форме слова" if missing else ""))

    fails = sum(1 for c in checks if c["status"] == "ПРОВАЛ")
    warns = sum(1 for c in checks if c["status"] == "ВНИМ")
    verdict = "ИСПРАВИТЬ" if fails else ("ПРОВЕРИТЬ" if warns else "ГОТОВО")

    return {
        "characters": chars, "limit": LIMIT, "truncate_at": cut,
        "visible": window, "truncated": truncated,
        "first_line_chars": len(first_line),
        "hashtags": tags, "mentions": mentions, "links": links,
        "emoji": len(emoji), "asks": asks,
        "checks": checks, "verdict": verdict,
    }


def render(a, out=sys.stdout):
    head = (f"ПРОВЕРКА ПОДПИСИ  ·  {a['characters']} / {a['limit']} знаков  ·  "
            f"хэштегов: {len(a['hashtags'])}  ·  призывов: {len(a['asks'])}")
    print("\n" + head, file=out)
    print("=" * max(len(head), 62), file=out)
    render_box(a["visible"], a["truncated"], out=out)
    print("", file=out)
    for c in a["checks"]:
        print(f"  {c['status']:<6} {c['check']:<14} {c['detail']}", file=out)
    print("-" * max(len(head), 62), file=out)
    print(f"  ИТОГ  {a['verdict']}\n", file=out)


def main():
    ap = argparse.ArgumentParser(description="Проверка подписи к посту в Instagram.")
    ap.add_argument("input", nargs="?", default="-", help="файл с подписью или - для stdin")
    ap.add_argument("--truncate", type=int, default=TRUNCATE,
                    help=f"сколько знаков видно до «… ещё» (по умолчанию {TRUNCATE})")
    ap.add_argument("--keywords", default="",
                    help="фразы через запятую, по которым тебя должны находить")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    a = analyse(raw, cut=args.truncate, keywords=args.keywords.split(","))
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    sys.exit(0 if a["verdict"] == "ГОТОВО" else 1)


if __name__ == "__main__":
    main()
