#!/usr/bin/env python3
"""
beats.py — превращает сценарий рилса в раскадровку по времени до съёмки.

Считает, сколько звучит каждая строка, раскладывает их по таймкоду и ловит
четыре вещи, которые убивают рилс на монтаже: хук длиннее трёх секунд, бит,
на котором зритель успевает уйти, несколько строк подряд без конкретики и
длину, которая не совпадает с задуманной.

Заготовки [..] и {{..}} в тайминг не идут: их не произносят. Скрипт
отмечает биты, где они остались.

Тайминг — оценка по числу слов и темпу речи. Для плана монтажа её хватает,
запись она не заменяет. По умолчанию 140 слов в минуту (≈ 2,3 слова в
секунду) — средний темп русской речи в кадре. Засеки себя на чтении
сценария вслух и поставь свой темп через --wpm: обычно выходит 120–170.

Запуск
  python3 beats.py script.txt
  python3 beats.py script.txt --target 30
  python3 beats.py script.txt --wpm 160 --target 45
  pbpaste | python3 beats.py -
  python3 beats.py script.txt --json
"""

import argparse
import json
import re
import sys

L = "A-Za-zА-Яа-яЁё"
WORD_RE = re.compile(rf"[0-9{L}₽$%][0-9{L}₽$%'’-]*")
SENT_RE = re.compile(r"[^.!?…]+[.!?…]*")

SPOKEN_NUMBERS = {
    "два", "две", "двух", "три", "трёх", "трех", "четыре", "пять", "пяти", "шесть",
    "семь", "восемь", "девять", "десять", "двадцать", "тридцать", "сорок",
    "пятьдесят", "сто", "двести", "триста", "пятьсот", "полгода", "полчаса",
    "дважды", "трижды", "вдвое", "втрое", "косарь", "лям",
}
SPOKEN_STEMS = ("тысяч", "миллион", "миллиард", "полтор", "половин", "рубл", "процент")

STOPWORDS = set("""и в во не что он на я с со как а то все всё она так его но да ты к у же вы за бы
по только её ее мне было вот от меня ещё еще нет о из ему теперь когда даже ну ли если уже или ни
быть был него до вас вам там потом себя ничего может они тут где есть надо для мы тебя их чем
была сам чтобы без чего раз тоже себе под будет тогда кто этот того потому этого какой здесь этом
один мой тем сейчас были можно при об после над больше тот через эти нас про всего них много эту
моя свою этой перед том такой им это тебе твой мои свой просто очень""".split())

HOOK_WINDOW = 4.3        # секунды. Дальше палец уже всё решил. Тот же предел,
                         # что HOOK_SECONDS в hookscore.py: при 140 сл/мин это 10 слов.
MAX_BEAT = 4.0           # секунды на одной мысли без смены картинки.
ABSTRACT_RUN = 3         # битов подряд без ничего проверяемого.


# Незаполненные заготовки: [результат] из шаблона и {{твоё число}} из сценария.
# Вслух их не произносят, поэтому в тайминг они не идут.
PLACEHOLDER_RE = re.compile(r"\[[^\]\n]+\]|\{\{[^}\n]*\}\}")


def hook_max_words(wps):
    """Сколько слов успевает прозвучать за HOOK_WINDOW секунд."""
    return int(HOOK_WINDOW * wps + 1e-9)


def normalize(text):
    """«50 000 ₽» вслух — одно число, значит и здесь одно слово."""
    t = re.sub(r"(?<=\d)[\s\u00a0\u202f](?=\d{3}\b)", "", text)
    t = re.sub(r"(?<=\d)[,.](?=\d)", ".", t)
    return re.sub(r"(?<=\d)\s?₽", "₽", t)


def words(text):
    return WORD_RE.findall(normalize(PLACEHOLDER_RE.sub(" ", text)))


def low(w):
    return w.lower().replace("ё", "е").strip("'’-")


def stem(w):
    """Грубая основа: «монтаж», «монтажа», «монтажом» — одно слово для петли."""
    w = low(w)
    return w[:5] if len(w) > 5 else w


def concrete_count(text):
    """Числа, суммы, имена и бренды не в начале предложения, числа словами."""
    n = len(re.findall(r"\d+(?:\.\d+)?", normalize(text)))
    raw = text.split()
    for i, tok in enumerate(raw):
        core = re.sub(rf"^[^{L}]+|[^{L}]+$", "", tok)
        if not core or tok[0] in "«\"„“(":
            continue
        new_sentence = i == 0 or raw[i - 1][-1:] in ".!?…:"
        if (len(core) >= 2 and core.isupper()) or (
                not new_sentence and core[0].isupper() and len(core) >= 3):
            n += 1
    for w in words(text):
        lw = low(w)
        if lw in SPOKEN_NUMBERS or lw.startswith(SPOKEN_STEMS):
            n += 1
    return n



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


def tc(seconds):
    m, s = divmod(seconds, 60)
    return f"{int(m)}:{s:04.1f}"


def split_beats(raw, wps):
    """Одна строка — один бит, если только строка не слишком длинная для одного."""
    beats = []
    for line in [l.strip() for l in raw.splitlines()]:
        if not line:
            continue
        if len(words(line)) / wps <= MAX_BEAT * 1.5:
            beats.append(line)
            continue
        # Длинный абзац режем по концам предложений, чтобы тайминг что-то значил.
        parts = [p.strip() for p in SENT_RE.findall(line) if p.strip()]
        buf = ""
        for part in parts:
            candidate = (buf + " " + part).strip()
            if buf and len(words(candidate)) / wps > MAX_BEAT:
                beats.append(buf)
                buf = part
            else:
                buf = candidate
        if buf:
            beats.append(buf)
    return beats


def analyse(raw, wpm=140, target=None):
    wps = wpm / 60.0
    beats = split_beats(raw, wps)
    if not beats:
        return None

    rows, clock = [], 0.0
    for i, text in enumerate(beats):
        n = len(words(text))
        dur = n / wps
        rows.append({
            "n": i + 1,
            "start": round(clock, 2),
            "dur": round(dur, 2),
            "words": n,
            "text": text,
            "concrete": concrete_count(PLACEHOLDER_RE.sub(" ", text)),
            "label": "",
            "flags": [],
            "placeholders": PLACEHOLDER_RE.findall(text),
        })
        clock += dur
    total = clock

    # Подписываем места, на которых держится рилс.
    for r in rows:
        if r["n"] == 1 or r["start"] + r["dur"] <= HOOK_WINDOW:
            r["label"] = "ХУК"
    rows[-1]["label"] = "ПРИЗЫВ" if rows[-1]["label"] != "ХУК" else "ХУК/ПРИЗЫВ"
    half = total / 2
    for r in rows:
        if not r["label"] and r["start"] <= half < r["start"] + r["dur"]:
            r["label"] = "СЕРЕДИНА"

    notes = []
    max_hook = hook_max_words(wps)
    if rows[0]["words"] > max_hook:
        rows[0]["flags"].append(f"хук звучит {c1(rows[0]['dur'])} с — дольше {HOOK_WINDOW:.0f} с")
        notes.append(f"Бит 1 говорится {c1(rows[0]['dur'])} с. Сократи до "
                     f"{max_hook} {pl(max_hook, 'слово', 'слова', 'слов')} или меньше, иначе хук прозвучит, "
                     "когда зритель уже всё решил.")
    holes = [r for r in rows if r["placeholders"]]
    for r in holes:
        r["flags"].append("заготовка не заполнена: " + ", ".join(r["placeholders"][:3]))
    if holes:
        notes.append(f"В {pl(len(holes), 'бите', 'битах', 'битах')} {', '.join(str(r['n']) for r in holes)} "
                     "остались заготовки. В тайминг они не вошли: впиши своё и прогони снова, "
                     "длина изменится.")
    if rows[0]["concrete"] == 0:
        notes.append("В бите 1 нет ни числа, ни имени. Хуки, в которых нечего проверить, "
                     "и листают первыми.")

    for r in rows:
        if r["dur"] > MAX_BEAT:
            r["flags"].append(f"{c1(r['dur'])} с на одном бите")
    long_beats = [r["n"] for r in rows if r["dur"] > MAX_BEAT]
    if long_beats:
        notes.append(f"Бит(ы) {', '.join(map(str, long_beats))} длиннее {MAX_BEAT:.0f} с. "
                     "Раздели строку или поменяй картинку внутри неё. "
                     "На статичном кадре и уходят.")

    run, start = 0, None
    for r in rows:
        if r["concrete"] == 0:
            run += 1
            start = start if start is not None else r["n"]
            if run == ABSTRACT_RUN:
                notes.append(f"В битах {start}–{r['n']} нет ничего конкретного. "
                             "Поставь в один из них число, имя или цену.")
        else:
            run, start = 0, None

    # Возвращает ли последняя строка к первой? Сравниваем по основам слов,
    # чтобы «монтаж» и «монтажа» считались одним словом.
    def content(text):
        out = {}
        for w in words(text):
            if low(w) not in STOPWORDS and not re.match(r"\d", w) and len(w) > 2:
                out.setdefault(stem(w), low(w))
        return out
    first, last = content(rows[0]["text"]), content(rows[-1]["text"])
    loop = sorted(first[s] for s in set(first) & set(last))
    if loop:
        notes.append(f"Петля есть: последний бит повторяет «{', '.join(loop[:3])}» из хука. "
                     "Повторный просмотр — бесплатный охват.")
    else:
        notes.append("Петли нет. Последний бит не повторяет ни одного слова из хука, "
                     "и ролик заканчивается в пустоту. Повторить одно слово из бита 1 — "
                     "самый дешёвый способ получить повторный просмотр.")

    if target:
        delta = total - target
        if abs(delta) <= target * 0.1:
            notes.append(f"Длина в цель ({c1(total)} с при цели {target:g} с).")
        elif delta > 0:
            notes.append(f"На {c1(delta)} с длиннее цели. Убери примерно {int(delta * wps)} {pl(delta * wps, 'слово', 'слова', 'слов')}.")
        else:
            notes.append(f"На {c1(-delta)} с короче цели. Добавь около {int(-delta * wps)} {pl(-delta * wps, 'слово', 'слова', 'слов')} "
                         "или снимай коротко. Обычно коротко — правильно.")

    return {
        "wpm": wpm, "target": target,
        "total_seconds": round(total, 2),
        "total_words": sum(r["words"] for r in rows),
        "beats": rows,
        "notes": notes,
    }


def render(a, out=sys.stdout):
    head = (f"РАСКАДРОВКА  ·  {a['total_words']} {pl(a['total_words'], 'слово', 'слова', 'слов')}  ·  ~{c1(a['total_seconds'])} с "
            f"при {a['wpm']:g} сл/мин" + (f"  ·  цель {a['target']:g} с" if a["target"] else ""))
    print("\n" + head, file=out)
    print("=" * max(len(head), 72), file=out)
    for r in a["beats"]:
        label = f"{r['label']:<11}" if r["label"] else " " * 11
        print(f"  {tc(r['start'])}  {c1(r['dur']):>4}с  {label}{r['text']}", file=out)
        for f in r["flags"]:
            print(f"  {'':>6}  {'':>5}  {'':<11}^ {f}", file=out)
    print("-" * max(len(head), 72), file=out)
    for n in a["notes"]:
        print(f"  - {n}", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Раскадровка сценария рилса по времени.")
    ap.add_argument("input", nargs="?", default="-", help="файл сценария или - для stdin")
    ap.add_argument("--wpm", type=float, default=140,
                    help="темп речи, слов в минуту (по умолчанию 140 ≈ 2,3 слова/с)")
    ap.add_argument("--target", type=float, help="целевая длина в секундах")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    a = analyse(raw, wpm=args.wpm, target=args.target)
    if not a:
        print("пустой сценарий", file=sys.stderr)
        sys.exit(2)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    sys.exit(0)


if __name__ == "__main__":
    main()
