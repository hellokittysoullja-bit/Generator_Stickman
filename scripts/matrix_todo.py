"""Список «что для канала ещё не сделано» из матрицы применения (24.10).

    python scripts/matrix_todo.py      # docs/reels_knowledge/apply_matrix.jsonl -> docs/reels_knowledge/apply_matrix_todo.md

Матрица — каждый приём базы знаний волны 9 (1 071 запись): `reel` решается в каждом рилсе (`check_matrix`), `global` — один
раз на канал (статус «код / воронка / бренд / сделать / противоречит решению владельца»), `forbidden` — никогда.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "reels_knowledge", "apply_matrix.jsonl")
OUT = os.path.join(ROOT, "docs", "reels_knowledge", "apply_matrix_todo.md")
GROUPS = {"H": "Хук", "B": "Середина и финал", "C": "Призыв, подпись, закреп, обложка", "V": "Картинка, звук, монтаж",
          "S": "Серии и замер", "F": "Личка, бот, сайт, канал, профиль"}


def owner(r):
    return "владелец" if "владел" in r["status"] else "агент"


def build():
    rows = [json.loads(x) for x in open(SRC, encoding="utf8") if x.strip()]
    todo = [r for r in rows if r["scope"] == "global" and str(r.get("status", "")).startswith("сделать")]
    by = {s: sum(r["scope"] == s for r in rows) for s in ("reel", "global", "forbidden")}
    out = ["# Матрица применения: что для канала ещё не сделано", "",
           f"Собрано `scripts/matrix_todo.py` из `apply_matrix.jsonl`: {len(rows)} приёмов — каждый рилс {by['reel']}, "
           f"один раз на канал {by['global']}, запреты {by['forbidden']}. Здесь — `global` со статусом «сделать». "
           "Решения «каждого рилса» проверяет код (`check_matrix`, стандарт 10).", "",
           f"Всего: {len(todo)}; владелец — {sum(owner(r) == 'владелец' for r in todo)}, "
           f"агент — {sum(owner(r) == 'агент' for r in todo)}.", ""]
    for g, name in GROUPS.items():
        rs = [r for r in todo if r["id"][0] == g]
        if not rs:
            continue
        out += [f"## {name} ({len(rs)})", ""]
        for who in ("владелец", "агент"):
            sub = [r for r in rs if owner(r) == who]
            if sub:
                out.append(f"**{who.capitalize()}:**")
                out += [f"- `{r['id']}` {r['title']} — {r['status'].removeprefix('сделать:').strip()}" for r in sub]
                out.append("")
    open(OUT, "w", encoding="utf8").write("\n".join(out))
    return len(todo)


if __name__ == "__main__":
    print(f"{build()} пунктов «сделать» -> {os.path.relpath(OUT, ROOT)}")
