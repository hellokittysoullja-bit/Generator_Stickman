#!/usr/bin/env python3
"""Обязательная структура длинного ролика YouTube (владелец 27.10: «без которой вообще невозможно сделать ролик»).

  python scripts/long_rules.py videos/NN_тема            — проверка до плана кадров, картинок и озвучки
  python scripts/long_rules.py videos/NN_тема --final    — то же + проверки готового ролика (F1–F4)
  python scripts/long_rules.py videos/NN_тема --template — заготовка long_passport.json со всеми полями

Правила — docs/long_knowledge/checklist.json (каждое из роликов, прочитанных целиком, конспект 01_notes.md).
kind=code проверяется здесь по script.txt и long_passport.json; kind=decide требует в паспорте items[id]
{"how": ...} или {"skip": ...}. make_video.py зовёт check() до первого платного шага и не идёт дальше при ошибке.
Код 0 — чисто, 1 — есть дыры."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from reel_rules import human_issues  # noqa: E402  (тот же «человеческий текст», что у рилсов)

CHECKLIST = os.path.join(ROOT, "docs", "long_knowledge", "checklist.json")
PASSPORT = "long_passport.json"
LONG_WORDS = 300            # сценарий длиннее — это длинный ролик, структура обязательна (эп.01/02 — пробы по 30 слов)
TITLE_MAX = 55              # Aprilynne Alter: дальше YouTube режет название троеточием
URGENCY = ("срочно", "успей", "последний шанс", "только сегодня", "пока не поздно", "осталось мало")
WARMUP = ("привет", "здравствуй", "добро пожаловать", "сегодня мы", "сегодня я", "в этом видео", "в этом ролике",
          "на нашем канале", "на моём канале", "на моем канале", "мой канал", "наш канал")
GOODBYE = ("спасибо за просмотр", "подписывайтесь", "подпишись", "ставьте лайк", "поставь лайк", "до встречи",
           "до новых встреч", "всем пока")
YOU = re.compile(r"\b(ты|тебя|тебе|тобой|твой|твоя|твоё|твое|твои|твоих|твоим|твою|твоей|твоего|твоему)\b")
CLIMAX_WORDS = 10
SKELETON = (6, 10)
CUT_SHARE = 0.10            # Jon Dorman: «если не вырезал 10 %, ты не старался»
EMOTIONS_MIN = 3


def checklist(path=CHECKLIST):
    return json.load(open(path, encoding="utf-8"))["items"]


def norm(s):
    s = (s or "").lower().replace("ё", "е")
    s = re.sub(r"\[[^\]]*\]", " ", s)
    s = re.sub(r"[^\w\s]", " ", s)
    return " ".join(s.split())


def sections(script_text):
    """[(ИМЯ, текст для голоса)] секций HOOK / BLOCK* / FINAL и title из METADATA."""
    parts = re.split(r"===\s*(.*?)\s*===", script_text)
    out, title = [], ""
    for i in range(1, len(parts), 2):
        name, body = parts[i].strip().upper(), parts[i + 1] if i + 1 < len(parts) else ""
        if name.startswith("METADATA"):
            m = re.search(r"^\s*TITLE\s*:\s*(.+)$", body, re.M)
            title = m.group(1).strip() if m else ""
        elif name.startswith(("HOOK", "BLOCK", "FINAL")):
            out.append((name, re.sub(r"\[[^\]]*\]", " ", body).strip()))
    return title, out


def sentences(text):
    return [x.strip() for x in re.split(r"(?<=[.!?…])\s+", text) if x.strip()]


def words(text):
    return re.findall(r"[а-яёa-z0-9]+", text.lower())


def is_long(video_dir):
    """Структура обязательна для длинного ролика: есть паспорт или сценарий длиннее LONG_WORDS слов."""
    if os.path.exists(os.path.join(video_dir, PASSPORT)):
        return True
    p = os.path.join(video_dir, "script.txt")
    if not os.path.exists(p):
        return False
    _, secs = sections(open(p, encoding="utf-8").read())
    return sum(len(words(t)) for _, t in secs) >= LONG_WORDS


def template(items=None):
    items = items or checklist()
    return {
        "standard": 1,
        "questions": ["", "", "", "", ""],
        "promise": ["", "", ""],
        "climax": "",
        "skeleton": ["", "", "", "", "", ""],
        "hook_candidates": [""] * 10,
        "hook_voiced": ["", ""],
        "points": [{"block": "BLOCK 1", "rehook": "", "unpack": "story", "unpack_quote": "", "payoff_quote": "",
                    "emotion": ""}],
        "end_hook": "",
        "facts": {},
        "revision": {"words_before": 0, "words_after": 0},
        "approved": {"title": False, "hook": False, "script": False},
        "items": {it["id"]: {"how": ""} for it in items if it["kind"] == "decide"},
        "final_checks": {"viewer_watch": [], "distraction_test": "", "phone_audio": "", "outsider": ""},
    }


def _filled(x):
    return isinstance(x, str) and x.strip() != ""


def check(video_dir, final=False, items=None):
    """Список дыр (пусто — структура соблюдена). Каждая строка начинается с id правила."""
    items = items or checklist()
    err = []
    sp = os.path.join(video_dir, "script.txt")
    pp = os.path.join(video_dir, PASSPORT)
    if not os.path.exists(sp):
        return [f"нет {sp}"]
    if not os.path.exists(pp):
        return [f"нет {pp}: заготовка — python scripts/long_rules.py {video_dir} --template "
                "(правила — docs/long_knowledge/checklist.json)"]
    title, secs = sections(open(sp, encoding="utf-8").read())
    try:
        p = json.load(open(pp, encoding="utf-8"))
    except ValueError as e:
        return [f"{pp} не читается как JSON: {e}"]
    hook = " ".join(t for n, t in secs if n.startswith("HOOK"))
    blocks = [(n, t) for n, t in secs if n.startswith("BLOCK")]
    final_txt = " ".join(t for n, t in secs if n.startswith("FINAL"))
    spoken = " ".join(t for _, t in secs)

    # T1 название
    if not title:
        err.append("T1: нет названия — === METADATA === и строка TITLE: …")
    else:
        if len(title) > TITLE_MAX:
            err.append(f"T1: название {len(title)} знаков > {TITLE_MAX} — YouTube обрежет конец («{title}»)")
        if any(u in title.lower() for u in URGENCY):
            err.append(f"T1: «срочность» в названии — у нас запрет давления («{title}»)")
    # Q1 вопросы и обещание
    qs = [q for q in p.get("questions") or [] if _filled(q)]
    if len(qs) < 5:
        err.append(f"Q1: выписано вопросов зрителя {len(qs)} < 5 (все вопросы, которые рождает название)")
    promise = [x for x in p.get("promise") or [] if _filled(x)]
    if len(promise) != 3:
        err.append(f"H3: обещаний {len(promise)}, нужно ровно три конкретные вещи (passport.promise)")
    for x in promise:
        if norm(x) not in norm(hook):
            err.append(f"H3: обещание «{x}» не стоит в HOOK дословно")
    # Q2, Q4 кульминация и скелет
    cl = p.get("climax") or ""
    if not _filled(cl):
        err.append("Q2: нет одной кульминации (passport.climax)")
    elif len(words(cl)) > CLIMAX_WORDS:
        err.append(f"Q2: кульминация {len(words(cl))} слов > {CLIMAX_WORDS} — сжать в одну короткую фразу")
    sk = [x for x in p.get("skeleton") or [] if _filled(x)]
    if not SKELETON[0] <= len(sk) <= SKELETON[1]:
        err.append(f"Q4: скелет {len(sk)} продвижений, нужно {SKELETON[0]}–{SKELETON[1]}")
    # H1, H2 первая фраза и разговор
    first = (sentences(hook) or [""])[0]
    low = norm(hook)[:200]
    for w in WARMUP:
        if norm(w) in low:
            err.append(f"H1: разгон в начале («{w}») — тема и ставка в первой фразе, без «о канале»")
            break
    if not first:
        err.append("H1: нет секции HOOK")
    if "?" not in hook or not YOU.search(hook.lower()):
        err.append("H2: в хуке нет вопроса зрителю на «ты» — ролик должен стать разговором")
    # H4 варианты вступления
    if len([x for x in p.get("hook_candidates") or [] if _filled(x)]) < 10:
        err.append("H4: вариантов вступления меньше 10 (hook_candidates)")
    if len([x for x in p.get("hook_voiced") or [] if _filled(x)]) < 2:
        err.append("H4: озвучено и прослушано меньше двух вариантов вступления (hook_voiced)")
    # P1–P5 пункты
    if len(blocks) < 3:
        err.append(f"P1: пунктов (=== BLOCK …) {len(blocks)} < 3")
    pts = p.get("points") or []
    by_block = {norm(x.get("block")): x for x in pts}
    emos = set()
    for n, t in blocks:
        pt = by_block.get(norm(n)) or by_block.get(norm(n.split(":")[0]))
        if not pt:
            err.append(f"P2: у «{n}» нет записи в passport.points (rehook, unpack, unpack_quote, payoff_quote, emotion)")
            continue
        head = norm(" ".join(sentences(t)[:2]))
        if not _filled(pt.get("rehook")) or norm(pt["rehook"]) not in head:
            err.append(f"P2: «{n}» не начинается своим хуком (rehook дословно в первых двух предложениях)")
        un, pay, body = norm(pt.get("unpack_quote")), norm(pt.get("payoff_quote")), norm(t)
        if pt.get("unpack") not in ("story", "metaphor"):
            err.append(f"P3: «{n}»: unpack — story или metaphor")
        if not un or un not in body:
            err.append(f"P3: «{n}»: история или метафора (unpack_quote) не найдена в тексте блока")
        elif not pay or pay not in body:
            err.append(f"P3: «{n}»: вывод (payoff_quote) не найден в тексте блока")
        elif body.index(un) > body.index(pay):
            err.append(f"P3: «{n}»: вывод звучит раньше истории — ответ выплачен сразу, кривая уйдёт ступенькой")
        if "?" not in t:
            err.append(f"P4: в «{n}» нет вопроса зрителю")
        if _filled(pt.get("emotion")):
            emos.add(norm(pt["emotion"]))
    if blocks and len(emos) < EMOTIONS_MIN:
        err.append(f"P5: эмоций по пунктам {len(emos)} < {EMOTIONS_MIN} — волна, а не ровная линия")
    # E1 конец
    eh = p.get("end_hook") or ""
    if not final_txt:
        err.append("E1: нет секции FINAL")
    elif not _filled(eh) or norm(eh) not in norm(final_txt):
        err.append("E1: конец-хук (end_hook) не стоит в FINAL дословно")
    for g in GOODBYE:
        if norm(g) in norm(final_txt):
            err.append(f"E1: «{g}» в конце — конец должен вести дальше, а не прощаться")
    # R1 правка
    rv = p.get("revision") or {}
    before, after = rv.get("words_before") or 0, rv.get("words_after") or 0
    now = len(words(spoken))
    if not before or not after:
        err.append("R1: нет замера правки (revision.words_before / words_after)")
    else:
        if after > before * (1 - CUT_SHARE):
            err.append(f"R1: правка вырезала {100 * (1 - after / before):.0f} % < {100 * CUT_SHARE:.0f} %")
        if abs(now - after) > max(10, 0.03 * after):
            err.append(f"R1: words_after {after}, а в тексте сейчас {now} слов — замер не от этого текста")
    # R3 цифры
    facts = {str(k) for k in (p.get("facts") or {})}
    for num in sorted(set(re.findall(r"\d+(?:[.,]\d+)?", spoken))):
        if num not in facts:
            err.append(f"R3: у цифры «{num}» нет источника в passport.facts")
    # R4 человеческий текст
    for i, m in human_issues([t for _, t in secs]):
        err.append(f"R4: {secs[i][0]}: {m}")
    # A1 одобрение
    ap = p.get("approved") or {}
    for k in ("title", "hook", "script"):
        if ap.get(k) is not True:
            err.append(f"A1: владелец не одобрил {k} — до плана кадров, картинок и озвучки нельзя")
    # decide-пункты
    got = p.get("items") or {}
    for it in items:
        if it["kind"] != "decide":
            continue
        d = got.get(it["id"])
        if not isinstance(d, dict) or not (_filled(d.get("how")) or _filled(d.get("skip"))):
            err.append(f"{it['id']}: нет решения — {it['rule']}")
    # F1–F4 проверки готового ролика
    if final:
        fc = p.get("final_checks") or {}
        if not [x for x in fc.get("viewer_watch") or [] if _filled(x)]:
            err.append("F1: нет пометок просмотра целиком как зритель (final_checks.viewer_watch)")
        for k, rid, what in (("distraction_test", "F2", "теста на отвлечение"),
                             ("phone_audio", "F3", "проверки звука с телефона без наушников"),
                             ("outsider", "F4", "показа вступления человеку не из ниши")):
            if not _filled(fc.get(k)):
                err.append(f"{rid}: нет {what} (final_checks.{k})")
    return err


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("video_dir")
    ap.add_argument("--final", action="store_true", help="плюс проверки готового ролика F1–F4")
    ap.add_argument("--template", action="store_true", help="записать заготовку long_passport.json")
    a = ap.parse_args()
    vd = os.path.abspath(a.video_dir)
    if a.template:
        p = os.path.join(vd, PASSPORT)
        if os.path.exists(p):
            sys.exit(f"{p} уже есть — не перезаписываю")
        json.dump(template(), open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"Заготовка: {p}")
        return
    err = check(vd, final=a.final)
    for e in err:
        print("✗", e)
    print(f"Структура длинного ролика: {'соблюдена' if not err else f'{len(err)} дыр'}")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
