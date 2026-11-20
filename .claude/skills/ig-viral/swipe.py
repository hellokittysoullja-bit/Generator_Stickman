#!/usr/bin/env python3
"""
swipe.py — ранжирует собранные рилсы по тому, во сколько раз каждый обогнал
медиану своего аккаунта, называет приём хука из базы Кирилла и пишет
swipe-файл.

Смысл скрипта в одной поправке: голые просмотры ничего не доказывают.
Аккаунт на 2 000 000 подписчиков с 400 000 просмотров — у него обычный
вторник. Аккаунт на 4 000 подписчиков с теми же 400 000 что-то нащупал. Здесь
считается кратность к собственной медиане аккаунта — единственная версия
«залетело», из которой можно что-то взять себе.

На входе — файл с табуляцией, который ты заполняешь, пока смотришь ролики,
по рилсу на строку, первая строка — названия колонок (по-русски или
по-английски):

    аккаунт   подписчики   медиана   просмотры   хук
    @montazh  48 000       11 тыс    412 тыс     Два года назад я бросила офис ради монтажа

`медиана` — типичные просмотры аккаунта за последние ролики, это лучшая
база. Если есть только `подписчики`, медиану можно не писать, скрипт скажет,
что считал по подписчикам. Числа можно писать как в Instagram: «12,5 тыс.»,
«1,2 млн», «48 000», «412K».

Запуск
  python3 swipe.py captured.tsv
  python3 swipe.py captured.tsv --out ~/.claude/instagram/swipe.md
  python3 swipe.py captured.tsv --json
"""

import argparse
import json
import os
import re
import statistics
import sys

sys.dont_write_bytecode = True                    # не мусорим __pycache__ в ig-reel

HERE = os.path.dirname(os.path.abspath(__file__))
REEL = os.path.join(HERE, "..", "ig-reel")
HOOKS = os.path.join(REEL, "hooks.json")
WORD_RE = re.compile(r"[0-9A-Za-zА-Яа-яЁё₽$%][0-9A-Za-zА-Яа-яЁё₽$%'’-]*")

try:                                              # по желанию: заодно оценить хуки
    sys.path.insert(0, REEL)
    from hookscore import run as score_hook       # noqa: E402
except Exception:                                 # ig-viral скопирован отдельно
    score_hook = None

COLUMNS = {
    "account": "account", "аккаунт": "account", "акк": "account", "автор": "account",
    "followers": "followers", "подписчики": "followers", "подписчиков": "followers",
    "median": "median", "медиана": "median",
    "views": "views", "просмотры": "views", "просмотров": "views",
    "hook": "hook", "хук": "hook",
    "length": "length", "длина": "length",
    "cta": "cta", "призыв": "cta",
    "on-screen": "on_screen", "на экране": "on_screen", "экран": "on_screen",
}

SIGNAL = 3.0        # выше — сигнал
NORMAL = 1.5        # ниже — обычный день аккаунта, учиться нечему


def parse_count(raw):
    """«12,5 тыс.» → 12500, «1,2 млн» → 1200000, «48 000» → 48000, «412K» → 412000."""
    if raw is None:
        return None
    s = str(raw).strip().lower().replace("\u00a0", " ").replace("\u202f", " ")
    if not s:
        return None
    m = re.match(r"^([\d\s]+(?:[.,]\d+)?)\s*(тыс\.?|т\.?|k|к|млн\.?|m|м|млрд\.?|b)?", s)
    if not m:
        return None
    num = m.group(1).replace(" ", "")
    unit = (m.group(2) or "").rstrip(".")
    mult = {"тыс": 1e3, "т": 1e3, "k": 1e3, "к": 1e3, "млн": 1e6, "m": 1e6, "м": 1e6,
            "млрд": 1e9, "b": 1e9}.get(unit, 1)
    if mult == 1:
        num = num.replace(",", "").replace(".", "")   # 48,000 / 48.000 — разделители
    else:
        num = num.replace(",", ".")
    try:
        return int(round(float(num) * mult))
    except ValueError:
        return None


def load_groups(path):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return None
    by_id = {g["id"]: g for g in d["groups"]}
    out = []
    for gid in d.get("classify_order") or list(by_id):
        g = by_id.get(gid)
        if not g:
            continue
        cats = g.get("categories") or {}
        cat = max(cats.items(), key=lambda kv: kv[1])[0] if cats else None
        out.append((gid, g["name"], cat, re.compile(g["match"], re.IGNORECASE)))
    return out


def classify(hook, groups):
    if not groups:
        return None, "без приёма", None
    t = re.sub(r"(?<=\d)[\s\u00a0\u202f](?=\d{3}\b)", "", hook).strip().lower()
    for gid, name, cat, pattern in groups:
        if pattern.search(t):
            return gid, name, cat
    return None, "без приёма", None


def read_rows(path):
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    lines = [l for l in raw.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    if not lines:
        return []
    head = [COLUMNS.get(c.strip().lower(), c.strip().lower()) for c in lines[0].split("\t")]
    if "views" in head and "hook" in head:
        cols, body = head, lines[1:]
    else:
        cols, body = ["account", "followers", "views", "hook"], lines
    rows = []
    for line in body:
        cells = line.split("\t")
        if len(cells) < len(cols):
            cells += [""] * (len(cols) - len(cells))
        r = dict(zip(cols, [c.strip() for c in cells]))
        r["views"] = parse_count(r.get("views")) or 0
        for k in ("followers", "median"):
            r[k] = parse_count(r.get(k))
        if r["views"] and r.get("hook"):
            rows.append(r)
    return rows


def analyse(rows, groups):
    used_median = any(r.get("median") for r in rows)
    for r in rows:
        base = r.get("median") or r.get("followers") or 0
        r["baseline"] = base
        r["outlier"] = round(r["views"] / base, 2) if base else None
        r["group_id"], r["group"], r["category"] = classify(r["hook"], groups)
        r["words"] = len(WORD_RE.findall(r["hook"]))
        if score_hook:
            _, overall, verdict, _ = score_hook(r["hook"])
            r["hook_score"], r["hook_verdict"] = round(overall, 1), verdict
        else:
            r["hook_score"], r["hook_verdict"] = None, None
    ranked = sorted(rows, key=lambda r: -(r["outlier"] or 0))
    third = max(1, len(ranked) // 3)
    top, bottom = ranked[:third], ranked[-third:]

    def med(items, key):
        vals = [i[key] for i in items if i.get(key) is not None]
        return round(statistics.median(vals), 1) if vals else None

    def count(items, key):
        c = {}
        for r in items:
            c[r[key] or "—"] = c.get(r[key] or "—", 0) + 1
        return sorted(c.items(), key=lambda kv: -kv[1])

    bottom_groups = dict(count(bottom, "group"))
    return {
        "baseline": "медиане аккаунта" if used_median else "числу подписчиков",
        "n": len(ranked),
        "accounts": len({r.get("account", "") for r in ranked}),
        "reels": ranked,
        "signals": sum(1 for r in ranked if (r["outlier"] or 0) > SIGNAL),
        "top_groups": [(g, c, bottom_groups.get(g, 0)) for g, c in count(top, "group")],
        "top_categories": count(top, "category"),
        "top_hook_score": med(top, "hook_score"),
        "bottom_hook_score": med(bottom, "hook_score"),
        "top_words": med(top, "words"),
        "bottom_words": med(bottom, "words"),
        "unclassified": sum(1 for r in ranked if r["group_id"] is None),
    }



def c1(x):
    """Русская десятичная запятая для вывода: 3,9 с."""
    return f"{x:.1f}".replace(".", ",")


def fmt(n):
    return f"{n:,}".replace(",", " ")


def render(a, out=sys.stdout):
    head = (f"SWIPE-ФАЙЛ  ·  рилсов: {a['n']}  ·  аккаунтов: {a['accounts']}  ·  "
            f"база: кратность к {a['baseline']}")
    print("\n" + head, file=out)
    print("=" * max(len(head), 78), file=out)
    for r in a["reels"]:
        mult = f"{c1(r['outlier'])}×" if r["outlier"] else "   ?"
        mark = "!" if (r["outlier"] or 0) > SIGNAL else ("·" if (r["outlier"] or 0) < NORMAL else " ")
        score = f"{r['hook_score']:.0f}" if r["hook_score"] is not None else " -"
        print(f" {mark}{mult:>7}  хук {score:>3}  {r['group'][:30]:<30} "
              f"{r.get('account', '')[:16]:<16} {fmt(r['views']):>11}", file=out)
        print(f"           «{r['hook'][:96]}»", file=out)
    print("-" * max(len(head), 78), file=out)
    print(f"  ! выше {SIGNAL:g}× — сигнал   · ниже {NORMAL:g}× — обычный день аккаунта", file=out)
    print("\nЧТО РАБОТАЕТ В ЭТОЙ ВЫБОРКЕ", file=out)
    print(f"  сигналов (выше {SIGNAL:g}×):      {a['signals']} из {a['n']}", file=out)
    if a["top_groups"]:
        print("  приёмы в верхней трети:   "
              + ", ".join(f"{g} ×{c} (внизу {b})" for g, c, b in a["top_groups"][:4]), file=out)
    if a["top_categories"]:
        print("  категории в верхней трети: "
              + ", ".join(f"{g} ×{c}" for g, c in a["top_categories"][:3]), file=out)
    if a["top_hook_score"] is not None:
        print(f"  медиана оценки хука:      верх {a['top_hook_score']:.0f}  "
              f"против низа {a['bottom_hook_score']:.0f}", file=out)
    print(f"  медиана длины хука:       верх {a['top_words']} слов  "
          f"против низа {a['bottom_words']}", file=out)
    print(f"  без приёма:               {a['unclassified']} из {a['n']}. Прочитай их руками: "
          "там прячется приём, которого нет в базе.", file=out)
    print("\n  Выборка, собранная руками, — улика, а не доказательство. Двенадцать рилсов "
          "не говорят\n  ничего, сорок по шести аккаунтам уже что-то говорят. Собери больше, "
          "прежде чем верить.\n", file=out)


def to_markdown(a):
    lines = ["# Swipe-файл", "",
             f"Рилсов: {a['n']}, аккаунтов: {a['accounts']}. "
             f"Ранжировано по кратности к {a['baseline']}.", ""]
    for r in a["reels"]:
        mult = f"{c1(r['outlier'])}×" if r["outlier"] else "?"
        cat = f", обычно {r['category']}" if r["category"] else ""
        lines += [f"## {mult}  {r['group']}{cat}  ({r.get('account', '')})",
                  f"- просмотры: {fmt(r['views'])}, база: {fmt(r['baseline'] or 0)}",
                  f"- оценка хука: {r['hook_score']}, слов: {r['words']}",
                  f"- хук: «{r['hook']}»"]
        for key, label in (("on_screen", "на экране"), ("length", "длина"), ("cta", "призыв")):
            if r.get(key):
                lines.append(f"- {label}: {r[key]}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Рейтинг собранных рилсов по кратности к медиане.")
    ap.add_argument("input", nargs="?", default="-", help="TSV-файл или - для stdin")
    ap.add_argument("--hooks", default=HOOKS, help="путь к ig-reel/hooks.json")
    ap.add_argument("--out", help="заодно записать swipe-файл в markdown сюда")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rows = read_rows(args.input)
    if not rows:
        print("нет строк, с которыми можно работать. Нужен файл с табуляцией, "
              "в нём хотя бы просмотры и хук.", file=sys.stderr)
        sys.exit(2)
    groups = load_groups(args.hooks)
    a = analyse(rows, groups)
    if not groups:
        print("заметка: hooks.json не найден, приёмы не названы. Укажи --hooks.", file=sys.stderr)
    if score_hook is None:
        print("заметка: hookscore.py не подключился, оценки хуков пропущены.", file=sys.stderr)

    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    if args.out:
        path = os.path.expanduser(args.out)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        open(path, "w", encoding="utf-8").write(to_markdown(a))
        print(f"записано: {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
