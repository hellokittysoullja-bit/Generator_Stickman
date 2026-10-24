"""Инвентарь всей базы → список приёмов с номерами, которые обязан решить каждый рилс (24.10, владелец: «каждый рилс без
этого не делался»).

Источник — `docs/reels_knowledge/20_funnel/01_inventory.md`: строки «- приём | источник | сила | метка | к нам | где»
по всем 400+ расшифровкам и документам базы. Номер пункта — от текста приёма и источника (sha1), поэтому правка
другой строки инвентаря номера не сдвигает.

Область (`scope`):
- `reel` — колонка «где» говорит о рилсе (хук, сценарий, монтаж, звук, субтитры, обложка, подпись, закреп,
  комментарии, пробные, серия): решается в `passport.inventory` КАЖДОГО рилса стандарта ≥ 12 (`reel_rules.check_inventory`);
- `never` — колонка «к нам» начинается с «нет» / «не брать» (обман, давление, чужие права): запреты, рилс их не
  решает, а соблюдает;
- `funnel` — «где» называет только сайт, бот, канал, оффер, метрики, рост и не называет рилс: решается в воронке
  (`20_funnel/02_funnel.md`);
- всё остальное, включая общие принципы без места («—», «процесс», «текст»), — `reel`: решает каждый рилс.

    python scripts/inventory_matrix.py          # пересобрать docs/reels_knowledge/inventory_matrix.jsonl и напечатать счёт
"""
import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "reels_knowledge", "20_funnel", "01_inventory.md")
OUT = os.path.join(ROOT, "docs", "reels_knowledge", "inventory_matrix.jsonl")

REEL_WHERE = re.compile(r"рилс|хук|сценари|монтаж|субтитр|звук|кадр|обложк|подпис|закреп|комментар|пробн|серия|"
                        r"финал|петл|удержан|окн|надпис|голос кота|кот\b|кот —|reels|shorts|публикац|карусел|профил|"
                        r"шапк|сторис|бренд|темы|контент-план|идеи", re.I)
FUNNEL_WHERE = re.compile(r"сайт|лендинг|бот|telegram|телеграм|канал|оффер|квиз|подписк|метрик|воронк|личк|сбор данных|"
                          r"цена|оплат|запуск|рост|реклам|посев|продукт|удержание подписчик|сообществ|событи|сеанс", re.I)
NEVER = re.compile(r"^\s*(\*\*)?(нет|не брать)\b", re.I)


def item_id(title, source):
    return "I" + hashlib.sha1(f"{title}|{source}".encode("utf8")).hexdigest()[:7]


def parse(path=SRC):
    items, sec = [], ""
    for n, line in enumerate(open(path, encoding="utf8"), 1):
        line = line.rstrip("\n")
        if line.startswith("#"):
            sec = line.strip("# ").strip()
            continue
        if not (line.startswith("- ") and line.count("|") >= 4):
            continue
        cols = [c.strip() for c in line[2:].split("|")]
        title, source, where = cols[0], cols[1], cols[-1]
        verdict = " ".join(cols[3:-1])
        k_nam = cols[-2] if len(cols) >= 2 else ""
        scope = ("never" if NEVER.search(k_nam) or NEVER.search(verdict) else
                 "funnel" if FUNNEL_WHERE.search(where) and not REEL_WHERE.search(where) else "reel")
        items.append({"id": item_id(title, source), "line": n, "section": sec, "title": title.replace("**", "")[:400],
                      "source": source, "verdict": verdict[:300], "where": where[:200], "scope": scope})
    return items


def main():
    items = parse()
    ids = Counter(i["id"] for i in items)
    for k, v in ids.items():                        # одинаковый приём из одного источника дважды — номер с хвостом
        if v > 1:
            for j, it in enumerate(x for x in items if x["id"] == k):
                if j: it["id"] = f"{k}_{j}"
    with open(OUT, "w", encoding="utf8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    c = Counter(i["scope"] for i in items)
    print(f"{OUT}: пунктов {len(items)} — рилс {c['reel']}, воронка {c['funnel']}, запреты {c['never']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
